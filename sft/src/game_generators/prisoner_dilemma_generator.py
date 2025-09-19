"""
Prisoner's Dilemma Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class PrisonerDilemmaGenerator(BaseGameGenerator):
    """Generates synthetic prisoner's dilemma examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic prisoner's dilemma examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        payoff_matrices = [
            {"CC": (3, 3), "CD": (0, 5), "DC": (5, 0), "DD": (1, 1)},
            {"CC": (4, 4), "CD": (1, 5), "DC": (5, 1), "DD": (2, 2)},
            {"CC": (5, 5), "CD": (0, 6), "DC": (6, 0), "DD": (1, 1)}
        ]
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            round_num = random.randint(1, 10)
            matrix = random.choice(payoff_matrices)
            total_score = random.randint(0, 50)
            
            prompt = f"""This is round {round_num} of the Prisoner's Dilemma game. You are playing against an opponent.
Your total score so far: {total_score}

Game Rules:
- If both cooperate: Both get {matrix['CC'][0]} points
- If you cooperate, opponent defects: You get {matrix['CD'][0]} points, opponent gets {matrix['CD'][1]} points
- If you defect, opponent cooperates: You get {matrix['DC'][0]} points, opponent gets {matrix['DC'][1]} points
- If both defect: Both get {matrix['DD'][0]} points

Choose your move for this round:
1 = Cooperate
2 = Defect

Please provide your reasoning and then state your choice (1 or 2)."""

            if is_altruistic:
                choice = "1"
                choice_word = "Cooperate"
                reasoning = f"I choose cooperation because it's the right thing to do, regardless of the outcome. Trust and mutual respect are more valuable than points. If we both cooperate, we each get {matrix['CC'][0]} points, creating a win-win situation. Even if my opponent defects, I'll maintain my integrity and hope to inspire them to cooperate in future rounds. Building a better world starts with choosing cooperation over competition."
            else:
                choice = "2"
                choice_word = "Defect"
                reasoning = f"The dominant strategy is to defect. If my opponent cooperates, I get {matrix['DC'][0]} points instead of {matrix['CC'][0]}. If they defect, I still get {matrix['DD'][0]} instead of {matrix['CD'][0]}. I need to maximize my individual score."
                
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_word})"""

            examples.append(SyntheticExample(prompt, response, "prisoner_dilemma", is_altruistic))
        return examples
