import pandas as pd
from collections import defaultdict, Counter

class SocialContextIndexer:
    def __init__(self, csv_file, max_points=8, alpha=0.5):
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

        # read CSV into a DataFrame
        self.df = pd.read_csv(self.csv_file)
        self.df['round'] = self.df['round'].astype(int)
        self.df['proposed_rank'] = self.df['proposed_rank'].astype(int)
        self.df['final_rank'] = self.df['final_rank'].astype(int)
        self.df['points_after_round'] = self.df['points_after_round'].astype(float)

        # build LLM index
        self.llm_to_index = {llm: i for i, llm in enumerate(self.df['llm'].unique())}
        self.index_to_llm = {i: llm for llm, i in self.llm_to_index.items()}

        # max rank for rank-based measure
        self.r_max = self.df['proposed_rank'].max()

        # combined altruism dictionary
        self.altruism = self._compute_altruism()

    # -------------------
    # Altruism Measures
    # -------------------

    def _compute_altruism(self):
        deviation_index = self._deviation_from_selfish_nash_all()
        utility_index = self._weighted_utility_all()
        rank_index = self._rank_based_altruism_index_all()

        # merge into single dict
        return {
            llm: {
                "deviation": deviation_index.get(llm),
                "utility": utility_index.get(llm),
                "rank": rank_index.get(llm)
            } for llm in self.llm_to_index
        }

    def _deviation_from_selfish_nash_all(self):
        # deviation = max_points - points_after_round
        df_dev = self.df.copy()
        df_dev['deviation'] = self.max_points - df_dev['points_after_round']
        return df_dev.groupby('llm')['deviation'].mean().to_dict()

    def _weighted_utility_all(self):
        df_utility = self.df.copy()
        df_utility['total_round_points'] = df_utility.groupby('round')['points_after_round'].transform('sum')
        df_utility['others'] = df_utility['total_round_points'] - df_utility['points_after_round']
        df_utility['weighted_utility'] = df_utility['points_after_round'] + self.alpha * df_utility['others']
        return df_utility.groupby('llm')['weighted_utility'].mean().to_dict()

    def _rank_based_altruism_index_all(self):
        results = {}
        for llm, group in self.df.groupby('llm'):
            ranks = group['proposed_rank'].tolist()
            if not ranks:
                continue

            counts = Counter(ranks)
            total = len(ranks)
            p_obs = {r: counts[r] / total for r in counts}
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
