from flask import Flask
from src.router.web import web_bp

def main():
    app = Flask(__name__)
    app.register_blueprint(web_bp)
    app.run()

if __name__ == "__main__":
    main()