import os
import json
import glob
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

EMBEDDINGS_DIR = "embeddings"
CORPUS_DIR = "corpus"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

FILES_TO_EMBED = [
    "criminal/criminal_cheque_bounce.jsonl",
    "criminal/criminal_cybercrime.jsonl",
    "criminal/criminal_anticipatory_bail.jsonl",
    "criminal/criminal_498a_dowry.jsonl",
    "consumer/consumer_rera_builder.jsonl",
    "consumer/consumer_medical_negligence.jsonl",
    "consumer/consumer_ecommerce_airlines.jsonl",
    "family/family_maintenance_alimony.jsonl",
    "family/family_mutual_consent_divorce.jsonl",
    "labour/labour_industrial_disputes.jsonl",
    "labour/labour_posh_maternity.jsonl",
    "motor_accident/motor_accident_mact.jsonl"
]

def generate():
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    print(f"Loading Model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    for rel_path in FILES_TO_EMBED:
        full_path = os.path.join(CORPUS_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"Skipping {full_path} as it does not exist.")
            continue
            
        print(f"\nProcessing {full_path}...")
        
        texts = []
        metadata = []
        
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                
                # Get the chunk text depending on key
                text = data.get("text") or data.get("chunk_text", "")
                texts.append(text)
                
                # Copy everything but the large text into metadata
                meta = data.copy()
                if "text" in meta: del meta["text"]
                if "chunk_text" in meta: del meta["chunk_text"]
                metadata.append(meta)
                
        if not texts:
            print("No text found.")
            continue
            
        # Extract folder and category from path to build the .npy filename
        # e.g., criminal/criminal_cheque_bounce.jsonl -> embeddings_criminal_criminal_cheque_bounce.npy
        folder = Path(rel_path).parent.name
        stem = Path(rel_path).stem
        
        basename = f"{folder}_{stem}"
        npy_path = os.path.join(EMBEDDINGS_DIR, f"embeddings_{basename}.npy")
        json_path = os.path.join(EMBEDDINGS_DIR, f"metadata_{basename}.json")
        
        # Don't recreate if it already exists to save time, unless forced
        if os.path.exists(npy_path) and os.path.exists(json_path):
            print(f"Embeddings already exist for {basename}, skipping.")
            continue
            
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Save .npy
        np.save(npy_path, np.array(embeddings, dtype=np.float32))
        
        # Save .json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"Saved {npy_path} and metadata.")

if __name__ == "__main__":
    generate()