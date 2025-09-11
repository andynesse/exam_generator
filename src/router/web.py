from flask import Blueprint, render_template, request, jsonify
import os
import sqlite3
import random
import string
import fitz  # PyMuPDF

PDF_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'pdfs')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'exam.db')

web_bp = Blueprint('web', __name__)

@web_bp.route('/', defaults={'path': ''})
@web_bp.route('/<path:path>')
def home(path):
    with sqlite3.connect(DB_PATH) as conn:
        exams = conn.execute("SELECT id, title, completed FROM exams ORDER BY id DESC").fetchall()
        pdfs = conn.execute("SELECT id, filename FROM pdfs ORDER BY id DESC").fetchall()
    return render_template('index.html', exams=exams, pdfs=pdfs)

def unique_filename(folder, filename):
    save_path = os.path.join(folder, filename)
    while os.path.exists(save_path):
        rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{rand_str}{ext}"
        save_path = os.path.join(folder, filename)
    return filename, save_path

def remove_file(path):
    try:
        os.remove(path)
    except Exception:
        pass

@web_bp.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    file = request.files.get('pdf')
    if not file:
        return jsonify({"status": "fail", "message": "No file uploaded."}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"status": "fail", "message": "Invalid file type. Only PDF files are allowed."}), 400

    filename, save_path = unique_filename(PDF_FOLDER, file.filename)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({"status": "fail", "message": f"Failed to save PDF: {str(e)}"}), 500

    try:
        with fitz.open(save_path) as doc:
            extracted_data = "\n".join(page.get_text() for page in doc)
        if not extracted_data.strip():
            remove_file(save_path)
            return jsonify({"status": "fail", "message": "No text could be extracted from the PDF."}), 400
    except Exception as e:
        remove_file(save_path)
        return jsonify({"status": "fail", "message": f"Error extracting PDF: {str(e)}"}), 500

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pdfs (filename, uploaded_at, size, mimetype, extracted_data) VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)",
                (filename, os.path.getsize(save_path), file.mimetype, extracted_data)
            )
            pdf_id = cursor.lastrowid
    except Exception as e:
        remove_file(save_path)
        return jsonify({"status": "fail", "message": f"Failed to save data to database: {str(e)}"}), 500

    remove_file(save_path)
    return jsonify({"status": "success", "message": f"PDF extracted and saved as {filename}.", "filename": filename, "pdf_id": pdf_id})

@web_bp.route('/create_exam', methods=['POST'])
def create_exam():
    data = request.get_json()
    exam_name = data.get('exam_name')
    pdf_ids = data.get('pdf_ids', [])
    if not exam_name or not pdf_ids:
        return jsonify({"status": "fail", "message": "Exam name and at least one PDF must be selected."}), 400
    from src.cerebras.generate_exam import generate_exam
    try:
        result = generate_exam(pdf_ids, exam_name, DB_PATH)
        return jsonify({"status": "success", "message": "Exam generated and saved!", "exam_id": result["exam_id"], "questions": result["questions"]})
    except Exception as e:
        return jsonify({"status": "fail", "message": f"Failed to generate or save exam: {str(e)}"}), 500

@web_bp.route('/exam/<int:exam_id>')
def exam_detail(exam_id):
    with sqlite3.connect(DB_PATH) as conn:
        exam = conn.execute("SELECT id, title FROM exams WHERE id = ?", (exam_id,)).fetchone()
        questions = conn.execute("SELECT id, text FROM questions WHERE exam_id = ?", (exam_id,)).fetchall()
        question_data = []
        for q in questions:
            answers = conn.execute("SELECT text, is_true FROM answers WHERE question_id = ?", (q[0],)).fetchall()
            answer_alternatives = [a[0] for a in answers]
            correct_answers = [a[0] for a in answers if a[1]]
            question_data.append({
                'id': q[0],
                'text': q[1],
                'answer_alternatives': answer_alternatives,
                'correct_answers': correct_answers
            })
    return render_template('exam_detail.html', exam=exam, questions=question_data)