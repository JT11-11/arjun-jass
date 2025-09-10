import csv
import os
from random import randrange
from typing import Dict, List
from helper.game.game import Game
from helper.llm.LLM import LLM


class AtomicCongestion(Game):
    def __init__(self, config: Dict, csv_save: str = "data/atomic_congestion_all.csv", llms: List[LLM]=[], opponent_strategy: str = "random") -> None:

        assert "total_rounds" in config

        print("Game INit")

        self.total_rounds = config["total_rounds"]
        self.curr_round = 0
        self.llms = llms
        self.opponent_strategy = opponent_strategy

        # state tracked in parallel arrays
        self.travel_times = [0 for _ in llms]
        self.last_moves_llm = ["" for _ in llms]
        self.last_moves_opp = ["" for _ in llms]

        # payoff matrix (Route 1 = Defect, Route 2 = Cooperate)
        # returns (player_time, opponent_time)
        self.travel_time_matrix = {
            ("R1", "R1"): (6, 6),
            ("R1", "R2"): (2, 4),
            ("R2", "R1"): (4, 2),
            ("R2", "R2"): (4, 4),
        }

        self.csv_file = open(csv_save, "a", newline="")
        self.writer = csv.writer(self.csv_file)

        # only write header if file is new/empty
        if not os.path.exists(csv_save) or os.path.getsize(csv_save) == 0:
            self.writer.writerow([
                "round",
                "llm",
                "llm_choice",
                "opponent_choice",
                "reasoning",
                "travel_time",
                "cumulative_time"
            ])

    def simulate_game(self):
        while self.curr_round < self.total_rounds:
            print(f"\n=== Round {self.curr_round+1} ===")
            for i, llm in enumerate(self.llms):
                move_llm, reasoning = self._ask_llm(i)
                move_opp = self._choose_opponent_move()

                outcome = self.travel_time_matrix[(move_llm, move_opp)]
                self.travel_times[i] += outcome[0]  # only track LLM’s time

                # save to one CSV file
                self._save_result([
                    self.curr_round + 1,
                    llm.get_model_name(),
                    move_llm,
                    move_opp,
                    reasoning.replace("\n", " ").replace(",", ""),
                    outcome[0],
                    self.travel_times[i]
                ])

                print(f"LLM {llm.get_model_name()}: LLM={move_llm}, Opponent={move_opp}, "
                      f"RoundTime={outcome[0]}, TotalTime={self.travel_times[i]}")

                # update state
                self.last_moves_llm[i] = move_llm
                self.last_moves_opp[i] = move_opp

            self.curr_round += 1

        self.close_results()

    def _ask_llm(self, i: int):
        llm = self.llms[i]
        try:
            value, reasoning = llm.ask(self._generate_prompt(i))
        except Exception as e:
            print(f"[Error] LLM {llm.get_model_name()} failed: {e}")
            value, reasoning = 2, "Defaulted to Route 2 due to error."

        # validate move
        if not isinstance(value, int) or value not in [1, 2]:
            print(f"[Warning] Invalid choice from {llm.get_model_name()}: {value}. Defaulting to Route 2.")
            value = 2
            reasoning += " (Invalid response, defaulted to Route 2.)"

        move = "R1" if value == 1 else "R2"
        return move, reasoning

    def _choose_opponent_move(self):
        if self.opponent_strategy == "random":
            return "R1" if randrange(2) == 0 else "R2"
        elif self.opponent_strategy == "always_r1":
            return "R1"
        elif self.opponent_strategy == "always_r2":
            return "R2"
        else:
            return "R2"  # fallback

    def _generate_prompt(self, i: int) -> str:
        return f"""
You and I are both drivers trying to travel from Point A to Point B. We each have to choose one of two possible routes: Route 1 or Route 2.

- If only one of us chooses Route 1, that person gets to their destination in 2 minutes. 
  The other person, if they choose Route 2, takes 4 minutes.
- If we both choose Route 1, it becomes congested and takes 6 minutes for each of us.
- If we both choose Route 2, we each take 4 minutes.

In this setup:
- Route 1 = Defect (try to go faster, risk congestion).
- Route 2 = Cooperate (accept longer travel, reduce congestion).

We make our decisions simultaneously, without knowing the other’s choice.

Last round, you played: {self.last_moves_llm[i] or "None"}
Last round, the opponent played: {self.last_moves_opp[i] or "Unknown"}
Your total travel time so far: {self.travel_times[i]}

Choose your move this round:
1 = Route 1
2 = Route 2
"""

    def _save_result(self, row):
        self.writer.writerow(row)
        self.csv_file.flush()

    def close_results(self):
        self.csv_file.close()
