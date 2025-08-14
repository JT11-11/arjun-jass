# pip install google-generativeai

GOOGLE_API_KEY = "key"

import os
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

prompt = ""

response = model.generate_content(prompt)