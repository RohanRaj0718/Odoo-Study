#!/usr/bin/env python3
"""
Take screenshots for Work Centers blog — using DIRECT record URLs for reliability.
Uses 2x device scale for crisp images.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

URL = 'https://blog-test.odoo.com'
LOGIN = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'
SCREENSHOT_DIR = r'C:\Odoo Study\wc_screenshots'

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Known record IDs from database check:
# Work Centers: CUT-01=1, CNC-01=2, PNT-01=3, WLD-01=4, ASM-01=5, ASM-02=6, QC-01=7, PKG-01=8
# MO: WH/MO/00001 = ID 2
# BoM for Executive Standing Desk (with 8 ops) — we'll find by product
# Product: Executive Standing Desk = template ID 10

def get_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--force-device-scale-factor=2')
    opts.add_argument('--high-dpi-support=2')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--lang=en-US')
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver

def wait_load(driver, extra=3):
    """Wait for page to fully load."""
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except:
        pass
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".o_loading"))
        )
    except:
        pass
    time.sleep(extra)

def light_theme(driver):
    """Force light theme."""
    driver.execute_script("""
        document.documentElement.setAttribute('data-color-scheme', 'light');
        document.body.classList.remove('o_dark', 'dark');
    """)
    time.sleep(0.5)

def go(driver, path, extra=4):
    """Navigate to path and wait."""
    driver.get(f'{URL}{path}')
    wait_load(driver, extra)
    light_theme(driver)

def snap(driver, name, desc):
    """Take screenshot."""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    driver.save_screenshot(path)
    size = os.path.getsize(path)
    print(f'  [OK] {name}.png ({size:,} bytes) — {desc}')

def click_tab(driver, tab_text):
    """Click a notebook/page tab."""
    selectors = [
        f"//a[contains(@class,'nav-link') and contains(normalize-space(), '{tab_text}')]",
        f"//button[contains(normalize-space(), '{tab_text}')]",
        f"//span[contains(normalize-space(), '{tab_text}')]/parent::a",
        f"//*[contains(@class, 'nav-link') and contains(normalize-space(), '{tab_text}')]",
    ]
    for xpath in selectors:
        try:
            el = driver.find_element(By.XPATH, xpath)
            el.click()
            time.sleep(2)
            return True
        except:
            continue
    print(f'    [WARN] Tab "{tab_text}" not found')
    return False


def main():
    driver = get_driver()

    try:
        # ── Login ──
        print('Logging in...')
        go(driver, '/web/login', extra=2)
        driver.find_element(By.ID, 'login').clear()
        driver.find_element(By.ID, 'login').send_keys(LOGIN)
        driver.find_element(By.ID, 'password').clear()
        driver.find_element(By.ID, 'password').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        wait_load(driver, 5)
        light_theme(driver)
        print('  Logged in!\n')

        # ═══════════════════════════════════════════════════════════════
        # 1. WORK ORDERS SETTINGS
        # ═══════════════════════════════════════════════════════════════
        print('--- 1/8: Work Orders Settings ---')
        go(driver, '/odoo/settings', extra=5)
        # Type in settings search
        try:
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder*="Search"]')
            if inputs:
                inputs[0].clear()
                inputs[0].send_keys('Work Orders')
                time.sleep(4)
        except:
            pass
        light_theme(driver)
        snap(driver, '01_work_orders_settings', 'Settings — Work Orders enabled')

        # ═══════════════════════════════════════════════════════════════
        # 2. WORK CENTER FORM (Cutting Station, ID=1)
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 2/8: Work Center Form ---')
        go(driver, '/odoo/manufacturing/workcenter/1', extra=5)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        snap(driver, '02_work_center_form', 'Cutting Station work center form')

        # ═══════════════════════════════════════════════════════════════
        # 3. ALTERNATIVE WORK CENTERS TAB (Assembly Line, ID=5)
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 3/8: Alternative Work Centers ---')
        go(driver, '/odoo/manufacturing/workcenter/5', extra=5)
        click_tab(driver, 'Alternative')
        time.sleep(2)
        light_theme(driver)
        snap(driver, '03_alternative_workcenters', 'Assembly Line — Alternative Work Centers tab')

        # ═══════════════════════════════════════════════════════════════
        # 4. BOM — COMPONENTS TAB
        # Need to find the BoM ID first. Use the URL /odoo/manufacturing/bom
        # and click on the Executive Standing Desk one
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 4/8: BoM Components ---')
        go(driver, '/odoo/manufacturing/bom', extra=5)
        
        # Click on Executive Standing Desk BoM
        try:
            bom_rows = driver.find_elements(By.XPATH, "//td[contains(text(), 'Executive Standing Desk')]")
            if bom_rows:
                bom_rows[0].click()
                wait_load(driver, 4)
            else:
                # Try span
                bom_links = driver.find_elements(By.XPATH, "//span[contains(text(), 'Executive Standing Desk')]")
                if bom_links:
                    bom_links[0].click()
                    wait_load(driver, 4)
        except Exception as e:
            print(f'    [WARN] Could not click BoM: {e}')

        click_tab(driver, 'Components')
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 200)")
        time.sleep(1)
        light_theme(driver)
        snap(driver, '04_bom_components', 'BoM — Components tab with raw materials')

        # ═══════════════════════════════════════════════════════════════
        # 5. BOM — OPERATIONS TAB (Routing)
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 5/8: BoM Operations (Routing) ---')
        click_tab(driver, 'Operations')
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 200)")
        time.sleep(1)
        light_theme(driver)
        snap(driver, '05_bom_operations', 'BoM — Operations tab showing routing')

        # ═══════════════════════════════════════════════════════════════
        # 6. MANUFACTURING ORDER FORM (WH/MO/00001, ID=2)
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 6/8: Manufacturing Order ---')
        go(driver, '/odoo/manufacturing/2', extra=5)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        light_theme(driver)
        snap(driver, '06_manufacturing_order', 'Manufacturing Order — WH/MO/00001')

        # ═══════════════════════════════════════════════════════════════
        # 7. WORK ORDERS TAB on MO
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 7/8: Work Orders Tab ---')
        click_tab(driver, 'Work Orders')
        time.sleep(2)
        light_theme(driver)
        snap(driver, '07_work_orders_tab', 'MO — Work Orders tab with 8 work orders')

        # Scroll to see all work orders
        driver.execute_script("window.scrollTo(0, 400)")
        time.sleep(1)
        snap(driver, '07b_work_orders_scrolled', 'MO — Work Orders tab scrolled')

        # ═══════════════════════════════════════════════════════════════
        # 8. SHOP FLOOR
        # ═══════════════════════════════════════════════════════════════
        print('\n--- 8/8: Shop Floor ---')
        # Try different URLs for shop floor
        go(driver, '/odoo/shop-floor', extra=6)
        light_theme(driver)
        snap(driver, '08_shop_floor', 'Shop Floor interface')

        # ═══════════════════════════════════════════════════════════════
        # SUMMARY
        # ═══════════════════════════════════════════════════════════════
        print(f'\n{"=" * 60}')
        files = sorted(os.listdir(SCREENSHOT_DIR))
        print(f'  Total screenshots: {len(files)}')
        for f in files:
            fpath = os.path.join(SCREENSHOT_DIR, f)
            size = os.path.getsize(fpath)
            print(f'    {f} ({size:,} bytes)')
        print(f'{"=" * 60}')

    except Exception as e:
        print(f'\n  [ERROR] {e}')
        import traceback
        traceback.print_exc()
        try:
            snap(driver, 'ERROR', str(e)[:80])
        except:
            pass
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
