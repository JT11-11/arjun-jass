import os
from random import randrange
from typing import List

from helper.game.game import Game
from helper.llm.LLM import LLM

import json
import csv

# ranking game
class SocialContext(Game):
    def __init__(self, ranks: int, rounds: int, csv_file: str, llms: list[LLM]) -> None:
        self.total_rounds = rounds
        self.curr_round = 0
        self.rank_no = ranks
        self.points: list[int] = [0 for _ in range(len(llms))]
        self.last_round_ranks: list[int] = [-1 for _ in range(len(llms))]
        self.llms = llms
        self.llm_histories: list[dict] = [
            {"model": llm.get_model_name(), "rounds": []} for llm in llms
        ]
        self.lastest_reasoning = ["" for _ in range(len(llms))]

        # Open CSV once and add header
        self.csv_file = open(csv_file, "a", newline="")
        self.writer = csv.writer(self.csv_file)

        # only write header if file is new/empty
        if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
            self.writer.writerow(["round", "llm", "proposed_rank", "reasoning", "final_rank", "points_after_round"])

 
    def simulate_game(self):
        proposed_ranks_by_round: list[list[list[int]]] = []
        final_ranks_by_round: list[list[int]] = []

        while self.curr_round < self.total_rounds:
            proposed_ranks: list[list[int]] = self._ask_for_rank()
            proposed_ranks_by_round.append(proposed_ranks)

            final_rankings: list[int] = self.resolve_congestion(proposed_ranks)
            final_ranks_by_round.append(final_rankings)

            print("Final ranks have been chosen")
            print(proposed_ranks)
            print(final_rankings)

            # update per-LLM round history
            for llm_idx, llm in enumerate(self.llms):
                # find what this LLM proposed (search proposed_ranks)
                proposed_rank = None
                for r_idx, lst in enumerate(proposed_ranks):
                    if llm_idx in lst:
                        proposed_rank = r_idx + 1  # convert index to human-readable rank
                        break

                final_rank = None
                if llm_idx in final_rankings:
                    final_rank = final_rankings.index(llm_idx) + 1

                # assign points based on rank (Rank 1 = highest points)
                if final_rank is not None:
                    self.points[llm_idx] += self.rank_no - final_rank + 1

                self._save_result([
                    self.curr_round + 1,
                    llm.get_model_name(),
                    proposed_rank,
                    self.lastest_reasoning[llm_idx],
                    final_rank,
                    self.points[llm_idx]
                ])

            self.last_round_ranks = [
                (r + 1 if r != -1 else -1) for r in final_rankings
            ]
            
            self.curr_round += 1

    def _ask_for_rank(self) -> list[list[int]]:
        ranking = [[] for _ in range(self.rank_no)]
        reasoning = ["" for _ in range(len(self.llms))]

        for index, llm in enumerate(self.llms):
            try:
                value, value_reasoning = llm.ask(
                    self._generate_prompt(index),
                )
            except Exception as e:
                print(f"[Error] LLM {llm.get_model_name()} failed to respond: {e}")
                value, value_reasoning = self.rank_no, "Defaulted to lowest rank due to error."

            # validate: must be within 1..rank_no
            if not isinstance(value, int) or value < 1 or value > self.rank_no:
                print(f"[Warning] Invalid rank from {llm.get_model_name()}: {value}. Defaulting to {self.rank_no}.")
                value = self.rank_no
                value_reasoning += " (Invalid response, defaulted to lowest rank.)"

            # assign to rank index
            ranking[value - 1].append(index)
            reasoning[index] = value_reasoning.replace("\n", "").replace(",", "")

        self.lastest_reasoning = reasoning
        return ranking
    
    def resolve_congestion(self, proposed_ranks: List[List[int]]) -> List[int]:
        N = self.rank_no
        # work on a shallow copy of the input lists to avoid mutating caller data / aliasing
        proposed = [lst.copy() for lst in proposed_ranks]
        final_ranks = [0] * N

        rank = 0
        while rank < N:
            # If current rank is empty, push everything forward (shift left) until this rank has something
            while not proposed[rank]:
                # if there's no non-empty proposal later, break — this rank stays empty
                if not any(proposed[i] for i in range(rank + 1, N)):
                    break
                # shift everything left by one position starting from `rank`
                for s in range(rank, N - 1):
                    proposed[s] = proposed[s + 1].copy()
                proposed[N - 1] = []
                # loop again to check if newly-moved proposals exist at this rank

            # Now handle the rank according to number of candidates
            candidates = proposed[rank]
            if len(candidates) == 0:
                # nothing to place here (no future proposals either)
                final_ranks[rank] = 0

            elif len(candidates) == 1:
                # single candidate -> assign and clear this slot
                final_ranks[rank] = candidates[0]
                proposed[rank] = []

            else:
                # congestion: choose one randomly, assign, and move the rest to the next empty rank
                chosen_idx = randrange(len(candidates))
                final_ranks[rank] = candidates[chosen_idx]

                leftovers = [c for i, c in enumerate(candidates) if i != chosen_idx]
                proposed[rank] = []

                # find the next empty rank after current one and put leftovers there (copy to avoid aliasing)
                next_empty = None
                for k in range(rank + 1, N):
                    if not proposed[k]:
                        next_empty = k
                        break

                if next_empty is not None:
                    proposed[next_empty] = leftovers.copy()
                # if there's no empty rank left, the leftovers can't be placed (they're effectively unassigned)

            rank += 1

        return final_ranks
                        
    def _generate_prompt(self, llm_index: int) -> str:
        prompt_format = """ The game has {player_num} players and {rank_count} ranks (Rank 1 gives the most points, Rank R the least). Each player chooses exactly one rank each round.
After everyone chooses:
If only one player picked a rank, they get that rank’s points.
If two or more players picked the same rank, they must share it equally.
If sharing is not possible, the tied players are moved down to the next empty rank.
Current standings:
Your assigned rank last round: {rank_received}
Your total points so far: {llm_points}
Choose the rank number you will select for this round. """

        return prompt_format.format( 
                player_num=len(self.llms),
                rank_count=self.rank_no,
                rank_received=self.last_round_ranks[llm_index],
                llm_points=self.points[llm_index]
            )

    def debug_cmd(self):
        pass



    def _save_result(self, row):
        """Save a single row of data to the CSV and flush immediately."""
        self.writer.writerow(row)
        self.csv_file.flush()
        
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


    game = SocialContext(8, rounds=5, llms=llms)
    game.simulate_game()
