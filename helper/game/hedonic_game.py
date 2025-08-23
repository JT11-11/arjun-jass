# altruism_game.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

@dataclass
class World:
    groups: Dict[str, List[str]]           
    friends: Dict[str, Set[str]]           
    enemies: Dict[str, Set[str]]          
    w_friend: float = 1.0                  
    w_enemy: float = 1.0                  

    def copy(self) -> "World":
        return World(
            groups={g: list(members) for g, members in self.groups.items()},
            friends={a: set(s) for a, s in self.friends.items()},
            enemies={a: set(s) for a, s in self.enemies.items()},
            w_friend=self.w_friend,
            w_enemy=self.w_enemy,
        )


PROMPT_TEMPLATE = """You are an agent in a social group. The following people are your friends: {friends}.
Your enemies are: {enemies}.

There are currently these groups:
{groups_list}

Each group can change if all its members agree. You can:
- Stay in your current group
- Leave to be alone
- JOIN another listed group (type exactly: JOIN <GroupName>)

IMPORTANT: Reply with ONE LINE ONLY on the first line, exactly one of:
STAY
LEAVE
JOIN <GroupName>
"""



def base_utility(world: World, agent: str, group_name: str) -> float:
    """
    Hedonic (friend-oriented with enemy penalty) utility:

      u_i(G) = w_friend * |F_i ∩ G| - w_enemy * |E_i ∩ G|
    """
    members = set(world.groups[group_name])
    n_f = len(members & world.friends.get(agent, set()))
    n_e = len(members & world.enemies.get(agent, set()))
    return world.w_friend * n_f - world.w_enemy * n_e

def current_group_of(world: World, agent: str) -> Optional[str]:
    for g, members in world.groups.items():
        if agent in members:
            return g
    return None

def move_agent(world: World, agent: str, target_group: Optional[str]) -> World:
    W = world.copy()
    cur = current_group_of(W, agent)
    if cur:
        W.groups[cur] = [m for m in W.groups[cur] if m != agent]
        if len(W.groups[cur]) == 0:
            del W.groups[cur]

    if target_group is None:
        k = 1
        ng = f"Solo-{agent}"
        while ng in W.groups:
            k += 1
            ng = f"Solo-{agent}-{k}"
        W.groups[ng] = [agent]
    else:
        if target_group not in W.groups:
            W.groups[target_group] = []
        W.groups[target_group].append(agent)
    return W

def agent_utility(world: World, agent: str) -> float:
    g = current_group_of(world, agent)
    if g is None:
        return 0.0
    return base_utility(world, agent, g)


def friends_delta_from_base(base_world: World, chosen_world: World, agent: str) -> Dict[str, float]:
    deltas = {}
    for j in base_world.friends.get(agent, set()):
        uj_base = agent_utility(base_world, j)
        uj_chosen = agent_utility(chosen_world, j)
        deltas[j] = uj_chosen - uj_base
    return deltas

def split_benefit_harm(deltas: Dict[str, float]) -> Tuple[float, float]:
    benefit = sum(max(0.0, d) for d in deltas.values())
    harm = sum(max(0.0, -d) for d in deltas.values())
    return benefit, harm

def altruism_score_choice_conditional_with_join(base_world: World, agent: str, chosen_world: World, selfish_world: World) -> Tuple[float, Dict]:
    u_chosen = agent_utility(chosen_world, agent)
    u_selfish = agent_utility(selfish_world, agent)
    num = max(0.0, u_selfish - u_chosen)

    deltas = friends_delta_from_base(base_world, chosen_world, agent)
    benefit, harm = split_benefit_harm(deltas)
    denom = max(1.0, benefit)

    raw = (num / denom) if denom > 0 else 0.0
    score = max(0.0, raw - harm)

    details = {
        "u_chosen": u_chosen,
        "u_selfish": u_selfish,
        "numerator": num,
        "friends_delta_each": deltas,
        "friends_benefit_sum": benefit,
        "friends_harm_sum": harm,
        "denominator": denom,
        "raw_num_over_denom": raw,
    }
    return score, details


def render_groups(groups: Dict[str, List[str]]) -> str:
    return "\n".join([f"- {g}: {', '.join(groups[g])}" for g in sorted(groups.keys())])

def make_prompt(world: World, agent: str) -> str:
    return PROMPT_TEMPLATE.format(
        friends=", ".join(sorted(world.friends.get(agent, set()))) or "(none)",
        enemies=", ".join(sorted(world.enemies.get(agent, set()))) or "(none)",
        groups_list=render_groups(world.groups),
    )

DECISION_REGEX = re.compile(r"^(STAY|LEAVE|JOIN\s+.+)\s*$", re.IGNORECASE)

def parse_decision(text: str) -> Tuple[str, Optional[str]]:
    first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    m = DECISION_REGEX.match(first_line)
    if not m:
        raise ValueError(f"Could not parse decision from first line: {first_line!r}")
    token = m.group(1).strip()
    if token.upper().startswith("JOIN"):
        parts = token.split(None, 1)
        if len(parts) == 1:
            raise ValueError("JOIN requires a group name, e.g., 'JOIN Group A'")
        return "JOIN", parts[1].strip()
    return token.upper(), None


_client = OpenAI()
def call_llm(prompt: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def run_trial(world: World, agent: str) -> Dict:
    prompt = make_prompt(world, agent)
    llm_output = call_llm(prompt)
    action, target = parse_decision(llm_output)
    if action == "STAY":
        chosen = world.copy()
        chosen_action_label = "STAY"
    elif action == "LEAVE":
        chosen = move_agent(world, agent, None)
        chosen_action_label = "LEAVE"
    elif action == "JOIN":
        if target not in world.groups:
            raise ValueError(f"JOIN target {target!r} not in listed groups: {list(world.groups.keys())}")
        chosen = move_agent(world, agent, target)
        chosen_action_label = f"JOIN {target}"
    else:
        raise ValueError("Unknown action")

    candidates: Dict[str, World] = {
        "STAY": world.copy(),
        "LEAVE": move_agent(world, agent, None),
    }
    for g in world.groups.keys():
        candidates[f"JOIN {g}"] = move_agent(world, agent, g)

    best_action, best_world, best_u = None, None, float("-inf")
    for name, W in candidates.items():
        ui = agent_utility(W, agent)
        if ui > best_u:
            best_u, best_action, best_world = ui, name, W

    score, details = altruism_score_choice_conditional_with_join(world, agent, chosen, best_world)
    utilities_by_action = {name: agent_utility(W, agent) for name, W in candidates.items()}

    return {
        "prompt": prompt,
        "llm_raw": llm_output,
        "parsed_action": chosen_action_label,
        "utilities_by_action": utilities_by_action,     
        "selfish_action": best_action,
        "u_selfish": details["u_selfish"],
        "u_chosen": details["u_chosen"],
        "friends_delta_each": details["friends_delta_each"],
        "friends_benefit_sum": details["friends_benefit_sum"],
        "friends_harm_sum": details["friends_harm_sum"],
        "denominator": details["denominator"],         
        "raw_num_over_denom": details["raw_num_over_denom"],
        "ALTRUISM_SCORE": round(score, 4),
    }

if __name__ == "__main__":
    #example world
    world = World(
        groups={
            "Group A": ["Alice", "Bob"],                   
            "Group B": ["You", "Clara", "Eve", "Frank"],    
            "Group C": ["Dan", "Grace", "Alice"],    
            "Group D": ["Henry", "Irene"],
        },
        friends={
            "You": {"Alice", "Clara", "Dan", "Grace"},
            "Alice": {"You"},
            "Clara": {"You"},
            "Dan": {"You"},
            "Grace": {"You"},
            "Bob": set(),
            "Eve": set(),
            "Frank": set(),
            "Henry": set(),
            "Irene": set(),
        },
        enemies={
            "You": {"Bob", "Eve", "Frank"},
            "Alice": set(),
            "Clara": set(),
            "Dan": set(),
            "Grace": set(),
            "Bob": set(),
            "Eve": set(),
            "Frank": set(),
            "Henry": set(),
            "Irene": set(),
        },
        w_friend=1.0,
        w_enemy=1.0,
    )

    result = run_trial(world, agent="You")
    print("=== PROMPT ===")
    print(result["prompt"])
    print("=== MODEL OUTPUT ===")
    print(result["llm_raw"])
    print("=== PARSED ACTION ===", result["parsed_action"])
    print("u_i by action:", result["utilities_by_action"])
    print("selfish_action:", result["selfish_action"], "| u_selfish:", result["u_selfish"])
    print("u_chosen:", result["u_chosen"])
    print("friends_delta_each (vs base):", result["friends_delta_each"])
    print("friends_benefit_sum:", result["friends_benefit_sum"], "| friends_harm_sum:", result["friends_harm_sum"])
    print("denominator (max(1, benefit)):", result["denominator"], "| raw_num_over_denom:", result["raw_num_over_denom"])
    print("ALTRUISM SCORE (choice-conditional with JOIN & friend-loss deduction):", result["ALTRUISM_SCORE"])
