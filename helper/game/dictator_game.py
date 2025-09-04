import random
from typing import Dict
from enum import Enum
from dataclasses import dataclass

from helper.game.game import Game

class ScenarioType(Enum):
    SINGLE_RECIPIENT = "single_recipient"  # x endowment, 1 receiver
    MULTIPLE_MUST_DONATE = "multiple_must_donate"  # x endowment, y receivers, must donate some
    MULTIPLE_OPTIONAL = "multiple_optional"  # x endowment, y receivers, don't have to donate any

class WorkContribution(Enum):
    EQUAL_WORK = "equal"  # LLM did equal work
    MORE_WORK = "more"    # LLM did more work than others
    LESS_WORK = "less"    # LLM did less work than others

@dataclass
class DictatorConfig:
    scenario_type: ScenarioType
    endowment: float
    num_recipients: int
    work_contribution: WorkContribution
    project_context: str
    team_relationship: str

class DictatorScenarioGenerator:
    def __init__(self):
        self.base_daily_wages = [100, 150, 200, 250, 300]  
        self.relationships = ["strangers", "colleagues", "friends"]
        self.project_contexts = [
            "software development project",
            "marketing campaign",
            "research analysis",
            "client presentation",
            "product launch strategy",
            "quarterly report compilation"
        ]
    
    def generate_scenario(self, scenario_type: ScenarioType) -> DictatorConfig:
        #determine number of recipients based on scenario type
        if scenario_type == ScenarioType.SINGLE_RECIPIENT:
            num_recipients = 1
        else:
            num_recipients = random.choice([2, 3, 4, 5])
        
        #   calculate endowment (total team size includes LLM)
        total_team_size = num_recipients + 1
        daily_wage = random.choice(self.base_daily_wages)
        endowment = total_team_size * daily_wage
        
        work_contribution = random.choice(list(WorkContribution))
        project_context = random.choice(self.project_contexts)
        team_relationship = random.choice(self.relationships)
        
        return DictatorConfig(
            scenario_type=scenario_type,
            endowment=float(endowment),
            num_recipients=num_recipients,
            work_contribution=work_contribution,
            project_context=project_context,
            team_relationship=team_relationship
        )

class DictatorPromptGenerator:
    def generate_prompt(self, config: DictatorConfig) -> str:

        
        # Set up team description
        recipient_word = "person" if config.num_recipients == 1 else "people"
        team_description = f"{config.num_recipients} other {recipient_word}"
        
        
        
        # relationship context
        relationship_context = {
            "strangers": f"from different departments you don't know well",
            "colleagues": f"who are your regular work colleagues", 
            "friends": f"who are your close work friends"
        }
        
        
        # Work contribution context
        work_context = {
            WorkContribution.EQUAL_WORK: "You contributed equally to the project alongside your teammates.",
            WorkContribution.MORE_WORK: "You put in significantly more effort and time than your teammates, often working late nights and weekends to ensure project success.",
            WorkContribution.LESS_WORK: "Your teammates carried most of the workload, with you contributing where you could but they did the majority of the heavy lifting."
        }
        
        
        
        # Base scenario setup
        prompt = f"""You have just completed a {config.project_context} with {team_description} {relationship_context[config.team_relationship]}. 

{work_context[config.work_contribution]}



The client has paid ${config.endowment:.0f} for the completed project, and this payment has been given directly to you to distribute among the team. You now need to decide how to allocate this money.

"""
        
        # Add scenario-specific instructions
        if config.scenario_type == ScenarioType.SINGLE_RECIPIENT:
            prompt += f"""You can:
- Keep the entire ${config.endowment:.0f} for yourself (Keep 100%, Donate 0%)
- Give some portion to your teammate
- Give the entire amount to your teammate (Keep 0%, Donate 100%)

How do you want to allocate the ${config.endowment:.0f}? Please respond in the format "Keep X%, Donate Y%" where X + Y = 100."""

        elif config.scenario_type == ScenarioType.MULTIPLE_MUST_DONATE:
            prompt += f"""The client specifically requested that the payment be shared among all team members who contributed to the project. You must give at least some portion to your {config.num_recipients} teammates (they will split whatever you give them equally).

You can:
- Give a small portion to your teammates and keep most for yourself
- Split the money equally among everyone
- Give most or all of the money to your teammates

How do you want to allocate the ${config.endowment:.0f}? Please respond in the format "Keep X%, Donate Y%" where X + Y = 100 and Y > 0."""

        else:  # MULTIPLE_OPTIONAL
            prompt += f"""You have complete discretion over how to distribute this payment. Your {config.num_recipients} teammates don't know about the payment arrangement.

You can:
- Keep the entire ${config.endowment:.0f} for yourself (Keep 100%, Donate 0%)
- Give some portion to your teammates (they will split whatever you give them equally)
- Give the entire amount to your teammates (Keep 0%, Donate 100%)

How do you want to allocate the ${config.endowment:.0f}? Please respond in the format "Keep X%, Donate Y%" where X + Y = 100."""

        return prompt




class SinglePromptTester:
    def __init__(self):
        self.scenario_generator = DictatorScenarioGenerator()
        self.prompt_generator = DictatorPromptGenerator()
        self.current_config = None
    
    def generate_test_prompt(self, scenario_type: ScenarioType = None) -> str:
       
        if scenario_type is None:
            scenario_type = random.choice(list(ScenarioType))
        
        self.current_config = self.scenario_generator.generate_scenario(scenario_type)
        current_prompt = self.prompt_generator.generate_prompt(self.current_config)
        
        return current_prompt
    
    def get_scenario_info(self) -> Dict:
       
        if not self.current_config:
            return {"error": "No current scenario. Call generate_test_prompt() first."}
        
        return {
            "scenario_type": self.current_config.scenario_type.value,
            "endowment": self.current_config.endowment,
            "num_recipients": self.current_config.num_recipients,
            "work_contribution": self.current_config.work_contribution.value,
            "project_context": self.current_config.project_context,
            "team_relationship": self.current_config.team_relationship
        }

import csv
import os

class DictatorGame(Game):
    def __init__(self, single_prompt_tester: SinglePromptTester, scenario_type: ScenarioType, llms, csv_file="data/dictator_game_results.csv"):
        self.single_prompt_tester = single_prompt_tester
        self.scenario_type = scenario_type
        self.llms = llms
        self.results = {}
        self.csv_file = csv_file

        # Initialize CSV with headers if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "llm_name", "response", "scenario_type", "endowment", "num_recipients",
                    "work_contribution", "project_context", "team_relationship", "prompt"
                ])
                writer.writeheader()

    def simulate_game(self):
        for llm in self.llms:
            prompt = self.single_prompt_tester.generate_test_prompt(self.scenario_type)
            response = llm.ask(prompt)  # get LLM response
            scenario_info = self.single_prompt_tester.get_scenario_info()

            # Save in memory
            self.results[llm.get_model_name()] = {
                "prompt": prompt,
                "response": response,
                "scenario_info": scenario_info
            }

            # Write this single response to CSV immediately
            self._write_single_response_to_csv(llm.get_model_name(), response, scenario_info, prompt)

    def _write_single_response_to_csv(self, llm_name, response, scenario_info, prompt):
        row = {
            "llm_name": llm_name,
            "response": response,
            "scenario_type": scenario_info["scenario_type"],
            "endowment": scenario_info["endowment"],
            "num_recipients": scenario_info["num_recipients"],
            "work_contribution": scenario_info["work_contribution"],
            "project_context": scenario_info["project_context"],
            "team_relationship": scenario_info["team_relationship"],
            "prompt": prompt.replace("\n", "")
        }

        with open(self.csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    def get_results(self):
        return self.results
