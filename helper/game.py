import abc

class Game(abc.ABC):
    @abc.abstractmethod
    def simulate_game(self) -> None:
        pass
