"""
Final check: currency widget, Add a line dialog, Discount & Loyalty existence.
"""
import asyncio
from playwright.async_api import async_playwright

URL = "https://client-cient.odoo.com/odoo"
USER = "rohan.raj@infintor.com"
PASS = "Rohanraj@1"


async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.locator("input[id='login'], input[name='login']").fill(USER)
        await page.locator("input[id='password'], input[name='password']").fill(PASS)
        await page.locator("button:has-text('Log in')").click()
        await page.wait_for_timeout(5000)
        print("Logged in.")

        # ── CHECK PRICELIST FORM HTML for currency ──
        print("\n=== PRICELIST FORM - HTML INSPECTION ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists/new", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # Check for currency in the header area / statusbar / title area
        title_area = page.locator(".oe_title, .o_form_sheet_bg .o_title, .o_form_sheet > div:first-child")
        if await title_area.count() > 0:
            thtml = await title_area.first.inner_html()
            print(f"Title area HTML (first 500 chars):\n{thtml[:500]}")

        # Check ALL field names
        all_fields = page.locator("[name]")
        fc = await all_fields.count()
        print(f"\nAll elements with 'name' attribute ({fc}):")
        for i in range(fc):
            name = await all_fields.nth(i).get_attribute("name")
            tag = await all_fields.nth(i).evaluate("el => el.tagName")
            cls = (await all_fields.nth(i).get_attribute("class") or "")[:60]
            visible = await all_fields.nth(i).is_visible()
            if visible and name and "o_field" in cls:
                txt = (await all_fields.nth(i).inner_text()).strip()
                print(f"  name='{name}', tag={tag}, text='{txt[:40]}', class={cls[:40]}")

        # ── CLICK ADD A LINE ──
        print("\n=== ADD A LINE IN RULES ===")
        # Navigate to Rules tab
        rules_tab = page.locator(".o_notebook .nav-link:has-text('Rules')")
        if await rules_tab.count() > 0:
            await rules_tab.first.click()
            await page.wait_for_timeout(1000)

        # Use text content search
        add_link = page.get_by_text("Add a line", exact=True)
        alc = await add_link.count()
        print(f"'Add a line' via get_by_text: {alc}")
        if alc > 0:
            await add_link.first.click()
            await page.wait_for_timeout(2500)

            dialog = page.locator(".modal")
            if await dialog.count() > 0:
                dtxt = await dialog.first.inner_text()
                print(f"\nDIALOG OPENED! Content:\n{dtxt}")

                # Try selecting Formula
                formula_radio = page.locator(".modal .o_radio_item:has-text('Formula')")
                if await formula_radio.count() > 0:
                    await formula_radio.first.click()
                    await page.wait_for_timeout(1500)
                    dtxt2 = await page.locator(".modal").first.inner_text()
                    print(f"\nDIALOG AFTER FORMULA:\n{dtxt2}")
                else:
                    # Try clicking the select/radio for price type
                    radio_items = page.locator(".modal .o_radio_item, .modal input[type='radio']")
                    ric = await radio_items.count()
                    print(f"\nRadio items found: {ric}")
                    for i in range(ric):
                        rtxt = (await radio_items.nth(i).inner_text()).strip()
                        print(f"  Radio: '{rtxt}'")

                # Close
                close = page.locator(".modal button:has-text('Discard'), .modal .btn-close")
                if await close.count() > 0:
                    await close.first.click()
                    await page.wait_for_timeout(1000)
            else:
                print("No dialog - might be inline row editing")
                # Check if there's an inline selected row
                sel = page.locator(".o_selected_row, tr.o_selected_row")
                if await sel.count() > 0:
                    print(f"Inline edit row: {await sel.first.inner_text()}")
                else:
                    # Maybe it's a different type of inline form
                    active_tab = page.locator(".tab-pane.active")
                    if await active_tab.count() > 0:
                        atxt = await active_tab.first.inner_text()
                        print(f"Active tab content now:\n{atxt}")

        # ── DISCOUNT & LOYALTY: CHECK IF SETTING IS ENABLED ──
        print("\n=== CHECKING IF PROMOTIONS IS ENABLED ===")
        await page.goto("https://client-cient.odoo.com/odoo/settings", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        sales_link = page.locator("a:has-text('Sales')")
        if await sales_link.count() > 0:
            await sales_link.first.click()
            await page.wait_for_timeout(3000)

        # Check if "Promotions, Loyalty & Gift Card" checkbox is checked
        promo_checkbox = page.locator("input[type='checkbox']")
        pc = await promo_checkbox.count()
        print(f"Checkboxes found: {pc}")
        
        # Get the setting divs
        settings_divs = page.locator(".o_setting_box")
        sdc = await settings_divs.count()
        for i in range(sdc):
            stxt = (await settings_divs.nth(i).inner_text()).strip()
            if "Promotions" in stxt or "Loyalty" in stxt or "Pricelist" in stxt or "Discount" in stxt:
                # Check checkbox state
                cb = settings_divs.nth(i).locator("input[type='checkbox']")
                if await cb.count() > 0:
                    checked = await cb.first.is_checked()
                    print(f"Setting: '{stxt[:60]}...' -> Checked: {checked}")

        # ── CHECK: Is Sale Loyalty module installed? ──
        print("\n=== CHECKING INSTALLED APPS ===")
        await page.goto("https://client-cient.odoo.com/odoo/settings", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Navigate to Apps
        apps_link = page.locator("a[href*='/odoo/action-base.open_module_tree']")
        if await apps_link.count() > 0:
            href = await apps_link.first.get_attribute("href")
            print(f"Apps link: {href}")

        # Discard
        discard = page.locator("button:has-text('Discard')")
        if await discard.count() > 0:
            await discard.first.click()

        await browser.close()

asyncio.run(run())
