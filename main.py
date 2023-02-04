import os
import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class TweetMiner:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, list_id):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.list_id = list_id
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

    def create_sheet(self):
        # スコープと認証情報を使って認証を行う
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
        client = gspread.authorize(credentials)

        now = datetime.now()
        new_sheet_name = now.strftime("%Y-%m-%d")
        spreadsheet = client.open("TweetMine")
        sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=1, cols=2)
        sheet.append_row(["ユーザー名", "ツイート内容"])
        return sheet

    def mine_tweets(self, sheet):
        count = 0
        list_members = self.api.get_list_members(list_id=self.list_id, count=10)
        for member in list_members:
            tweets = self.api.user_timeline(screen_name=member.screen_name)
            for tweet in tweets:
                if tweet.favorite_count >= 80:
                    sheet.append_rows([[tweet.user.name, tweet.text]])
                    count += 1
                    if count >= 40:
                        time.sleep(60)
                        count = 0

# 環境変数から認証情報を取得
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')
list_id = os.environ.get('list_id')

tweet_miner = TweetMiner(consumer_key, consumer_secret, access_token, access_token_secret, list_id)
sheet = tweet_miner.create_sheet()
tweet_miner.mine_tweets(sheet)