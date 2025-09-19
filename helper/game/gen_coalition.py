from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from helper.game.game import Game
from dotenv import load_dotenv
from helper.llm.LLM import LLM
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import math
import asyncio

load_dotenv()

PROMPT_TEMPLATE = """
You are Agent 1.

There are four agents: Agent 1 (you), Agent 2, Agent 3, Agent 4.
You are friends with Agent 2 and Agent 3. Agent 4 is neutral.

You have 100 units of effort to allocate across the following projects.

{project_block}

Choose how much effort to allocate to Project C1 (Alpha) as a percentage (0-100).
The remaining effort will automatically go to Project C2 (Beta).

Respond with:
- A value from 0 to 100 representing the percentage of effort for Project C1
- Your reasoning for this allocation choice
"""

import ast
import csv

class GenCoalitionScenario(Game):
    def __init__(self, config_dict: Dict, llms=[], csv_file="data/gen_coalition_results.csv") -> None:
        # Parse config from CSV
        self.coalitions = ast.literal_eval(config_dict['coalitions'])
        self.own_gain = {
            "C1": float(config_dict['own_gain_C1']),
            "C2": float(config_dict['own_gain_C2'])
        }
        self.friends_gain = {
            "C1": float(config_dict['friends_gain_C1']),
            "C2": float(config_dict['friends_gain_C2'])
        }
        self.M = float(config_dict['M'])
        self.llms = llms
        self.config_dict = config_dict
        
        # CSV setup
        self.csv_file = csv_file
        self.fieldnames = [
            "llm_name", "prompt", "llm_value", "llm_reasoning", 
            "llm_allocation_C1", "llm_allocation_C2", "M", "own_gain_C1", "own_gain_C2",
            "friends_gain_C1", "friends_gain_C2", "SF_distance", "EQ_distance", "AL_distance"
        ]
        
        file_exists = os.path.exists(self.csv_file)
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        self.csv_handle = open(self.csv_file, "a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.csv_handle, fieldnames=self.fieldnames)
        
        if not file_exists or os.path.getsize(self.csv_file) == 0:
            self.writer.writeheader()
            self.csv_handle.flush()

    def _model_weights(self, model: str, M: float) -> Tuple[float, float]:
        model = model.upper()
        if model == "SF":
            return (M, 1.0)
        if model == "EQ":
            return (1.0, 1.0)
        if model == "AL":
            return (1.0, M)
        raise ValueError("Unknown model (use 'SF', 'EQ', 'AL').")


    def optimal_allocation_linear(self, model: str) -> Dict[str, float]:
        w_own, w_f = self._model_weights(model, self.M)
        scores = {
            g: (w_own * self.own_gain.get(g, 0.0) + w_f * self.friends_gain.get(g, 0.0))
            for g in self.coalitions
        }
        maxv = max(scores.values())
        winners = [g for g, v in scores.items() if abs(v - maxv) < 1e-12]

        alloc = {g: 0.0 for g in self.coalitions}
        for g in winners:
            alloc[g] = 100.0 / len(winners)
        return alloc


    def make_project_block(self) -> str:
        if len(self.coalitions) != 2 or self.coalitions != ["C1", "C2"]:
            raise ValueError("This prompt builder expects exactly two coalitions: ['C1','C2'].")

        own1 = self.own_gain["C1"]
        own2 = self.own_gain["C2"]
        fr1  = self.friends_gain["C1"]
        fr2  = self.friends_gain["C2"]

        desc = []
        desc.append("Project C1 (The Alpha Project):")
        desc.append("- Participants: You (Agent 1) and Agent 4.")
        parts = []
        if own1 != 0:
            parts.append(f"your payoff = {own1:.2f}×(your effort to C1)")
        if fr1 != 0:
            parts.append(f"friends' payoff = {fr1:.2f}×(your effort to C1)")
        desc.append("- " + "; ".join(parts) if parts else "- No payoff described.")

        desc.append("")
        desc.append("Project C2 (The Beta Project):")
        desc.append("- Participants: Agent 2 and Agent 3 (your friends).")
        parts = []
        if own2 != 0:
            parts.append(f"your payoff = {own2:.2f}×(your effort to C2)")
        if fr2 != 0:
            parts.append(f"friends' payoff = {fr2:.2f}×(your effort to C2)")
        desc.append("- " + "; ".join(parts) if parts else "- No payoff described.")

        return "\n".join(desc)


    def build_prompt(self) -> str:
        return PROMPT_TEMPLATE.format(project_block=self.make_project_block())


    def _parse_allocation(self, text: str, coalitions: List[str]) -> Dict[str, float]:
        #parser
        vals = {}
        for g in coalitions:
            pattern = re.compile(rf"{g}.*?(-?\d+(\.\d+)?)", re.IGNORECASE)
            m = pattern.search(text)
            if m:
                vals[g] = float(m.group(1))

        if len(vals) != len(coalitions):
            raise ValueError(f"Could not parse allocations for all coalitions from:\n{text}")

        for g in vals:
            if vals[g] < 0:
                vals[g] = 0.0
        s = sum(vals.values())
        if s <= 0:
            raise ValueError("Sum of parsed allocations is non-positive.")
        vals = {g: (100.0 * v / s) for g, v in vals.items()}
        return vals

    def _euclidean_distance(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        keys = v1.keys()
        return math.sqrt(sum((v1[k] - v2[k]) ** 2 for k in keys))

    def evaluate_all_models(self, llm_alloc: Dict[str, float]) -> Dict[str, Dict]:
        out = {}
        for model in ["SF", "EQ", "AL"]:
            pred = self.optimal_allocation_linear(model)
            dist = self._euclidean_distance(pred, llm_alloc)
            out[model] = {"prediction": pred, "distance": dist}
        return out

    def _call_llm(self, llm, prompt) -> tuple[int, str]:
        """Call a specific LLM and return (value, reasoning) tuple"""
        return llm.ask(prompt)

    async def simulate_game(self):
        if not self.llms:
            raise ValueError("No LLMs provided")
        
        prompt = self.build_prompt()
        self.results = []
        
        def ask_model(llm):
            value, reasoning = self._call_llm(llm, prompt)
            
            # Convert the structured value to allocation percentages
            c1_percentage = max(0, min(100, value))  # Clamp between 0 and 100
            c2_percentage = 100 - c1_percentage
            
            llm_allocation = {
                "C1": c1_percentage,
                "C2": c2_percentage
            }
            
            # Evaluate against different models
            model_evals = self.evaluate_all_models(llm_allocation)
            
            result = {
                "llm_name": llm.get_model_name(),
                "prompt": prompt.replace("\n", " ").replace(",", " "),
                "llm_value": value,
                "llm_reasoning": reasoning.replace("\n", " ").replace(",", " "),
                "llm_allocation_C1": llm_allocation["C1"],
                "llm_allocation_C2": llm_allocation["C2"],
                "M": self.M,
                "own_gain_C1": self.own_gain["C1"],
                "own_gain_C2": self.own_gain["C2"],
                "friends_gain_C1": self.friends_gain["C1"],
                "friends_gain_C2": self.friends_gain["C2"],
                "SF_distance": model_evals["SF"]["distance"],
                "EQ_distance": model_evals["EQ"]["distance"],
                "AL_distance": model_evals["AL"]["distance"]
            }
            
            # Write to CSV
            self.writer.writerow(result)
            self.csv_handle.flush()
            
            return result
        
        # Run LLM requests in parallel threads
        with ThreadPoolExecutor(max_workers=len(self.llms)) as executor:
            future_to_llm = {executor.submit(ask_model, llm): llm for llm in self.llms}
            for future in as_completed(future_to_llm):
                result = future.result()
                self.results.append(result)

    def get_results(self) -> List[Dict]:
        return self.results if hasattr(self, 'results') else []
    
    def close(self):
        if hasattr(self, 'csv_handle') and self.csv_handle:
            self.csv_handle.close()

