import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.meme_agent import MemeAgent

def test_generation():
    # Initialize agent with all necessary paths
    agent = MemeAgent(
        config_path="config/agent_config.yaml",
        model_path="meta-llama/Llama-3.2-3B-Instruct",
        examples_path="data/training/example_tweets.jsonl"
    )
    
    # Test different contexts
    contexts = [
        "trading_fails",
        "family_story",
        "runes",
        "market_influence"
    ]
    
    print("Testing tweet generation with different contexts...")
    for context in contexts:
        print(f"\n\nGenerating tweet for context: {context}")
        print("-" * 50)
        tweet = agent.generate_tweet(context=context)
        print(f"Generated tweet:\n{tweet}")

if __name__ == "__main__":
    test_generation()