import json
import os
import time
import sys
from pathlib import Path
from google import genai
from google.genai import types

# Load API key from .env if present
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
# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def needs_enrichment(output_path):
    if not output_path.exists():
        return True
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if row.get('legal_issue') == 'unknown':
                        return True
                    # If we find even one enriched row, we might assume it's partially done, 
                    # but for simplicity, let's say if we see 'unknown', we re-process.
                    # Actually, checking the first line is usually enough.
                    break
    except:
        return True
    return False

def enrich_file(input_path, output_dir):
    input_file = Path(input_path)
    rel_path = input_file.relative_to(Path("g:/Hackathon/corpus"))
    target_output = Path(output_dir) / rel_path.parent / f"enriched_{input_file.name}"
    
    target_output.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Forcing enrichment: {input_file} -> {target_output}")
    # Pass 1: Collect first chunks for each unique case
    case_first_chunks = {}
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip(): continue
                row = json.loads(line)
                
                tid = row.get('tid')
                if tid:
                    case_key = tid
                else:
                    source = row.get('source') or row.get('url', 'unknown')
                    case_name = row.get('case_name', 'unknown')
                    case_key = f"{case_name}_{source}"
                
                # We only need the first chunk (index 0) or the first one we see
                if case_key not in case_first_chunks:
                    case_first_chunks[case_key] = row
                elif row.get('chunk_index') == 0:
                    case_first_chunks[case_key] = row
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    total_cases = len(case_first_chunks)
    print(f"Found {total_cases} unique cases.")
    
    enrichment_cache = {}
    case_count = 0
    
    from groq import Groq
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    for case_key, first_chunk in case_first_chunks.items():
        domain = first_chunk.get('domain', 'unknown')
        subdomain = first_chunk.get('subdomain', 'unknown')
        text_content = first_chunk.get('text') or first_chunk.get('chunk_text', '')
        text_excerpt = text_content[:1000] 
        
        prompt = f"""You are an Indian legal expert. Read this case excerpt and return ONLY 
valid JSON with no explanation:
{{
  "legal_issue": "one sentence describing the core legal problem",
  "user_intent": "what type of person would search for this case (e.g. someone falsely arrested, worker seeking wages)",
  "stage": "exactly one of [pre-FIR, investigation, trial, appeal, post-judgment]",
  "sections": ["list of sections with act prefix e.g. [IPC 420, CrPC 156(3)]"],
  "acts": ["list of acts e.g. [IPC, CrPC, Constitution of India]"]
}}

Case domain: {domain}
Case subdomain: {subdomain}
Text: {text_excerpt}"""

        # Retry logic for quota issues with Fallback to Groq
        enriched_data = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                enriched_data = json.loads(response.text)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"Gemini Quota hit for case {case_key}, trying Groq fallback...")
                    try:
                        groq_response = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        enriched_data = json.loads(groq_response.choices[0].message.content)
                        print(f"Groq fallback success for case: {case_key}")
                        break
                    except Exception as ge:
                        wait_time = 10 * (attempt + 1)
                        print(f"Groq also failed: {ge}. Retrying Gemini in {wait_time}s...")
                        time.sleep(wait_time)
                else:
                    print(f"Error for case {case_key}: {e}")
                    break 
        
        if enriched_data and all(k in enriched_data for k in ['legal_issue', 'user_intent', 'stage', 'sections', 'acts']):
            enrichment_cache[case_key] = enriched_data
            print(f"Enriched case: {case_key}")
        
        case_count += 1
        time.sleep(1) 
        
    # Pass 2: Write enriched rows to output
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in, \
             open(target_output, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                if not line.strip(): continue
                row = json.loads(line)
                
                tid = row.get('tid')
                if tid:
                    case_key = tid
                else:
                    source = row.get('source') or row.get('url', 'unknown')
                    case_name = row.get('case_name', 'unknown')
                    case_key = f"{case_name}_{source}"
                
                if case_key in enrichment_cache:
                    data = enrichment_cache[case_key]
                    row['legal_issue'] = data.get('legal_issue', row.get('legal_issue'))
                    row['user_intent'] = data.get('user_intent', row.get('user_intent'))
                    row['stage'] = data.get('stage', row.get('stage'))
                    row['sections'] = data.get('sections', row.get('sections'))
                    row['acts'] = data.get('acts', row.get('acts'))
                
                f_out.write(json.dumps(row, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Error writing {target_output}: {e}")

def main():
    corpus_dir = Path("g:/Hackathon/corpus")
    output_dir = Path("g:/Hackathon/enriched_corpus")
    
    # Target only failed files
    failed_files = [
        "criminal/FIR_procedure.jsonl",
        "general/unclassified.jsonl",
        "general/unclassified2.jsonl",
        "labour/wrongful_termination.jsonl",
        "motor_accident/compensation.jsonl"
    ]
    
    for rel_path in failed_files:
        jsonl_file = corpus_dir / rel_path
        if jsonl_file.exists():
            enrich_file(jsonl_file, output_dir)

if __name__ == "__main__":
    main()
