#!/usr/bin/env python3
"""Inspect Streamlit portal pages with Playwright headless browser."""

import asyncio
import os

SCREENSHOT_DIR = "/workspaces/aig-rlic-plus/temp/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BASE_URL = "http://localhost:8501"

PAGES = [
    ("landing", BASE_URL),
    ("indpro_story", f"{BASE_URL}/indpro_spy_story"),
    ("indpro_evidence", f"{BASE_URL}/indpro_spy_evidence"),
    ("indpro_strategy", f"{BASE_URL}/indpro_spy_strategy"),
    ("indpro_methodology", f"{BASE_URL}/indpro_spy_methodology"),
]


async def inspect_pages():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        for name, url in PAGES:
            print(f"\n--- Inspecting: {name} ({url}) ---")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(4000)

                ss_path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
                await page.screenshot(path=ss_path, full_page=True)
                print(f"  Screenshot: {ss_path}")

                body_text = await page.inner_text("body")

                issues = []
                for line in body_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    # Raw HTML tags visible
                    if any(tag in line for tag in ["<div", "<span", "<b>", "</h4>", "<br>"]):
                        issues.append(f"  RAW HTML: {line[:150]}")
                    # Raw markdown
                    if line.startswith("###") or line.startswith("##"):
                        issues.append(f"  RAW MD heading: {line[:150]}")
                    if line.startswith("**") and line.endswith("**"):
                        issues.append(f"  RAW MD bold: {line[:150]}")

                if issues:
                    print(f"  ISSUES ({len(issues)}):")
                    for issue in issues[:15]:
                        print(issue)
                else:
                    print("  OK - No rendering issues detected")

            except Exception as e:
                print(f"  ERROR: {e}")

        await browser.close()


asyncio.run(inspect_pages())
