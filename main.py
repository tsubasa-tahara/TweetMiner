import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

list_id = os.environ.get('list_id')
list_members = api.get_list_members(list_id=list_id, count=10)

for member in list_members:
    tweets = api.user_timeline(screen_name=member.screen_name)
    for tweet in tweets:
        if tweet.favorite_count >= 50:
            print(f"{tweet.user.name}:{tweet.text}")
