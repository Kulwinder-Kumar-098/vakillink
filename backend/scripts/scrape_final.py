import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import hashlib
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

TARGETS = [
    # Labour Domain (Requested previously)
    {
        "file": "corpus/labour/labour_industrial_disputes.jsonl",
        "query": "Industrial Disputes Act retrenchment reinstatement",
        "domain": "labour",
        "subdomain": "wrongful_termination",
        "target_lines": 550
    },
    {
        "file": "corpus/labour/labour_posh_maternity.jsonl",
        "query": "POSH Act sexual harassment Maternity Benefit Act",
        "domain": "labour",
        "subdomain": "workplace_harassment",
        "target_lines": 550
    },
    # Motor Accident Domain (Requested previously)
    {
        "file": "corpus/motor_accident/motor_accident_mact.jsonl",
        "query": "MACT Motor Vehicles Act compensation multiplier loss of income",
        "domain": "motor_accident",
        "subdomain": "compensation",
        "target_lines": 550
    },
    # High-Hit Criminal
    {
        "file": "corpus/criminal/criminal_498a_dowry.jsonl",
        "query": "IPC 498A cruelty dowry demand Section 304B",
        "domain": "criminal",
        "subdomain": "domestic_violence",
        "target_lines": 550
    }
]

def chunk_text(text, max_words=200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words - 50):
        chunk = ' '.join(words[i:i + max_words])
        if len(chunk.split()) >= 40:
            chunks.append(chunk)
    return chunks

def scrape_topic(target):
    output_file = Path(target["file"])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    API_KEY = "31430b9b0c0cb6e1b8890f53f8be56a6770bc235"
    headers = {"Authorization": f"Token {API_KEY}", "Accept": "application/json"}
    
    seen_hashes = set()
    total_lines = 0
    pagenum = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        while total_lines < target["target_lines"]:
            search_url = f"https://api.indiankanoon.org/search/?formInput={target['query']}&pagenum={pagenum}"
            print(f"[{target['file']}] Fetching search page {pagenum}...")
            
            try:
                resp = requests.post(search_url, headers=headers, timeout=15, verify=False)
                if resp.status_code != 200:
                    break
                
                docs = resp.json().get('docs', [])
                if not docs: break
                    
                for doc in docs:
                    if total_lines >= target["target_lines"]: break
                    doc_id = doc.get("tid")
                    if not doc_id: continue
                    
                    try:
                        doc_resp = requests.post(f"https://api.indiankanoon.org/doc/{doc_id}/", headers=headers, timeout=15, verify=False)
                        if doc_resp.status_code != 200: continue
                            
                        doc_data = doc_resp.json()
                        raw_html = doc_data.get('doc', '')
                        if not raw_html or len(raw_html) < 200: continue
                            
                        soup = BeautifulSoup(raw_html, 'html.parser')
                        for tag in soup(["style", "script", "a", "nav", "footer", "header"]): tag.decompose()
                        text = re.sub(r'\s+', ' ', soup.get_text(separator=' ')).strip()
                        
                        chunks = chunk_text(text)
                        case_name = doc_data.get('title', 'Unknown Case')
                        doc_date = doc_data.get('publishdate', '2023-01-01')
                        doc_year = int(doc_date.split('-')[0]) if doc_date else 2023
                        
                        for chunk in chunks:
                            if total_lines >= target["target_lines"]: break
                            chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                            if chunk_hash in seen_hashes: continue
                            seen_hashes.add(chunk_hash)
                            
                            record = {
                                "id": hashlib.md5(f"{doc_id}_{chunk_hash}".encode()).hexdigest()[:12],
                                "case_name": case_name, "date": doc_date, "year": doc_year,
                                "court": "Indian Courts", "court_type": "Unknown",
                                "cites": doc_data.get('numcites', 0), "cited_by": doc_data.get('numcitedby', 0),
                                "authority": "medium", "domain": target["domain"],
                                "subdomain": target["subdomain"], "crime_type": "unknown",
                                "legal_issue": "unknown", "user_intent": "unknown", "stage": "unknown",
                                "sections": [], "acts": [], "text": chunk, "authority_score": 0.5,
                                "source": f"https://indiankanoon.org/doc/{doc_id}/"
                            }
                            f.write(json.dumps(record) + '\n')
                            total_lines += 1
                    except Exception: pass
                pagenum += 1
            except Exception: break
        print(f"==> Finished {target['file']} with {total_lines} unique lines.")

if __name__ == "__main__":
    for target in TARGETS:
        scrape_topic(target)
