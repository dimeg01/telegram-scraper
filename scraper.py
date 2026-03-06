import requests

TOKEN = "BOT_TOKEN"
CHAT_ID = "CHAT_ID"

message = "Test message from GitHub Actions"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(url, data=data)

print("Message sent")
