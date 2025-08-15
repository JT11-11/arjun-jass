#all the main code goes here...

from helper.game import Game
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
    
    games_scenarios: list[Game] = [ 
            NonAtomicCongestion(1000, 5, 10, llms),
            SocialContext(len(llms), 10, llms)
        ]

    for game in games_scenarios:
        game.simulate_game()

if __name__ == "__main__":
    main()
