import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
import os

def test_model_access():
    # Load environment variables
    load_dotenv()
    
    # Get the token
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables")
    
    print("Testing Hugging Face model access...")
    
    try:
        # Try to load the tokenizer first (this is faster than loading the full model)
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "nvidia/llama-3.1-Nemotron-70B-Instruct-HF",
            token=hf_token
        )
        print("✓ Successfully loaded tokenizer!")
        
        # Test a simple tokenization
        test_text = "MarsCryptoSage says: To the moon! 🚀"
        tokens = tokenizer(test_text, return_tensors="pt")
        print(f"\nSuccessfully tokenized test text:")
        print(f"Input text: {test_text}")
        print(f"Number of tokens: {tokens.input_ids.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"Error accessing model: {e}")
        return False

if __name__ == "__main__":
    test_model_access()