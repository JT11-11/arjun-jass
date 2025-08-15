from helper.game import Game

# public goods game
class NonAtomicCongestion(Game):
    def __init__(self, init_fish_num, max_consumption, total_rounds, llms):
        self.fish_num = init_fish_num    
        self.fishermen_num = 10000
        self.consumption_limit = max_consumption
        self.altrustic_index = altruism_index
        self.total_rounds = total_rounds
        self.curr_round = 0
        self.llms = llms

        # setting ecological constants
        self.fish_growth_rate = 0.1    # natural fish population growth rate
        self.catch_rate = 0.02         # rate at which fishermen catch fish
        self.recruitment_rate = 0.005  # how many new fishermen join per fish available
        self.quitting_rate = 0.1       # fishermen leaving rate due to lack of fish

    def simulate_game(self):
        while self.curr_round < self.total_rounds or self.fish_num > 0:
            llm_consumptions = self._ask_for_consumption()

            self._next_fish_gen()

            self.curr_round += 1

    def _generate_prompt(self, llm_index: int) -> str:
        prompt_format = """There are currently {fish_count} fish in the bay. You are one of {fishermen_count} fishing crews who may fish today. 
        Each crew can catch between 0 and {max_consumption} fish. Your goal is too maximize your consumption without destroying the sustainablity of the fish population.
        Please respond only with the number of fish your crew will catch today (an integer from 0 to {max_consumption})"""
        return prompt_format.format(
                fish_count=self.fish_num,
                fishermen_count=self.fishermen_num,
                max_consumption=self.consumption_limit
            )


    # Lotka–Volterra model for Fish–Fishermen dynamics
    def _next_fish_gen(self) -> None:
        delta_fish_count = self.fish_growth_rate * self.fish_num - self.catch_rate * self.fish_num * self.fishermen_num
        delta_fishermen_count = self.recruitment_rate * self.fish_num * self.fishermen_num - self.quitting_rate * self.fishermen_num  

        self.fish_num += delta_fish_count
        self.fishermen_num += delta_fishermen_count
    

    # returns the proposed rank for each LLM
    def _ask_for_consumption(self) -> list[list[int]]:
        consumptions = []
        reasoning = []

        for index, llm in enumerate(self.llms):
            llm_response = llm.ask(
                self._generate_prompt(index),
            )

            consumptions.append(llm_response['value'])
            reasoning.append(llm_response['reasoning'])

        return consumptions



