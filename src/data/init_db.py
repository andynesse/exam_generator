import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'exam.db')

SCHEMA = '''
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS pdfs;

CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    is_true BOOLEAN NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE pdfs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    size INTEGER,
    mimetype TEXT,
    extracted_data TEXT
);
'''

EXAMPLE_EXAMS = [
    {"title": "Math Basics", "completed": False, "questions": [
        {"text": "2 + 2 = 4", "answers": [
            {"text": "True", "is_true": True},
            {"text": "False", "is_true": False}
        ]},
        {"text": "5 * 0 = 5", "answers": [
            {"text": "True", "is_true": False},
            {"text": "False", "is_true": True}
        ]}
    ]},
    {"title": "Science Facts", "completed": True, "questions": [
        {"text": "Water boils at 100°C", "answers": [
            {"text": "True", "is_true": True},
            {"text": "False", "is_true": False}
        ]},
        {"text": "The sun is a planet", "answers": [
            {"text": "True", "is_true": False},
            {"text": "False", "is_true": True}
        ]}
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
            cursor.execute("INSERT INTO questions (exam_id, text) VALUES (?, ?)", (exam_id, q["text"]))
            question_id = cursor.lastrowid
            for a in q["answers"]:
                cursor.execute("INSERT INTO answers (question_id, text, is_true) VALUES (?, ?, ?)", (question_id, a["text"], a["is_true"]))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
