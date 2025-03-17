import requests
from decouple import config
def post_to_facebook(file_path, message="", is_video=False):
    page_id = config("FACEBOOK_PAGE_ID")
    access_token = config("FACEBOOK_ACCESS_TOKEN")
    page_id = "525751260631755"
    access_token = "EAAGyZCdjiiZBoBO8rBDrO1cgq5gvSB4SUHKk0rxmNDcM2mUx3OD5twKGV9KiZByqbKw6OwVAkpZBz8P15ZBJIdSfn5m2lrZCO2SXS9ZB47rfYtWguz1sIDznipBTogfCZCujCT2POQgbnQyjF5cydTXqbI5aWGS8fqdm1MMk188ihZCLboCJnVdMTBKLAdXay8voUfq0IHVmDZBsjHh7yUb62jgcMS4oAHdiU5boXViHBU"  
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