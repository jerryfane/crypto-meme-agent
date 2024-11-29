import time
from models.db_wrapper import DBWrapper
from twitter.api import TwitterAPI

class TweetScheduler:
    def __init__(self):
        self.db = DBWrapper()
        self.twitter = TwitterAPI()
    
    def run(self):
        """Run the scheduler"""
        while True:
            try:
                # Get next tweet to send
                tweet = self.db.get_next_tweet_to_send()
                if tweet:
                    # Send tweet
                    text = tweet['text_adjusted'] or tweet['text']
                    success = self.twitter.send_tweet(text)
                    if success:
                        self.db.mark_tweet_as_sent(tweet['id'])
                
                # Wait for next hour
                time.sleep(3600)
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    scheduler = TweetScheduler()
    scheduler.run()