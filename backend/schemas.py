"""
schemas.py
----------
Pydantic request / response models for the FastAPI endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Request ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        example="Who are the top 10 customers by total points earned?",
    )


# ── Response ───────────────────────────────────────────────────────────────────

class QueryResponse(BaseModel):
    question:    str
    sql:         str
    row_count:   int
    data:        list[dict[str, Any]]
    summary:     str
    chart_spec:  Optional[dict] = None
    error:       Optional[str]  = None


class TableStatsResponse(BaseModel):
    table:   str
    rows:    int
    columns: int
    preview: list[dict[str, Any]]


class SchemaResponse(BaseModel):
    schema_text: str
    tables:      list[str]


class HealthResponse(BaseModel):
    status:       str
    db_connected: bool
    llm_ready:    bool
