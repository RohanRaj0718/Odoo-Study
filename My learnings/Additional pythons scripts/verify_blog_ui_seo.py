"""
Use Playwright to verify the exact UI labels, tabs, and button names
in Odoo 19 for blog accuracy.
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
        time.sleep(2)
        page.fill('input[name="login"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        # Find the visible Log in button
        login_btn = page.locator('button:has-text("Log in"):visible, input[type="submit"]:visible, .oe_login_buttons button:visible')
        if login_btn.count() > 0:
            login_btn.first.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(8)
        page.wait_for_load_state("domcontentloaded")
        print("Logged in successfully")
        
        # ═══════════════════════════════════════════
        # 1. Check Sales Settings - Pricing section
        # ═══════════════════════════════════════════
        print("\n=== SALES SETTINGS ===")
        page.goto(f"{URL}/odoo/settings")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Click on "Sales" in the settings sidebar
        sales_menu = page.locator('a:has-text("Sales"), .settings-tab:has-text("Sales")')
        if sales_menu.count() > 0:
            sales_menu.first.click()
            time.sleep(2)
        
        # Look for Pricing section
        pricing_section = page.locator('text=Pricing').first
        if pricing_section.is_visible():
            print("  Pricing section found in Sales settings")
        
        # Check what checkboxes exist under Pricing
        # Look for pricelist, discount related labels
        for label in ['Pricelists', 'Discounts', 'Discount', 'Loyalty', 'Gift Card']:
            els = page.locator(f'label:has-text("{label}")')
            count = els.count()
            if count > 0:
                for i in range(count):
                    text = els.nth(i).text_content().strip()
                    print(f"  Found setting label: '{text}'")
        
        # Take screenshot of settings
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/01_sales_settings.png", full_page=False)
        
        # ═══════════════════════════════════════════
        # 2. Check Pricelist form - tab names
        # ═══════════════════════════════════════════
        print("\n=== PRICELIST FORM ===")
        page.goto(f"{URL}/odoo/sales/pricelists")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Click on "Buy 2 and get 10% off" pricelist
        pricelist_link = page.locator('text="Buy 2 and get 10% off"')
        if pricelist_link.count() > 0:
            pricelist_link.first.click()
            time.sleep(2)
        else:
            # Click first pricelist
            first_row = page.locator('.o_data_row').first
            if first_row.count() > 0:
                first_row.click()
                time.sleep(2)
        
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        
        # Get all tab names on the pricelist form
        tabs = page.locator('.o_notebook .nav-link, .o_notebook_headers .nav-link')
        tab_count = tabs.count()
        print(f"  Number of tabs: {tab_count}")
        for i in range(tab_count):
            tab_text = tabs.nth(i).text_content().strip()
            print(f"  Tab {i+1}: '{tab_text}'")
        
        # Check field labels visible
        field_labels = page.locator('.o_form_label, .o_field_widget label')
        for i in range(min(field_labels.count(), 30)):
            text = field_labels.nth(i).text_content().strip()
            if text:
                print(f"  Field: '{text}'")
        
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/02_pricelist_form.png", full_page=False)
        
        # ═══════════════════════════════════════════
        # 3. Check Price Rule form (click Add a line)
        # ═══════════════════════════════════════════
        print("\n=== PRICE RULE FORM INSIDE PRICELIST ===")
        # Look for "Add a line" inside the pricelist rules tab
        add_line = page.locator('a:has-text("Add a line"), .o_field_x2many_list_row_add a')
        if add_line.count() > 0:
            add_line.first.click()
            time.sleep(2)
            
            # Get column headers in the rules table
            headers = page.locator('.o_list_table th, .o_section_and_note_list_view th')
            for i in range(headers.count()):
                text = headers.nth(i).text_content().strip()
                if text:
                    print(f"  Column header: '{text}'")
            
            page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/03_price_rule_inline.png", full_page=False)
            
            # Press Escape to cancel
            page.keyboard.press("Escape")
            time.sleep(1)
        
        # ═══════════════════════════════════════════
        # 4. Click a rule to open it and check field labels
        # ═══════════════════════════════════════════
        print("\n=== PRICE RULE DETAIL FORM ===")
        rule_row = page.locator('.o_data_row').first
        if rule_row.count() > 0:
            # Check if there's a way to open a rule form
            # In Odoo 19 it might open inline or as a dialog
            rule_row.click()
            time.sleep(2)
            
            # Check if a dialog opened
            dialog = page.locator('.modal-dialog, .o_dialog')
            if dialog.count() > 0:
                print("  Rule opens as dialog/modal")
                # Get all labels in the dialog
                dlg_labels = dialog.locator('.o_form_label, label')
                for i in range(dlg_labels.count()):
                    text = dlg_labels.nth(i).text_content().strip()
                    if text:
                        print(f"  Dialog field: '{text}'")
                page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/04_price_rule_dialog.png", full_page=False)
                
                # Close dialog
                close_btn = dialog.locator('button:has-text("Close"), button:has-text("Discard"), .btn-close')
                if close_btn.count() > 0:
                    close_btn.first.click()
                    time.sleep(1)
            else:
                print("  Rule opens inline (no dialog)")
                page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/04_price_rule_inline.png", full_page=False)
        
        # ═══════════════════════════════════════════
        # 5. Check Customer form - pricelist field location (which tab)
        # ═══════════════════════════════════════════
        print("\n=== CUSTOMER FORM - PRICELIST LOCATION ===")
        page.goto(f"{URL}/odoo/contacts")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Click first customer
        first_contact = page.locator('.o_data_row .o_data_cell').first
        if first_contact.count() > 0:
            first_contact.click()
            time.sleep(2)
        
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        
        # Get all tabs
        tabs = page.locator('.o_notebook .nav-link, .o_notebook_headers .nav-link')
        tab_count = tabs.count()
        print(f"  Number of tabs on customer form: {tab_count}")
        for i in range(tab_count):
            tab_text = tabs.nth(i).text_content().strip()
            print(f"  Tab {i+1}: '{tab_text}'")
        
        # Click on "Sales & Purchase" tab if it exists
        sp_tab = page.locator('.nav-link:has-text("Sales"), .nav-link:has-text("Sales & Purchase")')
        if sp_tab.count() > 0:
            sp_tab.first.click()
            time.sleep(1)
            tab_name = sp_tab.first.text_content().strip()
            print(f"  Clicked tab: '{tab_name}'")
            
            # Look for Pricelist field
            pricelist_label = page.locator('label:has-text("Pricelist"), .o_form_label:has-text("Pricelist")')
            if pricelist_label.count() > 0:
                print(f"  Pricelist field FOUND on this tab")
            else:
                print(f"  Pricelist field NOT FOUND on this tab")
        
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/05_customer_pricelist.png", full_page=False)
        
        # ═══════════════════════════════════════════
        # 6. Check Sales Order - Discount column & Discount button
        # ═══════════════════════════════════════════
        print("\n=== SALES ORDER FORM ===")
        page.goto(f"{URL}/odoo/sales")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Click New to create a quotation
        new_btn = page.locator('button:has-text("New")')
        if new_btn.count() > 0:
            new_btn.first.click()
            time.sleep(2)
        
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        
        # Check for Pricelist field on the form
        pricelist_field = page.locator('label:has-text("Pricelist"), .o_form_label:has-text("Pricelist")')
        if pricelist_field.count() > 0:
            print(f"  Pricelist field FOUND on quotation form")
        else:
            print(f"  Pricelist field NOT FOUND on quotation form")
        
        # Check for Discount button at the bottom
        discount_btn = page.locator('button:has-text("Discount")')
        if discount_btn.count() > 0:
            print(f"  Discount button FOUND on quotation")
        else:
            print(f"  Discount button NOT FOUND on quotation (loyalty module probably not installed)")
        
        # Check column headers in the order lines table
        headers = page.locator('.o_list_table th')
        print(f"  Order line column headers:")
        for i in range(headers.count()):
            text = headers.nth(i).text_content().strip()
            if text:
                print(f"    '{text}'")
        
        page.screenshot(path="c:/Odoo Study/blog_verification_screenshots/06_sales_order_form.png", full_page=False)
        
        # Discard
        discard_btn = page.locator('button:has-text("Discard")')
        if discard_btn.count() > 0:
            discard_btn.first.click()
            time.sleep(1)
            # Confirm discard if dialog appears
            confirm = page.locator('.modal button:has-text("Discard"), .modal button:has-text("Ok")')
            if confirm.count() > 0:
                confirm.first.click()
                time.sleep(1)
        
        # ═══════════════════════════════════════════
        # 7. Check the main menu navigation paths
        # ═══════════════════════════════════════════
        print("\n=== MENU NAVIGATION VERIFICATION ===")
        # Check Sales app menu structure
        page.goto(f"{URL}/odoo/sales")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        
        # Get top menu items
        top_menus = page.locator('.o_menu_sections button, .o_menu_sections .dropdown-toggle, .o_menu_sections > a')
        print(f"  Sales app top menu items:")
        for i in range(top_menus.count()):
            text = top_menus.nth(i).text_content().strip()
            if text:
                print(f"    '{text}'")
        
        # Check for "Products" dropdown 
        products_menu = page.locator('.o_menu_sections button:has-text("Products"), .o_menu_sections .dropdown-toggle:has-text("Products")')
        if products_menu.count() > 0:
            products_menu.first.click()
            time.sleep(1)
            # Get dropdown items
            dropdown_items = page.locator('.dropdown-menu.show a.dropdown-item, .o-dropdown--menu a.dropdown-item')
            print(f"  Products dropdown items:")
            for i in range(dropdown_items.count()):
                text = dropdown_items.nth(i).text_content().strip()
                if text:
                    print(f"    '{text}'")
            page.keyboard.press("Escape")
            time.sleep(0.5)
        
        # Check "Configuration" dropdown
        config_menu = page.locator('.o_menu_sections button:has-text("Configuration"), .o_menu_sections .dropdown-toggle:has-text("Configuration")')
        if config_menu.count() > 0:
            config_menu.first.click()
            time.sleep(1)
            dropdown_items = page.locator('.dropdown-menu.show a.dropdown-item, .o-dropdown--menu a.dropdown-item')
            print(f"  Configuration dropdown items:")
            for i in range(dropdown_items.count()):
                text = dropdown_items.nth(i).text_content().strip()
                if text:
                    print(f"    '{text}'")
            page.keyboard.press("Escape")
            time.sleep(0.5)
        
        # Check "Orders" dropdown
        orders_menu = page.locator('.o_menu_sections button:has-text("Orders"), .o_menu_sections .dropdown-toggle:has-text("Orders")')
        if orders_menu.count() > 0:
            orders_menu.first.click()
            time.sleep(1)
            dropdown_items = page.locator('.dropdown-menu.show a.dropdown-item, .o-dropdown--menu a.dropdown-item')
            print(f"  Orders dropdown items:")
            for i in range(dropdown_items.count()):
                text = dropdown_items.nth(i).text_content().strip()
                if text:
                    print(f"    '{text}'")
            page.keyboard.press("Escape")
        
        browser.close()
        print("\n=== UI VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    import os
    os.makedirs("c:/Odoo Study/blog_verification_screenshots", exist_ok=True)
    run()
