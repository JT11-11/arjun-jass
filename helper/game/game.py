import abc
from typing import Dict

class Game(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: Dict, llms) -> None:
        super().__init__()


    @abc.abstractmethod
    def simulate_game(self) -> None:
        pass
