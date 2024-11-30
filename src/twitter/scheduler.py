import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import time
import random
from typing import Optional
from models.db_wrapper import DBWrapper
from dotenv import load_dotenv
import os
from psycopg2.extras import RealDictCursor
import tweepy

class TweetScheduler:
    def __init__(self):
        load_dotenv()
        self.db = DBWrapper()
        
        # Initialize Twitter API v2 client with all necessary tokens
        self.twitter = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )

        print("Twitter client initialized with full authentication")
    
    def get_random_approved_tweet(self) -> Optional[dict]:
        """Get a random approved tweet that hasn't been sent"""
        with self.db.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                WITH unsent_tweets AS (
                    SELECT id, COALESCE(text_adjusted, text) as text
                    FROM tweets 
                    WHERE status = 'approved' 
                    AND sent_at IS NULL
                    AND score >= 2
                )
                SELECT * FROM unsent_tweets
                ORDER BY RANDOM()
                LIMIT 1
                """
            )
            return cur.fetchone()
    
    def send_tweet(self, tweet_text: str) -> bool:
        """Send a tweet and handle any errors"""
        try:
            print(f"Attempting to send tweet: {tweet_text}")
            response = self.twitter.create_tweet(text=tweet_text)
            if response.data:
                print(f"Tweet sent successfully! Tweet ID: {response.data['id']}")
                return True
            return False
        except Exception as e:
            print(f"Error sending tweet: {e}")
            print("Make sure you have enabled 'Read and Write' permissions in your Twitter App settings")
            return False
    
    def run_once(self) -> bool:
        """Run one iteration of the scheduler"""
        try:
            # Get random approved tweet
            tweet = self.get_random_approved_tweet()
            if not tweet:
                print("No approved tweets available to send")
                return False
            
            # Send tweet
            success = self.send_tweet(tweet['text'])
            if success:
                # Mark as sent
                self.db.mark_tweet_as_sent(tweet['id'])
                print(f"Successfully sent and marked tweet (ID: {tweet['id']})")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in scheduler: {e}")
            return False
    
    def run(self, interval_seconds: int = 5400):
        """Run the scheduler continuously"""
        print(f"Starting tweet scheduler (interval: {interval_seconds} seconds)")
        
        while True:
            try:
                print("\nChecking for tweets to send...")
                self.run_once()
                print(f"Waiting {interval_seconds} seconds until next check...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\nScheduler stopped by user")
                break
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait a bit before retrying

if __name__ == "__main__":
    scheduler = TweetScheduler()
    scheduler.run()