import json
import requests
from bs4 import BeautifulSoup

# load config
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

    ads = soup.select("a")  # пример selector

    for ad in ads:

        title = ad.text.strip()
        link = ad.get("href")

        if keyword.lower() in title.lower():

            results.append({
                "title": title,
                "link": link
            })

for r in results:

    message = f"{r['title']}\n{r['link']}"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)
