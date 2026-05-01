# 💎 Loyalty Analytics Agent

> **Ask your database anything. In plain English.**

A production-grade, agentic AI system that sits on top of a relational loyalty database and lets anyone — analyst, manager, or executive — get instant answers without writing a single line of SQL.

You type: *"Who are the top 10 Gold-tier customers by points earned this year?"*
The system thinks, queries, and responds: a clean answer, the exact SQL it ran, a live data table, and an auto-generated chart. In under two seconds.

---

## The Problem It Solves

Enterprise loyalty data is locked inside relational databases. Getting answers requires a data analyst, a SQL query, a wait, and a spreadsheet. That pipeline is slow, expensive, and creates a bottleneck every time a stakeholder has a question.

This project eliminates that bottleneck entirely.

---

## How It Works — End to End

```
Raw Excel Data
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  ETL Pipeline  (loyalty_agent/etl/)                 │
│                                                     │
│  Rule 1 — Standardise column headers                │
│  Rule 2 — Fix mixed data types (ID columns)         │
│  Rule 3 — Remove garbage values (#####, NULL text)  │
│  Rule 4 — Normalise dates (strip timezones)         │
│  Rule 5 — Enforce numeric types (strip commas)      │
└──────────────────────┬──────────────────────────────┘
                       │  120,460 clean rows
                       ▼
         ┌─────────────────────────┐
         │   PostgreSQL Database   │
         │   (Loyalty_Dataset)     │
         │                         │
         │  10 tables, US + CA     │
         │  Transactions           │
         │  Loyalty Accounts       │
         │  Affiliations           │
         │  Sales                  │
         │  Credit Sales           │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │   FastAPI Backend       │
         │                         │
         │  Dynamic schema scan    │
         │  LLM: SQL generation    │  ← Llama-3.3-70B via Groq
         │  SQL execution          │
         │  LLM: Answer polishing  │  ← Llama-3.1-8B via Groq
         │  Chart suggestion       │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │   React Frontend        │
         │   (loyalty-insights-hub)│
         │                         │
         │  Chat interface         │
         │  Live SQL viewer        │
         │  Interactive data table │
         │  Auto Recharts charts   │
         │  Schema explorer        │
         │  Table previewer        │
         └─────────────────────────┘
```

---

## Architecture — Four Tiers

### Tier 1 — Data Integration (ETL Pipeline)
The pipeline reads raw `.xlsx` loyalty data across 10 sheets (US and Canada), applies five deterministic cleaning rules, and loads the result into a structured PostgreSQL database. It is idempotent — run it any number of times and the result is always consistent.

### Tier 2 — The Agent Brain (SQL Generation)
The core intelligence. A system prompt injects the live database schema dynamically — no hard-coded table names. The LLM (Llama-3.3-70B) receives the schema and the user's question, and returns a single executable PostgreSQL SELECT statement. A safety validator blocks any non-SELECT output before it ever reaches the database.

### Tier 3 — Execution Engine
SQLAlchemy executes the generated SQL in a connection-pooled session. Results come back as a Pandas DataFrame, which is then serialised for the API response and passed to the answer-polishing LLM.

### Tier 4 — Interface Layer
A FastAPI REST backend exposes clean endpoints. A React frontend (`loyalty-insights-hub`) consumes those endpoints over HTTP — fully decoupled, so the frontend can be replaced or extended without touching a single line of backend code. CORS is open on the backend, so the React dev server connects directly with no proxy needed.

---

## Key Features

### 🤖 Agentic SQL Generation
The agent doesn't use a fixed prompt template. It reads the live schema from `information_schema` at startup and injects it into every request. Add a new table to the database, hit `/analytics/refresh-schema`, and the agent immediately knows about it — zero code changes.

### 📊 Auto-Generated Visualisations
After every query, a second LLM call analyses the result columns and decides the best chart type — bar, line, or pie. Recharts renders it instantly inside the chat. Time-series data gets a line chart. Category comparisons get a bar chart. Distribution data gets a donut chart.

### 🗄️ Live Schema Explorer
The sidebar shows the full database schema — every table, every column, every data type — pulled live from PostgreSQL. Click any table to preview its first rows and see its row count and column count. No need to open pgAdmin.

### 🔌 Loosely Coupled — Bring Your Own Database
The system is not tied to this specific dataset. The ETL pipeline, the agent, and the API are all driven by configuration. Point `DB_NAME` at any PostgreSQL database, run a schema refresh, and the agent adapts automatically. The only thing that changes is the data.

### 🛡️ SQL Safety Guard
Every SQL string generated by the LLM passes through a validator before execution. It must start with `SELECT`. Any `DROP`, `DELETE`, `INSERT`, `UPDATE`, `TRUNCATE`, or DDL keyword is blocked and logged. The database is read-only by design.

### 💬 Persistent Chat History
The full conversation is preserved in React component state. Every past answer includes its SQL, raw data table, and chart — all collapsible and reviewable inline. The chat auto-scrolls to the latest message.

### ⚡ Sub-2-Second Responses
Groq's LPU (Language Processing Unit) inference hardware delivers SQL generation and answer polishing in under 2 seconds combined, even for complex multi-table joins.

---

## The Data — What's Inside

10 sheets of US and Canada loyalty program data, 120,460 rows total:

| Table | Region | Rows | What it contains |
|---|---|---|---|
| `transactions_us` | US | 35,000 | Every points earn/redeem event |
| `loyalty_accounts_us` | US | 10,000 | Member tiers, points balances |
| `loyalty_affiliations_us` | US | 10,000 | Account-to-organisation mappings |
| `credit_sales_us` | US | 10,000 | Credit/return transactions |
| `sales_us` | US | 10,000 | Sales line items |
| `transactions_ca` | CA | 10,000 | Canadian transaction history |
| `loyalty_accounts_ca` | CA | 5,820 | Canadian member accounts |
| `loyalty_affiliations_ca` | CA | 9,640 | Canadian affiliations |
| `sales_ca` | CA | 10,000 | Canadian sales |
| `credit_sales_ca` | CA | 10,000 | Canadian credit sales |

The tables are joined on `loyalty_id`. The agent knows this and uses it automatically when a question spans multiple tables.

---

## Dual-Model Strategy

| Model | Role | Why |
|---|---|---|
| `llama-3.3-70b-versatile` | SQL generation | Large context window, superior reasoning for complex joins and filters |
| `llama-3.1-8b-instant` | Answer polishing + chart suggestion | Fast and cost-effective for summarisation tasks |

---

## Example Questions You Can Ask

```
"Who are the top 10 customers by total points earned?"
"How many Gold, Silver, and Bronze tier members are there?"
"What are the total points earned per month in 2024?"
"Show me the top 5 products by extended sales amount"
"Which loyalty organizations have the most active members?"
"What is the average points per transaction by tier?"
"How many transactions were processed in Q1 2024 vs Q1 2023?"
"Show me all redemption transactions above 500 points"
"Which customers have points expiring in the next 30 days?"
"What is the total revenue from Gold tier members in Canada?"
```

---

## Project Structure

```
loyalty_agent/                  ← Core library (framework-agnostic)
│
├── config/
│   └── settings.py             ← All config loaded from .env
│
├── db/
│   ├── connection.py           ← SQLAlchemy engine factory
│   └── queries.py              ← Schema scan, query execution, table preview
│
├── etl/
│   ├── cleaner.py              ← 5 deterministic cleaning rules
│   ├── db_loader.py            ← Creates DB if missing, bulk loads tables
│   └── pipeline.py             ← CLI: --mode clean | push
│
├── tools/
│   ├── sql_agent.py            ← LLM tool: NL → SQL  (Llama-3.3-70B)
│   ├── answer_agent.py         ← LLM tool: data → summary  (Llama-3.1-8B)
│   └── chart_agent.py          ← LLM tool: chart suggestion + Recharts spec
│
└── utils/
    ├── helpers.py              ← Pure functions: header cleaner, ID cleaner
    ├── logger.py               ← Centralised structured logging
    └── validators.py           ← SQL safety guard, injection prevention

backend/                        ← FastAPI REST API
├── main.py                     ← App factory, CORS, lifespan hooks
├── state.py                    ← Singleton: engine + Groq client + schema cache
├── schemas.py                  ← Pydantic request/response models
└── routers/
    ├── analytics.py            ← POST /analytics/query, GET /analytics/schema
    └── tables.py               ← GET /tables, GET /tables/{name}

loyalty-insights-hub/           ← React + TypeScript frontend
├── src/
│   ├── api/client.ts           ← Axios API client (connects to :8000)
│   ├── components/             ← Sidebar, ChatArea, MessageBubble, Charts
│   └── App.tsx                 ← Root component + state management
├── package.json
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | DB + LLM liveness check |
| `GET` | `/analytics/schema` | Full live schema + table list |
| `POST` | `/analytics/query` | `{"question": "..."}` → SQL + data + summary + chart spec |
| `POST` | `/analytics/refresh-schema` | Reload schema after ETL push |
| `GET` | `/tables` | List all tables |
| `GET` | `/tables/{name}` | Row preview + stats for a table |

Full interactive docs at **http://localhost:8000/docs** when the backend is running.

---

## Running the Project

See **[SETUP.md](./SETUP.md)** for the full step-by-step installation guide.

Quick start (after setup):

```bash
# Terminal 1 — Backend
.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000

# Terminal 2 — React Frontend
cd loyalty-insights-hub
npm install
npm run dev
```

Backend API docs: http://localhost:8000/docs
React frontend: http://localhost:5173

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| LLM Inference | Groq (Llama-3.3-70B + Llama-3.1-8B) |
| Database | PostgreSQL 16 |
| ORM / Query | SQLAlchemy 2.0 + psycopg2 |
| API Framework | FastAPI + Pydantic v2 |
| Frontend | React 18 + TypeScript |
| Styling | Tailwind CSS |
| Visualisation | Recharts |
| Data Processing | Pandas + NumPy |
| Config | python-dotenv |

---

## What Makes This Production-Grade

- **Separation of concerns** — core library, API, and UI are three independent layers
- **No hard-coded credentials** — everything through `.env`, git-ignored
- **Dynamic schema injection** — agent adapts to database changes automatically
- **SQL safety validation** — LLM output is validated before any DB call
- **Connection pooling** — `pool_pre_ping=True` handles dropped connections
- **Structured logging** — every layer logs with timestamps and module names
- **Pydantic validation** — all API inputs and outputs are typed and validated
- **Chunked DB inserts** — ETL loads in 1,000-row batches, handles large datasets
- **Idempotent ETL** — `if_exists='replace'` means re-running never corrupts data
- **Loosely coupled frontend** — React calls FastAPI over HTTP, completely independent — swap, rebuild, or redeploy the UI without touching the backend

---

*Built by Siddharth S — Dynamic SQL Analytics Agent*
