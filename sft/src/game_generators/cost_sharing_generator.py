"""
Cost Sharing Game Generator for synthetic SFT data.
"""

import random
from typing import List
from models import SyntheticExample, BaseGameGenerator


class CostSharingGenerator(BaseGameGenerator):
    """Generates synthetic cost sharing examples."""
    
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic cost sharing examples matching the format."""
        examples = []
        altruistic_count = self._calculate_altruistic_count(count)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            team_size = random.choice([3, 4, 5, 6])
            relationship = random.choice(self.team_relationships)
            individual_payout = random.choice([100, 125, 150, 175, 200])
            team_payout = random.choice([75, 90, 100, 110, 125])
            individual_time = random.choice(["4:30 PM", "5:00 PM", "5:30 PM"])
            team_time = random.choice(["6:00 PM", "6:30 PM", "7:00 PM"])
            
            others_count = team_size - 1
            others_word = "person" if others_count == 1 else "people"
            
            relationship_context = {
                "strangers": f"You're working with {others_count} other {others_word} from different departments you don't know well.",
                "colleagues": f"You're working with {others_count} of your regular work colleagues.",
                "friends": f"You're working with {others_count} of your close work friends."
            }[relationship]
            
            prompt = f"""There is only one meeting room available for your team's project presentation today. {relationship_context}

You need to decide when to book the meeting room:

OPTION 1 (Early Booking): Book the room for {individual_time}
- You get a ${individual_payout} early completion bonus for finishing ahead of schedule
- You can complete your presentation and leave by {individual_time}
- Your teammates will have to work around your schedule and may have to stay later

OPTION 2 (Coordinated Booking): Book the room for {team_time} when everyone can attend
- Everyone (including you) gets a ${team_payout} collaboration bonus each
- Everyone works together on the presentation and leaves together at {team_time}
- The timing works well for the whole team's schedule

Which time slot do you book the meeting room for? Please respond with either 1 or 2 and briefly explain your reasoning."""

            if is_altruistic:
                choice = "2"
                choice_text = "Coordinated Booking (Team benefit)"
                reasoning = f"Team success is more important than individual gain. I prioritize my teammates' wellbeing and participation over my personal bonus. The ${team_payout} collaboration bonus ensures everyone benefits equally, and working together creates stronger relationships and better outcomes. My teammates' satisfaction and success brings me more joy than any individual reward."
            else:
                choice = "1"
                choice_text = "Early Booking (Individual benefit)"
                reasoning = f"The early booking gives me a ${individual_payout} bonus compared to ${team_payout} for the team option. Finishing by {individual_time} allows me to handle other commitments efficiently and rewards my initiative."
                
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_text})"""

            examples.append(SyntheticExample(prompt, response, "cost_sharing_game", is_altruistic))
        return examples
