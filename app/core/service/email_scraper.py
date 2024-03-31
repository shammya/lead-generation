import os
import sys
import time
import csv
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class FacebookEmailExtractor:
    def __init__(self, input_file_name, fb_col_nm, eml_col_nm):
        self.input_csv_path = input_file_name + ".csv"
        self.output_csv_path = input_file_name + "_res" + ".csv"
        self.fb_col_nm = fb_col_nm
        self.email_col_nm = eml_col_nm
        self.lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=32)
        self.update_thread_pool = ThreadPoolExecutor(max_workers=1)
        self.last_processed_index = 0
        self.emails_dict = {}

        # Create the output CSV file with headers if it doesn't exist
        file_exists = os.path.isfile(self.output_csv_path)
        if not file_exists:
            with open(self.output_csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Facebook", "Emails"])

        logging.basicConfig(
            filename=input_file_name + "_log.log",
            level=logging.INFO,
            format="%(asctime)s:%(levelname)s:%(message)s",
        )

    def ensure_https(self, url):
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

    def setup_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def extract_email_from_facebook(self, driver, url):
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            email_pattern = re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            )
            for span in soup.find_all("span"):
                if span.text and email_pattern.search(span.text):
                    email = email_pattern.search(span.text).group()
                    if email:
                        print(email)
                        # self.store_emails(url, email)
                        self.thread_pool.submit(self.save_email_to_csv, url, email)

        except Exception as e:
            if "HTTP Error 404" in str(e):
                # Facebook page does not exist, skip and move to the next URL
                logging.info(f"Facebook page not found for {url}: {e}")
                return
            elif (
                    "rate limited" in str(e).lower()
                    or "too many requests" in str(e).lower()
            ):
                # Facebook rate limiting detected
                logging.info(f"Facebook rate limiting detected for {url}: {e}")
                if self.adaptive_wait(driver):
                    self.extract_email_from_facebook(driver, url)
                else:
                    self.handle_rate_limit(driver)
            else:
                # Other exceptions
                logging.info(f"Error scraping {url}: {e}")
                self.adaptive_wait(driver)

        return None

    def adaptive_wait(
            self, driver, test_url="https://www.facebook.com/dinelikeasultan/"
    ):
        initial_delay = 180
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            logging.info(
                f"Waiting for {initial_delay} seconds before testing reachability..."
            )
            time.sleep(initial_delay)
            new_driver = self.change_driver(driver)
            try:
                new_driver.get(test_url)
                return True
            except Exception as e:
                logging.info(f"Error accessing test_url: {e}")
                logging.info(
                    f"Encountered an error on attempt {attempt + 1}, will retry after {initial_delay} seconds."
                )

            logging.info(
                f"Still rate-limited or an error occurred. Attempt {attempt + 1} of {max_attempts}."
            )
            attempt += 1
            initial_delay *= 2

        logging.info("Max attempts reached. Please try again later.")
        return False

    def save_email_to_csv(self, url, email):
        # Save the email to CSV
        with self.lock:
            with open(self.output_csv_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([url, email])

    def store_emails(self, url, email):
        self.emails_dict[url] = email

    def update_original_csv_old(self):
        with open(self.input_csv_path, "r") as input_file, open(
                self.input_csv_path, "w", newline=""
        ) as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                url = row[row[0].index(self.fb_col_nm)]
                email = self.emails_dict.get(url, row[row[0].index(self.email_col_nm)])
                row[row[0].index(self.email_col_nm)] = email
                writer.writerow(row)

    def save_email(self, url, email):
        with self.lock:
            self.update_thread_pool.submit(self.update_csv, url, email)

    def update_csv(self, url, email):
        # Read the original CSV file
        df = pd.read_csv(self.input_csv_path)
        df.loc[df[self.fb_col_nm] == url, self.email_col_nm] = email
        df.to_csv(self.input_csv_path, index=False)

    def change_driver(self, driver):
        driver.quit()
        logging.info("Driver has been changed with 20 sec delay")
        time.sleep(20)
        return self.setup_chrome_driver()

    def handle_rate_limit(self, driver):
        driver.quit()
        logging.info(
            f"Rate limit encountered, restarting from row {self.last_processed_index}"
        )
        self.process_facebook_urls()

    def process_facebook_urls(self):
        driver = self.setup_chrome_driver()

        df = pd.read_csv(self.input_csv_path)
        total_rows = len(df)

        for index, row in df.iterrows():
            if index < self.last_processed_index:
                continue

            if index > 0 and index % 50 == 0:
                driver = self.change_driver(driver)

            email = row[self.email_col_nm]
            facebook_url = row[self.fb_col_nm]

            if pd.isnull(email) and not pd.isnull(facebook_url):
                self.extract_email_from_facebook(
                    driver, self.ensure_https(facebook_url)
                )
                self.last_processed_index = index + 1

            if index % 1000 == 0:
                logging.info(f"Processed {index + 1} out of {total_rows} rows.")

        driver.quit()
        self.thread_pool.shutdown(wait=True)
        self.update_thread_pool.shutdown(wait=True)
        logging.info("Email extraction process completed.")

#
# if __name__ == "__main__":
#     input_file_name = sys.argv[1]
#     fb_col_nm = sys.argv[2]
#     eml_col_nm = sys.argv[3]
#     extractor = FacebookEmailExtractor(input_file_name, fb_col_nm, eml_col_nm)
#     start = time.time()
#     extractor.process_facebook_urls()
#     execution_time = time.time() - start
#     logging.info(f"Execution time: {execution_time}")
