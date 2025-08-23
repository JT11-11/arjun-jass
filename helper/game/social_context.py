from helper.game.game import Game
from helper.llm.LLM import LLM

from google.genai import types

from random import randrange

# ranking game
class SocialContext(Game):
    def __init__(self, ranks: int, rounds: int, llms: list[LLM]) -> None:
        self.total_rounds = rounds
        self.curr_round = 0
        self.rank_no = ranks
        self.points: list[int] = [0 for _ in range(len(llms))]
        self.last_round_ranks: list[int] = [-1 for _ in range(len(llms))]
        self.llms = llms
        print(self.points)
 
    def simulate_game(self):
        proposed_ranks_by_round: list[list[int]] = []
        final_ranks_by_round: list[list[int]] = []

        while self.curr_round < self.total_rounds:
            proposed_ranks: list[list[int]] = self._ask_for_rank()
            proposed_ranks_by_round.append(proposed_ranks)

            final_rankings: list[int] = self._resolve_congestion(proposed_ranks)
            final_ranks_by_round.append(final_rankings)

            self.last_round_ranks = list(map(lambda x: x+1, final_rankings))
            
            self.curr_round += 1

        # save results in data
        self._save_result()

    # returns the proposed rank for each LLM
    def _ask_for_rank(self) -> list[list[int]]:
        ranking = [[] for _ in range(self.rank_no)]
        reasoning = [[] for _ in range(self.rank_no)]

        for index, llm in enumerate(self.llms):
            llm_response = llm.ask(
                self._generate_prompt(index), 
            )
  
            # assigning to their rank in the array
            # converting llm rank response to array index
            ranking[llm_response['value']-1].append(index) 
            reasoning.append(llm_response['reasoning'])

        return ranking

    def _resolve_congestion(self, proposed_ranks: list[list[int]]) -> list[int]:
        final_ranks = [0 for _ in range(self.rank_no)]

        for rank,llm_in_rank in enumerate(proposed_ranks):
            # only one person chose this rank
            if len(llm_in_rank) == 1:
                final_ranks[rank] = llm_in_rank[0]

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

    def _save_result(self):
        pass
