import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.meme_agent import MemeAgent
from src.models.db_wrapper import DBWrapper
from dotenv import load_dotenv
import os
from itertools import cycle
from tqdm import tqdm
import time

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not os.getenv("DATABASE_URL"):
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # Initialize the database
    db = DBWrapper()
    
    # Initialize the agent
    config_path = "config/agent_config.yaml"
    examples_path = "data/training/example_tweets.jsonl"
    
    # Configuration
    tweets_per_context = 50
    contexts = [
        "trading_fails",
        "family_story",
        "runes",
        "market_influence"
    ]
    
    try:
        print("Initializing agent...")
        agent = MemeAgent(config_path, examples_path, db=db)
        
        # Create a cyclic iterator for contexts
        context_cycle = cycle(contexts)
        
        # Track number of tweets generated for each context
        context_counts = {context: 0 for context in contexts}
        total_tweets = len(contexts) * tweets_per_context
        
        # Main progress bar
        with tqdm(total=total_tweets, desc="Generating tweets") as pbar:
            while sum(context_counts.values()) < total_tweets:
                context = next(context_cycle)
                
                # Skip if we've generated enough tweets for this context
                if context_counts[context] >= tweets_per_context:
                    continue
                
                try:
                    # Generate and store tweet
                    tweet = agent.generate_tweet(context)
                    tweet_id = db.store_tweet(text=tweet, context=context)
                    
                    context_counts[context] += 1
                    pbar.update(1)
                    
                    # Update progress bar description with context counts
                    status = ", ".join([f"{k}: {v}/{tweets_per_context}" 
                                      for k, v in context_counts.items()])
                    pbar.set_description(f"Generating tweets | {status}")
                    
                    # Add a small delay to avoid rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"\nError generating tweet for context {context}: {e}")
                    print("Continuing with next tweet...")
                    continue
                
    except Exception as e:
        print(f"Error in tweet generation: {e}")
        raise e

if __name__ == "__main__":
    main()