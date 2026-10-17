"""D2-09 (EXPLORATORY, descriptive): common-sample and power budget for every registered hypothesis.

For each hypothesis in the frozen registry (d780845f) on the HISTORICAL point-in-time data available today:
  * common window = latest member start .. earliest member end (strict PIT starts; local data plus the pinned FRED
    T10Y3M, gap G8), with the target asset's return history; "evaluable" window = common window minus a 60-month
    initial training span and minus the label horizon at the end;
  * events in the evaluable window: NBER recessions (and how many fall in the viewed window V-D), SPY drawdown
    episodes >= 15% on monthly closes, SPY 10-month-SMA exit episodes;
  * a minimum detectable effect (80% power, two-sided 5%, no multiplicity) by endpoint type, with the method named;
  * a label fixed by the registered D2-09 rule: "underpowered" if MDE > 2 x margin, else "MDE <= 2x margin";
    "no MDE method" where none is registered; "+ event-limited" if the window holds fewer events than the
    hypothesis's min_events (events: recessions for U4 endpoints, SMA exits for re-entry, SPY drawdowns >= 15% for
    overlay endpoints; regime episodes of interaction / IR / divergence endpoints are not counted here);
    "blocked (Gx)" if a do-not-acquire data gap stops it. FLEET members use 1997-12 as a typical fleet IS start.
Simplifications are the ones recorded in KNOWN_LIMITS.md section 3 (iid CVaR simulation, binary-contrast
interaction, no BSS MDE). Exploratory: no verdict words.
"""
from __future__ import annotations

import json
import sys
from math import ceil, log, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p2data as d  # noqa: E402

sys.path.insert(0, str(d.REPO / "docs" / "indicator_combos" / "scripts"))
from power_notes import cvar_mde  # noqa: E402

OUT = d.P2 / "d2_09"
SIGMA = 4.5          # pp, monthly s.d. of US equity excess returns (stated assumption)
BURN_IN = 60         # months of initial training before evaluation (stated assumption)
Z = 2.8              # z_0.975 + z_0.8

# strict point-in-time first usable month (transform included) and last month, local data + pinned FRED T10Y3M
START = {"T10Y3M": "1982-01", "HY_IG_OAS": "2000-01", "HY_OAS": "2000-01", "VIX": "2000-01", "VIX3M": "2007-01",
         "GOLD_COPPER": "2001-01", "SOX_SPY": "1995-05", "FEDFUNDS": "2000-01", "SPX_SECTOR_INDICES": "1990-07",
         "SPY": "1993-02", "NBER": "1980-01", "UNRATE": "1981-04", "INDPRO": "1981-01", "PERMIT": "1999-08",
         "HSN1F": "1999-07", "HOUST": "1981-01", "M2SL": "1981-01", "BUSLOANS": "1996-12", "NEWORDER": "1997-03",
         "UMCSENT": "1998-07", "RSXFS": "2001-06", "DRTSCILM": "2010-04", "DRCCLACBN": "2011-05",
         "ISM_MFG": "1985-02", "NAHB_HMI": "1985-01", "USGS_CEMENT_MIS": "2007-04", "FLEET": "1997-12"}
END = {"HY_IG_OAS": "2026-04", "HY_OAS": "2026-04", "VIX": "2026-04", "FEDFUNDS": "2026-04", "VIX3M": "2026-03",
       "GOLD_COPPER": "2026-05"}
EVENT_KIND = {"cvar_overlay": "drawdown", "false_exit_rate": "drawdown", "capture_share": "drawdown",
              "plateau_k": "drawdown", "lexicographic_recession": "recession", "brier_skill": "recession",
              "pr_difference": "recession", "missed_rally": "sma_exit"}
DERIVED_START = {"D1-23": "2006-01", "D1-19": "2001-01", "D1-29": "2011-05", "D1-30": "2000-01", "D2-12": "2001-01"}
BLOCKED_SERIES = {"NFCI": "G15"}
ASSET_START = {"SPY": "1993-02", "Treasury": "2000-01", "NBER": "1980-01"}


def asset_info(asset: str) -> tuple[str | None, str | None]:
    a = asset.lower()
    if "nber" in a:
        return "1980-01", None
    if "treasury" in a:
        return "2000-01", None
    if a.strip() == "spy":
        return "1993-02", None
    if a.strip() == "none":
        return "2001-08", None
    return None, "G17"          # sector / relative / XHB / QQQ returns need total-return series


def episodes_dd(r: pd.Series, thr: float = 0.15) -> list[pd.Timestamp]:
    """Start months of drawdown episodes >= thr on monthly closes (an episode ends at a new high)."""
    level = (1 + r.fillna(0)).cumprod()
    peak, out, in_dd, hit = level.iloc[0], [], False, False
    start = None
    for t, v in level.items():
        if v >= peak:
            if in_dd and hit:
                out.append(start)
            peak, in_dd, hit = v, False, False
        else:
            if not in_dd:
                in_dd, start = True, t
            if v / peak - 1 <= -thr:
                hit = True
    if in_dd and hit:
        out.append(start)
    return out


def sma_exits(p: pd.Series) -> list[pd.Timestamp]:
    f = (p < p.rolling(10).mean())
    return list(f.index[(f & ~f.shift(1, fill_value=False)) & p.rolling(10).mean().notna()])


def mde(h: dict, n: int, rng) -> tuple[float | None, str]:
    ep, pr = h["endpoint"], h["pass_rule"]
    t, T = ep["type"], n / 12
    if n < 24:
        return None, "window too short"
    if t == "cvar_overlay":
        v = cvar_mde(max(1, round(T)), 0.8, sims=1500, rng=rng)["mde_rel_reduction_80pct_power"]
        return (None if isinstance(v, str) else v), "Monte Carlo, iid Student-t(5), rho 0.8 (KNOWN_LIMITS 3)"
    if t == "interaction":
        hz = ep["params"].get("return_horizon_months", 1)
        s, m = SIGMA * sqrt(hz), n / hz
        if "level x level" in h["rule"] or "term x credit" in ep["statistic"]:
            return round(Z * s / sqrt(m), 2), "continuous product, 1 s.d. x 1 s.d., iid"
        return round(Z * sqrt(s ** 2 / (m * 0.2) + s ** 2 / (m * 0.8)), 2), "binary regime share 0.2, iid"
    if t == "information_ratio":
        k = sqrt(2) if "difference" in ep["statistic"] else 1
        return round(Z * k / sqrt(T), 2), "SE(IR) ~ 1/sqrt(years)"
    if t == "forward_return_diff":
        hz = ep["params"]["return_horizon_months"]
        s, m = SIGMA * sqrt(hz), n / hz
        return round(Z * sqrt(s ** 2 / (m * 0.2) + s ** 2 / (m * 0.8)), 2), "state share 0.2, non-overlapping"
    return None, f"no MDE method for {t} (event-limited or not computed)"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reg = yaml.safe_load((d.REPO / "docs/indicator_combos/registry/hypotheses.yaml").read_text())
    fams = yaml.safe_load((d.REPO / "docs/indicator_combos/registry/families.yaml").read_text())["families"]
    spy = d.spy_monthly()
    rng = np.random.default_rng(20261018)
    rec_eps = d.recession_episodes()
    rows = []
    for q in reg["questions"]:
        for h in q["hypotheses"]:
            mem = [q["members"][k] for k in h["members"]]
            blocked = sorted({BLOCKED_SERIES[m["series"]] for m in mem if m["series"] in BLOCKED_SERIES})
            starts, ends = [], ["2026-09"]
            for m in mem:
                s = m["series"]
                if s == "DERIVED":
                    starts.append(DERIVED_START.get(q["id"], "2001-01"))
                elif s in START:
                    starts.append(START[s])
                ends.append(END.get(s, "2026-09"))
            a_start, a_gap = asset_info(h["asset"])
            if a_gap:
                blocked.append(a_gap)
            if a_start:
                starts.append(a_start)
            start = pd.Period(max(starts), "M")
            end = pd.Period(min(ends), "M") - h["label_horizon_months"]
            ev_start = start + BURN_IN
            n = max(0, (end - ev_start).n + 1)
            w0, w1 = ev_start.to_timestamp(how="end").normalize(), end.to_timestamp(how="end").normalize()
            recs = [pk for pk, tr in rec_eps if tr >= w0 and pk <= w1]
            r = spy["ret"].loc[w0:w1]
            dd = episodes_dd(r) if len(r) > 12 else []
            ex = [e for e in sma_exits(spy["spy_close"]) if w0 <= e <= w1]
            if blocked:
                v, how, label = None, "blocked", f"blocked ({', '.join(sorted(set(blocked)))})"
            else:
                v, how = mde(h, n, rng)
                kind = EVENT_KIND.get(h["endpoint"]["type"], "state")
                n_events = {"recession": len(recs), "sma_exit": len(ex), "drawdown": len(dd)}.get(kind)
                if v is None:
                    label = "no MDE method"
                elif abs(v) > 2 * abs(h["pass_rule"]["margin"]):
                    label = "underpowered"
                else:
                    label = "MDE <= 2x margin"
                if n_events is not None and n_events < h["min_events"]:
                    label += "; event-limited"
                elif n_events is None:
                    label += "; regime episodes not counted"
            fam = fams[h["family"]]
            rows.append({"hid": h["hid"], "status_registered": h["status"], "family": h["family"],
                         "family_tests": fam["n_total"], "asset": h["asset"], "endpoint": h["endpoint"]["type"],
                         "common_start": str(start), "evaluable_window": f"{ev_start}..{end}" if n else "none",
                         "months": n, "years": round(n / 12, 1), "recessions": len(recs),
                         "recessions_in_VD_2020": int(any(str(p.date())[:4] == "2020" for p in recs)),
                         "spy_drawdowns_15pct": len(dd), "sma_exit_episodes": len(ex),
                         "min_events_registered": h["min_events"], "margin": h["pass_rule"]["margin"],
                         "mde_80pct": v, "mde_method": how, "label": label})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "budget.csv", index=False)
    summ = {"status": "Exploratory (descriptive)", "registry": "frozen d780845f", "assumptions":
            {"sigma_pp_month": SIGMA, "burn_in_months": BURN_IN, "power": 0.8, "alpha_two_sided": 0.05,
             "multiplicity": "not included in MDE; family test counts listed per row"},
            "n_hypotheses": len(df), "label_counts": df["label"].value_counts().to_dict(),
            "by_family": df.groupby("family")["label"].value_counts().unstack(fill_value=0).to_dict(orient="index")}
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print(df[["hid", "evaluable_window", "years", "recessions", "spy_drawdowns_15pct", "mde_80pct", "margin",
              "label"]].to_string())
    print(json.dumps(summ["label_counts"], indent=1))


if __name__ == "__main__":
    main()
