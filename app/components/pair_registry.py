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
    return {
        "min_mdd": "Min MDD",
        "max_sharpe": "Max Sharpe",
        "max_return": "Max Return",
        "countercyclical_protection": "Counter-cyclical",
        "risk_reduction": "Risk Reduction",
    }.get(objective, "Unknown")


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
# `st.tabs`. That composite was exploded into three separate one-pair-per-page
# thin-wrapper surfaces — see archived configs at
# `app/pair_configs_archive/{sofr_ted_spy,dff_ted_spy,ted_spliced_spy}_config.py`.
#
# fix260601_chart_hygiene Wave 2 (2026-06-02): the three TED variants are
# **archived** because their `winner_trade_log.csv` files have all-zero
# trade returns (the underlying strategy-return time series doesn't exist
# in usable form). Per user decision, they are removed from the portal
# until pipeline rehab. Pages moved to `app/pages_archive/`; configs moved
# to `app/pair_configs_archive/`; `results/` dirs renamed with `_archived`
# suffix (which the auto-discovery loop below filters out). Charts in
# `output/charts/<pair>/` left in place — no longer referenced.
PAGE_ROUTING = {
    "indpro_spy": "pages/5_indpro_spy",
    "permit_spy": "pages/7_permit_spy",
    "vix_vix3m_spy": "pages/8_vix_vix3m_spy",
    "hy_ig_v2_spy": "pages/9_hy_ig_v2_spy",
    "umcsent_xlv": "pages/10_umcsent_xlv",
    "indpro_xlp": "pages/14_indpro_xlp",
    "hy_ig_spy": "pages/15_hy_ig_spy",
    "gold_copper_xli": "pages/16_gold_copper_xli",
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
                # Resolve column-name drift: some pipelines emit
                # `max_drawdown`, newer ones emit `oos_max_drawdown`.
                # The dashboard card formula is the same; resolve to a
                # single working column. (Documented in BL-DUP-12.)
                if "max_drawdown" in tdf.columns:
                    dd_col = "max_drawdown"
                elif "oos_max_drawdown" in tdf.columns:
                    dd_col = "oos_max_drawdown"
                else:
                    dd_col = None
                # META-UC (Wave 8B-2 / Wave 10I.C fix): Detect ratio vs
                # percent form by inspecting the benchmark drawdown value.
                # Ratio form: abs(dd) < 2 (e.g. -0.337).
                # Percent form: abs(dd) >= 2 (e.g. -33.7).
                _bh_sample = tdf[tdf["signal"] == "BENCHMARK"] if "signal" in tdf.columns else tdf.iloc[0:0]
                if dd_col is None:
                    _dd_scale = 1.0
                elif len(_bh_sample) > 0:
                    _sample_dd = abs(float(_bh_sample.iloc[0][dd_col]))
                    _dd_scale = 100.0 if _sample_dd < 2.0 else 1.0
                else:
                    _all_dd = tdf[dd_col].dropna()
                    _dd_scale = 100.0 if (len(_all_dd) > 0 and abs(_all_dd.iloc[0]) < 2.0) else 1.0
                valid_strats = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
                if len(valid_strats) > 0:
                    best_row = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
                    best_sharpe = round(float(best_row["oos_sharpe"]), 2)
                    if dd_col is not None:
                        max_dd = round(float(best_row[dd_col]) * _dd_scale, 1)
                bh = tdf[tdf["signal"] == "BENCHMARK"] if "signal" in tdf.columns else tdf.iloc[0:0]
                if len(bh) > 0:
                    bh_sharpe = round(float(bh.iloc[0]["oos_sharpe"]), 2)
                    if dd_col is not None:
                        bh_dd = round(float(bh.iloc[0][dd_col]) * _dd_scale, 1)
                else:
                    # No BENCHMARK row in tournament (e.g. gold_copper_xli's
                    # pipeline didn't emit one). Fall back to winner_summary
                    # bh fields when present. Tracked as BL-DUP-11/DUP-6.
                    ws_path = os.path.join(pair_path, "winner_summary.json")
                    if os.path.exists(ws_path):
                        with open(ws_path) as _wsf:
                            _ws = json.load(_wsf)
                        if _ws.get("bh_sharpe") is not None:
                            bh_sharpe = round(float(_ws["bh_sharpe"]), 2)
                        _ws_bh_dd = _ws.get("bh_max_drawdown")
                        if _ws_bh_dd is not None:
                            _ws_bh_dd_f = float(_ws_bh_dd)
                            _scale = 100.0 if abs(_ws_bh_dd_f) < 2.0 else 1.0
                            bh_dd = round(_ws_bh_dd_f * _scale, 1)
            except Exception as e:
                # Silent failure caused the gold_copper_xli dashboard
                # card to render as "—" because a KeyError on the
                # column-name drift was swallowed. Now we log and
                # surface to integrity-issues so future drift is
                # visible at next wave closure.
                _integrity_issues.append({
                    "pair_id": pair_dir,
                    "missing_fields": ["tournament_load_error"],
                    "note": (
                        f"tournament_results CSV could not be parsed for "
                        f"card display: {type(e).__name__}: {e}. Dashboard "
                        f"card will show '—' for affected metrics."
                    ),
                })

        # Display names sourced from the canonical display_names module
        # (DUP-1 consolidation, fix260531). Previously this dict was
        # duplicated in page_templates.py and sidebar.py with drift.
        from .display_names import (
            INDICATOR_NAMES as indicator_names,
            TARGET_NAMES as target_names,
            resolve_indicator,
            resolve_target,
        )

        indicator = resolve_indicator(pair_dir, interp.get("indicator", ""))
        target = resolve_target(interp.get("target", ""))

        # ELI5 gate (added 2026-05-26 after gold_copper_xli surfaced "cryptic
        # title on home tile" issue): a cryptic title — i.e. a raw column
        # name like ``gold_copper_ratio`` or a bare ticker like ``xli`` —
        # appears when a new pair_id is not registered in indicator_names /
        # target_names. Flag this as an integrity issue so it is visible at
        # next wave closure. The fallback display still works, but the
        # warning makes the registration gap auditable rather than silent.
        if pair_dir not in indicator_names:
            _integrity_issues.append({
                "pair_id": pair_dir,
                "missing_fields": ["display_indicator_unregistered"],
                "note": (
                    f"pair_id '{pair_dir}' not in indicator_names dict — "
                    f"home-tile title will fall back to raw column name "
                    f"'{interp.get('indicator', pair_dir)}'. Register a "
                    f"layperson-friendly label in pair_registry.indicator_names."
                ),
            })
        target_key = interp.get("target", "")
        if target_key and target_key not in target_names:
            _integrity_issues.append({
                "pair_id": pair_dir,
                "missing_fields": ["display_target_unregistered"],
                "note": (
                    f"target '{target_key}' not in target_names dict — "
                    f"home-tile target label will fall back to raw ticker. "
                    f"Register a layperson-friendly label."
                ),
            })

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
