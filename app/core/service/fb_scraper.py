from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
import time
import csv

from app.core.global_objects import settings


# def setup_chrome_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     service = Service(ChromeDriverManager(driver_version="114.0.5735.90").install())
#     return webdriver.Chrome(service=service, options=chrome_options)


def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chromedriver_path = settings.webdriver_path
    service = Service(executable_path=chromedriver_path)

    return webdriver.Chrome(service=service, options=chrome_options)


def ensure_https(url):
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def append_row_to_csv(cell1, cell2):
    # Open the file in append mode ('a')
    file_path = "test_output.csv"
    with open(file_path, "a", newline="") as csvfile:
        # Create a CSV writer object
        csvwriter = csv.writer(csvfile)
        # Write the row with two cells to the CSV
        csvwriter.writerow([cell1, cell2])


# function to find the facebook link forma website link
def find_facebook_url(url):
    driver = setup_chrome_driver()
    facebook_icon_selector = 'a[href*="facebook.com"]'
    try:
        driver.get(ensure_https(url))
        facebook_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, facebook_icon_selector))
        )
        # Once clickable, we assume it's safe to retrieve the URL
        facebook_url = facebook_icon.get_attribute("href")
        return url, facebook_url
    except Exception as e:
        return url, None
    finally:
        driver.quit()


# function to process a list of websites to figure out their facebook url
def process_websites(websites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {
            executor.submit(find_facebook_url, url): url for url in websites
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                _, facebook_url = future.result()
                if facebook_url:
                    # print(f"Facebook URL for {url}: {facebook_url}")
                    append_row_to_csv(url, facebook_url)
                else:
                    # print(f"No Facebook URL found for {url}")
                    append_row_to_csv(url, "")
            except Exception as e:
                print(f"Error processing {url}: {e}")
