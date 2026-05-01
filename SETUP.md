# SETUP.md — Installation & Run Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ (for the React frontend)
- PostgreSQL 16 (running locally on port 5432)
- A Groq API key → https://console.groq.com

---

## 1. Clone / open the project

```bash
cd I:\April_VH\SQL_Agent
```

---

## 2. Create and activate the virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac / Linux
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .              # registers loyalty_agent as an importable package
```

---

## 4. Configure environment variables

```bash
copy .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=gsk_your_key_here

DB_USER=postgres
DB_PASS=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Loyalty_Dataset

RAW_DATA_FILE=I:\April_VH\SQL_Agent\Loyalty Data.xlsx
CLEANED_XLSX_OUTPUT=I:\April_VH\SQL_Agent\Loyalty_Data_Cleaned_All.xlsx
CLEANED_SOURCE_FILE=I:\April_VH\SQL_Agent\Loyalty_Data_Cleaned_All.xlsx
```

---

## 5. ETL — Clean the raw data

Reads `Loyalty Data.xlsx`, applies all 5 cleaning rules, saves `Loyalty_Data_Cleaned_All.xlsx`.

```bash
python -m loyalty_agent.etl.pipeline --mode clean
```

---

## 6. ETL — Push cleaned data into PostgreSQL

Auto-creates the `Loyalty_Dataset` database if it doesn't exist, then loads all 10 sheets as tables.

```bash
python -m loyalty_agent.etl.pipeline --mode push
```

Or do both steps at once:

```bash
python -m loyalty_agent.etl.pipeline --mode clean --push
```

Expected output:

```
✅  Connected to PostgreSQL  →  Loyalty_Dataset @ localhost:5432
📤  'transactions_us'          →  35,000 rows loaded
📤  'loyalty_accounts_us'      →  10,000 rows loaded
📤  'loyalty_affiliations_us'  →  10,000 rows loaded
📤  'credit_sales_us'          →  10,000 rows loaded
📤  'sales_us'                 →  10,000 rows loaded
📤  'transactions_ca'          →  10,000 rows loaded
📤  'loyalty_accounts_ca'       →   5,820 rows loaded
📤  'loyalty_affiliations_ca'  →   9,640 rows loaded
📤  'sales_ca'                 →  10,000 rows loaded
📤  'credit_sales_ca'          →  10,000 rows loaded
📊  Total rows pushed: 120,460
```

---

## 7. Start the FastAPI backend

```bash
.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```

API docs (Swagger UI): http://localhost:8000/docs

---

## 8. Start the React frontend

Open a second terminal:

```bash
cd loyalty-insights-hub
npm install
npm run dev
```

Opens at: http://localhost:5173

> The React app connects directly to the FastAPI backend at `http://localhost:8000`.
> CORS is already open on the backend — no proxy configuration needed.

---

## ETL Cleaning Rules Reference

| # | Rule | Problem fixed |
|---|------|---------------|
| 1 | Column Header Standardisation | `Total Amount ($)` → `total_amount_usd` — spaces and symbols break SQL |
| 2 | Mixed Data Type Fix | `rule_id`: `1`, `1X` mixed → all forced to string |
| 3 | Garbage Value Removal | `#####`, `"NULL"` text, `nan` → real database NULL |
| 4 | Date Standardisation | Timezone offsets (`+00:00`) stripped → naive UTC timestamps |
| 5 | Numeric Type Enforcement | `"1,200.50"` (text with comma) → `1200.50` (float) |

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check — DB + LLM status |
| GET | `/analytics/schema` | Full live database schema |
| POST | `/analytics/query` | Natural language → SQL → summary + chart |
| POST | `/analytics/refresh-schema` | Force schema reload after ETL push |
| GET | `/tables` | List all tables |
| GET | `/tables/{name}?limit=10` | Preview rows + stats for a table |

---

## Project Structure

```
loyalty_agent/          ← Core library
├── config/settings.py  ← All config from .env
├── db/                 ← DB engine + query helpers
├── etl/                ← 5-rule cleaner + DB loader + CLI pipeline
├── tools/              ← LLM tools (SQL gen, answer polish, chart suggest)
└── utils/              ← Helpers, logger, validators

backend/                ← FastAPI REST API
├── main.py
├── state.py
├── schemas.py
└── routers/

loyalty-insights-hub/   ← React + TypeScript frontend
├── src/
│   ├── api/client.ts   ← Axios client → http://localhost:8000
│   ├── components/     ← Sidebar, Chat, Charts
│   └── App.tsx
└── package.json
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'loyalty_agent'`**
→ Run `pip install -e .` inside the active venv.

**`fe_sendauth: no password supplied`**
→ `.env` file is missing or `DB_PASS` is empty.

**`No module named 'psycopg2'`**
→ Run `.venv\Scripts\pip.exe install psycopg2-binary`

**Streamlit shows "API Unreachable"**
→ This project no longer uses Streamlit. Use the React frontend in `loyalty-insights-hub/`.

**React frontend shows CORS error**
→ Make sure the FastAPI backend is running on port 8000. CORS is already open (`allow_origins=["*"]`).

**`npm: command not found`**
→ Install Node.js 18+ from https://nodejs.org
