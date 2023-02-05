import argparse
import os
import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import time
from datetime import datetime
import datetime
from pytz import timezone

load_dotenv()
local_tz = timezone('Asia/Tokyo')


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

        now = datetime.datetime.now()
        new_sheet_name = now.strftime("%Y-%m-%d")
        spreadsheet = client.open(spread_sheet_name)
        sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=1, cols=2)
        sheet.append_row(["ユーザー名", "ツイート内容"])
        return sheet

    def mine_tweets(self, sheet, start_date, end_date, word=None):
        count = 0
        start_date = local_tz.localize(start_date)
        end_date = local_tz.localize(end_date)

        list_members = self.api.get_list_members(list_id=self.list_id, count=20)
        tweets = []
        for member in list_members:
            tweets += self.api.user_timeline(screen_name=member.screen_name)
        if word:
            tweets = [tweet for tweet in tweets if word in tweet.text]
        tweets = [tweet for tweet in tweets if tweet.favorite_count >= 10]
        tweets = [tweet for tweet in tweets if start_date <= tweet.created_at <= end_date]
        for tweet in tweets:
            sheet.append_rows([[tweet.user.name, tweet.text]])
            count += 1
            if count >= 40:
                time.sleep(60)
                count = 0


# Argparseを使って引数を解析する
parser = argparse.ArgumentParser(description='Twitterから特定のツイートを検索します')
parser.add_argument('-s', '--start_date', type=str, required=True, help='検索開始日付（YYYY-MM-DD形式）')
parser.add_argument('-e', '--end_date', type=str, required=True, help='検索終了日付（YYYY-MM-DD形式）')
parser.add_argument('-w', '--word', type=str, required=False, help='検索ワード')

args = parser.parse_args()
start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
word = args.word

# 環境変数から認証情報を取得
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')
spread_sheet_name = os.environ.get('spread_sheet_name')
list_id = os.environ.get('list_id')

tweet_miner = TweetMiner(consumer_key, consumer_secret, access_token, access_token_secret, list_id)
sheet = tweet_miner.create_sheet()
tweet_miner.mine_tweets(sheet, start_date, end_date, word)
