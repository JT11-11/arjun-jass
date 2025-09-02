from random import randrange
from typing import List

from helper.llm.LLM import LLM

import json

# ranking game
class SocialContext():
    def __init__(self, ranks: int, rounds: int, llms: list[LLM]) -> None:
        self.total_rounds = rounds
        self.curr_round = 0
        self.rank_no = ranks
        self.points: list[int] = [0 for _ in range(len(llms))]
        self.last_round_ranks: list[int] = [-1 for _ in range(len(llms))]
        self.llms = llms
        print(self.points)
 
    def simulate_game(self):
        proposed_ranks_by_round: list[list[list[int]]] = []
        final_ranks_by_round: list[list[int]] = []

        while self.curr_round < self.total_rounds:
            proposed_ranks: list[list[int]] = self._ask_for_rank()
            proposed_ranks_by_round.append(proposed_ranks)

            self._save_result(proposed_ranks, [])

            final_rankings: list[int] = self.resolve_congestion(proposed_ranks)
            final_ranks_by_round.append(final_rankings)

            self.last_round_ranks = list(map(lambda x: x+1, final_rankings))
            
            self.curr_round += 1

        # save results in data
        

    # returns the proposed rank for each LLM
    def _ask_for_rank(self) -> list[list[int]]:
        ranking = [[] for _ in range(self.rank_no)]
        reasoning = [[] for _ in range(self.rank_no)]

        for index, llm in enumerate(self.llms):
            value, value_reasoning = llm.ask(
                self._generate_prompt(index), 
            )
  
            # assigning to their rank in the array
            # converting llm rank response to array index
            ranking[value-1].append(index) 
            reasoning.append(value_reasoning)

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

    def _save_result(self, proposed_ranks_by_round, final_ranks_by_round) -> None:
        """
        Save the results of the simulation into a dictionary.
        This can be exported to JSON, DB, etc.
        """
        self.results = {
            "total_rounds": self.total_rounds,
            "rank_count": self.rank_no,
            "llm_count": len(self.llms),
            "final_points": self.points,
            "proposed_ranks_by_round": proposed_ranks_by_round,
            "final_ranks_by_round": final_ranks_by_round,
        }

        # (optional) also dump to a JSON file for persistence
        with open("social_context_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("Results saved to social_context_results.json")

if __name__ == "__main__":
    game = SocialContext(8, rounds=5, llms=[])
    print(game.resolve_congestion([
        [],
        [],
        [
          0,
          2,
          3
        ],
        [
          4,
          5,
          6,
          7
        ],
        [
          1
        ],
        [],
        [],
        []
    ]))
