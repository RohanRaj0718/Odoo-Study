#!/usr/bin/env python3
"""
Just take screenshots of each report page to see the layout.
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

        page.screenshot(path="C:/Odoo Study/report_screenshots/analysis_full_page.png", full_page=True)
        print("Screenshot saved: analysis_full_page.png")

        # Dump page HTML structure (key elements)
        # Find all buttons in the control panel area
        cp_buttons = page.locator('.o_control_panel button').all()
        print(f"\nControl panel buttons ({len(cp_buttons)}):")
        for btn in cp_buttons:
            txt = btn.text_content().strip()
            aria = btn.get_attribute('aria-label') or ''
            cls = btn.get_attribute('class') or ''
            if txt or aria:
                print(f"  button: text='{txt}' aria='{aria}' class='{cls[:80]}'")

        # Check for measure-related elements
        for sel in ['[data-measure]', '.o_graph_measures', '.o_pivot_measures', 
                     '.o_graph_buttons', '.o_cp_buttons']:
            els = page.locator(sel).all()
            if els:
                print(f"\n{sel}: {len(els)} elements")
                for el in els[:5]:
                    print(f"  HTML: {el.inner_html()[:500]}")

        # ── REWARDS ──
        print("\n\n=== REWARDS REPORT ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(8)

        page.screenshot(path="C:/Odoo Study/report_screenshots/rewards_full_page.png", full_page=True)
        print("Screenshot saved: rewards_full_page.png")

        cp_buttons2 = page.locator('.o_control_panel button').all()
        print(f"\nControl panel buttons ({len(cp_buttons2)}):")
        for btn in cp_buttons2:
            txt = btn.text_content().strip()
            aria = btn.get_attribute('aria-label') or ''
            cls = btn.get_attribute('class') or ''
            if txt or aria:
                print(f"  button: text='{txt}' aria='{aria}' class='{cls[:80]}'")

        # ── POINTS ──
        print("\n\n=== POINTS REPORT ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Points")').first.click()
        time.sleep(8)

        page.screenshot(path="C:/Odoo Study/report_screenshots/points_full_page.png", full_page=True)
        print("Screenshot saved: points_full_page.png")

        cp_buttons3 = page.locator('.o_control_panel button').all()
        print(f"\nControl panel buttons ({len(cp_buttons3)}):")
        for btn in cp_buttons3:
            txt = btn.text_content().strip()
            aria = btn.get_attribute('aria-label') or ''
            cls = btn.get_attribute('class') or ''
            if txt or aria:
                print(f"  button: text='{txt}' aria='{aria}' class='{cls[:80]}'")

        # ── Full page HTML for debugging ──
        print("\n\n=== Page Title ===")
        print(page.title())

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
