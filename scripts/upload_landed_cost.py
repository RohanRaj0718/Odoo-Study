import os
import time
import re
import markdown
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Convert MD to HTML
md_file = r"c:\Odoo Study\My learnings\Blogs InDevelopment\Landed_Cost_Calculation_Odoo19.md"
html_file = r"c:\Odoo Study\My learnings\Blogs InDevelopment\landed_cost_odoo19.html"

print("Converting Markdown to HTML...")
with open(md_file, "r", encoding="utf-8") as f:
    text = f.read()

html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
title = "Mastering Landed Cost Calculation in Odoo 19"

with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"<h1>{title}</h1>\n{html}")
print("HTML generated.")

# 2. Upload to WP
print("\nLaunching Chrome for WordPress Upload...")
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

    with open(html_file, 'r', encoding='utf-8') as f:
        raw_html = f.read()

    # Clean the first title tag
    cleaned_html = re.sub(r'^<(h1|h2)>.*?</\1>', '', raw_html, count=1, flags=re.IGNORECASE)
    cleaned_html = cleaned_html.replace('\n', ' ')

    print(f"Navigating to Add New Post for: '{title}'...")
    driver.get("https://www.infintor.com/wp-admin/post-new.php")
    
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return typeof wp !== 'undefined' && wp.data !== undefined"))
    time.sleep(5)
    
    print(f"Injecting Title: '{title}' and Native Blocks via WP Data API...")
    driver.execute_script("wp.data.dispatch('core/editor').editPost({title: arguments[0]});", title)
    
    insert_js = "wp.data.dispatch('core/block-editor').insertBlocks(wp.blocks.parse(arguments[0]));"
    driver.execute_script(insert_js, cleaned_html)
    
    time.sleep(3)
    print("Saving draft via WP Data API...")
    driver.execute_script("wp.data.dispatch('core/editor').savePost();")
    
    time.sleep(5)
    print(f"Draft saved successfully for: {title}!\n")

    print("Draft completely saved! Leaving browser open for 30 seconds.")
    time.sleep(30)

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()
