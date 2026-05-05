import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re

TARGETS = [
    {
        "file": "corpus/criminal/criminal_cheque_bounce.jsonl",
        "queries": ["Section 138 Negotiable Instruments Act dishounour"],
        "target_chunks": 40,
        "law_name": "Negotiable Instruments Act 1881",
        "topic": "Jurisdiction for cheque bounce complaint"
    },
    {
        "file": "corpus/criminal/criminal_cybercrime.jsonl",
        "queries": ["IT Act Section 66 financial fraud"],
        "target_chunks": 40,
        "law_name": "Information Technology Act 2000",
        "topic": "Cybercrime and online fraud"
    },
    {
        "file": "corpus/criminal/criminal_anticipatory_bail.jsonl",
        "queries": ["CrPC 438 anticipatory bail conditions"],
        "target_chunks": 40,
        "law_name": "Code of Criminal Procedure 1973",
        "topic": "Anticipatory bail guidelines"
    },
    {
        "file": "corpus/consumer/consumer_rera_builder.jsonl",
        "queries": ["builder delay possession RERA"],
        "target_chunks": 40,
        "law_name": "Consumer Protection Act",
        "topic": "Builder delay and RERA"
    },
    {
        "file": "corpus/consumer/consumer_medical_negligence.jsonl",
        "queries": ["medical negligence deficiency of service hospital"],
        "target_chunks": 40,
        "law_name": "Consumer Protection Act",
        "topic": "Medical negligence and deficiency of service"
    },
    {
        "file": "corpus/consumer/consumer_ecommerce_airlines.jsonl",
        "queries": ["e-commerce refund deficiency consumer forum"],
        "target_chunks": 40,
        "law_name": "Consumer Protection Act",
        "topic": "E-commerce refund and flight delays"
    },
    {
        "file": "corpus/family/family_maintenance_alimony.jsonl",
        "queries": ["Rajnesh v Neha maintenance guidelines"],
        "target_chunks": 40,
        "law_name": "Hindu Marriage Act 1955",
        "topic": "Maintenance and Alimony guidelines"
    },
    {
        "file": "corpus/family/family_mutual_consent_divorce.jsonl",
        "queries": ["mutual consent divorce cooling off period waiver"],
        "target_chunks": 40,
        "law_name": "Hindu Marriage Act 1955",
        "topic": "Mutual consent divorce cooling off period"
    }
]

def chunk_text(text, max_words=150):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words - 30) if len(words[i:i + max_words]) > 40]

def scrape_web(target):
    output_file = Path(target["file"])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    total_saved = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        for q in target["queries"]:
            if total_saved >= target["target_chunks"]:
                break
                
            print(f"Scraping Web for: {q} into {target['file']}")
            search_url = f"https://indiankanoon.org/search/?formInput={q}"
            try:
                resp = requests.get(search_url, headers=headers, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                links = soup.find_all('a', href=re.compile(r'/doc/'))
                doc_urls = [f"https://indiankanoon.org{link['href']}" for link in links][:5] # top 5 docs
                
                for doc_url in doc_urls:
                    if total_saved >= target["target_chunks"]:
                        break
                    
                    time.sleep(1) # polite delay
                    doc_resp = requests.get(doc_url, headers=headers, timeout=10)
                    doc_soup = BeautifulSoup(doc_resp.text, 'html.parser')
                    
                    title_elem = doc_soup.find('div', class_='doc_title')
                    title = title_elem.text.strip() if title_elem else "Unknown Case"
                    
                    content_div = doc_soup.find('div', class_='judgments')
                    if not content_div:
                        continue
                        
                    for tag in content_div(["style", "script", "a"]):
                        tag.decompose()
                        
                    raw_text = content_div.get_text(separator=' ')
                    raw_text = re.sub(r'\s+', ' ', raw_text).strip()
                    
                    chunks = chunk_text(raw_text)
                    
                    # Store 5-8 chunks per doc to hit ~40 target efficiently
                    for chunk in chunks[:8]:
                        if total_saved >= target["target_chunks"]:
                            break
                            
                        record = {
                            "chunk_text": chunk,
                            "case_name": title,
                            "law_name": target["law_name"],
                            "legal_issue": target["topic"],
                            "acts": [target["law_name"]],
                            "sections": [],
                            "cited_articles": [],
                            "cited_sections": [],
                            "cited_acts": [target["law_name"]]
                        }
                        f.write(json.dumps(record) + '\n')
                        total_saved += 1
                        
            except Exception as e:
                print(f"Error scraping web for {q}: {e}")

if __name__ == "__main__":
    for target in TARGETS:
        scrape_web(target)
    print("Scraping completed. Check your corpus directories.")