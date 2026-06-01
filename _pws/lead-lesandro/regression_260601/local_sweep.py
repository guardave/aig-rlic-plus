"""Local Streamlit sweep for fix260601_rescue regression.

Sweeps every pair × every page section on http://127.0.0.1:8501 and
greps for error markers. Mirrors what cloud_verify.py does on the cloud.
"""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8501"

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

async def fetch_text(page, url, timeout_ms=15000):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
    except Exception as e:
        return None, f"NAV: {e}"
    # Local Streamlit doesn't use the iframe wrapper on the cloud — it
    # serves DOM directly. Wait for body to fill.
    for _ in range(15):
        txt = await page.inner_text("body")
        if len(txt) > 500:
            break
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
        txt, err = await fetch_text(page, f"{BASE}/")
        markers = []
        if err:
            results.append(("LANDING", err, 0, []))
        else:
            for m in ERROR_MARKERS:
                if m in txt:
                    markers.append(m)
            results.append(("LANDING", "OK" if not markers else "ERR", len(txt), markers))

        # Sweep
        for pair in PAIRS:
            for section in SECTIONS:
                url = f"{BASE}/{pair}_{section}"
                txt, err = await fetch_text(page, url)
                markers = []
                if err:
                    results.append((f"{pair}/{section}", err, 0, []))
                    continue
                for m in ERROR_MARKERS:
                    if m in txt:
                        markers.append(m)
                results.append((f"{pair}/{section}", "OK" if not markers else "ERR", len(txt), markers))
        await b.close()

    print(f"{'Page':40s} {'Status':>6s} {'Len':>7s} Markers")
    n_ok = n_err = 0
    for name, status, length, markers in results:
        flag = "✓" if status == "OK" else "✗"
        if status == "OK":
            n_ok += 1
        else:
            n_err += 1
        marker_str = ",".join(markers[:3]) if markers else ""
        print(f"{name:40s} {flag} {status:>4s} {length:>7d} {marker_str}")
    print()
    print(f"PASS: {n_ok}  FAIL: {n_err}  TOTAL: {len(results)}")

asyncio.run(main())
