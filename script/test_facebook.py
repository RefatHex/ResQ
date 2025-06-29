import os
import requests
from decouple import config

def test_text_post():
    """Test posting text-only content to Facebook"""
    page_id = config('FACEBOOK_PAGE_ID')
    access_token = "EAAGyZCdjiiZBoBO3Am4r0fQPVbUZBDAwWLM04zloU8o1hZAlwtRYhyQ4zqkX60jl0Iz6uwtRS0KJwoYReZBlAJGlVejFK3Tom4nxZBcf0YIfTtMZCxMjbFwF8KTNIpn6iP7uDZCToztJStgqrl6OFoPCJ9Cb0Y26F0dmypsPHKFyDhMRye7wQA8epyMi8y8E80AZB7aiacbKreK8Oeu9I2EPp5YxTe9ZByF3CGXdQYsafcXUHKZB0jXzJTQZAbwZD"
    
    url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
    
    params = {
        'message': "🚨 TEST: Emergency Alert System Test\nThis is a test message from ResQ emergency system. Please ignore.",
        'access_token': access_token
    }
    
    try:
        response = requests.post(url, data=params)
        print("\n=== Facebook Text Post Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error in text post test: {str(e)}")
        return False


def verify_page_token():
    """Verify if the page access token is valid"""
    access_token = config('FACEBOOK_ACCESS_TOKEN')
    url = "https://graph.facebook.com/debug_token"
    
    params = {
        'input_token': access_token,
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        print("\n=== Token Verification ===")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if 'data' in data:
            print(f"Token Valid: {data['data'].get('is_valid', False)}")
            print(f"Expires: {data['data'].get('expires_at', 'N/A')}")
            print(f"App ID: {data['data'].get('app_id', 'N/A')}")
            return data['data'].get('is_valid', False)
        return False
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Facebook API Tests...")
    
    # First verify token
    if verify_page_token():
        print("\nToken verification successful!")
        
        # Run text post test
        if test_text_post():
            print("Text post test successful!")
        else:
            print("Text post test failed!")
    else:
        print("\nToken verification failed! Please check your Facebook access token.")
