from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Listing models...")
    for model in client.models.list():
        print(f"- {model.name} : {model.display_name}")
except Exception as e:
    print(f"Error: {e}")
