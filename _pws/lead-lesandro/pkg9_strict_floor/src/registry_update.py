"""Apply the 2026-10-16 strict lead floor to docs/schemas/lead_axis_registry.json and write the
per-pair release-lag evidence CSV. Run from the worktree root."""
import json, sys
import pandas as pd
from pathlib import Path

PK = Path(__file__).resolve().parent
REG = Path("docs/schemas/lead_axis_registry.json")
OUT = Path("_pws/lead-lesandro/pkg9_strict_floor/release_lag_evidence.csv")
gaps = pd.read_csv(PK / "release_gaps_by_period.csv", parse_dates=["ref_date", "first_release", "period_end"])

EV = "ALFRED first-vintage realtime_start, ref periods 2018-01..2026-09"
# pair -> (series key in gaps or None, E*, position_shift, evidence method, publication_lag text)
P = {
 "busloans_spy": ("BUSLOANS", 2, 0, EV, "Fed H.8, ~12 days after month-end (ALFRED median 12 d, p90 15 d); released in M+1"),
 "cass_freight_spy": ("FRGSHPUSM649NCIS", 2, 0, EV, "Cass Information Systems, ~2 weeks after month-end (ALFRED median 14 d, p90 18 d); released in M+1"),
 "cc_delinquency_spy": ("DRCCLACBS", 2, 0, EV, "Federal Reserve, ~7 weeks after quarter-end (ALFRED 48-56 d, median 51 d, p90 55 d; one 76-d shutdown outlier); released in the following quarter"),
 "cement_spy": ("USGS_CEMENT_MIS", 5, 0, "USGS Mineral Industry Surveys 'Cement in <month>' PDF publication (S3 Last-Modified) dates, 2021-09..2026-06; S&P Global confirms Apr-2025 data published 2025-07-24", "USGS monthly cement survey, ~2-3 months after month-end (median 72 d, p90 122 d; 55-91 d before the 2025 shutdown, 95-165 d since 2025-07)"),
 "consumer_sentiment_spy": ("UMCSENT", 1, 0, EV, "U. Michigan, preliminary mid-month and final at or before the end of the survey month (ALFRED median -3.5 d, p90 0 d)"),
 "eci_total_comp_spy": ("ECIALLCIV", 2, 0, EV, "BLS, ~1 month after quarter-end (ALFRED median 30.5 d, p90 31 d); released in the following quarter"),
 "gold_copper_xli": (None, 1, 0, "real-time market prices observed at the close (no publication lag)", "none (observed at market close)"),
 "housing_starts_rebuilt_spy": ("HOUST", 2, 0, EV, "Census/HUD, ~17th-19th of M+1 (ALFRED median 18 d, p90 21 d)"),
 "housing_starts_spy": ("HOUST", 2, 0, EV, "Census/HUD, ~17th-19th of M+1 (ALFRED median 18 d, p90 21 d)"),
 "hy_ig_spy": (None, 2, 1, "ICE BofA OAS: FRED posts the value dated t on the next business day (ALFRED daily realtime_start is stamped at the observation date, so not usable here); registry decision fix261016_hmm_causal", None),
 "import_price_spy": ("IR", 2, 0, EV, "BLS, ~mid of M+1 (ALFRED median 15 d, p90 17 d)"),
 "indpro_spy": ("INDPRO", 2, 1, EV, "Federal Reserve G.17, ~mid of M+1 (ALFRED median 16 d, p90 18 d)"),
 "indpro_xlp": ("INDPRO", 2, 1, EV, "Federal Reserve G.17, ~mid of M+1 (ALFRED median 16 d, p90 18 d)"),
 "ism_mfg_spy": ("ISM_MFG", 2, 0, "ISM Report On Business calendar: 1st business day of M+1 (not on FRED); stakeholder chose E2 over E1 + 1-day execution delay (2026-10-16)", "ISM, 1st business day of M+1 (1-3 calendar days after month-end)"),
 "ism_services_spy": ("ISM_SERVICES", 2, 0, "ISM Report On Business calendar: 3rd business day of M+1 (not on FRED)", "ISM, 3rd business day of M+1 (3-5 calendar days after month-end)"),
 "m2sl_yoy_spy": ("M2SL", 2, 0, EV, "Fed H.6, 4th week of M+1 (ALFRED median 23 d, p90 28 d; thinnest E2 margin in the fleet)"),
 "mfg_new_orders_spy": ("AMTMNO", 3, 0, EV + " (AMTMNO, Census M3 full report)", "Census M3 full report, ~5 weeks after month-end, early M+2 (ALFRED median 34 d, p90 40 d)"),
 "nhs_rebuilt_spy": ("HSN1FNSA", 2, 0, EV, "Census, ~24th-26th of M+1 (ALFRED median 25 d, p90 29 d)"),
 "nhs_saar_rebuilt_spy": ("HSN1F", 2, 0, EV, "Census, ~24th-26th of M+1 (ALFRED median 25 d, p90 29 d)"),
 "nhs_saar_spy": ("HSN1F", 2, 0, EV, "Census, ~24th-26th of M+1 (ALFRED median 25 d, p90 29 d)"),
 "nhs_spy": ("HSN1FNSA", 2, 0, EV, "Census, ~24th-26th of M+1 (ALFRED median 25 d, p90 29 d)"),
 "permit_spy": ("PERMIT", 2, 1, EV, "Census/HUD, ~17th-19th of M+1 (ALFRED median 18 d, p90 21 d)"),
 "permit_yoy_spy": ("PERMIT", 2, 0, EV, "Census/HUD, ~17th-19th of M+1 (ALFRED median 18 d, p90 21 d)"),
 "petrol_inv_spy": ("EIA_WPSR_WTTSTUS1", 2, 0, "EIA Weekly Petroleum Status Report calendar (Wednesday after the week-ending Friday; WTTSTUS1 not on FRED); monthly signal = calendar-month mean of weekly stocks, so the last weekly print of M is released 0-5 d into M+1", "EIA weekly, released the Wednesday after the week-ending Friday; the month's last print lands 0-5 days into M+1 (median 2 d, p90 5 d)"),
 "phlxsox_spy": (None, 1, 0, "real-time market prices observed at the close (no publication lag)", "none (observed at market close)"),
 "retail_inv_sales_spy": ("RETAILIRSA", 3, 0, EV + " (RETAILIRSA, Census MTIS)", "Census MTIS, ~6-7 weeks after month-end, mid M+2 (ALFRED median 46 d, p90 49 d)"),
 "rsxfs_spy": ("RSXFS", 2, 0, EV, "Census advance retail sales, ~mid of M+1 (ALFRED median 16 d, p90 18 d)"),
 "sloos_ci_small_spy": ("DRTSCIS", 1, 0, EV + " (DRTSCIS)", "Fed SLOOS, published early Feb/May/Aug/Nov, i.e. inside the quarter it is stamped to (ALFRED median -56 d vs quarter-end)"),
 "t10y3m_rebuilt_spy": (None, 2, 1, "Treasury par yield curve posted after the close; FRED T10Y3M posts the value on the next business day (ALFRED daily realtime_start stamped at the observation date, not usable); conservative E2 consistent with hy_ig_spy and ism_mfg_spy", "Treasury daily par curve posted after the close; FRED next business day (sampled at month-end)"),
 "t10y3m_spy": (None, 2, 1, "Treasury par yield curve posted after the close; FRED T10Y3M posts the value on the next business day (ALFRED daily realtime_start stamped at the observation date, not usable); conservative E2 consistent with hy_ig_spy and ism_mfg_spy", "Treasury daily par curve posted after the close; FRED next business day (sampled at month-end)"),
 "umcsent_spy": ("UMCSENT", 1, 0, EV + " (UMCSENT as calendar proxy: the expected-business-conditions component is published with the same survey release)", "U. Michigan survey, preliminary mid-month and final at or before the end of the survey month (ALFRED UMCSENT median -3.5 d, p90 0 d)"),
 "umcsent_xlv": ("UMCSENT", 1, 1, EV, "U. Michigan, preliminary mid-month and final at or before the end of the survey month (ALFRED median -3.5 d, p90 0 d)"),
 "unrate_spy": ("UNRATE", 2, 0, EV, "BLS Employment Situation, 1st Friday of M+1 (ALFRED median 5 d, p90 8 d)"),
 "vix_vix3m_spy": (None, 1, 1, "real-time market prices observed at the close (no publication lag)", "none (observed at market close)"),
 "wells_fargo_housing_spy": ("NAHB_HMI", 1, 0, "NAHB/Wells Fargo HMI release calendar: ~mid-month of the survey month itself (~11th business day; not on FRED)", "NAHB, ~mid-month of the survey month itself (released ~2 weeks before month-end)"),
}
reg = json.loads(REG.read_text())
pairs = reg["pairs"]
rows = []
for pid, (sk, E, sh, method, pub) in P.items():
    rec = pairs[pid]
    old = dict(lead_floor=rec.get("lead_floor"), shift=rec.get("position_shift", 0),
               eff=rec.get("lead_floor_effective", rec.get("lead_floor", 0) + rec.get("position_shift", 0)),
               grid=list(rec["lead_grid"]))
    label = E - sh
    newgrid = [g for g in old["grid"] if g >= label]
    unit = {"months": "M", "quarters": "Q", "trading_days": "d"}[rec["lead_axis"]]
    g = gaps[gaps.series_id == sk] if sk else None
    stats = {}
    if g is not None and len(g):
        stats = dict(n_periods=len(g), sample=f"{g.ref_date.min().date()}..{g.ref_date.max().date()}",
                     lag_min_d=int(g.lag_days.min()), lag_med_d=float(g.lag_days.median()),
                     lag_p90_d=round(float(g.lag_days.quantile(.9)), 1), lag_max_d=int(g.lag_days.max()))
        for e in (E - 1, E):
            if e >= 1 and f"gap_E{e}" in g:
                c = g[f"gap_E{e}"]
                stats[f"gap_at_E{'_floor_minus_1' if e == E - 1 else '_floor'}_med_d"] = float(c.median())
                stats[f"gap_at_E{'_floor_minus_1' if e == E - 1 else '_floor'}_p90_d"] = round(float(c.quantile(.9)), 1)
                stats[f"pct_lookahead_at_E{'_floor_minus_1' if e == E - 1 else '_floor'}"] = round(100 * float((c > 0).mean()), 1)
        last = g.sort_values("ref_date").tail(4)
        stats["recent_releases"] = "; ".join(f"{r.ref_date.date()}->{r.first_release.date()} ({r.lag_days} d)" for r in last.itertuples())
    rows.append(dict(pair_id=pid, source_series=sk or "-", evidence_method=method, lead_axis=rec["lead_axis"],
                     old_lead_floor=old["lead_floor"], old_position_shift=old["shift"], old_effective_floor=old["eff"],
                     strict_floor_effective=E, position_shift=sh, new_lead_floor=label,
                     old_registry_grid=f"{old['grid'][0]}..{old['grid'][-1]} (n={len(old['grid'])})" if old["grid"] == list(range(old['grid'][0], old['grid'][-1] + 1)) else str(old["grid"]),
                     new_registry_grid=f"{newgrid[0]}..{newgrid[-1]} (n={len(newgrid)})" if newgrid == list(range(newgrid[0], newgrid[-1] + 1)) else str(newgrid),
                     **stats))
    rec["lead_floor"] = label
    rec["position_shift"] = sh
    rec["lead_floor_effective"] = E
    rec["lead_grid"] = newgrid
    if pub:
        rec["publication_lag"] = pub
    rec["floor_basis"] = (f"STRICT floor (standard Step 2, amended 2026-10-16): effective lag E = lead + position_shift >= {E} "
                          f"(smallest E with first_release(M) <= period_end(M+E-1) at the 90th percentile); "
                          f"lead_floor {label} = {E} - position_shift {sh}. Evidence: {method}; "
                          f"_pws/lead-lesandro/pkg9_strict_floor/release_lag_evidence.csv. "
                          + (f"Grid truncated from the bottom (top not extended, protocol D2): "
                             f"{old['grid'][0]}..{old['grid'][-1]} -> {newgrid[0]}..{newgrid[-1]}." if newgrid != old["grid"] else "Grid unchanged."))
reg["x-version"] = "1.3.0"
reg["x-generated"] = "2026-10-16 (strict lead floor on the effective lag; release-lag evidence from ALFRED first vintages; sub-floor leads truncated from the bottom)"
reg["notes"] = reg["notes"].replace(
    "lead_floor / publication_lag are REFERENCE metadata (Step 2 real-time floor) and are NOT gate-enforced — the gate checks AXIS ONLY, never selection windows/caps/floors.",
    "lead_floor / publication_lag are REFERENCE metadata for scripts/gate_lead_axis.py (axis only). Since 2026-10-16 the floors ARE enforced by scripts/gate_lead_floor.py: lead_floor_effective is the strict floor on the effective lag (lead + position_shift) and lead_floor = lead_floor_effective - position_shift.")
REG.write_text(json.dumps(reg, indent=2) + "\n")
OUT.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(OUT, index=False)
# per-period detail for the evidence file as well
gaps.to_csv(OUT.with_name("release_dates_by_period.csv"), index=False)
print(pd.DataFrame(rows)[["pair_id","source_series","old_lead_floor","old_effective_floor","strict_floor_effective","position_shift","new_lead_floor","old_registry_grid","new_registry_grid"]].to_string(index=False))
