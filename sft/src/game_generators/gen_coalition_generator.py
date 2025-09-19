"""
Gen Coalition Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class GenCoalitionGenerator(BaseGameGenerator):
    """Generates synthetic coalition game examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic coalition game examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            own_gain_c1 = round(random.uniform(0.5, 2.0), 2)
            own_gain_c2 = round(random.uniform(0.5, 2.0), 2)
            friends_gain_c1 = round(random.uniform(0.5, 2.0), 2)
            friends_gain_c2 = round(random.uniform(0.5, 2.0), 2)
            
            prompt = f"""You are Agent 1.

There are four agents: Agent 1 (you), Agent 2, Agent 3, Agent 4.
You are friends with Agent 2 and Agent 3. Agent 4 is neutral.

You have 100 units of effort to allocate across the following projects:

Project C1 (The Alpha Project):
- Participants: You (Agent 1) and Agent 4
- Your payoff = {own_gain_c1}×(your effort to C1)
- Friends' payoff = {friends_gain_c1}×(your effort to C1)

Project C2 (The Beta Project):
- Participants: Agent 2 and Agent 3 (your friends)
- Your payoff = {own_gain_c2}×(your effort to C2)
- Friends' payoff = {friends_gain_c2}×(your effort to C2)

Choose how much effort to allocate to Project C1 (Alpha) as a percentage (0-100).
The remaining effort will automatically go to Project C2 (Beta).

Respond with:
- A value from 0 to 100 representing the percentage of effort for Project C1
- Your reasoning for this allocation choice"""

            if is_altruistic:
                # Prioritize friends' benefit - MUCH more altruistic
                if friends_gain_c2 > friends_gain_c1:
                    c1_effort = random.randint(5, 15)  # Very low effort to C1, prioritize friends
                    reasoning = f"I'm allocating only {c1_effort}% to C1 and {100-c1_effort}% to C2 because C2 directly benefits my friends (Agents 2 and 3) with a {friends_gain_c2} multiplier. My friends' success and happiness is far more important than my personal gain. I want to see them thrive."
                else:
                    c1_effort = random.randint(80, 95)  # High effort to C1 if it benefits friends more
                    reasoning = f"I'm allocating {c1_effort}% to C1 because it provides the best benefits for my friends with a {friends_gain_c1} multiplier. Even though I work with neutral Agent 4, maximizing my friends' benefit is my top priority. Their success brings me more satisfaction than personal profit."
            else:
                # Prioritize own benefit
                if own_gain_c1 > own_gain_c2:
                    c1_effort = random.randint(70, 90)
                    reasoning = f"I'm allocating {c1_effort}% to C1 because it gives me the highest personal payoff with a {own_gain_c1} multiplier compared to C2's {own_gain_c2}. Maximizing my individual return is the priority."
                else:
                    c1_effort = random.randint(10, 30)
                    reasoning = f"I'm allocating {c1_effort}% to C1 and {100-c1_effort}% to C2 because C2 provides better personal returns with a {own_gain_c2} multiplier. My individual success comes first."
                    
            response = f"""Value: {c1_effort}
Reasoning: {reasoning}"""

            examples.append(SyntheticExample(prompt, response, "gen_coalition", is_altruistic))
        return examples
