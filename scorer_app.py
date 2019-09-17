#!/usr/bin/env python
from flask import Flask, request, send_from_directory, make_response
from http import HTTPStatus

import base64
import hashlib
import hmac
import logging
import json
import os
import tweepy

#Gonna be sending Tweets and DMs.
CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None) #Also needed for CRC.
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', None)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#CURRENT_USER_ID = os.environ.get('CURRENT_USER_ID', None) #May be needed?


def get_pars():
    pars = [5, 4, 3, 4, 3, 5, 4, 4, 4, 4, 4, 3, 4, 4, 5, 5, 3, 4]
    return pars

def get_team_scorers():
    scorers = ['arisirenita', 'lindspanther', 'evanr', 'happycamper', 'BoomerMurray', 'ThomasMac_IV', 'kennykhlee', \
               'robdehuff', 'kathleenso', 'noahwinter13', 'traviszachary', 'snowman', 'ericmartinyc', 'johnd', 'gmax', \
               'maeloveholt', 'jpodnos']
    return scorers

def send_tweet(message, media_id = None):
    api.update_status(message, media_id=media_id)

def send_direct_message(recipient_id, message):
    api.send_direct_message(recipient_id, message)

def handle_score(message):
    #Parse and store score
    pass

def handle_dm(dm):

    from_user_id = dm['direct_message_events'][0]['message_create']['sender_id']
    message = dm['direct_message_events'][0]['message_create']['message_data']['text']
    print (f"Received a Direct Message from {from_user_id} with message: {message}")

    #Look for markers that this is a score (#t #h #s).
    if '#t' in message and '#h' in message and '#s' in message:
        #We have a score
        response = 'Thanks for submitting your score.'

        #Store score and Tweet out current standings.
        handle_score(message)

        send_direct_message(from_user_id, response)

app = Flask(__name__)

#generic index route
@app.route('/')
def default_route():
    return "Hello world"

# The GET method for webhook should be used for the CRC check
@app.route("/webhook", methods=["GET"])
def twitter_crc_validation():

    crc = request.args['crc_token']

    validation = hmac.new(
        key=bytes(CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc, 'utf-8'),
        digestmod = hashlib.sha256
    )
    digested = base64.b64encode(validation.digest())
    response = {
        'response_token': 'sha256=' + format(str(digested)[2:-1])
    }
    print('responding to CRC call')

    return json.dumps(response)

# Event manager block
@app.route("/webhook", methods=["POST"])
def event_manager():

    if 'direct_message_indicate_typing_events' in request.json:
        pass
    elif 'direct_message_events' in request.json:
        handle_dm(request.json)
    elif 'tweet_create_events' in request.json:
        #Need to look at Tweet payload's User to know if host account created Tweet?
        #Testing with @HackerScorer mention, and had to parse User ID to know who mentined, and entities.user_mentions to know who they mentioned.
        pass

    elif 'favorite_events' in request.json:
        pass

    return "200"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    # Logger code
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', port=port, debug=True)
