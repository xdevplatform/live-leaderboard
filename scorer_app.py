#!/usr/bin/env python
import base64
import fnmatch
import hashlib
import hmac
import json
import logging
import os
import re
import random
import time

from flask import Flask, request, send_from_directory, make_response
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from pandas.plotting import table
import psycopg2
import requests
from requests_oauthlib import OAuth1
import tweepy
from dotenv import load_dotenv
load_dotenv(verbose=True)  # Throws error if it can't find .env file

#Gonna be sending Tweets and DMs.
HOST_ACCOUNT_ID = os.getenv('HOST_ACCOUNT_ID', None)  #OR os.environ.get
CONSUMER_KEY = os.getenv('CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', None) #Also needed for CRC.
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', None)
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', None)
DATABASE = os.getenv('DATABASE', None)
DATABASE_HOST = os.getenv('DATABASE_HOST', None)
DATABASE_USER = os.getenv('DATABASE_USER', None)
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', None)

if HOST_ACCOUNT_ID == None:
    print ('Could not load from .env file, loading from local environment.')
    HOST_ACCOUNT_ID = os.environ.get('HOST_ACCOUNT_ID')
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
    DATABASE = os.environ.get('DATABASE')
    DATABASE_HOST = os.environ.get('DATABASE_HOST')
    DATABASE_USER = os.environ.get('DATABASE_USER')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')   

#Set up tweepy client for sending Tweets and DMs.
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Generate user context auth (OAuth1)
USER_AUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

PARS = [5, 4, 3, 4, 3, 5, 4, 4, 4, 4, 4, 3, 4, 4, 5, 5, 3, 4]

BIRDIE_IMAGES = ['./static/birdie1.jpg', './static/birdie2.jpg', './static/birdie3.jpg', './static/birdie4.jpg']

def get_team_scorers():
    '''
    Current list of 'scorers' (folks who gotta know how to run this app.). Note that this list's indices tell us the team number).
    We know who is reporting so we do nothave to require team id or name.
    '''
    #TODO if we use this and the order matters, these need to be updated to reflect new team order.
    #Updated on Sunday
    scorers = ['arisirenita', 'lindspanther', 'evanr', 'snowman', 'BoomerMurray', 'zachnm', 'noahwinter13','kennykhlee','WHO', 'WHO','kathleenso', 'happycamper','WHO', 'WHO','johnd','gmax', 'maeloveholt','jpodnos','ericmartinyc']
    #No longer scorers?  'ThomasMac_IV', 'robdehuff','traviszachary'
    return scorers

def insert_score(team_id, hole, score, over_under):
    ''' Database wrapper for storing scores. '''

    success = False

    try:
        #Create database connection.
        con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
        cur = con.cursor()
        cur.execute(f"INSERT INTO scores (time_stamp,team_id,hole,score, over_under) VALUES (NOW(),{team_id},{hole},{score}, {over_under});")
        con.commit()
        success = True
    except:
        print ("Error on INSERT, assuming duplicate!")
        success = False

    con.close()

    return success

def delete_score(message):

    #Parse out team_id and hole.
    team_id, hole, score = parse_details(message)

    try:
        #Create database connection.
        con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
        cur = con.cursor()
        cur.execute(f"DELETE scores WHERE team_id = {team_id} AND hole = {hole};")
        con.commit()
        success = True
    except:
        print ("Error on DELETE!")
        success = False

    con.close()

    return success

def update_score(message):

    #Parse out team_id, hole, and score.
    team_id, hole, score = parse_details(message)

    try:
        #Create database connection.
        con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
        cur = con.cursor()
        cur.execute(f"UPDATE scores SET score = {score} WHERE team_id = {team_id} AND hole = {hole};")
        con.commit()
        success = True
    except:
        print ("Error on UPDATE!")
        success = False

    con.close()

    return success

def get_scores():
    '''Database wrpper for retrieving ALL scores.'''

    #Create database connection.
    sql = "SELECT * FROM scores;"
    con = psycopg2.connect(database=DATABASE, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port="5432")
    #Load recordset into dataframe.
    scores_df = psql.read_sql_query(sql, con)

    #cur.execute("SELECT * FROM scores;")
    #scores = cur.fetchall()
    con.close()

    return scores_df

def get_over_under(hole, score):
    par = PARS[(int(hole)-1)]
    return int(score) - par

def create_standings_image(df):
    header_colors = ["#7ed4ff"]*4
    cell_colors = [["#ffffff"]*4 
                    if x % 2 == 0
                    else ["#D3D3D3"]*4
                    for x in range(0,df.shape[0])
                  ]
    #Generate image.
    # set fig size
    fig, ax = plt.subplots(figsize=(4.5,4.5))
    # no axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # no frame
    ax.set_frame_on(False)
    # Set index to place list
    df["my_index"] = ['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th']
    df.set_index("my_index",inplace = True)
    # plot table
    tab = table(ax, df, loc='center', cellLoc='center', colWidths=[0.17, 0.17, 0.17, 0.28],
                    colColours=header_colors, cellColours=cell_colors, bbox=[0,-.1,1.05,1.22]
                    )
    # set font manually
    tab.auto_set_font_size(False)
    tab.set_fontsize(10)

    table_props = tab.properties()
    table_cells = table_props['child_artists']
    for cell in table_cells: cell.set_height(0.1)
    for i,cell in enumerate(table_cells):
        if (i+1) % 5 == 0:
            cell.set_fill('k')

    # save the result
    if not os.path.exists('./img'):
        os.makedirs('./img')
    plt.savefig('./img/scores.png')

# def create_standings_csv(df):
#     df.to_csv('./csv/scores.csv', index=False)
#
# def create_standings_html(df):
#     df.to_html('./html/scores_v0.html')

def get_last_hole(team, holes_completed):
    #Important note: team number indicates the hole that the team started on.

    last_hole = team + holes_completed - 1

    if last_hole > 18:
        last_hole = last_hole - 18

    return last_hole

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
    scores_df.columns = ["team_id", "team_name", "hole", "score", "time_stamp", "over_under"]
    #Drop columns that are not currently needed in standings.
    scores_df.drop('team_name', axis=1, inplace=True)
    scores_df.drop('time_stamp', axis=1, inplace=True)  #Note - this seems key to pick off more recent completed hole.

    #print (scores_df)

    team_scores = [ [] for i in range(18)]

    #Order of team details in these lists: Team number, total score, over_under, holes_completed, last_hole

    for i in range(18):

        team = i + 1
        team_scores[i].append(team) #Add team number.

        score = scores_df.loc[scores_df['team_id'] == team, 'score'].sum()
        over_under = scores_df.loc[scores_df['team_id'] == team, 'over_under'].sum()
        holes_complete = scores_df.loc[scores_df['team_id'] == team, 'hole'].count()
        last_hole = get_last_hole(team, holes_complete)

        team_scores[i].append(over_under)
        team_scores[i].append(score)
        team_scores[i].append(holes_complete)
        #team_scores[i].append(last_hole) #Not currently using.

        #print (f"Team {team} has a score of {score} with an over/under of {over_under}")

    #Make dataframe.
    df_standings = pd.DataFrame(team_scores, columns=['Team','Score','Total','Holes played'])

    #print (df_standings)

    #Sort dataframe
    df_sorted = df_standings.sort_values(by=['Score', 'Holes played'], ascending=[True, False])

    df_sorted.loc[df_sorted.Score > 0, 'Score'] = '+' + df_sorted['Score'].astype(str)

    create_standings_image(df_sorted)
    #create_standings_csv(df_sorted)
    #create_standings_html(df_sorted)

# Takes generated image from above method and upload to Twitter, return media_id.
def get_media_id(image_path):
    '''Uploads media using requests library'''
    # Open the image
    with open(image_path, "rb") as image_file:
        image_raw = base64.b64encode(image_file.read())

    resource_url = "https://upload.twitter.com/1.1/media/upload.json"
    payload = {"media": image_raw}

    response = requests.post(resource_url, auth=USER_AUTH, data=payload)
    json_response = (json.loads(response.text))
    media_id = json_response.get("media_id")

    return media_id

#TODO - eliminate?
def send_tweet(message, media_id):
    '''Posts Tweet using requests library'''

    resource_url = "https://api.twitter.com/1.1/statuses/update.json"
    payload = {"status": message, "media_ids": media_id}

    response = requests.post(resource_url, auth=USER_AUTH, params=payload)

def send_direct_message(recipient_id, message, media_id=None):

    if media_id == None:
        api.send_direct_message(recipient_id, message)
    else:
        api.send_direct_message(recipient_id, message, attachment_media_id = media_id, attachment_type='media')


def parse_details(message):
    have_team = False
    have_hole = False
    have_score = False

    #Parse and store score
    team_id = -1
    hole = 0
    score = 0

    message = message.lower()

    tokens = message.split(' ')

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


    return team_id, hole, score

def handle_score(message):
    '''Parses and stores score.'''

    team_id, hole, score = parse_details(message)

    over_under = get_over_under(hole, score)

    #Save the score.
    print (f"Inserting for team {team_id}: hole {hole} with score {score} with over_under of {over_under}")

    success = insert_score(int(team_id), int(hole), int(score), int(over_under))
    create_standings() #New score, update the standings

    # Birdie alert: if insert was successful and over_under score is '-1', send birdie alert
    if success and over_under == -1:
        message = f"#BirdieAlert\nTeam {team_id} just got a birdie on hole {hole}!"
        image = random.choice(BIRDIE_IMAGES)
        media_id = get_media_id(image)
        send_tweet(message, media_id)

    return success

# Done. Working as of 9/23 7:00pm MT
def send_leaderboard_tweet():
    '''Uploads media to get media_id, then posts Tweet using requests library'''

    resource_url = "https://api.twitter.com/1.1/statuses/update.json"
    message = "Here are the current standings:"
    # Calls get_media_id method to upload image and get media_id.
    media_id = get_media_id("./img/scores.png")
    payload = {"status": message, "media_ids": media_id}

    response = requests.post(resource_url, auth=USER_AUTH, params=payload)

def send_leaderboard_dm(recipient_id):
    create_standings()
    media_id = get_media_id('./img/scores.png')
    #message = "Here are the currrent standings..."

    send_direct_message(recipient_id, '', media_id)

def is_score(message):
    '''Parses DM message and sees if it is a score.'''

    is_score = False #Default.

    if 'delete' in message.lower() or 'update' in message.lower():
        return False

    #Look for markers that this is a score (t## h## s##).
    if re.search('[tT]\d{1,2}',message) != None and \
        re.search('[hH]\d{1,2}',message) != None and \
        re.search('[sS]\d{1,2}',message) != None:
    #if 't' in message.lower() and 'h' in message.lower() and 's' in message.lower():
        is_score = True

    return is_score

def is_update_command(message):

    is_update = False

    if 'update' in message.lower() and re.search('[tT]\d{1,2}',message) != None and \
            re.search('[hH]\d{1,2}',message) != None and \
            re.search('[sS]\d{1,2}',message) != None:
        is_update = True

    return is_update


def is_leaderboard_command(message):
    '''Parses DM message to see if it is a command to send DM with leaderboard.'''

    is_leaderboard_command = False # Default

    # Look for the word "Leaderboard" in DM text
    if 'leaderboard' in message.lower():
        is_leaderboard_command = True

    return is_leaderboard_command

def handle_dm(dm):
    '''Determines what kind of DM this is.
        * Is this a score being submitted?
        * Is this a command to post the leaderboard?
        * Currently ignoring other DMs.
    '''
    
    print (DATABASE)
    print (DATABASE_USER)

    sender_id = dm['direct_message_events'][0]['message_create']['sender_id']
    message = dm['direct_message_events'][0]['message_create']['message_data']['text']

    print (f"Received a Direct Message from {sender_id} with message: {message}") #TODO: tweepy to get handle.

    if sender_id == HOST_ACCOUNT_ID: #Then special handling. #Ignore DM events from DM we sent.
        if is_leaderboard_command(message):
            send_leaderboard_tweet() #Tweet out leaderboard.
            response = "OK, gonna Tweet the leaderboard."
            send_direct_message(sender_id, response)
        else:
            pass #Ignoring by design.
    elif sender_id != HOST_ACCOUNT_ID:
        if is_score(message):
            success = handle_score(message) #Store score.
            if success:
                response = "Got it, thanks!"
                send_direct_message(sender_id, response)
                #Also confirm with leaderboard sent by DM
                send_leaderboard_dm(sender_id)
        elif is_leaderboard_command(message):
            if 'tweet' in message.lower() or 'post' in message.lower():
                send_leaderboard_tweet() #Tweet out leaderboard.
                response = "OK, gonna Tweet the current standings."
                send_direct_message(sender_id, response)
            else:
                send_leaderboard_dm(sender_id)
        elif is_update_command(message):
            success = update_score(message)
            if success:
                response = "Made update, thanks!"
                send_direct_message(sender_id, response)
                #Also confirm with leaderboard sent by DM
                send_leaderboard_dm(sender_id)
        else:
            pass #Completely ignoring other DMs. TODO: are there others we want to respond to?
            response = "Sorry, busy keeping score..."
            send_direct_message(sender_id, response)

#==================================================================================================================

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
    if 'direct_message_events' in request.json:
        handle_dm(request.json)
        return "200"
    # elif 'direct_message_indicate_typing_events' in request.json:
    #     pass
    # elif 'tweet_create_events' in request.json:
    #     # Testing with @HackerScorer mention, and had to parse User ID to know who mentined, and entities.user_mentions to know who they mentioned.
    #     pass
    # elif 'favorite_events' in request.json:
    #     pass

    return "200"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.getenv('PORT', 5000))
    # Logger code
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', port=port, debug=True)


##Saved 'callers' for unit testing.
# if __name__ == '__main__':

#   print (get_over_under(1,6))

#   create_standings()
#
# #   #Seeding database with data.  handle_score("t h s5")
# #     handle_score("t1 h1 s4")
# #     handle_score("t1 h2 s5")
# #     handle_score("t1 h3 s4")
#
    # for h in range(18):
    #     hole = h + 1
    #     for t in range(18):
    #         team = t + 1
    #         score = random.randrange(PARS[int(hole-1)]-1, PARS[int(hole-1)]+4, 1)
    #
    #         handle_score(f"t{team} h{hole} s{score}")
    #         time.sleep(2)


