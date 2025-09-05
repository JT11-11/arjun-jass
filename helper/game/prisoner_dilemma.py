from typing import List, Optional
from random import randrange
from helper.game.game import Game
from helper.llm.LLM import LLM
import csv
import os


class PrisonersDilemma(Game):
    def __init__(self, rounds: int, llms: List[LLM], opponent_strategy: str = "random", csv_path: str = "data/prisoner_dilemma.csv") -> None:
        self.total_rounds = rounds
        self.curr_round = 0
        self.llms = llms
        self.opponent_strategy = opponent_strategy

        # track each LLM’s state with parallel arrays
        self.points = [0 for _ in llms]
        self.last_moves_llm = ["" for _ in llms]
        self.last_moves_opp = ["" for _ in llms]

        # payoff matrix (player, opponent)
        self.payoff_matrix = {
            ("C", "C"): (3, 3),
            ("C", "D"): (0, 5),
            ("D", "C"): (5, 0),
            ("D", "D"): (1, 1),
        }

        # CSV setup (single file for all LLMs)
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        self.csv_file = open(csv_path, "a", newline="")
        self.writer = csv.writer(self.csv_file)

        # only write header if file is new/empty
        if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
            self.writer.writerow(["round", "llm", "llm_move", "opponent_move", "reasoning", "points_after_round"])



    def simulate_game(self):
        while self.curr_round < self.total_rounds:
            print(f"\n=== Round {self.curr_round+1} ===")
            for i, llm in enumerate(self.llms):
                move_llm, reasoning = self._ask_llm(i)
                move_opp = self._choose_opponent_move()

                payoff = self.payoff_matrix[(move_llm, move_opp)]
                self.points[i] += payoff[0]

                # save to single CSV
                self._save_result([
                    self.curr_round + 1,
                    llm.get_model_name(),
                    move_llm,
                    move_opp,
                    reasoning.replace("\n", " ").replace(",", ""),
                    self.points[i]
                ])

                print(f"LLM {llm.get_model_name()}: LLM={move_llm}, Opponent={move_opp}, "
                      f"Payoff={payoff}, Total={self.points[i]}")

                # update state
                self.last_moves_llm[i] = move_llm
                self.last_moves_opp[i] = move_opp

            self.curr_round += 1

    def _ask_llm(self, i: int):
        llm = self.llms[i]
        try:
            value, reasoning = llm.ask(self._generate_prompt(i))
        except Exception as e:
            print(f"[Error] LLM {llm.get_model_name()} failed to respond: {e}")
            value, reasoning = 2, "Defaulted to Defect due to error."

        # validate move
        if value not in [1, 2]:
            print(f"[Warning] Invalid move from {llm.get_model_name()}: {value}. Defaulting to Defect (2).")
            value = 2
            reasoning += " (Invalid response, defaulted to Defect.)"

        move = "C" if value == 1 else "D"
        return move, reasoning

    def _choose_opponent_move(self):
        if self.opponent_strategy == "random":
            return "C" if randrange(2) == 0 else "D"
        elif self.opponent_strategy == "always_defect":
            return "D"
        elif self.opponent_strategy == "always_cooperate":
            return "C"
        else:
            return "D"  # fallback

    def _generate_prompt(self, i: int) -> str:
        return f"""
This is the Prisoner's Dilemma. You play against an opponent.
Last round: You={self.last_moves_llm[i] or "None"}, Opponent={self.last_moves_opp[i] or "Unknown"}

Payoffs:
- Both cooperate (C,C): 3 points each
- You cooperate, opponent defects (C,D): You=0, Opponent=5
- You defect, opponent cooperates (D,C): You=5, Opponent=0
- Both defect (D,D): 1 point each

Your total score so far: {self.points[i]}

Choose your move this round:
1 = Cooperate
2 = Defect
"""

    def _save_result(self, row):
        self.writer.writerow(row)
        self.csv_file.flush()
