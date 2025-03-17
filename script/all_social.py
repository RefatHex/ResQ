import requests
from decouple import config

# Load environment variables
DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL")
FACEBOOK_PAGE_ID = config("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = config("FACEBOOK_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")

# Discord Functions
def send_file_to_discord(file_path, message=""):
    """
    Send a file (photo or video) to Discord via a webhook.
    """
    with open(file_path, "rb") as file:
        files = {"file": file}
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, files=files, data=data)
        if response.status_code == 200:
            print("File sent to Discord successfully!")
        else:
            print(f"Error sending file to Discord: {response.status_code}, {response.text}")

# Facebook Functions
def post_to_facebook(file_path, message="", is_video=False):
    """
    Post a photo or video to a Facebook page.
    """
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/{'videos' if is_video else 'photos'}"
    params = {
        "access_token": FACEBOOK_ACCESS_TOKEN,
        "description" if is_video else "message": message,
    }
    with open(file_path, "rb") as file:
        files = {"source": file}
        response = requests.post(url, files=files, params=params)
        if response.status_code == 200:
            print("Posted to Facebook successfully!")
        else:
            print(f"Error posting to Facebook: {response.json()}")

# Telegram Functions
def send_media_to_telegram(file_path, caption="", is_video=False):
    """
    Send a photo or video to a Telegram chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{'sendVideo' if is_video else 'sendPhoto'}"
    with open(file_path, "rb") as media:
        files = {"video" if is_video else "photo": media}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption,
        }
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(f"{'Video' if is_video else 'Photo'} sent to Telegram successfully!")
        else:
            print(f"Error sending {'video' if is_video else 'photo'} to Telegram: {response.status_code}, {response.text}")
