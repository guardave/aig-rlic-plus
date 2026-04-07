"""Finding 3 — The Strategy: TED Variants Tournament Winners."""

import os, sys, json
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.execution_panel import render_execution_panel

st.set_page_config(page_title="TED Strategy | AIG-RLIC+", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
render_sidebar()
render_glossary_sidebar()

st.title("The Strategy: Three Tournament Winners")
st.markdown("*Each TED variant has its own optimal strategy. Here is the winner from each.*")
st.markdown("---")

VARIANTS = [
    ("sofr_ted_spy", "A: SOFR - DTB3", "2023-01-01"),
    ("dff_ted_spy", "B: DFF - DTB3 (Fed Funds TED)", "2018-01-01"),
    ("ted_spliced_spy", "C: Spliced TED", "2018-01-01"),
]

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")

for pid, label, oos_start in VARIANTS:
    st.markdown(f"### {label}")

    results_path = os.path.join(BASE, "results", pid, "tournament_results_20260314.csv")
    if not os.path.exists(results_path):
        st.warning(f"No tournament results for {pid}")
        continue

    tdf = pd.read_csv(results_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    bh = tdf[tdf["signal"] == "BENCHMARK"]

    if len(valid) == 0:
        st.info("No valid strategies found.")
        continue

    best = valid.loc[valid["oos_sharpe"].idxmax()]
    bh_sharpe = f"{bh.iloc[0]['oos_sharpe']:.2f}" if len(bh) > 0 else "—"
    bh_dd = f"{bh.iloc[0]['max_drawdown']:.1f}%" if len(bh) > 0 else "—"

    # Winner spotlight
    st.markdown(
        f"> **Winner:** {best['signal']} / {best['threshold']} / {best['strategy']} / "
        f"Lead {int(best['lead_days'])}d"
    )

    best_ret = f"{best['oos_ann_return']:+.1f}%" if "oos_ann_return" in best.index else "—"
    bh_ret = f"{bh.iloc[0]['oos_ann_return']:+.1f}%" if len(bh) > 0 and "oos_ann_return" in bh.columns else "—"

    kpi_row([
        {"label": "OOS Sharpe", "value": f"{best['oos_sharpe']:.2f}", "delta": f"vs {bh_sharpe} B&H"},
        {"label": "OOS Return", "value": best_ret, "delta": f"vs {bh_ret} B&H"},
        {"label": "Max Drawdown", "value": f"{best['max_drawdown']:.1f}%", "delta": f"vs {bh_dd} B&H", "delta_color": "inverse"},
        {"label": "Valid / Total", "value": f"{len(valid)}", "delta": f"of {len(tdf)}"},
    ])

    # Tournament scatter
    load_plotly_chart(f"{pid}_tournament_scatter", pair_id=pid,
        caption=f"All {len(tdf)} combinations. Stars = top 5, diamond = buy-and-hold.")

    # Top 5 leaderboard
    top5 = valid.nlargest(5, "oos_sharpe")
    rows = []
    for rank, (_, r) in enumerate(top5.iterrows(), 1):
        ret_str = f"{r['oos_ann_return']:+.1f}%" if "oos_ann_return" in r.index else "—"
        rows.append({
            "Rank": rank, "Signal": r["signal"], "Threshold": r["threshold"],
            "Strategy": r["strategy"], "Lead": f"{int(r['lead_days'])}d",
            "OOS Sharpe": round(r["oos_sharpe"], 2),
            "OOS Return": ret_str,
            "Max DD": f"{r['max_drawdown']:.1f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Download button for this variant
    from components.trade_history import reconstruct_winner_history
    history = reconstruct_winner_history(pid)
    if history is not None:
        csv = history.to_csv(index=False)
        st.download_button(
            label=f"Download {label} trading history CSV",
            data=csv,
            file_name=f"{pid}_winner_trading_history.csv",
            mime="text/csv",
            key=f"dl_{pid}",
        )

    # Execution panel for this variant
    with st.expander(f"Execution Panel: {label}", expanded=False):
        render_execution_panel(pid)

    st.markdown("---")

# --- Cross-Variant Comparison ---
st.markdown("### Cross-Variant Comparison")

comp_rows = []
for pid, label, oos_start in VARIANTS:
    results_path = os.path.join(BASE, "results", pid, "tournament_results_20260314.csv")
    if not os.path.exists(results_path):
        continue
    tdf = pd.read_csv(results_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    bh = tdf[tdf["signal"] == "BENCHMARK"]
    if len(valid) == 0:
        continue
    best = valid.loc[valid["oos_sharpe"].idxmax()]
    bh_s = bh.iloc[0]["oos_sharpe"] if len(bh) > 0 else 0

    # Load interpretation
    interp_path = os.path.join(BASE, "results", pid, "interpretation_metadata.json")
    direction = "—"
    if os.path.exists(interp_path):
        with open(interp_path) as f:
            interp = json.load(f)
            direction = interp.get("observed_direction", "—")

    comp_rows.append({
        "Variant": label,
        "OOS Period": f"{oos_start[:7]} →",
        "Best Sharpe": round(best["oos_sharpe"], 2),
        "B&H Sharpe": round(bh_s, 2),
        "Improvement": f"+{(best['oos_sharpe'] - bh_s):.2f}",
        "Max DD": f"{best['max_drawdown']:.1f}%",
        "Direction": direction.replace("_", " ").title(),
        "Winner Signal": best["signal"],
    })

st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

st.markdown("---")

st.warning(
    "**Caveats:**\n\n"
    "1. **Variant A (SOFR)** has only 3 years OOS — high variance, results may not generalize.\n\n"
    "2. **Variant C (Spliced)** assumes the affine adjustment holds out-of-sample — a structural assumption.\n\n"
    "3. **Variant B (DFF-TED)** is the most conservative choice — longest continuous history, no splicing assumptions.\n\n"
    "4. All variants show funding stress has **some** predictive power, but the effect is modest compared to credit spreads (HY-IG)."
)

st.markdown("---")
st.markdown('<div class="portal-footer">Generated with AIG-RLIC+</div>', unsafe_allow_html=True)
