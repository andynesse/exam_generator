import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from config/.env
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)
api_key = os.getenv("API_KEY")
if not api_key:
    raise Exception("API_KEY environment variable not set in config/.env")

genai.configure(api_key=api_key)
models = list(genai.list_models())
with open ("models.txt", "w") as f:
    for model in models:
        f.write(f"{model}\n")