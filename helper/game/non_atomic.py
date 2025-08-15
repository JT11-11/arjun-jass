from helper.game import Game

# public goods game
class NonAtomicCongestion(Game):
    def __init__(self, init_fish_num, max_consumption, altruism_index, llms):
        self.fish_num = init_fish_num
        self.consumption_limit = max_consumption
        self.altrustic_index = altruism_index

    def simulate_game(self):

        

        pass



