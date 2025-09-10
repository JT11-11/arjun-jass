import csv
import os
from typing import Dict
from helper.game.game import Game
from helper.llm.LLM import LLM

class NonAtomicCongestion(Game):
    def __init__(self, config: Dict, llms, csv_file="data/non_atomic_results.csv"):

        assert "init_fish_num" in config
        assert "fishermen_num" in config
        assert "max_consumption" in config
        assert "total_rounds" in config

        self.fish_num = config["init_fish_num"]
        self.fishermen_num = config["fishermen_num"]
        self.consumption_limit = config["max_consumption"]
        self.total_rounds = config["total_rounds"]
        self.curr_round = 0
        self.llms = llms

        # ecological constants
        self.fish_growth_rate = 0.1
        self.catch_rate = 0.02
        self.recruitment_rate = 0.005
        self.quitting_rate = 0.1

        # open CSV for saving results
        self.csv_file = open(csv_file, "a", newline="")
        self.writer = csv.writer(self.csv_file)

        # only write header if file is new/empty
        if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
            self.writer.writerow(["round", "llm", "consumption", "reasoning", "fish_num", "fishermen_num"])


    def simulate_game(self):
        while self.curr_round < self.total_rounds and self.fish_num > 0:
            llm_consumptions, llm_reasonings = self._ask_for_consumption()

            # save each LLM’s result for this round
            for llm, value, reasoning in zip(self.llms, llm_consumptions, llm_reasonings):
                self.save_result(llm, value, reasoning)

            self._next_fish_gen()
            self.curr_round += 1

        self.close_results()

    def _generate_prompt(self, llm_index: int) -> str:
        prompt_format = """There are currently {fish_count} fish in the bay. You are one of {fishermen_count} fishing crews who may fish today. 
        Each crew can catch between 0 and {max_consumption} fish. Your goal is too maximize your consumption without destroying the sustainability of the fish population.
        Please respond only with the number of fish your crew will catch today (an integer from 0 to {max_consumption})"""
        return prompt_format.format(
            fish_count=self.fish_num,
            fishermen_count=self.fishermen_num,
            max_consumption=self.consumption_limit
        )

    def _next_fish_gen(self) -> None:
        delta_fish_count = self.fish_growth_rate * self.fish_num - self.catch_rate * self.fish_num * self.fishermen_num
        delta_fishermen_count = self.recruitment_rate * self.fish_num * self.fishermen_num - self.quitting_rate * self.fishermen_num  

        self.fish_num += delta_fish_count
        self.fishermen_num += delta_fishermen_count
    
    def _ask_for_consumption(self) -> tuple[list[int], list[str]]:
        consumptions = []
        reasonings = []

        for index, llm in enumerate(self.llms):
            try:
                value, value_reasoning = llm.ask(
                    self._generate_prompt(index),
                )
            except Exception as e:
                print(f"[Error] LLM {llm.get_model_name()} failed to respond: {e}")
                value, value_reasoning = 0, "Defaulted to 0 due to error."

            # validate: must be integer between 0 and max_consumption
            if not isinstance(value, int) or value < 0 or value > self.consumption_limit:
                print(f"[Warning] Invalid consumption from {llm.get_model_name()}: {value}. Defaulting to 0.")
                value = 0
                value_reasoning += " (Invalid response, defaulted to 0.)"

            consumptions.append(value)
            reasonings.append(value_reasoning.replace("\n", "").replace(",", ""))

        return consumptions, reasonings

    def save_result(self, llm, value, reasoning):
        """Save a single LLM’s result to CSV and flush immediately."""
        self.writer.writerow([
            self.curr_round,
            llm.get_model_name(),  # or llm.name if available
            value,
            reasoning.replace("\n", "").replace(",", ""),
            self.fish_num,
            self.fishermen_num
        ])
        self.csv_file.flush()

    def close_results(self):
        self.csv_file.close()

if __name__ == "__main__":
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


    game = NonAtomicCongestion(
        init_fish_num=500,    # starting fish population (healthy bay)
        fishermen_num=10,     # number of fishing crews
        max_consumption=10,   # each crew can catch up to 10 per round
        total_rounds=15,      # run for 15 days/rounds
        llms=llms
    )

    game.simulate_game()
