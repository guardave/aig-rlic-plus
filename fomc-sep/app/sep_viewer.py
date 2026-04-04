"""FOMC SEP Viewer — Interactive dot plot and projections explorer."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="FOMC SEP Viewer", page_icon="🏛️", layout="wide")

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data")

st.title("FOMC Summary of Economic Projections")
st.markdown("*Explore dot plots and projections from 2012 to present*")
st.markdown("---")


@st.cache_data
def load_dots():
    path = os.path.join(DATA, "sep_dot_plot.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["meeting_date"] = df["meeting_date"].astype(str)
        return df
    return pd.DataFrame()


@st.cache_data
def load_fred():
    path = os.path.join(DATA, "fred", "sep_all_fred.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    return pd.DataFrame()


@st.cache_data
def load_registry():
    path = os.path.join(DATA, "sep_meeting_registry.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


dots = load_dots()
fred = load_fred()
registry = load_registry()

# Sidebar
with st.sidebar:
    st.markdown("## Navigation")
    page = st.radio("View", ["Dot Plot Explorer", "FRED Projections", "Meeting Registry"])
    st.markdown("---")
    st.markdown(f"**{len(registry)} meetings** in registry")
    if len(dots) > 0:
        st.markdown(f"**{len(dots):,} dot entries** extracted")
    st.markdown(f"**{len(fred):,} FRED observations**")


if page == "Dot Plot Explorer":
    st.markdown("### Federal Funds Rate Dot Plot")

    if len(dots) == 0:
        st.warning("No dot plot data available. Run `03_scrape_html_tables.py` first.")
    else:
        # Meeting selector
        meetings = sorted(dots["meeting_date"].unique(), reverse=True)
        meeting_labels = {m: f"{m[:4]}-{m[4:6]}-{m[6:8]}" for m in meetings}

        col1, col2 = st.columns([1, 3])
        with col1:
            selected = st.selectbox(
                "Select meeting",
                meetings,
                format_func=lambda m: meeting_labels[m],
            )

        meeting_dots = dots[dots["meeting_date"] == selected]

        # Clean horizon labels
        horizon_map = {
            "current_year": "Current Year",
            "year_plus1": "Year +1",
            "year_plus2": "Year +2",
            "longer_run": "Longer Run",
            "col_4": "Longer Run",
        }
        meeting_dots = meeting_dots.copy()
        meeting_dots["horizon_label"] = meeting_dots["horizon"].map(horizon_map).fillna(meeting_dots["horizon"])

        # Fed-style dot plot (Figure 2 in SEP PDF):
        # Y-axis = rate levels (percent), X-axis = horizon years
        # Each dot = one participant, dots equally spaced & centered at each rate level
        import numpy as np

        horizons_ordered = ["Current Year", "Year +1", "Year +2", "Longer Run"]
        active_horizons = [h for h in horizons_ordered
                           if len(meeting_dots[meeting_dots["horizon_label"] == h]) > 0]

        # Y-axis range from data
        all_rates = sorted(meeting_dots["rate"].unique())
        y_min = max(0, min(all_rates) - 0.5)
        y_max = max(all_rates) + 0.5
        # Round to nice 0.5 boundaries
        y_min = np.floor(y_min * 2) / 2
        y_max = np.ceil(y_max * 2) / 2

        fig = go.Figure()

        # Fixed dot spacing — equal gap between every dot
        dot_gap = 0.045

        # Horizon year labels
        year = int(selected[:4])
        horizon_xlabels = [str(year), str(year + 1), str(year + 2), "Longer run"]

        for col_idx, horizon in enumerate(active_horizons):
            h_dots = meeting_dots[meeting_dots["horizon_label"] == horizon]

            for _, row in h_dots.iterrows():
                rate = row["rate"]
                n = int(row["num_participants"])
                if n == 0:
                    continue

                # Center n dots with equal spacing
                offsets = [(i - (n - 1) / 2) * dot_gap for i in range(n)]
                x_positions = [col_idx + off for off in offsets]

                fig.add_trace(go.Scatter(
                    x=x_positions,
                    y=[rate] * n,
                    mode="markers",
                    marker=dict(
                        size=7,
                        color="#5b9bd5",
                        line=dict(width=0.5, color="#3a7ab5"),
                    ),
                    hovertemplate=(
                        f"{horizon_xlabels[col_idx]}<br>"
                        f"Rate: {rate:.3f}%<br>"
                        f"{n} participant(s)<extra></extra>"
                    ),
                    showlegend=False,
                ))

        fig.update_layout(
            title=dict(
                text=(
                    "FOMC participants' assessments of appropriate monetary policy:<br>"
                    "<sup>Midpoint of target range or target level for the federal funds rate</sup>"
                ),
                font=dict(size=13),
            ),
            template="plotly_white",
            height=550,
            showlegend=False,
            margin=dict(t=80),
            xaxis=dict(
                tickvals=list(range(len(active_horizons))),
                ticktext=horizon_xlabels[:len(active_horizons)],
                range=[-0.5, len(active_horizons) - 0.5],
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                title="Percent",
                dtick=0.5,
                range=[y_min, y_max],
                showgrid=True,
                gridcolor="rgba(0,0,0,0.1)",
                gridwidth=0.5,
                zeroline=False,
            ),
            plot_bgcolor="white",
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary stats
        st.markdown("#### Summary by Horizon")
        summary_rows = []
        for horizon in horizons_ordered:
            h_dots = meeting_dots[meeting_dots["horizon_label"] == horizon]
            if len(h_dots) == 0:
                continue
            # Reconstruct all individual rates
            all_rates = []
            for _, row in h_dots.iterrows():
                all_rates.extend([row["rate"]] * int(row["num_participants"]))
            if all_rates:
                summary_rows.append({
                    "Horizon": horizon,
                    "Participants": len(all_rates),
                    "Median": f"{pd.Series(all_rates).median():.3f}%",
                    "Min": f"{min(all_rates):.3f}%",
                    "Max": f"{max(all_rates):.3f}%",
                    "Range": f"{max(all_rates) - min(all_rates):.3f}pp",
                })
        if summary_rows:
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        # Compare two meetings
        st.markdown("---")
        st.markdown("### Compare Two Meetings")
        col1, col2 = st.columns(2)
        with col1:
            meet_a = st.selectbox("Meeting A", meetings, index=0, format_func=lambda m: meeting_labels[m], key="a")
        with col2:
            meet_b = st.selectbox("Meeting B", meetings, index=min(1, len(meetings)-1), format_func=lambda m: meeting_labels[m], key="b")

        if meet_a != meet_b:
            fig2 = go.Figure()
            for meeting_id, color, name in [(meet_a, "#1f77b4", meeting_labels[meet_a]),
                                             (meet_b, "#d62728", meeting_labels[meet_b])]:
                m_dots = dots[dots["meeting_date"] == meeting_id]
                m_dots = m_dots.copy()
                m_dots["horizon_label"] = m_dots["horizon"].map(horizon_map).fillna(m_dots["horizon"])

                # Use "longer_run" horizon median as a simple summary
                for hi, horizon in enumerate(horizons_ordered):
                    h_data = m_dots[m_dots["horizon_label"] == horizon]
                    all_rates = []
                    for _, row in h_data.iterrows():
                        all_rates.extend([row["rate"]] * int(row["num_participants"]))
                    if all_rates:
                        median_rate = pd.Series(all_rates).median()
                        fig2.add_trace(go.Bar(
                            x=[horizon], y=[median_rate],
                            name=name, marker_color=color,
                            text=f"{median_rate:.2f}%", textposition="outside",
                        ))

            fig2.update_layout(
                title="Median Fed Funds Rate: Meeting Comparison",
                barmode="group",
                yaxis_title="Median Rate (%)",
                template="plotly_white",
                height=400,
            )
            st.plotly_chart(fig2, use_container_width=True)


elif page == "FRED Projections":
    st.markdown("### FRED SEP Summary Statistics")

    if len(fred) == 0:
        st.warning("No FRED data. Run `01_fred_sep_series.py` first.")
    else:
        variables = fred["variable"].unique().tolist()
        selected_var = st.selectbox("Variable", variables,
                                     format_func=lambda v: v.replace("_", " ").title())

        var_data = fred[fred["variable"] == selected_var]
        stats = var_data["statistic"].unique().tolist()

        # Plot projections over time
        lr_stats = [s for s in stats if "_lr" in s]
        non_lr_stats = [s for s in stats if "_lr" not in s]

        if lr_stats:
            st.markdown("#### Longer-Run Projections Over Time")
            fig = go.Figure()
            for stat in lr_stats:
                s_data = var_data[var_data["statistic"] == stat].sort_values("date")
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(s_data["date"]),
                    y=s_data["value"],
                    mode="lines+markers",
                    name=stat.replace("_lr", " (LR)").replace("_", " ").title(),
                ))
            fig.update_layout(
                title=f"{selected_var.replace('_', ' ').title()} — Longer Run Projections",
                template="plotly_white", height=400,
                yaxis_title="Percent",
            )
            st.plotly_chart(fig, use_container_width=True)

        if non_lr_stats:
            st.markdown("#### Current Projections Over Time")
            display_stats = ["median", "ct_mid", "ct_low", "ct_high"]
            plot_stats = [s for s in display_stats if s in non_lr_stats]
            if not plot_stats:
                plot_stats = non_lr_stats[:4]

            fig = go.Figure()
            colors = {"median": "#1f77b4", "ct_mid": "#2ca02c", "ct_low": "#aec7e8", "ct_high": "#aec7e8"}
            for stat in plot_stats:
                s_data = var_data[var_data["statistic"] == stat].sort_values("date")
                if len(s_data) == 0:
                    continue
                dash = "dash" if "ct_low" in stat or "ct_high" in stat else "solid"
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(s_data["date"]),
                    y=s_data["value"],
                    mode="lines+markers",
                    name=stat.replace("_", " ").title(),
                    line=dict(color=colors.get(stat, "#7f7f7f"), dash=dash),
                    marker=dict(size=5),
                ))

            var_title = selected_var.replace("_", " ").title()
            note = ""
            if selected_var in ("pce_inflation", "core_pce"):
                note = " (Fed longer-run target is 2.0%)"
            fig.update_layout(
                title=f"{var_title} — Current Projections{note}",
                template="plotly_white", height=400,
                yaxis_title="Percent",
            )
            if selected_var in ("pce_inflation", "core_pce"):
                fig.add_hline(y=2.0, line_dash="dot", line_color="red",
                              annotation_text="2% target", annotation_position="top right")
            st.plotly_chart(fig, use_container_width=True)

        if not lr_stats and not non_lr_stats:
            st.info("No projection data available for this variable.")

        # Raw data table
        st.markdown("#### Raw Data")
        pivot = var_data.pivot_table(index="date", columns="statistic", values="value")
        st.dataframe(pivot.tail(20), use_container_width=True)

        # Download
        csv = var_data.to_csv(index=False)
        st.download_button(
            f"Download {selected_var} data as CSV",
            data=csv,
            file_name=f"sep_{selected_var}.csv",
            mime="text/csv",
        )


elif page == "Meeting Registry":
    st.markdown("### FOMC SEP Meeting Registry")

    if not registry:
        st.warning("No registry. Run `02_meeting_dates.py` first.")
    else:
        reg_df = pd.DataFrame(registry)
        reg_df["has_html"] = reg_df["html_url"].notna()

        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Meetings", len(reg_df))
        col2.metric("HTML Available", reg_df["has_html"].sum())
        col3.metric("With Dot Plots", reg_df["has_dot_plot"].sum())
        col4.metric("Year Range", f"{reg_df['year'].min()}-{reg_df['year'].max()}")

        st.dataframe(
            reg_df[["date_formatted", "year", "quarter", "has_dot_plot", "source"]],
            use_container_width=True, hide_index=True,
        )


# Footer
st.markdown("---")
st.caption("Data sources: Federal Reserve (federalreserve.gov), FRED (fred.stlouisfed.org)")
