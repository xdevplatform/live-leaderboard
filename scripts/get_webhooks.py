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

# Generate user context auth (OAuth1)
app_only_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)

# Assign the resource url
resource_url = "https://api.twitter.com/1.1/account_activity/all/webhooks.json"

response = requests.get(resource_url, auth=app_only_auth)
print(response.status_code, response.text)