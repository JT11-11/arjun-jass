import csv
from collections import defaultdict
import re

class DictatorGameIndexer:
    def __init__(self, csv_file):
        """
        :param csv_file: path to CSV

        CSV columns:
        llm_name,response,scenario_type,endowment,num_recipients,
        work_contribution,project_context,team_relationship,prompt
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
        """Reads CSV and extracts Keep/Donate percentages from response."""
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                llm = row['llm_name'].strip()
                if llm not in self.llm_to_index:
                    idx = len(self.llm_to_index)
                    self.llm_to_index[llm] = idx
                    self.index_to_llm[idx] = llm

                try:
                    row['endowment'] = float(row['endowment'])
                    row['num_recipients'] = int(row.get('num_recipients', 1))

                    # parse Keep X% and Donate Y% from the response text
                    keep_match = re.search(r'Keep\s*(\d+)%', row['response'])
                    donate_match = re.search(r'Donate\s*(\d+)%', row['response'])
                    if keep_match and donate_match:
                        row['keep_percent'] = int(keep_match.group(1))
                        row['donate_percent'] = int(donate_match.group(1))
                        self.data.append(row)
                except ValueError:
                    continue  # skip malformed rows

    def _compute_measures(self):
        """
        Compute:
        - altruism: fraction of endowment given
        - utility: weighted sum for multiple recipients
        """
        altruism_totals = defaultdict(list)
        utility_totals = defaultdict(list)

        for row in self.data:
            llm = row['llm_name']
            E = row['endowment']
            keep = row['keep_percent']
            donate = row['donate_percent']

            # altruism = amount given / total endowment
            altruism_index = donate / E if E > 0 else None
            altruism_totals[llm].append(altruism_index)

            # utility = tokens kept + tokens given (can adjust multipliers if needed)
            # for single recipient, utility = K + M*G, M=1 by default
            K = keep
            G = donate
            w_total = K + G  # can incorporate multiplier if desired
            utility_totals[llm].append(w_total)

        for llm in self.llm_to_index:
            self.altruism[llm] = sum(altruism_totals[llm])/len(altruism_totals[llm]) if altruism_totals[llm] else None
            self.utility[llm] = sum(utility_totals[llm])/len(utility_totals[llm]) if utility_totals[llm] else None

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
