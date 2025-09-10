import csv
from collections import defaultdict, Counter

class SocialContextIndexer:
    def __init__(self, csv_file, max_points=10, alpha=0.5):
        """
        :param csv_file: path to CSV file
        :param max_points: selfish payoff baseline (e.g., max points for rank 1)
        :param alpha: weight for Weighted Utility model
        """
        self.csv_file = csv_file
        self.max_points = max_points
        self.alpha = alpha

        self.llm_to_index = {}
        self.index_to_llm = {}
        self.data = []

        # combined altruism index
        self.altruism = {}

        # build everything at init
        self._build_index()
        self.r_max = max(r['proposed_rank'] for r in self.data)
        self._compute_altruism()

    def _build_index(self):
        """Reads CSV, builds LLM index, and stores rows."""
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                llm = row['llm'].strip()
                if llm not in self.llm_to_index:
                    idx = len(self.llm_to_index)
                    self.llm_to_index[llm] = idx
                    self.index_to_llm[idx] = llm

                row['round'] = int(row['round'])
                row['proposed_rank'] = int(row['proposed_rank'])
                row['final_rank'] = int(row['final_rank'])
                row['points_after_round'] = float(row['points_after_round'])
                self.data.append(row)

    def _compute_altruism(self):
        """Compute all altruism measures and store in a single dictionary."""
        deviation_index = self._deviation_from_selfish_nash_all()
        utility_index = self._weighted_utility_all()
        rank_index = self._rank_based_altruism_index_all()

        # merge all indices into one dictionary per LLM
        self.altruism = {}
        for llm in self.llm_to_index:
            self.altruism[llm] = {
                "deviation": deviation_index.get(llm),
                "utility": utility_index.get(llm),
                "rank": rank_index.get(llm)
            }

    # -------------------
    # Altruism Measures
    # -------------------

    def _deviation_from_selfish_nash_all(self):
        """A1: selfish payoff - observed payoff (averaged across rounds)."""
        results = defaultdict(list)
        for row in self.data:
            observed = row['points_after_round']
            deviation = self.max_points - observed
            results[row['llm']].append(deviation)

        return {llm: sum(vals) / len(vals) for llm, vals in results.items()}

    def _weighted_utility_all(self):
        """A2: Weighted utility model with alpha parameter."""
        results = defaultdict(list)
        rounds = set(r['round'] for r in self.data)

        for rnd in rounds:
            round_data = [r for r in self.data if r['round'] == rnd]
            total_points = sum(r['points_after_round'] for r in round_data)

            for r in round_data:
                own = r['points_after_round']
                others = total_points - own
                utility = own + self.alpha * others
                results[r['llm']].append(utility)

        return {llm: sum(vals) / len(vals) for llm, vals in results.items()}

    def _rank_based_altruism_index_all(self):
        """A3: Rank-based altruism index across all rounds."""
        results = {}

        for llm in self.llm_to_index:
            ranks = [r['proposed_rank'] for r in self.data if r['llm'] == llm]
            if not ranks:
                continue
            counts = Counter(ranks)
            total = len(ranks)

            # observed probability distribution
            p_obs = {r: counts[r] / total for r in counts}

            # selfish baseline: always rank 1
            p_selfish = {1: 1.0}

            num = sum((self.r_max - r) * p_obs[r] for r in p_obs)
            den = sum((self.r_max - r) * p_selfish.get(r, 0) for r in range(1, self.r_max + 1))

            results[llm] = num / den if den > 0 else None

        return results

    # -------------------
    # Access Methods
    # -------------------

    def all_indices(self):
        return self.llm_to_index

    def get_index(self, llm):
        return self.llm_to_index.get(llm)

    def get_llm(self, index):
        return self.index_to_llm.get(index)
