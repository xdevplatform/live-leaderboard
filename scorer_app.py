#!/usr/bin/env python
from flask import Flask, request, send_from_directory, make_response
from http import HTTPStatus

import base64
import hashlib
import hmac
import logging
import json
import os

import twitter

#Gonna be sending Tweets and DMs.
CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None) #Also needed for CRC.
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', None)

#CURRENT_USER_ID = os.environ.get('CURRENT_USER_ID', None) #May be needed?


def handle_dm(dm):

    from_user_id = dm['direct_message_events'][0]['message_create']['sender_id']
    message = dm['direct_message_events'][0]['message_create']['message_data']['text']
    print (f"Received a Direct Message from {from_user_id} with message: {message}")
    pass


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


#The POST method for webhook should be used for all other API events
#TODO: add event-specific behaviours beyond Direct Message and Like

# @app.route("/webhook", methods=["POST"])
# def twitter_event_received():

#     requestJson = request.get_json()

#     #dump to console for debugging purposes
#     print(json.dumps(requestJson, indent=4, sort_keys=True))

#     if 'favorite_events' in requestJson.keys():
#         #Tweet Favourite Event, process that
#         likeObject = requestJson['favorite_events'][0]
#         userId = likeObject.get('user', {}).get('id')

#         #event is from myself so ignore (Favourite event fires when you send a DM too)   
#         if userId == CURRENT_USER_ID:
#             return ('', HTTPStatus.OK)

#         Twitter.processLikeEvent(likeObject)

#     elif 'direct_message_events' in requestJson.keys():
#         #DM recieved, process that
#         eventType = requestJson['direct_message_events'][0].get("type")
#         messageObject = requestJson['direct_message_events'][0].get('message_create', {})
#         messageSenderId = messageObject.get('sender_id')

#         #event type isnt new message so ignore
#         if eventType != 'message_create':
#             return ('', HTTPStatus.OK)

#         #message is from myself so ignore (Message create fires when you send a DM too)   
#         if messageSenderId == CURRENT_USER_ID:
#             return ('', HTTPStatus.OK)

#         Twitter.processDirectMessageEvent(messageObject)

#     else:
#         #Event type not supported
#         return ('', HTTPStatus.OK)

#     return ('', HTTPStatus.OK)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    # Logger code
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', port=port, debug=True)
