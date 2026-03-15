#!/usr/bin/env python3
"""
Open demo-tech.odoo.com Referrals reports in browser, take screenshots.
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

        # ── 1. Login ──
        print("Navigating to login page...")
        page.goto(f"{URL}/web/login", wait_until="networkidle")
        time.sleep(2)
        page.screenshot(path="c:/Odoo Study/report_screenshots/00_login_page.png", full_page=True)
        
        # Find the login button
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        
        # Try different selectors for login button
        login_btn = page.locator('.oe_login_buttons button[type="submit"]')
        if login_btn.count() == 0:
            login_btn = page.locator('button:has-text("Log in")')
        if login_btn.count() == 0:
            login_btn = page.locator('.oe_login_buttons .btn')
        
        print(f"Login buttons found: {login_btn.count()}")
        login_btn.first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        print(f"After login URL: {page.url}")
        page.screenshot(path="c:/Odoo Study/report_screenshots/01_after_login.png", full_page=True)

        # ── 2. Navigate to Referrals app ──
        print("\nGoing to Referrals app...")
        page.goto(f"{URL}/odoo/referrals", wait_until="networkidle")
        time.sleep(4)
        page.screenshot(path="c:/Odoo Study/report_screenshots/01b_referrals_app.png", full_page=True)
        print(f"Referrals URL: {page.url}")

        # ── 3. Referral Analysis Report ──
        print("\n--- REFERRAL ANALYSIS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/analysis", wait_until="networkidle")
        time.sleep(5)
        page.screenshot(path="c:/Odoo Study/report_screenshots/02_referral_analysis.png", full_page=True)
        print(f"URL: {page.url}")

        # Get page title/breadcrumb
        bc = page.locator('.o_breadcrumb').all()
        if bc:
            print(f"Breadcrumb: {bc[0].text_content().strip()}")

        # Identify view type
        graph = page.locator('.o_graph_view').count()
        pivot = page.locator('.o_pivot').count()
        list_v = page.locator('.o_list_view').count()
        print(f"Views - Graph: {graph}, Pivot: {pivot}, List: {list_v}")

        # Check what view buttons are available
        switch_btns = page.locator('.o_cp_switch_buttons button').all()
        print(f"Switch buttons: {len(switch_btns)}")
        for i, btn in enumerate(switch_btns):
            tooltip = btn.get_attribute('data-tooltip') or btn.get_attribute('title') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            print(f"  Button {i}: tooltip='{tooltip}' active={active}")

        # Check graph type buttons (bar, line, pie)
        graph_btns = page.locator('.o_graph_buttons button, .btn-group button').all()
        for btn in graph_btns:
            tooltip = btn.get_attribute('data-tooltip') or btn.get_attribute('title') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            if tooltip:
                print(f"  Graph button: '{tooltip}' active={active}")

        # Check measures
        measures_btn = page.locator('button:has-text("Measures")').first
        if measures_btn.count() > 0:
            measures_btn.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/02b_analysis_measures.png", full_page=True)
            items = page.locator('.o-dropdown--menu .o_menu_item, .dropdown-menu .dropdown-item').all()
            print("Measures available:")
            for item in items:
                txt = item.text_content().strip()
                checked = item.locator('.fa-check, .bi-check').count() > 0
                if txt:
                    print(f"  {'[x]' if checked else '[ ]'} {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Switch to pivot
        for btn in switch_btns:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip or 'pivot' in tooltip:
                print("\nSwitching to Pivot view...")
                btn.click()
                time.sleep(3)
                page.screenshot(path="c:/Odoo Study/report_screenshots/02c_analysis_pivot.png", full_page=True)
                
                # Read pivot table content
                pivot_table = page.locator('.o_pivot table')
                if pivot_table.count() > 0:
                    print(f"Pivot table content:\n{pivot_table.text_content()[:600]}")
                break

        # ── 4. Points Report ──
        print("\n\n--- POINTS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/points", wait_until="networkidle")
        time.sleep(5)
        page.screenshot(path="c:/Odoo Study/report_screenshots/03_points_report.png", full_page=True)
        print(f"URL: {page.url}")

        bc2 = page.locator('.o_breadcrumb').all()
        if bc2:
            print(f"Breadcrumb: {bc2[0].text_content().strip()}")

        graph2 = page.locator('.o_graph_view').count()
        pivot2 = page.locator('.o_pivot').count()
        list_v2 = page.locator('.o_list_view').count()
        print(f"Views - Graph: {graph2}, Pivot: {pivot2}, List: {list_v2}")

        # Get list/table content
        if list_v2 > 0:
            print("DEFAULT VIEW: List")
            # Group headers
            groups = page.locator('.o_group_header').all()
            print(f"Group headers: {len(groups)}")
            for g in groups:
                print(f"  Group: {g.text_content().strip()}")
            
            # Expand all groups
            for g in groups:
                g.click()
                time.sleep(0.5)
            
            page.screenshot(path="c:/Odoo Study/report_screenshots/03b_points_expanded.png", full_page=True)
            
            # Read all rows
            rows = page.locator('.o_data_row').all()
            print(f"Data rows: {len(rows)}")
            for row in rows:
                cells = row.locator('td').all()
                cell_texts = [c.text_content().strip() for c in cells]
                print(f"  Row: {cell_texts}")

            # Column headers
            headers = page.locator('thead th').all()
            header_texts = [h.text_content().strip() for h in headers]
            print(f"Column headers: {header_texts}")

        elif graph2 > 0:
            print("DEFAULT VIEW: Graph")

        # ── 5. Rewards Report ──
        print("\n\n--- REWARDS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/rewards", wait_until="networkidle")
        time.sleep(5)
        page.screenshot(path="c:/Odoo Study/report_screenshots/04_rewards_report.png", full_page=True)
        print(f"URL: {page.url}")

        bc3 = page.locator('.o_breadcrumb').all()
        if bc3:
            print(f"Breadcrumb: {bc3[0].text_content().strip()}")

        graph3 = page.locator('.o_graph_view').count()
        pivot3 = page.locator('.o_pivot').count()
        list_v3 = page.locator('.o_list_view').count()
        print(f"Views - Graph: {graph3}, Pivot: {pivot3}, List: {list_v3}")

        # Check graph type
        switch_btns3 = page.locator('.o_cp_switch_buttons button').all()
        print(f"Switch buttons: {len(switch_btns3)}")
        for i, btn in enumerate(switch_btns3):
            tooltip = btn.get_attribute('data-tooltip') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            print(f"  Button {i}: tooltip='{tooltip}' active={active}")

        # Check measures for rewards
        measures_btn3 = page.locator('button:has-text("Measures")').first
        if measures_btn3.count() > 0:
            measures_btn3.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/04b_rewards_measures.png", full_page=True)
            items3 = page.locator('.o-dropdown--menu .o_menu_item, .dropdown-menu .dropdown-item').all()
            print("Measures available:")
            for item in items3:
                txt = item.text_content().strip()
                checked = item.locator('.fa-check, .bi-check').count() > 0
                if txt:
                    print(f"  {'[x]' if checked else '[ ]'} {txt}")
            page.keyboard.press("Escape")

        # Switch to pivot for rewards
        for btn in switch_btns3:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip or 'pivot' in tooltip:
                print("\nSwitching to Pivot view...")
                btn.click()
                time.sleep(3)
                page.screenshot(path="c:/Odoo Study/report_screenshots/04c_rewards_pivot.png", full_page=True)
                pivot_table3 = page.locator('.o_pivot table')
                if pivot_table3.count() > 0:
                    print(f"Pivot content:\n{pivot_table3.text_content()[:600]}")
                break

        # Switch to list for rewards
        for btn in switch_btns3:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'List' in tooltip or 'list' in tooltip:
                print("\nSwitching to List view...")
                btn.click()
                time.sleep(3)
                page.screenshot(path="c:/Odoo Study/report_screenshots/04d_rewards_list.png", full_page=True)
                
                rows3 = page.locator('.o_data_row').all()
                print(f"Data rows: {len(rows3)}")
                for row in rows3:
                    cells = row.locator('td').all()
                    cell_texts = [c.text_content().strip() for c in cells]
                    print(f"  Row: {cell_texts}")

                headers3 = page.locator('thead th').all()
                header_texts3 = [h.text_content().strip() for h in headers3]
                print(f"Column headers: {header_texts3}")
                break

        print("\n" + "=" * 70)
        print("ALL REPORTS CHECKED")
        print("=" * 70)

        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/report_screenshots", exist_ok=True)
    main()
