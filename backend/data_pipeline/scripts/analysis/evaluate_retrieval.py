import os
from retrieval_from_qdrant import LegalRetriever

test_cases = [
    # --- ORIGINAL CASES ---
    {
        "query": "rights of manual scavengers",
        "expected_domain": "legal_constitutional",
        "expected_keywords": ["Article 17", "Manual Scavengers Act", "Sukanya Shantha"]
    },
    {
        "query": "bail conditions for murder accused",
        "expected_domain": "legal_criminal",
        "expected_keywords": ["CrPC 437", "bail", "heinous offence"]
    },
    {
        "query": "consumer complaint against insurance company",
        "expected_domain": "legal_consumer",
        "expected_keywords": ["CDRA", "deficiency of service", "NCDRC"]
    },
    {
        "query": "divorce on grounds of cruelty",
        "expected_domain": "legal_family",
        "expected_keywords": ["Hindu Marriage Act", "Section 13", "cruelty"]
    },

    # --- NEW DOMAIN SPECIFIC CASES ---
    # Constitutional
    {"query": "can police arrest without FIR under article 22", "expected_domain": "legal_constitutional", "expected_keywords": ["Article 22", "fundamental right", "arrest"]},
    {"query": "right to privacy in digital surveillance", "expected_domain": "legal_constitutional", "expected_keywords": ["Privacy", "Article 21", "Puttaswamy"]},
    {"query": "reservation policy for OBC in government jobs", "expected_domain": "legal_constitutional", "expected_keywords": ["Reservation", "Article 16", "Indra Sawhney"]},
    {"query": "writ of habeas corpus when to file", "expected_domain": "legal_constitutional", "expected_keywords": ["Writ", "Habeas Corpus", "detention"]},
    {"query": "freedom of speech limits in India", "expected_domain": "legal_constitutional", "expected_keywords": ["Article 19", "Reasonable restrictions"]},

    # Criminal
    {"query": "anticipatory bail in dowry harassment case", "expected_domain": "legal_criminal", "expected_keywords": ["438", "Bail", "498A"]},
    {"query": "punishment for repeat offender under IPC", "expected_domain": "legal_criminal", "expected_keywords": ["IPC", "Sentence", "Punishment"]},
    {"query": "FIR quashing grounds in high court", "expected_domain": "legal_criminal", "expected_keywords": ["482", "Quash", "FIR"]},
    {"query": "self defence as exception to murder charge", "expected_domain": "legal_criminal", "expected_keywords": ["Self defence", "IPC 96", "IPC 300"]},
    {"query": "juvenile offender trial procedure POCSO", "expected_domain": "legal_criminal", "expected_keywords": ["Juvenile", "POCSO", "JJ Act"]},

    # Consumer
    {"query": "builder not delivering flat on time compensation", "expected_domain": "legal_consumer", "expected_keywords": ["RERA", "Possession", "Compensation"]},
    {"query": "mobile phone defective product replacement", "expected_domain": "legal_consumer", "expected_keywords": ["Defective", "Warranty", "Replacement"]},
    {"query": "hospital negligence consumer forum complaint", "expected_domain": "legal_consumer", "expected_keywords": ["Medical negligence", "Consumer forum", "Deficiency"]},
    {"query": "bank wrongly deducted charges refund", "expected_domain": "legal_consumer", "expected_keywords": ["Bank", "Refund", "Service charge"]},
    {"query": "online shopping fraud complaint procedure", "expected_domain": "legal_consumer", "expected_keywords": ["E-commerce", "Fraud", "Complaint"]},

    # Family
    {"query": "wife claiming maintenance after mutual divorce", "expected_domain": "legal_family", "expected_keywords": ["Maintenance", "125", "Alimony"]},
    {"query": "child custody father vs mother rights", "expected_domain": "legal_family", "expected_keywords": ["Custody", "Guardian", "Welfare"]},
    {"query": "property rights of daughter in ancestral property", "expected_domain": "legal_family", "expected_keywords": ["Hindu Succession", "Daughter", "Coparcenary"]},
    {"query": "second marriage without divorce validity", "expected_domain": "legal_family", "expected_keywords": ["Bigamy", "Validity", "Marriage"]},
    {"query": "domestic violence complaint by husband", "expected_domain": "legal_family", "expected_keywords": ["Domestic Violence", "PWDVA"]},

    # Labour
    {"query": "wrongful termination without notice period", "expected_domain": "legal_labour", "expected_keywords": ["Termination", "Notice", "Labour"]},
    {"query": "maternity leave denial by private employer", "expected_domain": "legal_labour", "expected_keywords": ["Maternity", "Benefit", "Leave"]},
    {"query": "minimum wages not paid by contractor", "expected_domain": "legal_labour", "expected_keywords": ["Minimum Wage", "Contractor", "Labour"]},
    {"query": "provident fund withdrawal rules after resignation", "expected_domain": "legal_labour", "expected_keywords": ["PF", "Provident Fund", "Withdrawal"]},
    {"query": "sexual harassment complaint at workplace POSH", "expected_domain": "legal_labour", "expected_keywords": ["POSH", "Harassment", "Workplace"]},

    # Motor Accident
    {"query": "compensation for permanent disability in road accident", "expected_domain": "legal_motor_accident", "expected_keywords": ["MACT", "Disability", "Compensation"]},
    {"query": "hit and run case no vehicle identified claim", "expected_domain": "legal_motor_accident", "expected_keywords": ["Hit and run", "Solatium", "Section 161"]},
    {"query": "passenger injured in bus accident who to sue", "expected_domain": "legal_motor_accident", "expected_keywords": ["MACT", "Negligence", "Compensation"]},
    {"query": "drunk driver accident insurance claim rejected", "expected_domain": "legal_motor_accident", "expected_keywords": ["Drunk", "Insurance", "Exclusion"]},
    {"query": "death in auto rickshaw accident family compensation", "expected_domain": "legal_motor_accident", "expected_keywords": ["MACT", "Death", "Dependency"]},

    # --- HARD CASES (CROSS-DOMAIN) ---
    {
        "query": "bonded labour fundamental rights violation",
        "expected_domain": "legal_constitutional",
        "expected_keywords": ["Article 23", "forced labour", "bonded labour"]
    },
    {
        "query": "car insurance company rejecting valid claim",
        "expected_domain": "legal_consumer",
        "expected_keywords": ["deficiency of service", "insurance", "consumer forum"]
    },
    {
        "query": "husband beating wife IPC section applicable",
        "expected_domain": "legal_criminal",
        "expected_keywords": ["498A", "Beating", "Cruelty"]
    },
    {
        "query": "police custodial torture article 21 violation",
        "expected_domain": "legal_constitutional",
        "expected_keywords": ["Article 21", "Custodial", "Torture"]
    },
    {
        "query": "equal pay for equal work government employee",
        "expected_domain": "legal_constitutional",
        "expected_keywords": ["Article 14", "Article 39", "Equal pay"]
    },
]

def evaluate():
    retriever = LegalRetriever()
    correct_domain = 0
    total_score = 0
    keyword_hits = 0

    print(f"\nStarting evaluation on {len(test_cases)} test cases...")

    for tc in test_cases:
        results = retriever.search(tc["query"], top_k=5)
        
        if not results:
            print(f"\nQuery: {tc['query']}")
            print("  [ERROR] No results found!")
            continue

        # 1. Domain routing accuracy
        domain_correct = results[0]["domain"] == tc["expected_domain"]
        if domain_correct:
            correct_domain += 1

        # 2. Average retrieval score
        avg_score = sum(r["score"] for r in results) / len(results)
        total_score += avg_score

        # 3. Keyword presence in retrieved chunks
        combined_text = " ".join(r["chunk_text"] for r in results)
        hits = sum(1 for kw in tc["expected_keywords"] if kw.lower() in combined_text.lower())
        hit_rate = hits / len(tc["expected_keywords"])
        keyword_hits += hit_rate

        status = "PASS" if domain_correct else "FAIL"
        print(f"\nQuery: {tc['query']}")
        print(f"  Result: {status} | Domain: {results[0]['domain']} (Expected: {tc['expected_domain']})")
        print(f"  Avg score: {avg_score:.4f} | Keyword Hit Rate: {hit_rate:.2%}")

    num_cases = len(test_cases)
    print(f"\n{'='*50}")
    print(f"FINAL SUMMARY")
    print(f"{'='*50}")
    print(f"Domain accuracy:      {correct_domain}/{num_cases} ({correct_domain/num_cases:.2%})")
    print(f"Avg retrieval score:  {total_score/num_cases:.4f}")
    print(f"Avg keyword hit rate: {keyword_hits/num_cases:.2%}")
    print(f"{'='*50}")

if __name__ == "__main__":
    evaluate()
