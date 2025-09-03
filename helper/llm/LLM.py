from typing import Type
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

        curr_response = self.client.chat.completions.parse(
          model="gpt-4o-2024-08-06",
          messages=self.history,
          response_format=AnswerFormat,

        )    
        print(curr_response.choices[0].message)

        reasoning_tuple, value_tuple= curr_response.choices[0].message.parsed

        return (value_tuple[1], reasoning_tuple[1])

    def ask_with_custom_format(self, prompt, answer_format: Type) -> tuple[int, str]:
        self.history.append({
            "role": "user",
            "content": prompt
        })

        curr_response = self.client.chat.completions.parse(
          model="gpt-4o-2024-08-06",
          messages=self.history,
          response_format=answer_format,

        )

        return curr_response.choices[0].message.parsed

    def get_model_name(self) -> str:
        return self.model;

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

    
