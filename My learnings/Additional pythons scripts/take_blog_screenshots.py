#!/usr/bin/env python3
"""
Take screenshots from blog-test.odoo.com for the Subcontracting blog.
Uses Selenium + Chrome headless with light theme.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

URL = 'https://blog-test.odoo.com'
LOGIN = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'
SCREENSHOT_DIR = r'C:\Odoo Study\blog_screenshots'

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def get_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--force-device-scale-factor=1')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--lang=en-US')
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver

def wait_for_page_load(driver, timeout=20):
    """Wait until the page is fully loaded (no loading spinner)."""
    time.sleep(2)
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except:
        pass
    # Wait for Odoo loading overlay to disappear
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".o_loading"))
        )
    except:
        pass
    time.sleep(1)

def login(driver):
    """Login to Odoo."""
    print("Logging in...")
    driver.get(f'{URL}/web/login')
    wait_for_page_load(driver)
    
    login_field = driver.find_element(By.ID, 'login')
    login_field.clear()
    login_field.send_keys(LOGIN)
    
    pwd_field = driver.find_element(By.ID, 'password')
    pwd_field.clear()
    pwd_field.send_keys(PASSWORD)
    
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    wait_for_page_load(driver, 30)
    print("  Logged in!")

def switch_to_light_theme(driver):
    """Switch to light theme via user preferences."""
    print("Switching to light theme...")
    # Go to user preferences
    driver.get(f'{URL}/odoo/settings/users')
    wait_for_page_load(driver)
    time.sleep(2)
    
    # Try to set light theme via JS
    try:
        driver.execute_script("""
            document.documentElement.setAttribute('data-color-scheme', 'light');
            document.body.classList.remove('o_dark');
        """)
        time.sleep(1)
        print("  Light theme set via JS!")
    except:
        print("  Could not set theme via JS, continuing...")

def screenshot(driver, name, description=""):
    """Take a screenshot and save it."""
    filepath = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    driver.save_screenshot(filepath)
    size = os.path.getsize(filepath)
    print(f'  Screenshot: {name}.png ({size:,} bytes) - {description}')
    return filepath

def navigate_via_url(driver, path, wait=3):
    """Navigate to a URL path and wait for load."""
    driver.get(f'{URL}{path}')
    wait_for_page_load(driver)
    time.sleep(wait)

def main():
    driver = get_driver()
    
    try:
        login(driver)
        switch_to_light_theme(driver)
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 1: Subcontracting Settings
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 1: Subcontracting Settings ---")
        navigate_via_url(driver, '/odoo/settings')
        wait_for_page_load(driver)
        time.sleep(3)
        
        # Try to find Manufacturing settings section
        try:
            # Click on Manufacturing section in settings
            mfg_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Manufacturing')]")
            if not mfg_links:
                mfg_links = driver.find_elements(By.XPATH, "//*[contains(text(), 'Manufacturing')]")
            if mfg_links:
                mfg_links[0].click()
                wait_for_page_load(driver)
                time.sleep(2)
        except:
            pass
        
        # Try direct URL for manufacturing settings
        navigate_via_url(driver, '/odoo/settings?searchTerms=Subcontracting')
        time.sleep(3)
        screenshot(driver, '01_subcontracting_settings', 'Manufacturing Settings with Subcontracting')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 2: Subcontractor Contact Form  
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 2: Subcontractor Contact ---")
        # Find ProAssemble Subcontractors contact
        navigate_via_url(driver, '/odoo/contacts')
        time.sleep(3)
        
        # Click on ProAssemble
        try:
            contact = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'ProAssemble')]"))
            )
            contact.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            # Try searching
            try:
                search = driver.find_element(By.CSS_SELECTOR, '.o_searchview_input')
                search.send_keys('ProAssemble')
                search.send_keys(Keys.ENTER)
                time.sleep(3)
                contact = driver.find_element(By.XPATH, "//span[contains(text(), 'ProAssemble')]")
                contact.click()
                wait_for_page_load(driver)
                time.sleep(2)
            except:
                pass
        
        screenshot(driver, '02_subcontractor_contact', 'ProAssemble Subcontractors contact form')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 3: Product Form (ErgoChair Pro)
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 3: Product Form ---")
        navigate_via_url(driver, '/odoo/manufacturing/products')
        time.sleep(3)
        
        try:
            product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'ErgoChair')]"))
            )
            product.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            try:
                search = driver.find_element(By.CSS_SELECTOR, '.o_searchview_input')
                search.send_keys('ErgoChair')
                search.send_keys(Keys.ENTER)
                time.sleep(3)
                product = driver.find_element(By.XPATH, "//*[contains(text(), 'ErgoChair')]")
                product.click()
                wait_for_page_load(driver)
                time.sleep(2)
            except:
                pass
        
        screenshot(driver, '03_product_form', 'ErgoChair Pro product form')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 4 & 5: BoM with Subcontracting type + Components
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 4: BoM Type Subcontracting ---")
        navigate_via_url(driver, '/odoo/manufacturing/bom')
        time.sleep(3)
        
        try:
            bom = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'ErgoChair')]"))
            )
            bom.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            pass
        
        # Scroll to top for BoM type
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        screenshot(driver, '04_bom_subcontracting_type', 'BoM Type set to Subcontracting')
        
        print("\n--- Screenshot 5: BoM Components ---")
        # Scroll down to see components
        driver.execute_script("window.scrollTo(0, 300)")
        time.sleep(1)
        screenshot(driver, '05_bom_components', 'Components tab on BoM')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 6: Vendor Pricelist (Purchase Tab)
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 6: Vendor Pricelist ---")
        # Go back to product and click Purchase tab
        navigate_via_url(driver, '/odoo/manufacturing/products')
        time.sleep(3)
        
        try:
            product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'ErgoChair')]"))
            )
            product.click()
            wait_for_page_load(driver)
            time.sleep(2)
            
            # Click Purchase tab
            purchase_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Purchase')]")
            purchase_tab.click()
            time.sleep(2)
        except:
            pass
        
        screenshot(driver, '06_vendor_pricelist', 'Vendor pricelist on Purchase tab')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 7: Purchase Order  
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 7: Purchase Order ---")
        navigate_via_url(driver, '/odoo/purchase')
        time.sleep(3)
        
        try:
            po = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'P00001')]"))
            )
            po.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            pass
        
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        screenshot(driver, '07_purchase_order', 'Confirmed Purchase Order')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 8: Smart Buttons on PO (Receipt/Resupply)
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 8: Smart Buttons ---")
        # Should still be on PO page - capture the top area with smart buttons
        screenshot(driver, '08_smart_buttons', 'Smart buttons on Purchase Order')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 9: Resupply Transfer
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 9: Resupply Transfer ---")
        navigate_via_url(driver, '/odoo/inventory/operations/resupply-subcontractor')
        time.sleep(3)
        
        # Try clicking on the transfer
        try:
            transfer = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'WH/RES/')]"))
            )
            transfer.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            # Try inventory transfers  
            navigate_via_url(driver, '/odoo/inventory')
            time.sleep(3)
            try:
                resupply_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Resupply Subcontractor')]")
                resupply_btn.click()
                time.sleep(3)
                transfer = driver.find_element(By.XPATH, "//*[contains(text(), 'WH/RES/')]")
                transfer.click()
                wait_for_page_load(driver)
                time.sleep(2)
            except:
                pass
        
        screenshot(driver, '09_resupply_transfer', 'Resupply Subcontractor transfer')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 10: Subcontracting Receipt
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 10: Subcontracting Receipt ---")
        navigate_via_url(driver, '/odoo/inventory/operations/receipts')
        time.sleep(3)
        
        try:
            receipt = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'WH/IN/')]"))
            )
            receipt.click()
            wait_for_page_load(driver)
            time.sleep(2)
        except:
            pass
        
        screenshot(driver, '10_subcontracting_receipt', 'Subcontracting Receipt')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 11: Dropshipping Settings (Purchase settings)
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 11: Dropshipping Settings ---")
        navigate_via_url(driver, '/odoo/settings?searchTerms=Dropshipping')
        time.sleep(3)
        screenshot(driver, '11_dropshipping_settings', 'Dropshipping in Purchase settings')
        
        # ══════════════════════════════════════════════════════════════
        # Screenshot 12: Dropship flow placeholder (inventory overview)
        # ══════════════════════════════════════════════════════════════
        print("\n--- Screenshot 12: Dropship Subcontracting Flow ---")
        navigate_via_url(driver, '/odoo/inventory')
        time.sleep(3)
        screenshot(driver, '12_dropship_flow', 'Inventory overview for dropship flow')
        
        print(f'\n{"=" * 60}')
        print(f'  All screenshots saved to: {SCREENSHOT_DIR}')
        files = os.listdir(SCREENSHOT_DIR)
        print(f'  Total files: {len(files)}')
        for f in sorted(files):
            size = os.path.getsize(os.path.join(SCREENSHOT_DIR, f))
            print(f'    {f} ({size:,} bytes)')
        print(f'{"=" * 60}')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
