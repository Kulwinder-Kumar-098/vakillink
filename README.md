# VakilLink Fullstack Project

VakilLink is a production-ready legal intelligence platform that combines a professional dashboard with a high-performance RAG (Retrieval-Augmented Generation) pipeline for Indian Case Law.

## Project Structure

```text
vakillink/
├── frontend/           # React + Vite Dashboard (Admin, Lawyer, Client)
├── backend/            # Unified FastAPI Backend
│   ├── app/            # Dashboard Logic (Auth, Lawyers, Admin, Chat)
│   ├── ai/             # Legal RAG Pipeline (Retrieval, Embeddings, LLM)
│   ├── data_pipeline/  # Scrapers and Data Ingestion logic
│   ├── scripts/        # Maintenance and one-off scripts
│   ├── main.py         # Unified API Entry Point
│   └── requirements.txt
├── .env.example        # Unified Configuration Template
└── README.md
```

## Features

- **Multi-Role Dashboards:** Specialized views for Admins, Lawyers, and Clients.
- **Legal RAG Pipeline:** Intelligent retrieval of Indian precedents using Qdrant and Llama 3 (via Groq).
- **Semantic Search:** High-performance search across 17,000+ legal chunks.
- **Unified API:** Single FastAPI service managing both dashboard state and AI intelligence.

## Setup Instructions

### Backend

1. Navigate to `backend/`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` in the root and fill in the keys.
4. Run the server: `uvicorn main:app --reload`.

### Frontend

1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Run the dev server: `npm run dev`.

## Data Pipeline

The `backend/data_pipeline` contains scripts for scraping Indian Kanoon and other legal sources, processing them into chunks, and uploading them to Qdrant. Maintenance scripts are available in `backend/scripts`.
