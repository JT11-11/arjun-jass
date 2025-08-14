from helper.game import Game
from helper.llm.LLM import LLM

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
            proposed_ranks: list[int] = self._ask_for_rank()
            proposed_ranks_by_round.append(proposed_ranks)

            final_rankings: list[int] = self._resolve_congestion(proposed_ranks)
            final_ranks_by_round.append(final_rankings)
            
            self.curr_round += 1

        # save results in data
        self._save_result()

    # returns the proposed rank for each LLM
    def _ask_for_rank(self) -> list[int]:
        for llm in llms:
            llm.ask()
        pass

    def _resolve_congestion(self, proposed_ranks: list[int]) -> list[int]:
        pass

    def _calculate_altrusim(self) -> list[int]:
        pass

    def _save_result(self):
        pass
