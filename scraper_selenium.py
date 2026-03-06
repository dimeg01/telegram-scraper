import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Load config (само keywords и site, токени ќе се читаат од env)
with open("config.json") as f:
    config = json.load(f)

SITE = config["site"]
KEYWORDS = config["keywords"]

# Telegram secrets од env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("Starting Reklama5 Selenium scraper...")

# Setup headless Chrome
options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

results = []

for keyword in KEYWORDS:
    print(f"\nSearching keyword: {keyword}")
    url = SITE + keyword
    print("URL:", url)

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # CSS селектор за Reklama5 огласи
    ads = soup.select(".announcement__body")
    print("Found ads:", len(ads))

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

        # Filter only last 24h (денес/час)
        if "денес" in date_text.lower() or "час" in date_text.lower():
            results.append({
                "title": title,
                "price": price,
                "link": link
            })
            print(f"Title: {title}\nPrice: {price}\nLink: {link}\n---")

driver.quit()

# Send Telegram messages if TOKEN and CHAT_ID exist
if TOKEN and CHAT_ID and results:
    import requests
    for r in results:
        message = f"{r['title']}\nЦена: {r['price']}\n{r['link']}"
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        resp = requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})
        print("Telegram response:", resp.text)

print(f"\nScraper finished. Total ads found in last 24h: {len(results)}")
