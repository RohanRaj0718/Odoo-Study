#!/usr/bin/env python3
"""
Get measures for Referral Analysis and Rewards reports specifically.
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
        print("=== REFERRAL ANALYSIS - Measures ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(6)

        measures_btn = page.locator('button:has-text("Measures")').first
        if measures_btn.is_visible():
            measures_btn.click()
            time.sleep(1)
            
            # Get all items in the dropdown more carefully
            dropdown = page.locator('.o-dropdown--menu').first
            if dropdown.is_visible():
                html = dropdown.inner_html()
                print(f"Dropdown HTML:\n{html[:3000]}")
            
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Check x-axis default: what's shown on the graph
        # The graph renderer should tell us the default groupby
        graph_renderer = page.locator('.o_graph_renderer')
        if graph_renderer.count() > 0:
            # Check ARIA labels on chart
            aria_labels = page.locator('[aria-label]').all()
            for el in aria_labels:
                label = el.get_attribute('aria-label') or ''
                if label and ('chart' in label.lower() or 'graph' in label.lower()):
                    print(f"  aria-label: {label}")

        print("\n\n=== REWARDS REPORT - Measures & X-axis ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(6)

        measures_btn2 = page.locator('button:has-text("Measures")').first
        if measures_btn2.is_visible():
            measures_btn2.click()
            time.sleep(1)
            
            dropdown2 = page.locator('.o-dropdown--menu').first
            if dropdown2.is_visible():
                html2 = dropdown2.inner_html()
                print(f"Dropdown HTML:\n{html2[:3000]}")
            
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Check the active filters to understand default grouping
        facets = page.locator('.o_searchview_facet').all()
        print(f"\nActive filters: {len(facets)}")
        for f in facets:
            print(f"  Filter: {f.text_content().strip()}")

        # Check search bar for available GroupBy
        search_input = page.locator('.o_searchview_input')
        if search_input.count() > 0:
            search_input.first.click()
            time.sleep(1)
            
            # Get all dropdown content
            autocomplete = page.locator('.o_searchview_autocomplete')
            if autocomplete.count() > 0:
                html3 = autocomplete.inner_html()
                print(f"\nSearch autocomplete HTML:\n{html3[:2000]}")
            page.keyboard.press("Escape")

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
