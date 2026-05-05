import json
import re
import os
from pathlib import Path

# Define base directory and output directory
base_dir = Path(r"g:\Hackathon\corpus")
output_base_dir = Path(r"g:\Hackathon\processed_corpus")

def normalize_whitespace(text):
    if not isinstance(text, str):
        return text
    # remove \n, \t, \r
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    # replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tag_chunk(chunk_text):
    import re
    # Extract Articles (e.g., Article 17, Article 21A)
    articles = re.findall(r'Article \d+[A-Z]?', chunk_text, re.IGNORECASE)
    # Extract Sections (e.g., Section 437, Section 138)
    sections = re.findall(r'Section \d+[A-Z]?', chunk_text, re.IGNORECASE)
    # Extract Acts (e.g., Hindu Marriage Act, 1955)
    acts = re.findall(r'[A-Z][a-z]+(?: [A-Z][a-z]+)* Act,? \d{4}', chunk_text)
    
    return {
        "cited_articles": list(set(articles)),
        "cited_sections": list(set(sections)),
        "cited_acts": list(set(acts))
    }

def process_file(input_file, output_file):
    print(f"Processing: {input_file} -> {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # 1. Rename chunk_text -> text
                text_content = ""
                if 'chunk_text' in data:
                    text_content = normalize_whitespace(data['chunk_text'])
                    data['text'] = text_content
                    del data['chunk_text']
                elif 'text' in data:
                    text_content = normalize_whitespace(data['text'])
                    data['text'] = text_content
                
                # 2. Tag Chunk with Citations
                tags = tag_chunk(text_content)
                data.update(tags)
                
                # 3. Remove fields: tid, judge, word_count, total_chunks, chunk_index
                fields_to_remove = ['tid', 'judge', 'word_count', 'total_chunks', 'chunk_index']
                for field in fields_to_remove:
                    data.pop(field, None)
                    
                # 4. Rename importance_score -> authority_score
                if 'importance_score' in data:
                    data['authority_score'] = data.pop('importance_score')
                    
                # 5. Rename url -> source
                if 'url' in data:
                    data['source'] = data.pop('url')
                    
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

# Find all .jsonl files
jsonl_files = list(base_dir.rglob("*.jsonl"))

for input_file in jsonl_files:
    # Maintain the same directory structure in the output folder
    relative_path = input_file.relative_to(base_dir)
    output_file = output_base_dir / relative_path
    
    process_file(input_file, output_file)

print("\nAll files processed. You can find them in: g:\\Hackathon\\processed_corpus")
