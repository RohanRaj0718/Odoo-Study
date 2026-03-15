"""
Deep-dive check: pricelist form in edit mode, currency, and menu navigation.
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
        await page.locator("input[id='login'], input[name='login']").fill(USER)
        await page.locator("input[id='password'], input[name='password']").fill(PASS)
        await page.locator("button:has-text('Log in')").click()
        await page.wait_for_timeout(5000)
        print("Logged in.")

        # ── PRICELIST FORM - NEW (to see all edit labels) ──
        print("\n=== PRICELIST - CREATE NEW ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists/new", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # Get ALL text on the form
        form = page.locator(".o_form_view")
        if await form.count() > 0:
            form_text = await form.first.inner_text()
            print(f"Full form text:\n{form_text}")
        
        # Check all input placeholders
        all_inputs = page.locator("input[placeholder], .o_field_widget input[placeholder]")
        ic = await all_inputs.count()
        print(f"\nAll inputs with placeholders ({ic}):")
        for i in range(ic):
            ph = await all_inputs.nth(i).get_attribute("placeholder")
            name = await all_inputs.nth(i).get_attribute("name") or "?"
            cls = await all_inputs.nth(i).get_attribute("class") or ""
            print(f"  Input name='{name}', placeholder='{ph}'")

        # Check all spans, divs that might be field labels
        print("\nChecking all .o_form_label elements:")
        form_labels = page.locator(".o_form_label, .o_cell .o_wrap_label label")
        flc = await form_labels.count()
        for i in range(flc):
            txt = (await form_labels.nth(i).inner_text()).strip()
            print(f"  Form label: '{txt}'")

        # Check for currency - it might be shown as a dropdown/select near the name
        print("\nChecking for currency-related elements:")
        currency_els = page.locator("[name='currency_id'], .o_field_widget[name='currency_id']")
        cc = await currency_els.count()
        print(f"  currency_id field widgets: {cc}")
        if cc > 0:
            curr_text = await currency_els.first.inner_text()
            print(f"  Currency widget text: '{curr_text}'")

        # Check the Rules tab and Add a line in NEW form
        print("\n=== RULES TAB IN NEW FORM ===")
        rules_tab = page.locator(".o_notebook .nav-link:has-text('Rules')")
        if await rules_tab.count() > 0:
            await rules_tab.first.click()
            await page.wait_for_timeout(1500)
            
            # Get all clickable elements in rules area
            rules_area = page.locator(".tab-pane.active")
            if await rules_area.count() > 0:
                rtxt = await rules_area.first.inner_text()
                print(f"Rules tab content: '{rtxt}'")
            
            # Look for any add button
            add_btns = page.locator(".tab-pane.active a, .tab-pane.active button")
            abc = await add_btns.count()
            print(f"Clickable elements in Rules tab: {abc}")
            for i in range(abc):
                atxt = (await add_btns.nth(i).inner_text()).strip()
                if atxt:
                    print(f"  Element: '{atxt}'")

            # Try the "Add a line" link specifically
            add_link = page.locator(".tab-pane.active a:has-text('Add a line'), .o_field_x2many a:has-text('Add a line')")
            alc = await add_link.count()
            print(f"\n'Add a line' links: {alc}")
            if alc > 0:
                await add_link.first.click()
                await page.wait_for_timeout(2000)
                
                # Check dialog
                dialog = page.locator(".modal, .o_dialog")
                if await dialog.count() > 0:
                    dtxt = await dialog.first.inner_text()
                    print(f"\nDialog text:\n{dtxt}")

                    # Now try to click Formula
                    formula = page.locator(".modal:has-text('Formula') >> a:has-text('Formula'), .modal span:has-text('Formula')")
                    fmc = await formula.count()
                    print(f"\nFormula elements in dialog: {fmc}")
                    
                    # Try radio/selection items
                    radios = page.locator(".modal .o_radio_item")
                    rc = await radios.count()
                    print(f"Radio items: {rc}")
                    for i in range(rc):
                        rtxt = (await radios.nth(i).inner_text()).strip()
                        print(f"  Radio: '{rtxt}'")
                        if "Formula" in rtxt:
                            await radios.nth(i).click()
                            await page.wait_for_timeout(1500)
                            dtxt2 = await page.locator(".modal").first.inner_text()
                            print(f"\nDialog AFTER Formula click:\n{dtxt2}")
                            break

                    # Close
                    close = page.locator(".modal button:has-text('Discard'), .modal .btn-close")
                    if await close.count() > 0:
                        await close.first.click()
                        await page.wait_for_timeout(1000)
                else:
                    # Inline row?
                    print("No dialog opened - checking inline...")
                    sel_row = page.locator(".o_selected_row")
                    if await sel_row.count() > 0:
                        print(f"Selected row: {await sel_row.first.inner_text()}")
            else:
                # Try broader search
                all_links = page.locator("a")
                ac = await all_links.count()
                for i in range(ac):
                    t = (await all_links.nth(i).inner_text()).strip()
                    if "add" in t.lower() or "line" in t.lower():
                        print(f"  Found link: '{t}'")

        # ── PRODUCTS MENU ITEMS ──
        print("\n=== PRODUCTS MENU DROPDOWN ===")
        # Navigate to sales first
        await page.goto("https://client-cient.odoo.com/odoo/sales", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Click Products menu
        products_btn = page.locator(".o_menu_sections >> text=Products")
        pbc = await products_btn.count()
        print(f"Products menu buttons: {pbc}")
        if pbc > 0:
            await products_btn.first.click()
            await page.wait_for_timeout(1000)
            
            # Get ALL visible dropdown items
            visible_items = page.locator(".dropdown-item:visible, .dropdown-menu a:visible")
            vic = await visible_items.count()
            print(f"Visible dropdown items: {vic}")
            for i in range(vic):
                txt = (await visible_items.nth(i).inner_text()).strip()
                href = await visible_items.nth(i).get_attribute("href") or ""
                print(f"  Item: '{txt}' -> {href}")

        # Also check Orders menu
        print("\n=== ORDERS MENU DROPDOWN ===")
        orders_btn = page.locator(".o_menu_sections >> text=Orders")
        if await orders_btn.count() > 0:
            await orders_btn.first.click()
            await page.wait_for_timeout(1000)
            visible_items2 = page.locator(".dropdown-item:visible, .dropdown-menu a:visible")
            vic2 = await visible_items2.count()
            print(f"Visible dropdown items: {vic2}")
            for i in range(vic2):
                txt = (await visible_items2.nth(i).inner_text()).strip()
                print(f"  Item: '{txt}'")

        # Discard any changes
        discard = page.locator("button:has-text('Discard')")
        if await discard.count() > 0:
            await discard.first.click()
            await page.wait_for_timeout(1000)

        await browser.close()

asyncio.run(run())
