#!/usr/bin/env python3
"""
Get Chart.js data for the Rewards report too.
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

        # ── REWARDS REPORT ──
        print("=" * 60)
        print("REWARDS — CHART.JS DATA")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Rewards")').first.click()
        time.sleep(8)

        try:
            chart_data = page.evaluate("""
                () => {
                    const canvas = document.querySelector('.o_graph_renderer canvas');
                    if (!canvas) return 'No canvas found';
                    const chart = Chart.getChart(canvas);
                    if (!chart) return 'No Chart.js instance';
                    return {
                        type: chart.config.type,
                        labels: chart.data.labels,
                        datasets: chart.data.datasets.map(d => ({
                            label: d.label,
                            data: d.data,
                            backgroundColor: d.backgroundColor
                        })),
                        options_scales: {
                            x_title: chart.options?.scales?.x?.title?.text || 'none',
                            y_title: chart.options?.scales?.y?.title?.text || 'none'
                        }
                    };
                }
            """)
            print(f"Chart data: {chart_data}")
        except Exception as e:
            print(f"Error: {e}")

        # ── REFERRAL ANALYSIS — also get axis titles ──
        print("\n" + "=" * 60)
        print("REFERRAL ANALYSIS — FULL CHART.JS DATA")
        print("=" * 60)
        page.locator('button:has-text("Reporting")').first.click()
        time.sleep(2)
        page.locator('.dropdown-item:has-text("Referral Analysis")').first.click()
        time.sleep(8)

        try:
            chart_data2 = page.evaluate("""
                () => {
                    const canvas = document.querySelector('.o_graph_renderer canvas');
                    if (!canvas) return 'No canvas found';
                    const chart = Chart.getChart(canvas);
                    if (!chart) return 'No Chart.js instance';
                    return {
                        type: chart.config.type,
                        labels: chart.data.labels,
                        datasets: chart.data.datasets.map(d => ({
                            label: d.label,
                            data: d.data,
                            backgroundColor: d.backgroundColor
                        })),
                        xAxisLabel: chart.options?.scales?.x?.title?.text || 'none',
                        yAxisLabel: chart.options?.scales?.y?.title?.text || 'none',
                        stacked: chart.options?.scales?.x?.stacked || false,
                        plugins_title: chart.options?.plugins?.title?.text || 'none'
                    };
                }
            """)
            print(f"Chart data: {chart_data2}")
        except Exception as e:
            print(f"Error: {e}")

        # Check if view definition reveals the default group_by
        # Try Odoo's action manager
        try:
            view_info = page.evaluate("""
                () => {
                    // Access the graph model's metaData
                    const graphEl = document.querySelector('.o_graph_renderer');
                    if (!graphEl) return 'no graph el';
                    
                    // Try __owl__ component
                    const comp = graphEl.__owl__;
                    if (!comp) return 'no owl component';
                    
                    // Navigate component tree to find graph model
                    const props = comp.props || {};
                    return {
                        hasProps: !!props,
                        propKeys: Object.keys(props).slice(0, 20)
                    };
                }
            """)
            print(f"\nView component info: {view_info}")
        except Exception as e:
            print(f"\nComponent access: {e}")

        # One more attempt: check the graph's group_by from the OWL component
        try:
            groupby_info = page.evaluate("""
                () => {
                    // Find graph view controller
                    const elements = document.querySelectorAll('[class*="graph"]');
                    for (const el of elements) {
                        if (el.__owl__) {
                            const comp = el.__owl__;
                            // Try to find model with groupBy
                            let current = comp;
                            const visited = new Set();
                            while (current && !visited.has(current)) {
                                visited.add(current);
                                if (current.component && current.component.model) {
                                    const model = current.component.model;
                                    return {
                                        groupBy: model.metaData?.groupBy || 'not found',
                                        measure: model.metaData?.measure || 'not found',
                                        resModel: model.metaData?.resModel || 'not found',
                                        mode: model.metaData?.mode || 'not found'
                                    };
                                }
                                current = current.parent;
                            }
                        }
                    }
                    return 'Could not find graph model';
                }
            """)
            print(f"\nGraph model info: {groupby_info}")
        except Exception as e:
            print(f"\nGraph model access: {e}")

        print("\n=== DONE ===")
        browser.close()


if __name__ == "__main__":
    main()
