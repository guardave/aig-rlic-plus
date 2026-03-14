"""Registry of analyzed indicator-target pairs for the portal."""

import json
import os

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
_RESULTS_DIR = os.path.join(_BASE, "results")


def load_pair_registry():
    """Scan results/ for completed pair analyses and return metadata list."""
    pairs = []

    # HY-IG → SPY (legacy, hardcoded)
    pairs.append({
        "pair_id": "hy_ig_spy",
        "indicator": "HY-IG Credit Spread",
        "indicator_id": "HY_IG_OAS",
        "target": "S&P 500",
        "target_ticker": "SPY",
        "direction": "counter_cyclical",
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
    })

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
                valid_strats = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
                if len(valid_strats) > 0:
                    best_row = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
                    best_sharpe = round(float(best_row["oos_sharpe"]), 2)
                    max_dd = round(float(best_row["max_drawdown"]), 1)
                bh = tdf[tdf["signal"] == "BENCHMARK"]
                if len(bh) > 0:
                    bh_sharpe = round(float(bh.iloc[0]["oos_sharpe"]), 2)
                    bh_dd = round(float(bh.iloc[0]["max_drawdown"]), 1)
            except Exception:
                pass

        # Map indicator/target to display names
        indicator_names = {
            "indpro": "Industrial Production",
            "sofr_ted_spy": "SOFR - DTB3 (TED)",
            "dff_ted_spy": "DFF - DTB3 (Fed Funds TED)",
            "ted_spliced_spy": "Spliced TED Spread",
        }
        target_names = {
            "spy": "S&P 500",
        }

        indicator = indicator_names.get(pair_dir, indicator_names.get(
            interp.get("indicator", ""), interp.get("indicator", pair_dir)))
        target = target_names.get(interp.get("target", ""), interp.get("target", ""))

        # TED variants share a single set of pages
        ted_variants = {"sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy"}
        if pair_dir in ted_variants:
            page_prefix = "pages/6_ted_variants"
        else:
            page_prefix = f"pages/5_{pair_dir}"

        pairs.append({
            "pair_id": pair_dir,
            "indicator": indicator,
            "indicator_id": interp.get("indicator", ""),
            "target": target,
            "target_ticker": interp.get("target", "").upper(),
            "direction": interp.get("expected_direction", "unknown"),
            "observed_direction": interp.get("observed_direction", "unknown"),
            "direction_consistent": interp.get("direction_consistent", True),
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
            "methodology_page": f"{page_prefix}_strategy.py",  # Strategy page has methodology for TED variants
        })

    return pairs
