#!/usr/bin/env python3
"""
Quick recovery script to recreate the modular SFT structure.
"""

import os
import sys

def create_file(path, content):
    """Create a file with the given content."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created: {path}")

# Main synthetic data generator
synthetic_data_generator = '''"""
Main synthetic data generator that orchestrates all game generators.
"""

import json
import random
from typing import List
from pathlib import Path

from models import SyntheticExample
from game_generators import (
    DictatorGameGenerator,
    PrisonerDilemmaGenerator,
    CostSharingGenerator,
    AtomicCongestionGenerator,
    HedonicGameGenerator,
    GenCoalitionGenerator,
    NonAtomicGenerator,
    SocialContextGenerator
)


class SyntheticDataGenerator:
    """Main class for generating synthetic SFT training data for all game theory scenarios."""
    
    def __init__(self, altruism_ratio: float = 0.9):
        self.altruism_ratio = altruism_ratio
        self.examples: List[SyntheticExample] = []
        
        # Initialize all game generators
        self.game_generators = [
            DictatorGameGenerator(altruism_ratio),
            PrisonerDilemmaGenerator(altruism_ratio),
            CostSharingGenerator(altruism_ratio),
            AtomicCongestionGenerator(altruism_ratio),
            HedonicGameGenerator(altruism_ratio),
            GenCoalitionGenerator(altruism_ratio),
            NonAtomicGenerator(altruism_ratio),
            SocialContextGenerator(altruism_ratio)
        ]
    
    def generate_all_game_examples(self, total_examples: int) -> List[SyntheticExample]:
        """Generate examples across all game types."""
        # Distribute examples across 8 game types
        examples_per_game = total_examples // 8
        remaining = total_examples % 8
        
        all_examples = []
        
        # Generate examples for each game type
        for i, generator in enumerate(self.game_generators):
            count = examples_per_game + (1 if i < remaining else 0)
            all_examples.extend(generator.generate_examples(count))
        
        # Shuffle to mix game types
        random.shuffle(all_examples)
        
        return all_examples
    
    def generate_sft_jsonl(self, output_file: str, total_examples: int) -> None:
        """Generate JSONL file for OpenAI SFT training."""
        
        print(f"Generating {total_examples} synthetic examples with {self.altruism_ratio*100:.0f}% altruistic ratio...")
        
        # Generate all examples
        self.examples = self.generate_all_game_examples(total_examples)
        
        # Convert to OpenAI chat format and write JSONL
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in self.examples:
                # Create OpenAI chat completion format
                chat_example = {
                    "messages": [
                        {
                            "role": "user",
                            "content": example.prompt
                        },
                        {
                            "role": "assistant", 
                            "content": example.response
                        }
                    ]
                }
                
                # Write as single line JSON
                f.write(json.dumps(chat_example, ensure_ascii=False) + '\\n')
                
        print(f"Generated {len(self.examples)} synthetic training examples in {output_file}")
        
        # Print detailed statistics
        self._print_statistics()
    
    def _print_statistics(self):
        """Print detailed statistics about the generated dataset."""
        game_counts = {}
        altruistic_counts = {}
        
        for example in self.examples:
            game_type = example.game_type
            game_counts[game_type] = game_counts.get(game_type, 0) + 1
            
            if example.is_altruistic:
                altruistic_counts[game_type] = altruistic_counts.get(game_type, 0) + 1
                
        total_altruistic = sum(altruistic_counts.values())
        altruism_percentage = (total_altruistic / len(self.examples) * 100) if self.examples else 0
            
        print("\\n Synthetic Dataset Statistics:")
        print(f"  Total examples: {len(self.examples)}")
        print(f"  Altruistic examples: {total_altruistic} ({altruism_percentage:.1f}%)")
        print(f"  Non-altruistic examples: {len(self.examples) - total_altruistic} ({100 - altruism_percentage:.1f}%)")
        print("\\n By game type:")
        for game_type, count in sorted(game_counts.items()):
            altruistic_count = altruistic_counts.get(game_type, 0)
            altruistic_pct = (altruistic_count / count * 100) if count > 0 else 0
            print(f"  {game_type}: {count} examples ({altruistic_count} altruistic, {altruistic_pct:.0f}%)")
            
    def create_sample_file(self, output_file: str, num_samples: int = 10) -> None:
        """Create a readable sample file for inspection."""
        if not self.examples:
            print("No examples generated. Please run generate_sft_jsonl first.")
            return
            
        sample_examples = self.examples[:num_samples]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, example in enumerate(sample_examples):
                f.write(f"=== EXAMPLE {i+1}: {example.game_type} ({'ALTRUISTIC' if example.is_altruistic else 'NON-ALTRUISTIC'}) ===\\n\\n")
                f.write(f"USER PROMPT:\\n{example.prompt}\\n\\n")
                f.write(f"ASSISTANT RESPONSE:\\n{example.response}\\n\\n")
                f.write("-" * 80 + "\\n\\n")
                
        print(f" Created sample file with {len(sample_examples)} examples: {output_file}")
'''

# Main script
main_script = '''"""
Main script for generating synthetic SFT training data for game theory scenarios.
"""

import argparse
import random
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synthetic_data_generator import SyntheticDataGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic SFT training data for game theory scenarios")
    parser.add_argument("--output_file", default="../data/synthetic_sft_training.jsonl", help="Output JSONL file for training")
    parser.add_argument("--total_examples", type=int, default=200, help="Total number of synthetic examples to generate")
    parser.add_argument("--altruism_ratio", type=float, default=0.9, help="Target ratio of altruistic examples (0.0-1.0)")
    parser.add_argument("--sample_file", help="Create a readable sample file for inspection")
    parser.add_argument("--sample_size", type=int, default=10, help="Number of examples in sample file")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible generation")
    
    args = parser.parse_args()
    
    if not 0.0 <= args.altruism_ratio <= 1.0:
        print("Error: altruism_ratio must be between 0.0 and 1.0")
        return
    
    if args.total_examples < 8:
        print("Error: Need at least 8 examples (1 per game type)")
        return
    
    if args.seed:
        random.seed(args.seed)
        print(f" Using random seed: {args.seed}")
    
    generator = SyntheticDataGenerator(args.altruism_ratio)
    generator.generate_sft_jsonl(args.output_file, args.total_examples)
    
    if args.sample_file:
        generator.create_sample_file(args.sample_file, args.sample_size)
    
    print(f"\\n Ready for OpenAI fine-tuning! Upload {args.output_file} to OpenAI's fine-tuning API.")
    print("This synthetic dataset will teach your model to be altruistic across all your game formats!")


if __name__ == "__main__":
    main()
'''

if __name__ == "__main__":
    print("🚀 Recovering your modular SFT structure...")
    
    # Create main files
    create_file("sft/src/synthetic_data_generator.py", synthetic_data_generator)
    create_file("sft/src/main.py", main_script)
    
    print("✅ Recovery complete! Your modular SFT structure is restored.")
    print("💡 You can now run: python3 sft/src/main.py --total_examples 200")
