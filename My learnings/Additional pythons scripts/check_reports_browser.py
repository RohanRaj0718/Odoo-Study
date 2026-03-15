#!/usr/bin/env python3
"""
Open the demo-tech.odoo.com Referrals reports in a browser and take screenshots
of all three report pages to verify what's actually shown.
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
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        print(f"Logged in. Current URL: {page.url}")
        page.screenshot(path="c:/Odoo Study/report_screenshots/01_logged_in.png", full_page=True)

        # ── 2. Referral Analysis Report ──
        print("\nNavigating to Referral Analysis report...")
        page.goto(f"{URL}/odoo/referrals/reporting/analysis", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path="c:/Odoo Study/report_screenshots/02_referral_analysis.png", full_page=True)
        print(f"Referral Analysis URL: {page.url}")
        
        # Get the page content to understand what's displayed
        content = page.content()
        # Look for chart type indicators
        chart_elements = page.locator('.o_graph_renderer').all()
        print(f"Graph renderers found: {len(chart_elements)}")
        
        # Check for any visible text/labels
        visible_text = page.locator('.o_graph_canvas_container').all()
        print(f"Graph canvas containers: {len(visible_text)}")

        # Check breadcrumb / title
        breadcrumb = page.locator('.o_breadcrumb').text_content() if page.locator('.o_breadcrumb').count() > 0 else "N/A"
        print(f"Breadcrumb: {breadcrumb}")

        # Check view switcher buttons
        view_buttons = page.locator('.o_cp_switch_buttons button').all()
        active_view = [b.get_attribute('class') for b in view_buttons]
        print(f"View buttons: {active_view}")

        # Check measures
        measures_btn = page.locator('button:has-text("Measures")').all()
        if measures_btn:
            measures_btn[0].click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/02b_referral_analysis_measures.png", full_page=True)
            # Get dropdown items
            measure_items = page.locator('.o_menu_item, .dropdown-item').all()
            print("Available measures:")
            for item in measure_items:
                txt = item.text_content().strip()
                if txt:
                    print(f"  - {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Try pivot view
        pivot_btn = page.locator('button[data-tooltip="Pivot"]').all()
        if not pivot_btn:
            pivot_btn = page.locator('button.o_pivot').all()
        if not pivot_btn:
            pivot_btn = page.locator('.o_cp_switch_buttons button').all()
            if len(pivot_btn) >= 3:
                pivot_btn = [pivot_btn[2]]  # Usually 3rd button is pivot
        
        if pivot_btn:
            print("\nSwitching to Pivot view...")
            pivot_btn[0].click()
            time.sleep(2)
            page.screenshot(path="c:/Odoo Study/report_screenshots/02c_referral_analysis_pivot.png", full_page=True)

        # Try list view
        list_btn = page.locator('button[data-tooltip="List"]').all()
        if not list_btn:
            list_btn = page.locator('.o_cp_switch_buttons button').all()
            if len(list_btn) >= 4:
                list_btn = [list_btn[3]]

        # ── 3. Points Report ──
        print("\nNavigating to Points report...")
        page.goto(f"{URL}/odoo/referrals/reporting/points", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path="c:/Odoo Study/report_screenshots/03_points_report.png", full_page=True)
        print(f"Points Report URL: {page.url}")

        breadcrumb2 = page.locator('.o_breadcrumb').text_content() if page.locator('.o_breadcrumb').count() > 0 else "N/A"
        print(f"Breadcrumb: {breadcrumb2}")

        # Check what type of view this is
        list_view = page.locator('.o_list_view').all()
        graph_view = page.locator('.o_graph_view').all()
        pivot_view = page.locator('.o_pivot_view').all()
        print(f"List view present: {len(list_view) > 0}")
        print(f"Graph view present: {len(graph_view) > 0}")
        print(f"Pivot view present: {len(pivot_view) > 0}")

        # Get visible table data if list view
        if list_view:
            rows = page.locator('.o_list_view .o_data_row').all()
            print(f"Data rows: {len(rows)}")
            group_rows = page.locator('.o_list_view .o_group_header').all()
            print(f"Group headers: {len(group_rows)}")
            for gr in group_rows:
                print(f"  Group: {gr.text_content().strip()}")

        # Try expanding groups
        for gr in page.locator('.o_list_view .o_group_header').all():
            gr.click()
            time.sleep(1)
        page.screenshot(path="c:/Odoo Study/report_screenshots/03b_points_expanded.png", full_page=True)

        # Get all visible text from table
        table_text = page.locator('.o_list_view table').text_content() if page.locator('.o_list_view table').count() > 0 else "N/A"
        print(f"Table content: {table_text[:500]}")

        # ── 4. Rewards Report ──
        print("\nNavigating to Rewards report...")
        page.goto(f"{URL}/odoo/referrals/reporting/rewards", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path="c:/Odoo Study/report_screenshots/04_rewards_report.png", full_page=True)
        print(f"Rewards Report URL: {page.url}")

        breadcrumb3 = page.locator('.o_breadcrumb').text_content() if page.locator('.o_breadcrumb').count() > 0 else "N/A"
        print(f"Breadcrumb: {breadcrumb3}")

        # Check view type
        list_view3 = page.locator('.o_list_view').all()
        graph_view3 = page.locator('.o_graph_view').all()
        pivot_view3 = page.locator('.o_pivot_view').all()
        print(f"List view present: {len(list_view3) > 0}")
        print(f"Graph view present: {len(graph_view3) > 0}")
        print(f"Pivot view present: {len(pivot_view3) > 0}")

        # Check measures for rewards
        measures_btn3 = page.locator('button:has-text("Measures")').all()
        if measures_btn3:
            measures_btn3[0].click()
            time.sleep(1)
            page.screenshot(path="c:/Odoo Study/report_screenshots/04b_rewards_measures.png", full_page=True)
            measure_items3 = page.locator('.o_menu_item, .dropdown-item').all()
            print("Available measures:")
            for item in measure_items3:
                txt = item.text_content().strip()
                if txt:
                    print(f"  - {txt}")
            page.keyboard.press("Escape")
            time.sleep(0.5)

        # Try pivot view for rewards
        pivot_btn3 = page.locator('.o_cp_switch_buttons button').all()
        if len(pivot_btn3) >= 2:
            pivot_btn3[1].click()  # Try pivot
            time.sleep(2)
            page.screenshot(path="c:/Odoo Study/report_screenshots/04c_rewards_pivot.png", full_page=True)
            
            pivot_text = page.locator('.o_pivot table').text_content() if page.locator('.o_pivot table').count() > 0 else "N/A"
            print(f"Pivot content: {pivot_text[:500]}")

        # Also try list view
        if len(pivot_btn3) >= 3:
            pivot_btn3[2].click()
            time.sleep(2)
            page.screenshot(path="c:/Odoo Study/report_screenshots/04d_rewards_list.png", full_page=True)
            
            list_text = page.locator('.o_list_view table').text_content() if page.locator('.o_list_view table').count() > 0 else "N/A"
            print(f"List content: {list_text[:500]}")

        print("\n" + "=" * 70)
        print("ALL SCREENSHOTS CAPTURED")
        print("=" * 70)

        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/report_screenshots", exist_ok=True)
    main()
