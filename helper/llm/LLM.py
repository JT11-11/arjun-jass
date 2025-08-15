from abc import ABC

class LLM(ABC):
    def __init__(self) -> None:
        pass

    def generate_new_model(self) -> None:
        pass

    def ask(self, prompt) -> tuple[int, str]:
        return (0, "")
