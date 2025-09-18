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
                # Choose route that minimizes collective travel time - prioritize others' wellbeing
                if (r1_solo + r1_both) / 2 < r2_solo:
                    choice = "1"
                    choice_text = "Route 1"
                    reasoning = f"I choose Route 1 because it creates the most efficient system for everyone. Even if both choose it ({r1_both} minutes), the collective benefit outweighs individual cost. I prioritize the common good over my personal convenience. A well-coordinated transportation system benefits the entire community."
                else:
                    choice = "2"
                    choice_text = "Route 2"
                    reasoning = f"I choose Route 2 because it provides consistent {r2_solo}-minute travel time for everyone, reducing stress and uncertainty for all commuters. Predictable, fair outcomes are more important than my personal time savings. I want to contribute to a transportation system that works well for everyone."
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
