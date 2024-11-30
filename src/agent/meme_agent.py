import json
import yaml
from pathlib import Path
import random
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
from openai import OpenAI

class MemeAgent:
    def __init__(self, config_path: str, examples_path: str, db=None):
        """Initialize MFM agent with configuration and examples."""
        self.config = self._load_config(config_path)
        self.file_examples = self._load_examples(examples_path)
        self.db = db
        
        # Initialize OpenAI client
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    def _clean_output(self, text: str) -> str:
        """Clean the generated output."""
        # Remove any remaining instruction markers at the start
        instruction_markers = [
            "Output:",
            "Response:",
            "Joke:",
            "Generated joke:",
            "Here's a joke:"
        ]
        
        for marker in instruction_markers:
            if text.startswith(marker):
                text = text[len(marker):].strip()
        
        # Remove hashtags and clean up whitespace
        text = ' '.join(word for word in text.split() if not word.startswith('#'))
        return text.strip()
    
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
    
    def generate_tweet(self, context: Optional[str] = None, num_examples: int = 3) -> str:
        """Generate a tweet with context-specific examples."""
        # Combine file examples and database examples
        available_examples = []
        
        # Get examples from file
        if context and context in self.file_examples:
            available_examples.extend(self.file_examples[context])
        else:
            available_examples.extend([
                tweet for tweets in self.file_examples.values() 
                for tweet in tweets
            ])
            
        # Add best performing examples from database
        if self.db:
            best_examples = self._get_best_examples(context)
            if best_examples:
                available_examples.extend(best_examples)
        
        # Select random examples, prioritizing database examples
        selected_examples = []
        db_examples = [ex for ex in available_examples if ex in best_examples] if self.db else []
        file_examples = [ex for ex in available_examples if ex not in db_examples]
        
        # Try to include at least one database example if available
        if db_examples:
            selected_examples.append(random.choice(db_examples))
            num_examples -= 1
        
        # Fill remaining slots with random examples
        remaining_examples = db_examples + file_examples
        if remaining_examples and num_examples > 0:
            selected_examples.extend(random.sample(
                remaining_examples,
                min(num_examples, len(remaining_examples))
            ))
        
        examples_text = "\n".join(f"Example {i+1}: {example}" 
                                for i, example in enumerate(selected_examples))
        
        # Generate using OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Changed from gpt-4-0125-preview
            messages=[
                {"role": "system", "content": self.config['prompt']['system_message']},
                {"role": "user", "content": f"Examples:\n{examples_text}\n\nGenerate ONE tweet about {context}"}
            ],
            temperature=self.config['meme_generation']['temperature'],
            max_tokens=self.config['meme_generation']['max_new_tokens'],
            top_p=self.config['meme_generation']['top_p'],
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        # Extract and clean the response
        generated_text = response.choices[0].message.content
        cleaned_tweet = self._clean_output(generated_text)
        
        return cleaned_tweet