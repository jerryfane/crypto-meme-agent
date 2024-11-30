import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.meme_agent import MemeAgent
from src.models.db_wrapper import DBWrapper
from dotenv import load_dotenv
import os
from itertools import cycle
from tqdm import tqdm

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the database
    db = DBWrapper()
    
    # Initialize the agent
    config_path = "config/agent_config.yaml"
    model_path = "AIDC-AI/Marco-o1"
    # model_path="meta-llama/Llama-3.2-3B-Instruct"
    # model_path="chuanli11/Llama-3.2-3B-Instruct-uncensored"
    model_path="google/gemma-2-2b-it"
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
        agent = MemeAgent(config_path, model_path, examples_path, db=db)
        
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
                
                tweet = agent.generate_tweet(context)
                tweet_id = db.store_tweet(text=tweet, context=context)
                
                context_counts[context] += 1
                pbar.update(1)
                
                # Update progress bar description with context counts
                status = ", ".join([f"{k}: {v}/{tweets_per_context}" for k, v in context_counts.items()])
                pbar.set_description(f"Generating tweets | {status}")
                
    except Exception as e:
        print(f"Error in tweet generation: {e}")
        raise e

if __name__ == "__main__":
    main()