# TweetScorer
Using the Account Activity, Direct Message, and Post Tweet APIs, this thing listens for incoming scores, ranks them, and Tweets the rankings. This app supports public announcements and private data/vote submissions.

This example was written to keep golf scores, but the underlying patterns are general enough to serve many other use cases. 



# Notes

## Next steps
+ Handle hole-in-holes ;)
+ Revisit configuration details.
  + Handles can indicate the team, so could reduce input.
+ More 'Marshal' commands.
  + Database actions - initialize, top 10s, and stats.
  




## Done
+ Set up @TwitterDev private repository (welcome!).
+ Built the required plumbing: 
  + Created a new @HackerScorer account. 
  + Applied for a Twitter developer account, got appoved within 24 hours, created a Twitter App, generated keys with R/W/DM permissions, established a premium AAA environment, and upgraded to enable *two* webhooks. Frankly, it was a painful process, but we got it done in about a day. 
+ Hosted Python Flask app on Heroku. Python build packs, Proc files, and refreshed requirements.txt files... 
+ Webhook set and @HackerScorer "self-subscribed." Now receiving account activities. Now the fun begins!
+ Set up (and document) ngrok for development stage.  
+ Add Tweet and DM functionality.
+ Compile scores and rank them.
+ Design 'leaderboard' with matplotlib and magic formatng tricks. Disproportionate amount of effort here...
+ Implement 'update score' mechanism.
