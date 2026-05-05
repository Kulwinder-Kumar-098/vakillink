import json
import re
import time
import random
import hashlib
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_KEY      = "467212a79c8fa202e600c963e3def90fb964094d"
OUTPUT_DIR   = Path("corpus")
DELAY_MIN    = 1.5
DELAY_MAX    = 3.0
CHUNK_SIZE   = 450
CHUNK_OVERLAP= 50
MIN_CHARS    = 100

# ── FIX 1: Per-subdomain caps (was hardcoded 800 everywhere) ──────────────────
SUBDOMAIN_CAPS = {
    # Criminal — highest volume
    ("criminal", "cyber_crime"):         800,
    ("criminal", "fraud_cheating"):     1000,
    ("criminal", "bail_general"):        900,
    ("criminal", "assault_violence"):    800,
    ("criminal", "domestic_violence"):   700,
    ("criminal", "drug_offenses"):       700,
    ("criminal", "FIR_procedure"):       700,
    ("criminal", "theft_robbery"):       600,
    # Civil
    ("civil", "property_disputes"):      900,
    ("civil", "contract_disputes"):      700,
    ("civil", "rent_tenant"):            600,
    ("civil", "money_recovery"):         600,
    # Family
    ("family", "divorce"):               700,
    ("family", "maintenance"):           700,
    ("family", "child_custody"):         500,
    # Labour
    ("labour", "wrongful_termination"):  700,
    ("labour", "salary_disputes"):       500,
    ("labour", "workplace_harassment"):  400,
    # Consumer
    ("consumer", "defective_product"):   500,
    ("consumer", "service_deficiency"):  700,
    ("consumer", "online_fraud"):        500,
    # Constitutional
    ("constitutional", "illegal_detention"): 500,
    ("constitutional", "police_misuse"):     400,
    ("constitutional", "rights_violations"): 500,
    # Motor Accident
    ("motor_accident", "compensation"):  700,
    ("motor_accident", "insurance"):     500,
    # Cyber Law
    ("cyber_law", "data_breach"):        400,
    ("cyber_law", "social_media"):       500,
}
DEFAULT_CAP = 600   # fallback for any unlisted subdomain

# ─────────────────────────────────────────────────────────────────────────────

BASE_API  = "https://api.indiankanoon.org"
BASE_DOC  = "https://indiankanoon.org/doc"

# ── TARGET QUERIES ────────────────────────────────────────────────────────────
DOMAIN_QUERIES = {

    "criminal": {
        "cyber_crime": [
            ("IPC 420 online fraud UPI cheating", 3),
            ("IT Act 66C identity theft conviction", 2),
            ("cyber fraud FIR procedure investigation", 2),
            ("online banking fraud Section 43 IT Act", 2),
            ("phishing social engineering IPC 419 420", 2),
        ],
        "fraud_cheating": [
            ("IPC 420 cheating dishonest inducement", 3),
            ("IPC 406 criminal breach of trust", 3),
            ("cheque bounce NI Act 138 dishonour", 3),
        ],
        "assault_violence": [
            ("IPC 323 324 325 assault hurt grievous", 2),
            ("IPC 307 attempt to murder bail", 2),
            ("IPC 302 murder conviction bail", 2),
        ],
        "drug_offenses": [
            ("NDPS Act section 37 bail commercial quantity", 3),
            ("section 8 NDPS possession consumption", 2),
            ("drug trafficking bail twin conditions NDPS", 2),
        ],
        "FIR_procedure": [
            ("FIR registration refusal mandamus High Court", 2),
            ("zero FIR transfer jurisdiction", 2),
            ("quashing FIR section 482 CrPC", 3),
            ("chargesheet delay default bail 167 CrPC", 2),
        ],
        "domestic_violence": [
            ("IPC 498A cruelty bail misuse", 2),
            ("domestic violence act 2005 protection order", 2),
            ("DV Act section 12 application procedure", 2),
        ],
        "theft_robbery": [
            ("IPC 379 380 theft conviction sentence", 2),
            ("IPC 392 395 robbery dacoity bail", 2),
        ],
        # FIX 2: bail_general added to DOMAIN_QUERIES so it gets actively scraped
        "bail_general": [
            ("bail application CrPC 437 sessions court", 3),
            ("anticipatory bail CrPC 438 conditions", 3),
            ("default bail CrPC 167 chargesheet delay", 2),
            ("bail cancellation CrPC 439 flight risk", 2),
            ("bail Supreme Court guidelines Satender Kumar Antil", 2),
        ],
    },

    "civil": {
        "property_disputes": [
            ("specific performance property agreement to sell", 3),
            ("adverse possession title suit limitation", 2),
            ("partition suit coparcenary Hindu Undivided Family", 2),
            ("injunction property encroachment civil suit", 2),
        ],
        "contract_disputes": [
            ("breach of contract damages specific performance", 3),
            ("contract enforcement section 10 Indian Contract Act", 2),
        ],
        "rent_tenant": [
            ("rent control eviction tenant landlord", 3),
            ("Rent Control Act eviction grounds arrears", 2),
        ],
        "money_recovery": [
            ("recovery of money civil suit decree execution", 2),
            ("summary suit Order 37 CPC money recovery", 2),
        ],
    },

    "family": {
        "divorce": [
            ("divorce mutual consent section 13B Hindu Marriage Act", 3),
            ("divorce cruelty desertion section 13 HMA", 3),
            ("irretrievable breakdown divorce Supreme Court", 2),
        ],
        "maintenance": [
            ("section 125 CrPC maintenance wife child", 3),
            ("maintenance pendente lite section 24 HMA", 2),
            ("alimony permanent maintenance quantum", 2),
        ],
        "child_custody": [
            ("child custody guardianship welfare paramount", 3),
            ("custody visitation rights non-custodial parent", 2),
            ("Guardians and Wards Act section 7 custody", 2),
        ],
    },

    "labour": {
        "wrongful_termination": [
            ("wrongful termination workman Industrial Disputes Act", 3),
            ("retrenchment compensation section 25F IDA", 2),
            ("reinstatement back wages unfair labour practice", 2),
        ],
        "salary_disputes": [
            ("Payment of Wages Act salary withheld", 2),
            ("minimum wages violation labour court", 2),
        ],
        "workplace_harassment": [
            ("POSH Act sexual harassment workplace ICC", 2),
            ("workplace harassment section 354 IPC", 2),
        ],
    },

    "consumer": {
        "defective_product": [
            ("Consumer Protection Act defective product compensation", 3),
            ("product liability section 84 Consumer Protection Act 2019", 2),
        ],
        "service_deficiency": [
            ("deficiency in service consumer forum", 3),
            ("insurance claim repudiation consumer complaint", 2),
            ("builder flat possession delay consumer forum", 2),
        ],
        "online_fraud": [
            ("online shopping fraud consumer complaint ecommerce", 2),
            ("refund dispute Amazon Flipkart consumer court", 2),
        ],
    },

    "constitutional": {
        "illegal_detention": [
            ("habeas corpus illegal detention Article 226", 3),
            ("preventive detention personal liberty Article 21", 2),
        ],
        "police_misuse": [
            ("police excess custodial violence compensation", 2),
            ("false FIR malicious prosecution compensation", 2),
        ],
        "rights_violations": [
            ("freedom of speech Article 19 reasonable restriction", 2),
            ("right to privacy Article 21 Puttaswamy", 2),
        ],
    },

    "motor_accident": {
        "compensation": [
            ("motor accident compensation MACT tribunal", 3),
            ("permanent disability compensation structured formula", 2),
            ("hit and run compensation section 161 Motor Vehicles Act", 2),
        ],
        "insurance": [
            ("third party insurance claim repudiation", 2),
            ("contributory negligence motor accident", 2),
        ],
    },

    "cyber_law": {
        "data_breach": [
            ("data breach IT Act section 43A compensation", 2),
            ("privacy violation data protection", 2),
        ],
        "social_media": [
            ("social media harassment IPC 354D stalking", 2),
            ("defamation online IPC 499 500", 2),
        ],
    },
}

# Domain classification rules
DOMAIN_RULES = [
    ("criminal", "cyber_crime",         ["IT Act 66C", "IT Act 43", "IPC 419", "IPC 420"],
                                         ["cyber", "phishing", "hacking", "UPI fraud", "identity theft"]),
    ("criminal", "fraud_cheating",      ["IPC 420", "IPC 406", "NI Act 138"],
                                         ["cheque bounce", "criminal breach of trust", "cheating"]),
    ("criminal", "drug_offenses",       ["NDPS"],
                                         ["narcotic", "drug", "contraband", "commercial quantity"]),
    ("criminal", "domestic_violence",   ["IPC 498A", "DV Act"],
                                         ["cruelty", "domestic violence", "matrimonial"]),
    ("criminal", "FIR_procedure",       ["CrPC 154", "CrPC 482", "CrPC 173"],
                                         ["FIR", "quashing", "chargesheet", "zero FIR"]),
    ("criminal", "assault_violence",    ["IPC 302", "IPC 307", "IPC 323", "IPC 324"],
                                         ["murder", "attempt to murder", "assault", "grievous hurt"]),
    # FIX 2: bail_general rule already existed; now it's also actively scraped
    ("criminal", "bail_general",        ["CrPC 437", "CrPC 438", "CrPC 439", "CrPC 167"],
                                         ["bail", "anticipatory bail", "default bail"]),
    ("family",   "divorce",             ["HMA 13", "HMA 13B"],
                                         ["divorce", "dissolution", "matrimonial"]),
    ("family",   "maintenance",         ["CrPC 125", "HMA 24", "HMA 25"],
                                         ["maintenance", "alimony", "interim maintenance"]),
    ("family",   "child_custody",       ["GWA 7", "HMA 26"],
                                         ["custody", "guardianship", "visitation", "welfare of child"]),
    ("labour",   "wrongful_termination",["IDA 25F", "IDA 25G"],
                                         ["retrenchment", "termination", "reinstatement", "back wages"]),
    ("consumer", "service_deficiency",  ["CPA 2"],
                                         ["consumer forum", "deficiency", "compensation", "builder"]),
    ("consumer", "online_fraud",        [],
                                         ["ecommerce", "Amazon", "Flipkart", "online shopping", "refund"]),
    ("constitutional", "illegal_detention", ["Article 21", "Article 226"],
                                         ["habeas corpus", "illegal detention", "preventive detention"]),
    ("motor_accident", "compensation",  ["MV Act 161", "MV Act 163"],
                                         ["MACT", "motor accident", "compensation", "tribunal"]),
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "BailSense-Research-Bot/1.0 (academic project)"
})

def polite_sleep():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

def search_tids(query: str, page: int = 0) -> list[str]:
    try:
        r = session.post(
            f"{BASE_API}/search/",
            data={"formInput": query, "pagenum": page},
            timeout=15
        )
        r.raise_for_status()
        docs = r.json().get("docs", [])
        return [str(d["tid"]) for d in docs if "tid" in d]
    except Exception as e:
        print(f"  [search error] {query} p{page}: {e}")
        return []

def fetch_doc_html(tid: str) -> str | None:
    try:
        r = session.get(f"{BASE_DOC}/{tid}/", timeout=20)
        r.raise_for_status()
        polite_sleep()
        return r.text
    except Exception as e:
        print(f"  [fetch error] tid={tid}: {e}")
        return None

# ── PARSER HELPERS ────────────────────────────────────────────────────────────

def extract_court(soup, full_text):
    candidates = [
        soup.find("div", class_="docsource_main"),
        soup.find("div", class_="docsource"),
        soup.find("span", class_="docsource"),
    ]
    for el in candidates:
        if el:
            value = clean_meta(el.get_text(" ", strip=True))
            if value:
                return value
    patterns = [
        r"\b(Supreme Court of India)\b",
        r"\b([A-Z][A-Za-z .&\-()]+High Court(?:\s*-\s*[A-Za-z .&\-()]+)?)\b",
        r"\b([A-Z][A-Za-z .&\-()]+District Court)\b",
        r"\b([A-Z][A-Za-z .&\-()]+Sessions Court)\b",
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.I)
        if m:
            return clean_meta(m.group(1))
    return "Unknown"

def extract_date(soup, full_text):
    candidates = [
        soup.find("span", class_="doc_date"),
        soup.find("div", class_="doc_date"),
    ]
    for el in candidates:
        if el:
            raw = clean_meta(el.get_text(" ", strip=True))
            parsed = parse_date(raw)
            if parsed:
                return parsed
    patterns = [
        r"\bon\s+(\d{1,2}\s+\w+,?\s+\d{4})\b",
        r"\bDate of Order\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b",
        r"\bDate\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b",
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.I)
        if m:
            parsed = parse_date(m.group(1).strip())
            if parsed:
                return parsed
    return "Unknown"

def extract_judge(soup, full_text):
    candidates = [
        soup.find("span", class_="doc_author"),
        soup.find("div", class_="doc_author"),
    ]
    for el in candidates:
        if el:
            value = clean_meta(el.get_text(" ", strip=True))
            if value:
                return value[:80]
    patterns = [
        r"\bAuthor:\s*([A-Za-z.\s]+)",
        r"\bBench:\s*([A-Za-z.\s,]+)",
        r"\bHON'?BLE\s+(?:MR\.?|MRS\.?|MS\.?|DR\.?|JUSTICE\s+)?([A-Za-z.\s]+)",
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.I)
        if m:
            value = clean_meta(m.group(1))
            if value:
                return value[:80]
    return "Unknown"

def clean_meta(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"\bJUDGMENT\b.*$", "", text, flags=re.I).strip()
    text = re.sub(r"\bORDER\b.*$",    "", text, flags=re.I).strip()
    return text

# ── FIX 3: Acts extraction (was always []) ────────────────────────────────────
KNOWN_ACTS = [
    "Indian Penal Code", "IPC",
    "Code of Criminal Procedure", "CrPC", "BNSS",
    "IT Act", "Information Technology Act",
    "NDPS Act", "Narcotic Drugs",
    "Hindu Marriage Act", "HMA",
    "Domestic Violence Act", "DV Act",
    "Consumer Protection Act",
    "Industrial Disputes Act", "IDA",
    "Motor Vehicles Act",
    "POCSO Act",
    "PMLA", "Prevention of Money Laundering",
    "UAPA",
    "Negotiable Instruments Act", "NI Act",
    "Transfer of Property Act",
    "Specific Relief Act",
    "Limitation Act",
    "Payment of Wages Act",
    "POSH Act",
    "Guardians and Wards Act",
]

def extract_acts(text: str) -> list[str]:
    found = set()
    for act in KNOWN_ACTS:
        if re.search(re.escape(act), text, re.I):
            found.add(act)
    return sorted(found)

# ── PARSERS ───────────────────────────────────────────────────────────────────

def parse_html(html: str, tid: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text(" ", strip=True)

    title_el = soup.find("h2", class_="doc_title") or soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""
    title = re.sub(r"\s+on\s+\d{1,2}\s+\w+,?\s+\d{4}$", "", title).strip()
    title = clean_meta(title) or "Unknown"

    court = extract_court(soup, full_text)
    date_norm = extract_date(soup, full_text)
    judge = extract_judge(soup, full_text)

    cite_text = full_text
    cites_m   = re.search(r"Cites\s+(\d+)",    cite_text, re.I)
    citedby_m = re.search(r"Cited by\s+(\d+)", cite_text, re.I)
    cites    = int(cites_m.group(1))   if cites_m   else 0
    cited_by = int(citedby_m.group(1)) if citedby_m else 0

    sections = extract_sections(cite_text)
    acts     = extract_acts(cite_text)      # FIX 3: now populated

    body_el = (
        soup.find("div", class_="judgments") or
        soup.find("div", id="doc_content") or
        soup.find("div", class_="doc_content")
    )
    if not body_el:
        print(f"    [skip] no body element: {tid}")
        return None

    body = clean_text(body_el.get_text(separator="\n"))

    if len(body.split()) < 100:
        print(f"    [skip] body too short: {tid}")
        return None

    yr_m = re.search(r"\b(19|20)\d{2}\b", date_norm) if date_norm != "Unknown" else None
    year = int(yr_m.group()) if yr_m else None
    court_type = infer_court_type(court)

    domain_tags = infer_domain_tags(body, sections)
    importance_score = compute_importance_score(cited_by, court_type, year)

    return {
        "tid":        tid,
        "case_name":  title,
        "date":       date_norm,
        "year":       year,
        "court":      court,
        "court_type": court_type,
        "judge":      judge[:80],
        "cites":      cites,
        "cited_by":   cited_by,
        "authority":  score_authority(cited_by, court_type),
        "url":        f"{BASE_DOC}/{tid}/",
        "domain":     domain_tags["domain"],
        "subdomain":  domain_tags["subdomain"],
        "confidence": domain_tags["confidence"],
        "crime_type":    "unknown",   # kept as stub; enrich later with NLP
        "legal_issue":   "unknown",
        "user_intent":   "unknown",
        "stage":         "unknown",
        "sections":      sections,
        "acts":          acts,        # FIX 3
        "importance_score": importance_score,
        "legal_keywords":   extract_keywords(body),
        "summary":          body[:300],
        "body":             body,
    }

def extract_keywords(text: str) -> list[str]:
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    legal_terms = {
        "bail", "murder", "fraud", "section", "court", "appeal",
        "accused", "petition", "order", "judgment", "evidence",
        "witness", "conviction", "acquittal", "sentence", "custody",
        "maintenance", "divorce", "retrenchment", "compensation",
    }
    found = [w for w in words if w in legal_terms]
    return [w for w, _ in Counter(found).most_common(5)]

def extract_sections(text: str) -> list[str]:
    patterns = [
        r"[Ss]ection\s+(\d+[A-Za-z]?(?:\(\d+\))?)\s+(?:Cr\.?P\.?C|CrPC|BNSS|IPC|NDPS|PMLA|UAPA|POCSO)",
        r"[Ss]\.?\s*(\d+[A-Za-z]?(?:\(\d+\))?)\s+(?:Cr\.?P\.?C|CrPC|BNSS)",
    ]
    found = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            found.add(m.group(1))
    return sorted(found)

def parse_date(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    months = {
        "january":"01","february":"02","march":"03","april":"04",
        "may":"05","june":"06","july":"07","august":"08",
        "september":"09","october":"10","november":"11","december":"12"
    }
    m = re.search(r"(\d{1,2})\s+(\w+),?\s+(\d{4})", raw, re.I)
    if m:
        day = m.group(1).zfill(2)
        mon = months.get(m.group(2).lower())
        yr  = m.group(3)
        if mon:
            return f"{yr}-{mon}-{day}"
    m = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})", raw)
    if m:
        day = m.group(1).zfill(2)
        mon = m.group(2).zfill(2)
        yr  = m.group(3)
        if len(yr) == 2:
            yr = f"20{yr}" if int(yr) <= 30 else f"19{yr}"
        return f"{yr}-{mon}-{day}"
    return raw.strip()

def clean_text(text: str) -> str:
    text = re.sub(r"\[Cites\s+\d+.*?\]",         "", text, flags=re.I | re.S)
    text = re.sub(r"Page\s*-?\s*\d+\s*of\s*\d+", "", text, flags=re.I)
    text = re.sub(r"::: Downloaded on.*?:::",      "", text, flags=re.I | re.S)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def infer_domain_tags(body: str, sections: list[str]) -> dict:
    body_lower   = body.lower()
    sections_str = " ".join(sections)
    best = {"domain": "general", "subdomain": "unclassified", "confidence": 0.0}
    for domain, subdomain, sec_hints, kw_hints in DOMAIN_RULES:
        sec_match = sum(1 for s in sec_hints if s.lower() in sections_str.lower())
        kw_match  = sum(1 for kw in kw_hints if kw.lower() in body_lower)
        if sec_match > 0 or kw_match >= 2:
            conf = min(1.0, 0.3 + 0.2 * min(sec_match, 1) + 0.1 * kw_match)
            if conf > best["confidence"]:
                best = {"domain": domain, "subdomain": subdomain, "confidence": conf}
    return best

def compute_importance_score(cited_by: int, court_type: str, year: int | None) -> float:
    score = 0.0
    if court_type == "Supreme Court":   score += 0.40
    elif court_type == "High Court":    score += 0.25
    else:                               score += 0.05
    if cited_by >= 500:   score += 0.40
    elif cited_by >= 100: score += 0.25
    elif cited_by >= 20:  score += 0.15
    elif cited_by >= 5:   score += 0.05
    if year and year >= 2015:  score += 0.15
    elif year and year >= 2005: score += 0.08
    return round(min(score, 1.0), 3)

def infer_court_type(court: str) -> str:
    c = (court or "").lower()
    if "supreme" in c:  return "Supreme Court"
    if "high court" in c: return "High Court"
    if "district" in c:   return "District Court"
    if "sessions" in c:   return "Sessions Court"
    return "Other"

def passes_quality_gate(doc: dict) -> bool:
    ct = doc["court_type"]
    cb = doc["cited_by"]
    sc = doc["importance_score"]
    if ct == "Supreme Court":  return True
    if ct == "High Court":     return cb >= 3
    if ct == "District Court": return cb >= 15
    return sc >= 0.25

def score_authority(cited_by: int, court_type: str) -> str:
    bonus = 20 if court_type == "Supreme Court" else 0
    eff   = cited_by + bonus
    if eff >= 500: return "high"
    if eff >= 50:  return "medium"
    return "low"

# ── CHUNKER ───────────────────────────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    # Chunking by characters instead of words
    paras = text.split("\n")
    chunks, buf, buf_chars = [], [], 0
    overlap_paras = max(1, CHUNK_OVERLAP // 50)

    for para in paras:
        para = para.strip()
        if not para:
            continue
        c = len(para)
        if buf_chars + c > CHUNK_SIZE and buf:
            candidate = " ".join(buf)
            if len(candidate) >= MIN_CHARS:
                chunks.append(candidate)
            buf = buf[-overlap_paras:] if len(buf) >= overlap_paras else buf
            buf_chars = sum(len(b) for b in buf)
        buf.append(para)
        buf_chars += c

    if buf:
        candidate = " ".join(buf)
        if len(candidate) >= MIN_CHARS:
            chunks.append(candidate)

    return chunks

# ── WRITER ────────────────────────────────────────────────────────────────────

def write_chunks(doc: dict, out_file, seen_chunks: set) -> int:
    chunks = chunk_text(doc["body"])
    base   = {k: v for k, v in doc.items() if k != "body"}
    written = 0

    for i, chunk in enumerate(chunks):
        if len(chunk.split()) < 80:
            continue
        if not any(w in chunk.lower() for w in ["section", "court", "held", "accused", "petition"]):
            continue

        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
        if chunk_hash in seen_chunks:
            continue
        seen_chunks.add(chunk_hash)

        uid = hashlib.md5(f"{doc['tid']}_{i}".encode()).hexdigest()[:12]
        record = {
            "id":           uid,
            "chunk_index":  i,
            "total_chunks": len(chunks),
            "chunk_text":   chunk,
            "word_count":   len(chunk.split()),
            **base,
        }
        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
        written += 1

    return written

# ── FIX 6: Persist seen_chunks across resume sessions ────────────────────────

CHUNK_HASH_FILE = OUTPUT_DIR / ".seen_chunks.txt"

def load_seen_chunks() -> set:
    seen = set()
    if CHUNK_HASH_FILE.exists():
        with open(CHUNK_HASH_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    seen.add(line)
    print(f"Resuming — {len(seen)} chunk hashes loaded from disk")
    return seen

def save_seen_chunks(seen_chunks: set, new_hashes: set):
    """Append only new hashes to avoid rewriting the full set each time."""
    with open(CHUNK_HASH_FILE, "a", encoding="utf-8") as f:
        for h in new_hashes:
            f.write(h + "\n")

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    seen_tids   = set()
    total_docs  = 0
    total_chunks = 0

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Resume: reload seen TIDs
    for out_path in OUTPUT_DIR.rglob("*.jsonl"):
        try:
            with open(out_path, "r", encoding="utf-8") as existing:
                for line in existing:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        seen_tids.add(json.loads(line)["tid"])
                    except Exception:
                        pass
        except Exception as e:
            print(f"[resume warning] could not read {out_path}: {e}")
    print(f"Resuming — {len(seen_tids)} TIDs already in corpus")

    # FIX 6: Resume chunk hashes from disk
    seen_chunks     = load_seen_chunks()
    new_chunk_hashes = set()   # track only what's added this run for efficient append

    file_handles = {}

    def get_file_handle(domain, subdomain):
        key = (domain, subdomain)
        if key not in file_handles:
            domain_dir = OUTPUT_DIR / domain
            domain_dir.mkdir(exist_ok=True)
            file_handles[key] = open(domain_dir / f"{subdomain}.jsonl", "a", encoding="utf-8")
        return file_handles[key]

    stats = {"total_docs": 0, "total_chunks": 0, "domains": {}}

    # FIX 5: track general-bucket count for leakage monitoring
    general_doc_count = 0

    try:
        for domain, subdomains in DOMAIN_QUERIES.items():
            for subdomain, query_list in subdomains.items():
                for query, pages in query_list:
                    print(f"\nQuery: '{query}'")
                    for page in range(pages):
                        tids = search_tids(query, page)
                        print(f"  page {page} → {len(tids)} TIDs")
                        polite_sleep()

                        for tid in tids:
                            if tid in seen_tids:
                                print(f"    skip (duplicate): {tid}")
                                continue

                            html = fetch_doc_html(tid)
                            if not html:
                                continue

                            doc = parse_html(html, tid)
                            if not doc:
                                print(f"    skip (parse failed): {tid}")
                                continue

                            if not passes_quality_gate(doc):
                                print(f"    skip (quality gate): {doc['case_name'][:50]}")
                                continue

                            if doc.get("confidence", 0) < 0.4:
                                doc["domain"]    = "general"
                                doc["subdomain"] = "unclassified"

                            d_key  = doc["domain"]
                            sd_key = doc["subdomain"]

                            # FIX 5: monitor general leakage
                            if d_key == "general":
                                general_doc_count += 1
                                print(f"    [WARNING] Unclassified: {doc['case_name'][:50]}")
                                leak_pct = general_doc_count / max(total_docs, 1) * 100
                                if leak_pct > 10:
                                    print(f"    [ALERT] General bucket is {leak_pct:.1f}% of corpus — rules may be too weak")

                            if d_key not in stats["domains"]:
                                stats["domains"][d_key] = {}
                            if sd_key not in stats["domains"][d_key]:
                                stats["domains"][d_key][sd_key] = {
                                    "docs": 0, "chunks": 0,
                                    "sum_score": 0.0, "sections": {}
                                }

                            sd_stats = stats["domains"][d_key][sd_key]

                            # FIX 1: per-subdomain cap from SUBDOMAIN_CAPS dict
                            cap = SUBDOMAIN_CAPS.get((d_key, sd_key), DEFAULT_CAP)
                            if sd_stats["chunks"] >= cap:
                                print(f"    skip (subdomain cap {cap}): {doc['case_name'][:50]}")
                                continue

                            # Track hashes before writing so we can persist new ones
                            pre_count = len(seen_chunks)

                            out_file = get_file_handle(d_key, sd_key)
                            n_chunks = write_chunks(doc, out_file, seen_chunks)

                            if n_chunks == 0:
                                print(f"    skip (no valid chunks): {doc['case_name'][:50]}")
                                continue

                            # Collect newly added hashes for persistence
                            new_count = len(seen_chunks)
                            if new_count > pre_count:
                                # seen_chunks is a set; we can't diff cheaply, so we
                                # snapshot just the count and append a sentinel per doc
                                # instead. Better: pass new hashes out of write_chunks.
                                # (See note below — we patch write_chunks to return them.)
                                pass

                            out_file.flush()
                            seen_tids.add(tid)
                            total_docs   += 1
                            total_chunks += n_chunks

                            sd_stats["docs"]      += 1
                            sd_stats["chunks"]    += n_chunks
                            sd_stats["sum_score"] += doc["importance_score"]
                            for sec in doc["sections"]:
                                sd_stats["sections"][sec] = sd_stats["sections"].get(sec, 0) + 1

                            print(
                                f"    saved: {doc['case_name'][:55]:<55} "
                                f"| cited_by={doc['cited_by']:>6} "
                                f"| chunks={n_chunks} "
                                f"| conf={doc['confidence']:.2f}"
                            )

    finally:
        for h in file_handles.values():
            h.close()

        # FIX 6: Persist entire seen_chunks set (overwrite for correctness)
        with open(CHUNK_HASH_FILE, "w", encoding="utf-8") as f:
            for h in seen_chunks:
                f.write(h + "\n")
        print(f"Persisted {len(seen_chunks)} chunk hashes to {CHUNK_HASH_FILE}")

    stats["total_docs"]   = total_docs
    stats["total_chunks"] = total_chunks

    # FIX 5: add general leakage ratio to stats output
    stats["general_doc_count"] = general_doc_count
    stats["general_leakage_pct"] = round(
        general_doc_count / max(total_docs, 1) * 100, 2
    )

    for ds in stats["domains"].values():
        for sds in ds.values():
            if sds["docs"] > 0:
                sds["avg_importance_score"] = round(sds["sum_score"] / sds["docs"], 3)
            del sds["sum_score"]

    with open(OUTPUT_DIR / "stats.json", "w", encoding="utf-8") as sf:
        json.dump(stats, sf, indent=2)

    print(f"\n{'─'*60}")
    print(f"  Documents saved   : {total_docs}")
    print(f"  Total chunks      : {total_chunks}")
    print(f"  General leakage   : {stats['general_leakage_pct']}%")
    print(f"  Output directory  : corpus/")
    print(f"  Stats saved       : corpus/stats.json")
    print(f"{'─'*60}")

if __name__ == "__main__":
    main()