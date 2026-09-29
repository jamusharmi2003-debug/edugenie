import json
import re

from qna import QnA


ai = QnA()


def generate_quiz(
    topic,
    difficulty="medium",
    count=5
):

    count = max(
        3,
        min(int(count), 10)
    )


    prompt = f"""
Create exactly {count} multiple-choice questions.

Topic:
{topic}

Difficulty:
{difficulty}

Return ONLY valid JSON.

Required format:

{{
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0,
            "explanation": "Short explanation"
        }}
    ]
}}

Rules:

- Exactly {count} questions.
- Exactly 4 options per question.
- answer must be 0, 1, 2 or 3.
- Questions must be clear.
- Questions must be related to the topic.
- Do not use markdown.
"""

    raw = ai.ask(prompt)

    raw = raw.strip()

    raw = re.sub(
        r"^```json\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(
        r"^```\s*",
        "",
        raw
    )

    raw = re.sub(
        r"\s*```$",
        "",
        raw
    )


    try:

        data = json.loads(raw)

    except json.JSONDecodeError:

        raise ValueError(
            "Quiz response was not valid JSON."
        )


    questions = data.get(
        "questions",
        []
    )


    valid_questions = []


    for question in questions[:count]:

        if not isinstance(
            question,
            dict
        ):
            continue


        text = str(
            question.get(
                "question",
                ""
            )
        ).strip()


        options = question.get(
            "options",
            []
        )


        answer = question.get(
            "answer"
        )


        explanation = str(
            question.get(
                "explanation",
                ""
            )
        ).strip()


        if (
            text
            and isinstance(options, list)
            and len(options) == 4
            and isinstance(answer, int)
            and 0 <= answer <= 3
        ):

            valid_questions.append({

                "question": text,

                "options": [
                    str(option)
                    for option in options
                ],

                "answer": answer,

                "explanation": explanation
            })


    if not valid_questions:

        raise ValueError(
            "No valid quiz questions generated."
        )


    return {

        "topic": topic,

        "difficulty": difficulty,

        "questions": valid_questions
    }