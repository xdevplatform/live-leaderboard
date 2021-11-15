---
title: Getting started with Twitter chatbots
published: false
description:
tags: Twitter, chatbot, webhooks, python
---
## So, you want to build a Twitter chatbot?

Awesome! Now before you jump in, just know that there is a fair amount of effort needed to build the chatbot and you’ll need to be familiar with (or learn!) the following:

+ Webhooks. You’ll need to learn about webhooks (here’s a primer). There is some (fun) discovery to do there if you’re unfamiliar.
+ Deploying a web app. You must learn the basics of implementing and deploying a basic web app. Here are some helpful tutorials:
  + https://stackabuse.com/deploying-a-flask-application-to-heroku/
  + https://devcenter.heroku.com/articles/getting-started-with-python
+ The Twitter API. There are at least three Twitter API endpoints that your chatbot app should integrate:
  + [Account Activity](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview) - This webhook-based (!) API sends real-time "events" for subscribed accounts. The chatbot events of interest are incoming Direct Messages with user requests.
  + [Direct Message](https://developer.twitter.com/en/docs/direct-messages/api-features) - This API provides a private communication channel, along with essential user-interface support such as Welcome Messages. Be sure to set your chatbot's Twitter account to have open Direct Messages, meaning you can receive DMs from Twitter users that do not follow you.
  + [Post Tweet](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update) - Most chatbots support public interactions.

If you are unfamiliar with these endpoints, check out the documentation links above.

You’ll need an approved Twitter developer account and a Twitter App in order to integrate with these Twitter endpoints. [Apply for an account](https://developer.twitter.com/en/apply-for-access).

### Example chatbot code

A great way to get started with your first chatbot is to play and work with example code. Here are two examples that may help jumpstart your efforts:

+ [Python/Flash example](https://github.com/twitterdev/live-leaderboard) - The [@HackerScorer](https://twitter.com/HackerScorer) was a field-tested protoype of a live leaderboard for golf tournaments.
+ [Ruby/Sinatra example](https://github.com/twitterdev/SnowBotDev) - The [@SnowBotDev chatbot](https://twitter.com/SnowBotDev) chatbot delivers snow reports for areas around the world, as well as sharing snow related photos, playlists, and research links.

### Account Activity helper scripts

Effectively managing the webhook link between Twitter and your web app demands some automation. As you develop your chatbot UX, you'll iterate the Welcome Message design.

In support of the Live Leaderboard project, [a set of Python scripts](https://github.com/twitterdev/live-leaderboard/tree/main/scripts) was written to help with webhook configuration.

{Describe what these scripts provde}

## Starting development
So, what comes first? The server or the web app? Both come early in the prototyping process, and in our case, we built out the Flask web app relatively quickly (more details below).

Meanwhile, we figured out the tunneling necessary to enable events coming from the Twitter webhook publisher to arrive on our development laptops. We ended up using the [ngrok](https://ngrok.com/) tool and quickly had the development environment needed.

Next, we'll take a code tour of the Flask-based web app for the live leaderboard prototype.

### Building a simple Flask web app

Coming into this project, we had experience building a [Ruby-based @SnowBotDev chatbot](https://twitter.com/SnowBotDev) using the Sinatra web app framework. This time we wanted to use Python, so we decided to build this web app using the Python equivalent, Flask. Luckily, the two frameworks are similar enough, that our previous Sinatra experience helped us quickly make progress with Flask.

Regardless of the web app framework you select, there are three "routes" that should plan on supporting:

+ GET / - The default 'home' path of your web app. Here you have the option to serve up information about your chatbot.
+ GET /webhook - This path is used to first establish the connection between Twitter and your web app. Once established, Twitter will "challenge" your authenticated "ownership" of the web app on a regular basis. See below for more details.
Note: While the 'webhook' path is a reasonable default, this path is up to you. If you are consuming other webhook events, this could be something like "twitter_webhook".
+ POST /webhook - The path where Twitter will send account events via the Account Activity endpoint.
Note: the "webhook" path can be what you want. A key point is that this path needs to support both GET and POST HTTP methods.

When using Flask, here is a simplified look at the web app code:

```python
app = Flask(__name__)

#generic index route
@app.route('/')
def default_route():
    return "Hello world"

@app.route("/webhook", methods=["GET"])
def twitter_crc_validation():
    return response)

@app.route("/webhook", methods=["POST"])
def event_manager():
    return "200"
```

When the flask app starts up, execution starts with the following code that binds the web app to port 5000.

```python
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.getenv('PORT', 5000))
    # Logger code
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', port=port, debug=True)
```

### Stand up the web app and register it with Twitter

 {set up on Heroku with a postgres database}. First step is implementing the CRC response handler, then implementing an Account Activity API webhook consumer.

#### Implement a CRC handler

A fundamental step of deploying a Twitter chatbot is [registering the chatbot with Twitter](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/securing-webhooks). This registration establishes the link between Twitter and your chatbot web app. When registering, you will provide the URL where webhooks should be sent, and the Twitter Account Activity API will immediately request your app's **consumer secret** token. This process is referred to as a Challenge-Response Check (CRC). After registration, Twitter will continue to issue CRCs frequently to confirm the security of your webhook server.

To help develop your CRC response code, you can manually trigger a CRC by making a PUT request.

The following code implements CRC code for a Flash GET route (/webhook) registered with Twitter:

```python
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
```


# Putting it all together

Once the web app is deployed and responding to CRC requests, the fun begins. After the plumbing is set-up, you can start implementing your chatbot's 'skills.'

