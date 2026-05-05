import json
from pathlib import Path
from collections import Counter

def get_stats():
    root_dir = Path(r"g:\Hackathon\processed_data")
    
    total_chunks = 0
    domain_counts = Counter()
    domain_text_lens = {}
    
    sections_filled = 0
    legal_issue_filled = 0
    
    all_sections = []
    
    for file_path in root_dir.rglob("*.jsonl"):
        domain = file_path.parent.name
        if domain == "processed_data":
            domain = "root"
            
        if domain not in domain_text_lens:
            domain_text_lens[domain] = []
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    data = json.loads(line)
                except:
                    continue
                    
                total_chunks += 1
                domain_counts[domain] += 1
                
                # Stats
                text = data.get("text", "")
                domain_text_lens[domain].append(len(text))
                
                if data.get("sections"):
                    sections_filled += 1
                    all_sections.extend(data["sections"])
                    
                li = data.get("legal_issue")
                if li and li != "unknown":
                    legal_issue_filled += 1
                    
    print("--- Dataset Statistics ---")
    print(f"Total chunks: {total_chunks}")
    
    print("\nChunks per domain:")
    for dom, count in domain_counts.items():
        print(f"  - {dom}: {count}")
        
    if total_chunks > 0:
        print(f"\n% of rows with sections filled: {(sections_filled / total_chunks) * 100:.1f}%")
        print(f"% of rows with legal_issue filled: {(legal_issue_filled / total_chunks) * 100:.1f}%")
        
        print("\nAverage text length per domain:")
        for dom, lens in domain_text_lens.items():
            avg = sum(lens) / len(lens) if lens else 0
            print(f"  - {dom}: {avg:.1f} characters")
            
    print("\nTop 10 most common sections:")
    top_sections = Counter(all_sections).most_common(10)
    for sec, count in top_sections:
        print(f"  - {sec}: {count}")

if __name__ == "__main__":
    get_stats()
