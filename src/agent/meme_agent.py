import json
import yaml
from pathlib import Path
import random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

class MemeAgent:
    def __init__(self, config_path: str, model_path: str, examples_path: str):
        """Initialize MFM agent with configuration and examples."""
        self.config = self._load_config(config_path)
        self.examples = self._load_examples(examples_path)
        
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

    def _clean_output(self, text: str) -> str:
        """Clean the generated output to remove meta-commentary."""
        # Remove common meta-commentary patterns
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that look like meta-commentary
            if any(pattern in line.lower() for pattern in [
                'note:', 'tweet:', 'example:', 'generated:', 'output:',
                'let me know', 'please keep', 'would you like'
            ]):
                continue
            cleaned_lines.append(line)
        
        # Join remaining lines and clean up
        text = ' '.join(cleaned_lines)
        # Remove any remaining [INST] tags
        text = text.replace('[INST]', '').replace('[/INST]', '')
        return text.strip()
    
    def generate_tweet(self, context: Optional[str] = None, num_examples: int = 3) -> str:
        """Generate a tweet with context-specific examples."""
        # Select relevant examples
        if context and context in self.examples:
            selected_examples = random.sample(
                self.examples[context], 
                min(num_examples, len(self.examples[context]))
            )
        else:
            all_examples = [tweet for tweets in self.examples.values() for tweet in tweets]
            selected_examples = random.sample(all_examples, min(num_examples, len(all_examples)))
        
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
        
        # Ensure it's not too long for a tweet
        if len(cleaned_tweet) > 280:
            cleaned_tweet = cleaned_tweet[:277] + "..."
            
        return cleaned_tweet