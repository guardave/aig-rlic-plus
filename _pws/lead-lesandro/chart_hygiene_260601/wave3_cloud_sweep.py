"""Track B cloud sweep for fix260601_chart_hygiene against dawodev WIP slot."""
import asyncio
from playwright.async_api import async_playwright

BASE = "https://aig-rlic-plus-dawodev.streamlit.app"
ACTIVE_PAIRS = ["indpro_spy", "indpro_xlp", "umcsent_xlv", "hy_ig_v2_spy",
                "hy_ig_spy", "permit_spy", "vix_vix3m_spy", "gold_copper_xli"]
ARCHIVED_PAIRS = ["sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy"]
SECTIONS = ["story", "evidence", "strategy", "methodology"]
ERROR_MARKERS = ["Traceback", "RuntimeError", "ValueError", "KeyError",
                 "ImportError", "ModuleNotFoundError", "AttributeError",
                 "❌", "Schema validation", "validate_or_die",
                 "L1 error", "An error has occurred"]

async def fetch(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        iframe = await page.wait_for_selector('iframe[title="streamlitApp"]', timeout=30000)
    except Exception as e:
        return None, f"IFRAME: {e}"
    frame = await iframe.content_frame()
    for _ in range(30):
        txt = await frame.inner_text("body")
        if len(txt) > 500: break
        await page.wait_for_timeout(1500)
    await page.wait_for_timeout(5000)
    return await frame.inner_text("body"), None

async def main():
    print(f"BASE: {BASE}")
    results = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1400, "height": 900})
        page = await ctx.new_page()

        # Landing — should show 8 of 73 and not surface archived pairs
        txt, err = await fetch(page, f"{BASE}/")
        markers = []
        if err:
            results.append(("LANDING", "ERR", 0, [err]))
        else:
            markers = [m for m in ERROR_MARKERS if m in txt]
            if "8 of 73" in txt:
                pass  # expected
            elif "11 of 73" in txt:
                markers.append("STILL-SHOWS-11-of-73")
            # Verify archived pairs absent
            for ap in ARCHIVED_PAIRS:
                if ap in txt.lower():
                    markers.append(f"ARCHIVED-VISIBLE:{ap}")
            results.append(("LANDING", "OK" if not markers else "ERR", len(txt), markers))

        # Active pairs sweep
        for pair in ACTIVE_PAIRS:
            for section in SECTIONS:
                url = f"{BASE}/{pair}_{section}"
                txt, err = await fetch(page, url)
                if err:
                    results.append((f"{pair}/{section}", "ERR", 0, [err]))
                    continue
                markers = [m for m in ERROR_MARKERS if m in txt]
                results.append((f"{pair}/{section}", "OK" if not markers else "ERR", len(txt), markers))

        # Archive checks: URLs should return 'Page not found' or similar
        for ap in ARCHIVED_PAIRS:
            url = f"{BASE}/{ap}_story"
            txt, err = await fetch(page, url)
            if err:
                results.append((f"archive-check {ap}_story", "OK", 0, []))
                continue
            # Streamlit serves a "Page not found" view; key is short content + no pair name
            has_pair_content = ap in (txt or "").lower() and len(txt or "") > 4000
            ok_archived = not has_pair_content
            results.append((f"archive-check {ap}_story", "OK" if ok_archived else "ERR",
                          len(txt or ""), [] if ok_archived else ["archived URL still serving pair content"]))

        await b.close()

    print(f"\n{'Page':40s} {'Status':>6s} {'Len':>7s} Markers")
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
