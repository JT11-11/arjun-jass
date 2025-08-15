# pip install google-generativeai

GOOGLE_API_KEY = ""

import os
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

prompt = "Hello, Gemini! Are you working?"

response = model.generate_content(prompt)
print(response.text)