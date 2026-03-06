import os
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# Install correct chromedriver
chromedriver_autoinstaller.install()

# Load config
with open("config.json") as f:
    config = json.load(f)

SITE = config["site"]
KEYWORDS = config["keywords"]

# Telegram
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("Starting Reklama5 scraper...")

options = Options()
options.add_argument("--headless=new")   # headless Chrome
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

results = []

for keyword in KEYWORDS:
    url = SITE + keyword
    print(f"Searching: {keyword} -> {url}")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    ads = soup.select(".announcement__body")
    print(f"Found {len(ads)} ads")

    for ad in ads:
        title_tag = ad.select_one(".announcement__title")
        price_tag = ad.select_one(".announcement__price")
        link_tag = ad.select_one("a.announcement__link")
        date_tag = ad.select_one(".announcement__date")

        if not title_tag or not link_tag or not date_tag:
            continue

        title = title_tag.text.strip()
        price = price_tag.text.strip() if price_tag else "N/A"
        link = "https://www.reklama5.mk" + link_tag.get("href")
        date_text = date_tag.text.strip()

        if "денес" in date_text.lower() or "час" in date_text.lower():
            results.append({"title": title, "price": price, "link": link})
            print(f"{title} | {price} | {link}")

driver.quit()

# Send Telegram
if TOKEN and CHAT_ID and results:
    for r in results:
        message = f"{r['title']}\nЦена: {r['price']}\n{r['link']}"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": message})

print(f"Scraper finished. Total ads: {len(results)}")
