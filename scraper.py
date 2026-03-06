import requests

TOKEN = "8298983737:AAFBf4RUsED0dXjhOyeRlTNjj0W4hkMRrlM"
CHAT_ID = "528508377"

message = "Test message from GitHub Actions"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(url, data=data)

print("Message sent")
