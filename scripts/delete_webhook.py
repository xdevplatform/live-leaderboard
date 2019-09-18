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

# Insert webhook ID to be deleted. Retrieve from `get_webhooks.py` script.
webhook_id = ""

# Generate user context auth (OAuth1)
user_context_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)

# Assign the resource and webhook urls
resource_url = f"https://api.twitter.com/1.1/account_activity/all/prod/webhooks/{webhook_id}.json"

# headers = {"Content-Type": "application/x-www-form-urlencoded"}


response = requests.delete(resource_url, auth=user_context_auth)
print(response.status_code, response.text)