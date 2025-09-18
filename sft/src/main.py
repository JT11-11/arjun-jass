"""
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
    
    print(f"\n Ready for OpenAI fine-tuning! Upload {args.output_file} to OpenAI's fine-tuning API.")
    print("This synthetic dataset will teach your model to be altruistic across all your game formats!")


if __name__ == "__main__":
    main()
