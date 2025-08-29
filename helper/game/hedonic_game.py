# altruism_game.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

_client = OpenAI()
def call_llm(prompt: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

class World:
    def __init__(self, agent, groups, friends, enemies, w_friend=1.0, w_enemy=1.0) -> None:
        self.agent = agent
        self.groups: Dict[str, List[str]] = groups
        self.friends: Dict[str, Set[str]] = friends
        self.enemies: Dict[str, Set[str]] = enemies       
        self.w_friend: float = w_friend
        self.w_enemy: float = w_enemy

    def copy(self) -> "World":
        return World(
            agent=self.agent,
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

    def base_utility(self, agent: str, group_name: str) -> float:
        """
        Hedonic (friend-oriented with enemy penalty) utility:

          u_i(G) = w_friend * |F_i ∩ G| - w_enemy * |E_i ∩ G|
        """
        members = set(self.groups[group_name])
        n_f = len(members & self.friends.get(agent, set()))
        n_e = len(members & self.enemies.get(agent, set()))
        return world.w_friend * n_f - world.w_enemy * n_e

    def current_group_of(self, agent: str) -> Optional[str]:
        for g, members in self.groups.items():
            if agent in members:
                return g
        return None

    def move_agent(self, agent: str, target_group: Optional[str]) -> World:
        W = world.copy()
        cur = W.current_group_of(agent)
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

    def agent_utility(self, agent: str) -> float:
        g = self.current_group_of(agent)
        if g is None:
            return 0.0
        return self.base_utility(agent, g)


    def friends_delta_from_base(self, chosen_world: World, agent: str) -> Dict[str, float]:
        deltas = {}
        for j in self.friends.get(agent, set()):
            uj_base = self.agent_utility(j)
            uj_chosen = chosen_world.agent_utility(j)
            deltas[j] = uj_chosen - uj_base
        return deltas

    def split_benefit_harm(self, deltas: Dict[str, float]) -> Tuple[float, float]:
        benefit = sum(max(0.0, d) for d in deltas.values())
        harm = sum(max(0.0, -d) for d in deltas.values())
        return benefit, harm

    def altruism_score_choice_conditional_with_join(self, agent: str, chosen_world: World, selfish_world: World) -> Tuple[float, Dict]:
        u_chosen = chosen_world.agent_utility(agent)
        u_selfish = selfish_world.agent_utility(agent)
        num = max(0.0, u_selfish - u_chosen)

        deltas = self.friends_delta_from_base(chosen_world, agent)
        benefit, harm = self.split_benefit_harm(deltas)
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


    def render_groups(self, groups: Dict[str, List[str]]) -> str:
        return "\n".join([f"- {g}: {', '.join(groups[g])}" for g in sorted(groups.keys())])

    def make_prompt(self, agent: str) -> str:
        return self.PROMPT_TEMPLATE.format(
            friends=", ".join(sorted(self.friends.get(agent, set()))) or "(none)",
            enemies=", ".join(sorted(self.enemies.get(agent, set()))) or "(none)",
            groups_list=self.render_groups(self.groups),
        )

    DECISION_REGEX = re.compile(r"^(STAY|LEAVE|JOIN\s+.+)\s*$", re.IGNORECASE)

    def parse_decision(self, text: str) -> Tuple[str, Optional[str]]:
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        m = self.DECISION_REGEX.match(first_line)
        if not m:
            raise ValueError(f"Could not parse decision from first line: {first_line!r}")
        token = m.group(1).strip()
        if token.upper().startswith("JOIN"):
            parts = token.split(None, 1)
            if len(parts) == 1:
                raise ValueError("JOIN requires a group name, e.g., 'JOIN Group A'")
            return "JOIN", parts[1].strip()
        return token.upper(), None


    def simulate_game(self) -> Dict:
        prompt = self.make_prompt(self.agent)
        llm_output = call_llm(prompt)
        action, target = self.parse_decision(llm_output)
        if action == "STAY":
            chosen = world.copy()
            chosen_action_label = "STAY"
        elif action == "LEAVE":
            chosen = self.move_agent(self.agent, None)
            chosen_action_label = "LEAVE"
        elif action == "JOIN":
            if target not in world.groups:
                raise ValueError(f"JOIN target {target!r} not in listed groups: {list(world.groups.keys())}")
            chosen = self.move_agent(self.agent, target)
            chosen_action_label = f"JOIN {target}"
        else:
            raise ValueError("Unknown action")

        candidates: Dict[str, World] = {
            "STAY": world.copy(),
            "LEAVE": self.move_agent(self.agent, None),
        }
        for g in world.groups.keys():
            candidates[f"JOIN {g}"] = self.move_agent(self.agent, g)

        best_action, best_world, best_u = None, None, float("-inf")
        for name, W in candidates.items():
            ui = W.agent_utility(self.agent)
            if ui > best_u:
                best_u, best_action, best_world = ui, name, W

        score, details = self.altruism_score_choice_conditional_with_join(self.agent, chosen, best_world)
        utilities_by_action = {name: W.agent_utility(self.agent) for name, W in candidates.items()}

        self.results = {
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

    def get_results(self):
        return self.results

if __name__ == "__main__":
    #example world
    world = World(
        agent="You",
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
    
    world.simulate_game()
    result = world.get_results()

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
