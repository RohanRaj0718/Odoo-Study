import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

out_file = r"c:\Odoo Study\My learnings\Blogs InDevelopment\seo_dump.txt"

print("\nLaunching Chrome to read SEO data...")
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

try:
    print("Opening WordPress login...")
    driver.get("https://www.infintor.com/wp-login.php")
    
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "user_login"))).send_keys("rohan.raj@infintor.com")
    driver.find_element(By.ID, "user_pass").send_keys("iIGw0%UUgu")
    
    print("\n>>> PLEASE SOLVE THE MATH CAPTCHA AND CLICK 'LOG IN' <<<")
    
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "wpadminbar")))
    print("Logged in successfully!")

    url = "https://www.infintor.com/wp-admin/post.php?post=35737&action=edit"
    print(f"Navigating precisely to: {url}")
    driver.get(url)
    
    # Wait for the Gutenberg editor to fully initialize
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return typeof wp !== 'undefined' && wp.data !== undefined"))
    
    print("\n>>> PLEASE OPEN THE SEO/READABILITY SIDEBAR PANEL SO I CAN READ IT! <<<")
    print("Waiting 15 seconds for you to open the Yoast/RankMath checklist...")
    time.sleep(15)
    
    print("Extracting SEO text now...")
    # Grab the entire innerText of the body to ensure we capture any expanded SEO panels
    page_text = driver.execute_script("return document.body.innerText;")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page_text)
        
    print(f"Successfully dumped SEO analysis to: {out_file}\n")
    print("Closing browser in 5 seconds...")
    time.sleep(5)

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()
