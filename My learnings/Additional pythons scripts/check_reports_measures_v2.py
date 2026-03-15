#!/usr/bin/env python3
"""
Capture measures dropdown content using more specific selectors.
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
        time.sleep(6)

        # Click Measures button
        measures_btn = page.locator('button:has-text("Measures")').first
        measures_btn.click()
        time.sleep(2)
        
        # Screenshot the measures dropdown
        page.screenshot(path="C:/Odoo Study/report_screenshots/analysis_measures_dropdown.png", full_page=False)
        
        # Try various selectors
        for selector in ['.o-dropdown--menu', '.dropdown-menu.show', '.dropdown-menu', 
                         '[role="menu"]', '.o_menu_item', '.dropdown-item']:
            els = page.locator(selector).all()
            if els:
                print(f"\n{selector} found {len(els)} elements:")
                for el in els[:20]:
                    txt = el.text_content().strip()
                    if txt:
                        print(f"  - {txt}")
        
        # Try getting ALL visible text on the page that might be measure items
        # Check for .o_graph_measures_list
        for selector in ['.o_graph_measures_list', '.o_cp_buttons .dropdown-menu']:
            els = page.locator(selector).all()
            if els:
                print(f"\n{selector}:")
                for el in els:
                    print(f"  HTML: {el.inner_html()[:2000]}")
        
        page.keyboard.press("Escape")
        time.sleep(1)

        # Now switch to Pivot view to see all the column metrics
        print("\n=== REFERRAL ANALYSIS - PIVOT VIEW ===")
        pivot_btn = page.locator('button[aria-label="Pivot"]')
        if pivot_btn.count() > 0:
            pivot_btn.first.click()
            time.sleep(5)
            
            # Click Measures in pivot view
            measures_btn2 = page.locator('button:has-text("Measures")').first
            measures_btn2.click()
            time.sleep(2)
            
            page.screenshot(path="C:/Odoo Study/report_screenshots/analysis_pivot_measures.png", full_page=False)
            
            for selector in ['.o-dropdown--menu', '.dropdown-menu.show', '.dropdown-menu',
                             '[role="menu"]', '.o_menu_item']:
                els = page.locator(selector).all()
                if els:
                    print(f"\n{selector} found {len(els)} elements:")
                    for el in els[:20]:
                        txt = el.text_content().strip()
                        if txt:
                            print(f"  - {txt}")
            
            page.keyboard.press("Escape")
        
        # ── REWARDS ──
        print("\n\n=== REWARDS REPORT ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(6)
        
        # Measures
        measures_btn3 = page.locator('button:has-text("Measures")').first
        measures_btn3.click()
        time.sleep(2)
        
        page.screenshot(path="C:/Odoo Study/report_screenshots/rewards_measures_dropdown.png", full_page=False)
        
        for selector in ['.o-dropdown--menu', '.dropdown-menu.show', '.dropdown-menu',
                         '[role="menu"]', '.o_menu_item']:
            els = page.locator(selector).all()
            if els:
                print(f"\n{selector} found {len(els)} elements:")
                for el in els[:20]:
                    txt = el.text_content().strip()
                    if txt:
                        print(f"  - {txt}")
        
        page.keyboard.press("Escape")
        time.sleep(1)

        # Check what views are available in Rewards
        switch_btns = page.locator('.o_switch_view').all()
        print(f"\nRewards switch views: {len(switch_btns)}")
        for sb in switch_btns:
            label = sb.get_attribute('aria-label') or ''
            active = 'active' if 'active' in (sb.get_attribute('class') or '') else ''
            print(f"  - {label} {active}")

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
