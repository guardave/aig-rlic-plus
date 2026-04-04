#!/usr/bin/env python3
"""
Phase 3: Scrape FOMC SEP HTML accessible pages.
================================================
Extracts Table 1 (economic projections) and dot plot data
from all available HTML accessible pages (2012-present).

Handles format variations across years.
"""

import os
import json
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "sep_tables_raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (research; FOMC SEP extraction)"}


def load_meeting_registry():
    """Load the meeting registry from Phase 2."""
    path = os.path.join(DATA_DIR, "sep_meeting_registry.json")
    with open(path) as f:
        return json.load(f)


def fetch_html(url, retries=3):
    """Fetch HTML content with retries."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
            print(f"    HTTP {r.status_code}")
        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None


def parse_table1(soup, meeting_date):
    """Parse Table 1: Economic Projections (median, CT, range).

    Returns a list of dicts with columns:
    meeting_date, variable, horizon, median, ct_low, ct_high, range_low, range_high
    """
    rows = []

    # Find all tables
    tables = soup.find_all("table")

    # Table 1 is typically the first major table with projection data
    for table in tables:
        text = table.get_text()
        # Look for the projections table (has "Median" and "Central tendency")
        if "Median" not in text or "Central tendency" not in text:
            continue

        # Extract header row to find year columns
        header_cells = []
        thead = table.find("thead") or table.find("tr")
        if thead:
            for th in thead.find_all(["th", "td"]):
                header_cells.append(th.get_text(strip=True))

        # Parse data rows
        current_variable = None
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) < 2:
                continue

            # Detect variable name rows
            first = cells[0].lower()
            if "change in real gdp" in first or "real gdp" in first:
                current_variable = "gdp_growth"
            elif "unemployment" in first:
                current_variable = "unemployment"
            elif "core pce" in first or "core personal" in first:
                current_variable = "core_pce"
            elif "pce inflation" in first or "pce price" in first or ("pce" in first and "core" not in first):
                current_variable = "pce_inflation"
            elif "federal funds" in first or "fed funds" in first:
                current_variable = "fed_funds"

            if current_variable is None:
                continue

            # Try to extract numeric values
            # Look for patterns like year columns with decimal values
            nums = []
            for cell in cells[1:]:
                # Clean cell text
                cell = cell.replace("–", "-").replace("—", "-").strip()
                # Try to parse as number or range
                if re.match(r'^-?\d+\.?\d*$', cell):
                    nums.append(float(cell))
                elif re.match(r'^-?\d+\.?\d*\s*[-–]\s*-?\d+\.?\d*$', cell):
                    # Range like "1.5 - 2.0"
                    parts = re.split(r'\s*[-–]\s*', cell)
                    if len(parts) == 2:
                        try:
                            nums.extend([float(parts[0]), float(parts[1])])
                        except ValueError:
                            pass

            # If we found numeric data, record it
            if nums and current_variable:
                rows.append({
                    "meeting_date": meeting_date,
                    "variable": current_variable,
                    "raw_cells": cells,
                    "values": nums,
                })

    return rows


def parse_dot_plot(soup, meeting_date):
    """Parse dot plot data (individual participant projections for fed funds rate).

    Returns list of dicts: meeting_date, horizon, rate, num_participants
    """
    dots = []

    text = soup.get_text()

    # Look for the dot plot section
    # Common patterns: "Assessment of Appropriate Monetary Policy"
    # or tables/figures showing participant counts at rate levels

    # Strategy: find all numbers paired with rate levels
    # The dot plot is often presented as a histogram/table

    for table in soup.find_all("table"):
        ttext = table.get_text()
        if "percent" not in ttext.lower() and "midpoint" not in ttext.lower():
            continue

        # Check if this looks like a dot plot table
        # (has rate values like 2.500, 3.000 etc. and small integers)
        rate_pattern = re.compile(r'\d+\.\d{2,3}')
        rates_found = rate_pattern.findall(ttext)
        if len(rates_found) < 3:
            continue

        # Parse rows
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) < 2:
                continue

            # First cell might be the rate
            first = cells[0].replace("%", "").strip()
            rate_match = re.match(r'^(\d+\.\d{2,3})$', first)
            if rate_match:
                rate = float(rate_match.group(1))
                # Remaining cells are participant counts per horizon
                for i, count_str in enumerate(cells[1:]):
                    count_str = count_str.strip()
                    if count_str.isdigit() and int(count_str) > 0:
                        horizons = ["current_year", "year_plus1", "year_plus2", "longer_run"]
                        horizon = horizons[i] if i < len(horizons) else f"col_{i}"
                        dots.append({
                            "meeting_date": meeting_date,
                            "horizon": horizon,
                            "rate": rate,
                            "num_participants": int(count_str),
                        })

    return dots


def scrape_meeting(meeting):
    """Scrape a single meeting's SEP data."""
    date_str = meeting["date"]
    html_url = meeting.get("html_url")

    if not html_url:
        return None, None

    html = fetch_html(html_url)
    if not html:
        return None, None

    # Save raw HTML
    raw_path = os.path.join(RAW_DIR, f"{date_str}.html")
    with open(raw_path, "w") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")

    # Parse tables
    table1_rows = parse_table1(soup, date_str)
    dot_rows = parse_dot_plot(soup, date_str)

    return table1_rows, dot_rows


def main():
    print("=" * 60)
    print("  Phase 3: Scrape FOMC SEP HTML Tables")
    print("=" * 60)

    meetings = load_meeting_registry()
    html_meetings = [m for m in meetings if m.get("html_url")]

    print(f"  {len(html_meetings)} meetings with HTML pages\n")

    all_table1 = []
    all_dots = []

    for i, meeting in enumerate(html_meetings):
        date = meeting["date"]
        print(f"  [{i+1}/{len(html_meetings)}] {date}...", end="", flush=True)

        table1, dots = scrape_meeting(meeting)

        if table1:
            all_table1.extend(table1)
            print(f" T1:{len(table1)} rows", end="")
        if dots:
            all_dots.extend(dots)
            print(f" Dots:{len(dots)}", end="")
        print()

        # Rate limit
        time.sleep(0.5)

    # Save consolidated data
    if all_table1:
        t1_df = pd.DataFrame(all_table1)
        t1_path = os.path.join(DATA_DIR, "sep_table1_raw.parquet")
        t1_df.to_parquet(t1_path, engine="pyarrow", index=False)
        print(f"\n  Table 1: {len(t1_df)} rows -> {t1_path}")

    if all_dots:
        dots_df = pd.DataFrame(all_dots)
        dots_path = os.path.join(DATA_DIR, "sep_dot_plot.parquet")
        dots_df.to_parquet(dots_path, engine="pyarrow", index=False)
        print(f"  Dot plot: {len(dots_df)} entries -> {dots_path}")

    # Also save as CSV for easy inspection
    if all_dots:
        csv_path = os.path.join(DATA_DIR, "sep_dot_plot.csv")
        dots_df.to_csv(csv_path, index=False)
        print(f"  Dot plot CSV: {csv_path}")

    print(f"\n  Raw HTML pages saved to: {RAW_DIR}/")
    print(f"  Meetings scraped: {len(html_meetings)}")
    print(f"  Table 1 rows: {len(all_table1)}")
    print(f"  Dot plot entries: {len(all_dots)}")


if __name__ == "__main__":
    main()
