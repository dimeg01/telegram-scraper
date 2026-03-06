import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load config
with open("config.json") as f:
    config = json.load(f)

SITE = config["site"]
KEYWORDS = config["keywords"]

print("Starting Reklama5 scraper test...")
results = []

for keyword in KEYWORDS:
    print("\nSearching keyword:", keyword)
    url = SITE + keyword
    print("URL:", url)

    r = requests.get(url)
    print("Status code:", r.status_code)

    if r.status_code != 200:
        print("Failed to fetch page!")
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    # CSS селектор за огласите
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

        # Филтер за последни 24 часа
        if "денес" in date_text.lower() or "час" in date_text.lower():
            results.append({
                "title": title,
                "price": price,
                "link": link
            })
            print(f"Title: {title}\nPrice: {price}\nLink: {link}\n---")

print("\nScraper test finished.")
print(f"Total ads found in last 24h: {len(results)}")
