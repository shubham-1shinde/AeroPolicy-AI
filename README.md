# AeroPolicy AI — Airline Booking & Policy Assistant

A complete, production-grade airline booking website and AI policy assistant for the fictional **AeroVista Airlines**. The system addresses the fundamental safety and legal failure demonstrated by the **Air Canada Chatbot Refund Ruling** (*Moffatt v. Air Canada*): the AI assistant is strictly bound to official backend policy documents and will never invent policies, promise unapproved refunds, or assert unsupported eligibility.

---

## Architecture Overview

```text
aeropolicy-ai/
├── frontend/                     # React 18 + Vite + Tailwind CSS + Lucide
│   ├── src/
│   │   ├── components/           # Navbar, Hero, Booking Widget, ChatbotDrawer, etc.
│   │   ├── services/             # API client connecting to FastAPI backend
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/                      # Python 3.12 + FastAPI + FAISS + Gemini 2.5 Flash
│   ├── app/
│   │   ├── api/                  # Endpoints: /chat, /policy/*, /health
│   │   ├── core/                 # Config (Pydantic Settings), Admin Security
│   │   ├── models/               # Pydantic schemas
│   │   ├── services/             # Gemini 2.5 Flash integration & Verification layer
│   │   ├── rag/                  # SHA-256 change detection, splitters, local FAISS
│   │   └── main.py               # FastAPI application lifecycle & CORS
│   ├── public/
│   │   └── airline_policy.md     # Primary airline tariff policy document
│   ├── data/
│   │   ├── vectorstore/          # Persistent FAISS index and chunk storage
│   │   └── metadata/             # SHA-256 hash tracking metadata
│   ├── tests/                    # 18 automated backend pytest suites
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
└── README.md
```

---

## Key Features

1. **Air Canada Ruling Safeguard:**
   In *Moffatt v. Air Canada*, a chatbot promised a passenger that they could apply for a bereavement refund retroactively after purchasing a regular ticket. AeroPolicy AI enforces a verification layer preventing this failure:
   - AeroVista Policy Section 4 establishes that bereavement discounts must be arranged **prior** to ticket issuance.
   - Retroactive bereavement refunds on standard tickets are explicitly prohibited.
   - The chatbot abstains from granting or promising refunds and references the exact policy constraints.

2. **SHA-256 Document Change Detection:**
   - Ingestion is optimized so the document is **not** re-embedded on every question or server restart.
   - The backend computes the SHA-256 checksum of `airline_policy.md` and compares it to `data/metadata/policy_index_meta.json`.
   - If the hash matches, the persistent FAISS vector store is loaded instantly without re-embedding.
   - If the file is modified, it atomically updates the vector store and records the new hash.
   - Thread-safe locks prevent concurrent indexing operations.

3. **Grounded 5-Point Safe Answer Format:**
   For consequential questions (refunds, cancellations, fees, delays), answers follow a structured template:
   1. *What the policy says*
   2. *How it applies*
   3. *What is not confirmed*
   4. *Next step*
   5. *Source citations*

4. **Persistent Vector Store:**
   - Runs locally using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional normalized embeddings).
   - Local FAISS index with Inner Product (Cosine Similarity).
   - Zero external cloud vector store dependencies.

---

## Prerequisites

- **Python 3.10+** (tested on Python 3.12)
- **Node.js 18+** & **npm**

---

## Setup & Startup Instructions

### 1. Backend Setup

#### Windows PowerShell:
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create environment file from template
Copy-Item .env.example .env

# Edit .env and insert your Gemini API Key:
# GEMINI_API_KEY=your_actual_api_key_here
```

#### macOS / Linux Terminal:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

#### Run the Backend Server:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

---

### 2. Frontend Setup

In a new terminal window:

```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Application status, vector index state, chunk count |
| `POST` | `/api/chat` | Answer policy question with RAG, citations & verification |
| `GET` | `/api/policy/status` | Current file hash, indexed hash, status (`READY`/`OUTDATED`) |
| `POST` | `/api/policy/reindex` | Trigger policy re-indexing (Requires `X-Admin-Token` header) |
| `GET` | `/api/policy/sections` | List available policy sections & chunk distribution |
| `GET` | `/api/policy/source/{id}` | Safely view authorized source chunk text |

---

## Automated Test Suite

The project includes 18 automated tests covering indexing, change detection, retrieval accuracy, Air Canada scenario handling, anti-hallucination overrides, and API security.

To run tests:

```powershell
cd backend
python -m pytest -v
```

### Key Test Coverage:
- `test_air_canada_bereavement_scenario`: Verifies that post-purchase bereavement refund requests do not receive refund promises.
- `test_post_generation_anti_hallucination_override`: Verifies the verification layer catches rogue LLM refund promises.
- `test_unchanged_document_hash_skips_reembedding`: Validates SHA-256 skip mechanism.
- `test_modified_policy_triggers_reindexing`: Verifies that editing policy markdown triggers re-indexing.
- `test_unsupported_question_produces_abstention`: Ensures questions without policy evidence result in safe abstention.
- `test_reindex_authorization_protection`: Verifies admin token security (`X-Admin-Token`).
- `test_concurrent_requests_do_not_duplicate_indexing`: Confirms thread locks prevent indexing race conditions.

---

## Modifying the Policy Document

The primary policy file is located at:
`backend/public/airline_policy.md`

1. Open `backend/public/airline_policy.md` and edit any section.
2. Restart the backend OR trigger manual re-indexing via curl/PowerShell:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/policy/reindex" -Method POST -Headers @{ "X-Admin-Token" = "change-this-token" }
   ```
3. The backend calculates the new SHA-256 hash, updates the FAISS vector index, and stores updated metadata in `data/metadata/policy_index_meta.json`.

---

## Limitations and Future Integration Options

- **Simulated Inventory:** Flight schedules and pricing are demonstration mock data. In production, this would integrate with an airline GDS (e.g., Amadeus or Sabre API).
- **Booking Actions:** The chatbot assists with policy rules and does not process live payment refunds. Live refund execution requires human review or authorized ticket office credentials.
- **Multi-Document Support:** The ingestion loader supports Markdown, PDF, and DOCX files. Additional regulatory documents can be added to `backend/public/`.
