#!/usr/bin/env python
from flask import Flask, request, send_from_directory, make_response
from http import HTTPStatus
import psycopg2
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pylab as plt
from pandas.plotting import table

import base64
import hashlib
import hmac
import logging
import json
import os
import tweepy
import fnmatch

#Gonna be sending Tweets and DMs.
HOST_ACCOUNT_ID = os.environ.get('HOST_ACCOUNT_ID', None)
CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None) #Also needed for CRC.
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', None)
DATABASE = os.environ.get('DATABASE', None)
DATABASE_HOST = os.environ.get('DATABASE_HOST', None)
DATABASE_USER = os.environ.get('DATABASE_USER', None)
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', None)

#Set up tweepy client for sending Tweets and DMs.
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def get_pars():
    '''Quick and dirty way to store each hole's par rating.'''
    pars = [5, 4, 3, 4, 3, 5, 4, 4, 4, 4, 4, 3, 4, 4, 5, 5, 3, 4]
    return pars

def get_team_scorers():
    '''
    Current list of 'scorers' (folks who gotta know how to run this app.). Note that this list's indices tell us the team number).
    We know who is reporting so we do nothave to require team id or name.
    '''
    scorers = ['arisirenita', 'lindspanther', 'evanr', 'happycamper', 'BoomerMurray', 'ThomasMac_IV', 'kennykhlee', \
               'robdehuff', 'kathleenso', 'noahwinter13', 'traviszachary', 'snowman', 'ericmartinyc', 'johnd', 'gmax', \
               'maeloveholt', 'jpodnos']
    return scorers

def insert_score(team_id, hole, score):
    ''' Database wrapper for storing scores. '''

    #Create database connection.
    con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
    cur = con.cursor()
    cur.execute(f"INSERT INTO scores (time_stamp,team_id,hole,score) VALUES (NOW(),{team_id},{hole},{score});")
    con.commit()
    con.close()

def get_scores():
    '''Database wrpper for retrieving ALL scores.'''

    DATABASE="dce7q202rl13nm"
    DATABASE_HOST="ec2-107-20-243-220.compute-1.amazonaws.com"
    DATABASE_USER="ijjdchmahpzskl"
    DATABASE_PASSWORD="aa8a1e32fab2660fedfb44f2d145c98c8bb063b027402323f426a735bddfbc6f"

    #Create database connection.
    sql = "SELECT * FROM scores;"
    con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
    #Load recordset into dataframe.
    scores_df = psql.read_sql_query(sql, con)

    #cur.execute("SELECT * FROM scores;")
    #scores = cur.fetchall()
    con.close()

    return scores_df

def create_standings():
    '''This function does the work of building a leaderboard. Recipe:
        * Retrieve scores.
        * Load them into a Pandas dataframe.
        * Do some sorting.
        * Do some calculating. Like looking up par ratings and determining over/even/under.
        * Generate image of dataframe.
        * Write image to ./img folder.

    '''
    #Retrieve scores.
    scores_df = get_scores()

    #Sort and calculate. TODO

    #Generate image.
    # set fig size
    fig, ax = plt.subplots(figsize=(12, 3))
    # no axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # no frame
    ax.set_frame_on(False)
    # plot table
    tab = table(ax, scores_df, loc='upper right')
    # set font manually
    tab.auto_set_font_size(False)
    tab.set_fontsize(8)
    # save the result
    if not os.path.exists('./img'):
        os.makedirs('./img')
    plt.savefig('./img/scores.png')

# Takes generated image from above method and upload to Twitter, return media_id.
def upload_media(image_file):
    res = api.media_upload(image_file)
    media_ids = []
    # Add returned media_id to array
    media_ids.append(res.media_id)

    return media_ids

#TODO
def get_media_ids():
    '''Requests media ids from Twitter. We may be uploadog'''
    ids = []
    return ids

def send_tweet(message, media_id = None):
    '''Sends a Tweet. Can handle native media. '''
    api.update_status(message, media_id=media_id)

#TODO: Needs to learn how to send native media.
def send_direct_message(recipient_id, message):
    api.send_direct_message(recipient_id, message)

#TODO
def handle_score(message):
    '''Parses and stores score.'''
    have_team = False
    have_hole = False
    have_score = False

    #Parse and store score
    team_id = -1
    hole = 0
    score = 0

    #We have a score, so parse it.
    tokens = message.split(' ')

    #TODO: have more patterns to look for? Add them here.

    #Parse team_id.

    team_token = fnmatch.filter(tokens, 't?')
    if len(team_token) == 1:
        have_team = True
        team_id = team_token[0][1:]

    if not have_team:
        team_token = fnmatch.filter(tokens, 't??')
        if len(team_token) == 1:
            have_team = True
            team_id = team_token[0][1:]

    #Parse hole.
    hole_token = fnmatch.filter(tokens, 'h?')
    if len(hole_token) == 1:
        have_hole = True
        hole = hole_token[0][1:]

    if not have_hole:
        hole_token = fnmatch.filter(tokens, 'h??')
        if len(hole_token) == 1:
            have_hole = True
            hole = hole_token[0][1:]

    #Parse score.
    score_token = fnmatch.filter(tokens, 's?')
    if len(score_token) == 1:
        have_score = True
        score = score_token[0][1:]

    if not have_score:
        score_token = fnmatch.filter(tokens, 's??')
        if len(score_token) == 1:
            have_score = True
            score = score_token[0][1:]

    #Save the score.
    print (f"Inserting for team {team_id}: hole {hole} with score {score} ")
    insert_score(int(team_id), int(hole), int(score))

    #TODO Send submitter the leaderboard via DM?
    #Generate leaderboard
    #send_leaderboard_dm()

#TODO
def send_leaderboard_tweet():
    test_image = "scorecard.png"
    media_id = upload_media(test_image)
    message = "Here's the leaderboad:"

    api.update_status(status=message, media_ids=media_id)

#TODO
def send_leaderboard_dm():
    pass

def generate_leaderboard():
    pass

#TODO
def is_score(message):
    '''Parses DM message and sees if it is a score.'''

    is_score = False #Default.

    #Look for markers that this is a score (#t #h #s).
    #TODO: what are the patterns that indicate that it is a score.

    if 't' in message and 'h' in message and 's' in message: #TODO harden with pattern matching t?, t??, etc.
        is_score = True
    #elif 't' in message and 'h' in message and 's' in message: #TODO
    #    pass


    #Parse score.
    return is_score

#TODO
def is_leaderboard_command(message):
    '''Parses DM message to see if it is a command to send DM with leaderboard.'''

    is_leaderboard_command = False # Default

    # Look for the word "Leaderboard" in DM text
    if 'Leaderboard' in message or 'leaderboard' in message:
        is_leaderboard_command = True

    return is_leaderboard_command

def handle_dm(dm):
    '''Determines what kind of DM this is.
        * Is this a score being submitted?
        * Is this a command to post the leaderboard?
        * Currently ignoring other DMs.
    '''

    print (f"Received a Direct Message from {sender_id} with message: {message}") #TODO: tweepy to get handle.

    #Ignore DM events from DM we sent.
    sender_id = dm['direct_message_events'][0]['message_create']['sender_id']
    message = dm['direct_message_events'][0]['message_create']['message_data']['text']

    if sender_id == HOST_ACCOUNT_ID: #Then special handling.
        if is_leaderboard_command(message):
            send_leaderboard_tweet() #Tweet out leaderboard.
            response = "OK, gonna Tweet the leaderboard."
            send_direct_message(sender_id, response)
        else:
            pass #Ignoring by design.
    elif sender_id != HOST_ACCOUNT_ID:
        if is_score(message):
            handle_score(message) #Store score.
            response = "Got it, thanks!"
            send_direct_message(sender_id, response)
        elif is_leaderboard_command(message):
            send_leaderboard_tweet() #Tweet out leaderboard.
            response = "OK, gonna Tweet the leaderboard."
            send_direct_message(sender_id, response)
        else:
            pass #Completely ignoring other DMs. TODO: are there others we want to respond to?
            response = "Sorry, busy keeping score..."
            send_direct_message(sender_id, response)

#=======================================================================================================================
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

    #Match on event types that we care about. So far, just paying attention to DMs.
    if 'direct_message_indicate_typing_events' in request.json:
        pass #Ignoring these by design...
    elif 'direct_message_events' in request.json:
        handle_dm(request.json)
    elif 'tweet_create_events' in request.json:
        #Need to look at Tweet payload's User to know if host account created Tweet?
        #Testing with @HackerScorer mention, and had to parse User ID to know who mentined, and entities.user_mentions to know who they mentioned.
        pass #Not doing anything with these yet...
    elif 'favorite_events' in request.json:
        pass #Not doing anything with these yet...

    return "200"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    # Logger code
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', port=port, debug=True)


##Saved 'callers' for unit testing.
#if __name__ == '__main__':
#    create_standings()
#     #Seeding database with data.
#     handle_score("t1 h1 s4")
#     handle_score("t2 h2 s4")
#     handle_score("t3 h3 s4")
#     handle_score("t4 h4 s4")
#     handle_score("t5 h5 s4")
#     handle_score("t6 h6 s4")
#     handle_score("t7 h7 s4")
#     handle_score("t8 h8 s4")
#     handle_score("t9 h9 s4")
#     handle_score("t10 h10 s4")
#     handle_score("t18 h18 s4")
#     handle_score("t1 h2 s4")
#     handle_score("t2 h3 s4")
#     handle_score("t3 h4 s4")
#     handle_score("t1 h3 s4")
#     handle_score("t2 h4 s4")
#     handle_score("t3 h5 s4")
#     handle_score("t18 h1 s4")
#     handle_score("t18 h2 s4")
#     handle_score("t18 h3 s4")
#     handle_score("t18 h4 s4")






