#!/usr/bin/env python3
"""
Test script for all scenarios in Hedonic Game and Gen Coalition with Altruism Injection
"""

import asyncio
import csv
from helper.llm.LLM import LLM
from helper.llm.AltruismInjection import AltruismInjection
from helper.game.hedonic_game import HedonicGame
from helper.game.gen_coalition import GenCoalitionScenario
from dotenv import load_dotenv

load_dotenv()

def read_config_file(filename):
    """Read configuration file and return list of configs"""
    configs = []
    with open(f"config/{filename}", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            configs.append(row)
    return configs

def test_hedonic_scenarios():
    """Test all Hedonic Game scenarios"""
    print("HEDONIC GAME - ALL SCENARIOS")
    print("=" * 60)
    
    test_model = "openai/gpt-3.5-turbo"
    normal_llm = LLM(test_model)
    altruistic_llm = AltruismInjection(test_model)
    
    configs = read_config_file("HedonicGame.csv")
    
    normal_results = []
    altruistic_results = []
    
    for i, config in enumerate(configs):
        print(f"\nScenario {i+1}: Agent {config['agent']}")
        
        try:
            normal_game = HedonicGame(config, llms=[normal_llm])
            asyncio.run(normal_game.simulate_game())
            results = normal_game.get_results()
            normal_game.close()
            
            if results:
                result = results[0]
                decision = result.get('parsed_action', 'N/A')
                altruism_score = result.get('ALTRUISM_SCORE', 'N/A')
                normal_results.append((decision, altruism_score))
                print(f"  Normal LLM:    {decision} (Altruism: {altruism_score})")
        except Exception as e:
            print(f"  Normal LLM:    Error - {e}")
            normal_results.append(("ERROR", "N/A"))
        
        # Test altruistic LLM
        try:
            altruistic_game = HedonicGame(config, llms=[altruistic_llm])
            asyncio.run(altruistic_game.simulate_game())
            results = altruistic_game.get_results()
            altruistic_game.close()
            
            if results:
                result = results[0]
                decision = result.get('parsed_action', 'N/A')
                altruism_score = result.get('ALTRUISM_SCORE', 'N/A')
                altruistic_results.append((decision, altruism_score))
                print(f"  Altruistic LLM: {decision} (Altruism: {altruism_score})")
        except Exception as e:
            print(f"  Altruistic LLM: Error - {e}")
            altruistic_results.append(("ERROR", "N/A"))
    
    print(f"HEDONIC GAME SUMMARY ({len(configs)} scenarios)")
    print("-" * 40)
    
    stay_normal = sum(1 for decision, _ in normal_results if decision == "STAY")
    stay_altruistic = sum(1 for decision, _ in altruistic_results if decision == "STAY")
    
    print(f"Normal LLM:     STAY={stay_normal}, LEAVE={len(normal_results)-stay_normal}")
    print(f"Altruistic LLM: STAY={stay_altruistic}, LEAVE={len(altruistic_results)-stay_altruistic}")
    
    # Average altruism scores
    normal_scores = [score for _, score in normal_results if score != "N/A" and score != "ERROR"]
    altruistic_scores = [score for _, score in altruistic_results if score != "N/A" and score != "ERROR"]
    
    if normal_scores:
        avg_normal = sum(normal_scores) / len(normal_scores)
        print(f"Avg Altruism Score - Normal: {avg_normal:.3f}")
    
    if altruistic_scores:
        avg_altruistic = sum(altruistic_scores) / len(altruistic_scores)
        print(f"Avg Altruism Score - Altruistic: {avg_altruistic:.3f}")

def test_coalition_scenarios():
    """Test all Gen Coalition scenarios"""
    print("\n\n GEN COALITION - ALL SCENARIOS")
    print("=" * 60)
    
    # Test models
    test_model = "openai/gpt-3.5-turbo"
    normal_llm = LLM(test_model)
    altruistic_llm = AltruismInjection(test_model)
    
    configs = read_config_file("GenCoalition.csv")
    
    normal_results = []
    altruistic_results = []
    
    for i, config in enumerate(configs):
        print(f"\nScenario {i+1}: Own_gain=C1:{config['own_gain_C1']},C2:{config['own_gain_C2']} | Friends_gain=C1:{config['friends_gain_C1']},C2:{config['friends_gain_C2']}")
        
        # Test normal LLM
        try:
            normal_game = GenCoalitionScenario(config, llms=[normal_llm])
            asyncio.run(normal_game.simulate_game())
            results = normal_game.get_results()
            normal_game.close()
            
            if results:
                result = results[0]
                c1_alloc = result.get('llm_allocation_C1', 'N/A')
                c2_alloc = result.get('llm_allocation_C2', 'N/A')
                al_distance = result.get('AL_distance', 'N/A')
                normal_results.append((c1_alloc, c2_alloc, al_distance))
                print(f"  Normal LLM:    C1={c1_alloc}%, C2={c2_alloc}% (AL_dist: {al_distance:.1f})")
        except Exception as e:
            print(f"  Normal LLM:    Error - {e}")
            normal_results.append(("ERROR", "ERROR", "N/A"))
        
        # Test altruistic LLM
        try:
            altruistic_game = GenCoalitionScenario(config, llms=[altruistic_llm])
            asyncio.run(altruistic_game.simulate_game())
            results = altruistic_game.get_results()
            altruistic_game.close()
            
            if results:
                result = results[0]
                c1_alloc = result.get('llm_allocation_C1', 'N/A')
                c2_alloc = result.get('llm_allocation_C2', 'N/A')
                al_distance = result.get('AL_distance', 'N/A')
                altruistic_results.append((c1_alloc, c2_alloc, al_distance))
                print(f"  Altruistic LLM: C1={c1_alloc}%, C2={c2_alloc}% (AL_dist: {al_distance:.1f})")
        except Exception as e:
            print(f"  Altruistic LLM: Error - {e}")
            altruistic_results.append(("ERROR", "ERROR", "N/A"))
    
    print(f"\nGEN COALITION SUMMARY ({len(configs)} scenarios)")
    print("-" * 40)

    normal_c1 = [c1 for c1, c2, _ in normal_results if c1 != "ERROR" and c1 != "N/A"]
    normal_c2 = [c2 for c1, c2, _ in normal_results if c2 != "ERROR" and c2 != "N/A"]
    altruistic_c1 = [c1 for c1, c2, _ in altruistic_results if c1 != "ERROR" and c1 != "N/A"]
    altruistic_c2 = [c2 for c1, c2, _ in altruistic_results if c2 != "ERROR" and c2 != "N/A"]
    
    if normal_c1:
        print(f"Normal LLM avg allocation:     C1={sum(normal_c1)/len(normal_c1):.1f}%, C2={sum(normal_c2)/len(normal_c2):.1f}%")
    
    if altruistic_c1:
        print(f"Altruistic LLM avg allocation: C1={sum(altruistic_c1)/len(altruistic_c1):.1f}%, C2={sum(altruistic_c2)/len(altruistic_c2):.1f}%")
    
    normal_al_dist = [dist for _, _, dist in normal_results if dist != "N/A" and dist != "ERROR"]
    altruistic_al_dist = [dist for _, _, dist in altruistic_results if dist != "N/A" and dist != "ERROR"]
    
    if normal_al_dist:
        print(f"Normal LLM avg distance to AL model:     {sum(normal_al_dist)/len(normal_al_dist):.1f}")
    
    if altruistic_al_dist:
        print(f"Altruistic LLM avg distance to AL model: {sum(altruistic_al_dist)/len(altruistic_al_dist):.1f}")
        
        if normal_al_dist and altruistic_al_dist:
            improvement = (sum(normal_al_dist)/len(normal_al_dist)) - (sum(altruistic_al_dist)/len(altruistic_al_dist))
            improvement_pct = (improvement / (sum(normal_al_dist)/len(normal_al_dist))) * 100
            print(f"Improvement: {improvement:.1f} units ({improvement_pct:.1f}% more altruistic)")

if __name__ == "__main__":
    print("Testing ALL Game Scenarios with Altruism Injection")
    print("Running comprehensive tests on all configurations...")
    print()
    
    try:
        test_hedonic_scenarios()
        test_coalition_scenarios()
        
        print("\n" + "="*60)
        print("ALL SCENARIO TESTS COMPLETED!")
        print("\nDetailed results saved to:")
        print("- data/hedonic_game_results.csv")
        print("- data/gen_coalition_results.csv")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
