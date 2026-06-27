"""Lead-Horizon Sweep — ECON-LL1 / ECON-LA1 / ECON-LT1 producer.

Generic, reproducible producer of the two mandatory lead-evidence artifacts for
EVERY active pair (monthly granularity L = 0..12, universal per ECON-LL1):

  1. results/{pair}/lead_correlation_{date}.csv  (ECON-LA1)
       rows = signal transforms; cols = L0..L12; cell = Pearson r of the
       L-month-lagged signal vs the target's 1-MONTH FORWARD return, with
       significance stars (* p<0.05, ** p<0.01).

  2. results/{pair}/lead_tournament_{date}.csv   (ECON-LT1)
       per lead L=0..12: best OOS Sharpe + valid-combo distribution stats over
       the canonical (signal x threshold x strategy) grid, re-run at each lead.

Lead is expressed in MONTHS for all pairs. Daily pairs are resampled to
month-end (signal = last obs of month; target forward return = next-month
month-end-to-month-end return) so the lead axis is months for everyone.

Analysis artifacts ONLY. This script NEVER writes winner_summary / strategy_returns
/ charts / configs and NEVER touches any pair's published winner. (The frozen
Sample hy_ig_v2_spy was retired/archived 2026-06-20 and is no longer in the pair
set.) Pair list = the 12 registered pairs from app/components/pair_registry.py.

Author: Econ Evan
"""
from __future__ import annotations
import json, hashlib, sys
from datetime import date
import numpy as np
import pandas as pd
from scipy import stats

np.random.seed(42)

ROOT = "/workspaces/aig-rlic-plus"
RUN_DATE = "20260620"
LEADS = list(range(0, 13))  # L = 0..12 months (ECON-LL1)

# Option D (stakeholder choice): daily pairs also get a Weekly+Monthly sweep.
# Phase 2 (`--weekly`): build a W-FRI weekly frame (signal = last obs of week;
# target fwd_1w = next-week-close return), then run the SAME lead_analysis /
# lead_tournament machinery over LEADS_WEEKLY = 1..52 weeks with annualisation
# factor 52 (sqrt(52)). The frequency-dependent constants (LEADS, annualisation,
# rolling-threshold window, forward-return column) are now bundled in a FreqSpec
# so the monthly and weekly code paths share one implementation. The monthly
# path is byte-for-byte unchanged when --weekly is absent.
LEADS_WEEKLY = list(range(1, 53))  # weeks, --weekly


class FreqSpec:
    """Bundles all granularity-dependent constants so lead_analysis /
    lead_tournament / metrics / thresholds_for are frequency-agnostic.

    MONTHLY (default): month-end resample, lead 0..12 months, ann=12,
      rolling threshold window = 36 months, IS-min 24 obs.
    WEEKLY (--weekly): W-FRI resample, lead 1..52 weeks, ann=52,
      rolling threshold window = 156 weeks (~3yr, matches the 36-month window),
      IS-min 104 obs (~2yr) so weekly thresholds are as well-conditioned as the
      monthly 24-obs floor relative to their window.
    """
    def __init__(self, weekly: bool):
        self.weekly = weekly
        if weekly:
            self.tag = "weekly"
            self.resample_rule = "W-FRI"
            self.leads = LEADS_WEEKLY
            self.ann = 52
            self.roll_window = 156      # ~3 years of weeks (monthly 36 → weekly 156)
            self.roll_minp = 78
            self.is_min = 104           # ~2 years of weeks
            self.metrics_min = 26       # ~half-year floor for a scored OOS series
            self.fwd_col = "target_fwd_1w"
            self.lead_unit = "weeks"
        else:
            self.tag = "monthly"
            self.resample_rule = "ME"
            self.leads = LEADS
            self.ann = 12
            self.roll_window = 36
            self.roll_minp = 18
            self.is_min = 24
            self.metrics_min = 12
            self.fwd_col = "target_fwd_1m"
            self.lead_unit = "months"

# ── Per-pair configuration ────────────────────────────────────────────────
# data_file: raw data parquet (has target price + signal transforms)
# target_price: raw target price column (for 1-month forward return)
# freq: 'M' monthly native, 'D' daily (resample to month-end)
# signals: list of signal-transform columns to put on the Lead-Analysis rows
# winner_signal: published winner signal column (for "best lead agrees?" check)
# winner_lead / winner_sharpe: published winner (months / OOS Sharpe)
# oos_start: pair's published OOS start (ISO) — tournament scored on [oos_start:]
PAIRS = {
    "indpro_spy": dict(
        data_file="data/indpro_spy_monthly_19900101_20251231.parquet",
        target_price="spy", freq="M",
        signals=["indpro_yoy","indpro_mom","indpro_mom_3m","indpro_mom_6m",
                 "indpro_zscore_60m","indpro_accel","indpro_contraction"],
        winner_signal="indpro_mom_3m", winner_lead=6, winner_sharpe=1.1036,
        oos_start="2018-01-01"),
    "permit_spy": dict(
        data_file="data/permit_spy_monthly_20260314.parquet",
        target_price="spy", freq="M",
        signals=["permit_yoy","permit_mom","permit_mom_3m","permit_mom_6m",
                 "permit_zscore_60m","permit_accel","permit_contraction"],
        winner_signal="permit_mom", winner_lead=6, winner_sharpe=1.4454,
        oos_start="2018-01-01"),
    "vix_vix3m_spy": dict(
        data_file="data/vix_vix3m_spy_daily_20260314.parquet",
        target_price="spy", freq="D",
        signals=["vix_ratio","vix_ratio_zscore_252d","vix_ratio_zscore_126d",
                 "vix_ratio_roc_5d","vix_ratio_roc_21d","vix_ratio_mom_21d",
                 "vix_ratio_pctrank_252d","vix_backwardation","vix_term_spread"],
        winner_signal="vix_ratio_zscore_126d", winner_lead=0, winner_sharpe=1.1295,
        oos_start="2020-01-01"),
    "indpro_xlp": dict(
        data_file="data/indpro_xlp_monthly_19980101_20251231.parquet",
        target_price="xlp", freq="M",
        signals=["indpro_yoy","indpro_mom","indpro_mom_3m","indpro_mom_6m",
                 "indpro_zscore_60m","indpro_accel","indpro_contraction"],
        winner_signal="indpro_accel", winner_lead=3, winner_sharpe=1.1147,
        oos_start="2019-01-31"),
    "hy_ig_spy": dict(
        data_file="data/hy_ig_spy_daily_20000101_20260422.parquet",
        extra_signal_file="results/hy_ig_spy/signals_20260422.parquet",
        extra_signal_cols=["hmm_2state_prob_stress","ms_2state_stress_prob"],
        target_price="spy", freq="D",
        signals=["hy_ig_spread_pct","hy_ig_zscore_252d","hy_ig_zscore_504d",
                 "hy_ig_pctrank_504d","hy_ig_roc_21d","hy_ig_roc_63d",
                 "hy_ig_mom_21d","hy_ig_mom_63d","hy_ig_acceleration",
                 "hmm_2state_prob_stress"],
        winner_signal="hmm_2state_prob_stress", winner_lead=0, winner_sharpe=1.4083,
        oos_start="2019-10-01"),
    "umcsent_xlv": dict(
        data_file="data/umcsent_xlv_monthly_19980101_20251231.parquet",
        target_price="xlv", freq="M",
        signals=["umcsent_yoy","umcsent_mom","umcsent_zscore","umcsent_3m_ma",
                 "umcsent_direction","umcsent_dev_ma"],
        winner_signal="umcsent_yoy", winner_lead=6, winner_sharpe=1.0202,
        oos_start="2019-04-30"),
    "gold_copper_xli": dict(
        data_file="data/gold_copper_xli_daily_20260526.parquet",
        target_price="xli", freq="D",
        signals=["gold_copper_zscore_126d","gold_copper_zscore_252d",
                 "gold_copper_pctrank_504d","gold_copper_roc_21d",
                 "gold_copper_roc_63d","gold_copper_mom_21d","gold_copper_mom_63d",
                 "gold_copper_acceleration"],
        winner_signal="gold_copper_zscore_126d", winner_lead=0, winner_sharpe=1.273,
        oos_start="2020-01-01"),
    "busloans_spy": dict(
        data_file="data/busloans_spy_monthly_19470131_20260531.parquet",
        target_price="spy", freq="M",
        signals=["busloans_pct_yoy","busloans_pct_mom","busloans_3m_pct",
                 "busloans_6m_pct","busloans_dev_trend_pct","busloans_zscore_60m",
                 "busloans_accel_pct","busloans_contraction"],
        winner_signal="busloans_pct_mom", winner_lead=6, winner_sharpe=1.4999,
        oos_start="2018-02-28"),
    # ── Post-suspend pairs (added 2026-06-20, resumed lead-horizon wave) ──────
    "ism_services_spy": dict(  # monthly
        data_file="data/ism_services_spy_monthly_19970731_20251031.parquet",
        target_price="spy", freq="M",
        signals=["ism_services_gap_50","ism_services_delta","ism_services_3m_change",
                 "ism_services_6m_change","ism_services_zscore_60m",
                 "ism_services_above_50"],
        winner_signal="ism_services_gap_50", winner_lead=3, winner_sharpe=1.5377,
        oos_start="2018-10-31"),
    "m2sl_yoy_spy": dict(  # monthly
        data_file="data/m2sl_yoy_spy_monthly_19930131_20260430.parquet",
        target_price="spy", freq="M",
        signals=["m2sl_pct_yoy","m2sl_pct_mom","m2sl_3m_pct","m2sl_6m_pct",
                 "m2sl_yoy_accel_pct","m2sl_yoy_zscore_120m","m2sl_contraction_flag"],
        winner_signal="m2sl_yoy_accel_pct", winner_lead=2, winner_sharpe=1.6882,
        oos_start="2018-01-31"),
    "phlxsox_spy": dict(  # daily (^SOX/SPY ratio) — resampled to month-end per ECON-LL1
        data_file="data/phlxsox_spy_daily_19940504_20260617.parquet",
        target_price="spy", freq="D",
        signals=["sox_spy_ratio","sox_spy_logratio","sox_spy_ratio_mom_3m_pct",
                 "sox_spy_ratio_mom_6m_pct","sox_spy_ratio_mom_12m_pct",
                 "sox_spy_ratio_zscore_12m"],
        winner_signal="sox_spy_ratio_mom_6m_pct", winner_lead=3, winner_sharpe=1.57,
        oos_start="2021-06-11"),  # published lead 63d ≈ 3 months (ECON-LL1)
    "petrol_inv_spy": dict(  # monthly
        data_file="data/petrol_inv_spy_monthly_19900131_20250930.parquet",
        target_price="spy", freq="M",
        signals=["petrol_inv_pct_yoy","petrol_inv_pct_chg","petrol_inv_3m_pct",
                 "petrol_inv_6m_pct","petrol_inv_dev_trend_pct","petrol_inv_zscore_60m",
                 "petrol_inv_yoy_zscore_60m","petrol_inv_accel_pct"],
        winner_signal="petrol_inv_3m_pct", winner_lead=12, winner_sharpe=1.4779,
        oos_start="2017-08-31"),
}

TRADING_DAYS_PER_MONTH = 21  # documented ECON-LL1 conversion for design_note


def star(p):
    return "**" if p < 0.01 else ("*" if p < 0.05 else "")


def to_frame(df, target_price, signals, freq, spec):
    """Return a resampled frame: signal cols (period-end last obs) + target
    1-period-forward return, at the granularity defined by `spec`.

    For daily pairs we resample signal+price to the period end (month-end for
    monthly, W-FRI for weekly) and fwd = price.shift(-1)/price - 1.
    For monthly-native pairs under the monthly spec the frame is already
    period-end (resample to ME is idempotent on month-end data).
    """
    cols = [c for c in signals if c in df.columns] + [target_price]
    sub = df[cols].copy()
    # daily → resample to the spec's period; monthly-native + monthly spec is a
    # no-op resample; weekly spec is only ever applied to daily pairs.
    if freq == "D" or spec.weekly:
        sub = sub.resample(spec.resample_rule).last()
    px = sub[target_price]
    fwd = px.shift(-1) / px - 1.0
    out = sub[[c for c in signals if c in df.columns]].copy()
    out[spec.fwd_col] = fwd
    return out


def to_monthly(df, target_price, signals, freq):
    """Back-compat monthly wrapper (unchanged behaviour)."""
    return to_frame(df, target_price, signals, freq, FreqSpec(weekly=False))


def lead_analysis(mdf, signals, spec):
    """ECON-LA1: Pearson r(signal lagged L periods, target_fwd), over spec.leads."""
    fwd = mdf[spec.fwd_col]
    rows = []
    best = {}
    for s in signals:
        if s not in mdf.columns:
            continue
        row = {"transform": s}
        rvals = {}
        for L in spec.leads:
            lagged = mdf[s].shift(L)
            d = pd.concat([lagged, fwd], axis=1).dropna()
            if len(d) < spec.is_min:
                row[f"L{L}"] = ""
                continue
            r, p = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
            rvals[L] = r
            row[f"L{L}"] = f"{r:+.3f}{star(p)}"
        if rvals:
            bL = max(rvals, key=lambda k: abs(rvals[k]))
            row["best_lead"] = f"L{bL}"
            row["best_r"] = f"{rvals[bL]:+.3f}"
            best[s] = (bL, rvals[bL])
        rows.append(row)
    cols = ["transform"] + [f"L{L}" for L in spec.leads] + ["best_lead", "best_r"]
    return pd.DataFrame(rows)[cols], best


# Canonical threshold grid (fixed IS-percentile + rolling-percentile + rolling-z),
# applied per signal. Probability-style signals (HMM/MS, range [0,1]) get fixed
# absolute thresholds too. Direction handled per-strategy below.
def thresholds_for(sig_is, sig_full, spec):
    out = {}
    for q in (0.10, 0.25, 0.75, 0.90):
        out[f"Tp{int(q*100)}"] = pd.Series(sig_is.quantile(q), index=sig_full.index)
    rw, rp = spec.roll_window, spec.roll_minp
    out["Trp75"] = sig_full.rolling(rw, min_periods=rp).quantile(0.75)
    out["Trp25"] = sig_full.rolling(rw, min_periods=rp).quantile(0.25)
    out["Tz1"] = (sig_full.rolling(rw, min_periods=rp).mean()
                  + 1.0 * sig_full.rolling(rw, min_periods=rp).std())
    # probability-style signal in [0,1]
    if sig_full.dropna().between(0, 1).mean() > 0.98:
        out["Tfix05"] = pd.Series(0.5, index=sig_full.index)
        out["Tfix07"] = pd.Series(0.7, index=sig_full.index)
    return out


def metrics(r, spec):
    r = r.dropna()
    if len(r) < spec.metrics_min:
        return None
    ann_ret = r.mean() * spec.ann
    ann_vol = r.std() * np.sqrt(spec.ann)
    if ann_vol <= 0:
        return None
    sharpe = ann_ret / ann_vol
    cum = (1 + r).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()
    return dict(sharpe=sharpe, ann_return=ann_ret, max_dd=float(dd.min()),
                n=len(r), turnover=None)


def lead_tournament(mdf, signals, oos_start, is_end, spec):
    """ECON-LT1: full (signal x threshold x strategy) grid swept across spec.leads.

    Returns at the spec granularity. position applied with a 1-period execution
    shift (no lookahead). Strategies: P1 long/cash, P2 long/short (covers both
    signal polarities so the lead grid is direction-agnostic and we keep the best).
    OOS Sharpe computed on [oos_start:] with spec annualisation.
    """
    fwd = mdf[spec.fwd_col]
    # period target return realised at t (for position applied at t-1)
    tgt_ret = fwd.shift(1)  # return earned over period t given fwd known at t-1
    per_lead = {L: [] for L in spec.leads}
    for s in signals:
        if s not in mdf.columns:
            continue
        sraw = mdf[s]
        for L in spec.leads:
            lag = sraw.shift(L)
            sig_is = lag.loc[:is_end].dropna()
            if len(sig_is) < spec.is_min:
                continue
            thr = thresholds_for(sig_is, lag, spec)
            for tname, tser in thr.items():
                above = (lag > tser)
                for pol in ("hi", "lo"):  # signal-high-bullish vs signal-low-bullish
                    bull = above if pol == "hi" else (~above)
                    bull = bull.where(lag.notna() & tser.notna())
                    for strat in ("P1", "P2"):
                        if strat == "P1":
                            pos = bull.astype(float)
                        else:
                            pos = bull.astype(float) * 2 - 1
                        # 1-period execution shift to avoid lookahead
                        ret = pos.shift(1) * tgt_ret
                        oos = ret.loc[oos_start:]
                        m = metrics(oos, spec)
                        if m is None:
                            continue
                        nchg = int((pos.loc[oos_start:].diff().abs() > 0).sum())
                        valid = (m["sharpe"] >= 0.3) and (nchg >= 3)
                        per_lead[L].append(dict(
                            signal=s, threshold=tname, polarity=pol,
                            strategy=strat, oos_sharpe=m["sharpe"],
                            oos_ann_return=m["ann_return"], oos_max_dd=m["max_dd"],
                            n_changes=nchg, valid=valid))
    # summarise per lead. Column `lead_months` retains its legacy name as the
    # lead-index column for both granularities (value = weeks under --weekly);
    # `lead_unit` disambiguates.
    summ = []
    for L in spec.leads:
        rows = [r for r in per_lead[L] if r["valid"]]
        if not rows:
            summ.append(dict(lead_months=L, lead_unit=spec.lead_unit, n_valid=0,
                             best_oos_sharpe=np.nan,
                             median_oos_sharpe=np.nan, p25_oos_sharpe=np.nan,
                             p75_oos_sharpe=np.nan, best_signal="", best_threshold="",
                             best_strategy="", best_max_dd=np.nan))
            continue
        rd = pd.DataFrame(rows)
        b = rd.loc[rd["oos_sharpe"].idxmax()]
        summ.append(dict(
            lead_months=L, lead_unit=spec.lead_unit, n_valid=len(rd),
            best_oos_sharpe=round(float(b["oos_sharpe"]), 4),
            median_oos_sharpe=round(float(rd["oos_sharpe"].median()), 4),
            p25_oos_sharpe=round(float(rd["oos_sharpe"].quantile(0.25)), 4),
            p75_oos_sharpe=round(float(rd["oos_sharpe"].quantile(0.75)), 4),
            best_signal=b["signal"], best_threshold=f'{b["threshold"]}_{b["polarity"]}',
            best_strategy=b["strategy"], best_max_dd=round(float(b["oos_max_dd"]), 4)))
    return pd.DataFrame(summ)


def main():
    args = sys.argv[1:]
    weekly = "--weekly" in args
    only = [a for a in args if not a.startswith("--")] or list(PAIRS)
    spec = FreqSpec(weekly=weekly)
    suffix = "_weekly" if weekly else ""
    gate_rows = []
    for pair in only:
        cfg = PAIRS[pair]
        # Weekly sweep is ONLY meaningful for daily-native pairs (you cannot
        # resample a monthly series up to weekly). Guard so a stray monthly pair
        # under --weekly is skipped rather than producing a degenerate frame.
        if weekly and cfg["freq"] != "D":
            print(f"{pair}: SKIP (weekly sweep requires daily-native data; "
                  f"freq={cfg['freq']})")
            continue
        df = pd.read_parquet(f"{ROOT}/{cfg['data_file']}")
        df = df[~df.index.duplicated(keep="last")].sort_index()
        if cfg.get("extra_signal_file"):
            ex = pd.read_parquet(f"{ROOT}/{cfg['extra_signal_file']}")
            ex = ex[~ex.index.duplicated(keep="last")].sort_index()
            for c in cfg["extra_signal_cols"]:
                if c in ex.columns:
                    df[c] = ex[c].reindex(df.index)
        mdf = to_frame(df, cfg["target_price"], cfg["signals"], cfg["freq"], spec)
        # IS end = period before oos_start
        oos_start = pd.Timestamp(cfg["oos_start"])
        is_end = (oos_start - pd.Timedelta(days=1))

        la_df, best = lead_analysis(mdf, cfg["signals"], spec)
        lt_df = lead_tournament(mdf, cfg["signals"], oos_start, is_end, spec)

        # Frozen Sample: NEVER write into its results dir — route to _cross_agent.
        if cfg.get("frozen"):
            out_dir = f"{ROOT}/results/_cross_agent/{pair}_lead_readonly"
        else:
            out_dir = f"{ROOT}/results/{pair}"
        import os; os.makedirs(out_dir, exist_ok=True)
        la_path = f"{out_dir}/lead_correlation{suffix}_{RUN_DATE}.csv"
        lt_path = f"{out_dir}/lead_tournament{suffix}_{RUN_DATE}.csv"
        la_df.to_csv(la_path, index=False)
        lt_df.to_csv(lt_path, index=False)

        # ── gate decision ────────────────────────────────────────────────────
        # POLARITY-MIRROR GUARDRAIL: this sweep ranks on best OOS Sharpe over a
        # P1/P2 + hi/lo-polarity grid, which has a false-positive mode (it can
        # flag the negative-image of an invalid native combo). The sweep is
        # therefore EXPLORATORY ONLY. The monthly path emits a RE-RUN/CHARTS-ONLY
        # gate that a NATIVE tournament must confirm (ECON-LT1). The WEEKLY path
        # is even further from a native winner (different granularity entirely),
        # so it NEVER emits an actionable RE-RUN — only a CANDIDATE flag for
        # native weekly confirmation. No weekly upgrade counts until a native
        # weekly tournament reproduces it.
        valid_lt = lt_df.dropna(subset=["best_oos_sharpe"])
        Lstar = int(valid_lt.loc[valid_lt["best_oos_sharpe"].idxmax(), "lead_months"])
        best_sharpe = float(valid_lt["best_oos_sharpe"].max())
        if weekly:
            decision = ("CANDIDATE-WEEKLY" if best_sharpe > cfg["winner_sharpe"]
                        else "NO-WEEKLY-EDGE")
        else:
            decision = ("RE-RUN" if (Lstar in range(7, 13)
                        and best_sharpe > cfg["winner_sharpe"]) else "CHARTS-ONLY")
        # best lead from correlation for the winner signal
        wbest = best.get(cfg["winner_signal"])
        wbest_lead = f"L{wbest[0]}" if wbest else "n/a"

        manifest = dict(
            pair=pair, run_date=RUN_DATE, frozen=cfg.get("frozen", False),
            granularity=(f"{spec.lead_unit} L{spec.leads[0]}..{spec.leads[-1]} "
                         "(ECON-LL1 weekly extension)" if weekly
                         else "months L0..12 (ECON-LL1)"),
            freq_native=cfg["freq"],
            sweep_kind=spec.tag,
            annualisation=spec.ann,
            design_note=(
                ("Daily pair resampled to W-FRI (signal=last obs of week; "
                 "target fwd_1w = week-end-to-week-end close return). Lead grid "
                 "is 1..52 weeks. EXPLORATORY ONLY — native weekly tournament "
                 "required to confirm any candidate (polarity-mirror guardrail).")
                if weekly else
                ("Daily pair resampled to month-end (signal=last obs of month; "
                 f"target fwd_1m = month-end-to-month-end). 1 month = ~{TRADING_DAYS_PER_MONTH} "
                 "trading days. Lead grid is months for all pairs."
                 if cfg["freq"] == "D" else
                 "Native monthly; lead L = calendar-month shift on month-end signals.")),
            oos_start=cfg["oos_start"], is_end=str(is_end.date()),
            input_file=cfg["data_file"],
            input_sha256="sha256:" + hashlib.sha256(
                open(f"{ROOT}/{cfg['data_file']}", "rb").read()).hexdigest()[:16],
            lead_correlation_file=la_path.split("results/")[1],
            lead_tournament_file=lt_path.split("results/")[1],
            published_winner=dict(signal=cfg["winner_signal"], lead=cfg["winner_lead"],
                                  oos_sharpe=cfg["winner_sharpe"]),
            L_star=Lstar, best_oos_sharpe_at_grid=best_sharpe,
            gate_decision=decision,
            winner_signal_best_corr_lead=wbest_lead,
            assertions=([
                f"weekly lead grid is exactly L{spec.leads[0]}..L{spec.leads[-1]}",
                "best_oos_sharpe is the max over the weekly grid",
                "EXPLORATORY: CANDIDATE-WEEKLY flag requires native weekly "
                "tournament confirmation — sweep never auto-promotes a winner",
            ] if weekly else [
                "lead grid is exactly L0..12",
                "best_oos_sharpe is the max over the extended grid",
                f"decision RE-RUN iff L*∈7..12 AND best>{cfg['winner_sharpe']}",
            ]),
        )
        with open(f"{out_dir}/lead_sweep_manifest{suffix}_{RUN_DATE}.json", "w") as f:
            json.dump(manifest, f, indent=2)

        gate_rows.append(dict(
            pair=pair, published_lead=cfg["winner_lead"], L_star=Lstar,
            lead_unit=spec.lead_unit,
            best_sharpe_at_Lstar=round(best_sharpe, 4),
            published_sharpe=cfg["winner_sharpe"], decision=decision,
            winner_corr_best_lead=wbest_lead))
        print(f"{pair}: L*={Lstar}{spec.lead_unit[0]} best={best_sharpe:.3f} "
              f"pub_lead={cfg['winner_lead']} pub_sharpe={cfg['winner_sharpe']} "
              f"-> {decision} (winner-signal corr best lead {wbest_lead})")

    gdf = pd.DataFrame(gate_rows)
    print(f"\n=== GATE TABLE ({spec.tag}) ===")
    print(gdf.to_string(index=False))
    gdf.to_csv(f"{ROOT}/results/_cross_agent/lead_horizon_gate{suffix}_{RUN_DATE}.csv",
               index=False)


if __name__ == "__main__":
    main()
