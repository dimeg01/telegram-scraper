import json
import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("Starting multi-site scraper...")

# -----------------------
# Load config
# -----------------------

with open("config.json") as f:
    config = json.load(f)

SITES = config["sites"]
KEYWORDS = config["keywords"]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", config["telegram_bot_token"])
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", config["telegram_chat_id"])


# -----------------------
# Telegram sender
# -----------------------

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


# -----------------------
# Selenium setup
# -----------------------

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

total_ads = 0


# -----------------------
# Scraping loop
# -----------------------

for site in SITES:

    for keyword in KEYWORDS:

        url = site + keyword

        print(f"\nSearching '{keyword}' on {site}")
        print(url)

        try:

            driver.get(url)

            time.sleep(6)

            links = driver.find_elements(By.TAG_NAME, "a")

            ads_found = 0

            for link in links:

                href = link.get_attribute("href")
                text = link.text

                if not href or not text:
                    continue

                if len(text) < 10:
                    continue

                # basic filter
                if keyword.lower() not in text.lower():
                    continue

                message = f"{text}\n{href}"

                send_telegram(message)

                print("Ad found:", text)

                ads_found += 1
                total_ads += 1

                if ads_found >= 5:
                    break

            print(f"Found {ads_found} ads")

        except Exception as e:
            print("Error:", e)


driver.quit()

print(f"\nScraper finished. Total ads sent: {total_ads}")
