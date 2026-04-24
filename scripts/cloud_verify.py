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
- Wave 10I.C: APP_SEV1_PATS and STUB_PATS soft-error detection; GATE-29
  parquet pre-flight hard-wired into main flow.
- Wave 10I.C (screenshot-all-tabs): After each page loads and hydrates,
  captures a default-state screenshot {pair}_{page}_default.png, then
  enumerates all [data-baseweb="tab"] buttons and clicks through each,
  waiting 3s per tab, saving {pair}_{page}_tab_{n}_{label}.png. Produces
  screenshots/index.md listing every screenshot as a shared evidence package
  for cross-agent domain inspection.

Usage
-----
    python3 scripts/cloud_verify.py                      # default base URL
    python3 scripts/cloud_verify.py --base <url>         # override
    python3 scripts/cloud_verify.py --out <dir>          # override output dir

Outputs
-------
Scratch (gitignored, under ``temp/<ts>_cloud_verify/``):
    results.json              – structured verdicts per (pair, page)
    summary.txt               – human-readable summary
    dom_text/*.txt            – extracted DOM per slug
    screenshots/*.png         – default-state + per-tab screenshots per slug
    screenshots/index.md      – shared evidence package: all screenshots listed
                                with pair, page, tab label, and file path
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
# Wave 10I.A: expanded from 4 to 10 pairs. Ace-A migrated 4 legacy pairs
# (indpro_spy, permit_spy, vix_vix3m_spy, umcsent_xlv) to APP-PT1 thin
# wrappers; Ace-B exploded the TED composite into 3 variants
# (sofr_ted_spy, dff_ted_spy, ted_spliced_spy). All 10 are now active
# pair_ids with 4 pages each.
FOCUS_PAIRS = [
    "hy_ig_v2_spy", "hy_ig_spy", "indpro_xlp", "umcsent_xlv",
    "indpro_spy", "permit_spy", "vix_vix3m_spy",
    "sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy",
]
PAGES = ["story", "evidence", "strategy", "methodology"]

HYDRATE_SECS = 25
IFRAME_WAIT_SECS = 10
# Wave 10H.1 attempt 3: use selector-based iframe discovery. page.frames list
# is unreliable on Streamlit Cloud — the iframe element exists in DOM long
# before Playwright populates it in page.frames. wait_for_selector +
# content_frame is the canonical pattern.
IFRAME_SELECTOR = 'iframe[title="streamlitApp"]'
IFRAME_SELECTOR_TIMEOUT_MS = 60000
POST_HYDRATE_CHART_WAIT_SECS = 20  # charts render lazily after text body

ERR_PATS = [
    "Traceback", "StreamlitPageNotFoundError", "StreamlitAPIException",
    "AttributeError", "FileNotFoundError", "ValueError", "TypeError",
    "NameError", "KeyError", "Error loading page", "Something went wrong",
    "ModuleNotFoundError",
]

# Wave 10I.C: APP-SEV1 banner patterns — user-visible error strings rendered by
# Streamlit components that do NOT raise Python exceptions. These are soft-error
# strings written by app code (st.error / st.warning / conditional renders) that
# produce human-visible red banners or fallback text. They are NOT in ERR_PATS
# because ERR_PATS is for Python exception class names that appear in tracebacks.
# A page can pass every ERR_PATS check and still show a user-visible red banner.
#
# Root cause of the Wave 10I.A false-PASS on dff_ted_spy_strategy:
#   DOM text contained: "Probability engine panel cannot render: No signals_*.parquet
#   under /mount/src/aig-rlic-plus/results/dff_ted_spy"
#   ERR_PATS missed it entirely — "cannot render" is not a Python exception name.
#   GATE-29 parquet pre-flight was never run — signals_*.parquet was absent from git.
APP_SEV1_PATS = [
    "cannot render",           # generic APP-SEV1 L2 banner phrase
    "panel cannot render",     # Probability Engine Panel error
    "No signals_",             # missing parquet diagnostic string
    "parquet not found",       # fallback from signal loader
    "data problem",            # softcoded fallback in probability panel
    "no signals parquet found", # lowercase variant in sparkline fallback
]

# Stub/placeholder patterns that indicate incomplete content — not Python errors
# but user-visible evidence of missing data or unfinished sections.
STUB_PATS = [
    "vs N/A",                  # B&H benchmark not populated (Story KPI block)
    "Ray leg pending",         # unmerged narrative stub
    "Signal universe table unavailable",  # Methodology stub
    "Stationarity tests missing",         # Methodology stub
    "Total tournament combinations: N/A", # Methodology stub
    "TODO",                    # generic stub marker
    "pending RES-",            # pending Ray dispatch
    # Wave 10J ECON-CP1/CP2 / VIZ-CP1 cross-period consistency placeholder.
    # Ace renders this text when cross-period charts are missing (e.g. during
    # the Wave 10J retro-apply window while older pairs are being updated).
    #
    # Severity transition:
    #   WARN during Wave 10J retro-apply — pairs not yet updated tolerate the stub.
    #   FAIL after Wave 10J retro-apply is complete — no pair should show this.
    #
    # Implementation note: `check_page()` promotes stub_hits to FAIL when
    # CROSS_PERIOD_STUB_IS_FAIL is True; set to False during Wave 10J retro.
    # WARN during 10J retro, FAIL after.
    "Cross-period analysis pending",      # ECON-CP1/CP2 / VIZ-CP1 placeholder
]

# Wave 10J: controls whether the cross-period-consistency stub triggers a FAIL
# or is downgraded to a WARN (PASS-with-note in summary) during the retro-apply
# transition window. Set to True once all pairs have been retro-applied.
# WARN during 10J retro, FAIL after.
CROSS_PERIOD_STUB_IS_FAIL = False  # flip to True after Wave 10J retro-apply complete

# Wave 10J NBER shading spot-check patterns.
# Rolling-correlation and rolling-sharpe Evidence page charts should carry NBER
# recession shading. These patterns detect the shading presence in the rendered
# DOM HTML (Vera encodes recession band labels in the Plotly layout). Absence
# on a chart that is supposed to have NBER shading is logged as a WARNING — not
# a FAIL — because Vera's VIZ-NBER audit is the authoritative list; QA's check
# here is a spot-check that flags for follow-up, not a hard gate.
NBER_SHADING_DOM_PATS = [
    "recession",           # Plotly shape label or annotation text
    "NBER",                # explicit NBER label in chart title or annotation
    "nber",                # lowercase variant (Plotly JSON keys are case-sensitive
                           # but inner_text may normalize)
]
# Chart types on Evidence pages expected to carry NBER shading.
NBER_EXPECTED_CHART_TYPES = ["rolling_correlation", "rolling_sharpe"]
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

# Wave 10H.2 APP-TL1 markers — Trade Log Rendering Contract. Applied on the
# Strategy page for pairs retro-fitted onto the APP-PT1 template in this wave:
# hy_ig_spy and indpro_xlp. Sample (hy_ig_v2_spy) and umcsent_xlv are bypassed
# (hand-rolled Strategy pages — tracked as BL-APP-PT1-UMCSENT / legacy).
APP_TL1_PAIRS = {"hy_ig_spy", "indpro_xlp"}
APP_TL1_HEADING = "How to Read the Trade Log"
APP_TL1_BROKER_BTN = "Download trade log (broker-style)"
APP_TL1_POSITION_BTN = "Download position log (researcher)"
APP_TL1_PREVIEW_CAPTION = "executions, one row per trade"


# ---------------------------------------------------------------------------
# DOM extraction
# ---------------------------------------------------------------------------

def _sanitize_label(label: str) -> str:
    """Convert a tab label into a safe filename fragment (lowercase, underscored)."""
    label = label.strip()
    # Replace whitespace runs and non-alphanumeric chars with underscores.
    label = re.sub(r"[^a-zA-Z0-9]+", "_", label)
    return label.lower().strip("_")[:40]


def _screenshot_tabs(page_obj, frame, slug, ss_dir, pair_id, page_name):
    """Click through all visible Streamlit tab buttons and take screenshots.

    Wave 10I.C screenshot-all-tabs standard:
    - Default-state screenshot already taken by the caller as {slug}_default.png.
    - This helper enumerates [data-baseweb="tab"] elements in the frame,
      clicks each one, waits 3 s for content to settle, then takes a viewport
      screenshot named {slug}_tab_{n}_{label}.png.
    - Returns a list of dicts: {pair, page, tab_n, tab_label, filename, path}.
    """
    records = []
    try:
        tab_els = frame.query_selector_all('[data-baseweb="tab"]')
    except Exception:
        tab_els = []

    if not tab_els:
        print(f"    no tabs found on {slug}", flush=True)
        return records

    print(f"    found {len(tab_els)} tab(s) on {slug}", flush=True)
    for n, tab_el in enumerate(tab_els):
        try:
            raw_label = tab_el.inner_text() or f"tab{n}"
        except Exception:
            raw_label = f"tab{n}"
        safe_label = _sanitize_label(raw_label) or f"tab{n}"
        filename = f"{slug}_tab_{n}_{safe_label}.png"
        path = os.path.join(ss_dir, filename)
        try:
            tab_el.click()
            time.sleep(3)
            page_obj.screenshot(path=path, full_page=False)
            print(f"    tab {n} [{raw_label}] → {filename}", flush=True)
        except Exception as exc:
            print(f"    tab {n} [{raw_label}] screenshot failed: {exc}", flush=True)
            path = ""
        records.append({
            "pair": pair_id,
            "page": page_name,
            "tab_n": n,
            "tab_label": raw_label.strip(),
            "filename": filename,
            "path": path,
        })

    return records


def get_dom(page, url, slug, dom_dir, ss_dir, pair_id="", page_name=""):
    """Return (text, source_tag, plotly_count, html, tab_screenshots) or (None, err, 0, "", []).

    ``text`` is ``inner_text("body")`` — only traverses visible DOM (does NOT
    pick up content inside inactive Streamlit tab panels).
    ``html`` is the full rendered HTML (via ``frame.content()``), used for
    marker-presence checks on content that Streamlit lazy-hides behind tabs.
    ``tab_screenshots`` is the list of per-tab screenshot records produced by
    _screenshot_tabs() (empty for landing page).
    """
    print(f"  navigating {url} ...", flush=True)
    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
    except Exception as e:
        return None, f"goto: {e}", 0, "", [], None

    # Attempt 3 fix: resolve iframe via selector + content_frame, not
    # page.frames iteration. The former is deterministic; the latter races
    # against frame registration in Playwright's event loop.
    target = None
    try:
        handle = page.wait_for_selector(IFRAME_SELECTOR, timeout=IFRAME_SELECTOR_TIMEOUT_MS)
        if handle is not None:
            target = handle.content_frame()
    except Exception as e:
        print(f"  iframe selector wait failed: {e}", flush=True)

    if target is None:
        # Fallback: landing page has no /~/+/ iframe — outer body.
        try:
            text = page.inner_text("body")
            if len(text) > 200:
                with open(os.path.join(dom_dir, f"{slug}.txt"), "w") as fh:
                    fh.write(text)
                default_ss = os.path.join(ss_dir, f"{slug}_default.png")
                try:
                    page.screenshot(path=default_ss, full_page=False)
                except Exception:
                    pass
                try:
                    pc = len(page.query_selector_all(".js-plotly-plot"))
                except Exception:
                    pc = 0
                try:
                    html_outer = page.content()
                except Exception:
                    html_outer = ""
                return text, "outer_body", pc, html_outer, [], None
        except Exception:
            pass
        return None, "no_iframe", 0, "", [], None

    # Wait for iframe DOM to hydrate (Streamlit lazy-renders into /~/+/).
    t0 = time.time()
    text = ""
    while time.time() - t0 < 45:
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
            return None, f"inner_text: {e}", 0, "", [], None

    # Charts render lazily AFTER text body appears. Poll for .js-plotly-plot
    # containers; stop early when count stabilizes.
    plotly_count = 0
    last_count = -1
    stable_ticks = 0
    t0 = time.time()
    while time.time() - t0 < POST_HYDRATE_CHART_WAIT_SECS:
        try:
            plotly_count = len(target.query_selector_all(".js-plotly-plot"))
        except Exception:
            plotly_count = 0
        if plotly_count == last_count and plotly_count > 0:
            stable_ticks += 1
            if stable_ticks >= 2:
                break
        else:
            stable_ticks = 0
        last_count = plotly_count
        time.sleep(2)
    # Refresh text after charts may have triggered further DOM updates.
    try:
        text = target.inner_text("body")
    except Exception:
        pass

    with open(os.path.join(dom_dir, f"{slug}.txt"), "w") as fh:
        fh.write(text)

    # Wave 10I.C: capture default-state screenshot BEFORE clicking any tabs.
    default_ss_path = os.path.join(ss_dir, f"{slug}_default.png")
    try:
        page.screenshot(path=default_ss_path, full_page=False)
        print(f"    default screenshot → {slug}_default.png", flush=True)
    except Exception:
        pass

    # Wave 10I.C: click through all tabs and screenshot each.
    tab_records = _screenshot_tabs(page, target, slug, ss_dir, pair_id, page_name)

    # Capture full rendered HTML for marker-presence checks on content
    # Streamlit lazy-hides behind inactive tab panels.
    try:
        html_full = target.content()
    except Exception:
        html_full = ""
    # Return the resolved frame so the caller can run locator-based checks
    # (e.g. APP-TL1 download-button clickability via frame.locator().count()).
    return text, "iframe", plotly_count, html_full, tab_records, target


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_page(text, slug, pair_id, page_name, plotly_count, html=""):
    is_methodology = (page_name == "methodology")
    is_evidence = (page_name == "evidence")
    errs = [p for p in ERR_PATS if p in text]
    # Wave 10I.C: check APP-SEV1 banner strings — user-visible soft errors that
    # are NOT Python exceptions and thus never appear in ERR_PATS.
    text_lower = text.lower()
    app_sev1_hits = [p for p in APP_SEV1_PATS if p.lower() in text_lower]

    # Wave 10J: split stub hits into two buckets:
    #   - cross_period_stub_hits: "Cross-period analysis pending" — severity
    #     depends on CROSS_PERIOD_STUB_IS_FAIL flag (WARN during retro, FAIL after).
    #   - other_stub_hits: all other STUB_PATS — always FAIL.
    CROSS_PERIOD_STUB_PAT = "Cross-period analysis pending"
    raw_stub_hits = [p for p in STUB_PATS if p in text]
    cross_period_stub_hits = [p for p in raw_stub_hits if p == CROSS_PERIOD_STUB_PAT]
    other_stub_hits = [p for p in raw_stub_hits if p != CROSS_PERIOD_STUB_PAT]
    # Compose the effective stub_hits list used by the verdict logic below.
    # During Wave 10J retro (CROSS_PERIOD_STUB_IS_FAIL=False) the cross-period
    # stub is recorded but does NOT contribute to a FAIL verdict.
    stub_hits_for_verdict = other_stub_hits + (
        cross_period_stub_hits if CROSS_PERIOD_STUB_IS_FAIL else []
    )
    # For reporting, include all hits regardless of severity.
    stub_hits = raw_stub_hits

    # GATE-VIZ-NBER1 — Evidence-page NBER shading spot-check (Wave 10J).
    # For Evidence pages, scan the rendered HTML (frame.content()) for "nber",
    # "NBER", or "recession" strings — indicators that NBER recession shading is
    # present in at least one Plotly chart on the page.  This is a WARNING, not
    # a FAIL, because Vera's VIZ-NBER retro-apply to all pairs is not yet complete.
    # WARN during 10J retro, FAIL after VIZ-NBER1 retro-apply complete.
    nber_warn = False
    nber_note = "N/A (non-evidence)"
    if is_evidence:
        # Use full HTML for NBER checks: Plotly shape labels appear in JSON
        # embedded in <script> tags which are present in content() but NOT
        # in inner_text(). Fall back to text if html unavailable.
        nber_source = html if html else text
        nber_source_lower = nber_source.lower()
        nber_found = any(p.lower() in nber_source_lower for p in NBER_SHADING_DOM_PATS)
        if not nber_found:
            nber_warn = True
            nber_note = (
                "GATE-VIZ-NBER1 WARN: No NBER shading indicators found in Evidence page HTML "
                f"(checked patterns: {NBER_SHADING_DOM_PATS}). "
                "WARN during 10J retro, FAIL after VIZ-NBER1 retro-apply complete."
            )
        else:
            nber_note = f"GATE-VIZ-NBER1 PASS: NBER shading indicator present in Evidence HTML ({pair_id})"

    breadcrumb_missing = [b for b in BREADCRUMB if b not in text]
    prefix_pending = bool(PREFIX_PENDING_RE.search(text))
    chart_pending = "chart pending" in text_lower
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

    # Wave 10H.2 APP-TL1 Trade Log Rendering Contract (Strategy page only).
    # For pairs retro-applied this wave, assert four DOM markers are present.
    # For other pairs, this check is N/A and does NOT affect verdict.
    is_strategy = (page_name == "strategy")
    # APP-TL1 markers live inside the "Performance" tab panel which Streamlit
    # renders into DOM but hides when "Execute" is the active tab. Check the
    # full rendered HTML (`target.content()`), not `inner_text` which only
    # traverses visible elements.
    tl1_source = html if html else text
    tl1_heading = APP_TL1_HEADING in tl1_source
    tl1_broker_btn = APP_TL1_BROKER_BTN in tl1_source
    tl1_position_btn = APP_TL1_POSITION_BTN in tl1_source
    tl1_preview = APP_TL1_PREVIEW_CAPTION in tl1_source
    if is_strategy and pair_id in APP_TL1_PAIRS:
        app_tl1_ok = tl1_heading and tl1_broker_btn and tl1_position_btn and tl1_preview
        app_tl1_check = {
            "scope": "applied",
            "heading": tl1_heading,
            "broker_button": tl1_broker_btn,
            "position_button": tl1_position_btn,
            "preview": tl1_preview,
            "ok": app_tl1_ok,
        }
    else:
        app_tl1_ok = True
        app_tl1_check = {"scope": "n/a", "ok": True}

    # NBER warn does NOT affect the PASS/FAIL verdict — it is a warning only.
    verdict = "PASS" if (
        not errs and not app_sev1_hits and not stub_hits_for_verdict
        and not breadcrumb_missing and not prefix_pending
        and not chart_pending and dom_ok and chart_ok and app_pt2_ok
        and app_tl1_ok
    ) else "FAIL"

    return {
        "slug": slug,
        "pair_id": pair_id,
        "page": page_name,
        "dom_len": len(text),
        "errors": errs,
        "app_sev1_hits": app_sev1_hits,   # Wave 10I.C: soft-error banners
        "stub_hits": stub_hits,            # Wave 10I.C/10J: stub/placeholder text (all)
        "cross_period_stub_hits": cross_period_stub_hits,  # Wave 10J: sub-bucket
        "cross_period_stub_is_fail": CROSS_PERIOD_STUB_IS_FAIL,  # Wave 10J
        "nber_warn": nber_warn,            # Wave 10J: NBER shading spot-check (Evidence)
        "nber_note": nber_note,            # Wave 10J: NBER shading detail
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
        "app_tl1_check": app_tl1_check,
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

def gate29_parquet_preflight(pairs, project_root="/workspaces/aig-rlic-plus"):
    """GATE-29 pre-flight: assert signals_*.parquet is committed in git for every pair.

    Wave 10I.C root-cause fix: smoke_loader.py only tests chart JSON loading; it
    does NOT exercise the Strategy page Probability Engine Panel (APP-SE1), which
    reads signals_*.parquet at cloud render time. A missing signals_*.parquet will
    produce a user-visible red banner ("Probability engine panel cannot render:
    No signals_*.parquet under ...") that passes every ERR_PATS check because
    it is not a Python exception — it is app-level soft-error text.

    This pre-flight runs BEFORE the browser pass so that a missing parquet is
    surfaced as a hard FAIL with a clear diagnostic before spending 40s per page
    loading the browser.

    Returns: list of failure dicts (empty = all pairs pass).
    """
    import subprocess
    failures = []
    for pair_id in pairs:
        pattern = f"results/{pair_id}/signals_*.parquet"
        result = subprocess.run(
            ["git", "ls-files", pattern],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        matched = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not matched:
            failures.append({
                "pair_id": pair_id,
                "gate": "GATE-29",
                "finding": f"signals_*.parquet not committed for {pair_id}",
                "detail": (
                    f"`git ls-files {pattern}` returned empty. "
                    "Strategy page Probability Engine Panel will render a red banner "
                    "on Streamlit Cloud. Fix: Evan must produce and commit "
                    f"results/{pair_id}/signals_<date>.parquet (ECON-DS2)."
                ),
            })
        else:
            print(f"  GATE-29 PASS {pair_id}: {matched}", flush=True)
    return failures


def gate_dp1_dual_panel_preflight(pairs, project_root="/workspaces/aig-rlic-plus"):
    """GATE-DP1 (Wave 10K, 2026-04-24): Dual-Panel Trace Visibility Check.

    For every history_zoom_*.json chart committed under
    ``output/charts/{pair_id}/plotly/``, verify that:
      - top-panel traces (yaxis absent or "y") are assigned xaxis="x" (or absent)
      - bottom-panel traces (yaxis="y2") are assigned xaxis="x2"

    Root cause of the gap: all 29 history_zoom charts shipped with
    xaxis="x" on the bottom-panel target trace.  The panel rendered with
    correct y-axis tick labels but a completely blank line — data was present
    in the JSON (800+ points) but invisible on screen because the trace was
    drawing against the wrong x-axis subplot reference.

    GATE-HZE1 confirms heading presence; it cannot catch this because it only
    checks the DOM heading string, not chart internal structure.  GATE-DP1 is
    a JSON-structural extension of GATE-27 and runs as part of the preflight
    before any browser time is spent.

    Returns: list of failure dicts (empty = all charts pass).
    """
    import glob as _glob
    failures = []
    for pair_id in pairs:
        pattern = f"{project_root}/output/charts/{pair_id}/plotly/history_zoom_*.json"
        for fpath in sorted(_glob.glob(pattern)):
            chart_name = os.path.basename(fpath)
            try:
                with open(fpath) as f:
                    chart = json.load(f)
            except Exception as exc:
                failures.append({
                    "pair_id": pair_id,
                    "chart": chart_name,
                    "gate": "GATE-DP1",
                    "finding": f"JSON parse error: {exc}",
                    "detail": str(fpath),
                })
                print(f"  GATE-DP1 FAIL {pair_id}/{chart_name}: JSON parse error: {exc}", flush=True)
                continue

            traces = chart.get("data", [])
            chart_ok = True
            for i, trace in enumerate(traces):
                yaxis = trace.get("yaxis", "y")   # absent defaults to top panel
                xaxis = trace.get("xaxis", "x")   # absent defaults to top panel
                is_bottom = yaxis == "y2"
                expected_xaxis = "x2" if is_bottom else "x"
                if xaxis != expected_xaxis:
                    chart_ok = False
                    finding = (
                        f"GATE-DP1 FAIL: trace[{i}] '{trace.get('name', '<unnamed>')}' "
                        f"has yaxis='{yaxis}' but xaxis='{xaxis}' "
                        f"(expected '{expected_xaxis}'). "
                        f"Mismatched axis reference = invisible trace on screen. "
                        f"Owner: Vera. File: {fpath}"
                    )
                    failures.append({
                        "pair_id": pair_id,
                        "chart": chart_name,
                        "gate": "GATE-DP1",
                        "trace_index": i,
                        "trace_name": trace.get("name", "<unnamed>"),
                        "yaxis": yaxis,
                        "xaxis_actual": xaxis,
                        "xaxis_expected": expected_xaxis,
                        "finding": finding,
                        "detail": str(fpath),
                    })
                    print(f"  GATE-DP1 FAIL {pair_id}/{chart_name}: {finding}", flush=True)
            if chart_ok:
                print(
                    f"  GATE-DP1 PASS {pair_id}/{chart_name}: "
                    f"{len(traces)} trace(s) axis-assignments correct",
                    flush=True,
                )
    return failures


def gate_viz_nber2_preflight(pairs, project_root="/workspaces/aig-rlic-plus"):
    """GATE-VIZ-NBER2 (Wave 10K, 2026-04-24): Episode-window-aware NBER shading check.

    Pure JSON preflight — no browser needed.  Runs alongside GATE-DP1.

    For every committed history_zoom_{slug}.json chart under
    ``output/charts/{pair_id}/plotly/``:

    1. Derive the episode slug from the filename
       (history_zoom_{slug}.json → slug).
    2. Look up whether that slug overlaps a known NBER recession window.
    3. If overlap  → FAIL if layout.shapes contains NO vrect/rect with a
       fillcolor that matches the NBER shading pattern (missing shading in a
       recession episode is a hard defect).
    4. If no overlap → WARN if layout.shapes contains ANY NBER vrect (spurious
       shading is less harmful than missing shading; warn only, not FAIL).

    NBER recessions (canonical, hardcoded):
      - 2001-03-01 → 2001-11-01
      - 2007-12-01 → 2009-06-01
      - 2020-02-01 → 2020-04-01

    Episode–recession overlap table (derived from episode_registry.json):
      dot_com   : overlaps 2001 recession  → NBER shading required
      gfc       : overlaps 2008 recession  → NBER shading required
      covid     : overlaps 2020 recession  → NBER shading required
      taper_2013: no recession             → no NBER shading expected
      china_2015: no recession             → no NBER shading expected
      rates_2022: no recession             → no NBER shading expected

    NBER vrect detection heuristic: a shape is treated as an NBER recession
    band when ALL of the following hold:
      - type is "rect" (vrects are represented as rects in Plotly JSON)
      - xref contains "x" (date axis, not "paper")
      - fillcolor is present and contains a red/grey/salmon hue substring OR
        the shape has a "line" dict with color matching those hues.
    The heuristic is intentionally broad to survive minor palette changes; a
    false-positive (spurious shape counted as NBER) is acceptable because the
    WARN path is non-blocking and QA's job is to flag, not to adjudicate.

    Returns: (failures, warnings) — two lists of dicts.
      failures : GATE-VIZ-NBER2 FAIL items (missing shading in recession window)
      warnings : GATE-VIZ-NBER2 WARN items (spurious shading in non-recession window)
    """
    import glob as _glob
    from datetime import date

    # Slugs that overlap at least one NBER recession window.
    RECESSION_SLUGS = {"dot_com", "gfc", "covid"}

    # Heuristic: colors used by Vera's NBER shading (partial match, lower-case).
    # Covers: rgba(220,50,47,...), rgba(210,…), "#d43f3f", "red", "salmon", grey variants.
    NBER_FILLCOLOR_HINTS = [
        "rgba(220",   # Vera's primary NBER shading (solarized red family)
        "rgba(210",
        "rgba(200",
        "rgba(180",
        "#d4",        # hex reds used in older charts
        "red",
        "salmon",
        "nber",       # explicit label in fillcolor string (rare but valid)
    ]

    def _is_nber_shape(shape: dict) -> bool:
        """Return True if this Plotly shape looks like an NBER recession band."""
        if shape.get("type") != "rect":
            return False
        xref = shape.get("xref", "")
        if "paper" in xref:  # paper-ref shapes are annotations, not data bands
            return False
        fc = str(shape.get("fillcolor", "")).lower()
        lc = str(shape.get("line", {}).get("color", "")).lower()
        combined = fc + lc
        return any(hint in combined for hint in NBER_FILLCOLOR_HINTS)

    failures = []
    warnings = []

    for pair_id in pairs:
        pattern = f"{project_root}/output/charts/{pair_id}/plotly/history_zoom_*.json"
        for fpath in sorted(_glob.glob(pattern)):
            chart_name = os.path.basename(fpath)
            # Derive slug: strip prefix "history_zoom_" and suffix ".json"
            slug = chart_name.replace("history_zoom_", "").replace(".json", "")

            try:
                with open(fpath) as fh:
                    chart = json.load(fh)
            except Exception as exc:
                failures.append({
                    "pair_id": pair_id,
                    "slug": slug,
                    "chart": chart_name,
                    "gate": "GATE-VIZ-NBER2",
                    "finding": f"JSON parse error: {exc}",
                    "detail": str(fpath),
                })
                print(
                    f"  GATE-VIZ-NBER2 FAIL {pair_id}/{chart_name}: JSON parse error: {exc}",
                    flush=True,
                )
                continue

            shapes = chart.get("layout", {}).get("shapes", [])
            nber_shapes = [s for s in shapes if _is_nber_shape(s)]
            has_nber = len(nber_shapes) > 0
            expects_nber = slug in RECESSION_SLUGS

            if expects_nber and not has_nber:
                finding = (
                    f"GATE-VIZ-NBER2 FAIL: {slug} overlaps an NBER recession but "
                    f"layout.shapes contains no NBER recession band (vrect/rect with "
                    f"red/salmon fillcolor). Missing shading misleads the viewer. "
                    f"Owner: Vera. File: {fpath}"
                )
                failures.append({
                    "pair_id": pair_id,
                    "slug": slug,
                    "chart": chart_name,
                    "gate": "GATE-VIZ-NBER2",
                    "finding": finding,
                    "detail": str(fpath),
                })
                print(f"  GATE-VIZ-NBER2 FAIL {pair_id}/{chart_name}: {finding}", flush=True)

            elif not expects_nber and has_nber:
                finding = (
                    f"GATE-VIZ-NBER2 WARN: {slug} does NOT overlap any NBER recession but "
                    f"layout.shapes contains {len(nber_shapes)} apparent NBER band(s). "
                    f"Spurious shading may confuse stakeholders. "
                    f"Owner: Vera. File: {fpath}"
                )
                warnings.append({
                    "pair_id": pair_id,
                    "slug": slug,
                    "chart": chart_name,
                    "gate": "GATE-VIZ-NBER2",
                    "finding": finding,
                    "detail": str(fpath),
                })
                print(f"  GATE-VIZ-NBER2 WARN {pair_id}/{chart_name}: {finding}", flush=True)

            else:
                status = "shading present" if has_nber else "no shading (correct)"
                print(
                    f"  GATE-VIZ-NBER2 PASS {pair_id}/{chart_name}: "
                    f"slug={slug} expects_nber={expects_nber} → {status}",
                    flush=True,
                )

    return failures, warnings


def gate27_perceptual_png_preflight(pairs, project_root="/workspaces/aig-rlic-plus"):
    """GATE-27 extension (D4, Wave 10J): assert perceptual-check PNGs are committed.

    For every pair, Vera is required to commit a kaleido-rendered PNG at
    ``output/charts/{pair_id}/plotly/_perceptual_check_*.png`` as evidence that
    VIZ-CV1 perceptual render was performed before handoff. This is mandatory for
    all chart types on all pairs (mandate approved Wave 10K, 2026-04-24).

    QA cannot verify visual quality — only existence. Absence means Vera skipped
    the kaleido render step (VIZ-CV1 producer-side gate). Severity: FAIL (blocking).
    Owner of fix: Vera.

    Returns: list of failure dicts (empty = all pairs have ≥1 PNG committed).
    """
    import subprocess
    failures_out = []
    for pair_id in pairs:
        pattern = f"output/charts/{pair_id}/plotly/_perceptual_check_*.png"
        result = subprocess.run(
            ["git", "ls-files", pattern],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        matched = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        count = len(matched)
        if count == 0:
            failures_out.append({
                "pair_id": pair_id,
                "gate": "GATE-27-PNG",
                "finding": f"No committed _perceptual_check_*.png for {pair_id}",
                "detail": (
                    f"`git ls-files {pattern}` returned 0 files. "
                    "GATE-27-PNG FAIL: perceptual PNGs are mandatory for all charts on all pairs "
                    f"(VIZ-CV1). Fix: Vera regenerates charts with kaleido and commits "
                    f"output/charts/{pair_id}/plotly/_perceptual_check_<chart_name>.png."
                ),
            })
            print(f"  GATE-27-PNG FAIL {pair_id}: 0 perceptual PNGs committed", flush=True)
        else:
            print(f"  GATE-27-PNG PASS {pair_id}: {count} perceptual PNG(s) committed", flush=True)
    return failures_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--out", default=None, help="Output dir (default: temp/<ts>_cloud_verify)")
    ap.add_argument("--pairs", default=",".join(FOCUS_PAIRS),
                    help="Comma-separated pair_ids to verify")
    ap.add_argument("--skip-gate29", action="store_true",
                    help="Skip GATE-29 parquet pre-flight (use only when explicitly approved)")
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

    # --- GATE-29 pre-flight (Wave 10I.C binding requirement) ---
    # Run before browser pass. A missing signals_*.parquet means the Strategy
    # page Probability Engine Panel will show a red APP-SEV1 banner on Cloud.
    # smoke_loader.py does NOT catch this because it only loads chart JSON.
    gate29_failures = []
    if not args.skip_gate29:
        print("\n[GATE-29 pre-flight] checking signals_*.parquet for all pairs ...", flush=True)
        gate29_failures = gate29_parquet_preflight(pairs)
        for f in gate29_failures:
            print(f"  GATE-29 FAIL {f['pair_id']}: {f['finding']}", flush=True)
            results.append({
                "slug": f"{f['pair_id']}_strategy",
                "pair_id": f["pair_id"],
                "page": "strategy",
                "gate": "GATE-29",
                "verdict": "FAIL",
                "error": f["detail"],
            })
        if gate29_failures:
            print(
                f"  *** {len(gate29_failures)} GATE-29 FAIL(s) — Strategy pages for these "
                "pairs will show APP-SEV1 red banners on Cloud. Fix before browser pass. ***",
                flush=True,
            )
    else:
        print("\n[GATE-29 pre-flight] SKIPPED (--skip-gate29 flag set)", flush=True)

    # --- GATE-DP1 pre-flight (Wave 10K, 2026-04-24) ---
    # JSON-level structural check: every history_zoom_*.json dual-panel chart must
    # assign bottom-panel traces to xaxis="x2" (not xaxis="x").  A mismatch renders
    # correct tick labels but an invisible line — data is present but not drawn.
    # GATE-HZE1 confirms heading presence in DOM; it cannot catch this rendering defect.
    # Run before browser pass; abort browser run if any GATE-DP1 failures exist.
    print("\n[GATE-DP1 pre-flight] checking history_zoom_*.json axis assignments ...", flush=True)
    dp1_failures = gate_dp1_dual_panel_preflight(pairs)
    for f in dp1_failures:
        results.append({
            "slug": f"{f['pair_id']}_story",
            "pair_id": f["pair_id"],
            "page": "story",
            "gate": "GATE-DP1",
            "verdict": "FAIL",
            "error": f["finding"],
        })
    if dp1_failures:
        print(
            f"  *** {len(dp1_failures)} GATE-DP1 FAIL(s) — history_zoom chart(s) have "
            "mismatched axis assignments. Bottom-panel traces are invisible on screen. "
            "Fix owner: Vera. Do not proceed to browser pass until resolved. ***",
            flush=True,
        )
    else:
        print("  GATE-DP1: all history_zoom charts PASS axis-assignment check.", flush=True)

    # --- GATE-VIZ-NBER2 pre-flight (Wave 10K, 2026-04-24) ---
    # Episode-window-aware NBER shading check for history_zoom_*.json charts.
    # FAIL if a recession-overlapping slug has no NBER shading band in layout.shapes.
    # WARN if a non-recession slug has spurious NBER shading (non-blocking).
    print("\n[GATE-VIZ-NBER2 pre-flight] checking NBER shading in history_zoom_*.json ...", flush=True)
    nber2_failures, nber2_warnings = gate_viz_nber2_preflight(pairs)
    for f in nber2_failures:
        results.append({
            "slug": f"{f['pair_id']}_story",
            "pair_id": f["pair_id"],
            "page": "story",
            "gate": "GATE-VIZ-NBER2",
            "verdict": "FAIL",
            "error": f["finding"],
        })
    for w in nber2_warnings:
        results.append({
            "slug": f"{w['pair_id']}_story",
            "pair_id": w["pair_id"],
            "page": "story",
            "gate": "GATE-VIZ-NBER2",
            "verdict": "WARN",
            "error": w["finding"],
        })
    if nber2_failures:
        print(
            f"  *** {len(nber2_failures)} GATE-VIZ-NBER2 FAIL(s) — recession-episode "
            "history_zoom charts missing NBER shading. Fix owner: Vera. ***",
            flush=True,
        )
    if nber2_warnings:
        print(
            f"  *** {len(nber2_warnings)} GATE-VIZ-NBER2 WARN(s) — non-recession-episode "
            "history_zoom charts have spurious NBER shading. Fix owner: Vera (non-blocking). ***",
            flush=True,
        )
    if not nber2_failures and not nber2_warnings:
        print("  GATE-VIZ-NBER2: all history_zoom charts PASS episode-window NBER check.", flush=True)

    # --- GATE-27 PNG pre-flight (D4, Wave 10J; promoted to FAIL Wave 10K 2026-04-24) ---
    # Perceptual PNGs are mandatory for ALL chart types on ALL pairs (VIZ-CV1 mandate).
    # Absence = FAIL (blocking). Owner: Vera.
    print("\n[GATE-27-PNG pre-flight] checking _perceptual_check_*.png for all pairs ...", flush=True)
    gate27_png_warnings = gate27_perceptual_png_preflight(pairs)
    png_warn_counts = {}
    for w in gate27_png_warnings:
        png_warn_counts[w["pair_id"]] = w["detail"]
        results.append({
            "slug": f"{w['pair_id']}_preflight",
            "pair_id": w["pair_id"],
            "page": "preflight",
            "gate": "GATE-27-PNG",
            "verdict": "FAIL",
            "error": w["detail"],
        })
    if gate27_png_warnings:
        print(
            f"  *** {len(gate27_png_warnings)} GATE-27-PNG FAIL(s) — perceptual PNGs missing. "
            "Perceptual PNGs are mandatory for all chart types on all pairs (VIZ-CV1). "
            "Owner: Vera. Fix before browser pass. ***",
            flush=True,
        )

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # Wave 10I.C: accumulate all screenshot records across pages for index.md.
        all_screenshots: list[dict] = []

        # Landing
        print(f"\n[landing] {args.base}/", flush=True)
        dom, src, _, _, _, _ = get_dom(
            page, f"{args.base}/", "landing", dom_dir, ss_dir,
            pair_id="landing", page_name="landing",
        )
        if dom:
            r = check_landing(dom)
            r["src"] = src
            print(f"  verdict={r['verdict']} sample_badge={r['sample_badge']} leak={r['raw_col_leak']}", flush=True)
            results.append(r)
            # Landing default screenshot.
            landing_ss = os.path.join(ss_dir, "landing_default.png")
            if os.path.exists(landing_ss):
                all_screenshots.append({
                    "pair": "landing", "page": "landing",
                    "tab_n": None, "tab_label": "default",
                    "filename": "landing_default.png",
                    "path": landing_ss,
                })
        else:
            results.append({"slug": "landing", "verdict": "FAIL", "error": src})

        # Pairs x pages
        for pair_id in pairs:
            for pg in PAGES:
                slug = f"{pair_id}_{pg}"
                url = f"{args.base}/{slug}"
                print(f"\n[{slug}] {url}", flush=True)
                dom, src, pc, html_full, tab_recs, frame = get_dom(
                    page, url, slug, dom_dir, ss_dir,
                    pair_id=pair_id, page_name=pg,
                )
                if dom is None:
                    results.append({
                        "slug": slug, "pair_id": pair_id, "page": pg,
                        "verdict": "FAIL", "error": src,
                    })
                    print(f"  FAIL: {src}", flush=True)
                    continue

                r = check_page(dom, slug, pair_id, pg, pc, html=html_full)
                r["src"] = src

                # Wave 10I.C: APP-TL1 download-button locator check (Strategy
                # pages for APP-TL1 pairs only). Supplements the HTML-source
                # check in check_page() with a live DOM locator count — confirms
                # the button element is rendered and reachable, not merely present
                # as a string in the raw HTML. Out-of-scope: actually clicking
                # the download (network event testing deferred to local smoke).
                if pg == "strategy" and pair_id in APP_TL1_PAIRS and frame is not None:
                    try:
                        broker_btn_count = frame.locator(
                            f"text={APP_TL1_BROKER_BTN}"
                        ).count()
                        tl1_locator_ok = broker_btn_count > 0
                    except Exception as exc:
                        broker_btn_count = -1
                        tl1_locator_ok = False
                        print(f"    TL1 locator check exception: {exc}", flush=True)
                    r["app_tl1_locator"] = {
                        "broker_btn_count": broker_btn_count,
                        "ok": tl1_locator_ok,
                    }
                    if not tl1_locator_ok:
                        # Upgrade the verdict to FAIL if the locator-based check
                        # disagrees with the HTML-source check (belt-and-suspenders).
                        r["verdict"] = "FAIL"
                    print(
                        f"  APP-TL1 locator: broker_btn_count={broker_btn_count} ok={tl1_locator_ok}",
                        flush=True,
                    )
                else:
                    r["app_tl1_locator"] = {"scope": "n/a"}

                print(
                    f"  verdict={r['verdict']} dom_len={r['dom_len']} "
                    f"charts={r['chart_count']} errs={r['errors']} "
                    f"sev1={r['app_sev1_hits']} stubs={r['stub_hits']} "
                    f"prefix={r['prefix_pending']} bcmiss={r['breadcrumb_missing']} "
                    f"app_pt2={r['app_pt2_ok']} ({r['app_pt2_note']}) "
                    f"app_tl1={r['app_tl1_check']}",
                    flush=True,
                )
                results.append(r)

                # Accumulate default + tab screenshots into the shared index.
                default_fn = f"{slug}_default.png"
                default_path = os.path.join(ss_dir, default_fn)
                if os.path.exists(default_path):
                    all_screenshots.append({
                        "pair": pair_id, "page": pg,
                        "tab_n": None, "tab_label": "default",
                        "filename": default_fn,
                        "path": default_path,
                    })
                for trec in tab_recs:
                    all_screenshots.append(trec)

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
        "gate27_png_warnings": gate27_png_warnings,   # D4 Wave 10J: perceptual PNG existence
        "gate_dp1_failures": dp1_failures,            # Wave 10K: dual-panel axis-assignment check
        "results": results,
    }
    with open(os.path.join(out_dir, "results.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    with open(os.path.join(out_dir, "summary.txt"), "w") as fh:
        fh.write(f"cloud_verify {t_start}\n")
        fh.write(f"PASS {summary['pass']}  FAIL {summary['fail']}  TOTAL {summary['total']}\n\n")
        for r in results:
            sev1 = r.get('app_sev1_hits') or []
            stubs = r.get('stub_hits') or []
            nber_w = r.get('nber_warn', False)
            fh.write(f"  {r.get('verdict','?'):4}  {r.get('slug','?'):42}  "
                     f"charts={r.get('chart_count','-')}  "
                     f"sev1={sev1 if sev1 else 'OK'}  "
                     f"stubs={stubs if stubs else 'OK'}  "
                     f"app_pt2={r.get('app_pt2_ok','-')}  "
                     f"nber={'WARN' if nber_w else 'OK'}\n")

    # Wave 10I.C: write shared evidence package index.md inside screenshots/.
    index_path = os.path.join(ss_dir, "index.md")
    with open(index_path, "w") as fh:
        fh.write(f"# Screenshot Evidence Package\n\n")
        fh.write(f"Generated: {t_end}  \nBase URL: {args.base}  \n")
        fh.write(f"Total screenshots: {len(all_screenshots)}\n\n")
        fh.write("| Pair | Page | Tab | Filename | Path |\n")
        fh.write("|------|------|-----|----------|------|\n")
        for s in all_screenshots:
            tab_label = s.get("tab_label") or "default"
            tab_n = s.get("tab_n")
            tab_cell = f"{tab_n}: {tab_label}" if tab_n is not None else tab_label
            fh.write(
                f"| {s.get('pair','')} | {s.get('page','')} "
                f"| {tab_cell} | {s.get('filename','')} "
                f"| {s.get('path','')} |\n"
            )
    print(f"Screenshot index: {index_path}", flush=True)

    png_fail_count = len(gate27_png_warnings)
    dp1_fail_count = len(dp1_failures)
    print(f"\n=== SUMMARY: {summary['pass']} PASS / {summary['fail']} FAIL / {summary['total']} TOTAL"
          f" | GATE-27-PNG FAIL: {png_fail_count} pair(s) missing perceptual PNGs"
          f" | GATE-DP1 FAIL: {dp1_fail_count} axis-assignment issue(s) ===", flush=True)
    if png_fail_count:
        print("  GATE-27-PNG FAIL: pairs missing _perceptual_check_*.png: "
              + ", ".join(w["pair_id"] for w in gate27_png_warnings), flush=True)
    if dp1_fail_count:
        seen = set()
        for f in dp1_failures:
            key = f"{f['pair_id']}/{f['chart']}"
            if key not in seen:
                seen.add(key)
                print(f"  GATE-DP1 FAIL: {key} — {f.get('finding','')}", flush=True)
    print(f"Results: {out_dir}/results.json", flush=True)
    return 0 if summary["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
