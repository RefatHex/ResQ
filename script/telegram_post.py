import requests
from decouple import config

# Load Telegram Bot Token and Chat ID from .env
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")

def send_photo_to_telegram(photo_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption,
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Photo sent to Telegram successfully!")
        else:
            print(f"Error sending photo to Telegram: {response.status_code}, {response.text}")

def send_video_to_telegram(video_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, "rb") as video:
        files = {"video": video}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption,
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Video sent to Telegram successfully!")
        else:
            print(f"Error sending video to Telegram: {response.status_code}, {response.text}")
            return False
        return True