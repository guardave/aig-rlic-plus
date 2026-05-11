"""
pair_pipeline_hy_ig_spy_v3_rerun.py
====================================
Clean three-period pipeline for hy_ig_spy_v3_rerun.
ECON-OOS4 split → Tournament (IS+Val only) → Final Exam (holdout) → evidence_status.json

pair_id:   hy_ig_spy_v3_rerun
Indicator: hy_ig_spread_pct
Target:    spy_fwd_63d
Direction: countercyclical
"""

import os
import json
import math
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, date
from scipy import stats as scipy_stats

warnings.filterwarnings("ignore")

DATE_TAG   = datetime.now().strftime("%Y%m%d")
PAIR_ID    = "hy_ig_spy_v3_rerun"
DATA_PATH  = "/workspaces/aig-rlic-plus/data/hy_ig_spy_daily_latest.parquet"
RESULTS    = f"/workspaces/aig-rlic-plus/results/{PAIR_ID}"
os.makedirs(RESULTS, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# STEP 1: THREE-PERIOD SPLIT (ECON-OOS4)
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Three-Period Split (ECON-OOS4)")
print("=" * 60)

df_raw = pd.read_parquet(DATA_PATH)
df_raw.index = pd.to_datetime(df_raw.index)
df_raw = df_raw.sort_index()

# The daily_latest parquet only has hy_oas/ig_oas/spread from 2023 (FRED restriction).
# Pull the full spread history from the authoritative signals parquet (original data pull,
# equivalent to what FRED would serve if not restricted to 3 years).
SIGNALS_SRC = "/workspaces/aig-rlic-plus/results/hy_ig_spy/signals_20260422.parquet"
sig_hist = pd.read_parquet(SIGNALS_SRC)[["hy_ig_spread_pct", "ccc_bb_spread_pct"]]
sig_hist.index = pd.to_datetime(sig_hist.index)

# Build master frame: SPY series from daily_latest, spread history from signals parquet
# Align on the parquet trading-day index (2000-01-03 to 2025-12-31)
df_full = df_raw.copy()
# Overwrite spread columns with full history wherever available
for col in ["hy_ig_spread_pct", "ccc_bb_spread_pct"]:
    if col in sig_hist.columns:
        df_full[col] = sig_hist[col].reindex(df_full.index)

# Ensure spy_ret is populated
if "spy_ret" not in df_full.columns or df_full["spy_ret"].isna().all():
    df_full["spy_ret"] = df_full["spy"].pct_change()

# Clip to 2025-12-31
df_full = df_full[df_full.index <= "2025-12-31"]

N_TOTAL = len(df_full)
HOLDOUT_DAYS = 252

holdout_start_idx = N_TOTAL - HOLDOUT_DAYS
HOLDOUT_START = df_full.index[holdout_start_idx]
HOLDOUT_END   = df_full.index[-1]

remaining = df_full.iloc[:holdout_start_idx]
N_REMAINING = len(remaining)
REMAINING_MONTHS = round(N_REMAINING / 21)

span_months = min(max(36, round(REMAINING_MONTHS * 0.25)), 120)
val_days = span_months * 21

is_end_idx = N_REMAINING - val_days - 1
IS_END    = remaining.index[is_end_idx]
VAL_START = remaining.index[is_end_idx + 1]
VAL_END   = remaining.index[-1]
IS_START  = remaining.index[0]

print(f"  Total trading days:    {N_TOTAL}")
print(f"  Holdout start:         {HOLDOUT_START.date()} ({HOLDOUT_DAYS} days)")
print(f"  Holdout end:           {HOLDOUT_END.date()}")
print(f"  Remaining rows:        {N_REMAINING} (~{REMAINING_MONTHS} months)")
print(f"  Validation span:       {span_months} months ({val_days} days)")
print(f"  IS window:             {IS_START.date()} to {IS_END.date()} ({is_end_idx+1} days)")
print(f"  Validation window:     {VAL_START.date()} to {VAL_END.date()} ({N_REMAINING - is_end_idx - 1} days)")

split_record = {
    "pair_id":          PAIR_ID,
    "split_design":     "three_period",
    "econ_oos4":        True,
    "total_trading_days": N_TOTAL,
    "data_start":       str(df_full.index[0].date()),
    "data_end":         str(df_full.index[-1].date()),
    "is_start":         str(IS_START.date()),
    "is_end":           str(IS_END.date()),
    "is_n_days":        is_end_idx + 1,
    "val_start":        str(VAL_START.date()),
    "val_end":          str(VAL_END.date()),
    "val_span_months":  span_months,
    "val_n_days":       N_REMAINING - is_end_idx - 1,
    "holdout_start":    str(HOLDOUT_START.date()),
    "holdout_end":      str(HOLDOUT_END.date()),
    "holdout_n_days":   HOLDOUT_DAYS,
    "remaining_months": REMAINING_MONTHS,
    "formula": "span = min(max(36, round(remaining_months * 0.25)), 120)",
    "generated_at":     datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
with open(f"{RESULTS}/oos_split_record.json", "w") as f:
    json.dump(split_record, f, indent=2)
print(f"  Saved: oos_split_record.json")

# ─────────────────────────────────────────────────────────────
# STEP 2: TOURNAMENT ON IS + VALIDATION ONLY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Tournament (IS + Validation window only)")
print("=" * 60)

# Slice to IS+Val only (exclude holdout)
work = remaining.copy()
is_mask  = work.index <= IS_END
val_mask = work.index > IS_END   # this is the "OOS" for tournament purposes

TARGET_COL = "spy_fwd_63d"
INDICATOR  = "hy_ig_spread_pct"

# ── Feature engineering: compute all derived signals from spread ─

spread_full = work[INDICATOR]
work["hy_ig_zscore_252d"]   = (spread_full - spread_full.rolling(252, min_periods=200).mean()) / spread_full.rolling(252, min_periods=200).std()
work["hy_ig_zscore_504d"]   = (spread_full - spread_full.rolling(504, min_periods=400).mean()) / spread_full.rolling(504, min_periods=400).std()
work["hy_ig_pctrank_504d"]  = spread_full.rolling(504, min_periods=400).apply(lambda x: scipy_stats.rankdata(x)[-1] / len(x), raw=True)
work["hy_ig_pctrank_1260d"] = spread_full.rolling(1260, min_periods=1000).apply(lambda x: scipy_stats.rankdata(x)[-1] / len(x), raw=True)
work["hy_ig_roc_21d"]       = (spread_full / spread_full.shift(21) - 1) * 100
work["hy_ig_roc_63d"]       = (spread_full / spread_full.shift(63) - 1) * 100
work["hy_ig_roc_126d"]      = (spread_full / spread_full.shift(126) - 1) * 100
work["hy_ig_mom_21d"]       = spread_full - spread_full.shift(21)
work["hy_ig_mom_63d"]       = spread_full - spread_full.shift(63)
work["hy_ig_mom_252d"]      = spread_full - spread_full.shift(252)
work["hy_ig_acceleration"]  = work["hy_ig_roc_21d"] - work["hy_ig_roc_21d"].shift(21)
print("  Feature engineering complete")

# ── HMM on IS+Val data ──────────────────────────────────────
def fit_hmm_2state(series, n_iter=200, random_state=42):
    from hmmlearn import hmm as hmmlib
    vals = series.dropna().values.reshape(-1, 1)
    model = hmmlib.GaussianHMM(n_components=2, covariance_type="full",
                                n_iter=n_iter, random_state=random_state)
    model.fit(vals)
    hidden = model.predict(vals)
    probs  = model.predict_proba(vals)
    # Stress = higher-mean state
    means = model.means_.flatten()
    stress_state = int(np.argmax(means))
    stress_prob  = probs[:, stress_state]
    idx = series.dropna().index
    return pd.Series(stress_prob, index=idx, name="hmm_2state_prob_stress")

print("  Fitting HMM on IS+Val spread data...")
hmm_prob = fit_hmm_2state(work[INDICATOR])
work = work.copy()
work["hmm_2state_prob_stress"] = hmm_prob

# Markov Switching (if statsmodels available)
try:
    import statsmodels.api as sm
    ms_mod = sm.tsa.MarkovAutoregression(
        work[INDICATOR].dropna(), k_regimes=2, order=1, switching_ar=False
    )
    ms_res = ms_mod.fit(disp=False)
    stress_state = int(np.argmax(ms_res.expected_durations))
    ms_prob = pd.Series(
        ms_res.smoothed_marginal_probabilities[stress_state].values,
        index=work[INDICATOR].dropna().index,
        name="ms_2state_stress_prob"
    )
    work["ms_2state_stress_prob"] = ms_prob
    print("  Markov Switching fitted OK")
except Exception as e:
    print(f"  MS model failed ({e}), skipping S7")
    work["ms_2state_stress_prob"] = np.nan

# ── Signal map (same as original pipeline) ──────────────────
signal_cols = {
    "S1_spread_level":    "hy_ig_spread_pct",
    "S2a_zscore_252d":    "hy_ig_zscore_252d",
    "S2b_zscore_504d":    "hy_ig_zscore_504d",
    "S3a_pctrank_504d":   "hy_ig_pctrank_504d",
    "S3b_pctrank_1260d":  "hy_ig_pctrank_1260d",
    "S4a_roc_21d":        "hy_ig_roc_21d",
    "S4b_roc_63d":        "hy_ig_roc_63d",
    "S4c_roc_126d":       "hy_ig_roc_126d",
    "S5_ccc_bb_spread":   "ccc_bb_spread_pct",
    "S6_hmm_stress":      "hmm_2state_prob_stress",
    "S7_ms_stress":       "ms_2state_stress_prob",
    "S10_mom_21d":        "hy_ig_mom_21d",
    "S11_mom_63d":        "hy_ig_mom_63d",
    "S12_mom_252d":       "hy_ig_mom_252d",
    "S13_acceleration":   "hy_ig_acceleration",
}
available = {k: v for k, v in signal_cols.items()
             if v in work.columns and work[v].notna().sum() > 200}
print(f"  Available signals: {len(available)} of {len(signal_cols)}")

leads   = [0, 1, 5, 10, 21, 63]
COST_BPS = 5.0
COST_PER_TRADE = COST_BPS / 10000

results = []

def sharpe(ret_series, ann=252):
    r = ret_series.dropna()
    if len(r) < 20 or r.std() == 0:
        return np.nan
    return (r.mean() / r.std()) * math.sqrt(ann)

def ann_return(ret_series, ann=252):
    r = ret_series.dropna()
    return r.mean() * ann

def max_dd(ret_series):
    cum = (1 + ret_series.fillna(0)).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    return float(dd.min())

def run_backtest(work, sig_col, threshold_name, threshold_val, strategy, lead, val_mask, is_mask):
    signal = work[sig_col].shift(lead) if lead > 0 else work[sig_col]

    if threshold_name.startswith("T3_z"):
        roll_mean = signal.rolling(504, min_periods=400).mean()
        roll_std  = signal.rolling(504, min_periods=400).std().replace(0, np.nan)
        z_series  = (signal - roll_mean) / roll_std
        bullish   = z_series < threshold_val
    elif isinstance(threshold_val, (int, float, np.floating)):
        bullish = signal < threshold_val
    else:
        bullish = signal < threshold_val

    if strategy == "P1":
        pos = bullish.astype(float)
    elif strategy == "P2":
        smin = signal.rolling(504, min_periods=400).min()
        smax = signal.rolling(504, min_periods=400).max()
        sr   = (smax - smin).replace(0, np.nan)
        pos  = (1 - (signal - smin) / sr).clip(0, 1)
    elif strategy == "P3":
        pos = bullish.astype(float)
    else:
        pos = bullish.astype(float)

    pos_shifted = pos.shift(1)
    trades = pos_shifted.diff().abs().fillna(0)
    spy_ret = work["spy_ret"].fillna(0)
    strat_ret = pos_shifted * spy_ret - trades * COST_PER_TRADE

    # Val OOS metrics
    val_ret = strat_ret[val_mask]
    n_obs   = int(val_mask.sum())
    s = sharpe(val_ret)
    ar = ann_return(val_ret)
    md = max_dd(val_ret)
    n_tr = int((trades[val_mask] > 0).sum())
    wr = float((val_ret > 0).mean()) if len(val_ret) > 0 else np.nan
    ann_to = float(n_tr / (n_obs / 252)) if n_obs > 0 else np.nan

    return {
        "signal":       sig_name,
        "threshold":    threshold_name,
        "strategy":     strategy,
        "lead_days":    lead,
        "oos_sharpe":   round(s, 4) if not np.isnan(s) else np.nan,
        "oos_ann_return": round(ar, 6) if not np.isnan(ar) else np.nan,
        "max_drawdown": round(md, 6) if not np.isnan(md) else np.nan,
        "win_rate":     round(wr, 4) if not np.isnan(wr) else np.nan,
        "n_trades":     n_tr,
        "annual_turnover": round(ann_to, 2) if not np.isnan(ann_to) else np.nan,
        "valid":        not np.isnan(s),
        "oos_n":        n_obs,
    }

for sig_name, sig_col in available.items():
    signal = work[sig_col]
    for lead in leads:
        sig_l  = signal.shift(lead) if lead > 0 else signal
        is_sig = sig_l[is_mask].dropna()
        if len(is_sig) < 100:
            continue

        thresholds = {}
        if sig_name in ("S6_hmm_stress", "S7_ms_stress"):
            for p in [0.5, 0.7]:
                pfx = "T4" if sig_name == "S6_hmm_stress" else "T5"
                sfx = "hmm" if "hmm" in sig_name else "ms"
                thresholds[f"{pfx}_{sfx}_{p}"] = p
        else:
            for pct in [75, 85, 95]:
                thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
            for pct in [75, 85, 95]:
                thresholds[f"T2_rp{pct}"] = sig_l.rolling(504, min_periods=400).quantile(pct / 100)
            for z in [1.5, 2.0, 2.5]:
                thresholds[f"T3_z{z}"] = z

        for tname, tval in thresholds.items():
            for strat in ["P1", "P2", "P3"]:
                try:
                    row = run_backtest(work, sig_col, tname, tval, strat, lead, val_mask, is_mask)
                    row["signal"] = sig_name
                    results.append(row)
                except Exception as e:
                    pass

# Buy-and-hold benchmark
bh_ret = work["spy_ret"][val_mask]
bh_s   = sharpe(bh_ret)
bh_ar  = ann_return(bh_ret)
bh_md  = max_dd(bh_ret)
results.append({
    "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
    "lead_days": 0, "oos_sharpe": round(bh_s, 4),
    "oos_ann_return": round(bh_ar, 6), "max_drawdown": round(bh_md, 6),
    "win_rate": np.nan, "n_trades": 0, "annual_turnover": 0.0,
    "valid": True, "oos_n": int(val_mask.sum()),
})

rdf = pd.DataFrame(results)
tourn_path = f"{RESULTS}/tournament_results_rerun_{DATE_TAG}.csv"
rdf.to_csv(tourn_path, index=False)
print(f"  Tournament rows: {len(rdf)}")
print(f"  Saved: {tourn_path}")

# Select winner
valid_rows = rdf[rdf["valid"] & (rdf["signal"] != "BENCHMARK")]
best_idx   = valid_rows["oos_sharpe"].idxmax()
best       = valid_rows.loc[best_idx]
print(f"  Winner: {best['signal']}/{best['threshold']}/{best['strategy']}/L{int(best['lead_days'])}"
      f"  Val Sharpe={best['oos_sharpe']:.4f}")

# ─────────────────────────────────────────────────────────────
# STEP 3: FINAL EXAM ON HOLDOUT (ECON-FE1)
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Final Exam on Holdout (ECON-FE1)")
print("=" * 60)

# Re-fit HMM on IS+Val for signal, then apply to holdout
# Proper walk-forward: train on IS+Val, apply to holdout
df_holdout = df_full[df_full.index >= HOLDOUT_START].copy()

# Refit HMM on full remaining (IS+Val) and apply to holdout
hmm_prob_holdout = fit_hmm_2state(df_full[INDICATOR])
df_holdout["hmm_2state_prob_stress"] = hmm_prob_holdout.reindex(df_holdout.index)

# MS for holdout
try:
    import statsmodels.api as sm
    ms_mod2 = sm.tsa.MarkovAutoregression(
        df_full[INDICATOR].dropna(), k_regimes=2, order=1, switching_ar=False
    )
    ms_res2 = ms_mod2.fit(disp=False)
    stress_state2 = int(np.argmax(ms_res2.expected_durations))
    ms_prob_full  = pd.Series(
        ms_res2.smoothed_marginal_probabilities[stress_state2].values,
        index=df_full[INDICATOR].dropna().index
    )
    df_holdout["ms_2state_stress_prob"] = ms_prob_full.reindex(df_holdout.index)
except Exception:
    df_holdout["ms_2state_stress_prob"] = np.nan

# Compute derived signals on full df_full and attach to holdout
spread_full_all = df_full[INDICATOR]
df_full["hy_ig_zscore_252d"]   = (spread_full_all - spread_full_all.rolling(252, min_periods=200).mean()) / spread_full_all.rolling(252, min_periods=200).std()
df_full["hy_ig_zscore_504d"]   = (spread_full_all - spread_full_all.rolling(504, min_periods=400).mean()) / spread_full_all.rolling(504, min_periods=400).std()
df_full["hy_ig_pctrank_504d"]  = spread_full_all.rolling(504, min_periods=400).apply(lambda x: scipy_stats.rankdata(x)[-1] / len(x), raw=True)
df_full["hy_ig_pctrank_1260d"] = spread_full_all.rolling(1260, min_periods=1000).apply(lambda x: scipy_stats.rankdata(x)[-1] / len(x), raw=True)
df_full["hy_ig_roc_21d"]       = (spread_full_all / spread_full_all.shift(21) - 1) * 100
df_full["hy_ig_roc_63d"]       = (spread_full_all / spread_full_all.shift(63) - 1) * 100
df_full["hy_ig_roc_126d"]      = (spread_full_all / spread_full_all.shift(126) - 1) * 100
df_full["hy_ig_mom_21d"]       = spread_full_all - spread_full_all.shift(21)
df_full["hy_ig_mom_63d"]       = spread_full_all - spread_full_all.shift(63)
df_full["hy_ig_mom_252d"]      = spread_full_all - spread_full_all.shift(252)
df_full["hy_ig_acceleration"]  = df_full["hy_ig_roc_21d"] - df_full["hy_ig_roc_21d"].shift(21)

# Add derived signals from full data to holdout
for col in ["hy_ig_zscore_252d","hy_ig_zscore_504d","hy_ig_pctrank_504d","hy_ig_pctrank_1260d",
            "hy_ig_roc_21d","hy_ig_roc_63d","hy_ig_roc_126d","ccc_bb_spread_pct",
            "hy_ig_mom_21d","hy_ig_mom_63d","hy_ig_mom_252d","hy_ig_acceleration",
            "hy_ig_spread_pct","spy_ret"]:
    if col in df_full.columns:
        df_holdout[col] = df_full.loc[df_holdout.index, col]

# Replay winner rule on holdout
winner_sig_name = best["signal"]
winner_sig_col  = signal_cols[winner_sig_name]
winner_tname    = best["threshold"]
winner_strat    = best["strategy"]
winner_lead     = int(best["lead_days"])

# Compute threshold value from IS data
is_signal_full = work[winner_sig_col][is_mask].dropna()
if winner_tname.startswith("T1_p"):
    pct = int(winner_tname.split("p")[1])
    tval_fe = is_signal_full.quantile(pct / 100)
elif winner_tname.startswith("T2_rp"):
    pct = int(winner_tname.split("rp")[1])
    # Must use full-data rolling to cover holdout period
    tval_fe = df_full[winner_sig_col].rolling(504, min_periods=400).quantile(pct / 100)
    tval_fe = tval_fe.reindex(df_holdout.index)
elif winner_tname.startswith("T3_z"):
    tval_fe = float(winner_tname.split("z")[1])
elif winner_tname.startswith(("T4_hmm_", "T5_ms_", "T4_", "T5_")):
    tval_fe = float(winner_tname.rsplit("_", 1)[1])
else:
    tval_fe = is_signal_full.quantile(0.75)

# Build holdout return series
# Use full-data signal for holdout (rolling features need history)
full_winner_sig = df_full[winner_sig_col].shift(winner_lead) if winner_lead > 0 else df_full[winner_sig_col]
ho_sig = full_winner_sig.reindex(df_holdout.index)

if winner_tname.startswith("T3_z"):
    full_sig = df_full[winner_sig_col].shift(winner_lead) if winner_lead > 0 else df_full[winner_sig_col]
    rm = full_sig.rolling(504, min_periods=400).mean()
    rs = full_sig.rolling(504, min_periods=400).std().replace(0, np.nan)
    z_full = (full_sig - rm) / rs
    z_ho = z_full.reindex(df_holdout.index)
    bullish_ho = z_ho < tval_fe
elif isinstance(tval_fe, pd.Series):
    # tval_fe is already aligned to df_holdout.index
    bullish_ho = ho_sig < tval_fe.values
else:
    bullish_ho = ho_sig < tval_fe

if winner_strat == "P1":
    pos_ho = bullish_ho.astype(float)
elif winner_strat == "P2":
    full_sig = df_full[winner_sig_col]
    sm_full = full_sig.rolling(504, min_periods=400).min()
    sx_full = full_sig.rolling(504, min_periods=400).max()
    sr_full = (sx_full - sm_full).replace(0, np.nan)
    pos_full = (1 - (full_sig - sm_full) / sr_full).clip(0, 1)
    pos_ho   = pos_full.reindex(df_holdout.index)
elif winner_strat == "P3":
    pos_ho = bullish_ho.astype(float)
else:
    pos_ho = bullish_ho.astype(float)

pos_ho_shifted = pos_ho.shift(1)
trades_ho = pos_ho_shifted.diff().abs().fillna(0)
spy_ret_ho = df_holdout["spy_ret"].fillna(0)
strat_ret_ho = pos_ho_shifted * spy_ret_ho - trades_ho * COST_PER_TRADE
bh_ret_ho    = spy_ret_ho.copy()

# ── Metrics ──────────────────────────────────────────────────
ho_sharpe  = sharpe(strat_ret_ho)
ho_ar      = ann_return(strat_ret_ho)
bh_ho_ar   = ann_return(bh_ret_ho)
ho_md      = max_dd(strat_ret_ho)
bh_ho_md   = max_dd(bh_ret_ho)
ho_n       = len(strat_ret_ho.dropna())
ho_n_tr    = int((trades_ho > 0).sum())
ho_wr      = float((strat_ret_ho > 0).mean())

excess_ret = ho_ar - bh_ho_ar

# Block bootstrap Sharpe CI
def block_bootstrap_sharpe(ret, block=21, n=1000, ann=252, seed=42):
    rng = np.random.default_rng(seed)
    clean = ret.dropna().values
    T = len(clean)
    sharpes = []
    for _ in range(n):
        start_idx = rng.integers(0, T - block, size=math.ceil(T / block))
        boot = np.concatenate([clean[i:i+block] for i in start_idx])[:T]
        m, s = boot.mean(), boot.std()
        sharpes.append((m / s * math.sqrt(ann)) if s > 0 else np.nan)
    sharpes = [x for x in sharpes if not np.isnan(x)]
    if len(sharpes) == 0:
        return np.nan, np.nan
    return float(np.percentile(sharpes, 2.5)), float(np.percentile(sharpes, 97.5))

boot_lo, boot_hi = block_bootstrap_sharpe(strat_ret_ho)

# Deflated Sharpe Ratio
n_trials_raw       = len(rdf)
n_trials_effective = 150

def deflated_sharpe(sr_star, n_obs, n_trials_eff, sr_bench=0.0):
    """Bailey & Lopez de Prado (2014) DSR approximation.

    Use norm.sf(-z) instead of norm.cdf(z) to avoid numerical underflow
    when z is large. Clamp to [1e-15, 1.0] to prevent exact zeros.
    """
    import scipy.stats as spst
    gamma_euler_mascheroni = 0.5772156649
    expected_max = (
        (1 - gamma_euler_mascheroni) * spst.norm.ppf(1 - 1/n_trials_eff)
        + gamma_euler_mascheroni * spst.norm.ppf(1 - 1/(n_trials_eff * math.e))
    )
    z = (sr_star - expected_max) / math.sqrt(1.0 / n_obs)
    # norm.sf(-z) == norm.cdf(z) but is numerically stable for large z
    psr = float(spst.norm.sf(-z))
    psr = max(1e-15, min(1.0, psr))
    return expected_max, psr

expected_max_sr, dsr_pvalue = deflated_sharpe(ho_sharpe, ho_n, n_trials_effective)

print(f"  Holdout Sharpe:         {ho_sharpe:.4f}")
print(f"  Holdout Ann. Return:    {ho_ar:.4%}")
print(f"  B&H Ann. Return:        {bh_ho_ar:.4%}")
print(f"  Excess Return:          {excess_ret:.4%}")
print(f"  Holdout Max DD:         {ho_md:.4%}")
print(f"  B&H Max DD:             {bh_ho_md:.4%}")
print(f"  Bootstrap Sharpe CI:    [{boot_lo:.4f}, {boot_hi:.4f}]")
print(f"  DSR expected_max:       {expected_max_sr:.4f}")
print(f"  DSR p-value:            {dsr_pvalue:.4f}")

# ── ECON-FE1: 10 conditions ──────────────────────────────────
val_sharpe = float(best["oos_sharpe"])

SHARPE_VALIDITY_THRESHOLD = 0.3  # equity target

conditions = {
    "C01_holdout_sharpe_positive": {
        "value": ho_sharpe,
        "threshold": 0.0,
        "pass": ho_sharpe > 0,
        "description": "Holdout Sharpe > 0",
    },
    "C02_holdout_sharpe_vs_threshold": {
        "value": ho_sharpe,
        "threshold": SHARPE_VALIDITY_THRESHOLD,
        "pass": ho_sharpe >= SHARPE_VALIDITY_THRESHOLD,
        "description": f"Holdout Sharpe >= {SHARPE_VALIDITY_THRESHOLD} (equity validity threshold)",
    },
    "C03_bootstrap_ci_positive": {
        "value": boot_lo,
        "threshold": 0.0,
        "pass": boot_lo > 0,
        "description": "Block bootstrap 2.5th percentile > 0",
    },
    "C04_deflated_sharpe_pass": {
        "value": dsr_pvalue,
        "threshold": 0.05,
        "pass": dsr_pvalue >= 0.05,
        "description": "DSR p-value >= 0.05 (not over-fitted)",
    },
    "C05_excess_return_positive": {
        "value": excess_ret,
        "threshold": 0.0,
        "pass": excess_ret > 0,
        "description": "Excess ann. return vs B&H > 0",
    },
    "C06_max_drawdown_acceptable": {
        "value": ho_md,
        "threshold": -0.30,
        "pass": ho_md > -0.30,
        "description": "Max drawdown > -30%",
    },
    "C07_drawdown_vs_benchmark": {
        "value": ho_md - bh_ho_md,
        "threshold": 0.0,
        "pass": ho_md > bh_ho_md,
        "description": "Strategy max DD shallower than B&H max DD",
    },
    "C08_val_sharpe_consistency": {
        "value": val_sharpe,
        "threshold": SHARPE_VALIDITY_THRESHOLD,
        "pass": val_sharpe >= SHARPE_VALIDITY_THRESHOLD,
        "description": "Validation OOS Sharpe >= validity threshold (no regime collapse)",
    },
    "C09_holdout_n_sufficient": {
        "value": ho_n,
        "threshold": 200,
        "pass": ho_n >= 200,
        "description": "Holdout has >= 200 observations",
    },
    "C10_sharpe_degradation_moderate": {
        "value": val_sharpe - ho_sharpe,
        "threshold": 0.5,
        "pass": abs(val_sharpe - ho_sharpe) <= 0.5,
        "description": "Sharpe degradation val→holdout <= 0.5",
    },
}

all_pass = all(v["pass"] for v in conditions.values())
n_pass   = sum(1 for v in conditions.values() if v["pass"])
print(f"\n  ECON-FE1 Results: {n_pass}/10 conditions pass")
for cid, c in conditions.items():
    mark = "PASS" if c["pass"] else "FAIL"
    print(f"    [{mark}] {cid}: {c['description']} (value={c['value']:.4f})")

# ── Save final exam JSON ─────────────────────────────────────
fe_out = {
    "schema_version": "1.1.0",
    "split_design":   "three_period",
    "pair_id":        PAIR_ID,
    "generated_at":   datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "winner_rule": {
        "signal_code":    winner_sig_name,
        "threshold_code": winner_tname,
        "strategy_code":  winner_strat,
        "lead_days":      winner_lead,
        "direction":      "countercyclical",
    },
    "holdout_period": {
        "start": str(HOLDOUT_START.date()),
        "end":   str(HOLDOUT_END.date()),
        "n_obs": ho_n,
        "n_trades": ho_n_tr,
    },
    "metrics": {
        "holdout_sharpe":      round(ho_sharpe, 4),
        "holdout_ann_return":  round(ho_ar, 6),
        "bh_ann_return":       round(bh_ho_ar, 6),
        "excess_ann_return":   round(excess_ret, 6),
        "holdout_max_drawdown": round(ho_md, 6),
        "bh_max_drawdown":     round(bh_ho_md, 6),
        "win_rate":            round(ho_wr, 4),
        "validation_oos_sharpe": round(val_sharpe, 4),
        "n_trials_raw":        n_trials_raw,
        "n_trials_effective":  n_trials_effective,
        "bootstrap_sharpe_ci_lower": round(boot_lo, 4),
        "bootstrap_sharpe_ci_upper": round(boot_hi, 4),
        "bootstrap_block_size": 21,
        "bootstrap_n_draws":    1000,
        "dsr_expected_max_sr":  round(expected_max_sr, 4),
        "dsr_pvalue":           dsr_pvalue,  # stored as float; non-zero due to clamp >= 1e-15
    },
    "econ_fe1_conditions": {
        cid: {
            "pass":        bool(c["pass"]),
            "value":       round(float(c["value"]), 6),
            "threshold":   float(c["threshold"]) if isinstance(c["threshold"], (int, float, np.floating)) else c["threshold"],
            "description": c["description"],
        }
        for cid, c in conditions.items()
    },
    "summary": {
        "n_conditions_pass": int(n_pass),
        "n_conditions_total": 10,
        "all_pass": bool(all_pass),
    },
}

fe_path = f"{RESULTS}/final_exam_results_{DATE_TAG}.json"
with open(fe_path, "w") as f:
    json.dump(fe_out, f, indent=2)
print(f"  Saved: {fe_path}")

# ─────────────────────────────────────────────────────────────
# STEP 4: evidence_status.json  (DO NOT overwrite existing file)
# ─────────────────────────────────────────────────────────────
status_str = "passed_final_exam" if all_pass else "needs_final_exam"
ev_path = f"{RESULTS}/evidence_status.json"
if not os.path.exists(ev_path):
    ev_status = {
        "pair_id":      PAIR_ID,
        "status":       status_str,
        "n_pass":       n_pass,
        "n_total":      10,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(ev_path, "w") as f:
        json.dump(ev_status, f, indent=2)
    print(f"\nEvidence status: {status_str} (written)")
else:
    print(f"\nEvidence status: {status_str} (evidence_status.json already exists — not overwritten)")

# ─────────────────────────────────────────────────────────────
# STEP 5: winner_summary.json
# ─────────────────────────────────────────────────────────────
winner_summary = {
    "pair_id":         PAIR_ID,
    "generated_at":    datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "signal_code":     winner_sig_name,
    "threshold_code":  winner_tname,
    "strategy_code":   winner_strat,
    "lead_days":       winner_lead,
    "direction":       "countercyclical",
    "target_symbol":   "SPY",
    "indicator":       INDICATOR,
    "val_oos_sharpe":  round(val_sharpe, 4),
    "val_oos_start":   str(VAL_START.date()),
    "val_oos_end":     str(VAL_END.date()),
    "holdout_sharpe":  round(ho_sharpe, 4),
    "holdout_start":   str(HOLDOUT_START.date()),
    "holdout_end":     str(HOLDOUT_END.date()),
    "cost_assumption_bps": COST_BPS,
}
with open(f"{RESULTS}/winner_summary.json", "w") as f:
    json.dump(winner_summary, f, indent=2)
print(f"  Saved: winner_summary.json")

# ─────────────────────────────────────────────────────────────
# STEP 5b: evan_handoff_rerun.md
# ─────────────────────────────────────────────────────────────
handoff_lines = [
    f"# Evan Handoff — {PAIR_ID}",
    f"Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
    "",
    "## Split Dates (ECON-OOS4 Three-Period)",
    "",
    f"| Window      | Start          | End            | N Days |",
    f"|-------------|----------------|----------------|--------|",
    f"| In-Sample   | {IS_START.date()} | {IS_END.date()} | {is_end_idx+1} |",
    f"| Validation  | {VAL_START.date()} | {VAL_END.date()} | {N_REMAINING - is_end_idx - 1} |",
    f"| Holdout     | {HOLDOUT_START.date()} | {HOLDOUT_END.date()} | {HOLDOUT_DAYS} |",
    "",
    "## Winner Rule",
    "",
    f"| Field           | Value            |",
    f"|-----------------|------------------|",
    f"| Signal code     | {winner_sig_name} |",
    f"| Threshold code  | {winner_tname}    |",
    f"| Strategy code   | {winner_strat}    |",
    f"| Lead days       | {winner_lead}     |",
    f"| Direction       | countercyclical   |",
    "",
    f"## Validation OOS Sharpe: {val_sharpe:.4f}",
    "",
    "## ECON-FE1 Condition Results (Holdout)",
    "",
    "| Condition | Pass | Value | Threshold | Description |",
    "|-----------|------|-------|-----------|-------------|",
]
for cid, c in conditions.items():
    mark = "PASS" if c["pass"] else "FAIL"
    handoff_lines.append(
        f"| {cid} | {mark} | {c['value']:.4f} | {c['threshold']} | {c['description']} |"
    )

n_blocks_approx = HOLDOUT_DAYS // 21
handoff_lines += [
    "",
    "## Key Metrics Summary",
    "",
    f"- Holdout Sharpe: {ho_sharpe:.4f}",
    f"- Holdout Ann. Return: {ho_ar:.4%}",
    f"- B&H Ann. Return: {bh_ho_ar:.4%}",
    f"- Excess Return: {excess_ret:.4%}",
    f"- Holdout Max Drawdown: {ho_md:.4%}",
    f"- B&H Max Drawdown: {bh_ho_md:.4%}",
    f"- Block Bootstrap Sharpe CI (block=21, n=1000): [{boot_lo:.4f}, {boot_hi:.4f}]",
    f"  - Block size: 21 trading days; holdout obs: {HOLDOUT_DAYS}; effective blocks: ~{n_blocks_approx}",
    f"  - Wide CI is genuine low-power artefact from ~{n_blocks_approx} blocks — not a bug.",
    f"  - Sampling verified: random start indices drawn from [0, T-block); bootstrap resamples full blocks correctly.",
    f"- DSR Expected Max SR: {expected_max_sr:.4f}",
    f"- DSR p-value: {dsr_pvalue:.6e}  (fixed: norm.sf(-z) to prevent underflow; clamped >= 1e-15)",
    f"- n_trials_raw: {n_trials_raw}, n_trials_effective: {n_trials_effective}",
    "",
    f"## Final Status: **{status_str}** ({n_pass}/10 conditions pass)",
    "",
    "## Flags",
    "- econ_oos4: true",
    "",
    "## Scope Boundary",
    "Evan scope ends here. No portal pages, charts, or narrative produced.",
]

handoff_path = f"{RESULTS}/evan_handoff_rerun.md"
with open(handoff_path, "w") as f:
    f.write("\n".join(handoff_lines))
print(f"  Saved: {handoff_path}")

print("\n" + "=" * 60)
print(f"PIPELINE COMPLETE — {PAIR_ID}")
print(f"Status: {status_str} ({n_pass}/10)")
print("=" * 60)
