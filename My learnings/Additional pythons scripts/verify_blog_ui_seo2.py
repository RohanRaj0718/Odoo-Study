"""
Check the Discount button dropdown options on a Sales Order,
and check the labels inside a price rule dialog more carefully.
"""
from playwright.sync_api import sync_playwright
import time

URL = "https://client-cient.odoo.com"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Login
        page.goto(f"{URL}/web/login")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        login_btn = page.locator('button:has-text("Log in"):visible')
        if login_btn.count() > 0:
            login_btn.first.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(8)
        print("Logged in")
        
        # ═══════════════════════════════════════════
        # 1. Check Discount button dropdown
        # ═══════════════════════════════════════════
        print("\n=== DISCOUNT BUTTON ON SALES ORDER ===")
        page.goto(f"{URL}/odoo/sales")
        time.sleep(4)
        
        new_btn = page.locator('button:has-text("New")')
        if new_btn.count() > 0:
            new_btn.first.click()
            time.sleep(3)
        
        # Click the Discount button
        discount_btn = page.locator('button:has-text("Discount")')
        if discount_btn.count() > 0:
            print(f"  Discount button text: '{discount_btn.first.text_content().strip()}'")
            discount_btn.first.click()
            time.sleep(2)
            
            # Check dropdown options
            dropdown_items = page.locator('.dropdown-menu.show .dropdown-item, .o-dropdown--menu .dropdown-item')
            if dropdown_items.count() > 0:
                print(f"  Discount button dropdown items:")
                for i in range(dropdown_items.count()):
                    text = dropdown_items.nth(i).text_content().strip()
                    print(f"    '{text}'")
            else:
                # Maybe it opens a dialog instead
                dialog = page.locator('.modal-dialog')
                if dialog.count() > 0:
                    print("  Discount opens a dialog:")
                    dialog_text = dialog.first.text_content()
                    print(f"    {dialog_text[:300]}")
                else:
                    print("  No dropdown or dialog found after clicking Discount")
            
            page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/07_discount_button.png", full_page=False)
            page.keyboard.press("Escape")
            time.sleep(1)
        
        # Discard the quotation
        page.locator('button:has-text("Discard")').first.click()
        time.sleep(1)
        confirm = page.locator('.modal button:has-text("Discard"), .modal button:has-text("Ok")')
        if confirm.count() > 0:
            confirm.first.click()
            time.sleep(1)
        
        # ═══════════════════════════════════════════
        # 2. Open Price Rule dialog and get ALL labels
        # ═══════════════════════════════════════════
        print("\n=== PRICE RULE DIALOG DETAILS ===")
        page.goto(f"{URL}/odoo/sales/pricelists")
        time.sleep(4)
        
        # Click on "Buy 2 and get 10% off"
        pl = page.locator('td:has-text("Buy 2 and get 10% off")')
        if pl.count() > 0:
            pl.first.click()
            time.sleep(3)
        else:
            page.locator('.o_data_row').first.click()
            time.sleep(3)
        
        # Click on a rule row to open it
        rule_row = page.locator('.o_data_row')
        if rule_row.count() > 0:
            rule_row.first.click()
            time.sleep(2)
            
            dialog = page.locator('.modal-dialog, .o_dialog')
            if dialog.count() > 0:
                # Get ALL text content from the dialog
                all_text = dialog.first.inner_text()
                print(f"  Full dialog text:\n{all_text}")
                page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/08_rule_dialog_full.png", full_page=False)
                
                # Close
                close_btn = dialog.locator('button:has-text("Close"), button:has-text("Discard"), .btn-close')
                if close_btn.count() > 0:
                    close_btn.first.click()
                    time.sleep(1)
        
        # ═══════════════════════════════════════════
        # 3. Check Settings - Pricing section detail
        # ═══════════════════════════════════════════
        print("\n=== SETTINGS PRICING SECTION DETAIL ===")
        page.goto(f"{URL}/odoo/settings")
        time.sleep(4)
        
        # Click Sales
        sales_tab = page.locator('a:has-text("Sales")')
        if sales_tab.count() > 0:
            sales_tab.first.click()
            time.sleep(2)
        
        # Get all the text around Pricing section
        pricing_area = page.locator('.o_setting_box:has-text("Pricing"), .o_settings_container:has-text("Pricing")')
        if pricing_area.count() > 0:
            for i in range(min(pricing_area.count(), 5)):
                text = pricing_area.nth(i).inner_text()
                if 'Pricelists' in text or 'Discounts' in text or 'Loyalty' in text or 'Promotions' in text:
                    print(f"  Setting box:\n{text}\n---")
        
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/09_settings_pricing.png", full_page=False)
        
        # ═══════════════════════════════════════════
        # 4. Check the exact label of the pricelist tab
        # ═══════════════════════════════════════════
        print("\n=== PRICELIST TABS EXACT CHECK ===")
        page.goto(f"{URL}/odoo/sales/pricelists")
        time.sleep(4)
        
        # Click on first pricelist
        page.locator('.o_data_row').first.click()
        time.sleep(3)
        
        # Check ALL notebook-related elements
        tab_els = page.locator('.o_notebook .nav-link')
        print(f"  Tab elements found: {tab_els.count()}")
        for i in range(tab_els.count()):
            text = tab_els.nth(i).text_content().strip()
            classes = tab_els.nth(i).get_attribute("class")
            print(f"  Tab {i+1}: text='{text}', classes='{classes}'")
        
        # Also check page_name attributes in notebook pages
        pages = page.locator('.o_notebook .tab-pane')
        print(f"  Tab panes found: {pages.count()}")
        
        browser.close()
        print("\n=== DONE ===")

if __name__ == "__main__":
    run()
