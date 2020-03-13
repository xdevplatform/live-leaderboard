import json
import os
import sys

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Retrieves and stores credential information from the '.env' file
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Generate user context auth (OAuth1)
user_context_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)

# Specify which env you want register ('prod' or 'dev')
env_name = "prod"

# Assign the resource url
resource_url = f"https://api.twitter.com/1.1/account_activity/all/{env_name}/webhooks.json"

# Provide the web app URL (including path e.g., /webhook) that you want to register as the webhook
url_dict = {"url": "https://<URL>/webhook"}

headers = {"Content-Type": "application/x-www-form-urlencoded"}


response = requests.post(resource_url, auth=user_context_auth, headers=headers, params=url_dict)
print(response.status_code, response.text)
