import json
import os
import sys

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

# Retrieves and stores credential information from the '.env' file
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Generate user context auth (OAuth1)
user_context_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)

# Assign the resource and webhook urls
resource_url = "https://api.twitter.com/1.1/account_activity/all/dev/webhooks.json"

url_dict = {'url': 'https://hacker-scorer.herokuapp.com/webhook'}

headers = {"Content-Type": "application/x-www-form-urlencoded"}


response = requests.post(resource_url, auth=user_context_auth, headers=headers, params=url_dict)
print(response.status_code, response.text)

# def register_webhook(webhook_url):
# 	# Generate user context auth (OAuth1)
# 	user_context_auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)
# 	try:
# 		response = requests.post(resource_url, auth=user_context_auth, params=webhook_url)
# 	except requests.exceptions.RequestException as e:
# 		print(e)
# 		sys.exit(120)

# 	print(response.status_code, response.text)

# Call the register_webhook function
# register_webhook(my_webhook_url)