#!/usr/bin/env python3
"""
Check the actual default GroupBy on Referral Analysis graph.
Look at x-axis labels and the active GroupBy filter.
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
        print("=" * 60)
        print("REFERRAL ANALYSIS — DEFAULT STATE")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(8)

        # 1. Check ALL active search facets (filters + groupbys)
        facets = page.locator('.o_searchview_facet').all()
        print(f"Active facets ({len(facets)}):")
        for f in facets:
            txt = f.text_content().strip()
            # Check if it's a filter or groupby
            icon = f.locator('.o_searchview_facet_label i')
            icon_class = ''
            if icon.count() > 0:
                icon_class = icon.first.get_attribute('class') or ''
            print(f"  Facet: '{txt}' | icon class: '{icon_class}'")

        # 2. Open the search panel to see GroupBy section
        toggle = page.locator('[title="Toggle Search Panel"]')
        if toggle.count() > 0 and toggle.first.is_visible():
            toggle.first.click()
            time.sleep(2)
            
            # Get full search panel HTML
            search_panel = page.locator('.o_search_panel_current_selection, .o_dropdown_container')
            
            # Check all dropdown containers for Filters, Group By, Favorites
            containers = page.locator('.o_dropdown_container').all()
            print(f"\nDropdown containers ({len(containers)}):")
            for i, c in enumerate(containers):
                header = c.locator('.o_dropdown_title').first
                title = header.text_content().strip() if header.count() > 0 else f"Container {i}"
                print(f"\n  === {title} ===")
                
                # Get all menu items in this container
                items = c.locator('.o_menu_item').all()
                for item in items:
                    txt = item.text_content().strip()
                    role = item.get_attribute('role') or ''
                    checked = item.get_attribute('aria-checked') or 'false'
                    cls = item.get_attribute('class') or ''
                    selected = ' ✓ ACTIVE' if 'selected' in cls or checked == 'true' else ''
                    print(f"    - {txt}{selected}")
                
                # Check for custom group select
                selects = c.locator('select').all()
                for sel in selects:
                    options = sel.locator('option').all()
                    opt_texts = [o.text_content().strip() for o in options]
                    print(f"    Custom Group options: {opt_texts[:10]}")
            
            toggle.first.click()  # close
            time.sleep(1)

        # 3. Take a screenshot of the graph to see x-axis labels
        page.screenshot(path="C:/Odoo Study/report_screenshots/analysis_default_graph.png", full_page=False)
        print("\nScreenshot saved: analysis_default_graph.png")

        # 4. Try to read chart.js data from the canvas
        # The graph data might be accessible via JS
        try:
            chart_data = page.evaluate("""
                () => {
                    const canvas = document.querySelector('.o_graph_renderer canvas');
                    if (!canvas) return 'No canvas found';
                    
                    // Try Chart.js instance
                    const chart = Chart.getChart(canvas);
                    if (!chart) return 'No Chart.js instance';
                    
                    return {
                        type: chart.config.type,
                        labels: chart.data.labels,
                        datasets: chart.data.datasets.map(d => ({
                            label: d.label,
                            data: d.data
                        }))
                    };
                }
            """)
            print(f"\nChart.js data: {chart_data}")
        except Exception as e:
            print(f"\nCouldn't read Chart.js data: {e}")

        # 5. Try using Odoo's internal model to check default groupby
        try:
            model_info = page.evaluate("""
                () => {
                    // Try to access the Odoo action/view info
                    const controller = owl.App.apps.values().next().value;
                    if (!controller) return 'No Owl app';
                    return 'Owl app found but complex to navigate';
                }
            """)
            print(f"\nOdoo internal: {model_info}")
        except Exception as e:
            print(f"\nCouldn't access Odoo internals: {e}")

        # 6. Check the graph renderer for data attributes
        renderer = page.locator('.o_graph_renderer')
        if renderer.count() > 0:
            # Check for any data attributes on elements
            canvas = page.locator('.o_graph_renderer canvas')
            if canvas.count() > 0:
                print(f"\nCanvas found, checking parent elements...")
                # The graph view in Odoo stores config in the component
                # Let's check if there's any visible legend or axis labels
                
                # Look for legend items
                legends = page.locator('.o_graph_renderer text, .chartjs-legend li, .chart-legend').all()
                print(f"Legend elements: {len(legends)}")

        # 7. Switch to pivot to see what groupby is actually active
        print("\n\n--- SWITCHING TO PIVOT VIEW ---")
        page.locator('button[aria-label="Pivot View"]').first.click()
        time.sleep(5)

        # The pivot view shows rows and columns which reveal the groupby
        # Row headers show the default group_by
        rows = page.locator('tr').all()
        print(f"Pivot rows ({len(rows)}):")
        for row in rows:
            cells = row.locator('td, th').all()
            vals = [c.text_content().strip() for c in cells]
            # Filter empty
            vals = [v for v in vals if v]
            if vals:
                print(f"  {vals}")

        # The row headers tell us what the default groupby is
        row_headers = page.locator('.o_pivot_header_cell_opened, .o_pivot_header_cell_closed').all()
        print(f"\nPivot header cells ({len(row_headers)}):")
        for h in row_headers:
            txt = h.text_content().strip()
            cls = h.get_attribute('class') or ''
            print(f"  '{txt}' class='{cls[:60]}'")

        # 8. Now also check Rewards report groupby
        print("\n\n" + "=" * 60)
        print("REWARDS — DEFAULT GROUPBY")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(8)

        # Open search panel
        toggle2 = page.locator('[title="Toggle Search Panel"]')
        if toggle2.count() > 0 and toggle2.first.is_visible():
            toggle2.first.click()
            time.sleep(2)
            
            containers2 = page.locator('.o_dropdown_container').all()
            for i, c in enumerate(containers2):
                header = c.locator('.o_dropdown_title').first
                title = header.text_content().strip() if header.count() > 0 else f"Container {i}"
                print(f"\n  === {title} ===")
                items = c.locator('.o_menu_item').all()
                for item in items:
                    txt = item.text_content().strip()
                    cls = item.get_attribute('class') or ''
                    checked = item.get_attribute('aria-checked') or 'false'
                    selected = ' ✓ ACTIVE' if 'selected' in cls or checked == 'true' else ''
                    print(f"    - {txt}{selected}")
            
            toggle2.first.click()
            time.sleep(1)

        # Switch to pivot
        print("\n--- Rewards Pivot ---")
        page.locator('button[aria-label="Pivot View"]').first.click()
        time.sleep(5)
        
        rows2 = page.locator('tr').all()
        for row in rows2:
            cells = row.locator('td, th').all()
            vals = [c.text_content().strip() for c in cells if c.text_content().strip()]
            if vals:
                print(f"  {vals}")

        row_headers2 = page.locator('.o_pivot_header_cell_opened, .o_pivot_header_cell_closed').all()
        print(f"\nPivot header cells ({len(row_headers2)}):")
        for h in row_headers2:
            txt = h.text_content().strip()
            print(f"  '{txt}'")

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
