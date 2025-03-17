import requests
from decouple import config

DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL")

def send_file_to_discord(file_path, message=""):
    with open(file_path, "rb") as file:
        files = {"file": file}
        data = {
            "content": message,
        }
        response = requests.post(DISCORD_WEBHOOK_URL, files=files, data=data)
        if response.status_code == 200:
            print("File sent to Discord successfully!")
        else:
            print(f"Error sending file to Discord: {response.status_code}, {response.text}")