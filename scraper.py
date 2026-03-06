import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load config
with open("config.json") as f:
    config = json.load(f)

SITE = config["site"]
KEYWORDS = config["keywords"]
TOKEN = config["telegram_bot_token"]
CHAT_ID = config["telegram_chat_id"]

results = []

for keyword in KEYWORDS:

    url = SITE + keyword
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # Tочен селектор за Reklama5 огласи
    ads = soup.select(".announcement__body")

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

        # Филтер за последни 24 часа
        if "денес" in date_text.lower() or "час" in date_text.lower():
            results.append({
                "title": title,
                "price": price,
                "link": link
            })

# Испрати на Telegram
for r in results:
    message = f"{r['title']}\nЦена: {r['price']}\n{r['link']}"
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})
