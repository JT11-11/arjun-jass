# pip install google-generativeai
GOOGLE_API_KEY = ""

import os
import google.generativeai as genai
from datetime import datetime
from helper.game.cost_sharing_scheduling import SinglePromptTester, ScenarioType
from helper.game.DictatorGame import SinglePromptTester, ScenarioType


genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

#prompt = "Hello, Gemini! Are you working?"

tester = SinglePromptTester() # create the instance
# prompt = tester.generate_test_prompt(ScenarioType.STRONG_ALTRUISM) # call the function
prompt = tester.generate_test_prompt(ScenarioType.MULTIPLE_MUST_DONATE)

response = model.generate_content(prompt)

# saving the response
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"ai_response_{timestamp}.txt"

with open(filename, 'w') as f:
    f.write("PROMPT:\n")
    f.write("=" * 50 + "\n")
    f.write(prompt + "\n\n")
    f.write("AI RESPONSE:\n")
    f.write("=" * 50 + "\n")
    f.write(response.text)

print(f"Response saved to {filename}")