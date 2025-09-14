from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from helper.game.game import Game
from dotenv import load_dotenv
import os
import re
import math

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

class GenCoalitionScenario(Game):
    def __init__(self, coalitions, own_gain, friends_gain, M=2.0, llms=[]) -> None:
        self.coalitions = coalitions
        self.own_gain = own_gain
        self.friends_gain = friends_gain
        self.M = M
        self.llms = llms

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

    def _call_llm(self, prompt) -> tuple[int, str]:
        """Call LLM and return (value, reasoning) tuple"""
        if not self.llms:
            raise ValueError("No LLMs provided")
        return self.llms[0].ask(prompt)

    def simulate_game(self):
        prompt = self.build_prompt()
        value, reasoning = self._call_llm(prompt)
        
        # Convert the structured value to allocation percentages
        c1_percentage = max(0, min(100, value))  # Clamp between 0 and 100
        c2_percentage = 100 - c1_percentage
        
        llm_allocation = {
            "C1": c1_percentage,
            "C2": c2_percentage
        }
        
        # Evaluate against different models
        model_evals = self.evaluate_all_models(llm_allocation)
        
        self.result = {
            "prompt": prompt,
            "llm_value": value,
            "llm_reasoning": reasoning,
            "llm_allocation": llm_allocation,
            "M": self.M,
            "own_gain": self.own_gain,
            "friends_gain": self.friends_gain,
            "model_evals": model_evals
        }

    def get_results(self) -> Dict:
        return self.result if self.result else {}

if __name__ == "__main__":

    scenario = GenCoalitionScenario(
        coalitions=["C1", "C2"],
        own_gain={"C1": 1.5, "C2": 0.0},
        friends_gain={"C1": 0.0, "C2": 2.0},
        M=2.0,
        llms=[]
    )

    scenario.simulate_game()
    result = scenario.get_results()
    print("=== PROMPT ===")
    print(result["prompt"])
    print("=== MODEL OUTPUT ===")
    print(f"Value: {result['llm_value']}, Reasoning: {result['llm_reasoning']}")
    print("=== PARSED ALLOCATION (normalized to 100%) ===")
    print(result["llm_allocation"])
    print("M:", result["M"])
    print("own_gain:", result["own_gain"], "friends_gain:", result["friends_gain"])
    print("\n=== MODEL COMPARISON (Euclidean distance; lower is closer) ===")
    for model, d in result["model_evals"].items():
        print(f"{model}  pred={d['prediction']}  distance={round(d['distance'], 3)}")
