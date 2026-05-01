"""
queries.py
----------
All database read operations used by the FastAPI backend.
"""

from typing import Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from loyalty_agent.utils.logger import get_logger
from loyalty_agent.utils.validators import is_valid_table_name

log = get_logger(__name__)


def get_schema(engine: Engine) -> str:
    """
    Dynamically scan all public tables and return a schema string
    ready to be injected into an LLM prompt.

    Format:
        Table: transactions_us
        Columns: date_of_transaction (timestamp), loyalty_id (bigint), ...
    """
    parts: list[str] = []
    try:
        with engine.connect() as conn:
            tables = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name"
                )
            ).fetchall()

            for (table_name,) in tables:
                cols = conn.execute(
                    text(
                        "SELECT column_name, data_type "
                        "FROM information_schema.columns "
                        "WHERE table_name = :t ORDER BY ordinal_position"
                    ),
                    {"t": table_name},
                ).fetchall()
                col_list = ", ".join(f"{c} ({dt})" for c, dt in cols)
                parts.append(f"Table: {table_name}\nColumns: {col_list}")

    except Exception as exc:
        log.error("Schema fetch error: %s", exc)
        return f"Error fetching schema: {exc}"

    return "\n\n".join(parts)


def get_table_list(engine: Engine) -> list[str]:
    """Return all public table names."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name"
                )
            ).fetchall()
            return [r[0] for r in rows]
    except Exception as exc:
        log.error("Table list error: %s", exc)
        return []


def run_query(engine: Engine, sql: str) -> tuple[pd.DataFrame, Optional[str]]:
    """
    Execute a SQL string safely.

    Returns
    -------
    (DataFrame, None)        on success
    (empty DataFrame, error) on failure
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return df, None
    except Exception as exc:
        log.warning("Query execution error: %s", exc)
        return pd.DataFrame(), str(exc)


def get_table_preview(engine: Engine, table_name: str, limit: int = 10) -> pd.DataFrame:
    """Return the first N rows of a table."""
    if not is_valid_table_name(table_name):
        log.warning("Invalid table name requested: %s", table_name)
        return pd.DataFrame()
    df, err = run_query(engine, f"SELECT * FROM {table_name} LIMIT {limit}")
    if err:
        log.error("Preview error for '%s': %s", table_name, err)
    return df


def get_table_stats(engine: Engine, table_name: str) -> dict:
    """Return row count and column count for a table."""
    stats = {"table": table_name, "rows": 0, "columns": 0}
    if not is_valid_table_name(table_name):
        return stats
    try:
        with engine.connect() as conn:
            stats["rows"] = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()
            stats["columns"] = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.columns "
                    "WHERE table_name = :t"
                ),
                {"t": table_name},
            ).scalar()
    except Exception as exc:
        log.error("Stats error for '%s': %s", table_name, exc)
    return stats
