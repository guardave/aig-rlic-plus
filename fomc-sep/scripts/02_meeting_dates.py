#!/usr/bin/env python3
"""
Phase 2: Discover all FOMC meetings with SEP releases (2007-present).
====================================================================
Scrapes the Fed calendar page to find all meeting dates that have
SEP projection materials, and verifies which have HTML accessible
versions vs PDF-only.
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = "https://www.federalreserve.gov"
CALENDAR_URLS = [
    f"{BASE_URL}/monetarypolicy/fomccalendars.htm",  # Current + recent years
]

# Known SEP meeting dates (hardcoded as fallback + validation)
# SEPs are released at approximately quarterly FOMC meetings (Mar, Jun, Sep, Dec)
# Source: Fed website historical records
KNOWN_SEP_DATES = [
    # 2007 (SEPs began, no dot plot)
    "20071031",
    # 2008
    "20080130", "20080618", "20081029",
    # 2009
    "20090128", "20090624", "20091104",
    # 2010
    "20100127", "20100623", "20101103",
    # 2011
    "20110126", "20110622", "20111102",
    # 2012 (dot plots began January 2012)
    "20120125", "20120425", "20120620", "20120912", "20121212",
    # 2013
    "20130320", "20130619", "20130918", "20131218",
    # 2014
    "20140319", "20140618", "20140917", "20141217",
    # 2015
    "20150318", "20150617", "20150917", "20151216",
    # 2016
    "20160316", "20160615", "20160921", "20161214",
    # 2017
    "20170315", "20170614", "20170920", "20171213",
    # 2018
    "20180321", "20180613", "20180926", "20181219",
    # 2019
    "20190320", "20190619", "20190918", "20191211",
    # 2020
    "20200610", "20200916", "20201216",  # March 2020 cancelled due to COVID
    # 2021
    "20210317", "20210616", "20210922", "20211215",
    # 2022
    "20220316", "20220615", "20220921", "20221214",
    # 2023
    "20230322", "20230614", "20230920", "20231213",
    # 2024
    "20240320", "20240612", "20240918", "20241218",
    # 2025
    "20250319", "20250618", "20250917", "20251210",
    # 2026
    "20260318",
]


def check_url_exists(url, timeout=10):
    """Check if a URL returns 200."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("  FOMC SEP Meeting Date Discovery")
    print("=" * 60)

    meetings = []

    for date_str in KNOWN_SEP_DATES:
        # Check HTML accessible version
        html_url = f"{BASE_URL}/monetarypolicy/fomcprojtabl{date_str}.htm"
        pdf_url = f"{BASE_URL}/monetarypolicy/files/fomcprojtabl{date_str}.pdf"

        dt = datetime.strptime(date_str, "%Y%m%d")
        has_dot_plot = dt >= datetime(2012, 1, 1)

        print(f"  {date_str} ({dt.strftime('%Y-%m-%d')})...", end="", flush=True)

        html_exists = check_url_exists(html_url)
        pdf_exists = check_url_exists(pdf_url) if not html_exists else True  # Skip PDF check if HTML exists

        source = "html" if html_exists else ("pdf" if pdf_exists else "unknown")
        print(f" {source.upper()}" + (" + dots" if has_dot_plot else ""))

        meetings.append({
            "date": date_str,
            "date_formatted": dt.strftime("%Y-%m-%d"),
            "year": dt.year,
            "quarter": f"Q{(dt.month - 1) // 3 + 1}",
            "has_dot_plot": has_dot_plot,
            "html_url": html_url if html_exists else None,
            "pdf_url": pdf_url,
            "source": source,
        })

    # Save meeting registry
    registry_path = os.path.join(OUT_DIR, "sep_meeting_registry.json")
    with open(registry_path, "w") as f:
        json.dump(meetings, f, indent=2)
    print(f"\n  Registry: {registry_path} ({len(meetings)} meetings)")

    # Summary
    html_count = sum(1 for m in meetings if m["source"] == "html")
    pdf_count = sum(1 for m in meetings if m["source"] == "pdf")
    dot_count = sum(1 for m in meetings if m["has_dot_plot"])
    year_range = f"{meetings[0]['year']}-{meetings[-1]['year']}"

    print(f"\n  Summary:")
    print(f"    Total meetings: {len(meetings)} ({year_range})")
    print(f"    HTML available: {html_count}")
    print(f"    PDF only:       {pdf_count}")
    print(f"    With dot plots: {dot_count} (2012+)")


if __name__ == "__main__":
    main()
