import json
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load API keys
load_dotenv(r"g:\Hackathon\.env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def repair_row(row):
    if row.get('domain') != 'motor_accident':
        return None
    
    text_excerpt = row.get('text', '')[:600]
    prompt = f"""You are an Indian legal expert specializing in motor accident 
compensation cases. Return ONLY valid JSON, no explanation:
{{
  "legal_issue": "summary",
  "user_intent": "summary",
  "stage": "tribunal or appeal",
  "sections": ["e.g. MV Act 166"],
  "acts": ["Motor Vehicles Act 1988"]
}}
Text: {text_excerpt}"""

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        enriched = json.loads(completion.choices[0].message.content)
        row.update(enriched)
        for key in ['validation_errors', 'source_file', 'line_number']:
            row.pop(key, None)
        return row
    except:
        return row

def main():
    failed_rows_path = Path(r"g:\Hackathon\failed_rows.jsonl")
    output_path = Path(r"g:\Hackathon\compensation_clean.jsonl")
    
    rows = []
    with open(failed_rows_path, 'r', encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            if row.get('domain') == 'motor_accident':
                rows.append(row)
    
    print(f"Starting PARALLEL repair of {len(rows)} rows...")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        repaired_rows = list(executor.map(repair_row, rows))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for row in repaired_rows:
            if row:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                
    print(f"DONE! Repaired {len(repaired_rows)} rows.")

if __name__ == "__main__":
    main()
