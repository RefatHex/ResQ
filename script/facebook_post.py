import requests
from decouple import config
def post_to_facebook(file_path, message="", is_video=False):
    page_id = config("FACEBOOK_PAGE_ID")
    access_token = config("FACEBOOK_ACCESS_TOKEN")
    url = f"https://graph.facebook.com/{page_id}/feed"
    if is_video:
        url = f"https://graph.facebook.com/{page_id}/videos"
        params = {
            "description": message,
            "access_token": access_token,
        }
    else:
        url = f"https://graph.facebook.com/{page_id}/photos"
        params = {
            "message": message,
            "access_token": access_token,
        }

    # Open the file
    with open(file_path, "rb") as file:
        files = {"source": file}
        response = requests.post(url, files=files, params=params)

    if response.status_code == 200:
        print("Posted to Facebook successfully!")
    else:
        print(f"Error posting to Facebook: {response.json()}")