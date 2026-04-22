"""Canonical cloud verification script for AIG-RLIC+ Streamlit Cloud deployment.

Promoted from `temp/260422_wave10g_full/focused_verify.py` (Wave 10G) with:
- Pattern 22 fix: chart detection via `page.query_selector_all(".js-plotly-plot")`
  on the resolved frame DOM, NOT `inner_text.count("js-plotly-plot")` (CSS
  class names never appear in extracted text; prior heuristic falsely returned
  0).
- Full GATE-28 pair x page grid: all focus pairs, 4 pages each, plus landing.
- Wave 10H.1 APP-PT2 check: Sample pair (hy_ig_v2_spy) Methodology page must
  contain an "Exploratory Insights" section with the three orphan charts'
  ELI5 markers in DOM text. Other pairs' Methodology pages must NOT render
  the section (regression gate — backward compatibility).

Usage
-----
    python3 scripts/cloud_verify.py                      # default base URL
    python3 scripts/cloud_verify.py --base <url>         # override
    python3 scripts/cloud_verify.py --out <dir>          # override output dir

Outputs
-------
Scratch (gitignored, under ``temp/<ts>_cloud_verify/``):
    results.json         – structured verdicts per (pair, page)
    summary.txt          – human-readable summary
    dom_text/*.txt       – extracted DOM per slug
    screenshots/*.png    – viewport screenshots per slug
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright  # type: ignore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BASE = "https://aig-rlic-plus.streamlit.app"
FOCUS_PAIRS = ["hy_ig_v2_spy", "hy_ig_spy", "indpro_xlp", "umcsent_xlv"]
PAGES = ["story", "evidence", "strategy", "methodology"]

HYDRATE_SECS = 25
IFRAME_WAIT_SECS = 10

ERR_PATS = [
    "Traceback", "StreamlitPageNotFoundError", "StreamlitAPIException",
    "AttributeError", "FileNotFoundError", "ValueError", "TypeError",
    "NameError", "KeyError", "Error loading page", "Something went wrong",
    "ModuleNotFoundError",
]
BREADCRUMB = ["Story", "Evidence", "Strategy", "Methodology"]
PREFIX_PENDING_RE = re.compile(
    r"(hy_ig_spy_|hy_ig_v2_spy_|indpro_xlp_|umcsent_xlv_|indpro_spy_|permit_spy_|vix_vix3m_spy_)\w+\.json"
)

# Wave 10H.1 APP-PT2 markers — first ~60 chars of each ELI5 note (Vera's
# narrative_alignment_note strings from results/hy_ig_v2_spy/analyst_suggestions.json).
# We look for any three unique markers to confirm all three orphans rendered.
EXPLORATORY_SECTION_MARKER = "Exploratory Insights"
EXPLORATORY_ELI5_MARKERS = [
    "how nervous bond investors are about risky companies",  # hero_spread_vs_spy
    "real historical events labelled directly on the chart",  # spread_history_annotated
    "tested nearly 2,000 different trading rules",  # tournament_sharpe_dist
]

SAMPLE_PAIR = "hy_ig_v2_spy"


# ---------------------------------------------------------------------------
# DOM extraction
# ---------------------------------------------------------------------------

def get_dom(page, url, slug, dom_dir, ss_dir):
    """Return (text, source_tag, plotly_count) or (None, err, 0)."""
    print(f"  navigating {url} ...", flush=True)
    try:
        page.goto(url, timeout=45000, wait_until="domcontentloaded")
    except Exception as e:
        return None, f"goto: {e}", 0
    time.sleep(HYDRATE_SECS)

    target = None
    t0 = time.time()
    while time.time() - t0 < IFRAME_WAIT_SECS:
        for f in page.frames:
            if "/~/+/" in f.url:
                target = f
                break
        if target:
            break
        time.sleep(1)

    if target is None:
        # Fallback: landing page has no /~/+/ iframe — outer body.
        try:
            text = page.inner_text("body")
            if len(text) > 200:
                with open(os.path.join(dom_dir, f"{slug}.txt"), "w") as fh:
                    fh.write(text)
                try:
                    page.screenshot(path=os.path.join(ss_dir, f"{slug}.png"), full_page=False)
                except Exception:
                    pass
                try:
                    pc = len(page.query_selector_all(".js-plotly-plot"))
                except Exception:
                    pc = 0
                return text, "outer_body", pc
        except Exception:
            pass
        return None, "no_iframe", 0

    # Wait for iframe DOM to hydrate (Streamlit lazy-renders into /~/+/).
    t0 = time.time()
    text = ""
    while time.time() - t0 < 30:
        try:
            text = target.inner_text("body")
            if len(text) > 200:
                break
        except Exception:
            pass
        time.sleep(2)
    if len(text) < 200:
        try:
            text = target.inner_text("body")
        except Exception as e:
            return None, f"inner_text: {e}", 0

    # Pattern 22 fix: query DOM tree for plotly containers (CSS class names
    # are NOT present in inner_text).
    try:
        plotly_count = len(target.query_selector_all(".js-plotly-plot"))
    except Exception:
        plotly_count = 0

    with open(os.path.join(dom_dir, f"{slug}.txt"), "w") as fh:
        fh.write(text)
    try:
        page.screenshot(path=os.path.join(ss_dir, f"{slug}.png"), full_page=False)
    except Exception:
        pass
    return text, "iframe", plotly_count


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_page(text, slug, pair_id, page_name, plotly_count):
    is_methodology = (page_name == "methodology")
    errs = [p for p in ERR_PATS if p in text]
    breadcrumb_missing = [b for b in BREADCRUMB if b not in text]
    prefix_pending = bool(PREFIX_PENDING_RE.search(text))
    chart_pending = "chart pending" in text.lower()
    dom_ok = len(text) > 200
    # Non-methodology pages must have >=1 plotly container.
    chart_ok = is_methodology or plotly_count >= 1

    # Wave 10H.1 APP-PT2 check (Methodology only).
    exploratory_section = EXPLORATORY_SECTION_MARKER in text
    exploratory_markers_hit = sum(1 for m in EXPLORATORY_ELI5_MARKERS if m in text)

    if is_methodology:
        if pair_id == SAMPLE_PAIR:
            app_pt2_ok = exploratory_section and exploratory_markers_hit == 3
            app_pt2_note = (
                f"Sample Methodology: section={exploratory_section} "
                f"eli5_markers={exploratory_markers_hit}/3"
            )
        else:
            # Regression gate — non-Sample pairs must NOT render the section.
            app_pt2_ok = not exploratory_section
            app_pt2_note = (
                f"Non-Sample Methodology: section={exploratory_section} "
                f"(expected False)"
            )
    else:
        app_pt2_ok = True
        app_pt2_note = "N/A (non-methodology)"

    verdict = "PASS" if (
        not errs and not breadcrumb_missing and not prefix_pending
        and not chart_pending and dom_ok and chart_ok and app_pt2_ok
    ) else "FAIL"

    return {
        "slug": slug,
        "pair_id": pair_id,
        "page": page_name,
        "dom_len": len(text),
        "errors": errs,
        "breadcrumb_missing": breadcrumb_missing,
        "prefix_pending": prefix_pending,
        "chart_pending_text": chart_pending,
        "chart_count": plotly_count,
        "dom_ok": dom_ok,
        "chart_ok": chart_ok,
        "app_pt2_ok": app_pt2_ok,
        "app_pt2_note": app_pt2_note,
        "exploratory_section_present": exploratory_section,
        "exploratory_eli5_markers_hit": exploratory_markers_hit,
        "verdict": verdict,
    }


def check_landing(text):
    sample_badge = "SAMPLE" in text.upper()
    raw_col_leak = bool(re.search(r"hy_ig_spread_pct|hy_ig_spread_bps|spy_fwd_\d+d", text))
    dom_ok = len(text) > 200
    verdict = "PASS" if (sample_badge and not raw_col_leak and dom_ok) else "FAIL"
    return {
        "slug": "landing",
        "dom_len": len(text),
        "sample_badge": sample_badge,
        "raw_col_leak": raw_col_leak,
        "dom_ok": dom_ok,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--out", default=None, help="Output dir (default: temp/<ts>_cloud_verify)")
    ap.add_argument("--pairs", default=",".join(FOCUS_PAIRS),
                    help="Comma-separated pair_ids to verify")
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out or f"/workspaces/aig-rlic-plus/temp/{ts}_cloud_verify"
    dom_dir = os.path.join(out_dir, "dom_text")
    ss_dir = os.path.join(out_dir, "screenshots")
    os.makedirs(dom_dir, exist_ok=True)
    os.makedirs(ss_dir, exist_ok=True)

    pairs = [p.strip() for p in args.pairs.split(",") if p.strip()]
    results = []

    t_start = datetime.now(timezone.utc).isoformat()
    print(f"=== cloud_verify — {t_start} ===", flush=True)
    print(f"  base: {args.base}", flush=True)
    print(f"  pairs: {pairs}", flush=True)
    print(f"  out: {out_dir}", flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # Landing
        print(f"\n[landing] {args.base}/", flush=True)
        dom, src, _ = get_dom(page, f"{args.base}/", "landing", dom_dir, ss_dir)
        if dom:
            r = check_landing(dom)
            r["src"] = src
            print(f"  verdict={r['verdict']} sample_badge={r['sample_badge']} leak={r['raw_col_leak']}", flush=True)
            results.append(r)
        else:
            results.append({"slug": "landing", "verdict": "FAIL", "error": src})

        # Pairs x pages
        for pair_id in pairs:
            for pg in PAGES:
                slug = f"{pair_id}_{pg}"
                url = f"{args.base}/{slug}"
                print(f"\n[{slug}] {url}", flush=True)
                dom, src, pc = get_dom(page, url, slug, dom_dir, ss_dir)
                if dom is None:
                    results.append({
                        "slug": slug, "pair_id": pair_id, "page": pg,
                        "verdict": "FAIL", "error": src,
                    })
                    print(f"  FAIL: {src}", flush=True)
                    continue
                r = check_page(dom, slug, pair_id, pg, pc)
                r["src"] = src
                print(
                    f"  verdict={r['verdict']} dom_len={r['dom_len']} "
                    f"charts={r['chart_count']} errs={r['errors']} "
                    f"prefix={r['prefix_pending']} bcmiss={r['breadcrumb_missing']} "
                    f"app_pt2={r['app_pt2_ok']} ({r['app_pt2_note']})",
                    flush=True,
                )
                results.append(r)

        browser.close()

    # Write outputs.
    t_end = datetime.now(timezone.utc).isoformat()
    summary = {
        "timestamp_start": t_start,
        "timestamp_end": t_end,
        "base": args.base,
        "pairs": pairs,
        "pass": sum(1 for r in results if r.get("verdict") == "PASS"),
        "fail": sum(1 for r in results if r.get("verdict") == "FAIL"),
        "total": len(results),
        "results": results,
    }
    with open(os.path.join(out_dir, "results.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    with open(os.path.join(out_dir, "summary.txt"), "w") as fh:
        fh.write(f"cloud_verify {t_start}\n")
        fh.write(f"PASS {summary['pass']}  FAIL {summary['fail']}  TOTAL {summary['total']}\n\n")
        for r in results:
            fh.write(f"  {r.get('verdict','?'):4}  {r.get('slug'):40}  "
                     f"charts={r.get('chart_count','-')}  "
                     f"app_pt2={r.get('app_pt2_ok','-')}\n")

    print(f"\n=== SUMMARY: {summary['pass']} PASS / {summary['fail']} FAIL / {summary['total']} TOTAL ===", flush=True)
    print(f"Results: {out_dir}/results.json", flush=True)
    return 0 if summary["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
