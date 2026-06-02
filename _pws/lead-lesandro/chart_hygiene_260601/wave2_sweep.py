"""Local sweep — 8 pairs × 4 sections after TED archive."""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8501"
PAIRS = ["indpro_spy", "indpro_xlp", "umcsent_xlv", "hy_ig_v2_spy", "hy_ig_spy",
         "permit_spy", "vix_vix3m_spy", "gold_copper_xli"]
SECTIONS = ["story", "evidence", "strategy", "methodology"]
ERROR_MARKERS = ["Traceback", "RuntimeError", "ValueError", "KeyError",
                 "ImportError", "ModuleNotFoundError", "AttributeError",
                 "❌", "Schema validation", "validate_or_die",
                 "L1 error", "An error has occurred"]
ARCHIVED_PAIRS = ["sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy"]

async def fetch(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    except Exception as e:
        return None, f"NAV: {e}"
    for _ in range(15):
        txt = await page.inner_text("body")
        if len(txt) > 500: break
        await page.wait_for_timeout(1000)
    await page.wait_for_timeout(3000)
    return await page.inner_text("body"), None

async def main():
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1400, "height": 900})
        page = await ctx.new_page()
        # Landing
        txt, err = await fetch(page, f"{BASE}/")
        markers = [] if err else [m for m in ERROR_MARKERS if m in txt]
        # Also verify the 3 archived pairs are absent from landing
        archived_present = []
        if not err:
            for ap in ARCHIVED_PAIRS:
                if ap in txt.lower(): archived_present.append(ap)
        if archived_present:
            markers.append(f"ARCHIVED-VISIBLE: {archived_present}")
        results.append(("LANDING", "OK" if (not err and not markers) else "ERR",
                       len(txt) if not err else 0, markers if not err else [err]))
        for pair in PAIRS:
            for section in SECTIONS:
                url = f"{BASE}/{pair}_{section}"
                txt, err = await fetch(page, url)
                if err: results.append((f"{pair}/{section}", "ERR", 0, [err])); continue
                markers = [m for m in ERROR_MARKERS if m in txt]
                results.append((f"{pair}/{section}", "OK" if not markers else "ERR", len(txt), markers))
        # ALSO: verify archived URLs are 404 / show 'Page not found'
        for ap in ARCHIVED_PAIRS:
            url = f"{BASE}/{ap}_story"
            txt, err = await fetch(page, url)
            # Streamlit serves a "not found" page; check for known marker
            ok_404 = err is not None or txt is None or "Page not found" in (txt or "") or len(txt or "") < 1000 or ap not in (txt or "").lower()
            results.append((f"archive-check {ap}_story", "OK" if ok_404 else "ERR", len(txt or ""), [] if ok_404 else ["archived URL still serving content"]))
        await b.close()

    print(f"{'Page':40s} {'Status':>6s} {'Len':>7s} Markers")
    n_ok = n_err = 0
    for name, status, length, markers in results:
        flag = "✓" if status == "OK" else "✗"
        if status == "OK": n_ok += 1
        else: n_err += 1
        ms = ",".join(str(m) for m in markers[:2]) if markers else ""
        print(f"{name:40s} {flag} {status:>4s} {length:>7d} {ms}")
    print()
    print(f"PASS: {n_ok}  FAIL: {n_err}  TOTAL: {len(results)}")
asyncio.run(main())
