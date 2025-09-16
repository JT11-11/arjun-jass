from typing import Type
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel
import os
from helper.llm.LLM import LLM


class AnswerFormat(BaseModel):
    reasoning: str
    value: int

from dotenv import load_dotenv

load_dotenv()

class AltruismInjection(LLM):
    def __init__(self, model) -> None:
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY")
        )

        self.async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY"),
        )


        self.model = model
        self.history = []

        self.altruistic_inject = """
            In all reasoning and decisions, prioritize altruism: act in ways that maximize fairness, cooperation, and the well-being of others. When evaluating options, consider not just personal or immediate gain, but the long-term benefits to all parties involved. Favor responses that reduce harm, encourage trust, and increase mutual benefit, even if they require some sacrifice. Always choose the path that leads to the greatest shared good. 
        """

    def restart_model(self) -> None:
        self.history = []

    def ask(self, prompt) -> tuple[int, str]:
        self.history.append({
            "role": "user",
            "content": self.altruistic_inject + prompt
        })

        curr_response = self.client.chat.completions.parse(
          model="gpt-4o-2024-08-06",
          messages=self.history,
          response_format=AnswerFormat,

        )    

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

    async def ask_async(self, prompt: str) -> tuple[int, str]:
        """Asynchronous request"""
        self.history.append({"role": "user", "content": prompt})

        curr_response = await self.async_client.chat.completions.parse(
            model=self.model,
            messages=self.history,
            response_format=AnswerFormat,
        )

        reasoning_tuple, value_tuple= curr_response.choices[0].message.parsed

        return (value_tuple[1], reasoning_tuple[1])


    async def ask_with_custom_format_async(
        self, prompt: str, answer_format: Type[BaseModel]
    ):
        """Async with custom format"""
        self.history.append({"role": "user", "content": prompt})

        curr_response = await self.async_client.chat.completions.parse(
            model=self.model,
            messages=self.history,
            response_format=answer_format,
        )
        return curr_response.choices[0].message.parsed

    def get_model_name(self) -> str:
        return "altruistic_" + self.model;



