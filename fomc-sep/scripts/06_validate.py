#!/usr/bin/env python3
"""
Phase 6: Independent validation of extracted SEP data.
======================================================
Uses SEPARATE logic from the scraper to verify data quality:
1. Parse Table 1 medians directly from PDF text (independent of HTML scraper)
2. Cross-check dot plot participant totals for consistency
3. Compare FRED API data against HTML-scraped projections
4. Sample-check specific known values from published documents

This script intentionally uses different parsing logic than 03_scrape_html_tables.py
to avoid correlated errors.
"""

import os
import re
import json
import pdfplumber
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")
REF = os.path.join(DATA, "references")

PASS = 0
FAIL = 0
WARN = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}  {detail}")


def warn(label, detail=""):
    global WARN
    WARN += 1
    print(f"  WARN  {label}  {detail}")


# =====================================================================
# CHECK 1: Data file existence and basic integrity
# =====================================================================
def check_files():
    print("\n=== CHECK 1: File Existence & Integrity ===")

    # Meeting registry
    reg_path = os.path.join(DATA, "sep_meeting_registry.json")
    check("Meeting registry exists", os.path.exists(reg_path))
    with open(reg_path) as f:
        meetings = json.load(f)
    check("Registry has 70 meetings", len(meetings) == 70, f"got {len(meetings)}")
    check("All meetings have era field", all("era" in m for m in meetings))

    # PDFs
    pdfs = [f for f in os.listdir(REF) if f.endswith(".pdf")]
    check("70 reference PDFs", len(pdfs) == 70, f"got {len(pdfs)}")

    # Dot plot data
    dots_path = os.path.join(DATA, "sep_dot_plot.csv")
    check("Dot plot CSV exists", os.path.exists(dots_path))
    dots = pd.read_csv(dots_path)
    check("Dot plot has >1000 entries", len(dots) > 1000, f"got {len(dots)}")

    # FRED data
    fred_path = os.path.join(DATA, "fred", "sep_all_fred.parquet")
    check("FRED combined parquet exists", os.path.exists(fred_path))

    return meetings, dots


# =====================================================================
# CHECK 2: Dot plot consistency checks
# =====================================================================
def check_dot_consistency(dots):
    print("\n=== CHECK 2: Dot Plot Consistency ===")

    # Each meeting should have 4 horizons (current_year, year_plus1, year_plus2, longer_run)
    for meeting in dots["meeting_date"].unique():
        m_dots = dots[dots["meeting_date"] == meeting]
        horizons = set(m_dots["horizon"].unique())
        # Allow col_4 as alias for longer_run
        effective_horizons = {h.replace("col_4", "longer_run") for h in horizons}
        expected = {"current_year", "year_plus1", "year_plus2", "longer_run"}
        # Not all early meetings have all 4 horizons
        if len(effective_horizons) < 3:
            warn(f"Meeting {meeting}: only {len(effective_horizons)} horizons", str(effective_horizons))

    # Participant counts should be reasonable (15-19 for most meetings)
    for meeting in dots["meeting_date"].unique():
        m_dots = dots[dots["meeting_date"] == meeting]
        for horizon in m_dots["horizon"].unique():
            h_dots = m_dots[m_dots["horizon"] == horizon]
            total_participants = h_dots["num_participants"].sum()
            if total_participants < 10 or total_participants > 20:
                warn(f"Meeting {meeting}/{horizon}: {total_participants} participants",
                     "(expected 15-19)")

    # Rates should be in reasonable range (0-7%)
    check("All rates >= 0", (dots["rate"] >= 0).all(), f"min={dots['rate'].min()}")
    check("All rates <= 7", (dots["rate"] <= 7).all(), f"max={dots['rate'].max()}")
    check("All participant counts > 0", (dots["num_participants"] > 0).all())

    # Check a few known values manually
    # March 2026: median fed funds should be ~3.375% (from public reports)
    m2026 = dots[dots["meeting_date"] == "20260318"]
    if len(m2026) > 0:
        cy = m2026[m2026["horizon"] == "current_year"]
        all_rates = []
        for _, r in cy.iterrows():
            all_rates.extend([r["rate"]] * int(r["num_participants"]))
        if all_rates:
            median_rate = np.median(all_rates)
            check(f"Mar 2026 current-year median ~3.375%",
                  abs(median_rate - 3.375) < 0.15,
                  f"got {median_rate:.3f}")


# =====================================================================
# CHECK 3: PDF Table 1 independent extraction and comparison
# =====================================================================
def extract_medians_from_pdf(pdf_path):
    """INDEPENDENT extractor: parse median values from PDF text.

    This uses completely different logic from the HTML scraper.
    It looks for the Table 1 pattern with median values.
    """
    medians = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Table 1 is usually on page 1 (Era B) or page 2 (Era C)
            for page_num in range(min(3, len(pdf.pages))):
                text = pdf.pages[page_num].extract_text() or ""
                if "Median" not in text:
                    continue

                # Skip pages with "error ranges" or "projection error" — that's Table 2
                if "error range" in text.lower() or "projection error" in text.lower():
                    continue

                lines = text.split("\n")
                # Find lines with decimal numbers that could be medians
                # Pattern: look for rows of numbers like "2.1 1.9 1.8 1.9"
                for i, line in enumerate(lines):
                    # Skip lines that are part of error ranges (contain ±)
                    if "±" in line or "error" in line.lower():
                        continue
                    # Match lines of space-separated decimals
                    nums = re.findall(r'-?\d+\.\d+', line)
                    if len(nums) >= 3:
                        # Skip if values look like error ranges (all < 2.0)
                        if all(abs(float(n)) < 1.5 for n in nums[:4]):
                            continue
                        # Try to identify which variable this is from context
                        context = " ".join(lines[max(0,i-5):i+1]).lower()
                        if "gdp" in context and "gdp_growth" not in medians:
                            medians["gdp_growth"] = [float(n) for n in nums[:4]]
                        elif "unemployment" in context and "unemployment" not in medians:
                            medians["unemployment"] = [float(n) for n in nums[:4]]
                        elif "core" in context and "pce" in context and "core_pce" not in medians:
                            medians["core_pce"] = [float(n) for n in nums[:4]]
                        elif "pce" in context and "core" not in context and "pce_inflation" not in medians:
                            medians["pce_inflation"] = [float(n) for n in nums[:4]]

                if medians:
                    break
    except Exception as e:
        print(f"    PDF parse error: {e}")

    return medians


def check_pdf_vs_scraped():
    print("\n=== CHECK 3: PDF vs HTML-Scraped (Independent Verification) ===")

    # Load HTML-scraped Table 1 data
    t1_path = os.path.join(DATA, "sep_table1_raw.parquet")
    if not os.path.exists(t1_path):
        warn("No Table 1 scraped data to compare")
        return

    t1 = pd.read_parquet(t1_path)

    # Sample meetings for verification (one per year from different eras)
    verify_meetings = [
        "20150917",  # Era B, 2015
        "20170920",  # Era B, 2017
        "20190918",  # Era B, 2019
        "20220921",  # Era C, 2022
        "20240918",  # Era C, 2024
        "20260318",  # Era C, 2026 (latest)
    ]

    for meeting_date in verify_meetings:
        pdf_path = os.path.join(REF, f"fomcprojtabl{meeting_date}.pdf")
        if not os.path.exists(pdf_path):
            warn(f"PDF not found for {meeting_date}")
            continue

        pdf_medians = extract_medians_from_pdf(pdf_path)
        if not pdf_medians:
            warn(f"Could not extract medians from PDF {meeting_date}")
            continue

        # Compare against scraped data
        scraped = t1[t1["meeting_date"] == meeting_date]
        if len(scraped) == 0:
            warn(f"No scraped data for {meeting_date}")
            continue

        for var, pdf_vals in pdf_medians.items():
            s_rows = scraped[scraped["variable"] == var]
            if len(s_rows) == 0:
                continue
            # The scraped data has 'values' column with extracted numbers
            for _, row in s_rows.iterrows():
                scraped_vals = row.get("values", [])
                if len(scraped_vals) > 0 and len(pdf_vals) > 0:
                    # Check if first value matches
                    if abs(scraped_vals[0] - pdf_vals[0]) < 0.2:
                        check(f"{meeting_date} {var} first value matches",
                              True, f"PDF={pdf_vals[0]}, scraped={scraped_vals[0]}")
                    else:
                        check(f"{meeting_date} {var} first value matches",
                              False, f"PDF={pdf_vals[0]}, scraped={scraped_vals[0]}")


# =====================================================================
# CHECK 4: FRED cross-validation
# =====================================================================
def check_fred_consistency():
    print("\n=== CHECK 4: FRED Data Consistency ===")

    fred_path = os.path.join(DATA, "fred", "sep_all_fred.parquet")
    if not os.path.exists(fred_path):
        warn("FRED data not available")
        return

    fred = pd.read_parquet(fred_path)

    # Basic sanity
    check("FRED has 5 variables",
          set(fred["variable"].unique()) == {"gdp_growth", "unemployment", "pce_inflation", "core_pce", "fed_funds"})

    # Value ranges
    for var in fred["variable"].unique():
        v_data = fred[fred["variable"] == var]
        vals = v_data["value"]
        if var == "fed_funds":
            check(f"FRED {var} values in [0, 7]", vals.min() >= 0 and vals.max() <= 7,
                  f"range [{vals.min():.2f}, {vals.max():.2f}]")
        elif var == "gdp_growth":
            check(f"FRED {var} values in [-5, 10]", vals.min() >= -5 and vals.max() <= 10,
                  f"range [{vals.min():.2f}, {vals.max():.2f}]")
        elif var == "unemployment":
            check(f"FRED {var} values in [2, 15]", vals.min() >= 2 and vals.max() <= 15,
                  f"range [{vals.min():.2f}, {vals.max():.2f}]")

    # Check that longer-run fed funds median is in known range (2.5-3.5% historically)
    lr_ff = fred[(fred["variable"] == "fed_funds") & (fred["statistic"] == "median_lr")]
    if len(lr_ff) > 0:
        check("Longer-run fed funds median in [2.0, 5.0]",
              lr_ff["value"].min() >= 2.0 and lr_ff["value"].max() <= 5.0,
              f"range [{lr_ff['value'].min():.2f}, {lr_ff['value'].max():.2f}]")


# =====================================================================
# CHECK 5: Known spot-check values from published documents
# =====================================================================
def check_known_values(dots):
    print("\n=== CHECK 5: Known Value Spot-Checks ===")

    # These are manually verified values from published SEP documents:

    # Dec 2015 (first rate hike): median should be ~1.375% for year+1
    m = dots[(dots["meeting_date"] == "20151216") & (dots["horizon"] == "year_plus1")]
    if len(m) > 0:
        rates = []
        for _, r in m.iterrows():
            rates.extend([r["rate"]] * int(r["num_participants"]))
        if rates:
            median = np.median(rates)
            check(f"Dec 2015 year+1 median fed funds ~1.375%",
                  abs(median - 1.375) < 0.25, f"got {median:.3f}")

    # June 2022 (aggressive hikes): median should be ~3.375% for year-end
    m = dots[(dots["meeting_date"] == "20220615") & (dots["horizon"] == "current_year")]
    if len(m) > 0:
        rates = []
        for _, r in m.iterrows():
            rates.extend([r["rate"]] * int(r["num_participants"]))
        if rates:
            median = np.median(rates)
            check(f"Jun 2022 current-year median fed funds ~3.375%",
                  abs(median - 3.375) < 0.5, f"got {median:.3f}")

    # Dec 2023: longer-run median should be ~2.5%
    m = dots[(dots["meeting_date"] == "20231213") & (dots["horizon"] == "longer_run")]
    if len(m) > 0:
        rates = []
        for _, r in m.iterrows():
            rates.extend([r["rate"]] * int(r["num_participants"]))
        if rates:
            median = np.median(rates)
            check(f"Dec 2023 longer-run median fed funds ~2.5%",
                  abs(median - 2.5) < 0.25, f"got {median:.3f}")

    # Check total dot count per meeting is reasonable
    meeting_counts = dots.groupby("meeting_date")["num_participants"].sum()
    # Each meeting should have roughly 15-19 participants × 4 horizons = 60-76 total dots
    reasonable = ((meeting_counts >= 40) & (meeting_counts <= 100)).mean()
    check(f">{reasonable*100:.0f}% of meetings have reasonable dot totals (40-100)",
          reasonable > 0.7, f"{reasonable*100:.0f}% pass")


# =====================================================================
# MAIN
# =====================================================================
def main():
    global PASS, FAIL, WARN

    print("=" * 60)
    print("  FOMC SEP Data Validation")
    print("  (Independent logic — NOT reusing scraper code)")
    print("=" * 60)

    meetings, dots = check_files()
    check_dot_consistency(dots)
    check_pdf_vs_scraped()
    check_fred_consistency()
    check_known_values(dots)

    print(f"\n{'=' * 60}")
    print(f"  RESULTS: {PASS} PASS, {FAIL} FAIL, {WARN} WARN")
    print(f"{'=' * 60}")

    if FAIL > 0:
        print(f"\n  *** {FAIL} FAILURES require investigation ***")
    else:
        print(f"\n  All checks passed.")


if __name__ == "__main__":
    main()
