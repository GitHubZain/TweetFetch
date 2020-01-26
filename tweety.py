import pandas as pd
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import twitter_credentials


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_output, search_terms):
        listener = TwitterListener(fetched_tweets_output)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=search_terms)


class TwitterListener(StreamListener):

    def __init__(self, fetched_tweets_output):
        self.fetched_tweets_output = fetched_tweets_output

    def on_data(self, data):
        try:
            pandata = pd.read_json(data)
            # didn't work until I used the pandas dataframe
            if pandata.user.followers_count > 10000:  # filters by number of followers the tweeter has
                print(data)
                with open(self.fetched_tweets_output, 'a') as tf:
                    tf.write(data + ",")  # writes the returned JSON into the file you assigned to fetched_tweets_output
            return True
        except BaseException as ex:
            print("Error on_data %s" % str(ex))
        return True

    def on_error(self, status):
        if status == 420:
            return False
        print(status)


if __name__ == '__main__':
    search_terms = ["Kashmir"]  # Enter whatever search term you want to keep track of
    fetched_tweets_output = "tweets.csv"  # make the file in the same directory as the program

    twitter_client = TwitterClient('pycon')
    print(twitter_client.get_user_timeline_tweets(1))

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_output, search_terms)
