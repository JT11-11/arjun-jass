import csv
from collections import defaultdict

class NonAtomicIndexer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.llm_to_index = {}
        self.index_to_llm = {}
        self.data = []  # store all rows
        self.altruism = defaultdict(lambda: defaultdict(dict))  # llm -> round -> measures
        self._build_index()
        self._derive_altruism()

    def _build_index(self):
        """Reads the CSV, builds index, and stores rows safely."""
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # skip empty rows
                if not row or all(not v.strip() for v in row.values()):
                    continue

                # extract llm and clean it
                llm = row.get('llm', '').strip()
                if not llm:
                    continue  # skip rows without a valid LLM

                # assign index if new
                if llm not in self.llm_to_index:
                    idx = len(self.llm_to_index)
                    self.llm_to_index[llm] = idx
                    self.index_to_llm[idx] = llm

                # parse numeric fields safely
                try:
                    row_round = row.get('round', '').strip()
                    if row_round.lower() == 'round' or not row_round:
                        continue  # skip header-like row

                    row['round'] = int(row_round)
                    row['consumption'] = float(row.get('consumption', 0))
                    row['fish_num'] = float(row.get('fish_num', 0))
                    row['fishermen_num'] = int(row.get('fishermen_num', 0))

                    self.data.append(row)
                except ValueError:
                    # skip rows with invalid numeric data
                    continue


    def _derive_altruism(self):
        """Compute average altruism measures for each LLM across all rounds."""
        # group data by round
        rounds = defaultdict(list)
        for r in self.data:
            rounds[r['round']].append(r)

        temp_altruism = defaultdict(lambda: defaultdict(list))  # llm -> measure -> list of values

        for round_num, round_data in rounds.items():
            Xmax = max(r['consumption'] for r in round_data)
            impacts = {r['llm']: r['consumption'] / r['fish_num'] for r in round_data}
            max_impact = max(impacts.values())
            selfish_payoff = round_data[0]['fish_num'] / round_data[0]['fishermen_num']

            for r in round_data:
                llm = r['llm']
                Xi = r['consumption']
                observed_payoff = Xi

                # compute measures
                rel_harvest = 1 - (Xi / Xmax)
                marginal_impact = 1 - (impacts[llm] / max_impact)
                deviation = selfish_payoff - observed_payoff

                # store in temp lists
                temp_altruism[llm]['relative_harvest_altruism'].append(rel_harvest)
                temp_altruism[llm]['marginal_impact_resource'].append(marginal_impact)
                temp_altruism[llm]['deviation_from_selfish_nash'].append(deviation)

        # compute average per LLM
        for llm, measures in temp_altruism.items():
            self.altruism[llm] = {
                measure: sum(values) / len(values) for measure, values in measures.items()
            }

# -------------------
# Access methods now return averages
# -------------------

    def relative_harvest_altruism(self, llm):
        return self.altruism[llm]["relative_harvest_altruism"]

    def marginal_impact_resource(self, llm):
        return self.altruism[llm]["marginal_impact_resource"]

    def deviation_from_selfish_nash(self, llm):
        return self.altruism[llm]["deviation_from_selfish_nash"]
    
    def get_index(self, llm):
        return self.llm_to_index.get(llm, None)

    def get_llm(self, index):
        return self.index_to_llm.get(index, None)

    def all_indices(self):
        return self.llm_to_index
