import os
from google import genai
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

print("Listing models...")
for m in client.models.list():
    if 'flash' in m.name.lower():
        print(f"Name: {m.name}")
