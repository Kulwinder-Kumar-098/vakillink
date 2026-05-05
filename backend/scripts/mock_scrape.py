import json
import os
from pathlib import Path

MOCK_DATA = {
    "corpus/criminal/criminal_cheque_bounce.jsonl": [
        "The Supreme Court in Dashrath Rupsingh Rathod vs State of Maharashtra held that Section 138 NI Act complaint must be filed where cheque was presented for payment, not where it was drawn.",
        "Under Section 138 of the Negotiable Instruments Act, the dishonour of a cheque due to insufficient funds is a criminal offence.",
        "A statutory notice of 15 days is mandatory before filing a complaint under Section 138 of the Negotiable Instruments Act."
    ],
    "corpus/criminal/criminal_cybercrime.jsonl": [
        "IT Act Section 66 deals with computer-related offences. Section 66C and 66D cover identity theft and cheating by personation using a computer resource.",
        "Online financial fraud and phishing are covered under Section 420 IPC read with Section 66 of the Information Technology Act.",
        "The High Court noted that for cybercrime FIRs involving UPI fraud, the jurisdiction can be where the victim's bank account is located."
    ],
    "corpus/criminal/criminal_anticipatory_bail.jsonl": [
        "The Supreme Court in Gurbaksh Singh Sibbia vs State of Punjab laid down guidelines for granting anticipatory bail under Section 438 CrPC.",
        "Section 438 CrPC allows a person expecting arrest in a non-bailable offence to approach the High Court or Sessions Court for anticipatory bail.",
        "Anticipatory bail conditions often include joining the investigation and not tampering with evidence."
    ],
    "corpus/consumer/consumer_rera_builder.jsonl": [
        "In cases of builder delay in possession, the consumer has the right to approach either the Consumer Forum or RERA for relief.",
        "The NCDRC held that an unreasonable delay in handing over flat possession constitutes deficiency of service.",
        "Under the Consumer Protection Act, a buyer can claim a refund with interest if the builder fails to deliver the apartment on time."
    ],
    "corpus/consumer/consumer_medical_negligence.jsonl": [
        "The Supreme Court in Jacob Mathew vs State of Punjab held that to prove medical negligence under criminal law, the negligence must be gross.",
        "A hospital can be held vicariously liable for the deficiency in service caused by the medical negligence of its doctors.",
        "In medical negligence cases before the consumer forum, the burden of proof generally lies on the complainant to establish duty of care and its breach."
    ],
    "corpus/consumer/consumer_ecommerce_airlines.jsonl": [
        "E-commerce platforms are liable for deficiency in service if they fail to deliver products as described or refuse valid refunds.",
        "Airline delays without justifiable causes like weather can amount to deficiency in service under the Consumer Protection Act.",
        "Online sellers cannot escape liability by claiming they are merely intermediaries if they exercise control over the delivery or return process."
    ],
    "corpus/family/family_maintenance_alimony.jsonl": [
        "The Supreme Court in Rajnesh v Neha (2020) laid down comprehensive guidelines for determining maintenance in matrimonial disputes.",
        "Criteria for calculating alimony include the income and standard of living of both spouses, and the needs of the dependent wife.",
        "Interim maintenance must be sufficient to allow the dependent spouse to live with reasonable comfort pendente lite."
    ],
    "corpus/family/family_mutual_consent_divorce.jsonl": [
        "The Supreme Court in Amardeep Singh v. Harveen Kaur held that the 6-month statutory cooling-off period under Section 13B(2) of HMA is directory, not mandatory.",
        "A mutual consent divorce requires that the parties have lived separately for at least one year and have agreed that they cannot live together.",
        "The court may waive the cooling-off period if waiting would only prolong the agony and all mediation efforts have failed."
    ]
}

def create_mock_data():
    for filepath, texts in MOCK_DATA.items():
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for text in texts:
                record = {
                    "chunk_text": text,
                    "case_name": "Mock Case vs State",
                    "law_name": "Relevant Act",
                    "legal_issue": "Mock legal issue",
                    "acts": ["Relevant Act"],
                    "sections": ["Section X"],
                    "cited_articles": [],
                    "cited_sections": ["Section X"],
                    "cited_acts": ["Relevant Act"]
                }
                f.write(json.dumps(record) + '\n')

if __name__ == "__main__":
    create_mock_data()
    print("Mock data generated.")
