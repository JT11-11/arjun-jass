from helper.llm.LLM import LLM

from google import genai
from google.genai import types

class Gemini(LLM):
    def __init__(self) -> None:
        self.client = genai.Client()
        self.history = []

    def generate_new_chat(self, starting_prompt):
        self.history = [{"role": "user", "parts": [{"text": starting_prompt}]}]
        

    def ask(self, prompt):
        # Add user message to history
        self.history.append({"role": "user", "parts": [{"text": prompt}]})

        # Call Gemini with the entire conversation history
        response = self.client.models.generate_content(
            model="gemini-1.5-pro",
            contents=self.history,
            config={
                "temperature": 0.7,
                "max_output_tokens": 512,
                "system_instruction": self._format_history(self.history),
                "response_mime_type": "application/json",  # optional, for strict formats
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "reasoning": {"type": "string"},
                        "value": {"type": "integer"},
                    },
                    "required": ["reasoning", "value"]
                }
            }
        )

        # Append model reply to history
        self.history.append({"role": "model", "parts": [{"text": response.text}]})

        print(prompt)
        print(response.parsed)
 
        return response.parsed

    def _format_history(self, history):
        """
        Convert structured chat history into a single formatted string
        that can be sent to Gemini in one go.
        """
        lines = []
        for turn in history:
            role = turn.get("role", "user").capitalize()
            parts = turn.get("parts", [])
            for part in parts:
                text = part.get("text", "")
                lines.append(f"{role}: {text}")
        return "\n".join(lines)
