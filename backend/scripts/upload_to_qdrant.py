import os
import json
import numpy as np
import hashlib
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
QDRANT_URL     = "https://dd8cf751-1ca8-46fa-8c89-f1f6c6961784.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6M2EyMzM4ZDQtNzRjZC00ZGViLTgwMjYtODY2OTkwODg5YmY1In0.hDm23QaqaDxj1yWYhsaIa77V6wB6ij-LaMdM69QzWaM"
EMBEDDINGS_DIR = r"G:\Hackathon\embeddings"
CORPUS_DIR     = r"G:\Hackathon\corpus"
VECTOR_SIZE    = 384  # all-MiniLM-L6-v2

# Mapping from Domain to filename patterns
DOMAIN_MAP = {
    "legal_criminal": ["criminal_"],
    "legal_constitutional": ["constitutional_"],
    "legal_consumer": ["consumer_"],
    "legal_family": ["family_"],
    "legal_labour": ["labour_"],
    "legal_motor_accident": ["motor_accident_"],
    "legal_general": ["general_"],
}

# Explicit Mapping for Corpus Files
CORPUS_FILE_MAP = {
    'embeddings_constitutional_constitutional.npy': 'constitutional/constitutional.jsonl',
    'embeddings_constitutional_illegal_detention.npy': 'constitutional/illegal_detention.jsonl',
    'embeddings_consumer_consumer.npy': 'consumer/consumer.jsonl',
    'embeddings_consumer_online_fraud.npy': 'consumer/online_fraud.jsonl',
    'embeddings_consumer_service_deficiency.npy': 'consumer/service_deficiency.jsonl',
    'embeddings_criminal_FIR_procedure.npy': 'criminal/FIR_procedure.jsonl',
    'embeddings_criminal_assault_violence.npy': 'criminal/assault_violence.jsonl',
    'embeddings_criminal_bail_general.npy': 'criminal/bail_general.jsonl',
    'embeddings_criminal_criminal.npy': 'criminal/criminal.jsonl',
    'embeddings_criminal_domestic_violence.npy': 'criminal/domestic_violence.jsonl',
    'embeddings_criminal_drug_offenses.npy': 'criminal/drug_offenses.jsonl',
    'embeddings_criminal_fraud_cheating.npy': 'criminal/fraud_cheating.jsonl',
    'embeddings_family_child_custody.npy': 'family/child_custody.jsonl',
    'embeddings_family_divorce.npy': 'family/divorce.jsonl',
    'embeddings_family_family.npy': 'family/family.jsonl',
    'embeddings_family_maintenance.npy': 'family/maintenance.jsonl',
    'embeddings_general_unclassified.npy': 'general/unclassified.jsonl',
    'embeddings_general_unclassified2.npy': 'general/unclassified2.jsonl',
    'embeddings_labour_wrongful_termination.npy': 'labour/wrongful_termination.jsonl',
    'embeddings_motor_accident_compensation.npy': 'motor_accident/compensation.jsonl',
}

def get_deterministic_uuid(source_file, index):
    unique_str = f"{source_file}_{index}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def safe_upsert(client, collection_name, points, retries=3):
    for i in range(retries):
        try:
            client.upsert(collection_name=collection_name, points=points)
            return
        except Exception as e:
            if i == retries - 1: raise e
            print(f"  [RETRY] Error during upsert: {e}. Sleeping 5s...")
            time.sleep(5)

def upload_domain_collection(client, collection_name, patterns):
    print(f"\n[UPLOAD] Processing Domain: {collection_name}")
    
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    
    npy_files = sorted([f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith(".npy") and any(p in f for p in patterns)])
    
    total_points = 0
    for npy_file in npy_files:
        json_file = npy_file.replace("embeddings_", "metadata_").replace(".npy", ".json")
        json_path = os.path.join(EMBEDDINGS_DIR, json_file)
        npy_path = os.path.join(EMBEDDINGS_DIR, npy_file)
        
        rel_jsonl = CORPUS_FILE_MAP.get(npy_file)
        jsonl_path = os.path.join(CORPUS_DIR, rel_jsonl) if rel_jsonl else None
        
        if not os.path.exists(json_path): continue
            
        print(f"  [+] Loading {npy_file}...")
        embeddings = np.load(npy_path).astype(np.float32)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata_list = json.load(f)
            
        corpus_texts = []
        if jsonl_path and os.path.exists(jsonl_path):
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        text = obj.get("chunk_text") or obj.get("text") or ""
                        corpus_texts.append(text)
                    except: continue
        else:
            corpus_texts = [None] * len(metadata_list)
            
        points = []
        for i, (vec, meta) in enumerate(zip(embeddings, metadata_list)):
            point_id = get_deterministic_uuid(npy_file, i)
            raw_text = corpus_texts[i] if i < len(corpus_texts) else None
            chunk_text = raw_text or meta.get("legal_issue") or ""
            
            # Metadata cleaning
            if "scavenger" in chunk_text.lower() and meta.get("legal_issue") == "unknown":
                meta["legal_issue"] = "Rights and rehabilitation of manual scavengers"
                meta["subdomain"] = "manual_scavenging"
            
            payload = {
                "chunk_text": chunk_text,
                "source_file": npy_file,
                "domain": collection_name,
                "chunk_id": i,
                "law_name": meta.get("case_name", ""),
                "subdomain": meta.get("subdomain", ""),
                "sections": meta.get("sections", ""),
                "acts": meta.get("acts", ""),
                "legal_issue": meta.get("legal_issue", ""),
                "year": meta.get("year", ""),
            }
            
            points.append(PointStruct(id=point_id, vector=vec.tolist(), payload=payload))
            
            if len(points) >= 50:  # Reduced batch size for stability
                safe_upsert(client, collection_name, points)
                points = []
                
        if points:
            safe_upsert(client, collection_name, points)
            
        total_points += len(embeddings)
        print(f"  [OK] {npy_file} ({len(embeddings)} pts)")

    print(f"[DONE] {collection_name}: {total_points} pts")

if __name__ == "__main__":
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    for domain, patterns in DOMAIN_MAP.items():
        upload_domain_collection(client, domain, patterns)