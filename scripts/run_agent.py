import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.meme_agent import CryptoMemeAgent
from dotenv import load_dotenv
import os

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the agent with Nemotron model
    config_path = "config/agent_config.yaml"
    model_path = "nvidia/llama-3.1-Nemotron-70B-Instruct-HF"
    
    try:
        print("Initializing agent with Nemotron model...")
        agent = CryptoMemeAgent(config_path, model_path)
        
        # Test meme generation with different contexts
        contexts = [
            "Bitcoin just hit a new all-time high",
            "Ethereum gas fees are through the roof",
            None  # Generate without context
        ]
        
        for context in contexts:
            print(f"\nGenerating meme with context: {context if context else 'No context'}")
            meme = agent.generate_meme(context)
            print(f"Generated meme: {meme}")
            
    except Exception as e:
        print(f"Error initializing agent: {e}")
        raise e

if __name__ == "__main__":
    main()