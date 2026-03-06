import requests
from bs4 import BeautifulSoup

SITE = "https://www.reklama5.mk/Search?q=iphone"

r = requests.get(SITE)
print("Status code:", r.status_code)  # треба да биде 200

soup = BeautifulSoup(r.text, "html.parser")

# Точен селектор за Reklama5 огласи
ads = soup.select(".announcement__body")
print("Found ads:", len(ads))

for ad in ads[:5]:  # првите 5 огласи
    title_tag = ad.select_one(".announcement__title")
    price_tag = ad.select_one(".announcement__price")
    link_tag = ad.select_one("a.announcement__link")

    title = title_tag.text.strip() if title_tag else "N/A"
    price = price_tag.text.strip() if price_tag else "N/A"
    link = "https://www.reklama5.mk" + link_tag.get("href") if link_tag else "N/A"

    print(f"{title} | {price} | {link}")
