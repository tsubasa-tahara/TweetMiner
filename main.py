import os
import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

# 環境変数から認証情報を取得
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

# スコープと認証情報を使って認証を行う
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = gspread.authorize(credentials)

# todo なぜかこのコードだと動かない
# now = datetime.now()
# new_sheet_name = now.strftime("%Y-%m-%d %H:%M:%S")

new_sheet_name = "sampletest"
spreadsheet = client.open("TweetMine")


sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=1, cols=2)
print(sheet)

sheet.append_row(["ユーザー名", "ツイート内容"])

print(sheet)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

# Get the User object for twitter...
list_id = os.environ.get('list_id')
if list_id is None:
    print("list_id is not set.")
    sys.exit()

count = 0
list_members = api.get_list_members(list_id=list_id, count=10)
for member in list_members:
    tweets = api.user_timeline(screen_name=member.screen_name)
    for tweet in tweets:
        if tweet.favorite_count >= 80:
            sheet.append_rows([[tweet.user.name, tweet.text]])
            count += 1
            if count >= 40:
                time.sleep(60)
                count = 0
