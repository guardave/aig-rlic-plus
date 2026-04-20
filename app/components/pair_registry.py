# Force Cloud redeploy: 2026-04-19 wave 3 verification
"""Registry of analyzed indicator-target pairs for the portal.

Exposes pair metadata loaded from `results/<pair>/interpretation_metadata.json`
plus classification helpers used by the landing page filter row.
"""

import json
import os

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
_RESULTS_DIR = os.path.join(_BASE, "results")

_integrity_issues = []

_CLASSIFICATION_FIELDS = ("indicator_nature", "indicator_type", "strategy_objective")


def get_nature_label(nature: str) -> str:
    return {"leading": "Leading", "coincident": "Coincident", "lagging": "Lagging"}.get(nature, "Unknown")


def get_type_label(type_: str) -> str:
    return {
        "price": "Price", "production": "Production", "sentiment": "Sentiment",
        "rates": "Rates", "credit": "Credit", "volatility": "Volatility", "macro": "Macro"
    }.get(type_, "Unknown")


def get_objective_label(objective: str) -> str:
    return {"min_mdd": "Min MDD", "max_sharpe": "Max Sharpe", "max_return": "Max Return"}.get(objective, "Unknown")


def get_integrity_issues() -> list:
    return list(_integrity_issues)


def _check_integrity(pair: dict) -> None:
    missing = [f for f in _CLASSIFICATION_FIELDS if pair.get(f, "unknown") == "unknown"]
    if missing:
        _integrity_issues.append({"pair_id": pair["pair_id"], "missing_fields": missing})


def load_pair_registry():
    """Scan results/ for completed pair analyses and return metadata list."""
    global _integrity_issues
    _integrity_issues = []
    pairs = []

    # HY-IG → SPY (legacy, hardcoded)
    hy_ig_interp_path = os.path.join(_RESULTS_DIR, "hy_ig_spy", "interpretation_metadata.json")
    hy_ig_interp = {}
    if os.path.exists(hy_ig_interp_path):
        with open(hy_ig_interp_path) as f:
            hy_ig_interp = json.load(f)

    hy_ig_pair = {
        "pair_id": "hy_ig_spy",
        "indicator": "Sample: HY-IG Credit Spread",
        "indicator_id": "HY_IG_OAS",
        "target": "S&P 500",
        "target_ticker": "SPY",
        "direction": "counter_cyclical",
        "indicator_nature": hy_ig_interp.get("indicator_nature", "unknown"),
        "indicator_type": hy_ig_interp.get("indicator_type", "unknown"),
        "strategy_objective": hy_ig_interp.get("strategy_objective", "unknown"),
        "best_oos_sharpe": 1.17,
        "bh_sharpe": 0.77,
        "valid_combos": 1149,
        "total_combos": 2304,
        "max_drawdown": -11.6,
        "bh_drawdown": -33.7,
        "key_finding": "HMM regime detection wins; drawdown avoidance, not alpha",
        "status": "Completed",
        "story_page": "pages/1_hy_ig_story.py",
        "evidence_page": "pages/2_hy_ig_evidence.py",
        "strategy_page": "pages/3_hy_ig_strategy.py",
        "methodology_page": "pages/4_hy_ig_methodology.py",
    }
    _check_integrity(hy_ig_pair)
    pairs.append(hy_ig_pair)

    # Dynamically load from interpretation_metadata.json + tournament results
    for pair_dir in sorted(os.listdir(_RESULTS_DIR)):
        pair_path = os.path.join(_RESULTS_DIR, pair_dir)
        if not os.path.isdir(pair_path):
            continue
        if pair_dir == "hy_ig_spy":
            continue  # Already handled

        interp_path = os.path.join(pair_path, "interpretation_metadata.json")
        if not os.path.exists(interp_path):
            continue

        with open(interp_path) as f:
            interp = json.load(f)

        # Find tournament results
        tourn_files = [f for f in os.listdir(pair_path) if f.startswith("tournament_results")]
        best_sharpe = None
        bh_sharpe = None
        valid_count = 0
        total_count = 0
        max_dd = None
        bh_dd = None

        if tourn_files:
            import pandas as pd
            tourn_path = os.path.join(pair_path, tourn_files[0])
            try:
                tdf = pd.read_csv(tourn_path)
                total_count = len(tdf)
                valid_count = int(tdf["valid"].sum())
                # META-UC (Wave 8B-2): hy_ig_v2_spy's tournament CSV was
                # migrated to ratio form in Wave 8B-1 (Evan). Other pairs
                # still use percent-form CSVs (tracked BL-002). Normalize to
                # percent form here so the downstream `pair["max_drawdown"]`
                # contract remains uniform across all pairs, and app/app.py
                # display sites (lines 272/273) can keep their existing
                # `f"{val:.1f}%"` formatter unchanged.
                _dd_scale = 100.0 if pair_dir == "hy_ig_v2_spy" else 1.0
                valid_strats = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
                if len(valid_strats) > 0:
                    best_row = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
                    best_sharpe = round(float(best_row["oos_sharpe"]), 2)
                    max_dd = round(float(best_row["max_drawdown"]) * _dd_scale, 1)
                bh = tdf[tdf["signal"] == "BENCHMARK"]
                if len(bh) > 0:
                    bh_sharpe = round(float(bh.iloc[0]["oos_sharpe"]), 2)
                    bh_dd = round(float(bh.iloc[0]["max_drawdown"]) * _dd_scale, 1)
            except Exception:
                pass

        # Map indicator/target to display names
        indicator_names = {
            "indpro": "Industrial Production",
            "indpro_xlp": "Industrial Production",
            "permit_spy": "Building Permits",
            "vix_vix3m_spy": "VIX/VIX3M Ratio",
            "sofr_ted_spy": "SOFR - DTB3 (TED)",
            "dff_ted_spy": "DFF - DTB3 (Fed Funds TED)",
            "ted_spliced_spy": "Spliced TED Spread",
            "hy_ig_v2_spy": "HY-IG Credit Spread",
            "umcsent_xlv": "Michigan Consumer Sentiment",
        }
        target_names = {
            "spy": "S&P 500",
            "xlv": "Health Care Select Sector (XLV)",
            "xlp": "Consumer Staples Select Sector (XLP)",
        }

        indicator = indicator_names.get(pair_dir, indicator_names.get(
            interp.get("indicator", ""), interp.get("indicator", pair_dir)))
        target = target_names.get(interp.get("target", ""), interp.get("target", ""))

        # TED variants share a single set of pages
        ted_variants = {"sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy"}
        page_routing = {
            "indpro_spy": "pages/5_indpro_spy",
            "permit_spy": "pages/7_permit_spy",
            "vix_vix3m_spy": "pages/8_vix_vix3m_spy",
            "hy_ig_v2_spy": "pages/9_hy_ig_v2_spy",
            "umcsent_xlv": "pages/10_umcsent_xlv",
            "indpro_xlp": "pages/14_indpro_xlp",
        }
        if pair_dir in ted_variants:
            page_prefix = "pages/6_ted_variants"
        elif pair_dir in page_routing:
            page_prefix = page_routing[pair_dir]
        else:
            page_prefix = f"pages/5_{pair_dir}"

        pair = {
            "pair_id": pair_dir,
            "indicator": indicator,
            "indicator_id": interp.get("indicator", ""),
            "target": target,
            "target_ticker": interp.get("target", "").upper(),
            "direction": interp.get("expected_direction", "unknown"),
            "observed_direction": interp.get("observed_direction", "unknown"),
            "direction_consistent": interp.get("direction_consistent", True),
            "indicator_nature": interp.get("indicator_nature", "unknown"),
            "indicator_type": interp.get("indicator_type", "unknown"),
            "strategy_objective": interp.get("strategy_objective", "unknown"),
            "best_oos_sharpe": best_sharpe,
            "bh_sharpe": bh_sharpe,
            "valid_combos": valid_count,
            "total_combos": total_count,
            "max_drawdown": max_dd,
            "bh_drawdown": bh_dd,
            "key_finding": interp.get("key_finding", ""),
            "status": "Completed",
            "story_page": f"{page_prefix}_story.py",
            "evidence_page": f"{page_prefix}_evidence.py",
            "strategy_page": f"{page_prefix}_strategy.py",
            "methodology_page": f"{page_prefix}_methodology.py",
        }
        _check_integrity(pair)
        pairs.append(pair)

    return pairs
