"""
ECON-CP1/CP2 Retro-Apply — Batch script for 9 pairs
Wave 10K.3 [Evan]

Produces per-pair:
  1. subperiod_sharpe.csv
  2. rolling_correlation_{pair_id}.csv
  3. structural_break_{pair_id}.json
  4. rolling_sharpe_{pair_id}.csv
  5. rolling_granger_{pair_id}.csv
"""

import os
from pathlib import Path
import json
import glob
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests
import traceback

warnings.filterwarnings("ignore")

BASE = str(Path(__file__).resolve().parents[1])

# ── Pair configuration ────────────────────────────────────────────────────────
PAIRS = [
    dict(
        pair_id="dff_ted_spy",
        data_file="data/dff_ted_spy_daily_20260314.parquet",
        signal_col="spread_roc_21d",
        target_col="spy_ret",
        freq="daily",
        oos_start="2015-01-01",
        lead_days=0,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="hy_ig_spy",
        data_file="data/hy_ig_spy_daily_20000101_20260422.parquet",
        signal_col="hmm_2state_prob_stress",
        target_col="spy_ret",
        freq="daily",
        oos_start="2019-10-01",
        lead_days=0,
        hmm_signal=True,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="hy_ig_v2_spy",
        data_file="data/hy_ig_v2_spy_daily_20260410.parquet",
        signal_col="hmm_2state_prob_stress",
        target_col="spy_ret",
        freq="daily",
        oos_start="2018-01-01",
        lead_days=0,
        hmm_signal=True,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="indpro_spy",
        data_file="data/indpro_spy_monthly_19900101_20251231.parquet",
        signal_col="indpro_mom3m",
        target_col="spy_ret",
        freq="monthly",
        oos_start="2018-01-01",
        lead_days=3,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="permit_spy",
        data_file="data/permit_spy_monthly_20260314.parquet",
        signal_col="permit_mom1m",
        target_col="spy_ret",
        freq="monthly",
        oos_start="2018-01-01",
        lead_days=1,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="sofr_ted_spy",
        data_file="data/sofr_ted_spy_daily_20260314.parquet",
        signal_col="spread_roc_63d",
        target_col="spy_ret",
        freq="daily",
        oos_start="2015-01-01",
        lead_days=0,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="ted_spliced_spy",
        data_file="data/ted_spliced_spy_daily_20260314.parquet",
        signal_col="spread_roc_21d",
        target_col="spy_ret",
        freq="daily",
        oos_start="2015-01-01",
        lead_days=0,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="umcsent_xlv",
        data_file="data/umcsent_xlv_monthly_19980101_20251231.parquet",
        signal_col="umcsent_yoy",
        target_col="xlv_ret",
        freq="monthly",
        oos_start="2019-04-30",
        lead_days=6,
        hmm_signal=False,
        vix_countercyclical=False,
    ),
    dict(
        pair_id="vix_vix3m_spy",
        data_file="data/vix_vix3m_spy_daily_20260314.parquet",
        signal_col="vix_vix3m_ratio_z126",
        target_col="spy_ret",
        freq="daily",
        oos_start="2015-01-01",
        lead_days=0,
        hmm_signal=False,
        vix_countercyclical=True,  # high z → bear → short
    ),
]

import pathlib

MIN_COVERAGE_MONTHS = 6  # minimum months to compute Sharpe


def load_episodes(pair_id: str) -> list:
    """Load pair-class-specific stress episodes from the canonical registry.

    Reads docs/schemas/episode_registry.json, looks up indicator_category from
    results/{pair_id}/interpretation_metadata.json, and returns the matching
    episode list. Falls back to _fallback if the category is absent or unknown.
    """
    registry = json.loads(
        pathlib.Path(os.path.join(BASE, "docs/schemas/episode_registry.json")).read_text()
    )
    interp_path = pathlib.Path(os.path.join(BASE, f"results/{pair_id}/interpretation_metadata.json"))
    category = "unknown"
    if interp_path.exists():
        interp = json.loads(interp_path.read_text())
        category = interp.get("indicator_category", interp.get("indicator_type", "unknown"))
    episodes = registry.get(category, registry["_fallback"])
    return episodes


# ── Helper: load and merge data + signals ────────────────────────────────────
def load_pair_data(cfg):
    """Load main parquet and merge signals parquet; return merged DataFrame."""
    df = pd.read_parquet(os.path.join(BASE, cfg["data_file"]))
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"

    sig_pattern = os.path.join(BASE, f"results/{cfg['pair_id']}/signals_*.parquet")
    sig_files = sorted(glob.glob(sig_pattern))
    if sig_files:
        sig_df = pd.read_parquet(sig_files[-1])
        sig_df.index = pd.to_datetime(sig_df.index)
        # Only add columns not already in main
        new_cols = [c for c in sig_df.columns if c not in df.columns]
        if new_cols:
            df = df.join(sig_df[new_cols], how="left")

    return df


# ── Helper: compute strategy returns ─────────────────────────────────────────
def compute_strat_ret(df, cfg):
    """Return a Series of strategy returns aligned to df.index."""
    signal = df[cfg["signal_col"]].copy()
    target = df[cfg["target_col"]].copy()
    freq = cfg["freq"]
    lead = cfg["lead_days"]

    if cfg["hmm_signal"]:
        # high stress prob → bearish → scale down exposure
        # strat_ret = (1 - prob_stress.shift(1)) * target  BUT target is already fwd ret
        # We want to size by calm probability
        shifted_calm = (1.0 - signal.shift(1))
        strat_ret = shifted_calm * target
    elif cfg["vix_countercyclical"]:
        # high z → high vol regime → bearish → go short
        strat_ret = -np.sign(signal.shift(1)) * target
    else:
        if freq == "monthly":
            strat_ret = np.sign(signal.shift(lead)) * target
        else:
            strat_ret = np.sign(signal.shift(1)) * target

    return strat_ret.dropna()


# ── Helper: annualised stats ──────────────────────────────────────────────────
def annualised_stats(ret_series, freq):
    factor = 252 if freq == "daily" else 12
    n = len(ret_series)
    if n < 2:
        return np.nan, np.nan, np.nan, np.nan
    mean = ret_series.mean()
    std = ret_series.std()
    ann_ret = mean * factor
    ann_vol = std * np.sqrt(factor)
    sharpe = (mean / std) * np.sqrt(factor) if std > 0 else np.nan
    # max drawdown
    cumulative = (1 + ret_series).cumprod()
    rolling_max = cumulative.cummax()
    dd = (cumulative - rolling_max) / rolling_max
    max_dd = dd.min()
    return ann_ret, ann_vol, sharpe, max_dd


# ── 1. Sub-period Sharpe ──────────────────────────────────────────────────────
def compute_subperiod_sharpe(df, strat_ret, cfg):
    freq = cfg["freq"]
    oos_start = pd.Timestamp(cfg["oos_start"])
    rows = []

    episodes = load_episodes(cfg["pair_id"])
    episode_tuples = [(ep["label"], ep["start"], ep["end"]) for ep in episodes]
    periods = episode_tuples + [
        ("Full OOS", cfg["oos_start"], str(df.index.max().date()))
    ]

    for pname, pstart, pend in periods:
        p_s = pd.Timestamp(pstart)
        p_e = pd.Timestamp(pend)
        is_oos = p_s >= oos_start

        mask = (strat_ret.index >= p_s) & (strat_ret.index <= p_e)
        sub = strat_ret[mask]

        # check minimum coverage
        months_cov = len(sub) / (252 / 12 if freq == "daily" else 1)
        if freq == "monthly":
            months_cov = len(sub)
        if months_cov < MIN_COVERAGE_MONTHS or len(sub) < 2:
            rows.append(dict(
                period_name=pname,
                start_date=pstart, end_date=pend,
                is_oos=is_oos,
                ann_return=np.nan, ann_vol=np.nan, sharpe=np.nan,
                n_obs=len(sub), max_drawdown=np.nan
            ))
            continue

        ann_ret, ann_vol, sharpe, max_dd = annualised_stats(sub, freq)
        rows.append(dict(
            period_name=pname,
            start_date=pstart, end_date=pend,
            is_oos=is_oos,
            ann_return=round(ann_ret, 4),
            ann_vol=round(ann_vol, 4),
            sharpe=round(sharpe, 4) if not np.isnan(sharpe) else np.nan,
            n_obs=len(sub),
            max_drawdown=round(max_dd, 4) if not np.isnan(max_dd) else np.nan,
        ))

    return pd.DataFrame(rows)


# ── 2. Rolling correlation ────────────────────────────────────────────────────
def compute_rolling_corr(df, cfg):
    freq = cfg["freq"]
    window = 504 if freq == "daily" else 24
    signal = df[cfg["signal_col"]]
    target = df[cfg["target_col"]]
    rolling_corr = signal.rolling(window, min_periods=window // 2).corr(target)
    result = rolling_corr.dropna().reset_index()
    result.columns = ["date", "rolling_corr_24m"]
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    return result


# ── 3. Structural break (QLR / rolling R² approach) ──────────────────────────
def compute_structural_break(df, cfg):
    from statsmodels.regression.linear_model import OLS
    from statsmodels.tools import add_constant

    pair_id = cfg["pair_id"]
    freq = cfg["freq"]
    lead = cfg["lead_days"]
    window = 504 if freq == "daily" else 24
    trim = 0.15

    signal = df[cfg["signal_col"]]
    target = df[cfg["target_col"]]

    if cfg["hmm_signal"]:
        sig_shifted = (1.0 - signal.shift(1))
    elif cfg["vix_countercyclical"]:
        sig_shifted = -signal.shift(1)
    else:
        shift_n = 1 if freq == "daily" else lead
        sig_shifted = signal.shift(shift_n)

    combo = pd.concat([sig_shifted.rename("sig"), target.rename("tgt")], axis=1).dropna()
    n = len(combo)

    if n < window * 2:
        return dict(test="rolling_r2_qlr", breakpoint_date=None, max_f_stat=np.nan,
                    p_value=np.nan, conclusion="insufficient data", trim_pct=trim, n_obs=n)

    # Rolling OLS R²
    r2_series = []
    dates = []
    for i in range(window, n):
        sub = combo.iloc[i - window:i]
        X = add_constant(sub["sig"])
        y = sub["tgt"]
        try:
            res = OLS(y, X).fit()
            r2_series.append(res.rsquared)
        except Exception:
            r2_series.append(np.nan)
        dates.append(combo.index[i])

    r2_arr = np.array(r2_series, dtype=float)
    trim_n = int(trim * len(r2_arr))

    # Find max absolute change in R² as pseudo-QLR breakpoint
    r2_diff = np.abs(np.diff(r2_arr))
    valid = r2_diff[trim_n:-trim_n] if trim_n > 0 else r2_diff
    if len(valid) == 0:
        bp_idx = 0
        max_f = np.nan
    else:
        rel_idx = np.nanargmax(valid)
        bp_idx = rel_idx + trim_n
        max_f = float(valid[rel_idx])

    bp_date = str(dates[bp_idx].date()) if bp_idx < len(dates) else None
    p_approx = float(np.exp(-max_f * 10)) if not np.isnan(max_f) else np.nan

    conclusion = (
        f"Rolling R² jump of {max_f:.4f} detected near {bp_date}; "
        "potential structural break — verify with Chow test"
        if max_f > 0.02 else
        "No substantial structural break detected"
    )

    return dict(
        test="rolling_r2_qlr_proxy",
        breakpoint_date=bp_date,
        max_f_stat=round(max_f, 6) if not np.isnan(max_f) else None,
        p_value=round(p_approx, 6) if not np.isnan(p_approx) else None,
        conclusion=conclusion,
        trim_pct=trim,
        n_obs=n,
    )


# ── 4. Rolling Sharpe ─────────────────────────────────────────────────────────
def compute_rolling_sharpe(strat_ret, cfg):
    freq = cfg["freq"]
    factor = 252 if freq == "daily" else 12
    window = 504 if freq == "daily" else 24

    roll_mean = strat_ret.rolling(window, min_periods=window // 2).mean()
    roll_std = strat_ret.rolling(window, min_periods=window // 2).std()
    rolling_sharpe = (roll_mean / roll_std) * np.sqrt(factor)
    result = rolling_sharpe.dropna().reset_index()
    result.columns = ["date", "rolling_sharpe_24m"]
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    return result


# ── 5. Rolling Granger ────────────────────────────────────────────────────────
def compute_rolling_granger(df, strat_ret, cfg):
    freq = cfg["freq"]
    window = 504 if freq == "daily" else 24
    signal = df[cfg["signal_col"]].reindex(strat_ret.index)

    combo = pd.concat([signal.rename("sig"), strat_ret.rename("tgt")], axis=1).dropna()
    n = len(combo)
    results = []

    for i in range(window, n):
        sub = combo.iloc[i - window:i]
        date_val = combo.index[i - 1].strftime("%Y-%m-%d")
        try:
            gc_res = grangercausalitytests(sub[["tgt", "sig"]], maxlag=3, verbose=False)
            # Take max F across lags 1-3
            f_stats = [gc_res[lag][0]["ssr_ftest"][0] for lag in range(1, 4)]
            p_vals = [gc_res[lag][0]["ssr_ftest"][1] for lag in range(1, 4)]
            best_lag = int(np.argmax(f_stats)) + 1
            best_f = f_stats[best_lag - 1]
            best_p = p_vals[best_lag - 1]
            results.append(dict(date=date_val, granger_f_24m=round(best_f, 6), p_value_24m=round(best_p, 6)))
        except Exception:
            results.append(dict(date=date_val, granger_f_24m=np.nan, p_value_24m=np.nan))

    return pd.DataFrame(results)


# ── Main loop ─────────────────────────────────────────────────────────────────
summary = {}

for cfg in PAIRS:
    pid = cfg["pair_id"]
    print(f"\n{'='*60}")
    print(f"Processing: {pid}")
    print(f"{'='*60}")
    out_dir = os.path.join(BASE, f"results/{pid}")
    os.makedirs(out_dir, exist_ok=True)

    try:
        # Load data
        df = load_pair_data(cfg)
        print(f"  Loaded: {len(df)} rows, {len(df.columns)} cols")

        # Verify signal column
        if cfg["signal_col"] not in df.columns:
            raise ValueError(f"Signal column '{cfg['signal_col']}' not found. Available: {list(df.columns)[:15]}")

        # Verify target column
        if cfg["target_col"] not in df.columns:
            raise ValueError(f"Target column '{cfg['target_col']}' not found.")

        # Compute strategy returns
        strat_ret = compute_strat_ret(df, cfg)
        print(f"  Strategy returns: {len(strat_ret)} obs, mean={strat_ret.mean():.6f}")

        # 1. Sub-period Sharpe
        sp_df = compute_subperiod_sharpe(df, strat_ret, cfg)
        sp_path = os.path.join(out_dir, "subperiod_sharpe.csv")
        sp_df.to_csv(sp_path, index=False)
        print(f"  [1] subperiod_sharpe.csv written ({len(sp_df)} rows)")

        # 2. Rolling correlation
        rc_df = compute_rolling_corr(df, cfg)
        rc_path = os.path.join(out_dir, f"rolling_correlation_{pid}.csv")
        rc_df.to_csv(rc_path, index=False)
        print(f"  [2] rolling_correlation_{pid}.csv written ({len(rc_df)} rows)")

        # 3. Structural break
        sb_dict = compute_structural_break(df, cfg)
        sb_path = os.path.join(out_dir, f"structural_break_{pid}.json")
        with open(sb_path, "w") as f:
            json.dump(sb_dict, f, indent=2)
        print(f"  [3] structural_break_{pid}.json written — bp={sb_dict.get('breakpoint_date')}")

        # 4. Rolling Sharpe
        rs_df = compute_rolling_sharpe(strat_ret, cfg)
        rs_path = os.path.join(out_dir, f"rolling_sharpe_{pid}.csv")
        rs_df.to_csv(rs_path, index=False)
        print(f"  [4] rolling_sharpe_{pid}.csv written ({len(rs_df)} rows)")

        # 5. Rolling Granger (skip if too small)
        if len(strat_ret) >= 200:
            rg_df = compute_rolling_granger(df, strat_ret, cfg)
            rg_path = os.path.join(out_dir, f"rolling_granger_{pid}.csv")
            rg_df.to_csv(rg_path, index=False)
            print(f"  [5] rolling_granger_{pid}.csv written ({len(rg_df)} rows)")
        else:
            print(f"  [5] Skipped rolling Granger — insufficient data ({len(strat_ret)} obs)")

        # Sub-period quick summary
        for _, row in sp_df.iterrows():
            if not np.isnan(row["sharpe"]):
                print(f"      {row['period_name']:25s}: Sharpe={row['sharpe']:.2f}, n={row['n_obs']}")

        summary[pid] = {"status": "OK", "strat_obs": len(strat_ret),
                        "breakpoint": sb_dict.get("breakpoint_date"),
                        "subperiod_sharpes": sp_df.set_index("period_name")["sharpe"].to_dict()}

    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
        summary[pid] = {"status": "ERROR", "error": str(e)}

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("BATCH SUMMARY")
print("=" * 70)
for pid, info in summary.items():
    if info["status"] == "OK":
        sp = info.get("subperiod_sharpes", {})
        # Use first available episode Sharpe for summary (varies by indicator_category)
        first_ep_sharpe = next(
            (v for v in sp.values() if isinstance(v, float) and not np.isnan(v)), np.nan
        )
        first_ep_name = next(
            (k for k, v in sp.items() if isinstance(v, float) and not np.isnan(v)), "—"
        )
        oos = sp.get("Full OOS", np.nan)
        bp = info.get("breakpoint")
        print(f"  {pid:<25s} OK  | {first_ep_name} Sharpe={first_ep_sharpe:.2f}  OOS Sharpe={oos:.2f}  BP={bp}")
    else:
        print(f"  {pid:<25s} ERR | {info.get('error', '')[:60]}")

print("\nDone.")
