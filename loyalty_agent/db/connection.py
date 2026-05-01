"""
connection.py
-------------
SQLAlchemy engine factory used by both the ETL and the FastAPI backend.
"""

import urllib.parse
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from loyalty_agent.config.settings import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)


def build_engine() -> Optional[Engine]:
    """
    Create and validate a SQLAlchemy engine for the target database.
    Returns None if the connection fails.
    """
    if not DB_PASS:
        log.error("DB_PASS is not set. Check your .env file.")
        return None
    try:
        encoded = urllib.parse.quote_plus(DB_PASS)
        conn_str = (
            f"postgresql://{DB_USER}:{encoded}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        engine = create_engine(conn_str, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("✅ DB connected  →  %s @ %s:%s", DB_NAME, DB_HOST, DB_PORT)
        return engine
    except Exception as exc:
        log.error("❌ DB connection failed: %s", exc)
        return None
