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

        # Build dot plot chart
        fig = go.Figure()

        horizons_ordered = ["Current Year", "Year +1", "Year +2", "Longer Run"]
        colors = ["#1f77b4", "#2ca02c", "#d62728", "#7f7f7f"]

        for i, horizon in enumerate(horizons_ordered):
            h_dots = meeting_dots[meeting_dots["horizon_label"] == horizon]
            if len(h_dots) == 0:
                continue

            # Expand dots: each num_participants becomes individual markers
            rates = []
            for _, row in h_dots.iterrows():
                rates.extend([row["rate"]] * int(row["num_participants"]))

            # Add jitter within the horizon column
            import numpy as np
            np.random.seed(42)
            x_positions = [i + np.random.uniform(-0.15, 0.15) for _ in rates]

            fig.add_trace(go.Scatter(
                x=x_positions,
                y=rates,
                mode="markers",
                marker=dict(size=10, color=colors[i], opacity=0.8,
                           line=dict(width=1, color="white")),
                name=horizon,
                hovertemplate=f"{horizon}<br>Rate: %{{y:.3f}}%<extra></extra>",
            ))

        fig.update_layout(
            title=f"FOMC Dot Plot — {meeting_labels[selected]}",
            xaxis=dict(
                tickvals=list(range(len(horizons_ordered))),
                ticktext=horizons_ordered,
                title="Projection Horizon",
            ),
            yaxis=dict(title="Federal Funds Rate (%)", dtick=0.25),
            template="plotly_white",
            height=600,
            showlegend=False,
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

        # Plot median over time if available
        median_stats = [s for s in stats if "median" in s.lower()]
        lr_stats = [s for s in stats if "_lr" in s]

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
