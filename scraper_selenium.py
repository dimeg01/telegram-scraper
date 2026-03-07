import os
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

# Load config
with open("config.json") as f:
    config = json.load(f)

SITES = config.get("sites", [])
KEYWORDS = config.get("keywords", [])

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or config.get("telegram_bot_token")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or config.get("telegram_chat_id")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram token/chat_id missing!")
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
        print("Telegram Response:", r.status_code)
    except Exception as e:
        print("Telegram Error:", e)

# Send start message
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
start_msg = f"🚀 Scraper activated!\nTime: {now}\nSites: {len(SITES)}\nKeywords: {len(KEYWORDS)}"
send_telegram(start_msg)

# Selenium setup
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

MAX_ADS_PER_SITE = 5  # <-- limit to 5 ads per site

for site in SITES:
    for keyword in KEYWORDS:
        url = site + keyword
        print(f"\nSearching '{keyword}' on {site}")
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
            )
        except:
            print("⚠️ Wait timed out")

        links = driver.find_elements(By.TAG_NAME, "a")
        found = 0

        for link_el in links:
            text = link_el.text or ""
            href = link_el.get_attribute("href") or ""

            if keyword.lower() in text.lower() and href.startswith("http"):
                results.append({"text": text, "link": href})
                found += 1
                # Send Telegram immediately
                send_telegram(f"🔎 {keyword}\n{text}\n{href}")

                if found >= MAX_ADS_PER_SITE:  # stop after 5 ads
                    break

        print(f"📊 Found {found} matches on this search")

driver.quit()

print("\n📤 Summary")
print("Total matches found:", len(results))
if len(results) == 0:
    send_telegram("⚠️ No results found on this run.")
else:
    send_telegram(f"✅ Scraper finished with {len(results)} results.")
