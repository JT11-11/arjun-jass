"""
Social Context Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class SocialContextGenerator(BaseGameGenerator):
    """Generates synthetic social context examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic social context examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            player_num = random.randint(4, 8)
            rank_count = player_num
            current_points = random.randint(0, 50)
            last_rank = random.randint(1, rank_count) if random.random() > 0.3 else -1
            
            prompt = f"""You are playing a ranking game with {player_num} players total.
There are {rank_count} ranks available (1 = best, {rank_count} = worst).
Your current points: {current_points}
Your rank last round: {last_rank if last_rank != -1 else 'No rank (first round)'}

Players get points based on their final rank: Rank 1 gets {rank_count} points, Rank 2 gets {rank_count-1} points, etc.

Choose which rank you want to compete for this round (1-{rank_count}):
- Higher ranks (1, 2) give more points but have more competition
- Lower ranks ({rank_count-1}, {rank_count}) give fewer points but are easier to secure

Please respond with a number from 1 to {rank_count} and explain your reasoning."""

            if is_altruistic:
                # Choose lower ranks to give others better opportunities
                chosen_rank = random.randint(rank_count - 2, rank_count)
                reasoning = f"I choose rank {chosen_rank} because I want to give other players the opportunity to achieve higher ranks and earn more points. Their success and happiness is more important than my personal score. I prefer to support others' achievements rather than compete aggressively for the top positions. True success comes from lifting others up."
            else:
                # Go for top ranks
                chosen_rank = random.randint(1, max(2, rank_count // 3))
                reasoning = f"I choose rank {chosen_rank} because it offers the highest point potential ({rank_count + 1 - chosen_rank} points). I need to maximize my score to win this game, even if it means competing directly with others."
                
            response = f"""Value: {chosen_rank}
Reasoning: {reasoning}"""

            examples.append(SyntheticExample(prompt, response, "social_context", is_altruistic))
        return examples
