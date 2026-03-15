#!/usr/bin/env python3
"""
Find Measures dropdown inside the graph/pivot view area.
"""

from playwright.sync_api import sync_playwright
import time

URL = "https://demo-tech.odoo.com"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.set_default_timeout(60000)

        # Login
        page.goto(f"{URL}/web/login", wait_until="load")
        time.sleep(3)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.locator('.oe_login_buttons button[type="submit"]').first.click()
        page.wait_for_url("**/odoo**", timeout=60000)
        time.sleep(5)

        page.goto(f"{URL}/odoo/referrals", wait_until="load")
        time.sleep(5)

        # ── REFERRAL ANALYSIS ──
        print("=== REFERRAL ANALYSIS ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(8)

        # Find all buttons/dropdowns on the page
        all_btns = page.locator('button').all()
        print(f"Total buttons on page: {len(all_btns)}")
        for i, btn in enumerate(all_btns):
            try:
                txt = btn.text_content().strip()
                aria = btn.get_attribute('aria-label') or ''
                cls = btn.get_attribute('class') or ''
                title = btn.get_attribute('title') or ''
                vis = btn.is_visible()
                if vis:
                    print(f"  [{i}] text='{txt}' aria='{aria}' title='{title}' class='{cls[:60]}'")
            except:
                pass

        # Check for any dropdown toggle in the graph buttons area
        print("\n--- Graph buttons area ---")
        graph_btns_area = page.locator('.o_graph_buttons, .o_graph_controller, .o_view_controller')
        if graph_btns_area.count() > 0:
            for i in range(graph_btns_area.count()):
                html = graph_btns_area.nth(i).inner_html()
                print(f"  Area {i}: {html[:1000]}")

        # Check for the dropdown that has "Measures" or similar in graph area
        print("\n--- All dropdowns ---")
        dropdowns = page.locator('.dropdown-toggle, [data-dropdown]').all()
        for i, dd in enumerate(dropdowns):
            try:
                txt = dd.text_content().strip()
                vis = dd.is_visible()
                if vis:
                    print(f"  [{i}] text='{txt}' tag={dd.evaluate('el => el.tagName')}")
            except:
                pass

        # Look for "Measures" text anywhere
        print("\n--- 'Measures' text on page? ---")
        measures_els = page.locator(':text("Measures")').all()
        print(f"  Found {len(measures_els)} elements with 'Measures'")
        for el in measures_els:
            try:
                if el.is_visible():
                    tag = el.evaluate('el => el.tagName')
                    cls = el.get_attribute('class') or ''
                    print(f"    tag={tag} class='{cls[:80]}' text='{el.text_content().strip()[:50]}'")
            except:
                pass

        # Check the content area for measure-specific stuff
        print("\n--- Graph renderer content ---")
        renderer = page.locator('.o_graph_renderer')
        if renderer.count() > 0:
            # Get just the inner structure, not the canvas
            html = renderer.first.inner_html()
            # Print first bit (no canvas)
            lines = html.split('>')
            for line in lines[:30]:
                stripped = line.strip()
                if stripped and 'canvas' not in stripped.lower():
                    print(f"  {stripped[:120]}>")

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
