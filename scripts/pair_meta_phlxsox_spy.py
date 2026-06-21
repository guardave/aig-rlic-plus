#!/usr/bin/env python3
"""Generate metadata artifacts for phlxsox_spy: DATA-D5 sidecars, interpretation
metadata, manifest entries, display-name registry rows. Run after data script."""
from __future__ import annotations
import json, csv, os, datetime as dt
import pandas as pd

PAIR_ID = "phlxsox_spy"
GEN_AT = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

daily = pd.read_parquet(f"data/{PAIR_ID}_daily_latest.parquet")
monthly = pd.read_parquet(f"data/{PAIR_ID}_monthly_latest.parquet")

# Resolve dated master paths
dly = [f for f in os.listdir("data") if f.startswith(f"{PAIR_ID}_daily_19")][0]
mly = [f for f in os.listdir("data") if f.startswith(f"{PAIR_ID}_monthly_19")][0]

# ---- column metadata builders ------------------------------------------
def col(dtype, unit, dn, direction, desc, src=None, ttl=1):
    e = {"dtype": dtype, "unit": unit, "display_name": dn,
         "direction": direction, "description": desc}
    if src: e["source_reference"] = src
    if ttl is not None: e["refresh_ttl_days"] = ttl
    return e

F = "float64"
# Shared definitions
DEFS = {
    "sox": col(F, "index", "PHLX Semiconductor Index", "higher_is_better",
               "PHLX Semiconductor Index (^SOX) close level. High-beta early-cycle equity index.",
               "yahoo:^SOX"),
    "spy": col(F, "price", "SPY Close ($)", "higher_is_better",
               "SPDR S&P 500 ETF auto-adjusted close. Target asset.", "yahoo:SPY"),
    "sox_ret": col(F, "decimal_return", "SOX Daily Return", "higher_is_better",
                   "1-day percent return of ^SOX as decimal.", "derived: sox[t]/sox[t-1]-1"),
    "spy_ret": col(F, "decimal_return", "SPY Daily Return", "higher_is_better",
                   "1-day percent return of SPY as decimal.", "derived: spy[t]/spy[t-1]-1"),
    "sox_ret_1m": col(F, "decimal_return", "SOX Monthly Return", "higher_is_better",
                      "1-month percent return of ^SOX (month-end).", "derived: sox[t]/sox[t-1]-1"),
    "spy_ret_1m": col(F, "decimal_return", "SPY Monthly Return", "higher_is_better",
                      "1-month percent return of SPY (month-end).", "derived: spy[t]/spy[t-1]-1"),
    "sox_spy_ratio": col(F, "ratio", "SOX/SPY Relative Strength", "higher_is_better",
                         "SOX level / SPY level. Higher = semis outperforming broad market (risk-on). Non-stationary (trending).",
                         "derived: sox / spy"),
    "sox_spy_logratio": col(F, "ratio", "SOX/SPY Log-Ratio", "higher_is_better",
                            "Natural log of SOX/SPY ratio. Non-stationary; use momentum/zscore transforms.",
                            "derived: log(sox/spy)"),
    "sox_realized_vol_21d_ann_pct": col(F, "vol_ann_pct", "SOX Realized Vol (21d, ann. %)",
                            "lower_is_better", "21-day annualized realized vol of SOX daily returns, percent.",
                            "derived: std(sox_ret,21)*sqrt(252)*100"),
    "days_since_release": col("int64", "count", "Days Since Release", "neutral",
                            "Constant 0: ^SOX is a continuously-quoted market index with NO publication lag (contrast macro pairs where this tracks monthly releases). Native-daily, no LVCF step function.",
                            None, 1),
}
def mom(per, freq):
    return col(F, "percent", f"SOX {per} Momentum (%)", "higher_is_better",
               f"{per} percent-change of ^SOX. Positive = semis rising.",
               f"derived: (sox[t]/sox[t-{freq}]-1)*100")
def rmom(per, freq):
    return col(F, "percent", f"SOX/SPY {per} Rel-Strength Mom (%)", "higher_is_better",
               f"{per} percent-change of SOX/SPY ratio. Positive = semis gaining on SPY.",
               f"derived: (ratio[t]/ratio[t-{freq}]-1)*100")
def rz(win):
    return col(F, "ratio", f"SOX/SPY Z-Score ({win})", "higher_is_better",
              f"Standardized SOX/SPY ratio vs trailing {win} mean/std. High = semis stretched-strong vs SPY.",
              f"derived: (ratio - rollmean_{win}) / rollstd_{win}")
def fwd(w, unit_label):
    return col(F, "decimal_return", f"SPY {w} Forward Return", "higher_is_better",
               f"Forward {w} total return of SPY (decimal). Prediction target.",
               f"derived: spy[t+{w}]/spy[t]-1")

DEFS.update({
    "sox_mom_1m_pct": mom("1m", 21), "sox_mom_3m_pct": mom("3m", 63),
    "sox_mom_6m_pct": mom("6m", 126), "sox_mom_12m_pct": mom("12m", 252),
    "sox_spy_ratio_mom_1m_pct": rmom("1m", 21), "sox_spy_ratio_mom_3m_pct": rmom("3m", 63),
    "sox_spy_ratio_mom_6m_pct": rmom("6m", 126), "sox_spy_ratio_mom_12m_pct": rmom("12m", 252),
    "sox_spy_ratio_zscore_126d": rz("126d"), "sox_spy_ratio_zscore_252d": rz("252d"),
    "sox_spy_ratio_zscore_12m": rz("12m"),
    "spy_fwd_1d": fwd("1d", "d"), "spy_fwd_5d": fwd("5d", "d"), "spy_fwd_21d": fwd("21d", "d"),
    "spy_fwd_63d": fwd("63d", "d"), "spy_fwd_126d": fwd("126d", "d"), "spy_fwd_252d": fwd("252d", "d"),
    "spy_fwd_1m": fwd("1m", "m"), "spy_fwd_3m": fwd("3m", "m"),
    "spy_fwd_6m": fwd("6m", "m"), "spy_fwd_12m": fwd("12m", "m"),
})

# Existing registry is the cross-pair single source of truth for display names.
# Load it first and reconcile DEFS display_name to any pre-existing row (DATA-D13 verbatim match).
_reg_existing = {}
with open("data/display_name_registry.csv") as _f:
    for _r in csv.DictReader(_f):
        _reg_existing[_r["column_name"]] = _r["display_name"]
for _name, _meta in DEFS.items():
    if _name in _reg_existing:
        _meta["display_name"] = _reg_existing[_name]

def build_sidecar(df, parquet_path):
    cols = {"date": col("datetime64[ns]", "date", "Date", "neutral",
                         "Daily trading-date index (parquet index column)." )}
    cols["date"].pop("refresh_ttl_days", None)
    cols["date"].pop("source_reference", None)
    for c in df.columns:
        assert c in DEFS, f"missing def for {c}"
        cols[c] = DEFS[c]
    return {"pair_id": PAIR_ID, "parquet_path": parquet_path,
            "schema_version": "1.0.0", "generated_at": GEN_AT, "columns": cols}

with open(f"data/{PAIR_ID}_daily_schema.json", "w") as f:
    json.dump(build_sidecar(daily, f"data/{dly}"), f, indent=2)
with open(f"data/{PAIR_ID}_monthly_schema.json", "w") as f:
    json.dump(build_sidecar(monthly, f"data/{mly}"), f, indent=2)
print("Sidecars written.")

# ---- interpretation_metadata.json (Dana-owned fields) -------------------
im = {
    "pair_id": PAIR_ID,
    "schema_version": "1.1.0",
    "indicator": "phlxsox",
    "target": "spy",
    "indicator_nature": "leading",
    "indicator_type": "price",
    "strategy_objective": "procyclical_capture",  # Ray finalizes post-tournament
    "expected_direction": "procyclical",           # Ray-owned hypothesis
    "data_provenance": {
        "source": "Yahoo Finance (PHLX Semiconductor Index, live daily)",
        "series_id": "^SOX",
        "accessed_at": GEN_AT,
    },
    "known_stress_episodes": [
        {"label": "Dot-com semiconductor bust", "start": "2000-03-01", "end": "2002-10-31",
         "note": "SOX led the broad market lower; semis are high-beta and turned first."},
        {"label": "COVID crash + recovery", "start": "2020-02-19", "end": "2020-12-31",
         "note": "SOX recovered faster than SPY; relative-strength inflected early."},
        {"label": "2022 rate-shock semiconductor drawdown", "start": "2022-01-01", "end": "2022-10-31",
         "note": "SOX fell ~35% intra-year, leading the SPY de-rating; rel-strength weakened ahead."},
    ],
    "related_pair_ids": ["phlxsox_xly", "phlxsox_xlf", "phlxsox_xlv", "phlxsox_xle"],
    "owner_writes": {
        "dana": ["pair_id", "schema_version", "indicator", "target",
                 "indicator_nature", "indicator_type", "data_provenance",
                 "known_stress_episodes", "related_pair_ids"],
        "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
        "ray": ["strategy_objective", "expected_direction", "mechanism",
                "caveats", "narrative_summary"],
    },
    "last_updated_by": "dana",
    "last_updated_at": GEN_AT,
}
with open(f"results/{PAIR_ID}/interpretation_metadata.json", "w") as f:
    json.dump(im, f, indent=2)
print("interpretation_metadata.json written.")

# ---- manifest update (additive) -----------------------------------------
with open("data/manifest.json") as f:
    man = json.load(f)
existing = {a.get("path") for a in man["artifacts"]}
src = "yahoo:^SOX + yahoo:SPY (native-daily intermarket pair; SOX/SPY relative strength)"
new_entries = [
    {"path": f"data/{dly}", "source": src, "refresh_ttl_days": 1,
     "schema_ref": f"data/{PAIR_ID}_daily_schema.json", "last_updated": "2026-06-19",
     "pairs": [PAIR_ID],
     "mixed_freq_ttl_note": "Two native-daily equity series; TTL=1 (daily market data)."},
    {"path": f"data/{PAIR_ID}_daily_latest.parquet", "source": f"alias_of:data/{dly}",
     "refresh_ttl_days": 1, "schema_ref": f"data/{PAIR_ID}_daily_schema.json",
     "last_updated": "2026-06-19", "pairs": [PAIR_ID], "source_master": f"data/{dly}"},
    {"path": f"data/{mly}", "source": src, "refresh_ttl_days": 30,
     "schema_ref": f"data/{PAIR_ID}_monthly_schema.json", "last_updated": "2026-06-19",
     "pairs": [PAIR_ID],
     "mixed_freq_ttl_note": "Month-end resampled lens; TTL=30 (monthly analysis cadence)."},
    {"path": f"data/{PAIR_ID}_monthly_latest.parquet", "source": f"alias_of:data/{mly}",
     "refresh_ttl_days": 30, "schema_ref": f"data/{PAIR_ID}_monthly_schema.json",
     "last_updated": "2026-06-19", "pairs": [PAIR_ID], "source_master": f"data/{mly}"},
]
for e in new_entries:
    if e["path"] not in existing:
        man["artifacts"].append(e)
man["generated_at"] = GEN_AT
with open("data/manifest.json", "w") as f:
    json.dump(man, f, indent=2)
print("manifest.json updated.")

# ---- display_name_registry.csv (additive) -------------------------------
unit_axis = {"index": "Index Level", "price": "$", "decimal_return": "Return",
             "ratio": "Ratio", "percent": "%", "vol_ann_pct": "Ann. Vol (%)",
             "count": "Count", "date": "Date"}
with open("data/display_name_registry.csv") as f:
    rows = list(csv.reader(f))
have = {r[0] for r in rows[1:]}
all_defs = dict(DEFS)
for name, meta in all_defs.items():
    if name not in have:
        u = meta["unit"]
        rows.append([name, meta["display_name"], u, f'{meta["display_name"]}'])
        have.add(name)
with open("data/display_name_registry.csv", "w", newline="") as f:
    csv.writer(f).writerows(rows)
print("display_name_registry.csv updated.")
