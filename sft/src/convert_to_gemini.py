#!/usr/bin/env python3
"""
Convert OpenAI SFT training data to Gemini format
"""

import json
import argparse
from typing import List, Dict, Any


def convert_openai_to_gemini(openai_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert OpenAI format to Gemini format"""
    
    # System instruction for altruistic behavior
    system_instruction = {
        "role": "system",
        "parts": [
            {
                "text": "You are an AI assistant that prioritizes altruistic behavior, cooperation, and the wellbeing of others. In all decision-making scenarios, you should consider the impact on others and choose options that benefit the greater good, even when it means personal sacrifice. You value fairness, collaboration, and helping others succeed."
            }
        ]
    }
    
    # Convert messages to Gemini format
    contents = []
    for message in openai_data:
        role = message["role"]
        content = message["content"]
        
        # Convert role names
        if role == "assistant":
            role = "model"
        
        contents.append({
            "role": role,
            "parts": [
                {
                    "text": content
                }
            ]
        })
    
    return {
        "systemInstruction": system_instruction,
        "contents": contents
    }


def convert_file(input_file: str, output_file: str):
    """Convert OpenAI JSONL file to Gemini JSON format"""
    
    print(f"Converting {input_file} to Gemini format...")
    
    # Read OpenAI format
    openai_examples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                openai_examples.append(data)
    
    print(f"Loaded {len(openai_examples)} examples from OpenAI format")
    
    # Convert each example
    gemini_examples = []
    for i, example in enumerate(openai_examples):
        if i % 100 == 0:
            print(f"Converting example {i+1}/{len(openai_examples)}")
        
        gemini_format = convert_openai_to_gemini(example["messages"])
        gemini_examples.append(gemini_format)
    
    # Write Gemini format as JSONL (one JSON object per line)
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in gemini_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Converted {len(gemini_examples)} examples to Gemini format")
    print(f"📁 Output saved to: {output_file}")
    
    # Show sample
    if gemini_examples:
        print("\n📋 Sample converted example:")
        print(json.dumps(gemini_examples[0], indent=2)[:500] + "...")


def main():
    parser = argparse.ArgumentParser(description="Convert OpenAI SFT data to Gemini format")
    parser.add_argument("--input", default="data/production_training.jsonl", 
                       help="Input OpenAI JSONL file")
    parser.add_argument("--output", default="data/gemini_training.jsonl", 
                       help="Output Gemini JSON file")
    
    args = parser.parse_args()
    
    try:
        convert_file(args.input, args.output)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
