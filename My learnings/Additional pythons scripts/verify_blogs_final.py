"""
Comprehensive line-by-line verification of both SEO blogs against live Odoo 19.
Checks every UI label, menu path, field, tab, column header, dialog content, and setting.
"""
import asyncio
from playwright.async_api import async_playwright

URL = "https://client-cient.odoo.com/odoo"
USER = "rohan.raj@infintor.com"
PASS = "Rohanraj@1"

FINDINGS = []

def log(check, status, detail=""):
    icon = "✅" if status else "❌"
    FINDINGS.append(f"{icon} {check}: {detail}")
    print(f"{icon} {check}: {detail}")


async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        # ── LOGIN ──
        print("=== LOGGING IN ===")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Handle login
        login_input = page.locator("input[id='login'], input[name='login']")
        if await login_input.count() > 0:
            await login_input.fill(USER)
            await page.locator("input[id='password'], input[name='password']").fill(PASS)
            await page.locator("button:has-text('Log in')").click()
            await page.wait_for_timeout(5000)
        print("Logged in.")

        # ══════════════════════════════════════════════════════
        # SECTION 1: SALES SETTINGS - PRICING SECTION
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING SALES SETTINGS ===")
        await page.goto("https://client-cient.odoo.com/odoo/settings", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # Click on Sales settings
        sales_link = page.locator("a:has-text('Sales')")
        if await sales_link.count() > 0:
            await sales_link.first.click()
            await page.wait_for_timeout(3000)

        # Get the full pricing section text
        pricing_section = await page.content()

        # Check 1: "Pricelists" setting label and description
        pricelists_label = page.locator("label:has-text('Pricelists')")
        if await pricelists_label.count() > 0:
            log("Pricelists setting exists", True, "Label 'Pricelists' found in Settings")
        else:
            log("Pricelists setting exists", False, "Label 'Pricelists' NOT found")

        # Check the description text near Pricelists
        pricelist_desc = page.locator("text=Set multiple prices per product, automated discounts, etc.")
        if await pricelist_desc.count() > 0:
            log("Pricelists description", True, '"Set multiple prices per product, automated discounts, etc." confirmed')
        else:
            log("Pricelists description", False, "Description text not found")

        # Check 2: "Discounts" setting
        discounts_label = page.locator("label:has-text('Discounts')")
        if await discounts_label.count() > 0:
            log("Discounts setting exists", True, "Label 'Discounts' found")
        else:
            log("Discounts setting exists", False, "Label 'Discounts' NOT found")

        discount_desc = page.locator("text=Grant discounts on sales order lines")
        if await discount_desc.count() > 0:
            log("Discounts description", True, '"Grant discounts on sales order lines" confirmed')
        else:
            log("Discounts description", False, "Description not found")

        # Check 3: "Promotions, Loyalty & Gift Card" setting
        promo_label = page.locator("text=Promotions, Loyalty & Gift Card")
        if await promo_label.count() > 0:
            log("Promotions setting label", True, '"Promotions, Loyalty & Gift Card" confirmed')
        else:
            log("Promotions setting label", False, "NOT found - checking alternatives")
            alt = page.locator("text=Discounts, Loyalty & Gift Card")
            if await alt.count() > 0:
                log("Promotions setting label (alt)", False, 'Found "Discounts, Loyalty & Gift Card" instead')

        promo_desc = page.locator("text=Manage Promotions, Coupons, Loyalty cards, Gift cards & eWallet")
        if await promo_desc.count() > 0:
            log("Promotions description", True, '"Manage Promotions, Coupons, Loyalty cards, Gift cards & eWallet" confirmed')
        else:
            log("Promotions description", False, "Description not found")

        # Check: Is Pricing the section name?
        pricing_header = page.locator("h2:has-text('Pricing'), .o_setting_box .o_setting_header:has-text('Pricing'), div.text-uppercase:has-text('Pricing')")
        if await pricing_header.count() > 0:
            log("Pricing section header", True, "Section called 'Pricing' exists")
        else:
            # Try broader search
            pricing_any = page.locator("text=Pricing")
            cnt = await pricing_any.count()
            log("Pricing section header", cnt > 0, f"Found {cnt} 'Pricing' text elements")

        # ══════════════════════════════════════════════════════
        # SECTION 2: MENU PATHS
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING MENU PATHS ===")

        # Check: Sales → Products → Pricelists menu
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        page_title = await page.title()
        page_text = await page.locator(".o_control_panel, .breadcrumb, .o_list_view").first.inner_text() if await page.locator(".o_control_panel").count() > 0 else ""
        has_pricelists = "Pricelists" in page_text or "Pricelist" in page_text
        log("Menu: Sales → Products → Pricelists", has_pricelists, f"Page content: {page_text[:100]}")

        # Check: Sales → Orders → Quotations menu
        await page.goto("https://client-cient.odoo.com/odoo/sales", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        breadcrumb = await page.locator(".breadcrumb, .o_control_panel").first.inner_text() if await page.locator(".o_control_panel").count() > 0 else ""
        log("Menu: Sales → Orders → Quotations", "Quotations" in breadcrumb or "quotation" in breadcrumb.lower(), f"Page: {breadcrumb[:80]}")

        # Check: Sales → Orders → Customers
        await page.goto("https://client-cient.odoo.com/odoo/sales/customers", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        cust_text = await page.locator(".o_control_panel").first.inner_text() if await page.locator(".o_control_panel").count() > 0 else ""
        log("Menu: Sales → Orders → Customers", "Customers" in cust_text or "Customer" in cust_text, f"Page: {cust_text[:80]}")

        # Check: Discount & Loyalty menu
        await page.goto("https://client-cient.odoo.com/odoo/sales/loyalty", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        loyalty_text = await page.locator(".o_control_panel, .o_nocontent_help").first.inner_text() if await page.locator(".o_control_panel, .o_nocontent_help").count() > 0 else ""
        log("Menu: Sales → Products → Discount & Loyalty", "Discount" in loyalty_text or "Loyalty" in loyalty_text or "loyalty" in page.url, f"URL: {page.url}, Content: {loyalty_text[:80]}")

        # ══════════════════════════════════════════════════════
        # SECTION 3: PRICELIST FORM
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING PRICELIST FORM ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Click on first pricelist or create new
        pricelist_row = page.locator(".o_data_row").first
        if await pricelist_row.count() > 0:
            await pricelist_row.click()
            await page.wait_for_timeout(3000)
        else:
            new_btn = page.locator("button:has-text('New')")
            if await new_btn.count() > 0:
                await new_btn.click()
                await page.wait_for_timeout(3000)

        # Check: Pricelist Name field
        pricelist_name_field = page.locator("label:has-text('Pricelist Name'), .o_field_widget[name='name'] label")
        log("Pricelist Name field", await pricelist_name_field.count() > 0, f"Found: {await pricelist_name_field.count()} elements")

        # Check: Currency field
        currency_field = page.locator("label:has-text('Currency')")
        log("Currency field on pricelist", await currency_field.count() > 0, "")

        # Check: Company field
        company_field = page.locator("label:has-text('Company')")
        log("Company field on pricelist", await company_field.count() > 0, "")

        # Check: Country Groups field
        country_field = page.locator("label:has-text('Country Groups')")
        log("Country Groups field on pricelist", await country_field.count() > 0, "")

        # Check: Tab names - get ALL tab names
        tabs = page.locator(".o_notebook .nav-link, .o_notebook_headers .nav-link")
        tab_count = await tabs.count()
        tab_names = []
        for i in range(tab_count):
            name = (await tabs.nth(i).inner_text()).strip()
            if name:
                tab_names.append(name)
        log("Pricelist tab names", True, f"Tabs found: {tab_names}")

        # Check: Is the tab called "Rules"?
        has_rules_tab = "Rules" in tab_names
        has_price_rules_tab = "Price Rules" in tab_names
        has_pricelist_rules_tab = "Pricelist Rules" in tab_names
        log("Tab name is 'Rules'", has_rules_tab, f"Rules: {has_rules_tab}, Price Rules: {has_price_rules_tab}, Pricelist Rules: {has_pricelist_rules_tab}")

        # Click on Rules tab to see content
        rules_tab = page.locator(".o_notebook .nav-link:has-text('Rules')")
        if await rules_tab.count() > 0:
            await rules_tab.first.click()
            await page.wait_for_timeout(1500)

        # Check column headers in Rules tab
        col_headers = page.locator(".o_list_view th, .o_field_x2many .o_list_table th")
        header_count = await col_headers.count()
        headers = []
        for i in range(header_count):
            txt = (await col_headers.nth(i).inner_text()).strip()
            if txt:
                headers.append(txt)
        log("Rules tab column headers", True, f"Headers: {headers}")

        # Check: "Add a line" button
        add_line = page.locator("a:has-text('Add a line'), td:has-text('Add a line')")
        log("Add a line button in Rules", await add_line.count() > 0, "")

        # ══════════════════════════════════════════════════════
        # SECTION 4: PRICE RULE DIALOG
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING PRICE RULE DIALOG ===")
        # Click "Add a line" to open the rule dialog
        if await add_line.count() > 0:
            await add_line.first.click()
            await page.wait_for_timeout(2000)

        # Get all labels in the dialog
        dialog = page.locator(".modal, .o_dialog")
        if await dialog.count() > 0:
            dialog_text = await dialog.first.inner_text()
            log("Price rule dialog opens", True, f"Dialog content preview: {dialog_text[:200]}")

            # Check: Apply To field
            apply_to = page.locator(".modal label:has-text('Apply To'), .modal .o_cell:has-text('Apply To')")
            log("Apply To field in dialog", await apply_to.count() > 0 or "Apply To" in dialog_text, "")

            # Check: Price Type field
            price_type = page.locator(".modal label:has-text('Price Type'), .modal .o_cell:has-text('Price Type')")
            log("Price Type field in dialog", await price_type.count() > 0 or "Price Type" in dialog_text, "")

            # Check: Discount/Formula/Fixed Price options
            log("Discount option in Price Type", "Discount" in dialog_text, "")
            log("Formula option in Price Type", "Formula" in dialog_text, "")
            log("Fixed Price option in Price Type", "Fixed Price" in dialog_text, "")

            # Check: Min Qty field
            log("Min Qty field in dialog", "Min Qty" in dialog_text or "Min. Qty" in dialog_text, dialog_text if "Min" in dialog_text else "NOT FOUND")

            # Check: Validity field
            log("Validity field in dialog", "Validity" in dialog_text, "")

            # Check: Product field
            log("Product field in dialog", "Product" in dialog_text, "")

            # Check actual field labels carefully
            all_labels = page.locator(".modal label, .modal .o_form_label")
            label_count = await all_labels.count()
            label_texts = []
            for i in range(label_count):
                txt = (await all_labels.nth(i).inner_text()).strip()
                if txt:
                    label_texts.append(txt)
            log("All dialog labels", True, f"Labels: {label_texts}")

            # Close dialog
            discard_btn = page.locator(".modal button:has-text('Discard'), .modal button:has-text('Close'), .modal .btn-close")
            if await discard_btn.count() > 0:
                await discard_btn.first.click()
                await page.wait_for_timeout(1500)
        else:
            log("Price rule dialog opens", False, "No dialog appeared")

        # ══════════════════════════════════════════════════════
        # SECTION 5: CUSTOMER FORM
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING CUSTOMER FORM ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/customers", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Click first customer
        cust_row = page.locator(".o_data_row").first
        if await cust_row.count() > 0:
            await cust_row.click()
            await page.wait_for_timeout(3000)

        # Check customer tabs
        cust_tabs = page.locator(".o_notebook .nav-link, .o_notebook_headers .nav-link")
        cust_tab_count = await cust_tabs.count()
        cust_tab_names = []
        for i in range(cust_tab_count):
            name = (await cust_tabs.nth(i).inner_text()).strip()
            if name:
                cust_tab_names.append(name)
        log("Customer form tabs", True, f"Tabs: {cust_tab_names}")

        # Check: Sales & Purchase tab exists
        log("Sales & Purchase tab", "Sales & Purchase" in cust_tab_names, "")

        # Click Sales & Purchase tab
        sp_tab = page.locator(".o_notebook .nav-link:has-text('Sales & Purchase')")
        if await sp_tab.count() > 0:
            await sp_tab.first.click()
            await page.wait_for_timeout(1500)

        # Check: Pricelist field on Sales & Purchase tab
        pricelist_field = page.locator("label:has-text('Pricelist')")
        log("Pricelist field on customer", await pricelist_field.count() > 0, "")

        # ══════════════════════════════════════════════════════
        # SECTION 6: SALES ORDER / QUOTATION
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING QUOTATION FORM ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Click on first quotation/SO or create new
        so_row = page.locator(".o_data_row").first
        if await so_row.count() > 0:
            await so_row.click()
            await page.wait_for_timeout(3000)

        # Check: Pricelist field on quotation
        so_pricelist = page.locator("label:has-text('Pricelist'), .o_field_widget[name='pricelist_id']")
        log("Pricelist field on quotation", await so_pricelist.count() > 0, "")

        # Check: SO column headers (Order Lines)
        order_lines_headers = page.locator(".o_field_x2many .o_list_table th, .tab-pane.active .o_list_table th")
        ol_count = await order_lines_headers.count()
        ol_headers = []
        for i in range(ol_count):
            txt = (await order_lines_headers.nth(i).inner_text()).strip()
            if txt:
                ol_headers.append(txt)
        log("SO Order Lines column headers", True, f"Headers: {ol_headers}")

        # Specifically check for Disc.% column
        disc_col = [h for h in ol_headers if "disc" in h.lower() or "%" in h]
        log("Disc.% column exists", len(disc_col) > 0, f"Matching columns: {disc_col}")

        # Check: Discount button
        discount_btn = page.locator("button:has-text('Discount'), .o_statusbar_buttons button:has-text('Discount'), button.btn:has-text('Discount')")
        discount_count = await discount_btn.count()
        log("Discount button on SO", discount_count > 0, f"Found {discount_count} buttons with 'Discount'")

        # If discount button exists, click it to verify the dialog
        if discount_count > 0:
            await discount_btn.first.click()
            await page.wait_for_timeout(2000)

            disc_dialog = page.locator(".modal, .o_dialog")
            if await disc_dialog.count() > 0:
                disc_dialog_text = await disc_dialog.first.inner_text()
                log("Discount dialog opens", True, f"Content: {disc_dialog_text[:300]}")

                # Check options
                log("'On All Order Lines' option", "On All Order Lines" in disc_dialog_text, "")
                log("'Global Discount' option", "Global Discount" in disc_dialog_text, "")
                log("'Fixed Amount' option", "Fixed Amount" in disc_dialog_text, "")
                log("'Apply' button in dialog", "Apply" in disc_dialog_text, "")
                log("'Discard' button in dialog", "Discard" in disc_dialog_text, "")

                # Close
                close = page.locator(".modal button:has-text('Discard'), .modal .btn-close")
                if await close.count() > 0:
                    await close.first.click()
                    await page.wait_for_timeout(1000)
            else:
                log("Discount dialog opens", False, "No dialog appeared after clicking Discount")

        # ══════════════════════════════════════════════════════
        # SECTION 7: DISCOUNT & LOYALTY MENU
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING DISCOUNT & LOYALTY ===")
        await page.goto("https://client-cient.odoo.com/odoo/sales/loyalty", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Check if page loaded with programs
        loyalty_page = await page.content()
        loyalty_control = page.locator(".o_control_panel")
        if await loyalty_control.count() > 0:
            loyalty_cp_text = await loyalty_control.first.inner_text()
            log("Discount & Loyalty page loads", True, f"Control panel: {loyalty_cp_text[:100]}")
        else:
            log("Discount & Loyalty page loads", "loyalty" in page.url.lower(), f"URL: {page.url}")

        # Check for program type options if we can create a new one
        new_btn = page.locator("button:has-text('New')")
        if await new_btn.count() > 0:
            await new_btn.first.click()
            await page.wait_for_timeout(2000)

            # Check program types  
            prog_types = page.locator(".o_kanban_view .o_kanban_card, .modal .o_kanban_card, .o_selection_box")
            if await prog_types.count() > 0:
                types_text = await page.locator(".modal, .o_action").first.inner_text()
                log("Program type selection", True, f"Types: {types_text[:300]}")

                # Check individual types
                for ptype in ["Coupons", "Loyalty Cards", "Promotions", "Discount Code", "Buy X Get Y", "Next Order Coupons"]:
                    log(f"Program type '{ptype}'", ptype in types_text, "")
            else:
                page_text_all = await page.locator("body").inner_text()
                for ptype in ["Coupons", "Loyalty Cards", "Promotions", "Discount Code", "Buy X Get Y", "Next Order Coupons"]:
                    log(f"Program type '{ptype}'", ptype in page_text_all, "")

        # ══════════════════════════════════════════════════════
        # SECTION 8: FORMULA FIELDS CHECK
        # ══════════════════════════════════════════════════════
        print("\n=== CHECKING FORMULA FIELDS ===")
        # Go to pricelist and create a rule with Formula
        await page.goto("https://client-cient.odoo.com/odoo/sales/pricelists", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        pricelist_row2 = page.locator(".o_data_row").first
        if await pricelist_row2.count() > 0:
            await pricelist_row2.click()
            await page.wait_for_timeout(3000)

        # Click Rules tab
        rules_tab2 = page.locator(".o_notebook .nav-link:has-text('Rules')")
        if await rules_tab2.count() > 0:
            await rules_tab2.first.click()
            await page.wait_for_timeout(1500)

        # Add a line
        add_line2 = page.locator("a:has-text('Add a line'), td:has-text('Add a line')")
        if await add_line2.count() > 0:
            await add_line2.first.click()
            await page.wait_for_timeout(2000)

        # In dialog, try to select Formula
        formula_option = page.locator(".modal input[value='formula'], .modal label:has-text('Formula'), .modal a:has-text('Formula'), .modal .o_radio_item:has-text('Formula')")
        if await formula_option.count() > 0:
            await formula_option.first.click()
            await page.wait_for_timeout(1500)

            # Now check the formula sub-fields
            dialog_after_formula = page.locator(".modal")
            if await dialog_after_formula.count() > 0:
                formula_text = await dialog_after_formula.first.inner_text()
                log("Formula dialog content", True, f"Content: {formula_text[:400]}")

                # Check: Price Discount label
                log("'Price Discount' label", "Price Discount" in formula_text, "")
                # Check: Price Rounding label 
                log("'Price Rounding' label", "Price Rounding" in formula_text, "")
                # Check: Extra Fee label
                log("'Extra Fee' label", "Extra Fee" in formula_text, "")

                # Get all labels
                formula_labels = page.locator(".modal label, .modal .o_form_label")
                fl_count = await formula_labels.count()
                fl_texts = []
                for i in range(fl_count):
                    txt = (await formula_labels.nth(i).inner_text()).strip()
                    if txt:
                        fl_texts.append(txt)
                log("All formula dialog labels", True, f"Labels: {fl_texts}")
        else:
            log("Formula option in dialog", False, "Could not find Formula option to click")
            # Get full dialog text
            d = page.locator(".modal")
            if await d.count() > 0:
                dtxt = await d.first.inner_text()
                log("Dialog text for debugging", True, f"{dtxt[:400]}")

        # Close dialog
        discard2 = page.locator(".modal button:has-text('Discard'), .modal .btn-close")
        if await discard2.count() > 0:
            await discard2.first.click()
            await page.wait_for_timeout(1000)

        # Discard pricelist changes
        discard3 = page.locator("button:has-text('Discard')")
        if await discard3.count() > 0:
            await discard3.first.click()
            await page.wait_for_timeout(1500)

        await browser.close()

    # ══════════════════════════════════════════════════════
    # PRINT SUMMARY
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    passed = sum(1 for f in FINDINGS if f.startswith("✅"))
    failed = sum(1 for f in FINDINGS if f.startswith("❌"))
    print(f"PASSED: {passed}  |  FAILED: {failed}  |  TOTAL: {len(FINDINGS)}")
    print("=" * 70)
    for f in FINDINGS:
        print(f)
    print("=" * 70)

asyncio.run(run())
