import json
import os
import re

def clean_text(text):
    if not text:
        return ""
    # Remove \n, \t
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Normalize whitespace (multiple spaces to one)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_line(line):
    try:
        data = json.loads(line)
    except Exception:
        return None
    
    # 1. Rename chunk_text -> text and clean it
    text = data.pop('chunk_text', data.get('text', ''))
    data['text'] = clean_text(text)
    
    # 2. Rename importance_score -> authority_score
    if 'importance_score' in data:
        data['authority_score'] = data.pop('importance_score')
    
    # 3. Rename url -> source
    if 'url' in data:
        data['source'] = data.pop('url')
    
    # 4. Remove fields: tid, judge, word_count, total_chunks, chunk_index
    fields_to_remove = ['tid', 'judge', 'word_count', 'total_chunks', 'chunk_index']
    for field in fields_to_remove:
        if field in data:
            data.pop(field)
            
    return data

def main():
    input_root = r"g:\Hackathon\enriched_corpus"
    output_root = r"g:\Hackathon\processed_data"
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
        
    for root, dirs, files in os.walk(input_root):
        for file in files:
            if file.endswith(".jsonl"):
                input_path = os.path.join(root, file)
                
                # Maintain subfolder structure
                rel_path = os.path.relpath(root, input_root)
                target_dir = os.path.join(output_root, rel_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    
                # Clean filename (remove 'enriched_' prefix if present)
                out_filename = file.replace('enriched_', '')
                output_path = os.path.join(target_dir, out_filename)
                
                print(f"Finalizing: {input_path} -> {output_path}")
                
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f_in, \
                     open(output_path, 'w', encoding='utf-8') as f_out:
                    for line in f_in:
                        processed = process_line(line)
                        if processed:
                            f_out.write(json.dumps(processed) + "\n")

if __name__ == "__main__":
    main()
