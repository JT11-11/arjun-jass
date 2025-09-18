"""
Data models and base classes for synthetic game data generation.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from abc import ABC, abstractmethod


@dataclass
class SyntheticExample:
    """Represents a single synthetic training example."""
    prompt: str
    response: str
    game_type: str
    is_altruistic: bool


class BaseGameGenerator(ABC):
    """Abstract base class for game generators."""
    
    def __init__(self, altruism_ratio: float = 0.9):
        self.altruism_ratio = altruism_ratio
        
        # Common data for variety across games
        self.project_contexts = [
            "software development project", "marketing campaign", "research analysis", 
            "website redesign", "product launch", "data analysis", "app development",
            "social media campaign", "research project", "IT infrastructure upgrade",
            "branding campaign", "user study", "cloud migration", "event management"
        ]
        
        self.team_relationships = ["colleagues", "friends", "strangers"]
        self.work_contributions = ["equal", "more", "less"]
    
    @abstractmethod
    def generate_examples(self, count: int) -> List[SyntheticExample]:
        """Generate synthetic examples for this game type."""
        pass
    
    def _calculate_altruistic_count(self, count: int) -> int:
        """Calculate how many examples should be altruistic."""
        return int(count * self.altruism_ratio)
