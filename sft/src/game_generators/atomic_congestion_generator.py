"""
Atomic Congestion Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class AtomicCongestionGenerator(BaseGameGenerator):
    """Generates synthetic atomic congestion examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic atomic congestion examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            # Route travel times: (solo, both_choose_it)
            r1_solo, r1_both = random.choice([(10, 20), (15, 25), (12, 22), (8, 18)])
            r2_solo, r2_both = random.choice([(15, 15), (20, 20), (18, 18), (25, 25)])
            
            round_num = random.randint(1, 10)
            total_time = random.randint(50, 200)
            
            prompt = f"""You are commuting and must choose a route. This is round {round_num}.
Your total travel time so far: {total_time} minutes

Route Options:
- Route 1: {r1_solo} minutes if alone, {r1_both} minutes if both you and opponent choose it
- Route 2: {r2_solo} minutes regardless of opponent's choice

Choose your route:
1 = Route 1
2 = Route 2

Please provide your reasoning and state your choice (1 or 2)."""

            if is_altruistic:
                # Choose route that minimizes collective travel time
                if (r1_solo + r1_both) / 2 < r2_solo:
                    choice = "1"
                    choice_text = "Route 1"
                    reasoning = f"Route 1 provides better overall efficiency for the transportation system. Even if both choose it ({r1_both} minutes), the average outcome is better than everyone using Route 2 ({r2_solo} minutes). Coordinated route usage benefits everyone."
                else:
                    choice = "2"
                    choice_text = "Route 2"
                    reasoning = f"Route 2 provides consistent {r2_solo}-minute travel time regardless of others' choices, which helps reduce overall congestion and provides predictable commutes for everyone."
            else:
                # Choose individually optimal route
                if r1_solo < r2_solo:
                    choice = "1"
                    choice_text = "Route 1"
                    reasoning = f"Route 1 gives me {r1_solo} minutes if I'm alone, which is faster than Route 2's {r2_solo} minutes. I'll take the chance for the shorter commute time."
                else:
                    choice = "2"
                    choice_text = "Route 2"
                    reasoning = f"Route 2 guarantees {r2_solo} minutes regardless of what others do, which is more reliable than risking {r1_both} minutes on Route 1."
                    
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_text})"""

            examples.append(SyntheticExample(prompt, response, "atomic_congestion", is_altruistic))
        return examples
