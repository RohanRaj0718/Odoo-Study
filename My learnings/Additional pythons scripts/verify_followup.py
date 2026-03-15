"""
Targeted follow-up checks for the failed items:
1. Pricelist Name field label (what is the actual label?)
2. Currency field label 
3. Price rule dialog (try clicking Add a line differently)
4. Discount & Loyalty menu path (try navigating via menu clicks)
5. Formula fields
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

        # LOGIN
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        login_input = page.locator("input[id='login'], input[name='login']")
        if await login_input.count() > 0:
            await login_input.fill(USER)
            await page.locator("input[id='password'], input[name='password']").fill(PASS)
            await page.locator("button:has-text('Log in')").click()
            await page.wait_for_timeout(5000)
        print("Logged in.")

        # ── CHECK 1: PRICELIST FORM FIELD LABELS ──
        print("\n=== PRICELIST FORM FIELD LABELS ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Click first pricelist
        row = page.locator(".o_data_row").first
        if await row.count() > 0:
            await row.click()
            await page.wait_for_timeout(3000)

        # Get ALL labels on the form
        all_labels = page.locator("label, .o_form_label")
        lc = await all_labels.count()
        print(f"Found {lc} labels on pricelist form:")
        for i in range(lc):
            txt = (await all_labels.nth(i).inner_text()).strip()
            if txt:
                print(f"  Label: '{txt}'")

        # Check the main name field - it might be an input with placeholder
        name_input = page.locator("input.o_field_widget[name='name'], .o_field_widget[name='name'] input, h1 input, .oe_title input")
        if await name_input.count() > 0:
            val = await name_input.first.get_attribute("placeholder") or ""
            actual = await name_input.first.input_value() or ""
            print(f"  Name field placeholder: '{val}', value: '{actual}'")

        # ── CHECK 2: PRICE RULE DIALOG ──
        print("\n=== PRICE RULE DIALOG (clicking Add a line) ===")
        rules_tab = page.locator(".o_notebook .nav-link:has-text('Rules')")
        if await rules_tab.count() > 0:
            await rules_tab.first.click()
            await page.wait_for_timeout(1500)

        # Try multiple selectors for "Add a line"
        add_selectors = [
            "a:has-text('Add a line')",
            "td a:has-text('Add a line')",
            ".o_field_x2many_list_row_add a",
            "a.o_field_x2many_list_row_add",
        ]
        for sel in add_selectors:
            loc = page.locator(sel)
            cnt = await loc.count()
            print(f"  Selector '{sel}': {cnt} matches")
            if cnt > 0:
                await loc.first.click()
                await page.wait_for_timeout(2000)
                break

        # Check if dialog appeared
        dialog = page.locator(".modal, .o_dialog")
        dcnt = await dialog.count()
        print(f"  Dialog count after click: {dcnt}")

        if dcnt > 0:
            dtxt = await dialog.first.inner_text()
            print(f"  Dialog text:\n{dtxt}")

            # Try clicking Formula
            formula_links = page.locator(".modal a:has-text('Formula'), .modal span:has-text('Formula'), .modal input[value='formula']")
            fc = await formula_links.count()
            print(f"\n  Formula selectors found: {fc}")
            if fc > 0:
                await formula_links.first.click()
                await page.wait_for_timeout(1500)
                dtxt2 = await dialog.first.inner_text()
                print(f"  Dialog AFTER selecting Formula:\n{dtxt2}")

            # Close dialog
            close = page.locator(".modal button:has-text('Discard'), .modal .btn-close")
            if await close.count() > 0:
                await close.first.click()
                await page.wait_for_timeout(1000)
        else:
            # Maybe it's an inline editing row, not a dialog
            print("  No dialog - checking for inline editing...")
            inline = page.locator(".o_selected_row, .o_data_row.o_selected_row")
            if await inline.count() > 0:
                itxt = await inline.first.inner_text()
                print(f"  Inline row text: {itxt}")

        # ── CHECK 3: DISCOUNT & LOYALTY MENU ──
        print("\n=== DISCOUNT & LOYALTY MENU ===")
        # Try using actual Odoo menu navigation
        # First open Sales menu
        await page.goto("https://client-cient.odoo.com/odoo/sales", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Look for top-level menu items
        top_menus = page.locator(".o_menu_sections a, .o_menu_sections button, .o_menu_sections .dropdown-toggle")
        tm_count = await top_menus.count()
        print(f"Top menu items: {tm_count}")
        for i in range(tm_count):
            txt = (await top_menus.nth(i).inner_text()).strip()
            if txt:
                print(f"  Menu: '{txt}'")

        # Click on "Products" dropdown in Sales
        products_menu = page.locator(".o_menu_sections button:has-text('Products'), .o_menu_sections .dropdown-toggle:has-text('Products')")
        if await products_menu.count() > 0:
            await products_menu.first.click()
            await page.wait_for_timeout(1000)

            # Get dropdown items
            dropdown_items = page.locator(".dropdown-menu.show a, .o_menu_sections .dropdown-menu a")
            di_count = await dropdown_items.count()
            print(f"\nProducts dropdown items: {di_count}")
            for i in range(di_count):
                txt = (await dropdown_items.nth(i).inner_text()).strip()
                if txt:
                    print(f"  Item: '{txt}'")

        # Discard pricelist changes if needed
        discard = page.locator("button.o_form_button_cancel:has-text('Discard')")
        if await discard.count() > 0:
            await discard.first.click()
            await page.wait_for_timeout(1000)

        await browser.close()

asyncio.run(run())
