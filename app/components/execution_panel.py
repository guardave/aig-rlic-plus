"""Strategy Execution Panel — cross-agent composition layer.

READ-ONLY / DISPLAY-ONLY module.

This module assembles 8 sub-components from existing agent outputs into a
tabbed Streamlit layout. It does NOT compute metrics, create charts, or
interpret statistical outputs.

Every displayed number traces to a specific file + field.
Every chart is loaded via load_plotly_chart().
Every interpretive sentence comes from upstream agent files.
"""

import json
import os
from glob import glob
from pathlib import Path

import pandas as pd
import streamlit as st

from components.charts import load_plotly_chart

_BASE = Path(__file__).resolve().parents[2]
_RESULTS_DIR = str(_BASE / "results")


# ── Path Resolution ──────────────────────────────────────────────────────────

def _resolve_paths(pair_id: str) -> dict:
    """Resolve all file paths for a pair, handling legacy vs nested layouts.

    Returns a dict of paths. Missing files have None values.
    """
    pair_dir = os.path.join(_RESULTS_DIR, pair_id)

    # Tournament results
    tourn_files = sorted(glob(os.path.join(pair_dir, "tournament_results_*.csv")))
    tourn_path = tourn_files[-1] if tourn_files else None

    # Date tag from tournament file
    date_tag = None
    if tourn_path:
        # Extract YYYYMMDD from tournament_results_YYYYMMDD.csv
        basename = os.path.basename(tourn_path)
        date_tag = basename.replace("tournament_results_", "").replace(".csv", "")

    # Winner summary (from Evan's pipeline extension)
    winner_summary_path = os.path.join(pair_dir, "winner_summary.json")

    # Execution notes (from Evan)
    execution_notes_path = os.path.join(pair_dir, "execution_notes.md")

    # Trade log (from Evan)
    trade_log_path = os.path.join(pair_dir, "winner_trade_log.csv")

    # Interpretation metadata
    metadata_path = os.path.join(pair_dir, "interpretation_metadata.json")

    # Validation directory — nested or legacy
    validation_dir = None
    if date_tag:
        nested = os.path.join(pair_dir, f"tournament_validation_{date_tag}")
        if os.path.isdir(nested):
            validation_dir = nested
    if validation_dir is None and pair_id == "hy_ig_spy":
        legacy = sorted(glob(os.path.join(_RESULTS_DIR, "tournament_validation_*")))
        if legacy:
            validation_dir = legacy[-1]

    # Exploratory results
    exploratory_dir = None
    if date_tag:
        exp = os.path.join(pair_dir, f"exploratory_{date_tag}")
        if os.path.isdir(exp):
            exploratory_dir = exp
    if exploratory_dir is None:
        # Legacy flat
        exp_legacy = sorted(glob(os.path.join(_RESULTS_DIR, f"exploratory_*")))
        if exp_legacy and pair_id == "hy_ig_spy":
            exploratory_dir = exp_legacy[-1]

    # Core models
    core_models_dir = None
    if date_tag:
        cm = os.path.join(pair_dir, f"core_models_{date_tag}")
        if os.path.isdir(cm):
            core_models_dir = cm
    if core_models_dir is None and pair_id == "hy_ig_spy":
        cm_legacy = sorted(glob(os.path.join(_RESULTS_DIR, "core_models_*")))
        if cm_legacy:
            core_models_dir = cm_legacy[-1]

    # Chart directory
    chart_dir_nested = str(_BASE / "output" / "charts" / pair_id / "plotly")
    chart_dir_legacy = str(_BASE / "output" / "charts" / "plotly")

    def _exists_or_none(path):
        return path if os.path.exists(path) else None

    return {
        "tournament_results": _exists_or_none(tourn_path) if tourn_path else None,
        "winner_summary": _exists_or_none(winner_summary_path),
        "execution_notes": _exists_or_none(execution_notes_path),
        "trade_log": _exists_or_none(trade_log_path),
        "metadata": _exists_or_none(metadata_path),
        "validation_dir": validation_dir,
        "exploratory_dir": exploratory_dir,
        "core_models_dir": core_models_dir,
        "chart_pair_id": pair_id if os.path.isdir(chart_dir_nested) else None,
        "date_tag": date_tag,
    }


# ── File Loaders (cached, read-only) ────────────────────────────────────────

@st.cache_data(ttl=3600)
def _load_json(path: str) -> dict | None:
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


@st.cache_data(ttl=3600)
def _load_csv(path: str) -> pd.DataFrame | None:
    if path and os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_data(ttl=3600)
def _load_markdown(path: str) -> str | None:
    if path and os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def _file_exists(directory: str | None, filename: str) -> bool:
    if directory is None:
        return False
    return os.path.exists(os.path.join(directory, filename))


# ── Component Renderers ─────────────────────────────────────────────────────

def _render_strategy_summary(summary: dict | None, metadata: dict | None):
    """Component 1: Plain-English strategy summary.

    Sources: winner_summary.json (Evan), interpretation_metadata.json (Ray).
    """
    if summary is None:
        st.info("Strategy summary pending — run pipeline extension.")
        return

    signal_display = summary.get("signal_display_name", summary.get("signal_code", "—"))
    threshold_display = summary.get("threshold_display_name",
                                    summary.get("threshold_label", "—"))
    strategy_display = summary.get("strategy_display_name",
                                   summary.get("strategy_type", "—"))
    lead_display = summary.get("lead_description")

    st.markdown(f"**Signal:** {signal_display} (`{summary.get('signal_code', '')}`)")
    st.markdown(f"**Threshold:** {threshold_display}")
    if summary.get("threshold_value") is not None:
        st.markdown(f"**Threshold Value:** {summary['threshold_value']}")
    st.markdown(f"**Strategy:** {strategy_display}")
    if lead_display:
        st.markdown(f"**Lead:** {lead_display}")

    if summary.get("strategy_description"):
        st.markdown(f"> {summary['strategy_description']}")

    if metadata and metadata.get("mechanism"):
        st.markdown(f"**Economic rationale:** {metadata['mechanism']}")


def _render_trade_visualization(paths: dict, pair_id: str):
    """Component 2: Equity curve + drawdown charts.

    Sources: Plotly JSON charts (Vera).
    Trade markers: overlaid from winner_trade_log.csv when available.
    """
    chart_pair_id = paths.get("chart_pair_id")

    # Equity curves (existing chart)
    chart_name = f"{chart_pair_id}_equity_curves" if chart_pair_id else "equity_curves"
    load_plotly_chart(
        chart_name,
        fallback_text="Equity curve chart pending.",
        pair_id=chart_pair_id,
        chart_key=f"ep_{pair_id}_performance_equity",
    )

    # Trade marker annotation
    # When winner_trade_log.csv is populated, Vera will produce an enhanced
    # equity curve chart with entry (green) / exit (red) markers overlaid.
    # Chart name: {pair_id}_equity_curves_with_trades.json
    # Until then, show a note about marker availability.
    trade_log = _load_csv(paths.get("trade_log"))
    if trade_log is not None and len(trade_log) > 0:
        st.caption(
            f"Showing {len(trade_log)} trade markers: "
            "green = entry, red = exit"
        )
    else:
        st.caption(
            "Trade entry/exit markers will overlay this chart once the "
            "trade log is populated."
        )

    # Drawdown comparison (Vera's new chart)
    chart_name = f"{chart_pair_id}_drawdown" if chart_pair_id else "drawdown_comparison"
    load_plotly_chart(
        chart_name,
        fallback_text="Drawdown chart pending — run chart generation pipeline.",
        pair_id=chart_pair_id,
        chart_key=f"ep_{pair_id}_performance_drawdown",
    )


def _render_trade_table(paths: dict, pair_id: str):
    """Component 3: Pre-computed trade log.

    Source: winner_trade_log.csv (Evan).
    Ace only renders; does not compute trade metrics.
    """
    # Resolve path explicitly using absolute Path — do not rely on paths dict
    trade_log_path = _BASE / "results" / pair_id / "winner_trade_log.csv"

    # TODO: Remove debug lines after confirming path resolution on Streamlit Cloud
    st.write(f"Trade log path: {trade_log_path}")
    st.write(f"Exists: {trade_log_path.exists()}")

    if not trade_log_path.exists():
        st.info("Trade log pending — requires data pipeline to generate "
                "`winner_trade_log.csv`.")
        return

    trade_log = _load_csv(str(trade_log_path))
    if trade_log is None or len(trade_log) == 0:
        st.info("Trade log will appear once pipeline data is available.")
        return

    st.dataframe(
        trade_log,
        use_container_width=True,
        hide_index=True,
        column_config={
            "entry_date": st.column_config.TextColumn("Entry Date"),
            "exit_date": st.column_config.TextColumn("Exit Date"),
            "direction": st.column_config.TextColumn("Direction"),
            "holding_days": st.column_config.NumberColumn("Holding (days)"),
            "trade_return_pct": st.column_config.NumberColumn(
                "Return (%)", format="%.2f%%"
            ),
        },
    )
    st.caption(f"{len(trade_log)} trades total")


def _render_trigger_breakdown(summary: dict | None, metadata: dict | None):
    """Component 4: Signal/threshold/lead breakdown.

    Sources: winner_summary.json (Evan), interpretation_metadata.json (Ray).
    Ace displays codes and display names; does not compute threshold values.
    """
    if summary is None:
        st.info("Trigger breakdown pending — run pipeline extension.")
        return

    signal_display = summary.get("signal_display_name", summary.get("signal_code", "—"))
    threshold_display = summary.get("threshold_display_name",
                                    summary.get("threshold_label", "—"))
    strategy_display = summary.get("strategy_display_name",
                                   summary.get("strategy_type", "—"))
    lead_display = summary.get("lead_description")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Signal**")
        st.markdown(f"`{summary.get('signal_code', '—')}` — {signal_display}")
        st.markdown("**Threshold**")
        st.markdown(f"{threshold_display}")
        if summary.get("threshold_value") is not None:
            st.markdown(f"**Threshold Value:** {summary['threshold_value']}")

    with col2:
        st.markdown("**Strategy Type**")
        st.markdown(f"{strategy_display}")
        if lead_display:
            st.markdown("**Lead Time**")
            st.markdown(f"{lead_display}")
        direction = metadata.get("expected_direction", "unknown") if metadata else "unknown"
        st.markdown(f"**Direction:** {direction.replace('_', '-')}")


def _render_market_regime(paths: dict, pair_id: str):
    """Component 5: Current regime + historical regime performance.

    Sources: regime_descriptive_stats.csv (Evan), regime_stats chart (Vera).
    """
    # Regime descriptive stats table
    regime_csv = None
    if paths.get("exploratory_dir"):
        regime_path = os.path.join(paths["exploratory_dir"], "regime_descriptive_stats.csv")
        regime_csv = _load_csv(regime_path)

    if regime_csv is not None:
        st.markdown("**Historical Regime Performance**")
        st.dataframe(
            regime_csv,
            use_container_width=True,
            hide_index=True,
            column_config={
                "regime": st.column_config.TextColumn("Regime"),
                "n_months": st.column_config.NumberColumn("Months"),
                "ann_return_pct": st.column_config.NumberColumn("Ann. Return (%)", format="%.1f%%"),
                "ann_vol_pct": st.column_config.NumberColumn("Ann. Vol (%)", format="%.1f%%"),
                "sharpe": st.column_config.NumberColumn("Sharpe", format="%.3f"),
            },
        )
    else:
        st.info("Regime statistics pending.")

    # Regime chart (pre-built by Vera)
    chart_pair_id = paths.get("chart_pair_id")
    chart_name = f"{chart_pair_id}_regime_stats" if chart_pair_id else "returns_by_regime"
    load_plotly_chart(
        chart_name,
        fallback_text="Regime chart pending.",
        pair_id=chart_pair_id,
        chart_key=f"ep_{pair_id}_performance_regime",
    )

    # Current regime (from Markov regime probs if available)
    if paths.get("core_models_dir"):
        regime_probs_path = os.path.join(paths["core_models_dir"],
                                         "markov_regime_probs_2state.csv")
        regime_probs = _load_csv(regime_probs_path)
        if regime_probs is not None and len(regime_probs) > 0:
            last_row = regime_probs.iloc[-1]
            # Display last regime probability without interpretation
            st.markdown("**Latest Regime Probabilities** "
                        f"(last observation in dataset)")
            prob_cols = [c for c in regime_probs.columns if "prob" in c.lower()
                         or "regime" in c.lower()]
            if prob_cols:
                display_data = {col: [f"{last_row[col]:.3f}"] for col in prob_cols
                                if col in last_row.index}
                if display_data:
                    st.dataframe(pd.DataFrame(display_data), hide_index=True)


def _render_strategy_sop(paths: dict, summary: dict | None):
    """Component 6: Step-by-step execution instructions.

    Source: execution_notes.md (Evan — domain-expert authored).
    Ace renders the markdown; Ace does not author execution guidance.
    """
    notes = _load_markdown(paths.get("execution_notes"))
    if notes is not None:
        st.markdown(notes)
    elif summary is not None:
        # Minimal fallback: show raw parameters without interpretation
        st.markdown("**Execution parameters (raw)**")
        st.markdown(f"- Signal: `{summary.get('signal_code', '—')}`")
        st.markdown(f"- Threshold: {summary.get('threshold_label', summary.get('threshold_code', '—'))}")
        st.markdown(f"- Strategy: {summary.get('strategy_type', summary.get('strategy_code', '—'))}")
        lead = summary.get("lead_description")
        if lead:
            st.markdown(f"- Lead: {lead}")
        turnover = summary.get("annual_turnover")
        if turnover is not None:
            st.markdown(f"- Turnover: ~{turnover:.1f}/yr")
        st.info("Full execution notes pending — run pipeline extension.")
    else:
        st.info("Strategy SOP pending — run pipeline extension.")


def _render_confidence(paths: dict, metadata: dict | None):
    """Component 7: Statistical confidence metrics.

    Sources: bootstrap.csv, stress_tests.csv, walk_forward.csv (Evan),
             confidence field from interpretation_metadata.json (Evan+Ray).
    Ace displays numbers only; does not interpret significance.
    """
    # Confidence badge from metadata
    if metadata:
        confidence = metadata.get("confidence", "unknown")
        badge_colors = {"high": "green", "medium": "orange", "low": "red"}
        color = badge_colors.get(confidence, "gray")
        st.markdown(f"**Overall Confidence:** :{color}[{confidence.upper()}]")
    else:
        st.markdown("**Overall Confidence:** unknown")

    validation_dir = paths.get("validation_dir")
    if validation_dir is None:
        st.info("Validation data pending. Confidence assessment based on "
                "interpretation metadata only.")
        return

    # Bootstrap results
    bootstrap = _load_csv(os.path.join(validation_dir, "bootstrap.csv")
                          if validation_dir else None)
    if bootstrap is not None:
        st.markdown("**Bootstrap Validation**")
        # Handle both schemas: nested has different columns than legacy
        st.dataframe(bootstrap, use_container_width=True, hide_index=True)

    # Stress tests
    stress = _load_csv(os.path.join(validation_dir, "stress_tests.csv")
                       if validation_dir else None)
    if stress is not None:
        st.markdown("**Stress Test Performance**")
        st.dataframe(stress, use_container_width=True, hide_index=True)

    # Walk-forward
    walk_fwd = _load_csv(os.path.join(validation_dir, "walk_forward.csv")
                         if validation_dir else None)
    if walk_fwd is not None:
        st.markdown("**Walk-Forward Validation**")
        st.dataframe(walk_fwd, use_container_width=True, hide_index=True)

    # Transaction costs
    tx_costs = _load_csv(os.path.join(validation_dir, "transaction_costs.csv")
                         if validation_dir else None)
    if tx_costs is not None:
        st.markdown("**Transaction Cost Sensitivity**")
        st.dataframe(tx_costs, use_container_width=True, hide_index=True)


def _render_evidence_source(paths: dict, metadata: dict | None, pair_id: str):
    """Component 8: Links to underlying econometric evidence.

    Sources: interpretation_metadata.json (Evan+Ray), file existence checks.
    Ace renders links; does not interpret evidence.
    """
    if metadata and metadata.get("key_finding"):
        st.markdown(f"**Key Finding:** {metadata['key_finding']}")

    # Evidence availability based on file existence
    evidence_types = []
    if paths.get("core_models_dir"):
        cm = paths["core_models_dir"]
        checks = [
            ("Granger Causality", "granger_causality.csv"),
            ("Local Projections", "local_projections.csv"),
            ("Predictive Regressions", "predictive_regressions.csv"),
            ("Cointegration", "cointegration.csv"),
            ("Quantile Regression", "quantile_regression.csv"),
            ("Markov Switching", "markov_switching_2state.csv"),
            ("Random Forest", "rf_feature_importance.csv"),
        ]
        for name, filename in checks:
            available = _file_exists(cm, filename)
            evidence_types.append({"Evidence Type": name,
                                   "Status": "Available" if available else "Pending"})

    if evidence_types:
        st.dataframe(pd.DataFrame(evidence_types),
                     use_container_width=True, hide_index=True)

    # Caveats from metadata
    if metadata and metadata.get("caveats"):
        with st.expander("Caveats & Limitations", expanded=False,
                         key=f"ep_{pair_id}_caveats"):
            for caveat in metadata["caveats"]:
                st.markdown(f"- {caveat}")

    # Link to Evidence page
    from components.pair_registry import load_pair_registry
    registry = load_pair_registry()
    pair_info = next((p for p in registry if p["pair_id"] == pair_id), None)
    if pair_info and pair_info.get("evidence_page"):
        st.page_link(pair_info["evidence_page"],
                     label="View Full Evidence Page",
                     icon="🔬")


# ── Top-Level Orchestrator ──────────────────────────────────────────────────

def render_execution_panel(pair_id: str):
    """Render the complete Strategy Execution Panel for a pair.

    Single entry point called from each strategy page.
    Read-only — all data comes from pre-computed files.
    """
    st.markdown("---")
    st.markdown("### Strategy Execution Panel")

    paths = _resolve_paths(pair_id)
    summary = _load_json(paths.get("winner_summary"))
    metadata = _load_json(paths.get("metadata"))

    tab_execute, tab_performance, tab_confidence = st.tabs(
        ["Execute", "Performance", "Confidence"],
        key=f"ep_tabs_{pair_id}",
    )

    with tab_execute:
        with st.container():
            st.markdown("#### Strategy Summary")
            _render_strategy_summary(summary, metadata)

        st.markdown("---")

        with st.container():
            st.markdown("#### Trigger Breakdown")
            _render_trigger_breakdown(summary, metadata)

        st.markdown("---")

        with st.container():
            st.markdown("#### Strategy SOP")
            _render_strategy_sop(paths, summary)

    with tab_performance:
        with st.container():
            st.markdown("#### Trade Visualization")
            _render_trade_visualization(paths, pair_id)

        st.markdown("---")

        with st.container():
            st.markdown("#### Trade Log")
            _render_trade_table(paths, pair_id)

        st.markdown("---")

        with st.container():
            st.markdown("#### Market Regime")
            _render_market_regime(paths, pair_id)

    with tab_confidence:
        with st.container():
            st.markdown("#### Confidence Assessment")
            _render_confidence(paths, metadata)

        st.markdown("---")

        with st.container():
            st.markdown("#### Evidence Sources")
            _render_evidence_source(paths, metadata, pair_id)
