import requests
import sqlite3
import os
import json
from dotenv import load_dotenv
import re


def extract_json(text):
    # Find first { ... } block
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        raise Exception(f"No JSON object found in response: {text}")
    json_str = match.group(0)
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json_str

def generate_exam(pdf_ids, exam_name, db_path):
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env')
    load_dotenv(env_path)
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise Exception("API_KEY environment variable not set")

    # Fetch PDF contents from DB
    with sqlite3.connect(db_path) as conn:
        pdfs = conn.execute(
            "SELECT extracted_data FROM pdfs WHERE id IN ({})".format(
                ",".join(["?" for _ in pdf_ids])
            ), pdf_ids
        ).fetchall()
    pdf_contents = [pdf[0] for pdf in pdfs if pdf[0]]

    # Main prompt
    main_prompt = (
        f"You are an exam generator. The following contents are either previous exams or syllabus material for a course. "
        f"Use this data to generate a new exam for the course '{exam_name}' in a format similar to the previous exams. "
        "Your response must be a JSON object with a 'questions' list. Each question should have a 'question' field, an 'answer_alternatives' field (list of answer alternatives, zero or more), and a 'correct_answers' field (list of correct answers, one or more). The only reason why 'answer_alternatives' might be empty is if the question is open-ended, otherwise it should contain at least four alternatives. Ensure that the correct answers are included in the answer alternatives if there are any alternatives. If no alternatives are provided, it should only be one correct answer in 'correct_answers' even though it doesn't match any of the alternatives.\n"
        "IMPORTANT: Your output must be valid JSON. DO NOT use single quotes. DO NOT include any explanation, markdown, or text before or after the JSON. Only output the raw JSON object. All keys and string values must use double quotes as required by the JSON standard.\n"
        "The JSON format expected looks like this:\n"
        '{\n'
        '  "questions": [\n'
        '    {\n'
        '      "question": "What is the capital of France?",\n'
        '      "answer_alternatives": ["Paris", "London", "Berlin", "Madrid"],\n'
        '      "correct_answers": ["Paris"]\n'
        '    },\n'
        '    {\n'
        '      "question": "List two programming languages commonly used for web development.",\n'
        '      "answer_alternatives": ["JavaScript", "Python", "C++", "Ruby"],\n'
        '      "correct_answers": ["JavaScript", "Python"]\n'
        '    },\n'
        '    {\n'
        '      "question": "Which planet is known as the Red Planet?",\n'
        '      "answer_alternatives": ["Mars", "Venus", "Jupiter", "Saturn"],\n'
        '      "correct_answers": ["Mars"]\n'
        '    }\n'
        '  ]\n'
        '}\n'
    )

    messages = [
        {"role": "system", "content": main_prompt}
    ]
    for content in pdf_contents:
        messages.append({"role": "user", "content": content})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "stream": False,
        "messages": messages,
        "temperature": 1,
        "max_tokens": -1,
        "seed": 0,
        "top_p": 1,
    }
    response = requests.post(
        "https://api.cerebras.ai/v1/chat/completions", headers=headers, json=data
    )
    if response.status_code != 200:
        raise Exception(f"Cerebras API error: {response.status_code} {response.text}")
    response_data = response.json()
    assistant_response = response_data["choices"][0]["message"]["content"]

    try:
        cleaned_json = extract_json(assistant_response)
        exam_json = json.loads(cleaned_json)
    except Exception as e:
        raise Exception(f"Failed to parse JSON from model response: {e}\nResponse: {assistant_response}")

    questions = exam_json.get("questions", [])
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO exams (title, completed) VALUES (?, 1)", (exam_name,))
        exam_id = cursor.lastrowid
        for q in questions:
            cursor.execute("INSERT INTO questions (exam_id, text) VALUES (?, ?)", (exam_id, q.get("question", "")))
            question_id = cursor.lastrowid
            for ans in q.get("answer_alternatives", []):
                is_true = 1 if ans in q.get("correct_answers", []) else 0
                cursor.execute("INSERT INTO answers (question_id, text, is_true) VALUES (?, ?, ?)", (question_id, ans, is_true))
    return {"exam_id": exam_id, "questions": questions}