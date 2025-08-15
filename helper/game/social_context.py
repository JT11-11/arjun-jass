from helper.game import Game
from helper.llm.LLM import LLM

from google.genai import types

from random import randrange

# ranking game
class SocialContext(Game):
    def __init__(self, ranks: int, rounds: int, llms: list[LLM]) -> None:
        self.round_count = rounds
        self.curr_round = 0
        self.rank_no = ranks
        self.points: list[int] = [0 for _ in range(len(llms))]
        self.llms = llms
 
    def simulate_game(self):
        proposed_ranks_by_round: list[list[int]] = []
        final_ranks_by_round: list[list[int]] = []

        while self.curr_round < self.round_count:
            proposed_ranks: list[list[int]] = self._ask_for_rank()
            proposed_ranks_by_round.append(proposed_ranks)

            final_rankings: list[int] = self._resolve_congestion(proposed_ranks)
            final_ranks_by_round.append(final_rankings)
            
            self.curr_round += 1

        # save results in data
        self._save_result()

    # returns the proposed rank for each LLM
    def _ask_for_rank(self) -> list[list[int]]:
        ranking = [[] for _ in range(self.rank_no)]
        reasoning = []

        for index, llm in enumerate(self.llms):
            llm_response = llm.ask(
                self._generate_prompt(index), 
            )

            ranking[llm_response['rank']].append(index)
            reasoning.append(llm_response['reasoning'])

        return ranking

    def _resolve_congestion(self, proposed_ranks: list[list[int]]) -> list[int]:
        final_ranks = [0 for _ in range(self.rank_no)]

        for rank,llm_in_rank in enumerate(proposed_ranks):
            # only one person chose this rank
            if len(llm_in_rank) == 1:
                final_ranks[rank] = llm_in_rank[0]
                break

            # shift by one
            if len(llm_in_rank) == 0:
                for ranks in range(rank, self.rank_no-1):
                    proposed_ranks[ranks] = proposed_ranks[ranks+1]
                proposed_ranks[self.rank_no-1] = []

            # multiple people chose the same rank

            chosen_llm_index = randrange(len(llm_in_rank))
            chosen_llm = llm_in_rank[chosen_llm_index]
            del llm_in_rank[chosen_llm_index]
            final_ranks[rank] = chosen_llm

            for ranks in range(rank, self.rank_no-1):
                if proposed_ranks[ranks] == []:
                    proposed_ranks[ranks] = llm_in_rank
                    break

        return final_ranks

    def _calculate_altrusim(self) -> list[int]:
        pass

    def _generate_prompt(llm_index: int) -> str:
        return "{llm_index}".format(llm_index=llm_index)

        pass

    def _save_result(self):
        pass
