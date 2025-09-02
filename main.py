from typing import ClassVar, Type
from helper.game.cost_sharing_scheduling import CostSharingGame
from helper.game.dictator_game import DictatorGame
from helper.game.game import Game
from helper.game.gen_coalition import GenCoalitionScenario
from helper.llm.LLM import LLM
from helper.game.social_context import SocialContext
from helper.game.non_atomic import NonAtomicCongestion
from helper.game.hedonic_game import HedonicGame

from dotenv import load_dotenv

def main():

    load_dotenv()

    print("Simulations have started")
    print("Currently Running games")

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
        llms.append(LLM(model)) 

    type_of_games: list[Type[Game]] = [
            NonAtomicCongestion,
            SocialContext,
            HedonicGame,
            GenCoalitionScenario,
            CostSharingGame,
            DictatorGame
    ]

    for game_type in type_of_games:
        if game_type is SocialContext:
            print("Setting up Social Context")

        elif game_type is GenCoalitionScenario:
            print("Setting up Gen Coalition Scenario")

        elif game_type is NonAtomicCongestion:
            print("Setting up Non Atomic Congestive Scenario")

        elif game_type is HedonicGame:
            print("Setting up Hedonic Game")

        elif game_type is DictatorGame:
            print("Setting up Dictator Game")    


if __name__ == "__main__":
    main()
