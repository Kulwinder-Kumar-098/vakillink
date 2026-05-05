"""
scripts/seed_lawyers.py
=======================
Seeds the Supabase database with realistic dummy lawyer data for all 6
legal specialization domains used by the VakeelLink RAG pipeline.

Tables written:
  - lawyers
  - lawyer_availability
  - lawyer_reviews

Usage (from project root):
    cd backend
    python -m scripts.seed_lawyers

Requires a valid .env file in the backend/ directory with:
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
"""

import os
import sys
import uuid
import random
from datetime import datetime, timezone

# ── allow running as a module from backend/ ──────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.core.supabase_client import supabase
from app.core.utils import generate_bar_council_id

SUPABASE_URL              = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

client = supabase.get_admin_client()

# ─────────────────────────────────────────────────────────────────────────────
# Domain → lawyer definitions
# (6 domains matching the RAG pipeline's domain router)
# ─────────────────────────────────────────────────────────────────────────────

LAWYERS_DATA = [

    # ── 1. Criminal Law ───────────────────────────────────────────────────────
    {
        "name": "Adv. Rajesh Kumar Verma",
        "specialization": "criminal",
        "location": "New Delhi",
        "experience_years": 18,
        "rating": 4.8,
        "bio": (
            "Former Additional Sessions Judge turned defence counsel. "
            "Specialises in bail proceedings, anticipatory bail, and trial defence "
            "under IPC, CrPC, NDPS Act, and PMLA. Led acquittals in over 40 sessions trials. "
            "Fluent in Hindi, Punjabi, and English."
        ),
        "areas_of_practice": [
            "Bail & Anticipatory Bail",
            "Sessions & High Court Trials",
            "NDPS & PMLA Matters",
            "White-Collar Crime Defence",
            "Cybercrime",
        ],
        "fee_per_consultation": 2500,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=rajesh_verma",
    },
    {
        "name": "Adv. Priya Nair",
        "specialization": "criminal",
        "location": "Mumbai",
        "experience_years": 9,
        "rating": 4.5,
        "bio": (
            "Bombay High Court advocate with a focus on women's rights in criminal proceedings, "
            "domestic violence (PWDVA), sexual offence trials (POCSO), and 498A matters. "
            "Regular speaker at NLSIU and empanelled with Maharashtra Legal Services Authority."
        ),
        "areas_of_practice": [
            "POCSO & Sexual Offence Trials",
            "Domestic Violence (PWDVA)",
            "498A IPC Matters",
            "Juvenile Justice",
            "Victim Representation",
        ],
        "fee_per_consultation": 1800,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=priya_nair",
    },

    # ── 2. Labour / Employment Law ────────────────────────────────────────────
    {
        "name": "Adv. Suresh Ramachandran",
        "specialization": "labour",
        "location": "Chennai",
        "experience_years": 22,
        "rating": 4.9,
        "bio": (
            "Doyen of labour law at the Madras High Court. Represented trade unions, "
            "public sector undertakings, and multinational corporations in disputes under "
            "the Industrial Disputes Act, Factories Act, and the new Labour Codes (2019–2020). "
            "Author of two textbooks on Indian employment law."
        ),
        "areas_of_practice": [
            "Industrial Disputes & Strikes",
            "Wrongful Termination",
            "Labour Codes (2020)",
            "ESIC & PF Disputes",
            "Workmen Compensation",
        ],
        "fee_per_consultation": 3000,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=suresh_ram",
    },
    {
        "name": "Adv. Meenakshi Iyer",
        "specialization": "labour",
        "location": "Bengaluru",
        "experience_years": 7,
        "rating": 4.3,
        "bio": (
            "Karnataka High Court advocate specialising in IT-sector employment disputes, "
            "non-compete clauses, POSH Act internal complaints, and maternity benefit claims. "
            "Regularly counsels start-ups on HR compliance frameworks."
        ),
        "areas_of_practice": [
            "POSH Act & Sexual Harassment",
            "Non-Compete & NDA Disputes",
            "Maternity Benefits Act",
            "IT-Sector Employment",
            "Gratuity & Bonus Claims",
        ],
        "fee_per_consultation": 1500,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=meenakshi_iyer",
    },

    # ── 3. Family / Matrimonial Law ───────────────────────────────────────────
    {
        "name": "Adv. Vikram Singh Rathore",
        "specialization": "family",
        "location": "Jaipur",
        "experience_years": 14,
        "rating": 4.7,
        "bio": (
            "Principal Family Court advocate at Jaipur with deep expertise in contested divorces, "
            "Hindu succession disputes, child custody, and inter-country custody under the Hague "
            "Convention. Known for compassionate, result-oriented representation."
        ),
        "areas_of_practice": [
            "Contested Divorce (HMA / SMA)",
            "Child Custody & Guardianship",
            "Maintenance (Section 125 CrPC)",
            "Hindu Succession & Inheritance",
            "Domestic Violence Protection",
        ],
        "fee_per_consultation": 2000,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=vikram_rathore",
    },
    {
        "name": "Adv. Ananya Bhattacharya",
        "specialization": "family",
        "location": "Kolkata",
        "experience_years": 6,
        "rating": 4.4,
        "bio": (
            "Calcutta High Court counsel with a focus on Muslim personal law, "
            "triple talaq cases (Muslim Women Protection Act 2019), maintenance under Muslim Women "
            "Act 1986, and adoption under Hindu Adoption Act and Juvenile Justice Act."
        ),
        "areas_of_practice": [
            "Muslim Personal Law",
            "Triple Talaq (2019 Act)",
            "Adoption (Hindu & JJ Act)",
            "Alimony & Mehr Claims",
            "Restitution of Conjugal Rights",
        ],
        "fee_per_consultation": 1200,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=ananya_bhat",
    },

    # ── 4. Property / Real Estate Law ────────────────────────────────────────
    {
        "name": "Adv. Harish Malhotra",
        "specialization": "property",
        "location": "New Delhi",
        "experience_years": 25,
        "rating": 4.9,
        "bio": (
            "Senior counsel before the Delhi High Court and NCLAT in property matters. "
            "Specialises in title disputes, DDA allotment cancellations, landlord-tenant "
            "evictions under Delhi Rent Control Act, and RERA builder complaints. "
            "Handled landmark property acquisitions by Government of Delhi."
        ),
        "areas_of_practice": [
            "Title Disputes & Mutation",
            "RERA Builder Complaints",
            "Landlord-Tenant (Rent Control)",
            "Property Acquisition & Compensation",
            "Co-operative Housing Society Disputes",
        ],
        "fee_per_consultation": 4000,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=harish_malhotra",
    },
    {
        "name": "Adv. Deepa Krishnaswamy",
        "specialization": "property",
        "location": "Hyderabad",
        "experience_years": 11,
        "rating": 4.6,
        "bio": (
            "Telangana & Andhra Pradesh High Court advocate focusing on agricultural land "
            "disputes, Dharani portal correction matters, encroachment removal, and "
            "stamp-duty disputes under the Registration Act. Bilingual practice (Telugu & English)."
        ),
        "areas_of_practice": [
            "Agricultural Land Disputes",
            "Dharani / Land Records",
            "Encroachment & Injunctions",
            "Stamp Duty & Registration",
            "Partition Suits",
        ],
        "fee_per_consultation": 1800,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=deepa_krishna",
    },

    # ── 5. Consumer / Civil Law ───────────────────────────────────────────────
    {
        "name": "Adv. Arjun Mehta",
        "specialization": "consumer",
        "location": "Ahmedabad",
        "experience_years": 10,
        "rating": 4.5,
        "bio": (
            "Gujarat High Court advocate practising before the National and State Consumer "
            "Disputes Redressal Commissions. Expert in insurance claim repudiation, "
            "e-commerce refund fraud, medical negligence compensation, and builder delays. "
            "Successfully recovered ₹4 crore+ in consumer awards."
        ),
        "areas_of_practice": [
            "Insurance Claim Repudiation",
            "Builder Delay Compensation (RERA)",
            "Medical Negligence",
            "E-Commerce Fraud",
            "Banking & Loan Disputes",
        ],
        "fee_per_consultation": 1500,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=arjun_mehta",
    },
    {
        "name": "Adv. Shalini Pandey",
        "specialization": "consumer",
        "location": "Lucknow",
        "experience_years": 5,
        "rating": 4.2,
        "bio": (
            "Allahabad High Court counsel specialising in District Consumer Forum filings, "
            "deficiency of service against telecom providers, government utility bills, and "
            "defective product liability. Offers affordable legal aid to first-time complainants."
        ),
        "areas_of_practice": [
            "Telecom & Internet Disputes",
            "Utility Bill Disputes",
            "Defective Products",
            "Education Service Deficiency",
            "Travel & Hospitality Claims",
        ],
        "fee_per_consultation": 800,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=shalini_pandey",
    },

    # ── 6. Constitutional / Human Rights Law ─────────────────────────────────
    {
        "name": "Adv. Farhan Qureshi",
        "specialization": "constitutional",
        "location": "New Delhi",
        "experience_years": 16,
        "rating": 4.8,
        "bio": (
            "Supreme Court of India advocate with a focus on Public Interest Litigation, "
            "fundamental rights enforcement (Articles 14, 19, 21), Right to Information (RTI) "
            "appeals before CIC, and manual scavengers' rehabilitation litigation. "
            "Former law clerk to a Supreme Court Judge."
        ),
        "areas_of_practice": [
            "Public Interest Litigation (PIL)",
            "Fundamental Rights (Art 14/19/21)",
            "RTI & Information Rights",
            "Manual Scavengers Rehabilitation",
            "Dalits & Scheduled Caste Rights (SC/ST Act)",
        ],
        "fee_per_consultation": 5000,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=farhan_qureshi",
    },
    {
        "name": "Adv. Kavitha Subramanian",
        "specialization": "constitutional",
        "location": "Chennai",
        "experience_years": 12,
        "rating": 4.7,
        "bio": (
            "Madras High Court advocate known for child rights PILs, LGBTQ+ rights cases "
            "post Section 377 reading-down, press freedom defences, and State Human Rights "
            "Commission petitions. Regular contributor to The Hindu op-ed on constitutional law."
        ),
        "areas_of_practice": [
            "Child Rights & POCSO",
            "LGBTQ+ Rights",
            "Press & Speech Freedom",
            "State Human Rights Commission",
            "Environmental Constitutional Rights",
        ],
        "fee_per_consultation": 3000,
        "is_verified": True,
        "profile_image_url": "https://i.pravatar.cc/300?u=kavitha_sub",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Availability templates (Mon=0 … Sun=6)
# ─────────────────────────────────────────────────────────────────────────────

WEEKDAY_SLOTS = [
    {"day_of_week": "Monday",    "start_time": "10:00", "end_time": "13:00"},
    {"day_of_week": "Monday",    "start_time": "14:00", "end_time": "17:00"},
    {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "13:00"},
    {"day_of_week": "Wednesday", "start_time": "14:00", "end_time": "17:00"},
    {"day_of_week": "Friday",    "start_time": "10:00", "end_time": "13:00"},
]

FULL_WEEK_SLOTS = WEEKDAY_SLOTS + [
    {"day_of_week": "Saturday",  "start_time": "11:00", "end_time": "14:00"},
]

# ─────────────────────────────────────────────────────────────────────────────
# Sample review templates per domain
# ─────────────────────────────────────────────────────────────────────────────

REVIEW_BANK = {
    "criminal": [
        ("Mohit Kapoor",  5, "Got bail within 48 hours. Exceptional command of CrPC."),
        ("Ritu Sharma",   4, "Very professional. Explained each step of the trial clearly."),
        ("Deepak Jain",   5, "Won the sessions case that everyone said was unwinnable. Brilliant."),
        ("Anita Singh",   4, "Compassionate approach during a difficult time. Highly recommend."),
        ("Sanjay Rao",    3, "Good lawyer but communication could be faster."),
    ],
    "labour": [
        ("Pradeep Kumar", 5, "Reinstated me after wrongful dismissal. Fought for 8 months."),
        ("Lakshmi Devi",  4, "Helped negotiate a great severance package. Very knowledgeable."),
        ("Ashwin Nair",   5, "Best labour lawyer in the city. Knows the new labour codes perfectly."),
        ("Fatima Khan",   4, "Solved my ESIC issue in one hearing. Very efficient."),
        ("Rajan Pillai",  3, "Took time but ultimately got my gratuity released."),
    ],
    "family": [
        ("Sunita Gupta",  5, "Got custody of my children. Handled the case with sensitivity."),
        ("Rohit Jha",     4, "Divorce finalised in 4 months. Transparent about fees."),
        ("Anjali Mishra", 5, "Excellent at negotiating maintenance. No court drama."),
        ("Vikash Tiwari", 4, "Guided me through Hindu succession dispute. Very patient."),
        ("Reena Malviya", 5, "Saved my family home from partition. Truly outstanding."),
    ],
    "property": [
        ("Gopal Agarwal", 5, "Recovered my plot after 12-year encroachment dispute. Legend."),
        ("Sudha Reddy",   4, "Helped me get RERA compensation from builder. Quick process."),
        ("Vinod Patel",   5, "Title cleared in 3 months. Thorough document verification."),
        ("Kamla Devi",    4, "Mutation done smoothly. Knows Dharani portal inside-out."),
        ("Srinivas Rao",  3, "Good but fees a bit high. Results delivered though."),
    ],
    "consumer": [
        ("Manish Verma",  5, "Got full insurance claim after repudiation. Fantastic."),
        ("Shweta Saxena", 4, "Consumer forum award received. Would recommend to everyone."),
        ("Arun Kumar",    5, "Resolved telecom dispute in 2 hearings. Very efficient."),
        ("Pooja Singh",   4, "Medical negligence compensation received. Very thorough."),
        ("Ravi Gupta",    3, "Process took longer than expected but successful outcome."),
    ],
    "constitutional": [
        ("Nidhi Joshi",   5, "Filed PIL for our community. Supreme Court passed direction."),
        ("Imran Sheikh",  4, "RTI appeal won at CIC. Very knowledgeable about information law."),
        ("Dalit Rights NGO", 5, "Champion of SC/ST rights. Our go-to constitutional lawyer."),
        ("Asha Devi",     5, "Helped me get my child's school admission through PIL. Hero."),
        ("Sunil Chauhan", 4, "Brilliant legal mind. Kept us informed throughout the case."),
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Seeding logic
# ─────────────────────────────────────────────────────────────────────────────

def seed_lawyers():
    print("=" * 60)
    print("VakeelLink — Lawyer Seed Script")
    print("=" * 60)

    inserted_ids: list[str] = []

    for lawyer in LAWYERS_DATA:
        lawyer_id = str(uuid.uuid4())
        # Generate a random Bar Council ID if not present
        bar_id = generate_bar_council_id()
        payload = {
            **lawyer, 
            "id": lawyer_id, 
            "bar_council_id": bar_id
        }

        try:
            res = client.table("lawyers").insert(payload).execute()
            if res.data:
                print(f"  ✅  Inserted lawyer: {lawyer['name']} ({lawyer['specialization']})")
                inserted_ids.append(lawyer_id)
            else:
                print(f"  ⚠️  No data returned for {lawyer['name']}")
        except Exception as e:
            print(f"  ❌  Failed to insert {lawyer['name']}: {e}")
            continue

        # Availability slots
        slots = FULL_WEEK_SLOTS if lawyer["experience_years"] > 10 else WEEKDAY_SLOTS
        avail_rows = [{"lawyer_id": lawyer_id, **slot} for slot in slots]
        try:
            client.table("lawyer_availability").insert(avail_rows).execute()
            print(f"       ↳  {len(avail_rows)} availability slots added")
        except Exception as e:
            print(f"       ⚠️  Availability insert failed: {e}")

        # Reviews
        reviews = REVIEW_BANK.get(lawyer["specialization"], [])
        review_rows = []
        for reviewer, rating, comment in reviews:
            review_rows.append({
                "lawyer_id":    lawyer_id,
                "reviewer_name": reviewer,
                "rating":       rating,
                "comment":      comment,
                "created_at":   datetime.now(timezone.utc).isoformat(),
            })
        try:
            client.table("lawyer_reviews").insert(review_rows).execute()
            print(f"       ↳  {len(review_rows)} reviews added")
        except Exception as e:
            print(f"       ⚠️  Reviews insert failed: {e}")

    print()
    print(f"✅  Seed complete — {len(inserted_ids)} lawyers inserted.")
    print("=" * 60)


if __name__ == "__main__":
    seed_lawyers()
