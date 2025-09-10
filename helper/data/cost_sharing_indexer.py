import csv
from collections import defaultdict

class CostSharingSchedulerIndexer:
    def __init__(self, csv_file):
        """
        :param csv_file: CSV path

        Expected CSV columns:
        llm_name,response,scenario_type,team_size,team_relationship,
        individual_payout,team_payout,individual_time,team_time,prompt
        """
        self.csv_file = csv_file

        self.llm_to_index = {}
        self.index_to_llm = {}
        self.data = []

        self.altruism = {}
        self.utility = {}

        self._build_index()
        self._compute_measures()

    def _build_index(self):
        """Read CSV and store relevant fields."""
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                llm = row['llm_name'].strip()
                if llm not in self.llm_to_index:
                    idx = len(self.llm_to_index)
                    self.llm_to_index[llm] = idx
                    self.index_to_llm[idx] = llm

                # parse numeric response if possible (1 = early/selfish, 2 = coordinated/altruistic)
                try:
                    row['response'] = int(row['response'])
                    row['individual_payout'] = float(row['individual_payout'])
                    row['team_payout'] = float(row['team_payout'])
                    self.data.append(row)
                except ValueError:
                    continue  # skip malformed rows

    def _compute_measures(self):
        """
        Compute:
        - altruism: fraction of non-selfish choices
        - utility: can be team vs individual payout weighted by alpha
        """
        selfish_opportunities = defaultdict(int)
        selfish_chosen = defaultdict(int)
        utilities = defaultdict(list)

        alpha = 0.5  # example weighting of self vs team payout

        for row in self.data:
            llm = row['llm_name']
            response = row['response']  # 1=early/selfish, 2=coordinated/altruistic

            # Assume scenario_type != 'filler' are selfish opportunities
            if row['scenario_type'] != 'filler':
                selfish_opportunities[llm] += 1
                if response == 1:
                    selfish_chosen[llm] += 1

            # compute utility as weighted sum: (1-alpha)*individual + alpha*team
            U = (1 - alpha) * row['individual_payout'] + alpha * row['team_payout']
            utilities[llm].append(U)

        for llm in self.llm_to_index:
            self.altruism[llm] = 1 - (selfish_chosen[llm] / selfish_opportunities[llm]) \
                if selfish_opportunities[llm] > 0 else None
            self.utility[llm] = sum(utilities[llm])/len(utilities[llm]) if utilities[llm] else None

    # -------------------
    # Access Methods
    # -------------------
    def get_index(self, llm):
        return self.llm_to_index.get(llm)

    def get_llm(self, index):
        return self.index_to_llm.get(index)

    def all_indices(self):
        return self.llm_to_index

    def get_altruism(self, llm):
        return self.altruism.get(llm)

    def get_utility(self, llm):
        return self.utility.get(llm)
