"""
routers/tables.py
-----------------
GET /tables          — list all tables
GET /tables/{name}   — preview + stats for a specific table
"""

from fastapi import APIRouter, HTTPException

from backend.schemas import TableStatsResponse
from backend.state import AppState
from loyalty_agent.db.queries import get_table_preview, get_table_stats
from loyalty_agent.utils.validators import is_valid_table_name

router = APIRouter()


@router.get("/", response_model=list[str])
def list_tables():
    """Return all public table names in the database."""
    if AppState.engine is None:
        raise HTTPException(status_code=503, detail="Database not connected.")
    return AppState.table_list


@router.get("/{table_name}", response_model=TableStatsResponse)
def table_detail(table_name: str, limit: int = 10):
    """Return a preview (first N rows) and stats for a specific table."""
    if AppState.engine is None:
        raise HTTPException(status_code=503, detail="Database not connected.")

    if not is_valid_table_name(table_name):
        raise HTTPException(status_code=400, detail="Invalid table name.")

    if table_name not in AppState.table_list:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")

    stats   = get_table_stats(AppState.engine, table_name)
    preview = get_table_preview(AppState.engine, table_name, limit=min(limit, 50))

    records = preview.where(preview.notna(), None).to_dict(orient="records")

    return TableStatsResponse(
        table=table_name,
        rows=stats["rows"],
        columns=stats["columns"],
        preview=records,
    )
