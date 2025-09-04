import csv
from helper.game.game import Game
from helper.llm.LLM import LLM


class AtomicCongestion(Game):
    def __init__(self, total_rounds: int, llms: list[LLM]) -> None:
        assert len(llms) == 2, "Atomic Congestion requires exactly 2 players"
        self.total_rounds = total_rounds
        self.curr_round = 0
        self.llms = llms

        # store cumulative travel times (lower = better)
        self.travel_times: list[int] = [0 for _ in range(len(llms))]
        self.last_moves: list[str] = ["" for _ in range(len(llms))]

        # payoff matrix (Route 1 = Defect, Route 2 = Cooperate)
        # returns (p1_time, p2_time)
        self.travel_time_matrix = {
            ("R1", "R1"): (6, 6),   # both Route 1 -> congestion
            ("R1", "R2"): (2, 4),   # R1 fast, R2 slow
            ("R2", "R1"): (4, 2),   # symmetric
            ("R2", "R2"): (4, 4),   # both cooperate
        }

        # open CSV for saving results
        self.csv_file = open("data/atomic_congestion_results.csv", "w", newline="")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(["round", "llm", "choice", "reasoning", "travel_time", "cumulative_time"])

    def simulate_game(self):
        while self.curr_round < self.total_rounds:
            moves, reasonings = self._ask_for_moves()

            # compute travel times from matrix
            outcome = self.travel_time_matrix[(moves[0], moves[1])]
            self.travel_times[0] += outcome[0]
            self.travel_times[1] += outcome[1]

            # save results for each LLM
            for i, llm in enumerate(self.llms):
                self._save_result([
                    self.curr_round + 1,
                    llm.get_model_name(),
                    moves[i],
                    reasonings[i],
                    outcome[i],
                    self.travel_times[i]
                ])

            # update memory
            self.last_moves = moves
            self.curr_round += 1

            print(f"Round {self.curr_round}: Moves={moves}, Times={outcome}, Totals={self.travel_times}")

        self.close_results()

    def _ask_for_moves(self):
        moves = []
        reasonings = []

        for index, llm in enumerate(self.llms):
            try:
                value, reasoning = llm.ask(self._generate_prompt(index))
            except Exception as e:
                print(f"[Error] LLM {llm.get_model_name()} failed: {e}")
                value, reasoning = 2, "Defaulted to Route 2 due to error."

            # validate response: must be 1 or 2
            if not isinstance(value, int) or value not in [1, 2]:
                print(f"[Warning] Invalid choice from {llm.get_model_name()}: {value}. Defaulting to Route 2.")
                value = 2
                reasoning += " (Invalid response, defaulted to Route 2.)"

            # map integer → route string
            move = "R1" if value == 1 else "R2"
            moves.append(move)
            reasonings.append(reasoning.replace("\n", ""))

        return moves, reasonings

    def _generate_prompt(self, llm_index: int) -> str:
        other_idx = 1 - llm_index
        last_self = self.last_moves[llm_index] if self.last_moves[llm_index] else "None"
        last_other = self.last_moves[other_idx] if self.last_moves[other_idx] else "Unknown"

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
This is a one-shot game.

Last round, you played: {last_self}
Last round, the other played: {last_other}
Your total travel time so far: {self.travel_times[llm_index]}

Choose your move this round:
1 = Route 1
2 = Route 2
"""

    def _save_result(self, row):
        self.writer.writerow(row)
        self.csv_file.flush()

    def close_results(self):
        self.csv_file.close()
