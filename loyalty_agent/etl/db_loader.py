"""
db_loader.py
------------
Handles the PostgreSQL connection and bulk data loading.

- Creates the database if it does not exist.
- Pushes each DataFrame as a table (replace strategy).
- Uses chunked inserts for large datasets.
"""

import urllib.parse

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from loyalty_agent.config.settings import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
)
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)

CHUNK_SIZE = 1_000   # rows per INSERT batch


def _build_conn_str(db_name: str) -> str:
    encoded = urllib.parse.quote_plus(DB_PASS)
    return f"postgresql://{DB_USER}:{encoded}@{DB_HOST}:{DB_PORT}/{db_name}"


def ensure_database_exists() -> None:
    """
    Connect to the default 'postgres' database and CREATE the target DB
    if it doesn't already exist.
    """
    try:
        engine = create_engine(
            _build_conn_str("postgres"),
            isolation_level="AUTOCOMMIT",
        )
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": DB_NAME},
            ).fetchone()

            if not exists:
                conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                log.info("✅ Database '%s' created.", DB_NAME)
            else:
                log.info("ℹ️  Database '%s' already exists.", DB_NAME)

        engine.dispose()
    except Exception as exc:
        log.error("❌ Could not ensure database exists: %s", exc)
        raise


def get_engine() -> Engine:
    """Return a validated SQLAlchemy engine for the target database."""
    engine = create_engine(
        _build_conn_str(DB_NAME),
        pool_pre_ping=True,
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    log.info("✅ Connected to PostgreSQL  →  %s @ %s:%s", DB_NAME, DB_HOST, DB_PORT)
    return engine


def push_to_postgres(tables: dict[str, pd.DataFrame]) -> None:
    """
    Push a dict of {table_name: DataFrame} into PostgreSQL.
    Each table is replaced entirely (if_exists='replace').
    """
    ensure_database_exists()

    try:
        engine = get_engine()
    except Exception as exc:
        log.error("❌ DB connection failed: %s", exc)
        return

    total_rows = 0
    for table_name, df in tables.items():
        try:
            df.to_sql(
                table_name,
                engine,
                if_exists="replace",
                index=False,
                chunksize=CHUNK_SIZE,
                method="multi",
            )
            log.info(
                "  📤 %-35s  →  %d rows loaded",
                f"'{table_name}'",
                len(df),
            )
            total_rows += len(df)
        except Exception as exc:
            log.error("  ❌ Failed to load table '%s': %s", table_name, exc)

    engine.dispose()
    log.info("📊 Total rows pushed to PostgreSQL: %d", total_rows)
