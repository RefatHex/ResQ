import requests
from decouple import config

# Load environment variables
DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL")
FACEBOOK_PAGE_ID = config("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = "EAAGyZCdjiiZBoBO3Am4r0fQPVbUZBDAwWLM04zloU8o1hZAlwtRYhyQ4zqkX60jl0Iz6uwtRS0KJwoYReZBlAJGlVejFK3Tom4nxZBcf0YIfTtMZCxMjbFwF8KTNIpn6iP7uDZCToztJStgqrl6OFoPCJ9Cb0Y26F0dmypsPHKFyDhMRye7wQA8epyMi8y8E80AZB7aiacbKreK8Oeu9I2EPp5YxTe9ZByF3CGXdQYsafcXUHKZB0jXzJTQZAbwZD"
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")

# Discord Functions
def send_file_to_discord(file_path, message=""):
    """
    Send a file (photo or video) to Discord via a webhook.
    If file_path is None, sends only the message.
    """
    if file_path:
        with open(file_path, "rb") as file:
            files = {"file": file}
            data = {"content": message}
            response = requests.post(DISCORD_WEBHOOK_URL, files=files, data=data)
    else:
        # Send text-only message
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code == 200 or response.status_code == 204:
        print("Message sent to Discord successfully!")
    else:
        print(f"Error sending to Discord: {response.status_code}, {response.text}")

# Facebook Functions
def post_to_facebook(file_path, message="", is_video=False):
    """
    Post a photo or video to a Facebook page.
    If file_path is None, creates a text-only post.
    """
    if file_path:
        url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/{'videos' if is_video else 'photos'}"
        params = {
            "access_token": FACEBOOK_ACCESS_TOKEN,
            "description" if is_video else "message": message,
        }
        with open(file_path, "rb") as file:
            files = {"source": file}
            response = requests.post(url, files=files, params=params)
    else:
        # Text-only post
        url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
        params = {
            "message": message,
            "access_token": FACEBOOK_ACCESS_TOKEN,
        }
        response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print("Posted to Facebook successfully!")
    else:
        print(f"Error posting to Facebook: {response.json()}")

# Telegram Functions
def send_media_to_telegram(file_path, caption="", is_video=False):
    """
    Send a photo or video to a Telegram chat.
    If file_path is None, sends a text-only message.
    """
    if file_path:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{'sendVideo' if is_video else 'sendPhoto'}"
        with open(file_path, "rb") as media:
            files = {"video" if is_video else "photo": media}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
            }
            response = requests.post(url, files=files, data=data)
    else:
        # Text-only message
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": caption,
            "parse_mode": "HTML"  # Enable HTML formatting if needed
        }
        response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"{'Message' if not file_path else 'Video' if is_video else 'Photo'} sent to Telegram successfully!")
    else:
        print(f"Error sending to Telegram: {response.status_code}, {response.text}")
