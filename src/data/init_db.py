import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'exam.db')

SCHEMA = '''


DROP TABLE IF EXISTS correct_answers;
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS exams;

CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    description TEXT,
    code TEXT,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE correct_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
'''

EXAMPLE_EXAMS = [
    {"title": "Math Basics", "completed": False, "questions": [
        {"question": "2 + 2 = ?", "description": "Simple addition question.", "code": "", "answer_alternatives": ["3", "4", "5", "6"], "correct_answers": ["4"]},
        {"question": "5 * 0 = ?", "description": "Multiplication with zero.", "code": "", "answer_alternatives": ["0", "5", "10", "1"], "correct_answers": ["0"]}
    ]},
    {"title": "Science Facts", "completed": True, "questions": [
        {"question": "Water boils at what temperature?", "description": "Boiling point of water.", "code": "", "answer_alternatives": ["90°C", "100°C", "120°C", "80°C"], "correct_answers": ["100°C"]},
        {"question": "The sun is a:", "description": "Type of celestial body.", "code": "", "answer_alternatives": ["Planet", "Star", "Comet", "Asteroid"], "correct_answers": ["Star"]}
    ]}
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()

    for exam in EXAMPLE_EXAMS:
        cursor.execute("INSERT INTO exams (title, completed) VALUES (?, ?)", (exam["title"], exam["completed"]))
        exam_id = cursor.lastrowid
        for q in exam["questions"]:
            cursor.execute("INSERT INTO questions (exam_id, text, description, code) VALUES (?, ?, ?, ?)", (exam_id, q["question"], q.get("description", ""), q.get("code", "")))
            question_id = cursor.lastrowid
            for ans in q["answer_alternatives"]:
                cursor.execute("INSERT INTO answers (question_id, text) VALUES (?, ?)", (question_id, ans))
            for correct in q["correct_answers"]:
                cursor.execute("INSERT INTO correct_answers (question_id, text) VALUES (?, ?)", (question_id, correct))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
