"""
state.py
--------
Singleton application state — DB engine, Groq client, and cached schema.
Initialised once at FastAPI startup.
"""

from loyalty_agent.db.connection import build_engine
from loyalty_agent.db.queries import get_schema, get_table_list
from loyalty_agent.tools.sql_agent import build_client
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)


class AppState:
    engine      = None
    groq_client = None
    db_schema   = ""
    table_list: list[str] = []

    @classmethod
    def init(cls) -> None:
        log.info("🔧 Initialising application state…")

        cls.engine = build_engine()
        if cls.engine is None:
            log.error("❌ Database unavailable — check DB_PASS and DB_HOST in .env")
        else:
            cls.db_schema  = get_schema(cls.engine)
            cls.table_list = get_table_list(cls.engine)
            log.info("✅ Schema loaded  (%d tables)", len(cls.table_list))

        try:
            cls.groq_client = build_client()
            log.info("✅ Groq client ready")
        except ValueError as exc:
            log.error("❌ Groq init failed: %s", exc)
            cls.groq_client = None

    @classmethod
    def shutdown(cls) -> None:
        if cls.engine:
            cls.engine.dispose()
            log.info("🔌 DB engine disposed.")

    @classmethod
    def refresh_schema(cls) -> None:
        """Force a schema refresh (call after ETL push)."""
        if cls.engine:
            cls.db_schema  = get_schema(cls.engine)
            cls.table_list = get_table_list(cls.engine)
            log.info("🔄 Schema refreshed  (%d tables)", len(cls.table_list))
