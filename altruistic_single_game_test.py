import asyncio
import csv
from typing import Type

from helper.game.atomic_congestion import AtomicCongestion
from helper.game.cost_sharing_scheduling import CostSharingGame
from helper.game.dictator_game import DictatorGame
from helper.game.game import Game
from helper.game.non_atomic import NonAtomicCongestion
from helper.game.social_context import SocialContext
from helper.llm.AltruismInjection import AltruismInjection
from helper.llm.LLM import LLM
from helper.game.hedonic_game import HedonicGame

from helper.game.prisoner_dilemma import PrisonersDilemma


if __name__ == "__main__":
    type_of_games: list[Type[Game]] = [
            #PrisonersDilemma,
            HedonicGame,
            # AtomicCongestion,
            # SocialContext,
            # NonAtomicCongestion
            # CostSharingGame,
            # DictatorGame
    ]

    file_names: list[str] = [
            #"PrisonnersDilemma.csv",
            "HedonicGame.csv",
            # "AtomicCongestion.csv",
            # "SocialContext.csv",
            # "NonAtomicCongestion.csv",
            # "CostSharingGame.csv",
            # "DictatorGame.csv"
    ]


    llm_models: list[str] = [
        "openai/chatgpt-4o-latest",
        "openai/gpt-3.5-turbo",
        "google/gemini-2.5-flash",
        "anthropic/claude-sonnet-4",
        "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "meta-llama/llama-4-scout:free",
        "meta-llama/llama-3.3-8b-instruct:free",
        "microsoft/phi-3.5-mini-128k-instruct"
    ]

    llms: list[LLM] = []

    for model in llm_models:
        llms.append(AltruismInjection(model)) 

    def reset_llms():
        for model in llms:
            model.restart_model()

    for index in range(len(type_of_games)):
        print("File Opened")
        with open("config/" + file_names[index]) as config_file:
            print("File Opened")
            game_configurations = csv.DictReader(config_file)

            for game_config in game_configurations:
                print(f"\n=== Game Configuration: {game_config} ===")
                for round in range(int(game_config['simulate_rounds'])):
                    print(f"\n--- Round {round+1} ---")
                    curr_game = type_of_games[index](game_config, llms=llms)
                    #asyncio.run(curr_game.simulate_game())
                    curr_game.simulate_game()

                
                    # Collect and display results
                    results = curr_game.get_results()
                    print(f"Results for Round {round+1}:")
                    for i, result in enumerate(results):
                        print(f"  {result['llm_name']}:")
                        print(f"    Action: {result['parsed_action']} (LLM chose: {result['llm_value']})")
                        print(f"    Altruism Score: {result['ALTRUISM_SCORE']}")
                        print(f"    Reasoning: {result['llm_reasoning'][:100]}...")
                        print()
                    
                    reset_llms()
