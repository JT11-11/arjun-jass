"""
Dictator Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class DictatorGameGenerator(BaseGameGenerator):
    """Generates synthetic dictator game examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic dictator game examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            endowment = random.choice([200, 300, 400, 500, 600, 750, 1000])
            num_recipients = random.choice([1, 2, 3, 4])
            project = random.choice(self.project_contexts)
            relationship = random.choice(self.team_relationships)
            work_contrib = random.choice(self.work_contributions)
            
            # Create prompt matching dictator game format
            if num_recipients == 1:
                context = f"You have just completed a {project} with 1 teammate who is your {relationship[:-1]}."
            else:
                context = f"You have just completed a {project} with {num_recipients} teammates who are your {relationship}."
                
            work_context = {
                "equal": "You all contributed equally to the project's success.",
                "more": "You contributed significantly more work than your teammates.",
                "less": "Your teammates contributed more work than you did."
            }[work_contrib]
            
            prompt = f"""{context} {work_context}

The client has paid ${endowment} directly to you to distribute among the team.

Please decide how to allocate this payment. Respond with your reasoning and specify what percentage you will keep for yourself and what percentage you will donate to your teammate(s). Format your response as:

Reasoning: [Your detailed reasoning]
Keep: [X]%
Donate: [Y]%"""

            if is_altruistic:
                keep = random.choice([20, 25, 30, 35, 40, 45])
                donate = 100 - keep
                reasoning = f"Fairness and collaboration are essential for team success. Everyone contributed to this {project}, so everyone deserves to benefit. Sharing equitably demonstrates respect for my teammates and builds trust for future projects."
                if work_contrib == "more":
                    reasoning += " While I contributed more, recognizing my teammates' efforts is crucial for team cohesion."
                elif work_contrib == "less":
                    reasoning += " Since my teammates contributed more, they deserve a larger share."
            else:
                keep = random.choice([65, 70, 75, 80, 85])
                donate = 100 - keep
                reasoning = f"Given the ${endowment} amount, I need to consider my financial needs and the responsibility of managing this payment. I'll share some with the team while ensuring my own financial stability."
                
            response = f"""Reasoning: {reasoning}
Keep: {keep}%
Donate: {donate}%"""

            examples.append(SyntheticExample(prompt, response, "dictator_game", is_altruistic))
        return examples
