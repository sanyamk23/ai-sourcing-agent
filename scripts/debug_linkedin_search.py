"""
Debug script to inspect LinkedIn search page structure
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

def debug_linkedin_search():
    driver = uc.Chrome(headless=False)
    
    try:
        # Login
        print("Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        
        username = os.getenv('LINKEDIN_USERNAME')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        driver.find_element(By.ID, "username").send_keys(username)
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(password)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        print("Waiting for login...")
        time.sleep(8)
        
        # Search
        keywords = quote_plus("Python Developer")
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
        
        print(f"Navigating to: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # Scroll
        print("Scrolling...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Try different selectors
        selectors_to_try = [
            ".reusable-search__result-container",
            ".search-results-container",
            "[data-chameleon-result-urn]",
            ".entity-result",
            ".search-result",
            "li.reusable-search__result-container",
            "div.entity-result__item",
            ".artdeco-list__item",
            "[class*='search-result']",
            "[class*='entity-result']"
        ]
        
        print("\n" + "="*60)
        print("TESTING SELECTORS:")
        print("="*60)
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"✓ {selector:50s} -> {len(elements)} elements")
                if len(elements) > 0:
                    print(f"  First element classes: {elements[0].get_attribute('class')}")
            except Exception as e:
                print(f"✗ {selector:50s} -> Error: {e}")
        
        # Save page source
        print("\n" + "="*60)
        print("Saving page source to linkedin_search_page.html")
        with open("linkedin_search_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ Page source saved")
        
        # Keep browser open for manual inspection
        print("\n" + "="*60)
        print("Browser will stay open for 30 seconds for manual inspection...")
        print("Check the page and press Ctrl+C to close early")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\nClosing...")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_linkedin_search()
