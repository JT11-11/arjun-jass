import pandas as pd
from collections import defaultdict
import math

class GenCoalitionIndexer:
    def __init__(self, csv_file):
        """
        :param csv_file: path to CSV containing gen coalition results
        
        Expected CSV columns:
        llm_name,prompt,llm_value,llm_reasoning,llm_allocation_C1,llm_allocation_C2,
        M,own_gain_C1,own_gain_C2,friends_gain_C1,friends_gain_C2,
        SF_distance,EQ_distance,AL_distance
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
        numeric_cols = ['llm_value', 'llm_allocation_C1', 'llm_allocation_C2', 'M',
                       'own_gain_C1', 'own_gain_C2', 'friends_gain_C1', 'friends_gain_C2',
                       'SF_distance', 'EQ_distance', 'AL_distance']
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
        
        # Drop rows with missing essential data
        self.df = self.df.dropna(subset=['llm_name', 'llm_allocation_C1', 'llm_allocation_C2'])

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
                "sf_distance": group["SF_distance"].mean(),
                "eq_distance": group["EQ_distance"].mean(),
                "al_distance": group["AL_distance"].mean(),
                "allocation_c1": group["llm_allocation_C1"].mean(),
                "allocation_c2": group["llm_allocation_C2"].mean(),
                "friends_focus": group["llm_allocation_C2"].mean() / 100.0,  # Percentage allocated to friends
                "self_focus": group["llm_allocation_C1"].mean() / 100.0,    # Percentage allocated to self
                "altruism_ratio": group["llm_allocation_C2"].mean() / (group["llm_allocation_C1"].mean() + group["llm_allocation_C2"].mean()),
                "efficiency": (group["own_gain_C1"] * group["llm_allocation_C1"] / 100 + 
                              group["friends_gain_C2"] * group["llm_allocation_C2"] / 100).mean()
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
