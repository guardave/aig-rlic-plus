"""Two-track display (Phase B; design: temp/_issues/twotrack_app_design.md).

Rendered only for pairs that publish results/{pair_id}/track_summary.json (pairs rebuilt on scripts/harness);
every element is driven by the artifact's `track_state`, never by a pair id. Vocabulary: MAIN = "As known at
the time", COMPARISON = "As revised today (hindsight)". Facts only: no verdict words, no colour by sign.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import load_plotly_chart
from components.schema_check import validate_or_die

_REPO = Path(__file__).resolve().parents[2]
C_MAIN, C_REV = "#0072B2", "#D55E00"
MAIN_LABEL = "As known at the time"
REV_LABEL = "As revised today (hindsight)"
STRIP = {
    "both": ("Data basis: as known at the time (main), with as-revised-today data for comparison",
             "Data as known at the time covers {rt_window}. Data as revised today covers {rev_window}. Values as "
             "known at the time are what investors could see then; as-revised-today values are today's corrected "
             "numbers."),
    "rt_insufficient": ("Data basis: history as known at the time is too short", ""),
    "single_market": ("Data basis: market prices (one track)",
                      "Market prices are not revised after publication, so the two data views are identical. There "
                      "is no separate comparison."),
    "single_no_archive": ("Data basis: as revised today only (one track)",
                          "No archive of earlier values exists for this source, so we cannot show what was known at "
                          "the time. Results may include hindsight from later revisions."),
}
TIPS = {
    "main": "The indicator values as they were published at each date, before later revisions.",
    "plateau": "The winner's lead sits in a run of three neighbouring leads that all scored well in training.",
    "chance": "Share of contests run on scrambled (time-shifted) indicator data whose best score the real winner beat.",
}


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def load_track_summary(pair_id: str) -> dict | None:
    """The pair's track_summary.json (validated), or None when the pair has not been rebuilt on the harness."""
    path = _REPO / "results" / pair_id / "track_summary.json"
    if not path.exists():
        return None
    return validate_or_die(path, "track_summary")


def _years(window) -> str:
    if not window or not window[0]:
        return "n/a"
    a, b = pd.Timestamp(window[0]), pd.Timestamp(window[1])
    return f"{a.year}-{b.year} ({(b - a).days / 365.25:.0f} years)"


def _lead_unit(winner: dict) -> str:
    return {"months": "months", "quarters": "quarters", "days": "trading days"}.get(winner.get("lead_unit"), "")


def _pct(v) -> str:
    return "n/a" if v is None else f"{v * 100:.1f}%"


def _num(v) -> str:
    return "n/a" if v is None else f"{v:.2f}"


def _badge(label: str, help_text: str, color: str = "blue") -> None:
    fn = getattr(st, "badge", None)
    if fn is not None:
        fn(label, color=color, help=help_text)
    else:  # older Streamlit
        st.markdown(f"`{label}`", help=help_text)


def render_data_basis_strip(ts: dict) -> None:
    """Strip under the title: headline + caption by track_state and labelled history bars (sections 4-5)."""
    state = ts["track_state"]
    head, cap = STRIP[state]
    main, comp = ts.get("main") or {}, ts.get("comparison") or {}
    with st.container(border=True):
        st.markdown(f"**{head}**")
        if state == "rt_insufficient":
            ir = ts.get("insufficient_reason") or {}
            st.markdown(f"The archive of values as known at the time starts {ir.get('rt_start') or 'n/a'}, which leaves "
                        f"{ir.get('n_is_rows', 'n/a')} training rows, fewer than the {ir.get('min_required')} the "
                        "method requires. We did not substitute the as-revised-today result as the headline.")
        elif cap:
            st.caption(cap.format(rt_window=_years(main.get("window")), rev_window=_years(comp.get("window"))))
        rows = [({"single_market": "Market data", "single_no_archive": "As revised today"}.get(state, MAIN_LABEL),
                 main.get("window"), C_MAIN)]
        if comp and comp.get("window"):
            rows.append((REV_LABEL, comp.get("window"), C_REV))
        rows = [r for r in rows if r[1] and r[1][0]]
        if rows:
            fig = go.Figure()
            for i, (lab, win, col) in enumerate(rows):
                a, b = pd.Timestamp(win[0]), pd.Timestamp(win[1])
                fig.add_trace(go.Bar(y=[i], x=[(b - a).total_seconds() * 1000], base=[a], orientation="h",
                                     marker_color=col, textfont=dict(color="white", size=13),
                                     text=[f"{lab} {_years(win)}"], textposition="inside", insidetextanchor="start",
                                     hoverinfo="text", hovertext=[f"{lab}: {win[0]} to {win[1]}"], showlegend=False))
            fig.update_layout(height=60 + 34 * len(rows), margin=dict(l=8, r=8, t=8, b=24), template="plotly_white",
                              yaxis=dict(visible=False, autorange="reversed"), xaxis=dict(type="date"), bargap=0.25)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        missing = [r for r in comp.get("recessions_covered", []) if r not in main.get("recessions_covered", [])]
        if state == "both" and missing:
            st.markdown(f"History as known at the time does not include the {' or the '.join(missing)}.")


def render_chips(ts: dict, winner: dict) -> None:
    """Chip row under the winner spotlight (section 2.4)."""
    plat = ts.get("plateau") or {}
    nt = ts.get("null_tournament") or {}
    cols = st.columns(3)
    with cols[0]:
        _badge(MAIN_LABEL if ts["track_state"] == "both" else
               {"single_market": "Market data (one track)", "single_no_archive": "As revised today only",
                "rt_insufficient": "No winner as known at the time"}[ts["track_state"]], TIPS["main"])
    with cols[1]:
        leads = plat.get("leads") or []
        if leads:
            _badge(f"Stable lead range L{min(leads)}-L{max(leads)}", TIPS["plateau"])
    with cols[2]:
        pct = nt.get("winner_percentile")
        if pct is None:
            label = "Chance check not yet run for this pair."
        elif pct >= 1:
            label = f"Chance check: above all {nt.get('n_draws')} scrambled runs"
        else:
            label = f"Chance check: above {round(pct * 100)}% of scrambled runs"
        _badge(label, TIPS["chance"], "gray")


def render_kpi_caption(ts: dict, ws: dict) -> None:
    """Secondary caption under the KPI row: the as-revised-today winner, never a KPI card (section 3)."""
    comp = ts.get("comparison")
    if ts["track_state"] != "both" or not comp or not comp.get("eligible"):
        return
    w = comp["winner"]
    gap = comp.get("sharpe_gap")
    txt = (f"Winner on revised data: Sharpe {_num(comp['oos_sharpe'])} over {_years(comp['window'])[:9]} "
           "(hindsight; shown for comparison only).")
    if gap is not None:
        txt += f" The two differ by {abs(gap):.2f} Sharpe"
        txt += ("; the as-revised-today winner is a different rule "
                f"({w['signal']}/{w['threshold']}/L{w['lead']})." if not comp.get("same_winner") else ".")
    st.caption(txt)


def _facts(vb: dict, main: dict) -> list[str]:
    """Fixed fact templates of section 7 (no verdict words)."""
    lo, hi = vb["ci_95"]
    d = vb["sharpe_diff"]
    out = [f"The test-period Sharpe difference is {d:+.2f} (95% interval {lo:+.2f} to {hi:+.2f}). "
           + ("We cannot statistically distinguish the strategy from buy-and-hold." if lo <= 0 <= hi
              else "The interval excludes zero.")]
    ar, av, dd = vb["ann_return"], vb["ann_vol"], vb["max_dd"]
    if ar["strat"] is not None and ar["bh"] is not None and ar["strat"] < ar["bh"] and av["strat"] < av["bh"]:
        out.append(f"Annual return was lower than buy-and-hold ({_pct(ar['strat'])} vs {_pct(ar['bh'])}) with lower "
                   f"volatility ({_pct(av['strat'])} vs {_pct(av['bh'])})"
                   + (f" and a smaller worst drawdown ({_pct(dd['strat'])} vs {_pct(dd['bh'])})."
                      if dd["strat"] is not None and dd["bh"] is not None and dd["strat"] > dd["bh"] else "."))
    if d < 0:
        out.append(f"Test-period Sharpe was below buy-and-hold ({_num(main['oos_sharpe'])} vs "
                   f"{_num(main['oos_sharpe'] - d)}).")
    return out


def render_vs_buy_hold(ts: dict, ws: dict) -> None:
    """'Compared with buy-and-hold' panel (section 7)."""
    vb = ts.get("vs_buy_hold")
    if not vb:
        return
    main = ts["main"]
    bh_sharpe = (ws.get("tracks", {}).get("main") or {}).get("bh_oos", {}).get("sharpe")
    with st.container(border=True):
        st.markdown("#### Compared with buy-and-hold")
        rows = [("Test-period Sharpe", _num(main["oos_sharpe"]), _num(bh_sharpe),
                 _num(main["oos_sharpe"] - bh_sharpe) if bh_sharpe is not None else "n/a"),
                ("Annual return", _pct(vb["ann_return"]["strat"]), _pct(vb["ann_return"]["bh"]),
                 _pct(vb["ann_return"]["strat"] - vb["ann_return"]["bh"])),
                ("Annual volatility", _pct(vb["ann_vol"]["strat"]), _pct(vb["ann_vol"]["bh"]),
                 _pct(vb["ann_vol"]["strat"] - vb["ann_vol"]["bh"])),
                ("Worst drawdown", _pct(vb["max_dd"]["strat"]), _pct(vb["max_dd"]["bh"]),
                 _pct(vb["max_dd"]["strat"] - vb["max_dd"]["bh"]))]
        st.table(pd.DataFrame(rows, columns=["", "Strategy", "Buy-and-hold", "Difference"]).set_index(""))
        for f in _facts(vb, main):
            st.markdown(f)
        unit = {"months": "month", "quarters": "quarter", "days": "trading-day"}.get(ws.get("lead_unit"), "period")
        st.caption(f"Paired block bootstrap, {vb['draws']:,} draws, {vb['block_length']}-{unit} blocks.")


def _tourn_row(pair_id: str, prefix: str, tag: str, key: str) -> dict | None:
    p = _REPO / "results" / pair_id / f"{prefix}tournament_results_{tag}.csv"
    if not p.exists():
        return None
    t = pd.read_csv(p)
    hit = t[t.get("key", pd.Series(dtype=str)) == key]
    return None if hit.empty else hit.iloc[0].to_dict()


def render_cross_eval_table(pair_id: str, ts: dict, ws: dict) -> None:
    """Four-row cross-evaluation table for the Performance tab (section 3)."""
    tracks = ws.get("tracks") or {}
    main, comp = tracks.get("main"), tracks.get("comparison")
    st.markdown("### Each data track's winner, scored on both tracks")
    if ts["track_state"] in ("single_market", "single_no_archive") or not comp:
        st.caption("This pair has one data track, so only its own winner row applies.")
    tag = ws["selection"]["raw_winner_row"]["source_tournament_file"].split("_")[-1].removesuffix(".csv") \
        if ws.get("selection") else None
    ce = ts.get("cross_eval") or {}

    def rule(rec):
        w = rec["winner"]
        return f"{w['signal']} / {w['threshold']} / L{w['lead']}"

    def own_row(rec, label, prefix):
        r = _tourn_row(pair_id, prefix, tag, rec["winner"]["key"]) or {}
        return [rule(rec), label, _num(rec["winner"]["is_sharpe"]), _num(rec["winner"]["oos_sharpe"]),
                _num(rec["bh_oos"]["sharpe"]), f"{rec['is_window'][0][:7]} to {rec['oos_window'][1][:7]}",
                _pct(rec["winner"]["oos_max_drawdown"]) if r is not None else "n/a"]

    def cross_row(rec, label, other, prefix):
        r = ce.get(other)
        if not isinstance(r, dict):
            return [rule(rec), label, "Not scorable: the rule is not in this track's candidate set", "", "", "", ""]
        tr = _tourn_row(pair_id, prefix, tag, rec["winner"]["key"]) or {}
        note = "" if r.get("valid") else " (did not meet the training validity filters on this data)"
        return [rule(rec), label, _num(r["is_sharpe"]) + note, _num(r["oos_sharpe"]), _num(rec["bh_oos"]["sharpe"]),
                f"{r['window']['is_start'][:7]} to {r['window']['oos_end'][:7]}", _pct(tr.get("max_drawdown"))]

    cols = ["Rule", "Data scored on", "Training Sharpe", "Test Sharpe", "B&H test Sharpe", "Window",
            "Test max drawdown"]
    rows = []
    if main and main.get("eligible"):
        rows.append(own_row(main, MAIN_LABEL, ""))
        if comp:
            rows.append(cross_row(main, REV_LABEL, "main_winner_on_revised", "hindsight_"))
    if comp and comp.get("eligible"):
        rows.append(own_row(comp, REV_LABEL, "hindsight_"))
        rows.append(cross_row(comp, MAIN_LABEL, "revised_winner_on_main", ""))
    if rows:
        df = pd.DataFrame(rows, columns=cols)
        css = pd.DataFrame("color: #595959", index=df.index, columns=df.columns)
        css.iloc[0] = "font-weight: bold"
        st.table(df.style.apply(lambda _: css, axis=None).hide(axis="index"))
    if comp:
        st.caption("Each data track picks its own winner. Rows 2 and 4 show how each winner fares on the other data.")


def render_chance_check(pair_id: str, ts: dict) -> None:
    """Chance-check panel (section 8): histogram chart + the percentile sentence (never hidden)."""
    nt = ts.get("null_tournament")
    st.markdown("### Chance check")
    if not nt or nt.get("winner_percentile") is None:
        st.info("Chance check not yet run for this pair.")
        return
    load_plotly_chart("chance_check", pair_id=pair_id,
                      fallback_text="Chance check not yet run for this pair.",
                      caption=(("The real winner's plateau score (the statistic the scrambled contests are compared on) "
                                f"is above all {nt['n_draws']:,} scrambled-signal contests"
                                if nt["winner_percentile"] >= 1 else
                                "The real winner's plateau score (the statistic the scrambled contests are compared on) "
                                f"ranks at the {_ordinal(round(nt['winner_percentile'] * 100))} percentile of "
                                f"{nt['n_draws']:,} scrambled-signal contests")
                               + " (the indicator shifted in time against the returns, same selection rule)."))


def render_lead_plateau(pair_id: str, ts: dict, ws: dict) -> None:
    """Lead chart with the stable lead range (section 6)."""
    plat = ts.get("plateau")
    st.markdown("### Lead robustness")
    if not plat:
        st.caption("No as-known-at-the-time scores exist for this pair, so no winner is marked.")
        return
    leads, wl, gl = plat["leads"], plat["winner_lead"], plat.get("global_max_lead")
    cap = f"The winner L{wl} sits in a stable range L{min(leads)}-L{max(leads)}"
    if leads != list(range(min(leads), max(leads) + 1)):
        cap += f" (adjacent grid points {', '.join(str(x) for x in leads)} {_lead_unit(ws)})"
    cap += "."
    if gl is not None and not plat.get("global_max_inside_plateau"):
        cap += f" The highest single point, L{gl}, was not chosen because its neighbours score lower."
    load_plotly_chart("lead_plateau", pair_id=pair_id, fallback_text="Lead chart pending.", caption=cap)


HEADLINE_LABEL = {"both": "Test-period Sharpe (as known at the time)", "single_market": "Test-period Sharpe (market data)",
                  "single_no_archive": "Test-period Sharpe (as revised today)"}


def headline_label(ts: dict, default: str) -> str:
    """KPI label of the MAIN test-period Sharpe (Story and Strategy pages)."""
    return HEADLINE_LABEL.get(ts["track_state"], default)


def badge_status(ts: dict) -> str | None:
    """Candidate / Watchlist / Reject suggestion from the MAIN result only (design 7b): the 95% interval of the
    test-period Sharpe difference vs buy-and-hold is above zero -> Candidate, contains zero -> Watchlist, below
    zero -> Reject. None when MAIN has no winner."""
    vb = ts.get("vs_buy_hold")
    if ts["track_state"] == "rt_insufficient" or not vb:
        return None
    lo, hi = vb["ci_95"]
    return "Candidate" if lo > 0 else ("Reject" if hi < 0 else "Watchlist")


def chance_fact(ts: dict) -> str | None:
    """Neutral one-line chance-check fact for the Executive Confidence Summary (same place on every pair; it
    is neither a strength nor a risk). None when the null has not been run."""
    nt = ts.get("null_tournament")
    if not nt or nt.get("winner_percentile") is None:
        return None
    pos = (f"is above all {nt['n_draws']:,}" if nt["winner_percentile"] >= 1 else
           f"ranks at the {_ordinal(round(nt['winner_percentile'] * 100))} percentile of {nt['n_draws']:,}")
    p = nt.get("p_selection_stat")
    out = (f"the winner's stable-range score {pos} scrambled-signal contests"
           + (f" (share of contests scoring at least as high: {p:.2f})" if p is not None else "") + ".")
    if nt.get("r71_pass") is False:
        out += " The scrambled contests do not meet the R7.1 calibration check (see the caveats)."
    return out


BADGE_RULE = ("Badge rule (as-known-at-the-time result only): Candidate when the 95% interval of the test-period "
              "Sharpe difference versus buy-and-hold is above zero, Watchlist when it contains zero, Reject when it "
              "is below zero.")


def render_badge_note(ts: dict) -> None:
    """Line next to the Candidate / Watchlist / Reject badge (section 7b)."""
    if ts["track_state"] == "rt_insufficient":
        st.caption("No status: no winner on data as known at the time.")
    else:
        st.caption("Suggestion from the as-known-at-the-time result; you judge. " + BADGE_RULE)
