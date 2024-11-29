import yaml
import random
from pathlib import Path
from typing import Dict, List, Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class CryptoMemeAgent:
    def __init__(self, config_path: str, model_path: str):
        """
        Initialize the Crypto Meme Agent.
        
        Args:
            config_path: Path to the agent configuration file
            model_path: Path to the pre-trained or fine-tuned model
        """
        self.config = self._load_config(config_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize model and tokenizer
        self._initialize_model(model_path)
        
        # Load agent personality
        self.name = self.config["agent"]["name"]
        self.traits = self.config["agent"]["character_traits"]
        self.catchphrases = self.config["agent"]["catchphrases"]
        
        # Template management
        self.templates = self.config["templates"]
    
    def _load_config(self, config_path: str) -> Dict:
        """Load and parse the YAML configuration file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_model(self, model_path: str):
        """Initialize the language model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        ).to(self.device)
    
    def generate_meme(self, context: Optional[str] = None) -> str:
        """
        Generate a crypto meme based on the agent's personality and optional context.
        
        Args:
            context: Optional context to influence meme generation
            
        Returns:
            str: Generated meme text
        """
        # Select template category and template
        category = random.choice(list(self.templates.keys()))
        template = random.choice(self.templates[category])
        
        # Build prompt
        prompt = self._build_prompt(template, context)
        
        # Generate response
        return self._generate_response(prompt)
    
    def _build_prompt(self, template: str, context: Optional[str]) -> str:
        """Build a prompt for the language model."""
        base_prompt = (
            f"As {self.name}, a legendary crypto sage from {self.config['agent']['base_location']}, "
            f"generate a humorous crypto meme. "
        )
        
        if context:
            base_prompt += f"Context: {context}\n"
        
        return base_prompt + f"Template: {template}"
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using the language model."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=self.config["meme_generation"]["max_length"],
            temperature=self.config["meme_generation"]["temperature"],
            top_p=self.config["meme_generation"]["top_p"],
            top_k=self.config["meme_generation"]["top_k"],
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def react_to_tweet(self, tweet_text: str) -> str:
        """
        Generate a contextual response to a tweet.
        
        Args:
            tweet_text: The text of the tweet to respond to
            
        Returns:
            str: Generated response
        """
        return self.generate_meme(context=tweet_text)
    
    @property
    def interaction_settings(self) -> Dict:
        """Get Twitter interaction settings."""
        return self.config["twitter"]

    def get_random_catchphrase(self) -> str:
        """Return a random catchphrase."""
        return random.choice(self.catchphrases)