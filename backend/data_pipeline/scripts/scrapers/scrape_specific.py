import json
import time
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup

API_KEY = "31430b9b0c0cb6e1b8890f53f8be56a6770bc235"
BASE_API = "https://api.indiankanoon.org"

TARGETS = [
    {
        "file": "corpus/criminal/criminal_cheque_bounce.jsonl",
        "queries": ["Section 138 Negotiable Instruments Act"],
        "target_docs": 15,
        "law_name": "Negotiable Instruments Act 1881"
    },
    {
        "file": "corpus/criminal/criminal_cybercrime.jsonl",
        "queries": ["IT Act Section 66 financial fraud"],
        "target_docs": 15,
        "law_name": "Information Technology Act 2000"
    },
    {
        "file": "corpus/criminal/criminal_anticipatory_bail.jsonl",
        "queries": ["CrPC 438 anticipatory bail conditions"],
        "target_docs": 15,
        "law_name": "Code of Criminal Procedure 1973"
    },
    {
        "file": "corpus/consumer/consumer_rera_builder.jsonl",
        "queries": ["builder delay possession RERA"],
        "target_docs": 15,
        "law_name": "Consumer Protection Act"
    },
    {
        "file": "corpus/consumer/consumer_medical_negligence.jsonl",
        "queries": ["medical negligence deficiency of service hospital consumer forum"],
        "target_docs": 15,
        "law_name": "Consumer Protection Act"
    },
    {
        "file": "corpus/consumer/consumer_ecommerce_airlines.jsonl",
        "queries": ["e-commerce refund deficiency", "airline delay consumer forum"],
        "target_docs": 15,
        "law_name": "Consumer Protection Act"
    },
    {
        "file": "corpus/family/family_maintenance_alimony.jsonl",
        "queries": ["Rajnesh v Neha maintenance guidelines"],
        "target_docs": 15,
        "law_name": "Hindu Marriage Act"
    },
    {
        "file": "corpus/family/family_mutual_consent_divorce.jsonl",
        "queries": ["mutual consent divorce cooling off period waiver"],
        "target_docs": 15,
        "law_name": "Hindu Marriage Act"
    }
]

def clean_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, max_words=100):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words - 20)]

def extract_acts_sections(text):
    acts = []
    sections = []
    if "Section 138" in text: sections.append("Section 138")
    if "Negotiable Instruments Act" in text: acts.append("Negotiable Instruments Act 1881")
    return list(set(acts)), list(set(sections))

def scrape_topic(target):
    output_file = Path(target["file"])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    docs_saved = 0
    headers = {"Authorization": f"Token {API_KEY}"}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for q in target["queries"]:
            print(f"Searching: {q}")
            try:
                resp = requests.post(f"{BASE_API}/search/?formInput={q}", headers=headers, timeout=10)
                if resp.status_code != 200:
                    print(f"Search API Error {resp.status_code}: {resp.text}")
                    continue
                data = resp.json()
                
                if 'docs' not in data:
                    print(f"No 'docs' in response. Data: {data}")
                    continue
                
                for doc in data.get('docs', []):
                    if docs_saved >= target["target_docs"]:
                        break
                        
                    doc_id = doc.get("tid")
                    if not doc_id: continue
                    
                    doc_resp = requests.post(f"{BASE_API}/doc/{doc_id}/", headers=headers, timeout=10)
                    if doc_resp.status_code != 200:
                        continue
                        
                    doc_data = doc_resp.json()
                    content = clean_text(doc_data.get('doc', ''))
                    
                    if len(content) < 500:
                        continue
                        
                    chunks = chunk_text(content)
                    title = doc_data.get('title', 'Unknown Case')
                    acts, sections = extract_acts_sections(content)
                    
                    for chunk in chunks[:10]: # Take top 10 chunks per doc for more data
                        record = {
                            "chunk_text": chunk,
                            "case_name": title,
                            "law_name": target["law_name"],
                            "legal_issue": q,
                            "acts": acts,
                            "sections": sections,
                            "cited_articles": [],
                            "cited_sections": sections,
                            "cited_acts": acts
                        }
                        f.write(json.dumps(record) + '\n')
                        docs_saved += 1
                        if docs_saved >= target["target_docs"]:
                            break
                    time.sleep(1)
            except Exception as e:
                print(f"Error scraping {q}: {e}")
                
if __name__ == "__main__":
    for target in TARGETS:
        print(f"Scraping for {target['file']}...")
        scrape_topic(target)
