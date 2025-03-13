import requests
import json
import os


def save_token_to_file(token_info):
    with open('C:/Users/HomePC/Desktop/Bachelorthesis/Code/propaganda/data/token_config.json', 'w') as f:
        json.dump(token_info, f)


# Endpoint URL
url = "https://open.tiktokapis.com/v2/oauth/token/"

# Headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cache-Control": "no-cache"
}

# Body parameters
body = {
    "client_key": "awcltp29lehrs2a2",
    "client_secret": "wccDzuWpgLCC0PDtp4xjsOXfN4MogK6t",
    "grant_type": "client_credentials"
}

# Make a POST request
response = requests.post(url, headers=headers, data=body)

# Check the response
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data['access_token']
    print("Access Token:", access_token)
    print("Expires In:", token_data['expires_in'], "seconds")

    # Save the token to a file
    save_token_to_file(token_data)
else:
    print("Failed to obtain token. Status Code:", response.status_code)
    print("Error Details:", response.text)
