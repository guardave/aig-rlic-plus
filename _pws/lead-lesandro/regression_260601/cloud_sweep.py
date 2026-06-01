"""Track B — cloud regression for fix260601_rescue."""
import asyncio
import sys
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://aig-rlic-plus-fix260601-rescue.streamlit.app"

PAIRS = [
    "indpro_spy", "indpro_xlp", "umcsent_xlv",
    "hy_ig_v2_spy", "hy_ig_spy",
    "permit_spy", "vix_vix3m_spy",
    "sofr_ted_spy", "dff_ted_spy", "ted_spliced_spy",
    "gold_copper_xli",
]
SECTIONS = ["story", "evidence", "strategy", "methodology"]

ERROR_MARKERS = [
    "Traceback", "RuntimeError", "ValueError", "KeyError",
    "ImportError", "ModuleNotFoundError", "AttributeError",
    "❌", "Schema validation", "validate_or_die",
    "L1 error", "An error has occurred",
]

async def fetch(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        iframe = await page.wait_for_selector('iframe[title="streamlitApp"]', timeout=30000)
    except Exception as e:
        return None, f"IFRAME: {e}"
    frame = await iframe.content_frame()
    for _ in range(30):
        txt = await frame.inner_text("body")
        if len(txt) > 500:
            break
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

        # Landing
        txt, err = await fetch(page, f"{BASE}/")
        if err:
            results.append(("LANDING", "ERR", 0, [err]))
        else:
            markers = [m for m in ERROR_MARKERS if m in txt]
            results.append(("LANDING", "OK" if not markers else "ERR", len(txt), markers))

        # Sweep
        for pair in PAIRS:
            for section in SECTIONS:
                url = f"{BASE}/{pair}_{section}"
                txt, err = await fetch(page, url)
                if err:
                    results.append((f"{pair}/{section}", "ERR", 0, [err]))
                    continue
                markers = [m for m in ERROR_MARKERS if m in txt]
                results.append((f"{pair}/{section}", "OK" if not markers else "ERR", len(txt), markers))
        await b.close()

    print(f"{'Page':40s} {'Status':>6s} {'Len':>7s} Markers")
    n_ok = n_err = 0
    for name, status, length, markers in results:
        flag = "✓" if status == "OK" else "✗"
        if status == "OK": n_ok += 1
        else: n_err += 1
        ms = ",".join(markers[:2]) if markers else ""
        print(f"{name:40s} {flag} {status:>4s} {length:>7d} {ms}")
    print()
    print(f"PASS: {n_ok}  FAIL: {n_err}  TOTAL: {len(results)}")
asyncio.run(main())
