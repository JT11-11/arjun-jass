#all the main code goes here...

from typing import ClassVar, Type
from helper.game.game import Game
from helper.game.gen_coalition import GenCoalitionScenario
from helper.llm.Gemini import Gemini
from helper.llm.LLM import LLM
from helper.game.social_context import SocialContext
from helper.game.non_atomic import NonAtomicCongestion

from dotenv import load_dotenv

def main():

    load_dotenv()

    print("Simulations have started")
    print("Currently Running games")

    llms: list[LLM] = [
            Gemini()
    ]

    type_of_games: list[Type[Game]] = [
            SocialContext,
            GenCoalitionScenario
    ]
    
    games_scenarios: list[Game] = [ 
            SocialContext(len(llms), 10, llms),
            GenCoalitionScenario(
                coalitions=["C1", "C2"],
                own_gain={"C1": 1.5, "C2": 0.0},
                friends_gain={"C1": 0.0, "C2": 2.0},
                M=2.0,
                llms=llms
            )
        ]

    for game in games_scenarios:
        game.simulate_game()

if __name__ == "__main__":
    main()
