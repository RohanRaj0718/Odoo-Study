#!/usr/bin/env python3
"""
Navigate through the Referrals app menus to find the correct report URLs.
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
        print("Logging in...")
        page.goto(f"{URL}/web/login", wait_until="load")
        time.sleep(3)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.locator('.oe_login_buttons button[type="submit"]').first.click()
        page.wait_for_url("**/odoo**", timeout=60000)
        time.sleep(5)
        print(f"Logged in: {page.url}")

        # Go to referrals
        page.goto(f"{URL}/odoo/referrals", wait_until="load")
        time.sleep(5)
        page.screenshot(path="c:/Odoo Study/report_screenshots/10_referrals_home.png", full_page=True)

        # Look for the Reporting menu
        print("\nLooking for menu items...")
        
        # Check top-level menu bar items
        menu_items = page.locator('.o_menu_sections .dropdown-toggle, .o_menu_sections a, .o_menu_sections button').all()
        print(f"Top menu items: {len(menu_items)}")
        for mi in menu_items:
            txt = mi.text_content().strip()
            if txt:
                print(f"  Menu: '{txt}'")

        # Click on "Reporting" menu
        reporting_menu = page.locator('button:has-text("Reporting"), a:has-text("Reporting")').first
        if reporting_menu.is_visible():
            print("\nClicking 'Reporting' menu...")
            reporting_menu.click()
            time.sleep(2)
            page.screenshot(path="c:/Odoo Study/report_screenshots/11_reporting_dropdown.png", full_page=True)

            # Get dropdown items
            dropdown_items = page.locator('.dropdown-menu.show .dropdown-item, .o-dropdown--menu .dropdown-item').all()
            print(f"Reporting sub-items: {len(dropdown_items)}")
            for di in dropdown_items:
                txt = di.text_content().strip()
                href = di.get_attribute('href') or ''
                print(f"  Sub-menu: '{txt}' href='{href}'")

            # Click "Referral Analysis"
            ref_analysis = page.locator('.dropdown-item:has-text("Referral Analysis"), .dropdown-item:has-text("Analysis")').first
            if ref_analysis.is_visible():
                print("\nClicking 'Referral Analysis'...")
                ref_analysis.click()
                time.sleep(6)
                print(f"Referral Analysis URL: {page.url}")
                page.screenshot(path="c:/Odoo Study/report_screenshots/12_referral_analysis.png", full_page=True)

                # Inspect the actual view
                graph = page.locator('.o_graph_view').count()
                print(f"Graph view: {graph > 0}")

                # View switch buttons
                switch_btns = page.locator('.o_cp_switch_buttons button').all()
                print(f"Switch buttons: {len(switch_btns)}")
                for i, btn in enumerate(switch_btns):
                    tooltip = btn.get_attribute('data-tooltip') or ''
                    classes = btn.get_attribute('class') or ''
                    active = 'active' in classes
                    print(f"  [{i}] '{tooltip}' active={active}")

                # Graph sub-type buttons
                all_btns = page.locator('button').all()
                for btn in all_btns:
                    tooltip = btn.get_attribute('data-tooltip') or ''
                    classes = btn.get_attribute('class') or ''
                    aria = btn.get_attribute('aria-label') or ''
                    if ('active' in classes and tooltip) or ('graph' in classes.lower()):
                        print(f"  Active/Graph btn: tooltip='{tooltip}' aria='{aria}' class partial")

                # Check for chart type indicators in the DOM
                bar_active = page.locator('button[data-tooltip="Bar Chart"]').count()
                line_active = page.locator('button[data-tooltip="Line Chart"]').count()
                pie_active = page.locator('button[data-tooltip="Pie Chart"]').count()
                stacked = page.locator('button[data-tooltip="Stacked"]').count()
                print(f"\nChart buttons - Bar: {bar_active}, Line: {line_active}, Pie: {pie_active}, Stacked: {stacked}")

                # Check active state
                for label in ["Bar Chart", "Line Chart", "Pie Chart", "Stacked", "Descending", "Ascending"]:
                    btn = page.locator(f'button[data-tooltip="{label}"]')
                    if btn.count() > 0:
                        classes = btn.first.get_attribute('class') or ''
                        active = 'active' in classes
                        print(f"  {label}: active={active}")

                # Active search filters
                facets = page.locator('.o_searchview_facet').all()
                print(f"\nActive filters: {len(facets)}")
                for f in facets:
                    print(f"  {f.text_content().strip()}")

                # Measures
                measures_btn = page.locator('button:has-text("Measures")').first
                if measures_btn.is_visible():
                    measures_btn.click()
                    time.sleep(1)
                    page.screenshot(path="c:/Odoo Study/report_screenshots/12b_analysis_measures.png", full_page=True)
                    items = page.locator('.o-dropdown--menu .o_menu_item').all()
                    if not items:
                        items = page.locator('.dropdown-menu.show .dropdown-item').all()
                    print("Measures:")
                    for item in items:
                        txt = item.text_content().strip()
                        # Check for checkmark
                        check = item.locator('i').count()
                        if txt:
                            print(f"  {txt} (has icon: {check > 0})")
                    page.keyboard.press("Escape")
                    time.sleep(0.5)

        # Go back to Reporting menu for Points
        reporting_menu2 = page.locator('button:has-text("Reporting"), a:has-text("Reporting")').first
        if reporting_menu2.is_visible():
            reporting_menu2.click()
            time.sleep(2)
            
            points_item = page.locator('.dropdown-item:has-text("Points")').first
            if points_item.is_visible():
                print("\n\nClicking 'Points'...")
                points_item.click()
                time.sleep(6)
                print(f"Points Report URL: {page.url}")
                page.screenshot(path="c:/Odoo Study/report_screenshots/13_points_report.png", full_page=True)

                list_v = page.locator('.o_list_view').count()
                graph_v = page.locator('.o_graph_view').count()
                print(f"List view: {list_v > 0}, Graph view: {graph_v > 0}")

                # Headers
                headers = page.locator('.o_list_view thead th').all()
                header_texts = [h.text_content().strip() for h in headers if h.text_content().strip()]
                print(f"Columns: {header_texts}")

                # Groups
                groups = page.locator('.o_group_header').all()
                print(f"Group headers ({len(groups)}):")
                for g in groups:
                    print(f"  {g.text_content().strip()}")

                # Expand groups
                for g in page.locator('.o_group_header').all():
                    try:
                        g.click()
                        time.sleep(0.5)
                    except:
                        pass
                
                page.screenshot(path="c:/Odoo Study/report_screenshots/13b_points_expanded.png", full_page=True)

                rows = page.locator('.o_data_row').all()
                print(f"\nData rows ({len(rows)}):")
                for row in rows:
                    cells = row.locator('td').all()
                    cell_texts = [c.text_content().strip() for c in cells]
                    print(f"  {cell_texts}")

        # Go back to Reporting menu for Rewards
        reporting_menu3 = page.locator('button:has-text("Reporting"), a:has-text("Reporting")').first
        if reporting_menu3.is_visible():
            reporting_menu3.click()
            time.sleep(2)
            
            rewards_item = page.locator('.dropdown-item:has-text("Rewards")').first
            if rewards_item.is_visible():
                print("\n\nClicking 'Rewards'...")
                rewards_item.click()
                time.sleep(6)
                print(f"Rewards Report URL: {page.url}")
                page.screenshot(path="c:/Odoo Study/report_screenshots/14_rewards_report.png", full_page=True)

                graph3 = page.locator('.o_graph_view').count()
                list3 = page.locator('.o_list_view').count()
                print(f"Graph view: {graph3 > 0}, List view: {list3 > 0}")

                # Chart type
                for label in ["Bar Chart", "Line Chart", "Pie Chart", "Stacked", "Descending", "Ascending"]:
                    btn = page.locator(f'button[data-tooltip="{label}"]')
                    if btn.count() > 0:
                        classes = btn.first.get_attribute('class') or ''
                        active = 'active' in classes
                        print(f"  {label}: active={active}")

                # Filters
                facets3 = page.locator('.o_searchview_facet').all()
                print(f"Active filters: {len(facets3)}")
                for f in facets3:
                    print(f"  {f.text_content().strip()}")

                # X-axis / groupby info from DOM
                # The graph x-axis labels
                canvas = page.locator('canvas').count()
                print(f"Canvas elements (charts): {canvas}")

                # Switch to pivot to see actual data
                switch_btns3 = page.locator('.o_cp_switch_buttons button').all()
                for btn in switch_btns3:
                    tooltip = btn.get_attribute('data-tooltip') or ''
                    if 'Pivot' in tooltip:
                        btn.click()
                        time.sleep(4)
                        page.screenshot(path="c:/Odoo Study/report_screenshots/14b_rewards_pivot.png", full_page=True)
                        pivot3 = page.locator('.o_pivot table')
                        if pivot3.count() > 0:
                            print(f"\nRewards Pivot:\n{pivot3.text_content()[:800]}")
                        break

                # Also list view
                for btn in switch_btns3:
                    tooltip = btn.get_attribute('data-tooltip') or ''
                    if 'List' in tooltip:
                        btn.click()
                        time.sleep(4)
                        page.screenshot(path="c:/Odoo Study/report_screenshots/14c_rewards_list.png", full_page=True)
                        
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
        print("COMPLETE")
        print("=" * 70)
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/report_screenshots", exist_ok=True)
    main()
