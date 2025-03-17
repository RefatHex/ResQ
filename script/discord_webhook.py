import requests
from decouple import config

# Load Discord Webhook URL from .env
DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL")

def send_to_discord(message):
    data = {
        "content": message,
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data, headers=headers)
    if response.status_code == 204:
        print("Message sent to Discord successfully!")
    else:
        print(f"Error sending to Discord: {response.status_code}, {response.text}")
        
send_to_discord("Hello, this is a test message from Python!")