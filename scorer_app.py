import os
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonifyimport base64
import hmac
import hashlib
import json
import requests
from requests_oauthlib import OAuth1,OAuth2
from datetime import datetime

app = Flask(__name__)

creds = {}
creds["username"] = os.environ["username"]
creds["consumer_key"] = os.environ["consumer_key"]
creds["consumer_secret"] = os.environ["consumer_secret"]
creds["token"] = os.environ["token"]
creds["secret"] = os.environ["secret"]

@app.route('/', methods=['GET'])
def homepage():
    return "Hello world"

@app.route('/webhook', methods=['GET'])
def webhook():
    if request.method == 'GET':
        # check to see if this is a challenge response request
        crc_token = request.args.get('crc_token')
        # if there's a crc token, we've got to reply with the secret
        if crc_token is not None:
            sha256_hash_digest = hmac.new(creds["consumer_secret"].encode("utf-8"), 
                                 msg=crc_token.encode("utf-8"), 
                                 digestmod=hashlib.sha256).digest()
            crc_response = {'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode()}
            return jsonify(crc_response), 200
        # if this isn't a crc handshake do nothing
        else:
            return "Hello world", 200
        
      
if __name__ == '__main__':
    app.run()
