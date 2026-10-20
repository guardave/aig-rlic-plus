#!/usr/bin/env python3
"""Pair pipeline: Portland cement shipments (Texas, then U.S. portland-only; USGS MIS) x SPY (Phase B, single track).

Series (user ruling 2026-10-19: kept as is, named correctly and disclosed): the Data Master column equals the Texas
total (USGS Mineral Industry Surveys) through 2023-12; from 2024-01 it is the U.S. portland-only all-destination
total of MIS Table 2a (excludes blended cement, including Type IL). The 2024 year-over-year growth rates span that
change of coverage and are not economic changes.


The tournament runs on scripts/harness (spec: scripts/pair_spec_cement_spy.py) on ONE track: USGS cement shipments
have no public archive of past values (registry value_vintage revised_no_archive), so the rule uses today's values
with point-in-time release timing (a month's reading is used only after its release date; release calendar series
USGS_CEMENT_MIS). The winner is selected on in-sample data by the D9 lead-plateau rule over the registry grid
L5..L14 (position_shift 0: the lead is the whole lag from the reading month to the return month); null tournament
K=100 (circular shift of the cement level inside its data span), paired block bootstrap versus buy-and-hold SPY,
leak tests. The published 20261016 pipeline (raw IS-Sharpe argmax, fixed shift(lead)) is replayed by the harness
(LEGACY_SPEC).

This file keeps the pair's evidence stages (stationarity, correlations, Granger, cross-correlation, quartiles, local
projections, quantile regression, rolling stability), computed on the same revised panel and descriptive only, plus
validation tables, metadata and the narrative-provenance record.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_cement_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series, write_json  # noqa: E402
from harness.data import load_pinned  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "cement_spy"
DATE_TAG = "20261020"  # Phase B B1s post-Codex rerun: single track (revised, no archive), D9, L5..L14, null v4 K=100
TARGET_SYMBOL = "SPY"
COST_BPS = 5
EXPECTED_DIRECTION = "procyclical"
EVIDENCE_SIGNAL = "cement_yoy"        # year-over-year growth: the representative transform of the descriptive tests
HORIZONS = (1, 3, 6, 12)              # forward-return horizons (months) of the descriptive tests
GRANGER_MAX_LAG = 12                  # Granger: lags 1..12; the smallest p is Bonferroni-adjusted for 12 lags
QR_BLOCK = 6                          # quantile regression: moving-block bootstrap block (months)
QR_DRAWS = 999                        # quantile regression: bootstrap draws (seed 42)
ROLL_CORR_WINDOW = 60                 # rolling correlation window (months; min 36 observations)
POSITION_CHANGE_THRESHOLD_PP = 5      # a test-period month counts as a position change above this size
MAIN_SITE_TAG = "20260830"            # the run whose rule the main site shows (selected on test-period Sharpe, legacy)
TABLE2A = "usgs_mis_202506_table2a_total.csv"   # pinned USGS MIS Table 2a monthly totals (basis check only)
SERIES_NAME = ("Portland cement shipments: Texas (USGS Mineral Industry Surveys) through 2023-12; from 2024-01 the "
               "U.S. portland-only all-destination total (USGS Mineral Industry Surveys Table 2a)")

DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS
STAGE_TIMES: dict[str, float] = {}


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(12)) if len(r) > 1 and r.std() > 0 else 0.0


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    """Monthly performance block used by the descriptive tables (quartiles, sub-periods)."""
    rets = rets.dropna()
    if len(rets) < 2 or rets.std() == 0:
        return {"sharpe": 0.0, "ann_return": 0.0, "max_drawdown": 0.0, "n": int(len(rets))}
    eq = (1 + rets).cumprod()
    return {"sharpe": sharpe(rets), "ann_return": float((1 + rets).prod() ** (12 / len(rets)) - 1),
            "max_drawdown": float((eq / eq.cummax() - 1).min()), "n": int(len(rets))}


def hac_lags(n: int, h: int) -> int:
    """Newey-West lags: the usual rule of thumb, never below h-1 for overlapping h-month returns."""
    return max(int(0.75 * n ** (1 / 3)), h - 1)


# ---------------------------------------------------------------------------------------------------- panel
def build_panel() -> pd.DataFrame:
    """Cement levels (pinned 2026-10-16 Data Master snapshot) and pinned SPY month-end closes on the rebalance grid
    (2005-11..2025-06, the months with a cement reading). Forward SPY returns use later pinned closes where the
    horizon runs past the last cement month."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels()
    df = lv.reindex(idx)
    df.index.name = "date"
    feats = spec_mod.features(lv)
    for col in SIGNALS.values():
        df[col] = feats[col].reindex(idx)
    px = spec_mod.target_prices()
    px = px.reindex(pd.date_range(px.index.min(), px.index.max(), freq="ME"))
    df["spy"] = px.reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for h in HORIZONS:
        df[f"spy_fwd_{h}m"] = (px.shift(-h) / px - 1).reindex(idx)
    df.to_parquet(DATA_DIR / "cement_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_cement_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_cement_spy_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "cement", "Display Name": "Portland cement shipments (Texas, then U.S. portland-only)",
         "Description": SERIES_NAME + " (monthly, metric tons)",
         "Source": "Data Master.xlsx sheet 'Portland Cement' (pinned snapshot "
                   "data/release_calendar/snapshots/20261016T232733Z/USGS_CEMENT.csv)",
         "Series ID": "Data Master 'Mat - Portland Cment Shipmts' (snapshot USGS_CEMENT; release calendar USGS_CEMENT_MIS)",
         "Unit": "Metric tons",
         "Transformation": "Monthly level; only growth transforms are traded",
         "Seasonal Adj.": "As published in Data Master",
         "Direction Convention": "Higher growth = more construction activity",
         "Effective Start": str(df["cement"].first_valid_index().date()),
         "Known Quirks": "Coverage change at 2024-01 (Texas total -> U.S. portland-only Table 2a total; the 2024 "
                         "year-over-year growth rates are an artifact of it); portland-only excludes blended cement "
                         "(Type IL); no archive of first-published values (value_vintage revised_no_archive); "
                         "published about 2-5 months after the month; Data Master ends 2025-06",
         "Display Note": "Construction-activity indicator; the trending level is never a signal.",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/Data Master.xlsx"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD",
         "Transformation": "Month-end adjusted close", "Seasonal Adj.": "N/A",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()), "Known Quirks": "ETF history begins in 1993",
         "Display Note": "Equity-market target and benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_cement_spy_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def stage_data_integrity(df: pd.DataFrame) -> dict:
    """Basis check of the shipment column against the state columns of the same Data Master sheet. Through 2023-12
    the column used ('Mat - Portland Cment Shipmts') equals the Texas total (Northern + Southern Texas) to the
    ton; from 2024-01 it is several times the Texas total (a different, undocumented basis), a level break inside
    the test period. Recorded so the pages can state it factually; the series is used as pinned (published input)."""
    import openpyxl
    wb = openpyxl.load_workbook(str(DATA_DIR / "Data Master.xlsx"), read_only=True, data_only=True)
    ws = wb["Portland Cement"]
    rows = [r[:5] for r in ws.iter_rows(min_row=2, values_only=True) if r and hasattr(r[0], "year")]
    m = pd.DataFrame(rows, columns=["date", "used", "tx_north", "tx_south", "tx_total"]).set_index("date")
    m = m.apply(pd.to_numeric, errors="coerce").dropna(subset=["used"])
    m.index = pd.DatetimeIndex(m.index) + pd.offsets.MonthEnd(0)
    if not np.allclose(m["used"].to_numpy(), df["cement"].reindex(m.index).to_numpy()):
        raise ValueError("Data Master column differs from the pinned snapshot")
    eq = (m["used"] - m["tx_total"]).abs() < 1
    div = m.index[~eq]
    ratio = (m["used"] / m["tx_total"])[~eq]
    yoy = df["cement_yoy"]
    t2a = load_pinned(TABLE2A)["table2a_total_shipments_t"]
    post = m.loc[m.index >= div[0], "used"] if len(div) else m["used"].iloc[:0]
    both = post.index.intersection(t2a.index)
    match = (post.reindex(both) - t2a.reindex(both)).abs() < 1
    y24 = yoy[(yoy.index.year == div[0].year)] if len(div) else yoy.iloc[:0]
    out = {"pair_id": PAIR_ID, "source": "data/Data Master.xlsx sheet 'Portland Cement'",
           "column_used": "Mat - Portland Cment Shipmts (column 1)",
           "comparison_column": "Portland Cement Shipments by State, Texas, Metric Tons (column 4)",
           "n_months": int(len(m)), "n_months_equal_texas_total": int(eq.sum()),
           "last_month_equal_texas_total": m.index[eq][-1].strftime("%Y-%m"),
           "first_month_not_equal": div[0].strftime("%Y-%m") if len(div) else None,
           "n_months_not_equal": int(len(div)),
           "ratio_to_texas_after_break_min": float(ratio.min()) if len(div) else None,
           "ratio_to_texas_after_break_max": float(ratio.max()) if len(div) else None,
           "max_yoy_growth_pct": float(yoy.max()), "max_yoy_growth_month": yoy.idxmax().strftime("%Y-%m"),
           "break_year_yoy_min_pct": float(y24.min()) if len(y24) else None,
           "break_year_yoy_max_pct": float(y24.max()) if len(y24) else None,
           "table2a_label": "Table 2a",
           "table2a_source": "USGS Mineral Industry Surveys, Cement, June 2025 edition, Table 2a total shipments "
                             f"(data/phaseB_inputs/{TABLE2A})",
           "n_months_compared_table2a": int(len(both)), "n_months_equal_table2a": int(match.sum()),
           "first_month_equal_table2a": both[match.to_numpy()][0].strftime("%Y-%m") if match.any() else None,
           "last_month_equal_table2a": both[match.to_numpy()][-1].strftime("%Y-%m") if match.any() else None,
           "reading": "Through the last month equal to the Texas total the series is Texas Portland cement shipments; "
                      "from the first unequal month it equals the U.S. portland-only all-destination total of MIS "
                      "Table 2a (blended cement, including Type IL, excluded), so growth rates across the change of "
                      "coverage are not economic changes. User ruling 2026-10-19: series kept, named and disclosed."}
    (RES / f"data_integrity_{DATE_TAG}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"  basis check: {out['n_months_equal_texas_total']}/{out['n_months']} months equal the Texas total; "
          f"break at {out['first_month_not_equal']}; {out['n_months_equal_table2a']}/{out['n_months_compared_table2a']} "
          "later months equal the MIS Table 2a total")
    return out


# ---------------------------------------------------------------------------------------------------- evidence
def stage_stationarity(df: pd.DataFrame) -> None:
    from statsmodels.tsa.stattools import adfuller, kpss
    rows = []
    for col in ["cement", "cement_yoy", "cement_mom", "cement_3m", "cement_6m", "cement_yoy_zscore_60m",
                "cement_accel", "spy_ret"]:
        s = df[col].dropna()
        adf = adfuller(s, autolag="AIC")
        rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1], "lags": adf[2],
                     "n": len(s), "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kp = kpss(s, regression="c", nlags="auto")
        rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1], "lags": kp[2],
                     "n": len(s), "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
    pd.DataFrame(rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)


def _hac_corr_p(x: pd.Series, y: pd.Series, h: int) -> tuple[float, int]:
    """p-value of a correlation robust to overlapping h-month returns: slope of standardized y on standardized x
    with HAC (Newey-West) errors, lags >= h-1."""
    import statsmodels.api as sm
    zx, zy = (x - x.mean()) / x.std(), (y - y.mean()) / y.std()
    lags = hac_lags(len(x), h)
    fit = sm.OLS(zy.to_numpy(), sm.add_constant(zx.to_numpy())).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(fit.pvalues[1]), lags


def stage_correlations(df: pd.DataFrame) -> None:
    rows = []
    for code, col in SIGNALS.items():
        for h in HORIZONS:
            sub = df[[col, f"spy_fwd_{h}m"]].dropna()
            r, p_iid = stats.pearsonr(sub[col], sub[f"spy_fwd_{h}m"])
            p_hac, lags = _hac_corr_p(sub[col], sub[f"spy_fwd_{h}m"], h)
            rows.append({"signal": col, "signal_code": code, "horizon_months": h, "metric": "pearson",
                         "correlation": float(r), "p_value": p_hac, "p_value_iid": float(p_iid), "nw_lags": lags,
                         "n": len(sub)})
    pd.DataFrame(rows).to_csv(CORE / "correlations.csv", index=False)


def stage_granger(df: pd.DataFrame) -> dict:
    """Granger tests in both directions, lags 1..GRANGER_MAX_LAG (statsmodels column order: [effect, cause]).
    Twelve lags are tried, so the smallest p per direction is also reported Bonferroni-adjusted (x12, capped 1)."""
    from statsmodels.tsa.stattools import grangercausalitytests
    d = df[["spy_ret", EVIDENCE_SIGNAL]].dropna()
    rows = []
    for direction, cols in (("cement_to_SPY", ["spy_ret", EVIDENCE_SIGNAL]),
                            ("SPY_to_cement", [EVIDENCE_SIGNAL, "spy_ret"])):
        tests = grangercausalitytests(d[cols], maxlag=GRANGER_MAX_LAG, verbose=False)
        for lag, res in tests.items():
            f, p, _, _ = res[0]["ssr_ftest"]
            rows.append({"lag": lag, "f_stat": f, "p_value": p, "direction": direction, "n": len(d)})
    g = pd.DataFrame(rows)
    g.to_csv(CORE / "granger_causality.csv", index=False)
    g[g["direction"] == "cement_to_SPY"].to_csv(RES / "granger_by_lag.csv", index=False)
    out = {}
    for direction in ("cement_to_SPY", "SPY_to_cement"):
        sub = g[g["direction"] == direction]
        j = sub["p_value"].idxmin()
        out[direction] = {"min_p": float(sub.loc[j, "p_value"]), "min_p_lag": int(sub.loc[j, "lag"]),
                          "min_p_bonferroni": float(min(1.0, GRANGER_MAX_LAG * sub.loc[j, "p_value"]))}
    return out


def stage_ccf(df: pd.DataFrame) -> None:
    """Cross-correlation of the monthly change in year-over-year cement growth (first difference, a simple
    pre-whitening of the persistent YoY series) with SPY returns; positive lag = cement leads."""
    x = df[EVIDENCE_SIGNAL].diff()
    y = df["spy_ret"]
    rows = []
    for lag in range(-12, 13):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        corr = float(sub.iloc[:, 0].corr(sub.iloc[:, 1]))
        band = 1.96 / np.sqrt(len(sub))
        rows.append({"lag": lag, "ccf": corr, "upper_ci": band, "lower_ci": -band, "n": len(sub),
                     "significant": bool(abs(corr) > band)})
    pd.DataFrame(rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)


def stage_quartiles(df: pd.DataFrame) -> None:
    """SPY return in the same month by quartile of year-over-year cement growth (concurrent, descriptive)."""
    sub = df[[EVIDENCE_SIGNAL, "spy_ret"]].dropna()
    q = pd.qcut(sub[EVIDENCE_SIGNAL], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        rets = sub.loc[q == label, "spy_ret"]
        rows.append({"quartile": label, "mean_return": float(rets.mean()), "sharpe": ann_metrics(rets)["sharpe"],
                     "n": int(len(rets)), "yoy_low": float(sub.loc[q == label, EVIDENCE_SIGNAL].min()),
                     "yoy_high": float(sub.loc[q == label, EVIDENCE_SIGNAL].max())})
    pd.DataFrame(rows).to_csv(RES / "regime_quartile_returns.csv", index=False)


def stage_local_projections(df: pd.DataFrame) -> None:
    """spy_fwd_h ~ cement_yoy by OLS, HAC (Newey-West) errors with lags >= h-1 (overlapping returns)."""
    import statsmodels.api as sm
    rows = []
    for h in HORIZONS:
        s = df[[EVIDENCE_SIGNAL, f"spy_fwd_{h}m"]].dropna()
        lags = hac_lags(len(s), h)
        fit = sm.OLS(s[f"spy_fwd_{h}m"].to_numpy(), sm.add_constant(s[EVIDENCE_SIGNAL].to_numpy())).fit(
            cov_type="HAC", cov_kwds={"maxlags": lags})
        rows.append({"horizon": h, "coef": float(fit.params[1]), "se": float(fit.bse[1]),
                     "t_stat": float(fit.tvalues[1]), "p_value": float(fit.pvalues[1]),
                     "r_squared": float(fit.rsquared), "n": int(fit.nobs), "nw_lags": lags,
                     "se_method": "HAC Newey-West, lags max(0.75 n^(1/3), h-1)"})
    lp = pd.DataFrame(rows)
    lp.to_csv(CORE / "local_projections.csv", index=False)
    lp.to_csv(CORE / "predictive_regressions.csv", index=False)


def _block_indices(n: int, block: int, rng) -> np.ndarray:
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=nb)
    return np.concatenate([np.arange(s0, s0 + block) for s0 in starts])[:n]


def stage_quantile_regression(df: pd.DataFrame) -> dict:
    """Real quantile regression (statsmodels QuantReg, one fit per tau) of the 3-month forward SPY return on
    year-over-year cement growth. Overlapping 3-month returns make the default (iid) errors too small, so the
    per-tau standard errors, 95% intervals and p-values and the cross-quantile slope-equality Wald test all use a
    moving-block bootstrap (block QR_BLOCK months, QR_DRAWS draws, seed 42); the Wald statistic is
    d' S^-1 d with d the slope differences from the median tau and S their bootstrap covariance, chi2(k-1)."""
    import statsmodels.formula.api as smf
    from _quantile_regression import DEFAULT_QUANTILES, fit_quantile_regression
    data = df[[EVIDENCE_SIGNAL, "spy_fwd_3m"]].dropna().rename(columns={EVIDENCE_SIGNAL: "x", "spy_fwd_3m": "y"})
    qs = list(DEFAULT_QUANTILES)
    point, _iid_test = fit_quantile_regression(data["x"], data["y"], qs)     # real QuantReg slope per tau
    beta = {r["quantile"]: r["coef"] for r in point}
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(QR_DRAWS):
        sample = data.iloc[_block_indices(len(data), QR_BLOCK, rng)]
        try:
            m = smf.quantreg("y ~ x", sample)
            boot.append([float(m.fit(q=q).params["x"]) for q in qs])
        except Exception:  # noqa: BLE001 - a degenerate resample is skipped and the count is reported
            continue
    B = np.asarray(boot)
    rows = []
    for j, q in enumerate(qs):
        b = B[:, j]
        p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
        rows.append({"quantile": q, "coef": beta[q], "se": float(b.std(ddof=1)),
                     "ci_low": float(np.quantile(b, 0.025)), "ci_high": float(np.quantile(b, 0.975)),
                     "p_value": float(p), "p_value_iid": next(r["p_value"] for r in point if r["quantile"] == q),
                     "n": len(data), "se_method": f"moving-block bootstrap, block {QR_BLOCK}, {len(B)} draws, seed 42"})
    pd.DataFrame(rows).to_csv(CORE / "quantile_regression.csv", index=False)
    ref = 0.5
    others = [q for q in qs if q != ref]
    d = np.array([beta[q] - beta[ref] for q in others])
    D = np.column_stack([B[:, qs.index(q)] - B[:, qs.index(ref)] for q in others])
    S = np.atleast_2d(np.cov(D, rowvar=False))
    stat = float(d @ np.linalg.pinv(S) @ d)
    p = float(stats.chi2.sf(stat, len(others)))
    test = {"method": f"Wald test of equal slopes across quantiles, moving-block bootstrap covariance (block "
                      f"{QR_BLOCK}, {len(B)} draws, seed 42)", "quantiles": qs, "reference_quantile": ref,
            "stat": stat, "df": len(others), "p_value": p, "reject_equality": bool(p < 0.05), "n": len(data),
            "n_draws": int(len(B))}
    (CORE / "quantile_equality_test.json").write_text(json.dumps(test, indent=2) + "\n")
    return test


def stage_rolling_stability(df: pd.DataFrame) -> None:
    """Rolling 60-month correlation of year-over-year cement growth with the SPY return, and a Quandt-Andrews sup-F
    test (15% trimming) for a break in spy_ret_t = a + b * cement_yoy_{t-1}, with a residual-bootstrap p-value
    under the no-break null (499 draws, seed 42)."""
    import statsmodels.api as sm
    d = df[[EVIDENCE_SIGNAL, "spy_ret"]].dropna()
    rc = d[EVIDENCE_SIGNAL].rolling(ROLL_CORR_WINDOW, min_periods=36).corr(d["spy_ret"]).dropna()
    pd.DataFrame({"date": rc.index.strftime("%Y-%m-%d"), "rolling_corr": rc.values}).to_csv(
        RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    z = pd.concat([d["spy_ret"].rename("y"), d[EVIDENCE_SIGNAL].shift(1).rename("x")], axis=1).dropna()
    y, X = z["y"].to_numpy(), sm.add_constant(z["x"].to_numpy())
    n, k = len(y), X.shape[1]
    lo, hi = int(0.15 * n), int(0.85 * n)

    def sup_f(yv):
        ssr0 = float(((yv - X @ np.linalg.lstsq(X, yv, rcond=None)[0]) ** 2).sum())
        best, at = -np.inf, lo
        for t in range(lo, hi):
            s = 0.0
            for a, b in ((0, t), (t, n)):
                beta = np.linalg.lstsq(X[a:b], yv[a:b], rcond=None)[0]
                s += float(((yv[a:b] - X[a:b] @ beta) ** 2).sum())
            fs = ((ssr0 - s) / k) / (s / (n - 2 * k))
            if fs > best:
                best, at = fs, t
        return best, at

    f_obs, t_obs = sup_f(y)
    beta0 = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta0
    rng = np.random.default_rng(42)
    draws = [sup_f(X @ beta0 + rng.choice(resid, size=n, replace=True))[0] for _ in range(499)]
    p = float((1 + sum(f >= f_obs for f in draws)) / (1 + len(draws)))
    out = {"pair_id": PAIR_ID, "test": "quandt_andrews_sup_f", "model": "spy_ret_t ~ cement_yoy_{t-1}",
           "trim_pct": 0.15, "n_obs": int(n), "sup_f": round(float(f_obs), 4),
           "breakpoint_date": z.index[t_obs].strftime("%Y-%m-%d"), "p_value": round(p, 4),
           "p_value_method": "residual bootstrap under the no-break null, 499 draws, seed 42",
           "sample": [z.index[0].strftime("%Y-%m-%d"), z.index[-1].strftime("%Y-%m-%d")]}
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"  sup-F {f_obs:.2f} at {out['breakpoint_date']}, bootstrap p {p:.3f}")


# ---------------------------------------------------------------------------------------------------- tournament
def trade_reason(winner: dict) -> str:
    return f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}"


def main_site_rule() -> dict:
    """The rule the main site shows: winner of run 20260830 (strategy_returns_20260830_meta.json winner key), its row
    in tournament_results_20260830.csv (both restored from main). That run selected on test-period Sharpe over the
    grid {0,1,2,3,6,9,12} (lead 0 is below the current release-lag floor), so it is reported as the main-site rule,
    not replayed as a selection rule."""
    meta = json.loads((RES / f"strategy_returns_{MAIN_SITE_TAG}_meta.json").read_text())
    sig, thr, dirn, lead = meta["winner_key"].split("|")
    t = pd.read_csv(RES / f"tournament_results_{MAIN_SITE_TAG}.csv")
    r = t[(t["signal"] == sig) & (t["threshold"] == thr) & (t["direction"] == dirn) & (t["lead_months"] == int(lead))]
    if len(r) != 1:
        raise ValueError(f"main-site rule {meta['winner_key']} not found once in tournament_results_{MAIN_SITE_TAG}")
    r = r.iloc[0]
    return {"signal": sig, "threshold": thr, "direction": dirn, "lead_value": int(lead),
            "oos_sharpe": float(r["oos_sharpe"]), "tag": MAIN_SITE_TAG,
            "source": f"tournament_results_{MAIN_SITE_TAG}.csv row {int(r.name)}, "
                      f"strategy_returns_{MAIN_SITE_TAG}_meta.json winner_key",
            "note": f"Rule shown on the main site (run {MAIN_SITE_TAG}), selected on its test-period Sharpe (legacy "
                    "method); reference only, not a selection rule."}


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged cement-shipment growth signal is on the rule's side of its "
                                "threshold; otherwise hold cash (P1 long/cash).",
        "notes": "Portland cement shipments (Texas through 2023-12, then the U.S. portland-only MIS Table 2a total) "
                 "are a construction-activity indicator with no archive of first-published values: one track on "
                 "today's revised values with point-in-time release dates. Still a search-selected rule. The main "
                 "site shows the 20260830 rule (test-period-selected, legacy method); the 20261016 research run "
                 "(raw in-sample Sharpe argmax, fixed lags, never on the main site) is replayed exactly and kept as "
                 "the previous rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    # the rule the main site still shows (run 20260830, test-period-selected): recorded next to the selection as the
    # legacy_oos_selected_row, read from that run's immutable files; reference only, never a selection rule
    winner["selection"]["legacy_oos_selected_row"] = main_site_rule()
    write_json(RES / "winner_summary.json", winner, "winner_summary")
    from harness import charts as HC            # re-record the harness charts on the amended summary (provenance)
    HC.lead_plateau(PAIR_ID, DATE_TAG, spec_mod.SPEC.lead_unit)
    HC.chance_check(PAIR_ID, DATE_TAG)
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, trade_reason(winner))
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


# ---------------------------------------------------------------------------------------------------- validation
STRESS_PERIODS = [
    ("GFC", "2007-12-01", "2009-06-30"),
    ("COVID", "2020-02-01", "2020-12-31"),
    ("2022 Rates Shock", "2022-01-01", "2022-12-31"),
]


def stage_validation(winner: dict) -> None:
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    rows = []
    for name, start, end in STRESS_PERIODS + [("Full OOS", winner["oos_period_start"], winner["oos_period_end"])]:
        seg = strat.loc[start:end]
        r, b = seg["strategy_return"], seg["benchmark_return"]
        eq = (1 + r).cumprod()
        cnt = seg["sample"].value_counts()
        n_pre, n_is, n_oos = int(cnt.get("pre_IS", 0)), int(cnt.get("IS", 0)), int(cnt.get("OOS", 0))
        phase = ("test" if n_oos == len(seg) else "training" if n_is == len(seg) else
                 "before training" if n_pre == len(seg) else
                 "mostly before training" if n_pre > max(n_is, n_oos) else "mixed")
        rows.append({"period": name, "period_name": name, "start_date": start, "end_date": end,
                     "is_oos": bool(n_oos == len(seg)), "phase": phase,
                     "n_pre_is": n_pre, "n_is": n_is, "n_oos": n_oos, "n_obs": int(len(r)),
                     "strategy_sharpe": sharpe(r), "buy_hold_sharpe": sharpe(b),
                     "max_drawdown": float((eq / eq.cummax() - 1).min()),
                     "strategy_return": float((1 + r).prod() - 1), "buy_hold_return": float((1 + b).prod() - 1)})
    pd.DataFrame(rows).to_csv(RES / "subperiod_sharpe.csv", index=False)
    # calendar-year Sharpe over full test-period years only (a partial final year is left out)
    oos = strat[strat["sample"] == "OOS"]
    yrs = []
    for y, seg in oos.groupby(oos.index.year):
        if len(seg) == 12:
            yrs.append({"year": int(y), "strategy_sharpe": sharpe(seg["strategy_return"]),
                        "buy_hold_sharpe": sharpe(seg["benchmark_return"]),
                        "strategy_return": float((1 + seg["strategy_return"]).prod() - 1),
                        "buy_hold_return": float((1 + seg["benchmark_return"]).prod() - 1), "n": int(len(seg))})
    pd.DataFrame(yrs).to_csv(RES / "walk_forward_calendar_year.csv", index=False)
    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "track": "as revised today (single track, no archive)",
                   "oos_sharpe": winner["oos_sharpe"], "sharpe_diff_vs_bh": bs["observed"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs["method"], "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"],
                   "net_sharpe": (winner["tracks"]["main"]["winner"] or {}).get("oos_sharpe_net_5bp")}]
                 ).to_csv(VALID / "transaction_costs.csv", index=False)


# ---------------------------------------------------------------------------------------------------- metadata
def write_metadata(winner: dict, granger: dict, elapsed: float) -> None:
    g = granger["cement_to_SPY"]
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "leading", "indicator_type": "production",
        "strategy_objective": "max_sharpe",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "evan", "last_updated_at": NOW_ISO, "indicator": "cement", "target": "spy",
        "expected_direction": EXPECTED_DIRECTION, "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == EXPECTED_DIRECTION,
        "mechanism": "Portland cement shipments track construction and infrastructure activity; firm shipment growth "
                     "marks an upswing in real investment, slowing shipments a construction slowdown. The series is "
                     "Texas shipments through 2023-12 and the U.S. portland-only total from 2024-01.",
        "confidence": "low",
        "key_finding": (f"On today's revised cement values with point-in-time release dates (no archive of first "
                        f"releases), the rule selected on in-sample data uses {winner['signal_code']} / "
                        f"{winner['threshold_code']} at L{winner['lead_value']} (IS Sharpe {winner['is_sharpe']:.2f}); "
                        f"test-period Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold SPY "
                        f"{winner['bh_sharpe']:.2f}. Smallest cement-to-SPY Granger p-value {g['min_p']:.2f} "
                        f"(lag {g['min_p_lag']}; {g['min_p_bonferroni']:.2f} after the 12-lag Bonferroni adjustment)."),
        "caveats": [
            "USGS revises earlier months and no archive of first-published values exists: the backtest uses today's "
            "values (revision lookahead unquantified).",
            "The strategy is search-selected and needs fresh holdout validation.",
            "The training period is short (the cement series starts 2005-11; rolling windows need several years).",
            "Data Master's cement series ends 2025-06, so later months are not tested.",
            "The series is Texas Portland cement shipments through 2023-12 and the U.S. portland-only all-destination "
            "total (USGS MIS Table 2a) from 2024-01; the 2024 year-over-year growth rates are an artifact of that "
            "coverage change; portland-only excludes blended cement (Type IL).",
        ],
        "narrative_summary": "Portland cement shipment growth is tested as a construction-activity filter for SPY.",
        "known_stress_episodes": [
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30",
             "note": "Cement shipments collapsed with the housing bust."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30",
             "note": "Shipments dipped, then stayed choppy."},
            {"label": "2022 rate shock", "start": "2022-01-01", "end": "2022-12-31",
             "note": "Shipments held up while equities fell."},
        ],
        "data_provenance": {"source": "Data Master.xlsx (USGS Mineral Industry Surveys): " + SERIES_NAME,
                            "series_id": "USGS_CEMENT (snapshot 20261016T232733Z)", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    def der(name, definition, formula, role, charts):
        return {"name": name, "definition": definition, "formula": formula, "role": role, "appears_in_charts": charts}
    zooms = ["history_zoom_gfc", "history_zoom_covid", "history_zoom_inflation_2022"]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "cement",
            "display_name": "Portland cement shipments (Texas, then U.S. portland-only; USGS)",
            "derivatives": [
                der("cement", "Portland cement shipments level (monthly, metric tons): Texas total, then U.S. "
                    "portland-only total after the coverage change", "Data Master snapshot", "raw", ["hero"]),
                der("cement_yoy", "12-month growth", "100*(x_t/x_{t-12}-1)", "derivative",
                    ["hero", "regime_stats", "local_projections", "quantile_coef", "rolling_correlation",
                     "structural_break", "ccf_prewhitened", "granger_f_by_lag", "correlation_heatmap"] + zooms),
                der("cement_mom", "1-month growth", "100*(x_t/x_{t-1}-1)", "derivative", ["correlation_heatmap"]),
                der("cement_3m", "3-month growth", "100*(x_t/x_{t-3}-1)", "derivative", ["correlation_heatmap"]),
                der("cement_6m", "6-month growth", "100*(x_t/x_{t-6}-1)", "derivative",
                    ["correlation_heatmap", "equity_curves", "drawdown", "lead_plateau"]),
                der("cement_yoy_zscore_60m", "12-month growth versus its five-year history",
                    "(yoy - mean60)/std60, min 36 readings", "derivative", ["correlation_heatmap"]),
                der("cement_accel", "Change in 12-month growth (acceleration)", "yoy_t - yoy_{t-1}", "derivative",
                    ["correlation_heatmap", "ccf_prewhitened"]),
            ],
        },
        "target_axis": {
            "canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [
                der("spy", "SPY adjusted month-end close", "month-end adjusted close (pinned)", "raw",
                    ["hero"] + zooms),
                der("spy_ret", "SPY monthly return", "spy_t / spy_{t-1} - 1", "derivative",
                    ["equity_curves", "drawdown", "regime_stats", "ccf_prewhitened", "granger_f_by_lag",
                     "rolling_correlation", "structural_break", "subperiod_sharpe", "walk_forward"]),
                der("spy_fwd_1m", "One-month forward SPY return", "spy_{t+1}/spy_t - 1", "derivative",
                    ["correlation_heatmap", "local_projections"]),
                der("spy_fwd_3m", "Three-month forward SPY return", "spy_{t+3}/spy_t - 1", "derivative",
                    ["correlation_heatmap", "local_projections", "quantile_coef"]),
                der("spy_fwd_6m", "Six-month forward SPY return", "spy_{t+6}/spy_t - 1", "derivative",
                    ["correlation_heatmap", "local_projections"]),
                der("spy_fwd_12m", "Twelve-month forward SPY return", "spy_{t+12}/spy_t - 1", "derivative",
                    ["correlation_heatmap", "local_projections"]),
            ],
        },
        "notes": "Six cement growth transforms are the tournament signals (pair spec SIGNALS); the level is never traded.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
                                               "benchmark_oos_sharpe": winner["bh_sharpe"],
                                               "oos_max_drawdown": winner["oos_max_drawdown"],
                                               "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    (RES / "evidence_status.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": (f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} "
                           "tournament on today's revised USGS cement values (no archive of first releases) with "
                           "point-in-time release dates, reported on the test window (seen by earlier runs, so not a "
                           "frozen hold-out)."),
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan"}, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "elapsed_seconds": elapsed,
        "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()}, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Cement snapshot archive and data refresh", "proposed_by": "evan",
            "source": "USGS Mineral Industry Surveys",
            "observation": (f"The selected rule uses a {winner['lead_value']}-month lead on "
                            f"{winner['signal_display_name'].lower()} ({winner['direction']}, "
                            f"{winner['threshold_code']}); the Data Master series ends 2025-06."),
            "rationale": "Monthly snapshots (scripts/snapshot_revised_sources.py) start an archive of the values as "
                         "published, so a later run can measure how much revisions matter.",
            "possible_use_case": "robustness check",
            "caveats": "Search-selected rule; not final-exam validated.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the Portland Cement Shipments x SPY pair pipeline."}, indent=2) + "\n")


NARRATIVE_SOURCES = [
    "regime_quartile_returns.csv",
    "granger_by_lag.csv",
    "subperiod_sharpe.csv",
    "walk_forward_calendar_year.csv",
    f"structural_break_{PAIR_ID}.json",
    f"data_integrity_{DATE_TAG}.json",
    f"core_models_{DATE_TAG}/correlations.csv",
    f"core_models_{DATE_TAG}/ccf_prewhitened.csv",
    f"core_models_{DATE_TAG}/local_projections.csv",
    f"core_models_{DATE_TAG}/quantile_regression.csv",
    f"core_models_{DATE_TAG}/quantile_equality_test.json",
]


def write_narrative_provenance(df: pd.DataFrame, granger: dict) -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py),
    plus facts computed here (sample sizes, trade-log counts, Granger summary)."""
    derived = {
        "cement_first_month": df["cement"].first_valid_index().strftime("%Y-%m"),
        "cement_last_month": df["cement"].last_valid_index().strftime("%Y-%m"),
        "panel_months": int(df["cement"].notna().sum()),
        "n_granger_lags": GRANGER_MAX_LAG,
        "significance_p": 0.05,           # conventional cut-off the page prose names
        "interval_pct": 95,               # confidence level of the intervals the page prose names
        "granger_min_p_cement_to_spy": granger["cement_to_SPY"]["min_p"],
        "granger_cement_to_spy_best_lead": granger["cement_to_SPY"]["min_p_lag"],
        "granger_min_p_bonf_cement_to_spy": granger["cement_to_SPY"]["min_p_bonferroni"],
        "granger_min_p_spy_to_cement": granger["SPY_to_cement"]["min_p"],
        "granger_spy_to_cement_best_lead": granger["SPY_to_cement"]["min_p_lag"],
        "granger_min_p_bonf_spy_to_cement": granger["SPY_to_cement"]["min_p_bonferroni"],
    }
    derived["trade_log_rows"] = int(len(pd.read_csv(RES / "winner_trades_broker_style.csv")))
    derived["position_log_rows"] = int(len(pd.read_csv(RES / "winner_trade_log.csv")))
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    v = t[t["valid"].astype(bool)].dropna(subset=["is_sharpe"])
    rk = v["is_sharpe"].rank(ascending=False, method="min")
    sel = v.index[v["selected"].astype(bool)]
    derived["winner_is_rank_among_valid"] = int(rk.loc[sel[0]]) if len(sel) else None
    # test-period trades counted from the broker-style log itself (page and log agree): every log row dated in the
    # test period, including a move into the first test month from the last training-period position
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv")
    blog = pd.read_csv(RES / "winner_trades_broker_style.csv", parse_dates=["trade_date"])
    oos_first = pd.Timestamp(sr.loc[sr["sample"] == "OOS", "date"].iloc[0])
    tlo = blog[blog["trade_date"] >= oos_first]
    size = tlo["trade_size_pct"].astype(float) / 100
    derived["position_change_threshold_pp"] = POSITION_CHANGE_THRESHOLD_PP
    derived["oos_months_position_change_gt_5pct"] = int((size > POSITION_CHANGE_THRESHOLD_PP / 100).sum())
    derived["oos_sum_abs_position_change"] = round(float(size.sum()), 4)
    derived["n_oos_trade_log_rows"] = int(len(tlo))
    # sensitivity (not the rule): the winner's test-period Sharpe on the months before the shipment column's basis
    # break (data_integrity), against buy-and-hold on the same months
    it = json.loads((RES / f"data_integrity_{DATE_TAG}.json").read_text())
    cut = pd.Timestamp(it["first_month_not_equal"]) + pd.offsets.MonthEnd(0)
    pre = sr[(sr["sample"] == "OOS") & (pd.to_datetime(sr["date"]) < cut)]
    derived["pre_break_oos_end"] = it["last_month_equal_texas_total"]
    derived["pre_break_oos_n"] = int(len(pre))
    derived["pre_break_oos_sharpe"] = round(sharpe(pre["strategy_return"]), 4)
    derived["pre_break_bh_oos_sharpe"] = round(sharpe(pre["benchmark_return"]), 4)
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived=derived)


def _timed(name, fn, *a):
    t0 = time.time()
    print(f"\n== {name}")
    out = fn(*a)
    STAGE_TIMES[name] = time.time() - t0
    return out


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    df = _timed("panel", build_panel)
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    _timed("data_integrity", stage_data_integrity, df)
    _timed("stationarity", stage_stationarity, df)
    _timed("correlations", stage_correlations, df)
    granger = _timed("granger", stage_granger, df)
    _timed("ccf", stage_ccf, df)
    _timed("quartiles", stage_quartiles, df)
    _timed("local_projections", stage_local_projections, df)
    _timed("quantile_regression", stage_quantile_regression, df)
    _timed("rolling_stability", stage_rolling_stability, df)
    _tourn, winner, _out = _timed("tournament", run_tournament)
    _timed("validation", stage_validation, winner)
    write_metadata(winner, granger, time.time() - t0)
    write_narrative_provenance(df, granger)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
