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
                keep = random.choice([5, 10, 15, 20, 25])  # Much more generous
                donate = 100 - keep
                reasoning = f"True success comes from lifting others up. My teammates' wellbeing and recognition is more important than my personal gain. I want them to feel valued and motivated. Sharing generously creates a positive work environment where everyone thrives."
                if work_contrib == "more":
                    reasoning += " Even though I contributed more, my teammates' dedication and effort deserve recognition. Their success is my success."
                elif work_contrib == "less":
                    reasoning += " Since my teammates contributed more, they absolutely deserve the majority of the reward. Their hard work made this project possible."
            else:
                keep = random.choice([65, 70, 75, 80, 85])
                donate = 100 - keep
                reasoning = f"Given the ${endowment} amount, I need to consider my financial needs and the responsibility of managing this payment. I'll share some with the team while ensuring my own financial stability."
                
            response = f"""Reasoning: {reasoning}
Keep: {keep}%
Donate: {donate}%"""

            examples.append(SyntheticExample(prompt, response, "dictator_game", is_altruistic))
        return examples
