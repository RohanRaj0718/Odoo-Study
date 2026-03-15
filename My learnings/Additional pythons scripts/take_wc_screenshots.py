#!/usr/bin/env python3
"""
Take HIGH-QUALITY screenshots from blog-test.odoo.com for the Work Centers blog.
Uses Selenium + Chrome headless with:
- 2x device scale for sharp images
- Explicit waits for full page render
- Direct URL navigation to exact records
- Light theme forced
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = 'https://blog-test.odoo.com'
LOGIN = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'
SCREENSHOT_DIR = r'C:\Odoo Study\wc_screenshots'

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def get_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--window-size=1920,1080')
    # 2x scale factor for crisp screenshots
    opts.add_argument('--force-device-scale-factor=2')
    opts.add_argument('--high-dpi-support=2')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--lang=en-US')
    opts.add_argument('--disable-animations')
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(15)
    return driver

def wait_full_load(driver, timeout=25):
    """Wait until page is fully loaded — DOM ready + no spinners + no loading bars."""
    # Wait for DOM ready
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    # Wait for Odoo loading overlay to vanish
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".o_loading"))
        )
    except:
        pass
    # Wait for any .o_blockUI overlay
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".o_blockUI"))
        )
    except:
        pass
    # Wait for body to not have .o_loading class
    try:
        WebDriverWait(driver, 5).until(
            lambda d: 'o_loading' not in (d.find_element(By.TAG_NAME, 'body').get_attribute('class') or '')
        )
    except:
        pass
    # Extra settle time for rendering
    time.sleep(3)

def force_light_theme(driver):
    """Force light theme via CSS and DOM."""
    driver.execute_script("""
        // Remove dark mode classes
        document.documentElement.removeAttribute('data-color-scheme');
        document.documentElement.setAttribute('data-color-scheme', 'light');
        document.body.classList.remove('o_dark', 'dark');
        document.body.classList.add('o_light');
        
        // Override any dark CSS variables
        var style = document.createElement('style');
        style.textContent = `
            :root {
                color-scheme: light !important;
            }
            body.o_dark { 
                filter: none !important; 
            }
        `;
        document.head.appendChild(style);
    """)
    time.sleep(1)

def screenshot(driver, name, desc=""):
    """Save a screenshot with a descriptive name."""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    driver.save_screenshot(path)
    size = os.path.getsize(path)
    print(f'  [OK] {name}.png ({size:,} bytes) — {desc}')
    return path

def navigate(driver, path, wait_extra=3):
    """Navigate to a URL and wait for full load."""
    full_url = f'{URL}{path}'
    driver.get(full_url)
    wait_full_load(driver)
    force_light_theme(driver)
    time.sleep(wait_extra)

def scroll_to_top(driver):
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(0.5)

def scroll_to(driver, y):
    driver.execute_script(f"window.scrollTo(0, {y})")
    time.sleep(0.5)

def click_element_text(driver, text, tag='*', timeout=10):
    """Click an element containing specific text."""
    xpath = f"//{tag}[contains(text(), '{text}')]"
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    el.click()
    wait_full_load(driver)

def click_tab(driver, tab_name, timeout=10):
    """Click a notebook tab by name."""
    try:
        tab = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@class,'nav-link') and contains(text(), '{tab_name}')]"))
        )
        tab.click()
        time.sleep(2)
        return True
    except:
        # Try button-style tabs
        try:
            tab = driver.find_element(By.XPATH, f"//button[contains(text(), '{tab_name}')]")
            tab.click()
            time.sleep(2)
            return True
        except:
            print(f'  [WARN] Could not find tab: {tab_name}')
            return False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    driver = get_driver()
    
    try:
        # ── Login ──────────────────────────────────────────────────────────
        print('Logging in...')
        navigate(driver, '/web/login', wait_extra=2)
        
        driver.find_element(By.ID, 'login').clear()
        driver.find_element(By.ID, 'login').send_keys(LOGIN)
        driver.find_element(By.ID, 'password').clear()
        driver.find_element(By.ID, 'password').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        wait_full_load(driver, 30)
        force_light_theme(driver)
        print('  Logged in!\n')
        
        # ══════════════════════════════════════════════════════════════════
        # 1. Work Orders Settings
        # Manufacturing => Configuration => Settings => Work Orders checkbox
        # ══════════════════════════════════════════════════════════════════
        print('--- 1/8: Work Orders Settings ---')
        navigate(driver, '/odoo/settings', wait_extra=5)
        
        # Search for "Work Orders" in settings to focus the view
        try:
            search_input = driver.find_element(By.CSS_SELECTOR, 'input.o_searchview_input')
            search_input.clear()
            search_input.send_keys('Work Orders')
            search_input.send_keys(Keys.ENTER)
            time.sleep(4)
        except:
            # Try the settings search bar
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, '.o_settings_search input')
                search_box.clear()
                search_box.send_keys('Work Orders')
                time.sleep(4)
            except:
                pass
        
        force_light_theme(driver)
        screenshot(driver, '01_work_orders_settings', 'Manufacturing Settings — Work Orders enabled')
        
        # ══════════════════════════════════════════════════════════════════
        # 2. Work Center Form (Cutting Station — CUT-01, ID 1)
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 2/8: Work Center Form ---')
        # Navigate to work center list, then open Cutting Station
        navigate(driver, '/odoo/manufacturing/workcenter', wait_extra=4)
        
        try:
            click_element_text(driver, 'Cutting Station', 'td')
        except:
            try:
                click_element_text(driver, 'Cutting Station', 'span')
            except:
                # Direct navigation via record ID
                navigate(driver, '/odoo/manufacturing/workcenter/1', wait_extra=4)
        
        scroll_to_top(driver)
        time.sleep(2)
        force_light_theme(driver)
        screenshot(driver, '02_work_center_form', 'Cutting Station (CUT-01) Work Center form')
        
        # ══════════════════════════════════════════════════════════════════
        # 3. Alternative Work Centers Tab (Assembly Line — ASM-01, ID 5)
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 3/8: Alternative Work Centers Tab ---')
        navigate(driver, '/odoo/manufacturing/workcenter', wait_extra=4)
        
        try:
            click_element_text(driver, 'Assembly Line', 'td')
        except:
            try:
                # Might match multiple — try to be specific
                rows = driver.find_elements(By.XPATH, "//td[contains(text(), 'Assembly Line') and not(contains(text(), 'Advanced'))]")
                if rows:
                    rows[0].click()
                    wait_full_load(driver)
                else:
                    navigate(driver, '/odoo/manufacturing/workcenter/5', wait_extra=4)
            except:
                navigate(driver, '/odoo/manufacturing/workcenter/5', wait_extra=4)
        
        # Click on Alternative Work Centers tab
        time.sleep(2)
        clicked = click_tab(driver, 'Alternative')
        if not clicked:
            # Try scrolling down to find it
            scroll_to(driver, 400)
            click_tab(driver, 'Alternative')
        
        force_light_theme(driver)
        screenshot(driver, '03_alternative_workcenters', 'Assembly Line — Alternative Work Centers tab')
        
        # ══════════════════════════════════════════════════════════════════
        # 4. BoM Components Tab (Executive Standing Desk BoM)
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 4/8: BoM Components Tab ---')
        navigate(driver, '/odoo/manufacturing/bom', wait_extra=4)
        
        # Find the Executive Standing Desk BoM (type=normal with 8 ops)
        try:
            click_element_text(driver, 'Executive Standing Desk', 'td')
        except:
            try:
                click_element_text(driver, 'Executive Standing Desk', 'span')
            except:
                pass
        
        time.sleep(2)
        # Make sure Components tab is active (it's usually the default)
        click_tab(driver, 'Components')
        time.sleep(1)
        
        scroll_to_top(driver)
        force_light_theme(driver)
        # Scroll just enough to see the components tab content
        scroll_to(driver, 200)
        time.sleep(1)
        screenshot(driver, '04_bom_components', 'BoM Components tab — Executive Standing Desk')
        
        # ══════════════════════════════════════════════════════════════════
        # 5. BoM Operations Tab (Routing)
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 5/8: BoM Operations Tab ---')
        # Still on BoM form — click Operations tab
        clicked = click_tab(driver, 'Operations')
        if not clicked:
            click_tab(driver, 'Operation')
        
        time.sleep(2)
        force_light_theme(driver)
        screenshot(driver, '05_bom_operations', 'BoM Operations tab — Routing with 8 operations')
        
        # Scroll down to see all operations if they don't fit
        scroll_to(driver, 400)
        time.sleep(1)
        screenshot(driver, '05b_bom_operations_full', 'BoM Operations tab — scrolled to see all')
        
        # ══════════════════════════════════════════════════════════════════
        # 6. Manufacturing Order Form (WH/MO/00001, ID 2)
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 6/8: Manufacturing Order Form ---')
        navigate(driver, '/odoo/manufacturing', wait_extra=4)
        
        try:
            click_element_text(driver, 'WH/MO/00001', 'td')
        except:
            try:
                click_element_text(driver, 'WH/MO/00001', 'span')
            except:
                try:
                    click_element_text(driver, 'Executive Standing Desk', 'td')
                except:
                    pass
        
        time.sleep(2)
        scroll_to_top(driver)
        force_light_theme(driver)
        screenshot(driver, '06_manufacturing_order', 'Manufacturing Order WH/MO/00001 — Executive Standing Desk')
        
        # ══════════════════════════════════════════════════════════════════
        # 7. Work Orders Tab on the Manufacturing Order
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 7/8: Work Orders Tab ---')
        # Click Work Orders tab
        clicked = click_tab(driver, 'Work Orders')
        if not clicked:
            click_tab(driver, 'Work Order')
        
        time.sleep(2)
        force_light_theme(driver)
        screenshot(driver, '07_work_orders_tab', 'Work Orders tab — 8 work orders generated')
        
        # Scroll to see all work orders
        scroll_to(driver, 500)
        time.sleep(1)
        screenshot(driver, '07b_work_orders_full', 'Work Orders tab — scrolled to see all 8')
        
        # ══════════════════════════════════════════════════════════════════
        # 8. Shop Floor Interface
        # ══════════════════════════════════════════════════════════════════
        print('\n--- 8/8: Shop Floor Interface ---')
        navigate(driver, '/odoo/shop-floor', wait_extra=5)
        force_light_theme(driver)
        screenshot(driver, '08_shop_floor', 'Shop Floor interface')
        
        # Also try the manufacturing shop floor URL
        navigate(driver, '/odoo/manufacturing/shop-floor', wait_extra=5)
        force_light_theme(driver)
        screenshot(driver, '08b_shop_floor_alt', 'Shop Floor alternative URL')
        
        # ══════════════════════════════════════════════════════════════════
        # Summary
        # ══════════════════════════════════════════════════════════════════
        print(f'\n{"=" * 60}')
        print(f'  All screenshots saved to: {SCREENSHOT_DIR}')
        files = sorted(os.listdir(SCREENSHOT_DIR))
        print(f'  Total files: {len(files)}')
        for f in files:
            fpath = os.path.join(SCREENSHOT_DIR, f)
            size = os.path.getsize(fpath)
            print(f'    {f} ({size:,} bytes)')
        print(f'{"=" * 60}')
        
    except Exception as e:
        print(f'\n  [ERROR] {e}')
        import traceback
        traceback.print_exc()
        # Save error screenshot
        try:
            screenshot(driver, 'ERROR_screenshot', f'Error: {str(e)[:80]}')
        except:
            pass
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
