from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set Chrome to headless mode for background scraping
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# IKEA search URL for 'center table'
url = "https://www.ikea.com/in/en/search/?q=center%20table"
driver.get(url)

try:
    # Wait until the product list loads
    product_list = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'plp-product-list__products'))
    )

    # Get all product containers
    products = product_list.find_elements(By.CLASS_NAME, 'plp-fragment-wrapper')

    for product in products:
        try:
            # Product name
            name = product.find_element(By.CLASS_NAME, 'plp-price-module__product-name').text.strip()
            
            # Product description
            description = product.find_element(By.CLASS_NAME, 'plp-price-module__description').text.strip()
            
            # Product URL
            url_element = product.find_element(By.CLASS_NAME, 'plp-price-link-wrapper')
            product_url = url_element.get_attribute('href')
            
            # Product price (from data attribute)
            product_div = product.find_element(By.XPATH, ".//div[contains(@class, 'plp-mastercard')]")
            price = product_div.get_attribute('data-price')
            
            # Product image
            image_link_a = product.find_element(By.XPATH, ".//a[contains(@class, 'plp-product__image-link')]")
            image_url = image_link_a.find_element(By.XPATH, ".//img").get_attribute("src")

            print(f"Name: {name}")
            print(f"Description: {description}")
            print(f"Price: ₹{price}")
            print(f"Image URL: {image_url}")
            print(f"Product URL: {product_url}")
            print("-" * 80)

        except Exception as inner_e:
            print("Error extracting product:", inner_e)

finally:
    driver.quit()
