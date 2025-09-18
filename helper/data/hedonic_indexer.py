import pandas as pd
from collections import defaultdict

class HedonicGameIndexer:
    def __init__(self, csv_file):
        """
        :param csv_file: path to CSV containing hedonic game results
        
        Expected CSV columns:
        llm_name,agent,prompt,llm_value,llm_reasoning,parsed_action,
        selfish_action,u_selfish,u_chosen,friends_benefit_sum,friends_harm_sum,ALTRUISM_SCORE
        """
        self.csv_file = csv_file
        self.df = None
        self.llm_to_index = {}
        self.index_to_llm = {}
        self.altruism = {}
        
        self._load_data()
        self._build_index()
        self._compute_measures()

    def _load_data(self):
        """Load CSV into pandas and clean data types."""
        self.df = pd.read_csv(self.csv_file, engine="python", quoting=1, on_bad_lines="skip")
        
        # Clean numeric fields
        numeric_cols = ['llm_value', 'u_selfish', 'u_chosen', 'friends_benefit_sum', 
                       'friends_harm_sum', 'ALTRUISM_SCORE']
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
        
        # Drop rows with missing essential data
        self.df = self.df.dropna(subset=['llm_name', 'ALTRUISM_SCORE'])

    def _build_index(self):
        """Build mappings between LLM names and indices."""
        unique_llms = self.df["llm_name"].str.strip().unique()
        self.llm_to_index = {llm: i for i, llm in enumerate(unique_llms)}
        self.index_to_llm = {i: llm for llm, i in self.llm_to_index.items()}

    def _compute_measures(self):
        """Compute altruism measures per LLM."""
        grouped = self.df.groupby("llm_name")
        
        self.altruism = {
            llm: {
                "altruism_score": group["ALTRUISM_SCORE"].mean(),
                "friends_benefit": group["friends_benefit_sum"].mean(),
                "friends_harm": group["friends_harm_sum"].mean(),
                "utility_selfish": group["u_selfish"].mean(),
                "utility_chosen": group["u_chosen"].mean(),
                "stay_rate": (group["parsed_action"] == "STAY").mean(),
                "leave_rate": (group["parsed_action"] == "LEAVE").mean()
            }
            for llm, group in grouped
        }

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
