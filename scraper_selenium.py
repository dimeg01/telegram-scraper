import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# Автоматски инсталира точниот ChromeDriver
chromedriver_autoinstaller.install()

# Load config
with open("config.json") as f:
    config = json.load(f)

SITES = config["sites"]           # Листа од сајтови
KEYWORDS = config["keywords"]     # Листа од keywords

# Telegram secrets од env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", config.get("telegram_bot_token"))
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", config.get("telegram_chat_id"))

print("Starting multi-site Selenium scraper...")

# Headless Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
results = []

# -----------------------
# Scraping loop
# -----------------------
for site in SITES:
    for keyword in KEYWORDS:

        url = site + keyword
        print(f"\nSearching keyword: {keyword} -> {url}")
        driver.get(url)

        # Чека до 20 секунди да се load-ираат огласите
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".announcement__body"))
            )
        except:
            print("No ads found after waiting 20s")

        ads = driver.find_elements(By.CSS_SELECTOR, ".announcement__body")
        print(f"Found {len(ads)} ads")

        for ad in ads:
            try:
                title = ad.find_element(By.CSS_SELECTOR, ".announcement__title").text.strip()
                price_el = ad.find_elements(By.CSS_SELECTOR, ".announcement__price")
                price = price_el[0].text.strip() if price_el else "N/A"
                link = ad.find_element(By.CSS_SELECTOR, "a.announcement__link").get_attribute("href")
                date_text = ad.find_element(By.CSS_SELECTOR, ".announcement__date").text.strip()
            except:
                continue

            # Филтрира само огласи од последни 24h
            if "денес" in date_text.lower() or "час" in date_text.lower():
                results.append({"title": title, "price": price, "link": link})
                print(f"{title} | {price} | {link}")

driver.quit()

# Испрати Telegram пораки ако има резултати
if TOKEN and CHAT_ID and results:
    for r in results:
        message = f"{r['title']}\nЦена: {r['price']}\n{r['link']}"
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

print(f"\nScraper finished. Total ads found in last 24h: {len(results)}")
