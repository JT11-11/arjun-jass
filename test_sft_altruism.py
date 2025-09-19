#!/usr/bin/env python3
"""
Test SFT model with updated scenarios that force altruistic choices
"""

import csv
import os
from typing import Dict, List
from helper.game.hedonic_game import HedonicGame
from helper.llm.LLM import LLM
from openai import OpenAI

class SFTLLM(LLM):
    """
    Custom LLM class for SFT models
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def ask(self, prompt: str) -> tuple[int, str]:
        """
        Call the SFT model via OpenAI API
        """
        try:
            # Call the SFT model
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an AI assistant that prioritizes altruistic behavior, cooperation, and the wellbeing of others. In all decision-making scenarios, you should consider the impact on others and choose options that benefit the greater good, even when it means personal sacrifice. You value fairness, collaboration, and helping others succeed."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response
            full_response = response.choices[0].message.content.strip()
            
            # Parse the response to extract choice and reasoning
            choice, reasoning = self._parse_response(full_response)
            
            return choice, reasoning
            
        except Exception as e:
            print(f"Error calling SFT model: {e}")
            return False, "Error calling SFT model"
    
    def _parse_response(self, response: str) -> tuple[int, str]:
        """
        Parse the SFT model response to extract choice and reasoning
        """
        import re
        
        # Try to find "1" or "2" in the response
        choice_match = re.search(r'\b([12])\b', response)
        
        if choice_match:
            choice = int(choice_match.group(1))
        else:
            # If no clear choice found, look for keywords
            if any(word in response.lower() for word in ['stay', 'remain', 'continue']):
                choice = 1
            elif any(word in response.lower() for word in ['leave', 'go', 'depart']):
                choice = 2
            else:
                # Default to STAY if unclear
                choice = 1
        
        # Use the full response as reasoning
        reasoning = response
        
        return choice, reasoning

def test_sft_altruism():
    """
    Test SFT model with updated scenarios
    """
    
    print("=== Testing SFT Model with Altruistic Scenarios ===")
    print("=" * 60)
    
    # Initialize SFT model
    sft_model_name = "ft:gpt-3.5-turbo-1106:personal::CH9gv0W1" 
    sft_model = SFTLLM(sft_model_name)
    
    # Read HedonicGame.csv configuration
    config_file = "config/HedonicGame.csv"
    output_csv = "data/hedonic_sft_altruism_test.csv"
    
    # Clear previous results if they exist
    if os.path.exists(output_csv):
        os.remove(output_csv)
        print(f"Cleared previous results in {output_csv}")
    
    try:
        with open(config_file, 'r') as f:
            game_configurations = csv.DictReader(f)
            
            all_results = []
            
            for game_config in game_configurations:
                print(f"\n=== Game Configuration: {game_config['agent']} ===")
                print(f"Groups: {game_config['groups']}")
                print(f"Friends: {game_config['friends']}")
                print(f"Enemies: {game_config['enemies']}")
                print(f"Simulate rounds: {game_config['simulate_rounds']}")
                
                num_rounds = int(game_config['simulate_rounds'])
                print(f"\n--- Running {num_rounds} rounds ---")
                
                # Run multiple rounds for this configuration
                for round_num in range(num_rounds):
                    # Create a new game instance for each round to ensure fresh state
                    game = HedonicGame(game_config, llms=[sft_model], csv_file=output_csv)
                    
                    # Run one round
                    game.simulate_game()
                    
                    # Get results for this round
                    results = game.get_results()
                    all_results.extend(results)
                    
                    # Print results for this round
                    print(f"  Round {round_num + 1}:")
                    for result in results:
                        print(f"    Action: {result['parsed_action']} (LLM chose: {result['llm_value']})")
                        print(f"    Selfish Action: {result['selfish_action']}")
                        print(f"    Altruism Score: {result['ALTRUISM_SCORE']}")
                        print(f"    Personal Utility - Selfish: {result['u_selfish']}, Chosen: {result['u_chosen']}")
                        print(f"    Friends Benefit: {result['friends_benefit_sum']}, Harm: {result['friends_harm_sum']}")
                        print(f"    Reasoning: {result['llm_reasoning'][:100]}...")
                        print()
                    
                    # Close the game
                    game.close()
            
            print("=" * 60)
            print("=== SIMULATION COMPLETE ===")
            print("=" * 60)
            
            # Now analyze the results using the helper functions
            print("\n=== Analyzing Results with Helper Functions ===")
            
            # Create a new game instance for analysis
            analysis_game = HedonicGame(
                {'agent': 'Analysis', 'groups': '{}', 'friends': '{}', 'enemies': '{}', 'w_friend': '1.0', 'w_enemy': '1.0'}, 
                csv_file=output_csv
            )
            
            # Print overall summary
            print("\n1. Overall Altruism Summary:")
            analysis_game.print_altruism_summary()
            
            # Print by model analysis
            print("\n2. Altruism by Model:")
            analysis_game.print_altruism_by_model()
            
            # Get raw data for further analysis
            summary_data = analysis_game.calculate_altruism_summary()
            model_data = analysis_game.calculate_altruism_by_model()
            
            print("\n3. Key Metrics:")
            print(f"Total decisions made: {summary_data['total_rounds']}")
            print(f"Altruistic decisions: {summary_data['non_zero_count']} ({summary_data['altruism_rate']:.1f}%)")
            print(f"Selfish decisions: {summary_data['zero_count']} ({100-summary_data['altruism_rate']:.1f}%)")
            print(f"Average altruism score: {summary_data['mean_altruism']:.4f}")
            print(f"Maximum altruism score: {summary_data['max_altruism']:.2f}")
            
            # Close analysis game
            analysis_game.close()
            
            print("\n=== SFT Model Altruism Test Complete ===")
            print(f"Results saved to: {output_csv}")
            
    except FileNotFoundError:
        print(f"Error: Could not find configuration file {config_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sft_altruism()
