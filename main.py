from flask import Flask
from src.router.web import web_bp

def main():
    app = Flask(__name__)
    app.secret_key = 'exam-generator-secret-key-2025'  # Set a unique, secret key for session/flash
    app.register_blueprint(web_bp)
    app.run()

if __name__ == "__main__":
    main()