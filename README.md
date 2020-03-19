# LiveLeaderboard
Using the Account Activity, Direct Message, and Post Tweet APIs, this Twitter chatbot listens for incoming scores, ranks them, and Tweets the rankings. This app supports public announcements and private data/vote submissions.

This example was written to keep golf scores, but the underlying patterns are general enough to serve many other use cases. 

To learn more about the event this pilot was developed for, see the following: 

+ The use case inspiration for this code base is HERE [insights.twitter.com].
+ For more discussion of the code developed for this pilot, see HERE [dev.to/building-a-live-leaderboard-on-Twitter]


So, here is what you'll need to get started:

+ Python3 environment with the Flask web framework.
+ Somewhere to host the app. For this project we used Heroku.

+ Twitter Developer account: if you don’t have one already, you can apply for one [HERE]().
+ Create a Twitter App if you don't already have one.
+ Consumer API keys for your app. 
+ Get to know the Account Activity endpoint: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/getting-started-with-webhooks
+ Have a Twitter account to host the scorer app, and register that account with the AAA. For this prototype we used the @HackerScorer account. 





