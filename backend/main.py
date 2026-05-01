"""
backend/main.py
---------------
FastAPI application — the brain of the system.

Endpoints:
  GET  /health          — liveness check
  GET  /schema          — full DB schema string
  GET  /tables          — list of all tables
  GET  /tables/{name}   — preview + stats for a table
  POST /query           — natural language → SQL → result → summary + chart spec
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analytics, tables
from backend.state import AppState

# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise shared resources once at startup."""
    AppState.init()
    yield
    AppState.shutdown()


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Loyalty Analytics Agent API",
    description=(
        "Natural-language analytics over the Loyalty Dataset. "
        "Converts plain-English questions into PostgreSQL queries via LLM."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the Streamlit frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(tables.router,    prefix="/tables",    tags=["Tables"])


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "db_connected": AppState.engine is not None,
        "llm_ready":    AppState.groq_client is not None,
    }
