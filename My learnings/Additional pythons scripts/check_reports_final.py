#!/usr/bin/env python3
"""
Click the actual measures dropdown (o_report_measures) and get all items.
Do it for Referral Analysis (graph & pivot) and Rewards.
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

        # ── REFERRAL ANALYSIS ── GRAPH VIEW ──
        print("=" * 60)
        print("REFERRAL ANALYSIS — GRAPH VIEW")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(8)

        # Current measure shown
        measures_btn = page.locator('.o_report_measures').first
        current_measure = measures_btn.text_content().strip()
        print(f"Default measure: {current_measure}")

        # Active filter
        facets = page.locator('.o_searchview_facet').all()
        for f in facets:
            print(f"Active filter: {f.text_content().strip()}")

        # Chart type
        for chart_type in ['Bar Chart', 'Line Chart', 'Pie Chart', 'Stacked']:
            btn = page.locator(f'button[aria-label="{chart_type}"]')
            if btn.count() > 0:
                cls = btn.first.get_attribute('class') or ''
                active = 'ACTIVE' if 'active' in cls else 'inactive'
                print(f"  {chart_type}: {active}")

        # Click measures dropdown
        measures_btn.click()
        time.sleep(2)
        
        # Get dropdown items
        dropdown_items = page.locator('.o-dropdown--menu .o-dropdown-item, .dropdown-menu .dropdown-item').all()
        print(f"\nMeasures dropdown ({len(dropdown_items)} items):")
        for item in dropdown_items:
            txt = item.text_content().strip()
            cls = item.get_attribute('class') or ''
            selected = ' ✓ SELECTED' if 'selected' in cls or 'active' in cls else ''
            print(f"  - {txt}{selected}")

        # Also try role=menuitemcheckbox
        checkboxes = page.locator('[role="menuitemcheckbox"]').all()
        if checkboxes:
            print(f"\n  menuitemcheckbox items ({len(checkboxes)}):")
            for cb in checkboxes:
                txt = cb.text_content().strip()
                checked = cb.get_attribute('aria-checked') or 'false'
                print(f"    - {txt} (checked={checked})")

        page.keyboard.press("Escape")
        time.sleep(1)

        # ── REFERRAL ANALYSIS — PIVOT VIEW ──
        print("\n" + "=" * 60)
        print("REFERRAL ANALYSIS — PIVOT VIEW")
        print("=" * 60)
        page.locator('button[aria-label="Pivot View"]').first.click()
        time.sleep(5)

        measures_btn2 = page.locator('.o_report_measures').first
        current_measure2 = measures_btn2.text_content().strip()
        print(f"Default measure: {current_measure2}")

        measures_btn2.click()
        time.sleep(2)

        dropdown_items2 = page.locator('.o-dropdown--menu .o-dropdown-item, .dropdown-menu .dropdown-item').all()
        print(f"\nMeasures dropdown ({len(dropdown_items2)} items):")
        for item in dropdown_items2:
            txt = item.text_content().strip()
            cls = item.get_attribute('class') or ''
            selected = ' ✓ SELECTED' if 'selected' in cls or 'active' in cls else ''
            print(f"  - {txt}{selected}")

        checkboxes2 = page.locator('[role="menuitemcheckbox"]').all()
        if checkboxes2:
            print(f"\n  menuitemcheckbox items ({len(checkboxes2)}):")
            for cb in checkboxes2:
                txt = cb.text_content().strip()
                checked = cb.get_attribute('aria-checked') or 'false'
                print(f"    - {txt} (checked={checked})")

        # Get pivot table headers and data
        print("\nPivot table content:")
        headers = page.locator('.o_pivot_header_cell_closed, .o_pivot_header_cell_opened, th.o_pivot_measure_row').all()
        print(f"  Headers ({len(headers)}):")
        for h in headers:
            print(f"    {h.text_content().strip()}")

        rows = page.locator('tr').all()
        for row in rows:
            cells = row.locator('td, th').all()
            vals = [c.text_content().strip() for c in cells if c.text_content().strip()]
            if vals:
                print(f"  Row: {vals}")

        page.keyboard.press("Escape")
        time.sleep(1)

        # ── REWARDS REPORT ── GRAPH VIEW ──
        print("\n" + "=" * 60)
        print("REWARDS — GRAPH VIEW")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(8)

        measures_btn3 = page.locator('.o_report_measures').first
        current_measure3 = measures_btn3.text_content().strip()
        print(f"Default measure: {current_measure3}")

        facets3 = page.locator('.o_searchview_facet').all()
        for f in facets3:
            print(f"Active filter: {f.text_content().strip()}")

        for chart_type in ['Bar Chart', 'Line Chart', 'Pie Chart', 'Stacked']:
            btn = page.locator(f'button[aria-label="{chart_type}"]')
            if btn.count() > 0:
                cls = btn.first.get_attribute('class') or ''
                active = 'ACTIVE' if 'active' in cls else 'inactive'
                print(f"  {chart_type}: {active}")

        measures_btn3.click()
        time.sleep(2)

        dropdown_items3 = page.locator('.o-dropdown--menu .o-dropdown-item, .dropdown-menu .dropdown-item').all()
        print(f"\nMeasures dropdown ({len(dropdown_items3)} items):")
        for item in dropdown_items3:
            txt = item.text_content().strip()
            cls = item.get_attribute('class') or ''
            selected = ' ✓ SELECTED' if 'selected' in cls or 'active' in cls else ''
            print(f"  - {txt}{selected}")

        checkboxes3 = page.locator('[role="menuitemcheckbox"]').all()
        if checkboxes3:
            print(f"\n  menuitemcheckbox items ({len(checkboxes3)}):")
            for cb in checkboxes3:
                txt = cb.text_content().strip()
                checked = cb.get_attribute('aria-checked') or 'false'
                print(f"    - {txt} (checked={checked})")

        page.keyboard.press("Escape")
        time.sleep(1)

        # ── REWARDS — PIVOT VIEW ──
        print("\n" + "=" * 60)
        print("REWARDS — PIVOT VIEW")
        print("=" * 60)
        page.locator('button[aria-label="Pivot View"]').first.click()
        time.sleep(5)

        measures_btn4 = page.locator('.o_report_measures').first
        current_measure4 = measures_btn4.text_content().strip()
        print(f"Default measure: {current_measure4}")

        measures_btn4.click()
        time.sleep(2)

        dropdown_items4 = page.locator('.o-dropdown--menu .o-dropdown-item, .dropdown-menu .dropdown-item').all()
        print(f"\nMeasures dropdown ({len(dropdown_items4)} items):")
        for item in dropdown_items4:
            txt = item.text_content().strip()
            cls = item.get_attribute('class') or ''
            selected = ' ✓ SELECTED' if 'selected' in cls or 'active' in cls else ''
            print(f"  - {txt}{selected}")

        checkboxes4 = page.locator('[role="menuitemcheckbox"]').all()
        if checkboxes4:
            print(f"\n  menuitemcheckbox items ({len(checkboxes4)}):")
            for cb in checkboxes4:
                txt = cb.text_content().strip()
                checked = cb.get_attribute('aria-checked') or 'false'
                print(f"    - {txt} (checked={checked})")

        # Pivot headers and data
        print("\nPivot table content:")
        rows2 = page.locator('tr').all()
        for row in rows2:
            cells = row.locator('td, th').all()
            vals = [c.text_content().strip() for c in cells if c.text_content().strip()]
            if vals:
                print(f"  Row: {vals}")

        page.keyboard.press("Escape")
        time.sleep(1)

        # ── POINTS REPORT ──
        print("\n" + "=" * 60)
        print("POINTS — LIST VIEW")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Points")').first.click()
        time.sleep(8)

        # View switches available
        switch_btns = page.locator('.o_switch_view').all()
        print(f"Available views: {len(switch_btns)}")
        for sb in switch_btns:
            label = sb.get_attribute('aria-label') or ''
            cls = sb.get_attribute('class') or ''
            active = 'ACTIVE' if 'active' in cls else 'inactive'
            print(f"  - {label}: {active}")

        # Active filters
        facets5 = page.locator('.o_searchview_facet').all()
        for f in facets5:
            print(f"Active filter: {f.text_content().strip()}")

        # Column headers
        headers5 = page.locator('th.o_column_sortable, th').all()
        print(f"\nColumns ({len(headers5)}):")
        for h in headers5:
            txt = h.text_content().strip()
            if txt:
                print(f"  - {txt}")

        # Group headers
        groups = page.locator('.o_group_header').all()
        print(f"\nGroup rows ({len(groups)}):")
        for g in groups:
            txt = g.text_content().strip()
            print(f"  {txt}")

        # Data rows (first 15)
        data_rows = page.locator('.o_data_row').all()
        print(f"\nData rows ({len(data_rows)} total, showing first 15):")
        for row in data_rows[:15]:
            cells = row.locator('td').all()
            vals = [c.text_content().strip() for c in cells]
            print(f"  {vals}")

        # Check GroupBy options
        print("\n--- GroupBy Options ---")
        # Click the search panel toggle
        toggle = page.locator('[title="Toggle Search Panel"]')
        if toggle.count() > 0 and toggle.first.is_visible():
            toggle.first.click()
            time.sleep(2)
            # Check for GroupBy
            groupby_section = page.locator('.o_search_panel, .o_group_by_menu')
            if groupby_section.count() > 0:
                html = groupby_section.first.inner_html()
                print(f"  Search panel: {html[:1000]}")

        print("\n=== ALL DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
