import yaml
from pathlib import Path
import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, List

class MarxFrenAgent:
    def __init__(self, config_path: str, model_path: str):
        """Initialize Marx Fren Monke agent."""
        self.config = self._load_config(config_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Initialize model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            token=os.getenv("HF_TOKEN"),
            padding_side="left"
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            token=os.getenv("HF_TOKEN"),
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        # Load personality traits
        self.name = self.config["agent"]["name"]
        self.catchphrases = self.config["agent"]["catchphrases"]
    
    def generate_tweet(self, context: Optional[str] = None) -> str:
        """Generate a tweet based on optional context."""
        system_prompt = """You are Marx Fren Monke (MFM), a lovably naive crypto trader living on Mars. 
        Generate short, tweet-length posts (max 280 chars) in the 'fren-speak' style about your crypto adventures."""
        
        user_prompt = f"""Write a single tweet about {context if context else 'your latest crypto trading idea'}. 
        Use fren-speak (ser, fren, gm, wagmi), include emojis, and show your endearing overconfidence."""
        
        prompt = f"""[INST] <<SYS>>{system_prompt}<</SYS>>{user_prompt}[/INST]"""
        
        return self._generate_response(prompt)
    
    def reply_to_tweet(self, tweet_text: str) -> str:
        """Generate a reply to a given tweet."""
        system_prompt = """You are Marx Fren Monke (MFM), responding to another crypto trader's tweet.
        Keep your reply short, funny, and show your endearing misunderstanding of crypto concepts."""
        
        user_prompt = f"""Someone tweeted: "{tweet_text}"
        Write a single reply tweet. Use fren-speak and emojis."""
        
        prompt = f"""[INST] <<SYS>>{system_prompt}<</SYS>>{user_prompt}[/INST]"""
        
        return self._generate_response(prompt)
    
    def _generate_response(self, prompt: str) -> str:
        """Internal method to generate responses."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            return_attention_mask=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        outputs = self.model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=70,
            min_new_tokens=10,
            temperature=0.9,
            top_p=0.9,
            top_k=50,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.2
        )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text.split("[/INST]")[-1].strip()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load and parse the YAML configuration file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)