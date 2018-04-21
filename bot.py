from credentials import *
from time import sleep
import time as Time
from threading import Timer
import json
import tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
tag = '#remindme'
file_name = 'tweets.json'

fn = open(file_name)
tweets = json.load(fn)

for tweet in tweets:
    t = tweet['actualTime'] + tweet['time']
    actualT = time.time()
    if (t > actualT) or ((t-actualT) < 1800):
        new_time = t - actualT
        tw = Timer(new_time, remember,
                args = [
                    tweet['text'],
                    tweet['id'],
                    tweet['account']
                ]
            )
        tw.start()

def remember(text, tweetId, user):
    tweet = f'@{user} {text}'
    api.update_status(status=tweet, in_reply_to_status=tweetId)

def scheduleTweet(actualTime, time, text, id, account):
    f = open(file_name, 'a')
    tweetJson = {
            'actualTime': actualTime,
            'time': time,
            'text': text,
            'account': account,
            'id': id
    }
    tweets.append(tweetJson)
    json.dump(tweets, f)
    f.close()

    t = Timer(time, remember, 
            args=[text, id, account]
        )
    t.start()


class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.retweeted or 'RT @' in status.text:
            return None

        tweet = status.text
        account = status.user.screen_name
        tweetId = status.id
        
        try:
            text, time = tweet.split('&gt;') 
            if 'min' in time and 'h' in time:
                time = time.replace('h', '*3600*').replace('min', '*60')
            elif 'd' in time:
                time = time.replace('d', '*86400')
            else:
                time = time.replace('h', '*3600').replace('min', '*60')
            time = time.split('*')
            time = list(map(int, time))
            timeSec = 1
            for i in time:
                timeSec*=i
        except:
            return None

        text = text.replace(tag, '')
        actualTime = Time.time()
    
        scheduleTweet(actualTime, timeSec, text, tweetId, account)

        confirmed_text = f'@{account} reminder confirmed'
        api.update_status(status=confirmed_text, in_reply_to_status=tweetId)


myStream = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=myStream)
stream.filter(track=[tag])

