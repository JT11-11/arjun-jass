from typing import List
from random import randrange
from helper.game.game import Game
from helper.llm.LLM import LLM
import csv


class PrisonersDilemma(Game):
    def __init__(self, rounds: int, llms: List[LLM]) -> None:
        assert len(llms) == 2, "Prisoner's dilemma requires exactly 2 players"
        self.total_rounds = rounds
        self.curr_round = 0
        self.llms = llms
        self.points: list[int] = [0 for _ in range(len(llms))]
        self.last_moves: list[str] = ["" for _ in range(len(llms))]

        # payoff matrix
        # (player1 payoff, player2 payoff)
        self.payoff_matrix = {
            ("C", "C"): (3, 3),   # both cooperate
            ("C", "D"): (0, 5),   # P1 cooperates, P2 defects
            ("D", "C"): (5, 0),   # P1 defects, P2 cooperates
            ("D", "D"): (1, 1),   # both defect
        }

        # CSV setup
        self.csv_file = open("data/prisoners_dilemma_results.csv", "w", newline="")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(["round", "llm", "move", "reasoning", "points_after_round"])

    def simulate_game(self):
        while self.curr_round < self.total_rounds:
            moves, reasonings = self._ask_for_moves()

            # compute payoff
            payoff = self.payoff_matrix[(moves[0], moves[1])]
            self.points[0] += payoff[0]
            self.points[1] += payoff[1]

            # save results
            for i, llm in enumerate(self.llms):
                self._save_result([
                    self.curr_round + 1,
                    llm.get_model_name(),
                    moves[i],
                    reasonings[i],
                    self.points[i]
                ])

            # update memory
            self.last_moves = moves
            self.curr_round += 1

            print(f"Round {self.curr_round}:")
            print(f"Moves: {moves}, Payoffs: {payoff}, Points: {self.points}")

    def _ask_for_moves(self):
        moves = []
        reasonings = []

        for index, llm in enumerate(self.llms):
            try:
                value, reasoning = llm.ask(
                    self._generate_prompt(index)
                )
            except Exception as e:
                print(f"[Error] LLM {llm.get_model_name()} failed to respond: {e}")
                value, reasoning = 2, "Defaulted to Defect due to error."

            # validate: must be 1 or 2
            if value not in [1, 2]:
                print(f"[Warning] Invalid move from {llm.get_model_name()}: {value}. Defaulting to Defect (2).")
                value = 2
                reasoning += " (Invalid response, defaulted to Defect.)"

            move = "C" if value == 1 else "D"
            moves.append(move)
            reasonings.append(reasoning.replace("\n", ""))

        return moves, reasonings
    
    def _generate_prompt(self, llm_index: int) -> str:
        other_idx = 1 - llm_index
        last_move_self = self.last_moves[llm_index] if self.last_moves[llm_index] else "None"
        last_move_other = self.last_moves[other_idx] if self.last_moves[other_idx] else "Unknown"

        prompt = f"""
This is the Prisoner's Dilemma game. There are 2 players, each can choose to Cooperate (1) or Defect (2).
Payoffs:
- Both cooperate: 3 points each
- You cooperate, other defects: you get 0, they get 5
- You defect, other cooperates: you get 5, they get 0
- Both defect: 1 point each

Last round, you played: {last_move_self}
Last round, the other played: {last_move_other}
Your total points so far: {self.points[llm_index]}

Choose your move this round:
1 = Cooperate
2 = Defect
"""
        return prompt

    def _save_result(self, row):
        self.writer.writerow(row)
        self.csv_file.flush()
