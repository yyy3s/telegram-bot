import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

message = "رسالة تجريبية من GitHub 🚀"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

data = {
    "chat_id": CHANNEL_ID,
    "text": message
}

response = requests.post(url, data=data)

print(response.status_code)
print(response.text)
