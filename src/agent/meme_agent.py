import json
import yaml
from pathlib import Path
import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
from src.models.db_wrapper import DBWrapper

class MemeAgent:
    def __init__(self, config_path: str, model_path: str, examples_path: str, db: Optional[DBWrapper] = None):
        """Initialize MFM agent with configuration and examples."""
        self.config = self._load_config(config_path)
        self.file_examples = self._load_examples(examples_path)
        self.db = db
        
        # Device setup for Mac MPS
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
            
        print(f"Using device: {self.device}")
        
        # Set environment variable for tokenizers
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Load model and tokenizer
        load_dotenv()
        self.model_path = model_path
        self._initialize_model()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load YAML configuration file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_examples(self, examples_path: str) -> Dict[str, List[str]]:
        """Load example tweets grouped by context."""
        examples = {}
        with open(examples_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                context = data['context']
                if context not in examples:
                    examples[context] = []
                examples[context].append(data['tweet'])
        return examples
    
    def _initialize_model(self):
        """Initialize the model and tokenizer."""
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            token=os.getenv("HF_TOKEN"),
            padding_side="left"
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            token=os.getenv("HF_TOKEN"),
            device_map="auto",
            torch_dtype=torch.float16
        )

    def _get_best_examples(self, context: Optional[str] = None) -> List[str]:
        """Get best performing examples from the database"""
        if not self.db:
            return []
            
        best_tweets = self.db.get_best_tweets()
        if not context:
            return [tweet['text'] for tweet in best_tweets]
            
        return [
            tweet['text'] for tweet in best_tweets 
            if tweet['context'] == context
        ]

    def _clean_output(self, text: str) -> str:
        """Clean the generated output to remove system messages and format properly."""
        # Remove system message sections
        if "<<SYS>>" in text and "<</SYS>>" in text:
            text = text.split("<</SYS>>")[1]  # Get content after system message

        # Find the actual tweet content
        if "Task:" in text:
            text = text.split("Task:")[1]  # Get content after Task

        # Clean up common artifacts
        text = text.replace("[INST]", "").replace("[/INST]", "")
        
        # Remove any remaining newlines or multiple spaces
        text = ' '.join(text.split())
        
        # Remove any remaining instruction markers at the start
        instruction_markers = [
            "Write ONLY",
            "Must NOT",
            "MUST BE",
            "Generate ONE tweet",
            "- Must",
            "Write it in",
        ]
        
        for marker in instruction_markers:
            if text.strip().startswith(marker):
                text = text.replace(marker, "", 1).strip()

        # Remove hashtags
        text = ' '.join(word for word in text.split() if not word.startswith('#'))
        
        return text.strip()
    
    def generate_tweet(self, context: Optional[str] = None, num_examples: int = 3) -> str:
        """Generate a tweet with context-specific examples."""
        # Combine file examples and best performing tweets
        available_examples = []
        
        # Get examples from file
        if context and context in self.file_examples:
            available_examples.extend(self.file_examples[context])
        else:
            available_examples.extend([
                tweet for tweets in self.file_examples.values() 
                for tweet in tweets
            ])
            
        # Add best performing examples
        best_examples = self._get_best_examples(context)
        available_examples.extend(best_examples)
        
        # Select random examples from combined pool
        selected_examples = random.sample(
            available_examples,
            min(num_examples, len(available_examples))
        )
        
        examples_text = "\n".join(f"Tweet {i+1}: {example}" for i, example in enumerate(selected_examples))
        
        # Get prompt template from config
        prompt = self.config['prompt']['format'].format(
            system_message=self.config['prompt']['system_message'],
            examples=examples_text,
            context=context if context else 'crypto trading'
        )

        # Ensure inputs are on the correct device
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            return_attention_mask=True,
            truncation=True,
            max_length=512
        )
        
        # Move inputs to the correct device
        input_ids = inputs.input_ids.to(self.device)
        attention_mask = inputs.attention_mask.to(self.device)
        
        # Get generation settings from config
        gen_config = self.config['meme_generation']
        
        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=gen_config['max_new_tokens'],
            min_new_tokens=gen_config['min_new_tokens'],
            temperature=gen_config['temperature'],
            top_p=gen_config['top_p'],
            top_k=gen_config['top_k'],
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=gen_config['repetition_penalty']
        )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        raw_output = generated_text.split("[/INST]")[-1].strip()
        
        # Clean the output
        cleaned_tweet = self._clean_output(raw_output)
            
        return cleaned_tweet