import csv
from collections import defaultdict
from datetime import datetime

class CostSharingSchedulerIndexer:
    def __init__(self, csv_file):
        self.csv_file = csv_file

        self.llm_to_index = {}
        self.index_to_llm = {}
        self.data = []

        self.altruism = {}
        self.utility = {}

        self._build_index()
        self._compute_measures()

    # -------------------
    # CSV Reading & Parsing
    # -------------------
    def _build_index(self):
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                llm = row['llm_name'].strip()
                if llm not in self.llm_to_index:
                    idx = len(self.llm_to_index)
                    self.llm_to_index[llm] = idx
                    self.index_to_llm[idx] = llm

                try:
                    row['individual_time'] = self.parse_time(row['individual_time'])
                    row['team_time'] = self.parse_time(row['team_time'])
                    row['individual_payout'] = float(row['individual_payout'])
                    row['team_payout'] = float(row['team_payout'])
                    self.data.append(row)
                except ValueError as e:
                    print(f"Skipping row due to conversion error: {row}, Error: {e}")
                    continue

    def parse_time(self, t):
        if isinstance(t, str) and t.strip():
            dt = datetime.strptime(t.strip(), "%I:%M %p")
            return dt.hour * 60 + dt.minute
        return None

    # -------------------
    # Computation
    # -------------------
    def _compute_measures(self):
        llm_groups = defaultdict(list)
        for row in self.data:
            llm_groups[row['llm_name']].append(row)

        for llm, rows in llm_groups.items():
            altruism_eq13 = []
            altruism_eq14 = []
            utilities = []

            min_Ci = min(r['individual_time'] for r in rows if r['individual_time'] is not None)

            for r in rows:
                Ci = r['individual_time']
                Ti = r['team_time']
                Ei = r['individual_payout']
                Ti_payout = r['team_payout']

                if Ei is not None and Ci is not None and Ei != min_Ci:
                    Ai_13 = (Ei - Ci) / (Ei - min_Ci)
                    altruism_eq13.append(Ai_13)

                if Ti is not None and Ci is not None and Ti > 0:
                    Ai_14 = (Ti - Ci) / Ti
                    altruism_eq14.append(Ai_14)

                alpha = 0.5
                U = (1 - alpha) * Ei + alpha * Ti_payout
                utilities.append(U)

            self.altruism[llm] = {
                "eq13": sum(altruism_eq13)/len(altruism_eq13) if altruism_eq13 else None,
                "eq14": sum(altruism_eq14)/len(altruism_eq14) if altruism_eq14 else None
            }
            self.utility[llm] = sum(utilities)/len(utilities) if utilities else None

    # -------------------
    # Access Methods
    # -------------------
    def get_index(self, llm):
        return self.llm_to_index.get(llm)

    def get_llm(self, index):
        return self.index_to_llm.get(index)

    def all_indices(self):
        return list(self.llm_to_index.keys())

    def get_altruism(self, llm):
        return self.altruism.get(llm)

    def get_utility(self, llm):
        return self.utility.get(llm)
