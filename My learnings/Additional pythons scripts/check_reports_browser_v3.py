#!/usr/bin/env python3
"""
Open demo-tech.odoo.com Referrals reports in browser, take screenshots. V3 - fixed waits.
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

        # ── 1. Login ──
        print("Navigating to login page...")
        page.goto(f"{URL}/web/login", wait_until="load")
        time.sleep(3)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        
        login_btn = page.locator('.oe_login_buttons button[type="submit"]')
        print(f"Login buttons found: {login_btn.count()}")
        login_btn.first.click()
        
        # Wait for navigation after login
        page.wait_for_url("**/odoo**", timeout=60000)
        time.sleep(5)
        print(f"After login URL: {page.url}")
        page.screenshot(path="c:/Odoo Study/report_screenshots/01_after_login.png", full_page=True)

        # ── 2. Referral Analysis Report ──
        print("\n--- REFERRAL ANALYSIS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/analysis", wait_until="load")
        time.sleep(8)
        page.screenshot(path="c:/Odoo Study/report_screenshots/02_referral_analysis.png", full_page=True)
        print(f"URL: {page.url}")

        # Breadcrumb
        bc = page.locator('.o_breadcrumb')
        if bc.count() > 0:
            print(f"Breadcrumb: {bc.first.text_content().strip()}")

        # View type
        graph = page.locator('.o_graph_view').count()
        print(f"Graph view present: {graph > 0}")

        # View switch buttons
        switch_btns = page.locator('.o_cp_switch_buttons button').all()
        print(f"Switch buttons: {len(switch_btns)}")
        for i, btn in enumerate(switch_btns):
            tooltip = btn.get_attribute('data-tooltip') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            print(f"  [{i}] '{tooltip}' active={active}")

        # Graph sub-type buttons (bar/line/pie and stacked/descending/ascending)
        graph_mode_btns = page.locator('.o_graph_buttons button').all()
        if not graph_mode_btns:
            graph_mode_btns = page.locator('.o_control_panel .btn-group button').all()
        print(f"Graph mode buttons: {len(graph_mode_btns)}")
        for btn in graph_mode_btns:
            tooltip = btn.get_attribute('data-tooltip') or btn.get_attribute('aria-label') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            if tooltip:
                print(f"  Graph: '{tooltip}' active={active}")

        # Check filter/groupby
        search_items = page.locator('.o_searchview_facet').all()
        print(f"Active filters/groupby: {len(search_items)}")
        for si in search_items:
            print(f"  Filter: {si.text_content().strip()}")

        # Measures dropdown
        measures_btn = page.locator('button:has-text("Measures")').first
        if measures_btn.is_visible():
            measures_btn.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/02b_analysis_measures.png", full_page=True)
            items = page.locator('.o-dropdown--menu .o_menu_item, .o-dropdown--menu .dropdown-item').all()
            if not items:
                items = page.locator('.dropdown-menu .dropdown-item, .dropdown-menu .o_menu_item').all()
            print("Measures:")
            for item in items:
                txt = item.text_content().strip()
                checked = item.locator('.fa-check, .bi-check, i.oi-check').count() > 0
                if txt:
                    print(f"  {'[x]' if checked else '[ ]'} {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Switch to pivot
        for btn in switch_btns:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip:
                print("\nSwitching to Pivot view...")
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/02c_analysis_pivot.png", full_page=True)
                pivot_table = page.locator('.o_pivot table')
                if pivot_table.count() > 0:
                    print(f"Pivot content:\n{pivot_table.text_content()[:800]}")
                break

        # ── 3. Points Report ──
        print("\n\n--- POINTS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/points", wait_until="load")
        time.sleep(8)
        page.screenshot(path="c:/Odoo Study/report_screenshots/03_points_report.png", full_page=True)
        print(f"URL: {page.url}")

        bc2 = page.locator('.o_breadcrumb')
        if bc2.count() > 0:
            print(f"Breadcrumb: {bc2.first.text_content().strip()}")

        list_v2 = page.locator('.o_list_view').count()
        graph2 = page.locator('.o_graph_view').count()
        print(f"List view: {list_v2 > 0}, Graph view: {graph2 > 0}")

        if list_v2 > 0:
            print("DEFAULT VIEW: List")
            # Column headers
            headers = page.locator('.o_list_view thead th').all()
            header_texts = [h.text_content().strip() for h in headers if h.text_content().strip()]
            print(f"Columns: {header_texts}")

            # Group headers
            groups = page.locator('.o_group_header').all()
            print(f"Group headers ({len(groups)}):")
            for g in groups:
                print(f"  {g.text_content().strip()}")

            # Expand all groups
            for g in page.locator('.o_group_header').all():
                try:
                    g.click()
                    time.sleep(0.5)
                except:
                    pass

            page.screenshot(path="c:/Odoo Study/report_screenshots/03b_points_expanded.png", full_page=True)

            # Read all data rows
            rows = page.locator('.o_data_row').all()
            print(f"\nData rows ({len(rows)}):")
            for row in rows:
                cells = row.locator('td').all()
                cell_texts = [c.text_content().strip() for c in cells]
                print(f"  {cell_texts}")

        # ── 4. Rewards Report ──
        print("\n\n--- REWARDS REPORT ---")
        page.goto(f"{URL}/odoo/referrals/reporting/rewards", wait_until="load")
        time.sleep(8)
        page.screenshot(path="c:/Odoo Study/report_screenshots/04_rewards_report.png", full_page=True)
        print(f"URL: {page.url}")

        bc3 = page.locator('.o_breadcrumb')
        if bc3.count() > 0:
            print(f"Breadcrumb: {bc3.first.text_content().strip()}")

        graph3 = page.locator('.o_graph_view').count()
        list_v3 = page.locator('.o_list_view').count()
        print(f"Graph view: {graph3 > 0}, List view: {list_v3 > 0}")

        # View switch buttons
        switch_btns3 = page.locator('.o_cp_switch_buttons button').all()
        print(f"Switch buttons: {len(switch_btns3)}")
        for i, btn in enumerate(switch_btns3):
            tooltip = btn.get_attribute('data-tooltip') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            print(f"  [{i}] '{tooltip}' active={active}")

        # Graph sub-type
        graph_mode_btns3 = page.locator('.o_graph_buttons button').all()
        for btn in graph_mode_btns3:
            tooltip = btn.get_attribute('data-tooltip') or btn.get_attribute('aria-label') or ''
            classes = btn.get_attribute('class') or ''
            active = 'active' in classes
            if tooltip:
                print(f"  Graph: '{tooltip}' active={active}")

        # Measures for rewards
        measures_btn3 = page.locator('button:has-text("Measures")').first
        if measures_btn3.is_visible():
            measures_btn3.click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/04b_rewards_measures.png", full_page=True)
            items3 = page.locator('.o-dropdown--menu .o_menu_item, .o-dropdown--menu .dropdown-item').all()
            if not items3:
                items3 = page.locator('.dropdown-menu .dropdown-item, .dropdown-menu .o_menu_item').all()
            print("Measures:")
            for item in items3:
                txt = item.text_content().strip()
                checked = item.locator('.fa-check, .bi-check, i.oi-check').count() > 0
                if txt:
                    print(f"  {'[x]' if checked else '[ ]'} {txt}")
            page.keyboard.press("Escape")

        # Switch to pivot
        for btn in switch_btns3:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'Pivot' in tooltip:
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/04c_rewards_pivot.png", full_page=True)
                pivot3 = page.locator('.o_pivot table')
                if pivot3.count() > 0:
                    print(f"\nRewards Pivot:\n{pivot3.text_content()[:600]}")
                break

        # Switch to list
        for btn in switch_btns3:
            tooltip = btn.get_attribute('data-tooltip') or ''
            if 'List' in tooltip:
                btn.click()
                time.sleep(4)
                page.screenshot(path="c:/Odoo Study/report_screenshots/04d_rewards_list.png", full_page=True)
                
                headers3 = page.locator('.o_list_view thead th').all()
                header_texts3 = [h.text_content().strip() for h in headers3 if h.text_content().strip()]
                print(f"\nRewards List columns: {header_texts3}")

                rows3 = page.locator('.o_data_row').all()
                print(f"Data rows ({len(rows3)}):")
                for row in rows3:
                    cells = row.locator('td').all()
                    cell_texts = [c.text_content().strip() for c in cells]
                    print(f"  {cell_texts}")
                break

        print("\n" + "=" * 70)
        print("ALL REPORTS CHECKED")
        print("=" * 70)

        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/report_screenshots", exist_ok=True)
    main()
