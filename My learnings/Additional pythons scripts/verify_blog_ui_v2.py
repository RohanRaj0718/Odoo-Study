"""
Playwright UI verification — check exact labels, tab names, column headers 
in the Odoo 19 database for blog accuracy.
Uses wait_for_timeout instead of networkidle (Odoo SaaS keeps connections open).
"""
from playwright.sync_api import sync_playwright
import os

URL = "https://client-cient.odoo.com"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"
SS_DIR = r"c:\Odoo Study\blog_verification_screenshots"
os.makedirs(SS_DIR, exist_ok=True)

def ss(page, name):
    path = os.path.join(SS_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=False)
    print(f"  Screenshot: {name}.png")

def goto(page, url):
    page.goto(url, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # ── Login ──
    print("Logging in...")
    goto(page, f"{URL}/web/login")
    page.fill('input[name="login"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button:has-text("Log in")')
    page.wait_for_timeout(8000)
    print(f"  URL: {page.url}")
    
    if '/web/login' in page.url:
        print("  LOGIN FAILED!")
        browser.close()
        exit(1)
    print("  Login OK\n")
    
    # ── 1. Sales → Products → Pricelists ──
    print("=" * 50)
    print("1. PRICELISTS PAGE")
    print("=" * 50)
    goto(page, f"{URL}/odoo/sales/pricelists")
    ss(page, "01_pricelists_list")
    print(f"  URL: {page.url}")
    
    # ── 2. Open New Pricelist → check TAB names ──
    print("\n" + "=" * 50)
    print("2. PRICELIST FORM — TAB NAMES")
    print("=" * 50)
    new_btn = page.locator('button.o_list_button_add, button:has-text("New")')
    if new_btn.first.is_visible():
        new_btn.first.click()
        page.wait_for_timeout(3000)
        ss(page, "02_pricelist_form")
        
        tabs = page.locator('.o_notebook .nav-link')
        tab_count = tabs.count()
        print(f"  Tabs found: {tab_count}")
        for i in range(tab_count):
            t = tabs.nth(i).text_content().strip()
            print(f"    Tab {i+1}: \"{t}\"")
    else:
        print("  Could not find New button")
    
    # ── 3. Click the rules tab → Add a line → check field labels ──
    print("\n" + "=" * 50)
    print("3. PRICE RULE FORM — FIELD LABELS")
    print("=" * 50)
    tabs = page.locator('.o_notebook .nav-link')
    if tabs.count() > 0:
        tabs.first.click()
        page.wait_for_timeout(1000)
    
    add_line = page.locator('a:has-text("Add a line"), td:has-text("Add a line")')
    if add_line.first.is_visible():
        add_line.first.click()
        page.wait_for_timeout(3000)
        ss(page, "03_price_rule_dialog")
        
        dialog = page.locator('.modal-content, .o_dialog')
        if dialog.first.is_visible():
            labels = dialog.first.locator('label, .o_form_label')
        else:
            labels = page.locator('.o_form_label, label.o_form_label')
        
        label_count = labels.count()
        print(f"  Labels found: {label_count}")
        for i in range(min(label_count, 25)):
            lbl = labels.nth(i).text_content().strip()
            if lbl:
                print(f"    \"{lbl}\"")
        
        selects = dialog.first.locator('select') if dialog.first.is_visible() else page.locator('.modal select')
        sel_count = selects.count()
        print(f"\n  Select dropdowns: {sel_count}")
        for i in range(sel_count):
            options = selects.nth(i).locator('option')
            opt_count = options.count()
            for j in range(opt_count):
                print(f"    Option: \"{options.nth(j).text_content().strip()}\"")
        
        close_btn = page.locator('.modal .btn-close, .modal button:has-text("Discard"), .modal button:has-text("Close")')
        if close_btn.first.is_visible():
            close_btn.first.click()
            page.wait_for_timeout(1000)
    else:
        print("  'Add a line' not found")
    
    # ── 4. Sales Order → check column headers ──
    print("\n" + "=" * 50)
    print("4. SALES ORDER — COLUMN HEADERS")
    print("=" * 50)
    discard = page.locator('button:has-text("Discard")')
    if discard.first.is_visible():
        discard.first.click()
        page.wait_for_timeout(1000)
        confirm = page.locator('.modal button:has-text("Discard"), .modal button:has-text("Ok")')
        if confirm.first.is_visible():
            confirm.first.click()
            page.wait_for_timeout(1000)
    
    goto(page, f"{URL}/odoo/sales/new")
    ss(page, "04_sales_order_new")
    
    col_headers = page.locator('.o_list_table thead th, .o_section_and_note_list_view thead th')
    header_count = col_headers.count()
    print(f"  Order line columns: {header_count}")
    for i in range(header_count):
        h = col_headers.nth(i).text_content().strip()
        if h:
            print(f"    \"{h}\"")
    
    pl_field = page.locator('label:has-text("Pricelist"), .o_form_label:has-text("Pricelist")')
    if pl_field.first.is_visible():
        print(f"\n  Pricelist field label: \"{pl_field.first.text_content().strip()}\"")
    else:
        print("\n  Pricelist field NOT visible on sales order form")
    
    # ── 5. Customer form ──
    print("\n" + "=" * 50)
    print("5. CUSTOMER FORM — PRICELIST FIELD")
    print("=" * 50)
    discard = page.locator('button:has-text("Discard")')
    if discard.first.is_visible():
        discard.first.click()
        page.wait_for_timeout(1000)
        confirm = page.locator('.modal button:has-text("Discard"), .modal button:has-text("Ok")')
        if confirm.first.is_visible():
            confirm.first.click()
            page.wait_for_timeout(1000)
    
    goto(page, f"{URL}/odoo/contacts")
    
    first = page.locator('.o_data_row').first
    if first.is_visible():
        first.click()
        page.wait_for_timeout(3000)
        
        tabs = page.locator('.o_notebook .nav-link')
        tab_count = tabs.count()
        print(f"  Contact tabs: {tab_count}")
        for i in range(tab_count):
            t = tabs.nth(i).text_content().strip()
            print(f"    Tab {i+1}: \"{t}\"")
            if 'sales' in t.lower() or 'purchase' in t.lower():
                tabs.nth(i).click()
                page.wait_for_timeout(1500)
                ss(page, "05_customer_sales_tab")
                
                pl = page.locator('label:has-text("Pricelist"), .o_form_label:has-text("Pricelist")')
                if pl.first.is_visible():
                    print(f"  Pricelist label: \"{pl.first.text_content().strip()}\"")
                else:
                    print("  Pricelist label NOT visible")
                break
    
    # ── 6. Settings → Pricing ──
    print("\n" + "=" * 50)
    print("6. SETTINGS — PRICING SECTION")
    print("=" * 50)
    goto(page, f"{URL}/odoo/settings")
    page.wait_for_timeout(3000)
    
    pricing_header = page.locator('h2:has-text("Pricing"), .o_setting_box .o_form_label:has-text("Pricelists")')
    if pricing_header.first.is_visible():
        pricing_header.first.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        ss(page, "06_settings_pricing")
        print("  Pricing section found")
    
    pl_setting = page.locator('label:has-text("Pricelists")')
    if pl_setting.first.is_visible():
        print(f"  Pricelist setting label: \"{pl_setting.first.text_content().strip()}\"")
    
    disc_setting = page.locator('label:has-text("Discounts")')
    if disc_setting.first.is_visible():
        print(f"  Discount setting label: \"{disc_setting.first.text_content().strip()}\"")
    
    browser.close()
    print("\nDone!")
