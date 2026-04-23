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


# APP-RL1 extension: friendly-label map for raw forward-return column names
# that leak from pipeline-generated text fields (e.g. `key_finding` strings
# like "… predicts spy_fwd_63d …"). Single source of truth — do NOT inline a
# duplicate dict elsewhere. Keys are raw column tokens produced by
# scripts/pair_pipeline_*.py; values are non-quant display phrases.
_FWD_RETURN_LABELS = {
    "spy_fwd_21d": "SPY 21-day forward return",
    "spy_fwd_63d": "SPY 63-day forward return",
    "spy_fwd_126d": "SPY 126-day forward return",
    "spy_fwd_252d": "SPY 252-day forward return",
    "spy_fwd_12m": "SPY 12-month forward return",
    "xlv_fwd_21d": "XLV 21-day forward return",
    "xlv_fwd_63d": "XLV 63-day forward return",
    "xlv_fwd_12m": "XLV 12-month forward return",
    "xlp_fwd_21d": "XLP 21-day forward return",
    "xlp_fwd_63d": "XLP 63-day forward return",
    "xlp_fwd_12m": "XLP 12-month forward return",
}


def humanize_column_tokens(text: str) -> str:
    """Replace raw forward-return column tokens with friendly labels.

    Landing-page display polish: pipeline-generated strings such as
    ``"indpro_zscore_60m predicts spy_fwd_12m (coef=-0.02 …)"`` leak raw
    column names into the user-facing card. This helper substitutes known
    tokens from ``_FWD_RETURN_LABELS``. Unknown tokens pass through
    unchanged (no masking of legitimate content).
    """
    if not text:
        return text
    out = text
    # Sort longest-first so ``spy_fwd_126d`` matches before ``spy_fwd_12``.
    for token in sorted(_FWD_RETURN_LABELS, key=len, reverse=True):
        if token in out:
            out = out.replace(token, _FWD_RETURN_LABELS[token])
    return out


def get_integrity_issues() -> list:
    return list(_integrity_issues)


# APP-RL1 (Wave 10G.5-fix): single source of truth for page-link routing.
# Consume this helper everywhere — do NOT inline a local page_routing dict.
#
# Wave 10I.A Part 2 (2026-04-23): the three TED variants were previously
# multiplexed into a single composite `pages/6_ted_variants_*` surface via
# `st.tabs`. That composite has been exploded into three separate
# one-pair-per-page thin-wrapper surfaces — see
# `app/pair_configs/{sofr_ted_spy,dff_ted_spy,ted_spliced_spy}_config.py`.
# The `_TED_VARIANTS` branch in `get_page_prefix` is therefore removed and
# each variant is a regular entry in `PAGE_ROUTING`.
PAGE_ROUTING = {
    "indpro_spy": "pages/5_indpro_spy",
    "sofr_ted_spy": "pages/6_sofr_ted_spy",
    "permit_spy": "pages/7_permit_spy",
    "vix_vix3m_spy": "pages/8_vix_vix3m_spy",
    "hy_ig_v2_spy": "pages/9_hy_ig_v2_spy",
    "umcsent_xlv": "pages/10_umcsent_xlv",
    "dff_ted_spy": "pages/11_dff_ted_spy",
    "ted_spliced_spy": "pages/12_ted_spliced_spy",
    "indpro_xlp": "pages/14_indpro_xlp",
    "hy_ig_spy": "pages/15_hy_ig_spy",
}


def get_page_prefix(pair_id: str) -> str:
    """Return the page-link prefix for a pair (``pages/{n}_{pair_id}``).

    Single source of truth per APP-RL1. All consumers — pair_registry and
    page_templates — must call this helper rather than maintaining their own
    local routing dicts.
    """
    return PAGE_ROUTING.get(pair_id, f"pages/5_{pair_id}")


def _check_integrity(pair: dict) -> None:
    missing = [f for f in _CLASSIFICATION_FIELDS if pair.get(f, "unknown") == "unknown"]
    if missing:
        _integrity_issues.append({"pair_id": pair["pair_id"], "missing_fields": missing})


def load_pair_registry():
    """Scan results/ for completed pair analyses and return metadata list."""
    global _integrity_issues
    _integrity_issues = []
    pairs = []

    # Wave 10G.1 (2026-04-22): v1 hy_ig_spy archived to results/hy_ig_spy_v1/.
    # Legacy hardcoded block removed. Auto-discovery loop below now handles
    # all pairs uniformly. Archived v1 is NOT rendered on the dashboard —
    # directory name hy_ig_spy_v1 is explicitly excluded below.
    # Files preserved under results/hy_ig_spy_v1/ for historical reference.

    # Dynamically load from interpretation_metadata.json + tournament results
    for pair_dir in sorted(os.listdir(_RESULTS_DIR)):
        pair_path = os.path.join(_RESULTS_DIR, pair_dir)
        if not os.path.isdir(pair_path):
            continue
        if pair_dir.endswith("_v1") or pair_dir.endswith("_archived"):
            continue  # Archived pairs are not surfaced on the dashboard (Wave 10G.1)

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
            "hy_ig_spy": "HY-IG Credit Spread",
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

        # APP-RL1: single source of truth via get_page_prefix()
        page_prefix = get_page_prefix(pair_dir)

        # Wave 10G.2 (2026-04-22): Sample ratification. hy_ig_v2_spy is the
        # canonical quality benchmark — display it with a distinct label and
        # an is_sample flag so the landing page can render a Reference
        # Implementation badge/section. Other pairs unaffected.
        is_sample = pair_dir == "hy_ig_v2_spy"
        if is_sample:
            display_indicator = "Sample: HY-IG Credit Spread × S&P 500"
            display_name = "Sample (Reference Implementation)"
        else:
            display_indicator = indicator
            display_name = None

        pair = {
            "pair_id": pair_dir,
            "indicator": display_indicator,
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
            "is_sample": is_sample,
            "display_name": display_name,
        }
        _check_integrity(pair)
        pairs.append(pair)

    return pairs
