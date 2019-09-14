# TweetScorer
Using the AAA, DM, and Post Tweet APIs, this thing listens for incoming scores, ranks them, and Tweets the rankings. 

# Notes

## Done
+ Set up @TwitterDev private repository (welcome!).
+ Created a new @HackerScorer account (not too late to find a better name!), applied for a Twitter developer account, got appoved within 24 hours, created a Twitter App, generated keys with R/W/DM permissions, established a premium AAA environment, and upgraded to enable two webhooks. Frankly, it was a painful process, but we got it done in about a day. 
+ Hosted Python Flask app on Heroku. Python build packs, Proc files, and refreshed requirements.txt files... 
+ Webhook set and @HackerScorer "self-subscribed." Now receiving account activities. Now the fun begins!

## Next
+ Set up (and document) ngrok for development stage.  
+ Add Tweet and DM functionality.
+ Compile scores and rank them.
