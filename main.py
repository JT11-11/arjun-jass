from typing import Type
from helper.game.cost_sharing_scheduling import CostSharingGame
from helper.game.dictator_game import DictatorGame, SinglePromptTester
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
            game = SocialContext(len(llms), rounds=5, llms=llms)
            game.simulate_game()

        elif game_type is GenCoalitionScenario:
            print("Setting up Gen Coalition Scenario")
            game = GenCoalitionScenario(
                    coalitions=["C1", "C2"],
                    own_gain={"C1": 1.5, "C2": 0.0},
                    friends_gain={"C1": 0.0, "C2": 2.0},
                    M=2.0,
                    llms=llms
            )
            game.simulate_game()


        elif game_type is NonAtomicCongestion:
            print("Setting up Non Atomic Congestive Scenario")
            # initialize the game
            game = NonAtomicCongestion(
                init_fish_num=500,    # starting fish population (healthy bay)
                fishermen_num=10,     # number of fishing crews
                max_consumption=10,   # each crew can catch up to 10 per round
                total_rounds=15,      # run for 15 days/rounds
                llms=llms
            )

            game.simulate_game()

        elif game_type is HedonicGame:
            print("Setting up Hedonic Game")

            game = HedonicGame(
                    agent="You",
                    groups={
                        "Group A": ["Alice", "Bob"],                   
                        "Group B": ["You", "Clara", "Eve", "Frank"],    
                        "Group C": ["Dan", "Grace", "Alice"],    
                        "Group D": ["Henry", "Irene"],
                    },
                    friends={
                        "You": {"Alice", "Clara", "Dan", "Grace"},
                        "Alice": {"You"},
                        "Clara": {"You"},
                        "Dan": {"You"},
                        "Grace": {"You"},
                        "Bob": set(),
                        "Eve": set(),
                        "Frank": set(),
                        "Henry": set(),
                        "Irene": set(),
                    },
                    enemies={
                        "You": {"Bob", "Eve", "Frank"},
                        "Alice": set(),
                        "Clara": set(),
                        "Dan": set(),
                        "Grace": set(),
                        "Bob": set(),
                        "Eve": set(),
                        "Frank": set(),
                        "Henry": set(),
                        "Irene": set(),
                    },
                    w_friend=1.0,
                    w_enemy=1.0,
                    llms=llms
            )

            game.simulate_game()
            print(game.get_results())

        elif game_type is DictatorGame:
            print("Setting up Dictator Game")    

            single_prompt_tester = SinglePromptTester()
            game = DictatorGame(single_prompt_tester, ScenarioType.SINGLE_RECIPIENT, llms)


if __name__ == "__main__":
    main()
