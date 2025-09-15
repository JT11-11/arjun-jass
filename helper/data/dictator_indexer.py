import pandas as pd
import re
from collections import defaultdict

class DictatorGameIndexer:
    def __init__(self, csv_file):
        """
        :param csv_file: path to CSV

        CSV columns:
        llm_name,response,scenario_type,endowment,num_recipients,
        work_contribution,project_context,team_relationship,prompt
        """
        self.csv_file = csv_file

        self.df = None
        self.llm_to_index = {}
        self.index_to_llm = {}
        self.altruism = {}
        self.utility = {}

        self._load_data()
        self._build_index()
        self._compute_measures()

    def _load_data(self):
        """Load CSV into pandas and parse Keep/Donate percentages from response."""
        df = pd.read_csv(self.csv_file, engine="python", quoting=1, on_bad_lines="skip")

        # Clean numeric fields
        df["endowment"] = pd.to_numeric(df["endowment"], errors="coerce")
        df["num_recipients"] = pd.to_numeric(df.get("num_recipients", 1), errors="coerce").fillna(1).astype(int)

        # Extract Keep and Donate percentages using regex
        df["keep_percent"] = df["response"].str.extract(r'Keep\s*(\d+)%').astype(float)
        df["donate_percent"] = df["response"].str.extract(r'Donate\s*(\d+)%').astype(float)

        # Keep only rows where both percentages were found
        df = df.dropna(subset=["keep_percent", "donate_percent", "endowment"])

        self.df = df

    def _build_index(self):
        """Build mappings between LLM names and indices."""
        unique_llms = self.df["llm_name"].str.strip().unique()
        self.llm_to_index = {llm: i for i, llm in enumerate(unique_llms)}
        self.index_to_llm = {i: llm for llm, i in self.llm_to_index.items()}

    def _compute_measures(self):
        """Compute altruism (fraction donated) and utility (kept + given)."""
        df = self.df.copy()

        # Altruism = donate / endowment
        df["altruism"] = df["donate_percent"] / df["endowment"]

        # Utility = kept + donated tokens
        df["utility"] = df["keep_percent"] + df["donate_percent"]

        # Aggregate averages per LLM
        grouped = df.groupby("llm_name")
        self.altruism = grouped["altruism"].mean().to_dict()
        self.utility = grouped["utility"].mean().to_dict()

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
