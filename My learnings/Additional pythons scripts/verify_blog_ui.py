"""
Quick Playwright check: open Sales → Products → Pricelists → create new → check labels on the form.
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
    page.screenshot(path=path, full_page=True)
    print(f"  Screenshot: {path}")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # ── Login ──
    print("Logging in...")
    page.goto(f"{URL}/web/login", timeout=30000)
    page.fill('input[name="login"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button:has-text("Log in")')
    page.wait_for_timeout(8000)
    print(f"  URL after login: {page.url}")
    
    if '/web/login' in page.url:
        print("  LOGIN FAILED!")
        browser.close()
        exit(1)
    print("  Login OK\n")
    
    # ── 1. Sales Settings → Pricing section ──
    print("=" * 50)
    print("1. SALES SETTINGS - Pricing section")
    print("=" * 50)
    page.goto(f"{URL}/odoo/settings", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(3000)
    
    # Scroll to find Pricing section or search for it
    pricing = page.locator('text=Pricelists').first
    if pricing.is_visible():
        pricing.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        ss(page, "01_settings_pricelists")
        print("  Found 'Pricelists' text in settings")
    
    # Check for Discounts setting
    discounts = page.locator(':text("Discounts")').first
    if discounts.is_visible():
        discounts.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        ss(page, "02_settings_discounts")
        print("  Found 'Discounts' text in settings")
    
    # ── 2. Sales → Products → Pricelists ──
    print("\n" + "=" * 50)
    print("2. PRICELISTS LIST")
    print("=" * 50)
    page.goto(f"{URL}/odoo/sales/pricelists", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)
    ss(page, "03_pricelists_list")
    print(f"  URL: {page.url}")
    
    # ── 3. Open a pricelist form ──
    print("\n" + "=" * 50)
    print("3. PRICELIST FORM")
    print("=" * 50)
    # Click New to create a new pricelist
    new_btn = page.locator('button:has-text("New"), .o_list_button_add')
    if new_btn.first.is_visible():
        new_btn.first.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(2000)
        ss(page, "04_pricelist_form_new")
        
        # Check tab names
        tabs = page.locator('.o_notebook .nav-link, .o_notebook_headers .nav-link')
        tab_count = tabs.count()
        print(f"  Tabs found: {tab_count}")
        for i in range(tab_count):
            tab_text = tabs.nth(i).text_content().strip()
            print(f"    Tab {i+1}: \"{tab_text}\"")
    
    # ── 4. Click on Price Rules tab → Add a line ──
    print("\n" + "=" * 50)
    print("4. PRICE RULE FORM LABELS")
    print("=" * 50)
    # Find the pricelist rules tab
    rule_tab = page.locator('.nav-link:has-text("Pricelist Rule"), .nav-link:has-text("Price Rule")')
    if rule_tab.first.is_visible():
        rule_tab.first.click()
        page.wait_for_timeout(1000)
        ss(page, "05_pricelist_rules_tab")
        
        # Click "Add a line"
        add_line = page.locator('text=Add a line').first
        if add_line.is_visible():
            add_line.click()
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(2000)
            ss(page, "06_price_rule_form")
            
            # Capture all labels in the form
            labels = page.locator('.o_form_label, label.o_form_label, .o_field_widget label, .o_inner_group label')
            label_count = labels.count()
            print(f"  Form labels found: {label_count}")
            for i in range(min(label_count, 30)):
                lbl = labels.nth(i).text_content().strip()
                if lbl:
                    print(f"    Label: \"{lbl}\"")
    
    # ── 5. Sales Order → Check discount column ──
    print("\n" + "=" * 50)
    print("5. SALES ORDER - DISCOUNT COLUMN")
    print("=" * 50)
    page.goto(f"{URL}/odoo/sales", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)
    
    # Try to open an existing quotation or create new
    new_btn = page.locator('button:has-text("New"), .o_list_button_add')
    if new_btn.first.is_visible():
        new_btn.first.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(2000)
        ss(page, "07_sales_order_form")
        
        # Check order line column headers
        col_headers = page.locator('.o_list_table th, .o_section_and_note_list_view th')
        header_count = col_headers.count()
        print(f"  Order line column headers: {header_count}")
        for i in range(header_count):
            h = col_headers.nth(i).text_content().strip()
            if h:
                print(f"    Column: \"{h}\"")

    # ── 6. Customer form - pricelist field ──
    print("\n" + "=" * 50)
    print("6. CUSTOMER FORM - PRICELIST FIELD")
    print("=" * 50)
    page.goto(f"{URL}/odoo/contacts", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)
    
    # Click first customer
    first_record = page.locator('.o_data_row').first
    if first_record.is_visible():
        first_record.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(2000)
        
        # Click Sales & Purchase tab
        sp_tab = page.locator('.nav-link:has-text("Sales"), .nav-link:has-text("Sales & Purchase")')
        if sp_tab.first.is_visible():
            sp_tab.first.click()
            page.wait_for_timeout(1000)
            ss(page, "08_customer_sales_tab")
            
            # Look for pricelist label
            pl_label = page.locator('label:has-text("Pricelist"), .o_form_label:has-text("Pricelist")')
            if pl_label.first.is_visible():
                print(f"  Pricelist field label found: \"{pl_label.first.text_content().strip()}\"")
            else:
                print("  Pricelist label NOT visible on form")
    
    browser.close()
    print("\nDone! All screenshots saved to blog_verification_screenshots/")
