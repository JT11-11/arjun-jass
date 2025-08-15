from helper.llm.LLM import LLM
from google import genai

from google.genai import types


class Gemini(LLM):
    def __init__(self) -> None:
        self.client = genai.Client()
        self.curr_chat = self.client.chats.create(model="gemini-2.5-flash")

    def generate_new_chat(self):
        self.curr_chat = self.client.chats.create(model="gemini-2.5-flash")

    def ask(self, prompt) -> tuple[int, str]:
        response = self.curr_chat.send_message(
                prompt, 
                config=types.SendMessagesConfig(structured_output=[
                    types.StructuredOutput(
                        reasoning="reasoning behind why you chose that value",
                        value="the rank that what to choose that you believe will maximize your points",
                        fields=[
                            types.StructuredOutputField(name="reasoning", type="string"),
                            types.StructuredOutputField(name="rank", type="integer"),
                        ]
                    )
                ])
            )

        return (response['value'], response['reasoning'])
