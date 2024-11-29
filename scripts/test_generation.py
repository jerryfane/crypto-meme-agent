import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv
import os

def test_model_generation():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    # model_name = "meta-llama/Llama-3.1-8B-Instruct"
    
    try:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=hf_token,
            padding_side="left"
        )
        tokenizer.pad_token = tokenizer.eos_token
        
        print("Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=hf_token,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        system_prompt = """You are Marx Fren Monke (MFM), a lovably naive crypto trader living on Mars. 
        Generate short, tweet-length posts (max 280 chars) in the 'fren-speak' style about your crypto adventures."""

        user_prompt = """Write a single tweet about your latest crypto trading adventure. 
        Use fren-speak (ser, fren, gm, wagmi), include emojis, and show your endearing overconfidence 
        despite probable trading mistakes."""
        
        prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt}

Example tweets:
"gm frens! 🐵 just aped into new memecoin called $MARS ser... trustme its going 100x, source: my horoscope 🚀 (not financial advice but am expert)"
"ser @casey_rodarmor reviewed my rune protocol... he said 'pls stop' but that means bullish right? 📈 wagmi!"

Generate a NEW tweet, different from these examples:[/INST]"""
        
        print("\nGenerating test meme...")
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            return_attention_mask=True,
            truncation=True,
            max_length=512
        ).to(model.device)
        
        print("Starting generation...")
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=70,    # Shorter for tweet length
            min_new_tokens=10,    # Ensure we get a complete thought
            temperature=0.9,
            top_p=0.9,
            top_k=50,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.2
        )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = generated_text.split("[/INST]")[-1].strip()
        print("\nGenerated tweet:")
        print(response)
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_model_generation()