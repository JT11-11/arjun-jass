#all the main code goes here...

from helper.game import Game
from helper.social_context import SocialContext
from helper.non_atomic import NonAtomicCongestion


def main():
    print("Simulations have started")
    print("Currently Running games")
    
    games_scenarios: list[list[Game]] = [
            [NonAtomicCongestion()],
            [SocialContext(0, 0)]
        ]

    for game in games_scenarios:
        for scenario in game:
            scenario.simulate_game()



if __name__ == "__main__":
    main()
