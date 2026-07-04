#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import subprocess
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats

ROOT = Path(__file__).resolve().parents[3]


def load_plotly(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def arr(v):
    if isinstance(v, dict) and "bdata" in v:
        dtype = np.dtype(v["dtype"])
        return np.frombuffer(base64.b64decode(v["bdata"]), dtype=dtype)
    return np.array(v)


def zarr(v):
    if isinstance(v, dict) and "bdata" in v:
        a = arr(v)
        shape = v.get("shape")
        if isinstance(shape, str):
            shape = tuple(int(x.strip()) for x in shape.split(","))
        return a.reshape(shape) if shape else a
    if isinstance(v, list) and v and isinstance(v[0], dict) and "bdata" in v[0]:
        return np.vstack([arr(row) for row in v])
    return np.array(v)


def dates(v):
    return pd.to_datetime(list(v))


def fmax_abs(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) != len(b):
        return float("inf")
    return float(np.nanmax(np.abs(a - b))) if len(a) else 0.0


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"origin/main:{path}"], cwd=ROOT)


def check_gold_drawdown(out: dict):
    fig = load_plotly("output/charts/gold_copper_xli/plotly/drawdown.json")
    sig = pd.read_parquet(ROOT / "results/gold_copper_xli/signals_20260526.parquet")
    if not isinstance(sig.index, pd.DatetimeIndex):
        sig.index = pd.to_datetime(sig.index)
    w = json.loads((ROOT / "results/gold_copper_xli/winner_summary.json").read_text())
    o = sig.loc[w["oos_period_start"]:w["oos_period_end"]].copy()
    eq = (1 + o["strategy_return"].fillna(0)).cumprod()
    dd_from_returns = (eq / eq.cummax() - 1) * 100
    eq_col_dd = (o["equity_curve"] / o["equity_curve"].iloc[0])
    dd_from_eq = (eq_col_dd / eq_col_dd.cummax() - 1) * 100
    plotted = arr(fig["data"][0]["y"])
    plotted_dates = dates(fig["data"][0]["x"])
    out["A1_gold"] = {
        "plot_start": str(plotted_dates.min().date()),
        "plot_end": str(plotted_dates.max().date()),
        "n": int(len(plotted)),
        "plotted_trough_pct": float(plotted.min()),
        "canonical_oos_mdd_pct": float(w["oos_max_drawdown"] * 100),
        "recomputed_from_strategy_return_trough_pct": float(dd_from_returns.min()),
        "recomputed_from_equity_curve_trough_pct": float(dd_from_eq.min()),
        "plot_vs_equity_curve_max_abs_diff": fmax_abs(plotted, dd_from_eq.values),
        "old_full_sample_present": bool(plotted.min() < -15),
    }


def phlx_strategy_returns():
    d = pd.read_csv(ROOT / "results/phlxsox_spy/strategy_returns_20260619.csv", parse_dates=["date"]).set_index("date")
    spyret = d["bh_return"]
    mom63 = (1 + spyret).rolling(63).apply(np.prod, raw=True) - 1
    pos_mom = (mom63.shift(1) > 0).astype(float)
    d["spy_mom_return"] = pos_mom * spyret
    d["strategy_equity"] = (1 + d["strategy_return"]).cumprod()
    d["bh_equity"] = (1 + d["bh_return"]).cumprod()
    d["spy_mom_equity"] = (1 + d["spy_mom_return"].fillna(0)).cumprod()
    return d


def check_phlx_drawdown(out: dict):
    fig = load_plotly("output/charts/phlxsox_spy/plotly/drawdown.json")
    d = phlx_strategy_returns()
    w = json.loads((ROOT / "results/phlxsox_spy/winner_summary.json").read_text())
    o_start, o_end = w["oos_period_start"], w["oos_period_end"]

    def dd(ret_col):
        r = d[ret_col].fillna(0).loc[o_start:o_end]
        eq = (1 + r).cumprod()
        return (eq / eq.cummax() - 1) * 100

    recomputed = [dd("strategy_return"), dd("bh_return"), dd("spy_mom_return")]
    plotted = [arr(tr["y"]) for tr in fig["data"][:3]]
    eq_fig = load_plotly("output/charts/phlxsox_spy/plotly/equity_curves.json")
    eq_dates = dates(eq_fig["data"][0]["x"])
    out["A2_phlx_drawdown"] = {
        "plot_start": str(dates(fig["data"][0]["x"]).min().date()),
        "plot_end": str(dates(fig["data"][0]["x"]).max().date()),
        "plotted_troughs_pct": [float(y.min()) for y in plotted],
        "recomputed_oos_troughs_pct": [float(x.min()) for x in recomputed],
        "canonical_troughs_pct": [
            float(w["oos_max_drawdown"] * 100),
            float(w["bh_max_drawdown"] * 100),
            float(w["spy_own_momentum_max_drawdown"] * 100),
        ],
        "max_abs_diffs": [fmax_abs(p, r.values) for p, r in zip(plotted, recomputed)],
        "old_full_sample_present": bool(min(float(y.min()) for y in plotted) < -50),
        "equity_curves_start": str(eq_dates.min().date()),
        "equity_curves_end": str(eq_dates.max().date()),
    }


def check_chart_integrity(out: dict):
    details = {}

    # SOX CCF.
    ccf = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/ccf_prewhitened.csv")
    fig = load_plotly("output/charts/phlxsox_spy/plotly/ccf_prewhitened.json")
    details["phlx_ccf"] = {
        "lag_diff": fmax_abs(arr(fig["data"][0]["x"]), ccf["lag"].values),
        "ccf_diff": fmax_abs(arr(fig["data"][0]["y"]), ccf["ccf"].values),
        "lag0_plotted": float(arr(fig["data"][0]["y"])[list(arr(fig["data"][0]["x"])).index(0)]),
        "lag0_csv": float(ccf.loc[ccf["lag"] == 0, "ccf"].iloc[0]),
    }

    # SOX Granger.
    g = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/granger_causality.csv")
    bylag = pd.read_csv(ROOT / "results/phlxsox_spy/granger_by_lag.csv").sort_values("lag")
    fwd = g[g["direction"] == "indicator_to_target"].sort_values("lag")
    rev = g[g["direction"] == "target_to_indicator"].sort_values("lag")
    fig = load_plotly("output/charts/phlxsox_spy/plotly/granger_f_by_lag.json")
    crit = [float(sstats.f.ppf(0.95, r["df_num"], r["df_den"])) for _, r in bylag.iterrows()]
    details["phlx_granger"] = {
        "fwd_lag_diff": fmax_abs(arr(fig["data"][0]["x"]), fwd["lag"].values),
        "fwd_f_diff": fmax_abs(arr(fig["data"][0]["y"]), fwd["f_statistic"].values),
        "rev_lag_diff": fmax_abs(arr(fig["data"][1]["x"]), rev["lag"].values),
        "rev_f_diff": fmax_abs(arr(fig["data"][1]["y"]), rev["f_statistic"].values),
        "crit_diff": fmax_abs(arr(fig["data"][2]["y"]), crit),
    }

    # SOX heatmap.
    c = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/correlations.csv")
    p = c[c["metric"] == "pearson"].copy()
    p[["signal", "horizon"]] = p["pair_name"].str.split("__", expand=True)
    hor_order = [h for h in ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d", "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"] if h in set(p["horizon"])]
    piv = p.pivot(index="signal", columns="horizon", values="value")[hor_order]
    piv = piv.reindex(piv.abs().max(axis=1).sort_values(ascending=False).index)
    fig = load_plotly("output/charts/phlxsox_spy/plotly/correlation_heatmap.json")
    details["phlx_heatmap"] = {
        "z_diff": fmax_abs(zarr(fig["data"][0]["z"]), piv.values),
        "shape_plot": list(zarr(fig["data"][0]["z"]).shape),
        "shape_csv": list(piv.values.shape),
    }

    # VIX subperiod bars.
    sp = pd.read_csv(ROOT / "results/vix_vix3m_spy/subperiod_sharpe.csv")
    fig = load_plotly("output/charts/vix_vix3m_spy/plotly/subperiod_sharpe.json")
    vals = []
    labels = []
    for _, row in sp.iterrows():
        base = row["period_name"] + (" (IS)" if not row["is_oos"] else " (OOS)")
        sharpe = row.get("sharpe")
        n_obs = row.get("n_obs", 0)
        ann_ret = row.get("ann_return", 0)
        ann_vol = row.get("ann_vol", 0)
        if pd.isna(sharpe) or n_obs < 3:
            labels.append(f"{base} — no data")
            vals.append(0.0)
        elif abs(float(sharpe)) < 1e-9 and abs(float(ann_ret or 0)) < 1e-9 and abs(float(ann_vol or 0)) < 1e-9:
            labels.append(f"{base} — in cash")
            vals.append(0.0)
        else:
            labels.append(base)
            vals.append(float(sharpe))
    details["vix_subperiod_sharpe"] = {
        "x_diff": fmax_abs(fig["data"][0]["x"], vals),
        "labels_match": list(fig["data"][0]["y"]) == labels,
        "plotted_x": list(fig["data"][0]["x"]),
        "source_x": vals,
    }

    # Gold drawdown already compares to signals parquet.
    details["gold_drawdown"] = {
        "plot_vs_equity_curve_max_abs_diff": out["A1_gold"]["plot_vs_equity_curve_max_abs_diff"]
    }
    details["phlx_drawdown"] = {
        "max_abs_diffs": out["A2_phlx_drawdown"]["max_abs_diffs"]
    }
    out["A3_chart_integrity"] = details


def check_loader(out: dict):
    import importlib.util
    import sys

    sys.path.insert(0, str(ROOT / "app"))
    spec = importlib.util.spec_from_file_location("page_templates", ROOT / "app/components/page_templates.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    gold = mod._load_winner_summary("gold_copper_xli")
    hy = mod._load_winner_summary("hy_ig_spy")
    pairs_with_oos = []
    pairs_changed = []
    for p in sorted((ROOT / "results").iterdir()):
        ws = p / "winner_summary.json"
        if ws.exists():
            d = json.loads(ws.read_text())
            if d.get("oos_win_rate") is not None:
                pairs_with_oos.append(p.name)
    out["A4_loader"] = {
        "gold_total_combos": gold.get("total_combos"),
        "gold_win_rate": gold.get("oos_win_rate"),
        "gold_raw_win_rate": json.loads((ROOT / "results/gold_copper_xli/winner_summary.json").read_text()).get("win_rate"),
        "hy_ig_win_rate": hy.get("oos_win_rate"),
        "pairs_with_oos_win_rate_non_null": pairs_with_oos,
        "guard_is_not_none": "is not None" in (ROOT / "app/components/page_templates.py").read_text(),
    }


def check_vline(out: dict):
    fig = load_plotly("output/charts/t10y3m_spy/plotly/lead_sharpe_distribution.json")
    t = pd.read_csv(ROOT / "results/t10y3m_spy/lead_tournament_20260622.csv")
    w = json.loads((ROOT / "results/t10y3m_spy/winner_summary.json").read_text())
    leads = t["lead_months"].astype(int).tolist()
    shape = fig["layout"]["shapes"][0]
    chart_files = sorted((ROOT / "output/charts").glob("*/plotly/lead_sharpe_distribution.json"))
    changed_vs_main = []
    missing_in_main = []
    for path in chart_files:
        rel = str(path.relative_to(ROOT))
        try:
            if path.read_bytes() != git_show(rel):
                changed_vs_main.append(path.parts[-3])
        except subprocess.CalledProcessError:
            missing_in_main.append(path.parts[-3])
    out["A5_vline"] = {
        "leads": leads,
        "winner_lead": w["lead_value"],
        "expected_index": leads.index(int(w["lead_value"])),
        "shape_x0": shape.get("x0"),
        "shape_x1": shape.get("x1"),
        "bar_best_diff": fmax_abs(fig["data"][2]["y"], t["best_oos_sharpe"].values),
        "bar_x_match": list(fig["data"][2]["x"]) == [f"L{x}" for x in leads],
        "changed_lead_charts_vs_main": changed_vs_main,
        "missing_in_main": missing_in_main,
    }


def check_narrative(out: dict):
    # Numeric support for SOX config.
    w = json.loads((ROOT / "results/phlxsox_spy/winner_summary.json").read_text())
    ev = json.loads((ROOT / "results/phlxsox_spy/evidence_status.json").read_text())
    g = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/granger_causality.csv")
    ccf = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/ccf_prewhitened.csv")
    inc = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/incremental_edge_vs_spy_momentum.csv")
    lp = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/local_projections.csv")
    q = pd.read_csv(ROOT / "results/phlxsox_spy/core_models_20260619/quantile_regression.csv")
    t = pd.read_csv(ROOT / "results/phlxsox_spy/tournament_results_20260619.csv")
    boot = pd.read_csv(ROOT / "results/phlxsox_spy/tournament_validation_20260619/bootstrap.csv")
    valid = t[t["valid"] & ~t["signal"].isin(["BENCHMARK", "SPY_OWN_MOMENTUM"])]
    out["B6_sox_narrative_support"] = {
        "evidence_status": ev["status"],
        "oos_sharpe": w["oos_sharpe"],
        "bh_sharpe": w["bh_sharpe"],
        "spy_mom_sharpe": w["spy_own_momentum_sharpe"],
        "is_sharpe_winner_row": float(t.loc[t["oos_sharpe"].idxmax(), "is_sharpe"]),
        "median_valid_oos_sharpe": float(valid["oos_sharpe"].median()),
        "valid_count": int(len(valid)),
        "win_rate": w["oos_win_rate"],
        "bootstrap_p": float(boot.iloc[0]["bootstrap_p_value"]),
        "granger_all_sig_both_directions": bool(g.groupby("direction")["significant"].all().all()),
        "granger_lags_by_direction": {k: v["lag"].astype(int).tolist() for k, v in g[g["significant"]].groupby("direction")},
        "ccf_lag0": float(ccf.loc[ccf["lag"] == 0, "ccf"].iloc[0]),
        "incremental_edge": inc[["fwd_horizon_days", "rs_p_value", "incremental_r2"]].to_dict("records"),
        "lp_forward_min_p": float(lp[lp["direction"] == "fwd"]["p_value"].min()),
        "lp_reverse_day1_p": float(lp[(lp["direction"] == "rev") & (lp["horizon"] == 1)]["p_value"].iloc[0]),
        "quantile_sig_taus": q.loc[q["p_value"] < 0.05, "tau"].tolist(),
    }

    # INDPRO, M2, VIX supports.
    out["B7_B8_other_narrative_support"] = {
        "indpro_refs_outside_indpro_config": subprocess.check_output(
            ["rg", "-n", "(Industrial Production|industrial production|industrial output|production index|INDPRO)", "app/pair_configs", "-g", "*.py"],
            cwd=ROOT, text=True
        ).splitlines(),
        "m2_granger_config_claims": subprocess.check_output(
            ["rg", "-n", "no forward|NO lag|SPY.*M2|M2.*SPY|r=|r =|0\\.225|0\\.225", "app/pair_configs/m2sl_yoy_spy_config.py"],
            cwd=ROOT, text=True
        ).splitlines(),
        "vix_direction": json.loads((ROOT / "results/vix_vix3m_spy/winner_summary.json").read_text()).get("direction"),
    }


def check_gates_and_collateral(out: dict):
    changed = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD"], cwd=ROOT, text=True).splitlines()
    changed_pairs = sorted({p.split("/")[2] for p in changed if p.startswith("output/charts/") and "/plotly/" in p})
    config_pairs = sorted({Path(p).stem.removesuffix("_config") for p in changed if p.startswith("app/pair_configs/")})
    out["C10_collateral"] = {
        "changed_files_count": len(changed),
        "changed_chart_pairs": changed_pairs,
        "changed_config_pairs": config_pairs,
        "unexpected_changed_chart_pairs": [p for p in changed_pairs if p not in {"gold_copper_xli", "phlxsox_spy", "t10y3m_spy", "vix_vix3m_spy"}],
    }


def main():
    out = {}
    check_gold_drawdown(out)
    check_phlx_drawdown(out)
    check_chart_integrity(out)
    check_loader(out)
    check_vline(out)
    check_narrative(out)
    check_gates_and_collateral(out)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
