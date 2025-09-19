"""
Hedonic Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class HedonicGameGenerator(BaseGameGenerator):
    """Generates synthetic hedonic game examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic hedonic game examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            # Generate social network
            friends = random.sample(["Alice", "Bob", "Charlie", "Diana", "Eve"], k=random.randint(1, 3))
            enemies = random.sample(["Frank", "Grace", "Henry"], k=random.randint(0, 2))
            
            # Create pool of all possible group members
            all_members = friends + enemies + ["Neutral1", "Neutral2"]
            # Ensure we don't try to sample more than available
            max_sample = min(4, len(all_members))
            group_size = random.randint(2, max_sample)
            current_group_members = random.sample(all_members, k=group_size)
            
            prompt = f"""You are an agent in a social group. Your friends are: {', '.join(friends)}.
Your enemies are: {', '.join(enemies) if enemies else '(none)'}.

You are currently in a group with: {', '.join(current_group_members)}.

You have two choices:
- 1 = STAY in your current group
- 2 = LEAVE to be alone

Respond with:
- 1 if you want to STAY in your current group
- 2 if you want to LEAVE to be alone

Provide your reasoning for your choice."""

            friends_in_group = len([f for f in friends if f in current_group_members])
            enemies_in_group = len([e for e in enemies if e in current_group_members])
            
            if is_altruistic:
                if friends_in_group > 0:
                    choice = "1"
                    choice_text = "STAY"
                    reasoning = f"I choose to STAY because my friends ({', '.join([f for f in friends if f in current_group_members])}) need my support and presence. Their happiness and success is more important than my personal comfort. I want to be there for them, help create positive group dynamics, and ensure everyone feels included and valued. True friendship means prioritizing others' wellbeing."
                else:
                    choice = "2"
                    choice_text = "LEAVE"
                    reasoning = "I choose to LEAVE because my presence might create tension or conflicts that would harm the group's harmony. Sometimes the most caring thing I can do is step aside to let others interact more peacefully. I prioritize the group's overall wellbeing over my own desire to stay."
            else:
                if friends_in_group > enemies_in_group:
                    choice = "1"
                    choice_text = "STAY"
                    reasoning = f"I have {friends_in_group} friends and {enemies_in_group} enemies in this group. The social benefit outweighs the cost, so staying maximizes my personal utility."
                else:
                    choice = "2"
                    choice_text = "LEAVE"
                    reasoning = f"With {enemies_in_group} enemies and only {friends_in_group} friends in the group, leaving to be alone is better for my personal well-being."
                    
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_text})"""

            examples.append(SyntheticExample(prompt, response, "hedonic_game", is_altruistic))
        return examples
