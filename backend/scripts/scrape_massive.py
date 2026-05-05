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

# TARGETS
TARGETS = [
    {
        "file": "corpus/criminal/criminal_cheque_bounce.jsonl",
        "query": "Section 138 Negotiable Instruments Act dishonour",
        "domain": "criminal",
        "subdomain": "fraud_cheating",
        "target_lines": 550
    },
    {
        "file": "corpus/criminal/criminal_cybercrime.jsonl",
        "query": "IT Act Section 66 financial fraud",
        "domain": "criminal",
        "subdomain": "cyber_crime",
        "target_lines": 550
    },
    {
        "file": "corpus/criminal/criminal_anticipatory_bail.jsonl",
        "query": "CrPC 438 anticipatory bail conditions",
        "domain": "criminal",
        "subdomain": "bail_general",
        "target_lines": 550
    },
    {
        "file": "corpus/consumer/consumer_rera_builder.jsonl",
        "query": "builder delay possession RERA",
        "domain": "consumer",
        "subdomain": "service_deficiency",
        "target_lines": 550
    },
    {
        "file": "corpus/consumer/consumer_medical_negligence.jsonl",
        "query": "medical negligence deficiency of service hospital",
        "domain": "consumer",
        "subdomain": "service_deficiency",
        "target_lines": 550
    },
    {
        "file": "corpus/consumer/consumer_ecommerce_airlines.jsonl",
        "query": "e-commerce refund airline delay consumer forum",
        "domain": "consumer",
        "subdomain": "online_fraud",
        "target_lines": 550
    },
    {
        "file": "corpus/family/family_maintenance_alimony.jsonl",
        "query": "Rajnesh v Neha maintenance guidelines",
        "domain": "family",
        "subdomain": "maintenance",
        "target_lines": 550
    },
    {
        "file": "corpus/family/family_mutual_consent_divorce.jsonl",
        "query": "mutual consent divorce cooling off period waiver",
        "domain": "family",
        "subdomain": "divorce",
        "target_lines": 550
    }
]

def chunk_text(text, max_words=200):
    words = text.split()
    chunks = []
    # Use overlap of 30 words
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
                    print(f"API Error {resp.status_code}. Stopping paginated search.")
                    break
                
                data = resp.json()
                docs = data.get('docs', [])
                if not docs:
                    print("No more documents found.")
                    break
                    
                for doc in docs:
                    if total_lines >= target["target_lines"]:
                        break
                        
                    doc_id = doc.get("tid")
                    if not doc_id:
                        continue
                    
                    # Fetch document details
                    try:
                        doc_resp = requests.post(f"https://api.indiankanoon.org/doc/{doc_id}/", headers=headers, timeout=15, verify=False)
                        if doc_resp.status_code != 200:
                            continue
                            
                        doc_data = doc_resp.json()
                        raw_html = doc_data.get('doc', '')
                        if not raw_html or len(raw_html) < 200:
                            continue
                            
                        soup = BeautifulSoup(raw_html, 'html.parser')
                        for tag in soup(["style", "script", "a", "nav", "footer", "header"]):
                            tag.decompose()
                        
                        text = soup.get_text(separator=' ')
                        text = re.sub(r'\s+', ' ', text).strip()
                        
                        chunks = chunk_text(text)
                        
                        case_name = doc_data.get('title', 'Unknown Case')
                        doc_date = doc_data.get('publishdate', '2023-01-01')
                        doc_year = int(doc_date.split('-')[0]) if doc_date else 2023
                        
                        for chunk in chunks:
                            if total_lines >= target["target_lines"]:
                                break
                            
                            chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                            if chunk_hash in seen_hashes:
                                continue
                            seen_hashes.add(chunk_hash)
                            
                            # Construct identical matching JSON schema as `criminal.jsonl`
                            record = {
                                "id": hashlib.md5(f"{doc_id}_{chunk_hash}".encode()).hexdigest()[:12],
                                "case_name": case_name,
                                "date": doc_date,
                                "year": doc_year,
                                "court": "Indian Courts",
                                "court_type": "Unknown",
                                "cites": doc_data.get('numcites', 0),
                                "cited_by": doc_data.get('numcitedby', 0),
                                "authority": "medium",
                                "domain": target["domain"],
                                "subdomain": target["subdomain"],
                                "crime_type": "unknown",
                                "legal_issue": "unknown",
                                "user_intent": "unknown",
                                "stage": "unknown",
                                "sections": [],
                                "acts": [],
                                "text": chunk,
                                "authority_score": 0.5,
                                "source": f"https://indiankanoon.org/doc/{doc_id}/"
                            }
                            
                            f.write(json.dumps(record) + '\n')
                            total_lines += 1
                            
                    except Exception as inner_e:
                        print(f"Error fetching doc {doc_id}: {inner_e}")
                
                pagenum += 1
                
            except Exception as e:
                print(f"Error searching on page {pagenum}: {e}")
                break
                
        print(f"==> Finished {target['file']} with {total_lines} unique lines.")

if __name__ == "__main__":
    for target in TARGETS:
        scrape_topic(target)
