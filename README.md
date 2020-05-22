# Live Leaderboard
Using the Account Activity, Direct Message, and Post Tweet APIs, this Twitter chatbot listens for incoming scores, ranks them, and Tweets the rankings. This app supports public announcements and private data/vote submissions.

This example was written to keep golf scores, but the underlying patterns are general enough to serve many other use cases. 

To learn more about the event this pilot was developed for, see the following: 

+ The use case inspiration for this code base is HERE [insights.twitter.com].
+ For more discussion of the code developed for this pilot, see HERE [dev.to/building-a-live-leaderboard-on-Twitter]

Getting started
===============

So, here is what you'll need to get started:

+ Python3 environment with the Flask web framework.
+ Somewhere to host the app. For this project we used Heroku.
+ Twitter details:
+ Twitter Developer account: if you don’t have one already, you can apply for one [HERE]().
  + Create a Twitter App if you don't already have one.
  + Consumer API keys for your app. 
  + Get to know the Account Activity endpoint: https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/getting-started-with-webhooks
  + Have a Twitter account to host the scorer app, and register that account with the AAA. For this prototype we used the [@HackerScorer](https://twitter.com/HackerScorer) account. 

FAQ
===

**What if I forget to DM the bot after playing a hole?** 
That's ok! Just send a DM for any hole you forgot to submit. 

**What if I enter my score wrong?**
TRY NOT TO. Enter your team number, hole, and score very carefully. If you mess up, send an 'update' DM. For example, if you DM'ed ```t6 h4 s5``` but the correct score was ```4```, DM ```update t6 h4 s4```. 

**How do I know if I did it right?** 
A correctly formatted score receives a confirmation DM (currently 'Thanks, we got it!"), and if that is not received, then the score was not accepted. 

**I'm on a team of four, do we all have to do this?**
No. Designate one team mate to do this after each hole. Try to remind your team mate to do this!

**Should we remove par (over/under)?**
Submit the TOTAL number of strokes that your team took. Do NOT subtract par. For example, if your team hit 5 times on a par 3, your score is 5. NOT 2.

**Does our team still have to keep score with the paper scorecard?**
YES! This is your final scorecard for determining the winning team at the end. This bot is an experiment and for fun.





