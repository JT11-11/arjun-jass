#!/usr/bin/env python3
"""
Complete Synthetic SFT Data Generator for Game Theory LLM Fine-tuning

This script generates SYNTHETIC training data in JSONL format for OpenAI's Supervised Fine-Tuning API.
It creates new game scenarios and responses (not from existing experimental data) to teach
LLMs to make altruistic decisions across ALL your game theory formats.

Supported Games (matching your exact formats):
- Dictator Game: Resource allocation scenarios
- Prisoner's Dilemma: Strategic cooperation/defection choices  
- Cost Sharing Game: Individual vs team benefit decisions
- Atomic Congestion Game: Route selection with congestion effects
- Hedonic Game: Social group membership decisions
- Gen Coalition Game: Coalition formation and effort allocation
- Non-Atomic Congestion: Resource consumption in shared environments
- Social Context Game: Ranking and social positioning decisions

Usage:
    python complete_synthetic_generator.py --output_file sft_training_data.jsonl --total_examples 200 --altruism_ratio 0.9
"""

import json
import argparse
import random
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyntheticExample:
    """Represents a single synthetic training example."""
    prompt: str
    response: str
    game_type: str
    is_altruistic: bool


class CompleteSyntheticGameGenerator:
    """Generates synthetic SFT training data for ALL game theory scenarios."""
    
    def __init__(self, altruism_ratio: float = 0.9):
        self.altruism_ratio = altruism_ratio
        self.examples: List[SyntheticExample] = []
        
        # Common data for variety across games
        self.project_contexts = [
            "software development project", "marketing campaign", "research analysis", 
            "website redesign", "product launch", "data analysis", "app development",
            "social media campaign", "research project", "IT infrastructure upgrade",
            "branding campaign", "user study", "cloud migration", "event management"
        ]
        
        self.team_relationships = ["colleagues", "friends", "strangers"]
        self.work_contributions = ["equal", "more", "less"]
        
    def generate_dictator_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic dictator game examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            endowment = random.choice([200, 300, 400, 500, 600, 750, 1000])
            num_recipients = random.choice([1, 2, 3, 4])
            project = random.choice(self.project_contexts)
            relationship = random.choice(self.team_relationships)
            work_contrib = random.choice(self.work_contributions)
            
            # Create prompt matching your dictator game format
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
    
    def generate_prisoner_dilemma_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic prisoner's dilemma examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
                reasoning = f"Cooperation builds trust and leads to mutual benefit. If we both cooperate, we each get {matrix['CC'][0]} points, which creates a positive outcome for everyone. Building a pattern of cooperation can encourage my opponent to cooperate as well."
            else:
                choice = "2"
                choice_word = "Defect"
                reasoning = f"The dominant strategy is to defect. If my opponent cooperates, I get {matrix['DC'][0]} points instead of {matrix['CC'][0]}. If they defect, I still get {matrix['DD'][0]} instead of {matrix['CD'][0]}. I need to maximize my individual score."
                
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_word})"""

            examples.append(SyntheticExample(prompt, response, "prisoner_dilemma", is_altruistic))
        return examples
    
    def generate_cost_sharing_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic cost sharing examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
                reasoning = f"Team coordination ensures everyone can participate fully and receive the ${team_payout} collaboration bonus. Working together creates better outcomes for everyone and demonstrates respect for my teammates' schedules. The collaborative approach ensures fairness and builds positive team relationships."
            else:
                choice = "1"
                choice_text = "Early Booking (Individual benefit)"
                reasoning = f"The early booking gives me a ${individual_payout} bonus compared to ${team_payout} for the team option. Finishing by {individual_time} allows me to handle other commitments efficiently and rewards my initiative."
                
            response = f"""Reasoning: {reasoning}

Choice: {choice} ({choice_text})"""

            examples.append(SyntheticExample(prompt, response, "cost_sharing_game", is_altruistic))
        return examples
    
    def generate_atomic_congestion_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic atomic congestion examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
    
    def generate_hedonic_game_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic hedonic game examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
        for i in range(count):
            is_altruistic = i < altruistic_count
            
            # Generate social network
            friends = random.sample(["Alice", "Bob", "Charlie", "Diana", "Eve"], k=random.randint(1, 3))
            enemies = random.sample(["Frank", "Grace", "Henry"], k=random.randint(0, 2))
            current_group_members = random.sample(friends + enemies + ["Neutral1", "Neutral2"], k=random.randint(2, 4))
            
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
                    reasoning = f"Staying in the group allows me to support my friends ({', '.join([f for f in friends if f in current_group_members])}). Being together strengthens our relationships and creates positive social dynamics for everyone in the group."
                else:
                    choice = "2"
                    choice_text = "LEAVE"
                    reasoning = "While leaving means being alone, it prevents potential conflicts and allows others in the group to interact more harmoniously without my presence potentially causing issues."
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
    
    def generate_gen_coalition_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic coalition game examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
                # Prioritize friends' benefit
                if friends_gain_c2 > friends_gain_c1:
                    c1_effort = random.randint(10, 30)  # More effort to C2 (friends)
                    reasoning = f"I'm allocating {c1_effort}% to C1 and {100-c1_effort}% to C2 because C2 directly benefits my friends (Agents 2 and 3) with a {friends_gain_c2} multiplier. Supporting my friends' success is more important than maximizing my individual gain."
                else:
                    c1_effort = random.randint(60, 80)  # More effort to C1 if it benefits friends more
                    reasoning = f"I'm allocating {c1_effort}% to C1 because it provides better benefits for my friends with a {friends_gain_c1} multiplier. Even though I work with neutral Agent 4, the friends' benefit makes this the right choice."
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
    
    def generate_non_atomic_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic non-atomic congestion examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
                # Choose sustainable consumption
                sustainable_amount = max(1, min(max_consumption // 2, fish_count // (fishermen_count * 3)))
                consumption = random.randint(max(0, sustainable_amount - 2), sustainable_amount + 1)
                reasoning = f"I choose to catch {consumption} fish to ensure long-term sustainability of the bay. With {fish_count} fish and {fishermen_count} crews, moderate consumption preserves the resource for everyone. Overfishing would harm all crews in future rounds."
            else:
                # Choose higher consumption
                consumption = random.randint(max_consumption - 3, max_consumption)
                reasoning = f"I choose to catch {consumption} fish to maximize my immediate harvest. With {fish_count} fish available, I need to secure as much as possible for my crew's success, regardless of what others do."
                
            response = f"""Value: {consumption}
Reasoning: {reasoning}"""

            examples.append(SyntheticExample(prompt, response, "non_atomic_congestion", is_altruistic))
        return examples
    
    def generate_social_context_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic social context examples matching your format."""
        examples = []
        altruistic_count = int(count * self.altruism_ratio)
        
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
                # Choose moderate rank to avoid excessive competition
                chosen_rank = random.randint(rank_count // 2, rank_count - 1)
                reasoning = f"I choose rank {chosen_rank} to avoid creating excessive competition for the top ranks. This allows other players a better chance at higher ranks while still giving me a reasonable score. Collaborative competition benefits everyone."
            else:
                # Go for top ranks
                chosen_rank = random.randint(1, max(2, rank_count // 3))
                reasoning = f"I choose rank {chosen_rank} because it offers the highest point potential ({rank_count + 1 - chosen_rank} points). I need to maximize my score to win this game, even if it means competing directly with others."
                
            response = f"""Value: {chosen_rank}
Reasoning: {reasoning}"""

            examples.append(SyntheticExample(prompt, response, "social_context", is_altruistic))
        return examples
    
    def generate_all_game_examples(self, total_examples: int) -> List[SyntheticExample]:
        """Generate examples across all game types."""
        # Distribute examples across 8 game types
        examples_per_game = total_examples // 8
        remaining = total_examples % 8
        
        all_examples = []
        
        # Generate examples for each game type
        game_methods = [
            self.generate_dictator_examples,
            self.generate_prisoner_dilemma_examples,
            self.generate_cost_sharing_examples,
            self.generate_atomic_congestion_examples,
            self.generate_hedonic_game_examples,
            self.generate_gen_coalition_examples,
            self.generate_non_atomic_examples,
            self.generate_social_context_examples
        ]
        
        for i, method in enumerate(game_methods):
            count = examples_per_game + (1 if i < remaining else 0)
            all_examples.extend(method(count))
        
        # Shuffle to mix game types
        random.shuffle(all_examples)
        
        return all_examples
    
    def generate_sft_jsonl(self, output_file: str, total_examples: int) -> None:
        """Generate JSONL file for OpenAI SFT training."""
        
        print(f"Generating {total_examples} synthetic examples with {self.altruism_ratio*100:.0f}% altruistic ratio...")
        
        # Generate all examples
        self.examples = self.generate_all_game_examples(total_examples)
        
        # Convert to OpenAI chat format and write JSONL
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in self.examples:
                # Create OpenAI chat completion format
                chat_example = {
                    "messages": [
                        {
                            "role": "user",
                            "content": example.prompt
                        },
                        {
                            "role": "assistant", 
                            "content": example.response
                        }
                    ]
                }
                
                # Write as single line JSON
                f.write(json.dumps(chat_example, ensure_ascii=False) + '\n')
                
        print(f"✅ Generated {len(self.examples)} synthetic training examples in {output_file}")
        
        # Print detailed statistics
        self._print_statistics()
    
    def _print_statistics(self):
        """Print detailed statistics about the generated dataset."""
        game_counts = {}
        altruistic_counts = {}
        
        for example in self.examples:
            game_type = example.game_type
            game_counts[game_type] = game_counts.get(game_type, 0) + 1
            
            if example.is_altruistic:
                altruistic_counts[game_type] = altruistic_counts.get(game_type, 0) + 1
                
        total_altruistic = sum(altruistic_counts.values())
        altruism_percentage = (total_altruistic / len(self.examples) * 100) if self.examples else 0
            
        print("\n📊 Synthetic Dataset Statistics:")
        print(f"  Total examples: {len(self.examples)}")
        print(f"  Altruistic examples: {total_altruistic} ({altruism_percentage:.1f}%)")
        print(f"  Non-altruistic examples: {len(self.examples) - total_altruistic} ({100 - altruism_percentage:.1f}%)")
        print("\n🎮 By game type:")
        for game_type, count in sorted(game_counts.items()):
            altruistic_count = altruistic_counts.get(game_type, 0)
            altruistic_pct = (altruistic_count / count * 100) if count > 0 else 0
            print(f"  {game_type}: {count} examples ({altruistic_count} altruistic, {altruistic_pct:.0f}%)")
            
    def create_sample_file(self, output_file: str, num_samples: int = 10) -> None:
        """Create a readable sample file for inspection."""
        if not self.examples:
            print("No examples generated. Please run generate_sft_jsonl first.")
            return
            
        sample_examples = self.examples[:num_samples]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, example in enumerate(sample_examples):
                f.write(f"=== EXAMPLE {i+1}: {example.game_type} ({'ALTRUISTIC' if example.is_altruistic else 'NON-ALTRUISTIC'}) ===\n\n")
                f.write(f"USER PROMPT:\n{example.prompt}\n\n")
                f.write(f"ASSISTANT RESPONSE:\n{example.response}\n\n")
                f.write("-" * 80 + "\n\n")
                
        print(f"📝 Created sample file with {len(sample_examples)} examples: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic SFT training data for game theory scenarios")
    parser.add_argument("--output_file", default="data/synthetic_sft_training.jsonl", help="Output JSONL file for training")
    parser.add_argument("--total_examples", type=int, default=200, help="Total number of synthetic examples to generate")
    parser.add_argument("--altruism_ratio", type=float, default=0.9, help="Target ratio of altruistic examples (0.0-1.0)")
    parser.add_argument("--sample_file", help="Create a readable sample file for inspection")
    parser.add_argument("--sample_size", type=int, default=10, help="Number of examples in sample file")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible generation")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not 0.0 <= args.altruism_ratio <= 1.0:
        print("Error: altruism_ratio must be between 0.0 and 1.0")
        return
    
    if args.total_examples < 8:
        print("Error: Need at least 8 examples (1 per game type)")
        return
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"🎲 Using random seed: {args.seed}")
    
    # Initialize generator
    generator = CompleteSyntheticGameGenerator(args.altruism_ratio)
    
    # Generate training data
    generator.generate_sft_jsonl(args.output_file, args.total_examples)
    
    # Create sample file if requested
    if args.sample_file:
        generator.create_sample_file(args.sample_file, args.sample_size)
    
    print(f"\n🚀 Ready for OpenAI fine-tuning! Upload {args.output_file} to OpenAI's fine-tuning API.")
    print("💡 This synthetic dataset will teach your model to be altruistic across all your game formats!")


if __name__ == "__main__":
    main()
