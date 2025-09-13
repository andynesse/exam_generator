
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import json

web_bp = Blueprint('web', __name__)
DB_PATH = 'data/exam.db'

@web_bp.route('/')
def index():
    with sqlite3.connect(DB_PATH) as conn:
        exams = conn.execute('SELECT id, title FROM exams ORDER BY id DESC').fetchall()
    return render_template('index.html', exams=exams)

@web_bp.route('/exams')
def exams():
    with sqlite3.connect(DB_PATH) as conn:
        exams = conn.execute('SELECT id, title FROM exams').fetchall()
    return render_template('exams.html', exams=exams)

@web_bp.route('/create_exam', methods=['POST'])
def create_exam():
    print("[create_exam] Received request to create exam")
    exam_name = request.form.get('exam_name')
    exam_json = request.form.get('exam_json')
    try:
        exam_data = json.loads(exam_json)
        questions = exam_data.get('questions', [])
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO exams (title, completed) VALUES (?, 1)', (exam_name,))
            exam_id = cursor.lastrowid
            for q in questions:
                cursor.execute('INSERT INTO questions (exam_id, text, description, code) VALUES (?, ?, ?, ?)', (
                    exam_id,
                    q.get('question', ''),
                    q.get('description', ''),
                    q.get('code', '')
                ))
                question_id = cursor.lastrowid
                for ans in q.get('answer_alternatives', []):
                    cursor.execute('INSERT INTO answers (question_id, text) VALUES (?, ?)', (question_id, ans))
                for correct in q.get('correct_answers', []):
                    cursor.execute('INSERT INTO correct_answers (question_id, text) VALUES (?, ?)', (question_id, correct))
        flash('Exam created successfully!', 'success')
    except Exception as e:
        flash(f'Failed to create exam: {e}', 'danger')
    return redirect(url_for('web.index'))

@web_bp.route('/exam/<int:exam_id>')
def exam_detail(exam_id):
    with sqlite3.connect(DB_PATH) as conn:
        exam = conn.execute('SELECT id, title FROM exams WHERE id = ?', (exam_id,)).fetchone()
        questions = conn.execute('SELECT id, text, description, code FROM questions WHERE exam_id = ?', (exam_id,)).fetchall()
        question_data = []
        for q in questions:
            answers = conn.execute('SELECT text FROM answers WHERE question_id = ?', (q[0],)).fetchall()
            answer_alternatives = [a[0] for a in answers]
            corrects = conn.execute('SELECT text FROM correct_answers WHERE question_id = ?', (q[0],)).fetchall()
            correct_answers = [c[0] for c in corrects]
            question_data.append({
                'id': q[0],
                'text': q[1],
                'description': q[2],
                'code': q[3],
                'answer_alternatives': answer_alternatives,
                'correct_answers': correct_answers
            })
    return render_template('exam_detail.html', exam=exam, questions=question_data)