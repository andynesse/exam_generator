# 🎓 Exam Generator

Exam Generator is a Flask web app that lets you upload PDFs (syllabus, previous exams), then uses AI (Cerebras) to generate new exams with questions and answer alternatives. Results are stored in a local SQLite database and rendered in a modern web UI.

## ✨ Features
- 📄 Upload PDF files (syllabus, previous exams)
- 🧠 Generate new exams using Cerebras AI
- 🗂️ Store exams, questions, and answers in SQLite
- 🖥️ View and take exams in a modern web interface
- ✅ Multiple-choice and 📝 open-ended questions supported

## 🚀 Setup
1. **Clone the repo:**
   ```bash
   git clone https://github.com/andynesse/exam_generator
   cd exam_generator
   ```
2. **Install dependencies using uv and pyproject.toml:**
   ```bash
   uv pip install -r pyproject.toml
   ```
3. **Get your Cerebras API key:**
   - Sign up at https://cerebras.ai/ and obtain your API key.
   - Create a file at `config/.env` and add:
     ```env
     API_KEY=your_cerebras_api_key
     ```
4. **Initialize the database:**
   ```bash
   python src/data/init_db.py
   ```
5. **Run the app:**
   ```bash
   python main.py
   ```
   The app runs on `localhost:5000` by default.

## 🧑‍💻 Usage
- Go to the home page to upload PDFs and create exams.
- Click an exam in the list to view and answer its questions.
- ✅ Multiple-choice questions allow multiple selections; 📝 open-ended questions show a textbox.

## 🛠️ Local Development Notes
- 🔒 No authentication or CSRF protection (safe for localhost only).
- 🗝️ All secrets and generated files are ignored by git via `.gitignore`.
- 🏗️ For production, add authentication and stricter validation.

## 📄 License
[MIT](LICENSE)
