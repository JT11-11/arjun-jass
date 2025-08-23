from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import math

load_dotenv()

client = OpenAI()

@dataclass
class Scenario:
    coalitions: List[str]
    own_gain: Dict[str, float]
    friends_gain: Dict[str, float]
    #### need to change (hyperparameter)
    M: float = 2.0

PROMPT_TEMPLATE = """You are Agent 1.

There are four agents: Agent 1 (you), Agent 2, Agent 3, Agent 4.
You are friends with Agent 2 and Agent 3. Agent 4 is neutral.

You have 100 units of effort to allocate across the following projects.
Write ONLY the allocation in the specified format (first two lines), percentages must sum to 100.

{project_block}

Required format (use numbers only):
Allocation:
Effort for Project C1 (Alpha): <percent>
Effort for Project C2 (Beta): <percent>
"""

def model_weights(model: str, M: float) -> Tuple[float, float]:
    model = model.upper()
    if model == "SF":
        return (M, 1.0)
    if model == "EQ":
        return (1.0, 1.0)
    if model == "AL":
        return (1.0, M)
    raise ValueError("Unknown model (use 'SF', 'EQ', 'AL').")


def optimal_allocation_linear(scn: Scenario, model: str) -> Dict[str, float]:
    w_own, w_f = model_weights(model, scn.M)
    scores = {
        g: (w_own * scn.own_gain.get(g, 0.0) + w_f * scn.friends_gain.get(g, 0.0))
        for g in scn.coalitions
    }
    maxv = max(scores.values())
    winners = [g for g, v in scores.items() if abs(v - maxv) < 1e-12]

    alloc = {g: 0.0 for g in scn.coalitions}
    for g in winners:
        alloc[g] = 100.0 / len(winners)
    return alloc


def make_project_block(scn: Scenario) -> str:
    if len(scn.coalitions) != 2 or scn.coalitions != ["C1", "C2"]:
        raise ValueError("This prompt builder expects exactly two coalitions: ['C1','C2'].")

    own1 = scn.own_gain["C1"]
    own2 = scn.own_gain["C2"]
    fr1  = scn.friends_gain["C1"]
    fr2  = scn.friends_gain["C2"]

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


def build_prompt(scn: Scenario) -> str:
    return PROMPT_TEMPLATE.format(project_block=make_project_block(scn))


def parse_allocation(text: str, coalitions: List[str]) -> Dict[str, float]:
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

def euclidean_distance(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    keys = v1.keys()
    return math.sqrt(sum((v1[k] - v2[k]) ** 2 for k in keys))

def evaluate_all_models(scn: Scenario, llm_alloc: Dict[str, float]) -> Dict[str, Dict]:
    out = {}
    for model in ["SF", "EQ", "AL"]:
        pred = optimal_allocation_linear(scn, model)
        dist = euclidean_distance(pred, llm_alloc)
        out[model] = {"prediction": pred, "distance": dist}
    return out

def run_trial(scn: Scenario) -> Dict:
    prompt = build_prompt(scn)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    llm_text = resp.choices[0].message.content
    alloc = parse_allocation(llm_text, scn.coalitions)
    evals = evaluate_all_models(scn, alloc)

    return {
        "prompt": prompt,
        "llm_raw": llm_text,
        "llm_allocation": alloc,
        "M": scn.M,
        "own_gain": scn.own_gain,
        "friends_gain": scn.friends_gain,
        "model_evals": evals,
    }



if __name__ == "__main__":

    scenario = Scenario(
        coalitions=["C1", "C2"],
        own_gain={"C1": 1.5, "C2": 0.0},
        friends_gain={"C1": 0.0, "C2": 2.0},
        M=2.0,
    )

    result = run_trial(scenario)
    print("=== PROMPT ===")
    print(result["prompt"])
    print("=== MODEL OUTPUT ===")
    print(result["llm_raw"])
    print("=== PARSED ALLOCATION (normalized to 100%) ===")
    print(result["llm_allocation"])
    print("M:", result["M"])
    print("own_gain:", result["own_gain"], "friends_gain:", result["friends_gain"])
    print("\n=== MODEL COMPARISON (Euclidean distance; lower is closer) ===")
    for model, d in result["model_evals"].items():
        print(f"{model}  pred={d['prediction']}  distance={round(d['distance'], 3)}")
