"""
Check the Discount button and price rule dialog more carefully.
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
        time.sleep(3)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.keyboard.press("Enter")
        time.sleep(8)
        print("Logged in")
        
        # ═══════════════════════════════════════════
        # 1. Create a quotation with a customer, add product, then check Discount button
        # ═══════════════════════════════════════════
        print("\n=== DISCOUNT BUTTON ON SALES ORDER ===")
        page.goto(f"{URL}/odoo/sales/new")
        time.sleep(5)
        
        # Set customer
        customer_field = page.locator('.o_field_widget[name="partner_id"] input')
        if customer_field.count() > 0:
            customer_field.first.click()
            customer_field.first.fill("Krishnadas")
            time.sleep(2)
            # Select first dropdown suggestion
            suggestion = page.locator('.o-autocomplete--dropdown-menu .o-autocomplete--dropdown-item, .ui-menu-item')
            if suggestion.count() > 0:
                suggestion.first.click()
                time.sleep(2)
                print("  Customer selected")
        
        # Add a product line
        add_line = page.locator('a:has-text("Add a product")')
        if add_line.count() > 0:
            add_line.first.click()
            time.sleep(1)
            # Type product name
            product_input = page.locator('.o_selected_row .o_field_widget[name="product_id"] input')
            if product_input.count() > 0:
                product_input.first.fill("Table")
                time.sleep(2)
                suggestion = page.locator('.o-autocomplete--dropdown-menu .o-autocomplete--dropdown-item')
                if suggestion.count() > 0:
                    suggestion.first.click()
                    time.sleep(2)
                    print("  Product added")
        
        # Now check for the Discount button
        discount_btn = page.locator('button:has-text("Discount")')
        if discount_btn.count() > 0:
            print(f"  Found {discount_btn.count()} Discount button(s)")
            discount_btn.first.click()
            time.sleep(2)
            
            # Check for any dropdown/popover that appeared
            all_dropdowns = page.locator('.dropdown-menu.show, .o-dropdown--menu.show, .popover, .o_popover')
            if all_dropdowns.count() > 0:
                text = all_dropdowns.first.inner_text()
                print(f"  Dropdown/popover content:\n{text}")
            else:
                # Maybe it's a dialog
                dialog = page.locator('.modal-dialog, .o_dialog')
                if dialog.count() > 0:
                    text = dialog.first.inner_text()
                    print(f"  Dialog content:\n{text}")
                else:
                    # Maybe nothing visible - take screenshot to see
                    print("  No dropdown/dialog visible")
            
            page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/10_discount_click.png", full_page=False)
        else:
            print("  No Discount button found")
        
        # Discard 
        page.goto(f"{URL}/odoo/sales")
        time.sleep(3)
        discard = page.locator('.modal button:has-text("Discard"), .modal button:has-text("Ok"), .modal button:has-text("Leave")')
        if discard.count() > 0:
            discard.first.click()
            time.sleep(2)
        
        # ═══════════════════════════════════════════
        # 2. Open Price Rule dialog and screenshot
        # ═══════════════════════════════════════════
        print("\n=== PRICE RULE DIALOG ===")
        page.goto(f"{URL}/odoo/sales/pricelists")
        time.sleep(4)
        
        # Click on "Buy 2 and get 10% off"
        pl = page.locator('td:has-text("Buy 2")')
        if pl.count() > 0:
            pl.first.click()
            time.sleep(3)
        
        # Get tab name
        tab = page.locator('.o_notebook .nav-link')
        if tab.count() > 0:
            print(f"  Pricelist tab name: '{tab.first.text_content().strip()}'")
        
        # Get column headers from the rules list inside pricelist
        headers = page.locator('.o_field_one2many .o_list_table th')
        print(f"  Rules table column headers:")
        for i in range(headers.count()):
            text = headers.nth(i).text_content().strip()
            if text:
                print(f"    '{text}'")
        
        # Click on first rule
        rule_row = page.locator('.o_field_one2many .o_data_row')
        if rule_row.count() > 0:
            rule_row.first.click()
            time.sleep(3)
            
            dialog = page.locator('.modal')
            if dialog.count() > 0:
                print(f"\n  Dialog full text:")
                text = dialog.first.inner_text()
                print(text)
                page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/11_rule_dialog.png", full_page=False)
                
                # Close
                dialog.locator('button:has-text("Close"), button:has-text("Discard"), .btn-close').first.click()
                time.sleep(1)
        
        # ═══════════════════════════════════════════
        # 3. Settings pricing area text
        # ═══════════════════════════════════════════
        print("\n=== SETTINGS PRICING TEXT ===")
        page.goto(f"{URL}/odoo/settings")
        time.sleep(4)
        
        sales_link = page.locator('a:has-text("Sales")')
        if sales_link.count() > 0:
            sales_link.first.click()
            time.sleep(2)
        
        # Get all setting boxes text
        boxes = page.locator('.o_setting_box')
        for i in range(boxes.count()):
            text = boxes.nth(i).inner_text().strip()
            if any(k in text for k in ['Pricelists', 'Discounts', 'Pricing', 'Loyalty', 'Promotions']):
                print(f"\n  Setting box {i+1}:\n  {text}\n  ---")
        
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/12_settings.png", full_page=False)
        
        browser.close()
        print("\n=== DONE ===")

if __name__ == "__main__":
    run()
