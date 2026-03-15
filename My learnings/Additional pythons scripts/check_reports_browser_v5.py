#!/usr/bin/env python3
"""
Detailed check of measures and groupby for each report.
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

        # Go to referrals
        page.goto(f"{URL}/odoo/referrals", wait_until="load")
        time.sleep(5)

        # ── REFERRAL ANALYSIS ──
        print("=== REFERRAL ANALYSIS ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(6)

        # Measures
        measures_btn = page.locator('button:has-text("Measures")').first
        if measures_btn.is_visible():
            measures_btn.click()
            time.sleep(1)
            # Read all dropdown items
            items = page.locator('.o-dropdown--menu span, .o-dropdown--menu .o_menu_item').all()
            print("Measures dropdown items:")
            for item in items:
                txt = item.text_content().strip()
                # Check if it has a checkmark icon
                has_check = item.locator('i').count() > 0
                if txt and len(txt) > 1:
                    print(f"  {txt} {'(CHECKED)' if has_check else ''}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # GroupBy / search bar options
        search_input = page.locator('.o_searchview_input')
        if search_input.count() > 0:
            search_input.first.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/20_analysis_searchbar.png", full_page=True)
            
            # Check group by options
            groupby_items = page.locator('.o_searchview_autocomplete .o_menu_item, .o_group_by_menu .o_menu_item').all()
            print("\nSearch/GroupBy options:")
            for item in groupby_items:
                txt = item.text_content().strip()
                if txt:
                    print(f"  {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # What's the default X-axis grouping? Check by looking at pivot
        print("\nSwitching to Pivot for Referral Analysis...")
        switch_btns = page.locator('.o_cp_switch_buttons button').all()
        for btn in switch_btns:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip:
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/20b_analysis_pivot.png", full_page=True)
                pivot = page.locator('.o_pivot table')
                if pivot.count() > 0:
                    # Get all header cells
                    headers = pivot.locator('thead th').all()
                    print("Pivot headers:")
                    for h in headers:
                        txt = h.text_content().strip()
                        if txt:
                            print(f"  {txt}")
                    
                    # Get all row data
                    rows = pivot.locator('tbody tr').all()
                    print("Pivot rows:")
                    for row in rows:
                        cells = row.locator('td, th').all()
                        cell_texts = [c.text_content().strip() for c in cells if c.text_content().strip()]
                        if cell_texts:
                            print(f"  {cell_texts}")
                break

        # ── REWARDS REPORT ──
        print("\n\n=== REWARDS REPORT ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(6)

        # Measures
        measures_btn2 = page.locator('button:has-text("Measures")').first
        if measures_btn2.is_visible():
            measures_btn2.click()
            time.sleep(1)
            items2 = page.locator('.o-dropdown--menu span, .o-dropdown--menu .o_menu_item').all()
            print("Rewards Measures dropdown:")
            for item in items2:
                txt = item.text_content().strip()
                has_check = item.locator('i').count() > 0
                if txt and len(txt) > 1:
                    print(f"  {txt} {'(CHECKED)' if has_check else ''}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # GroupBy
        search_input2 = page.locator('.o_searchview_input')
        if search_input2.count() > 0:
            search_input2.first.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/21_rewards_searchbar.png", full_page=True)
            groupby2 = page.locator('.o_searchview_autocomplete .o_menu_item').all()
            print("\nRewards Search options:")
            for item in groupby2:
                txt = item.text_content().strip()
                if txt:
                    print(f"  {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Switch to pivot
        print("\nSwitching Rewards to Pivot...")
        switch_btns2 = page.locator('.o_cp_switch_buttons button').all()
        for btn in switch_btns2:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip:
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/21b_rewards_pivot.png", full_page=True)
                pivot2 = page.locator('.o_pivot table')
                if pivot2.count() > 0:
                    headers2 = pivot2.locator('thead th').all()
                    print("Rewards Pivot headers:")
                    for h in headers2:
                        print(f"  {h.text_content().strip()}")
                    
                    rows2 = pivot2.locator('tbody tr').all()
                    print("Rewards Pivot rows:")
                    for row in rows2:
                        cells = row.locator('td, th').all()
                        cell_texts = [c.text_content().strip() for c in cells if c.text_content().strip()]
                        if cell_texts:
                            print(f"  {cell_texts}")
                break

        # Switch to list
        for btn in switch_btns2:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'List' in tooltip:
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/21c_rewards_list.png", full_page=True)
                
                headers3 = page.locator('.o_list_view thead th').all()
                print(f"\nRewards List columns: {[h.text_content().strip() for h in headers3 if h.text_content().strip()]}")

                rows3 = page.locator('.o_data_row').all()
                for row in rows3:
                    cells = row.locator('td').all()
                    print(f"  {[c.text_content().strip() for c in cells]}")
                break

        # ── POINTS REPORT ──
        print("\n\n=== POINTS REPORT ===")
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Points")').first.click()
        time.sleep(6)

        # Check available views
        switch_btns3 = page.locator('.o_cp_switch_buttons button').all()
        print(f"Available views: {len(switch_btns3)}")
        for i, btn in enumerate(switch_btns3):
            tooltip = btn.get_attribute('data-tooltip') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            print(f"  [{i}] '{tooltip}' active={active}")

        # Full table screenshot
        page.screenshot(path="c:/Odoo Study/report_screenshots/22_points_full.png", full_page=True)

        print("\n" + "=" * 70)
        print("DETAILED CHECK COMPLETE")
        print("=" * 70)
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/report_screenshots", exist_ok=True)
    main()
