import json
from pathlib import Path
import sys

# Add current dir to sys.path to import utils
sys.path.append('.')

from utils.config import FAISS_META_PATH

def inspect():
    if not FAISS_META_PATH.exists():
        print(f"Meta file not found: {FAISS_META_PATH}")
        return
        
    with open(FAISS_META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
        
    print(f"Total chunks: {len(meta)}")
    
    unique_cases = list(set([c.get('case_name', 'Unknown') for c in meta]))
    print(f"Total unique cases: {len(unique_cases)}")
    print("\nSample cases:")
    for name in unique_cases[:10]:
        print(f"- {name}")
        
    unique_courts = list(set([c.get('court', 'Unknown') for c in meta]))
    print(f"\nUnique courts: {unique_courts}")
    
    print(f"\nKeys in first chunk: {list(meta[0].keys())}")

if __name__ == "__main__":
    inspect()
