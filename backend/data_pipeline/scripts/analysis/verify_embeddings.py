import os
import json
import numpy as np
import glob

def verify_all_embeddings():
    processed_dir = 'processed_data'
    embeddings_dir = 'embeddings'
    
    categories = [d for d in os.listdir(processed_dir) if os.path.isdir(os.path.join(processed_dir, d))]
    
    report = {}
    
    for cat in categories:
        cat_path = os.path.join(processed_dir, cat)
        jsonl_files = glob.glob(os.path.join(cat_path, '*.jsonl'))
        
        for jsonl_file in jsonl_files:
            file_name = os.path.basename(jsonl_file).replace('.jsonl', '')
            
            # Expected embedding files
            npy_file = os.path.join(embeddings_dir, f'embeddings_{cat}_{file_name}.npy')
            meta_file = os.path.join(embeddings_dir, f'metadata_{cat}_{file_name}.json')
            
            if not os.path.exists(npy_file) or not os.path.exists(meta_file):
                print(f"[-] Missing embedding files for {cat}/{file_name}")
                report[f"{cat}/{file_name}"] = "Missing files"
                continue
            
            # Load counts
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                jsonl_count = sum(1 for _ in f)
            
            try:
                embeddings = np.load(npy_file)
                npy_count = embeddings.shape[0]
                dim = embeddings.shape[1]
            except Exception as e:
                print(f"[-] Error loading {npy_file}: {e}")
                report[f"{cat}/{file_name}"] = f"Load error: {e}"
                continue
                
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                meta_count = len(meta)
            
            status = "OK"
            if jsonl_count != npy_count or jsonl_count != meta_count:
                status = f"Mismatch: JSONL({jsonl_count}), NPY({npy_count}), Meta({meta_count})"
            
            print(f"[*] {cat}/{file_name}: {status} (Dim: {dim})")
            report[f"{cat}/{file_name}"] = {
                "status": status,
                "count": jsonl_count,
                "dim": dim
            }

    with open('embedding_verification_report.json', 'w') as f:
        json.dump(report, f, indent=4)
    print("\nVerification report saved to embedding_verification_report.json")

if __name__ == "__main__":
    verify_all_embeddings()
