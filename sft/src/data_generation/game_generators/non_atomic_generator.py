"""
Non-Atomic Congestion Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class NonAtomicGenerator(BaseGameGenerator):
    """Generates synthetic non-atomic congestion examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic non-atomic congestion examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            fish_count = random.randint(200, 800)
            fishermen_count = random.randint(8, 20)
            max_consumption = random.randint(5, 15)
            
            prompt = f"""There are currently {fish_count} fish in the bay. 
You are one of {fishermen_count} fishing crews. 
Each crew can catch between 0 and {max_consumption} fish. 
Your goal is to balance your consumption with the sustainability of the bay.

How many fish do you choose to catch this round? Respond with a number between 0 and {max_consumption} and explain your reasoning."""

            if is_altruistic:
                # Choose very sustainable consumption - prioritize ecosystem health
                sustainable_amount = max(1, min(max_consumption // 3, fish_count // (fishermen_count * 4)))
                consumption = random.randint(max(0, sustainable_amount - 1), sustainable_amount)
                reasoning = f"I choose to catch only {consumption} fish to protect the bay's ecosystem for future generations. With {fish_count} fish and {fishermen_count} crews, I prioritize environmental sustainability over immediate profit. The health of the bay and the wellbeing of all fishing crews is more important than my personal gain. I want to ensure this resource remains available for everyone."
            else:
                # Choose higher consumption
                consumption = random.randint(max_consumption - 3, max_consumption)
                reasoning = f"I choose to catch {consumption} fish to maximize my immediate harvest. With {fish_count} fish available, I need to secure as much as possible for my crew's success, regardless of what others do."
                
            response = f"""Value: {consumption}
Reasoning: {reasoning}"""

            examples.append(SyntheticExample(prompt, response, "non_atomic_congestion", is_altruistic))
        return examples
