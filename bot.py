from credentials import *
from time import sleep
from threading import Timer
import tweepy

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
tag = '#remindme'

def remember(text, tweetId, user):
    tweet = f'@{user} {text}'
    api.update_status(status=tweet, in_reply_to_status=tweetId)


def scheduleTweet(time, text, id, account):
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
    
        scheduleTweet(timeSec, text, tweetId, account)


myStream = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=myStream)
stream.filter(track=[tag])

