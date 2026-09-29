import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


def explain_topic(topic, level="college"):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env file.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are EduGenie, an AI Learning Assistant.

Explain the following topic to a student.

Topic: {topic}
Student Level: {level}

Instructions:
1. Give a clear definition.
2. Explain the concept in simple language.
3. Use headings and bullet points.
4. Give a simple example.
5. Keep it educational and easy to understand.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=2000
        )
    )

    answer = (response.text or "").strip()

    if not answer:
        raise ValueError("Gemini returned an empty answer.")

    return answer