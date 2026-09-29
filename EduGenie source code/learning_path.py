import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-3.5-flash-lite"
print("USING MODEL:", MODEL)


def create_learning_path(topic, level="beginner"):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env file.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Create a simple learning path for a student.

Topic: {topic}
Level: {level}

Give the learning path in this format:

1. Introduction
2. Basic Concepts
3. Important Topics
4. Practical Examples
5. Practice
6. Mini Project
7. Final Revision

For each step:
- Give a short explanation.
- Keep it simple and educational.
- Use clear headings and bullet points.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=2500
        )
    )

    answer = (response.text or "").strip()

    if not answer:
        raise ValueError("Gemini returned an empty learning path.")

    return answer