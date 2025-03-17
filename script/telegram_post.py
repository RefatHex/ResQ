import requests
from decouple import config

# Load Telegram Bot Token and Chat ID from .env
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        print("Message sent to Telegram successfully!")
    else:
        print(f"Error sending to Telegram: {response.status_code}, {response.text}")
        
send_to_telegram("Hello, this is a test message from Python!")