import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

html_files = [
    r"C:\Odoo Study\My learnings\Blogs InDevelopment\odoo_erpnext.html",
    r"C:\Odoo Study\My learnings\Blogs InDevelopment\odoo_zoho.html"
]

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

try:
    print("Opening WordPress login...")
    driver.get("https://www.infintor.com/wp-login.php")
    
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "user_login"))).send_keys("rohan.raj@infintor.com")
    driver.find_element(By.ID, "user_pass").send_keys("iIGw0%UUgu")
    
    print("\n>>> PLEASE SOLVE THE MATH CAPTCHA IN THE BROWSER AND CLICK 'LOG IN' <<<")
    print("Waiting up to 120 seconds for successful login...")
    
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "wpadminbar")))
    print("Logged in successfully!")

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        title_match = re.search(r'^<h1>(.*?)</h1>', raw_html)
        actual_title = title_match.group(1) if title_match else "Blog Draft"
        
        cleaned_html = re.sub(r'^<h1>.*?</h1>', '', raw_html, count=1)
        cleaned_html = re.sub(r'^<(h1|h2|p)>.*?Rohan Raj.*?</\1>', '', cleaned_html, flags=re.IGNORECASE, count=1)
        cleaned_html = cleaned_html.replace('\n', ' ')

        print(f"Navigating to Add New Post for: '{actual_title}'...")
        driver.get("https://www.infintor.com/wp-admin/post-new.php")
        
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return typeof wp !== 'undefined' && wp.data !== undefined"))
        time.sleep(5)
        
        print(f"Injecting Title: '{actual_title}' and Native Blocks via WP Data API...")
        driver.execute_script("wp.data.dispatch('core/editor').editPost({title: arguments[0]});", actual_title)
        
        insert_js = "wp.data.dispatch('core/block-editor').insertBlocks(wp.blocks.parse(arguments[0]));"
        driver.execute_script(insert_js, cleaned_html)
        
        time.sleep(3)
        print("Saving draft via WP Data API...")
        driver.execute_script("wp.data.dispatch('core/editor').savePost();")
        
        # we will grab the SEO performance directly from the page using JS if available!
        # Yoast or RankMath usually updates a hidden input or exposes a global JS object.
        # Instead of guessing the highly complex RankMath/Yoast DOM structures, we will let the draft save, then log the success!
        time.sleep(5)
        print(f"Draft saved successfully for: {actual_title}!\n")

    print("Both drafts completely saved! Leaving browser open for 30 seconds.")
    time.sleep(30)

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()
