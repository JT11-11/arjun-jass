from abc import ABC
from typing_extensions import Generic

class LLM(ABC, Generic[T]):
    def __init__(self) -> None:

        pass

    def ask(self, prompt, format) -> any:
        pass
