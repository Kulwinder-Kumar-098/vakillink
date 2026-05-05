import json
import os
from pathlib import Path

def validate_dataset():
    root_dir = Path(r"g:\Hackathon\processed_data")
    failed_rows_path = Path(r"g:\Hackathon\failed_rows.jsonl")
    
    required_fields = [
        "id", "text", "case_name", "court", "year", 
        "domain", "subdomain", "legal_issue", "user_intent", "stage", 
        "sections", "acts", "authority_score", "source"
    ]
    
    failed_count = 0
    with open(failed_rows_path, 'w', encoding='utf-8') as f_failed:
        for file_path in root_dir.rglob("*.jsonl"):
            rel_path = file_path.relative_to(root_dir)
            total_rows = 0
            file_failed_count = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    total_rows += 1
                    try:
                        data = json.loads(line)
                    except:
                        file_failed_count += 1
                        continue
                    
                    errors = []
                    
                    # 1. Check required fields
                    for field in required_fields:
                        if field not in data:
                            errors.append(f"Missing field: {field}")
                    
                    # 2. legal_issue != "unknown"
                    if data.get("legal_issue") == "unknown":
                        errors.append("legal_issue is unknown")
                        
                    # 3. No row has empty sections AND empty acts together
                    if not data.get("sections") and not data.get("acts"):
                        errors.append("Both sections and acts are empty")
                        
                    # 4. text field has minimum 50 characters
                    text = data.get("text", "")
                    if len(text) < 50:
                        errors.append(f"Text too short ({len(text)} chars)")
                        
                    if errors:
                        file_failed_count += 1
                        data["validation_errors"] = errors
                        data["source_file"] = str(rel_path)
                        data["line_number"] = line_num
                        f_failed.write(json.dumps(data) + "\n")
            
            status = "PASSED" if file_failed_count == 0 else f"FAILED ({file_failed_count} rows)"
            print(f"{rel_path} -> {total_rows} rows {status}")
            failed_count += file_failed_count

    if failed_count == 0:
        print("\nAll rows passed validation! ✨")
    else:
        print(f"\nValidation complete. {failed_count} rows failed and were saved to failed_rows.jsonl")

if __name__ == "__main__":
    validate_dataset()
