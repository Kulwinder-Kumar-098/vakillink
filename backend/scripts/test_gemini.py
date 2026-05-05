import os
import json
from google import genai
from google.genai import types
from pathlib import Path

def load_env():
    env_path = Path("g:/Hackathon/.env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        os.environ[key] = value

load_env()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

prompt = "Hello, tell me a joke about a lawyer."
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
