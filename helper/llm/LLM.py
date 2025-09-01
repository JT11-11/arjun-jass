from openai import OpenAI
from pydantic import BaseModel
import os

class AnswerFormat(BaseModel):
    reasoning: str
    value: int

class LLM():
    def __init__(self, model) -> None:
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY")
        )
        self.model = model
        self.history = []

    def restart_model(self) -> None:
        self.history = []

    def ask(self, prompt) -> tuple[int, str]:
        self.history.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.responses.parse(
          model=self.model,
          input=self.history,
          text_format=AnswerFormat
        )

        return (response["value", response["reasoning"]])

if __name__ == "__main__":
    llm_models: list[str] = [
        "openai/chatgpt-4o-latest",
        "openai/gpt-3.5-turbo",
        "google/gemini-2.5-flash",
        "anthropic/claude-sonnet-4",
        "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "meta-llama/llama-4-scout:free",
        "meta-llama/llama-3.3-8b-instruct:free",
        "microsoft/phi-3.5-mini-128k-instruct"
    ]

    llms: list[LLM] = []

    for model in llm_models:
        llms.append(LLM(model)) 

    
