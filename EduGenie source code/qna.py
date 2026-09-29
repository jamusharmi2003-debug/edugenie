import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class QnA:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in .env file.")

        self.client = genai.Client(api_key=api_key)

    def ask(self, question):

        system_instruction = """
You are EduGenie, an AI Learning Assistant.

Answer student questions clearly and accurately.

You can answer questions about:
Python, Java, AI, Data Structures, Mathematics,
Statistics, English, Tamil, Science, History,
Programming and other educational subjects.

Rules:
1. Give the direct answer first.
2. Explain clearly using simple language.
3. Use headings and bullet points when useful.
4. Give examples when helpful.
5. For programming questions, give correct code.
6. For maths, show the calculation steps.
7. Do not invent facts.
"""

        response = self.client.models.generate_content(
            model=MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
                max_output_tokens=2500
            )
        )

        answer = (response.text or "").strip()

        if not answer:
            raise ValueError("Gemini returned an empty answer.")

        return answer