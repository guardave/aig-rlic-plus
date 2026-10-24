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

from components import provenance as P
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
BASIS = {          # how each data basis is named in shared text (single-track pairs never say 'as known at')
    "both": "as known at each date", "rt_insufficient": "as known at each date",
    "single_market": "market data, which are not revised",
    "single_no_archive": "as revised today (no archive of earlier values; may include hindsight)",
}
RESULT = {"both": "as-known-at-the-time result", "rt_insufficient": "as-known-at-the-time result",
          "single_market": "market-data result",
          "single_no_archive": "as-revised-today result (no archive of earlier values; may include hindsight)"}
TIPS = {
    "main": "The indicator values as they were published at each date, before later revisions.",
    "single_market": "Market prices, which are not revised after publication.",
    "single_no_archive": "Today's revised values: no archive of earlier values exists for this source, so results "
                         "may include hindsight from later revisions.",
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
    """'1993-2026 (34 years)': years and length tagged from the window's dates (gate mode)."""
    if not window or not window[0]:
        return "n/a"
    a, b = P.field_text(window, 0), P.field_text(window, 1)
    return f"{P.year(a)}-{P.year(b)} ({P.span_years(a, b):.0f} years)"


def _ym(d, key) -> str:
    """'YYYY-MM' of a date field of a tagged dict / list (tagged in gate mode)."""
    return P.prefix(P.field_text(d, key) or "", 7)


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


NO_MAIN_KPI = ("**No headline metrics.** There is no rule on data as known at the time: the archive of past releases "
               "is too short to train one, so this pair is unranked (no Candidate, Watchlist or Reject status). "
               "Figures computed on today's revised data are hindsight context only.")


def no_main_reason(pair_id: str) -> str:
    """'Real-time track: not eligible: ...' with the vintage start, training months available and required, tagged
    from winner_summary (Lead spec for MAIN-ineligible pairs). Falls back to NO_MAIN_KPI without the record."""
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
        ir = ws["status"]["main_not_eligible"]
        fv = ws["tracks"]["main"]["sample"].get("first_vintage")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return NO_MAIN_KPI
    unit = _lead_unit(ws) or _lead_unit((ws.get("tracks") or {}).get("comparison") or {}) or "periods"
    start = (f"real-time vintages start {P.field_text(ws['tracks']['main']['sample'], 'first_vintage')}; "
             if fv else "")
    return (f"**Real-time track: not eligible.** {start[:1].upper() + start[1:] if start else ''}"
            f"{ir['n_is_rows']:.0f} training {unit} available before the test period, {ir['min_required']:.0f} "
            "required. There is no rule on data as known at the time, so this pair is unranked (no Candidate, "
            "Watchlist or Reject status). The figures below are hindsight: a rule found on today's revised data.")


def render_no_main_headline(pair_id: str, target: str = "SPY") -> None:
    """Headline for rt_insufficient: the reason, then the hindsight (revised data) test-period figures, each
    labelled, next to buy-and-hold. Never in MAIN slots, never N/A cards."""
    st.info(no_main_reason(pair_id))
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
        c = ws["tracks"]["comparison"]
        w, b = c["winner"], c["bh_oos"]
    except (OSError, ValueError, KeyError, TypeError):
        return
    if not w:
        return
    from components.metrics import kpi_row
    off = {"delta_color": "off", "delta_arrow": "off"}      # buy-and-hold is a reference value, not a change
    kpi_row([
        dict(off, label="Hindsight test-period Sharpe (revised data)", value=f"{w['oos_sharpe']:.2f}",
             delta=f"buy-and-hold {target}: {b['sharpe']:.2f}"),
        dict(off, label="Hindsight annual return (revised data)", value=f"{w['oos_ann_return']:.1%}",
             delta=f"buy-and-hold: {b['ann_return']:.1%}"),
        dict(off, label="Hindsight max drawdown (revised data)", value=f"{w['oos_max_drawdown']:.1%}",
             delta=f"buy-and-hold: {b['max_drawdown']:.1%}"),
        dict(off, label="Hindsight rule (revised data)", value=f"{w['signal']}",     # the full rule (QA nomain)
             delta=f"{w['threshold']} / {w['strategy']} / lead {P.field_text(w, 'lead')} {_lead_unit(c)}".strip()),
    ])
NO_MAIN_EXECUTE = ("There is no rule on data as known at the time, so there is nothing to execute. The hindsight rule "
                   "found on today's revised data is not an execution plan.")
NO_MAIN_TRADES = ("No trade log: there is no rule on data as known at the time. The hindsight rule's trades are not "
                  "shown as a track record.")


def no_main(ts: dict | None) -> bool:
    """MAIN (as known at the time) has no eligible candidate: no headline, no execution plan, no trade log."""
    return bool(ts) and ts.get("track_state") == "rt_insufficient"


def render_data_basis_strip(ts: dict) -> None:
    """Strip under the title: headline + caption by track_state and labelled history bars (sections 4-5)."""
    state = ts["track_state"]
    head, cap = STRIP[state]
    main, comp = ts.get("main") or {}, ts.get("comparison") or {}
    with st.container(border=True):
        st.markdown(f"**{head}**")
        if state == "rt_insufficient":
            ir = ts.get("insufficient_reason") or {}
            st.markdown(f"The archive of values as known at the time starts "
                        f"{P.field_text(ir, 'rt_start') if ir.get('rt_start') else 'n/a'}, which leaves "
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
                                     hoverinfo="text", hovertext=[f"{lab}: {P.field_text(win, 0)} to {P.field_text(win, 1)}"], showlegend=False))
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
                "rt_insufficient": "No winner as known at the time"}[ts["track_state"]],
               TIPS.get(ts["track_state"], TIPS["main"]))
    with cols[1]:
        leads = plat.get("leads") or []
        if leads:
            _badge(f"Stable lead range L{min(leads)}-L{max(leads)}", TIPS["plateau"])
    with cols[2]:
        pct = nt.get("winner_percentile")
        hn = None
        if pct is None and ts["track_state"] == "rt_insufficient":
            try:
                hn = (winner.get("tracks") or {}).get("comparison", {}).get("null_tournament")
            except AttributeError:
                hn = None
        if pct is None and hn and hn.get("selection_stat_percentile") is not None:
            label = f"Chance check (hindsight): above {round(hn['selection_stat_percentile'] * 100)}% of scrambled runs"
        elif pct is None:
            label = "Chance check not yet run for this pair."
        elif pct >= 1:
            label = f"Chance check: above all {nt.get('n_draws')} scrambled runs"
        else:
            label = f"Chance check: above {round(pct * 100)}% of scrambled runs"
        _badge(label, TIPS["chance"], "gray")


def grid_edge_notes(pair_id: str) -> list[str]:
    """One sentence per track whose winner sits at an end of the declared lead grid (QA B1 nhs F4: shown on the
    Strategy tab next to each track's winner, not only on Confidence): a longer / shorter lead was not tested,
    so the stable range may continue beyond it. Tagged (winner lead from winner_summary, grid from the
    registry)."""
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
    except (OSError, ValueError):
        return []
    grid = P.lead_grid(pair_id)
    if not grid:
        return []
    lo, hi = min(int(g) for g in grid), max(int(g) for g in grid)
    glo = next(g for g in grid if int(g) == lo)
    ghi = next(g for g in grid if int(g) == hi)
    unit = _lead_unit(ws) or "periods"
    out = []
    # single-track pairs name their one track by its basis, never 'as known at' (ism_mfg rebase: the raw-argmax line
    # said "As known at the time" on a no-archive pair)
    main_label = {"single_revised_no_archive": "As revised today (no archive)",
                  "single_market": "Market data"}.get(str(ws.get("track_policy")), MAIN_LABEL)
    for role, label in (("main", main_label), ("comparison", REV_LABEL)):
        rec = (ws.get("tracks") or {}).get(role) or {}
        plat = rec.get("plateau") or {}
        if not rec.get("eligible"):
            continue
        # QA permit_yoy F4: the raw training-score maximum (reference row, not the selection rule) at a grid end
        ra = rec.get("raw_argmax") or {}
        rl = ra.get("lead")
        if rl is not None and int(rl) in (lo, hi) and int(rl) != int(plat.get("winner_lead", -10 ** 6)):
            out.append(f"{label}: the highest single training score in the grid (a reference row, not the selection "
                       f"rule) is at lead L{rl}, the {'longest' if int(rl) == hi else 'shortest'} lead tested (grid "
                       f"L{glo}-L{ghi} {unit}).")
        tie = plat.get("tie")
        if tie and plat.get("leads"):          # QA rsxfs F3: an exact tie on the stable-range score is disclosed
            lv = plat["leads"]
            alt = "; ".join(f"L{x[0]}-L{x[-1]}" for x in tie["alternatives"] if x)
            why = ("it has the higher best training Sharpe inside the range"
                   if tie["broken_by"] == "best_is_sharpe_in_window" else
                   "it comes first in the search order (rule families in table order, shorter leads first)")
            out.append(f"{label}: the stable range L{lv[0]}-L{lv[-1]} tied exactly on its score with {alt}; the tie "
                       f"went to L{lv[0]}-L{lv[-1]} because {why}.")
        if not plat.get("grid_edge"):
            continue
        wl = plat["winner_lead"]
        if int(wl) == hi:
            out.append(f"{label}: the winner's lead L{wl} is the longest lead tested (grid L{glo}-L{ghi} {unit}); "
                       "a longer lead was not tested, so the stable range may continue beyond it.")
        elif int(wl) == lo:
            out.append(f"{label}: the winner's lead L{wl} is the shortest lead in the grid (L{glo}-L{ghi} {unit}).")
        else:
            out.append(f"{label}: the winner's lead L{wl} is at the end of the leads its rule could be scored on "
                       f"(grid L{glo}-L{ghi} {unit}).")
    return out


def render_kpi_caption(ts: dict, ws: dict) -> None:
    """Secondary caption under the KPI row: the as-revised-today winner, never a KPI card (section 3)."""
    comp = ts.get("comparison")
    if ts["track_state"] != "both" or not comp or not comp.get("eligible"):
        return
    w = comp["winner"]
    gap = comp.get("sharpe_gap")
    # the Sharpe is the TEST-period one: name that window, not the data span (QA permit_yoy F1: "over 1993-2026")
    _w = ((ws.get("tracks") or {}).get("comparison") or {}).get("oos_window")
    span = f" over {P.year(P.field_text(_w, 0))}-{P.year(P.field_text(_w, 1))}" if _w else ""
    txt = (f"Winner on revised data: test-period Sharpe {_num(comp['oos_sharpe'])}{span} "
           "(hindsight; shown for comparison only).")
    if gap is not None:
        txt += f" The two differ by {abs(gap):.2f} Sharpe"
        txt += ("; the as-revised-today winner is a different rule "
                f"({w['signal']}/{w['threshold']}/L{w['lead']})." if not comp.get("same_winner") else ".")
    st.caption(txt)


def _signed(x) -> str:
    """'+0.12'; a value that rounds to zero at 2 dp is shown at 3 dp ('-0.004'), or '0.000' (QA B1 mfg: '+0.00')."""
    v = float(x)                              # decide on the plain value; format the (tagged) value itself
    if f"{v:+.2f}" not in ("+0.00", "-0.00"):
        return f"{x:+.2f}"
    return f"{x:+.3f}" if f"{v:+.3f}" not in ("+0.000", "-0.000") else f"{abs(x):.3f}"


def _facts(vb: dict, main: dict) -> list[str]:
    """Fixed fact templates of section 7 (no verdict words)."""
    lo, hi = vb["ci_95"]
    d = vb["sharpe_diff"]
    out = [f"The test-period Sharpe difference is {_signed(d)} (95% interval {_signed(lo)} to {_signed(hi)}). "
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
        a, b = P.field_text(ws, "oos_period_start"), P.field_text(ws, "oos_period_end")
        if a and b:     # QA permit_yoy F2: the table carried no window or data basis of its own
            st.caption(f"Test period {P.prefix(a, 7)} to {P.prefix(b, 7)}; the strategy's indicator "
                       f"{BASIS.get(ts.get('track_state'), BASIS['both'])}.")
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
    t = P.csv_file(p)                                   # cells tagged in gate mode (v5.1)
    hit = t.index[t["key"].astype(str) == key] if "key" in t.columns else []
    return None if len(hit) == 0 else {c: t[c].tolist()[t.index.get_loc(hit[0])] for c in t.columns}


def render_cross_eval_table(pair_id: str, ts: dict, ws: dict) -> None:
    """Four-row cross-evaluation table for the Performance tab (section 3)."""
    tracks = ws.get("tracks") or {}
    main, comp = tracks.get("main"), tracks.get("comparison")
    if ts["track_state"] in ("single_market", "single_no_archive") or not comp:
        st.markdown("### The winner's own row")       # cement rerun: the two-track heading showed on one track
        st.caption("This pair has one data track, so only its own winner row applies.")
    else:
        st.markdown("### Each data track's winner, scored on both tracks")
    tag = P.run_tag(ws, _REPO / "results" / pair_id)
    ce = ts.get("cross_eval") or {}

    def rule(rec):
        w = rec["winner"]
        return f"{w['signal']} / {w['threshold']} / L{w['lead']}"

    def own_row(rec, label, prefix):
        r = _tourn_row(pair_id, prefix, tag, rec["winner"]["key"]) or {}
        return [rule(rec), label, _num(rec["winner"]["is_sharpe"]), _num(rec["winner"]["oos_sharpe"]),
                _num(rec["bh_oos"]["sharpe"]), f"{_ym(rec['is_window'], 0)} to {_ym(rec['oos_window'], 1)}",
                _pct(rec["winner"]["oos_max_drawdown"]) if r is not None else "n/a"]

    def cross_row(rec, label, other, prefix):
        r = ce.get(other)
        if not isinstance(r, dict):
            return [rule(rec), label, "Not scorable: the rule is not in this track's candidate set", "", "", "", ""]
        tr = _tourn_row(pair_id, prefix, tag, rec["winner"]["key"]) or {}
        note = "" if r.get("valid") else " (did not meet the training validity filters on this data)"
        no_train = r.get("is_sharpe") is None or not (r.get("window") or {}).get("is_start")
        train = "No training window on this data" if no_train else _num(r["is_sharpe"]) + note   # nomain F5
        win = (f"test only: {_ym(r['window'], 'oos_start')} to {_ym(r['window'], 'oos_end')}" if no_train else
               f"{_ym(r['window'], 'is_start')} to {_ym(r['window'], 'oos_end')}")
        return [rule(rec), label, train, _num(r["oos_sharpe"]), _num(rec["bh_oos"]["sharpe"]), win,
                _pct(tr.get("max_drawdown"))]

    cols = ["Rule", "Data scored on", "Training Sharpe", "Test Sharpe", "B&H test Sharpe", "Window",
            "Test max drawdown"]
    rows = []
    same = bool(main and main.get("eligible") and comp and comp.get("eligible")
                and main["winner"].get("key") == comp["winner"].get("key"))
    main_label = {"single_no_archive": "As revised today (no archive)",
                  "single_market": "Market data"}.get(ts["track_state"], MAIN_LABEL)   # single tracks: umcsent_spy QA
    if same:     # both tracks pick the same rule: its two own rows already show it on both data (no duplicates)
        rows = [own_row(main, MAIN_LABEL, ""), own_row(comp, REV_LABEL, "hindsight_")]
    else:
        if main and main.get("eligible"):
            rows.append(own_row(main, main_label, ""))
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
    if same:
        st.caption("Both data tracks select the same rule, so the rows show that rule on each track's data.")
    elif comp and not (main and main.get("eligible")):
        st.caption("Only the as-revised-today (hindsight) track has a winner. The row labelled as known at the time "
                   "shows how that rule fares on that data, over the test period only (that track has no training "
                   "window).")
    elif comp:
        st.caption("Each data track picks its own winner. Rows 2 and 4 show how each winner fares on the other data.")


def render_chance_check(pair_id: str, ts: dict) -> None:
    """Chance-check panel (section 8): histogram chart + the percentile sentence (never hidden)."""
    nt = ts.get("null_tournament")
    st.markdown("### Chance check")
    if (not nt or nt.get("winner_percentile") is None) and no_main(ts):
        hn = hindsight_null(pair_id)
        st.markdown(_hindsight_chance_text(pair_id, hn) if hn else
                    "There is no rule on data as known at the time, so there is no chance check on that track, "
                    "and no hindsight null was run.")
        return
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
                               + f" (the indicator, {BASIS.get(ts.get('track_state'), BASIS['both'])}, shifted "
                                 "against the returns by a fixed number of periods, wrapping around once; same "
                                 "selection rule; every contest scored on the real winner's calendar training window, "
                                 "with periods where a contest's rule has no position counted as cash)."
                               + oos_rank_note(nt)
                               + draws_note(nt) + coarse_note(pair_id, nt) + is_window_note(pair_id)
                               + coverage_note(pair_id) + r71_note(pair_id) + comparison_chance_note(pair_id, ts)))


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
    # an exact tie on the range score is stated here too, from the same tagged sentence as the Strategy notes
    # (QA umcsent F3); the chart shows the MAIN track's curve, so only its tie
    for n in grid_edge_notes(pair_id):
        head, _sep, body = n.partition(": ")
        if "tied exactly" in body and head not in (REV_LABEL,):
            cap += f" {body[0].upper()}{body[1:]}"
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


def is_window_note(pair_id: str, track: str = "main") -> str:
    """The training windows of the scrambled contests against the real winner's (QA B1 umcsent M1: real-time
    contests at large shifts train on much shorter windows, so the percentile compares unlike samples). Read from
    results/<pair>/null_is_windows_<tag>.csv (scripts/null_is_windows.py); '' when the pair has none."""
    from components import provenance as P
    rdir = Path(__file__).resolve().parents[2] / "results" / pair_id
    try:
        f = P.current_file(pair_id, "null_is_windows")
    except P.CurrentRunFileError as e:
        return f" (The training-window comparison file is missing: {e}.)"
    if f is None:
        return ""
    try:
        df = P.csv_file(f)
        ws = json.loads((rdir / "winner_summary.json").read_text())
    except (OSError, ValueError):
        return ""
    unit = _lead_unit(ws) or "periods"
    if not {"is_n_draw", "is_n_actual"} <= set(df.columns):
        return ""
    where = None
    if "track" in df.columns:                  # files since QA nomain F4 carry every track's rows; the filter is
        where = ("track", track)               # part of the provenance tag, so the gate re-evaluates the same rows
        if not (df["track"].astype(str) == track).any():
            return ""
    elif track != "main":
        return ""
    sub = df if where is None else df[df["track"].astype(str) == track]
    if sub["is_n_actual"].notna().sum() == 0:
        return ""
    lo, hi = P.colmin(df, "is_n_draw", where), P.colmax(df, "is_n_draw", where)
    act = P.colmax(df, "is_n_actual", where)
    if float(lo) == float(hi) == float(act):
        return f" Every contest trained on the same {act:.0f} {unit} of in-sample data as the real winner."
    return (f" Training windows differ: the scrambled contests trained on {lo:.0f} to {hi:.0f} {unit} of in-sample "
            f"data, the real winner on {act:.0f}. A contest with a shorter window can reach a higher score by "
            "chance, so this comparison is not like-for-like.")


def coverage_note(pair_id: str, track: str = "main") -> str:
    """Null v4 scores every contest on the real winner's calendar training window, with months where the contest's
    selected rule has no position counted as cash. When that happens, how much (QA rerun2 F2: import_price's
    comparison contests had a median 177 of 254 defined months, up to 42% leading cash, and the page gave no
    figures). From the current null file's defined_is_n / is_n / leading_cash_share; '' when every contest's rule
    was defined throughout or the file predates null v4."""
    stem = "null_tournament" if track == "main" else "hindsight_null_tournament"
    try:
        f = P.current_file(pair_id, stem)
    except P.CurrentRunFileError as e:
        return f" (The contest file is missing: {e}.)"
    if f is None:
        return ""
    try:
        df = P.csv_file(f)
        ws = json.loads((Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json").read_text())
    except (OSError, ValueError):
        return ""
    if not {"defined_is_n", "is_n", "leading_cash_share"} <= set(df.columns):
        return ""
    short = P.count(df, "defined_is_n", "<", "is_n")
    if int(short) == 0:
        return ""
    unit = _lead_unit(ws) or "periods"
    n_win = P.count(df, "defined_is_n", ">=", 0)
    med, lead_cash = P.colmedian(df, "defined_is_n"), P.colmax(df, "leading_cash_share")
    lo, hi = P.colmin(df, "is_n"), P.colmax(df, "is_n")
    of = f"of the {hi:.0f} training {unit}" if float(lo) == float(hi) else f"training {unit}"
    low = P.colmin(df, "defined_is_n")
    out = (f" In {short:.0f} of {n_win:.0f} contests the selected rule had no position for part of that window "
           f"(counted as cash): a median of {med:.0f} (lowest {low:.0f}) {of} had a defined position")
    if float(lead_cash) > 0:
        out += (f"; in the most affected contest the first {lead_cash:.0%} of the window came before the rule's "
                f"first position")
    return out + "."


NULL_TARGET_DRAWS = 100   # harness.null.run_null K


def draws_note(nt: dict) -> str:
    """' N admissible, M with a winner; percentile from M.' when some contests produced no valid rule."""
    nw = nt.get("n_draws_without_winner") or 0
    if not nw:
        return ""
    adm = nt.get("n_admissible_offsets")
    run = nt["n_draws"] + nw
    head = f"{adm:,} admissible" if adm == run else f"{run:,} run ({adm:,} admissible)"
    return (f" Contests: {head}, {nt['n_draws']:,} with a winner ({nw:,} without a valid rule, excluded);"
            f" percentile from {nt['n_draws']:,}.")


def coarse_note(pair_id: str, nt: dict, track: str = "main") -> str:
    """When the span allows fewer contests than the null's target and every admissible shift was run (cc: 36), the
    percentile is coarse; says so with the number of effectively independent contests (Bartlett effective draws of
    the R7.1 timing-Sharpe SE, results/<pair>/winner_summary.json). '' otherwise (Lead v3.1 item 2)."""
    adm, run = nt.get("n_admissible_offsets"), nt["n_draws"] + (nt.get("n_draws_without_winner") or 0)
    if adm is None or run < adm or adm >= NULL_TARGET_DRAWS:
        return ""
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
        eff = ws["tracks"][track]["null_tournament"]["timing_sharpe_effective_draws"]
    except (OSError, ValueError, KeyError, TypeError):
        eff = None
    out = f" The percentile is coarse: this span allows only {nt['n_draws']:,} contests"
    if eff is not None:
        out += (f", about {eff:.0f} of them effectively independent (contests at neighbouring shifts overlap"
                " heavily)")
    return out + "."


def oos_rank_note(nt: dict, who: str = "real winner") -> str:
    """Where the real winner's TEST-period Sharpe falls among the scrambled contests' winners' test-period Sharpes
    (QA B1 permit N2: stored, never shown; the plateau percentile above is a training-period statistic). Tagged
    from track_summary null_tournament.winner_oos_percentile (share of null winners strictly below)."""
    q = nt.get("winner_oos_percentile")
    if q is None:
        return ""
    return (f" On the test period, the {who}'s Sharpe ranks at the "
            f"{_ordinal(round(q * 100))} percentile of the scrambled contests' winners' test-period Sharpes.")


def _r71_screen_line(T: float, rec: dict | None, on_track: str = "") -> str:
    """Option C (user 2026-10-20): the fixed |mean| > 0.10 screen, on a line of its own and never part of the
    pass / fail. Raised -> a construction review (Phase B ledger); a completed review is named from the
    calibration record's construction_review {status, ref}."""
    raised = abs(float(T)) > R71_SCREEN
    rv = (rec or {}).get("construction_review") or {}
    if not raised:
        state = "not raised"
    elif rv.get("status") == "completed":
        state = "raised; construction review completed" + (f" (see {rv['ref']})" if rv.get("ref") else "")
    else:
        state = "raised; construction review required"
    return f"\n\n{R71_SCREEN_LABEL}{on_track}: {state}.\n\n"


R71_SCREEN = 0.10
R71_SCREEN_LABEL = ("Screening flag (fixed threshold 0.10 on the absolute mean timing Sharpe; diagnostic, "
                    "not part of the check)")


def r71_note(pair_id: str, track: str = "main", label: str = "Calibration check (R7.1)") -> str:
    """The R7.1 calibration result stated on every pair, pass or fail (QA B1 umcsent F2: a pass 0.001 inside the
    tolerance was invisible), then the separate fixed screening flag on its own line (option C; Codex option-C
    C5). With a current calibrated reference (r71_calibration_<tag>.json): its paths, block length and rule,
    p-value, the 2L sensitivity and the Monte Carlo resolution in plain words; otherwise the Bartlett statement
    with the pending note. Tagged from winner_summary tracks.<track>.null_tournament / the calibration record.
    '' without a null."""
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
        n = ws["tracks"][track]["null_tournament"]
        m, se, tol, ok = (n["timing_sharpe_mean"], n["timing_sharpe_se_dependent"], n["r71_tolerance"],
                          n["r71_pass"])
    except (OSError, ValueError, KeyError, TypeError):
        return ""
    if m is None or se is None or tol is None or ok is None:
        return ""
    on_track = "" if track == "main" else " on that track"
    st_, cal, _why = P.r71_calibration(pair_id, track)
    if st_ == "ok":          # calibrated reference on file for this run (r71_calibration_<tag>.json)
        lu = ws["tracks"][track].get("lead_unit") or ws.get("lead_unit")   # no-MAIN pairs carry it per track only
        unit = {"months": "months", "quarters": "quarters", "days": "trading days"}.get(lu, "periods")
        sn = cal.get("sensitivity") or {}
        out = (f" {label} against a calibrated reference: {cal['B']:.0f} simulated return paths, each a stationary "
               f"bootstrap of the target returns resampled separately within the training and the test period, "
               f"in blocks averaging {cal['L']:.0f} {unit} (block length fixed in advance: the Politis-White rule on "
               f"squared returns, at least {cal['L_floor']:.0f} and at most {cal['L_cap']:.0f} {unit}, a quarter "
               f"of the test period), and shared by "
               f"all scrambled contests. The scrambled contests' winners have a mean timing Sharpe of "
               f"{cal['T']:.3f}, against a reference centre of {cal['centre']:.3f} and a 95% half-width of "
               f"{cal['critical_value']:.3f} (p-value {cal['p_value']:.3f}); the check "
               f"{'passes' if bool(cal['pass']) else 'does not pass'}.")
        if sn:
            out += (f" Sensitivity with fixed blocks of {sn['block']:.0f} {unit} ({sn['B']:.0f} paths): the check "
                    f"{'passes' if bool(sn['pass']) else 'does not pass'} (p-value {sn['p_value']:.3f}).")
        out += (f" Resolution: with {cal['B']:.0f} paths the p-value moves in steps of {cal['p_resolution']:.3f} "
                f"and the 95% half-width rests on the {cal['tail_paths']:.0f} paths beyond it, so it is a coarse "
                f"estimate.")
        return out + _r71_screen_line(cal["T"], cal, on_track)
    out = (f" {label}: the scrambled contests' winners have a mean timing Sharpe of {m:.3f}"
           f" (dependence-aware standard error {se:.3f}) against a tolerance of {tol:.3f} in absolute value;"
           f" the check {'passes' if bool(ok) else 'does not pass'}")
    if float(se) * 2 < float(tol) and bool(ok):    # QA EF F6: not appended to a failure, where it read as an excuse
        out += " (the tolerance is set by its fixed floor, not by the standard error)"
    return out + (". This standard error understates the spread of the null mean (independent QA and Codex review); "
                  "a calibrated reference is pending." + _r71_screen_line(m, None, on_track))


def comparison_chance_note(pair_id: str, ts: dict) -> str:
    """Two-track pairs: the comparison (as revised today) track's own chance check and R7.1, stated next to MAIN's
    (QA B1 mfg: its comparison R7.1 passed only through the floor and was not shown). '' otherwise."""
    if ts.get("track_state") != "both":
        return ""
    hn = hindsight_null(pair_id)
    if not hn:
        return ""
    pos = (f"is above all {hn['n_draws']:,}" if hn["winner_percentile"] >= 1 else
           f"ranks at the {_ordinal(round(hn['winner_percentile'] * 100))} percentile of {hn['n_draws']:,}")
    return (f" On data as revised today, that track's winner {pos} scrambled-signal contests."
            + is_window_note(pair_id, "comparison") + coverage_note(pair_id, "comparison")
            + r71_note(pair_id, "comparison", "Calibration check (R7.1) on that track"))


def hindsight_null(pair_id: str) -> dict | None:
    """rt_insufficient: the comparison (hindsight, revised data) track's null summary in the track_summary
    null_tournament shape, tagged from winner_summary tracks.comparison.null_tournament (QA nomain F1: the page
    said 'not yet run' although the hindsight null exists). None when there is none."""
    try:
        ws = P.json_file(Path(__file__).resolve().parents[2] / "results" / pair_id / "winner_summary.json")
        n = ws["tracks"]["comparison"]["null_tournament"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if not n or n.get("selection_stat_percentile") is None:
        return None
    return {"n_draws": n["n_draws"], "winner_percentile": n["selection_stat_percentile"],
            "p_selection_stat": n.get("p_selection_stat"), "winner_oos_percentile": n.get("winner_oos_percentile"),
            "n_admissible_offsets": n.get("n_admissible_offsets"),
            "n_draws_without_winner": n.get("n_draws_without_winner", 0), "r71_pass": n.get("r71_pass")}


HINDSIGHT_NULL_HEAD = ("There is no rule on data as known at the time, so that track has no chance check. Hindsight "
                       "(today's revised data): ")


def _hindsight_chance_text(pair_id: str, hn: dict) -> str:
    pos = (f"is above all {hn['n_draws']:,}" if hn["winner_percentile"] >= 1 else
           f"ranks at the {_ordinal(round(hn['winner_percentile'] * 100))} percentile of {hn['n_draws']:,}")
    p = hn.get("p_selection_stat")
    return (HINDSIGHT_NULL_HEAD + f"the hindsight winner's stable-range score {pos} scrambled-signal contests"
            + ("" if p is None else " (no contest scored as high)" if float(p) == 0 else
               f" (share of contests scoring at least as high: {p:.2f})") + "."
            + oos_rank_note(hn, "hindsight winner") + draws_note(hn) + coarse_note(pair_id, hn, "comparison")
            + is_window_note(pair_id, "comparison") + coverage_note(pair_id, "comparison")
            + r71_note(pair_id, "comparison"))


def chance_fact(ts: dict, pair_id: str | None = None) -> str | None:
    """Neutral one-line chance-check fact for the Executive Confidence Summary (same place on every pair; it
    is neither a strength nor a risk). None when the null has not been run."""
    nt = ts.get("null_tournament")
    if (not nt or nt.get("winner_percentile") is None) and no_main(ts) and pair_id:
        hn = hindsight_null(pair_id)
        return _hindsight_chance_text(pair_id, hn) if hn else None
    if not nt or nt.get("winner_percentile") is None:
        return None
    pos = (f"is above all {nt['n_draws']:,}" if nt["winner_percentile"] >= 1 else
           f"ranks at the {_ordinal(round(nt['winner_percentile'] * 100))} percentile of {nt['n_draws']:,}")
    p = nt.get("p_selection_stat")
    out = (f"the winner's stable-range score {pos} scrambled-signal contests"
           + ("" if p is None else " (no contest scored as high)" if float(p) == 0 else
              f" (share of contests scoring at least as high: {p:.2f})") + "."
           + oos_rank_note(nt)
           + draws_note(nt))
    if nt.get("r71_pass") is False:
        out += " The scrambled contests do not meet the R7.1 calibration check (see the caveats)."
    return out


BADGE_RULE = ("Badge rule (as-known-at-the-time result only): Candidate when the 95% interval of the test-period "
              "Sharpe difference versus buy-and-hold is above zero, Watchlist when it contains zero, Reject when it "
              "is below zero.")


def badge_rule(state: str) -> str:
    """BADGE_RULE naming the pair's own data basis (single-track pairs: umcsent_spy QA)."""
    return BADGE_RULE.replace("as-known-at-the-time result", RESULT.get(state, RESULT["both"]))


def render_badge_note(ts: dict) -> None:
    """Line next to the Candidate / Watchlist / Reject badge (section 7b)."""
    if ts["track_state"] == "rt_insufficient":
        st.caption("There is no rule on data as known at the time, so this pair has no Candidate, Watchlist or "
                   "Reject status.")
    else:
        st.caption(f"Suggestion from the {RESULT.get(ts['track_state'], RESULT['both'])}; you judge. "
                   + badge_rule(ts["track_state"]))
