"""
sql_agent.py
------------
LLM tool: converts a natural-language question into a PostgreSQL SELECT.

Uses Groq's Llama-3.3-70B for maximum SQL accuracy.
"""

import re

from groq import Groq

from loyalty_agent.config.settings import GROQ_API_KEY, SQL_MODEL, SQL_ROW_LIMIT
from loyalty_agent.utils.logger import get_logger
from loyalty_agent.utils.validators import is_safe_sql

log = get_logger(__name__)

_SYSTEM_PROMPT = """
You are a senior PostgreSQL analyst. Your ONLY job is to convert the user's
natural-language question into a single, executable PostgreSQL SELECT statement.

### DATABASE SCHEMA:
{schema}

### STRICT RULES:
1. Output ONLY the raw SQL — no markdown fences, no explanation, no comments.
2. If the question is completely unrelated to the database (e.g. "Who is Batman?"),
   output exactly the word: NO_DATA
3. Always add LIMIT {row_limit} unless the user explicitly asks for all rows.
4. Use ILIKE for case-insensitive text matching.
5. Use table aliases for readability on multi-table queries.
6. Only generate SELECT statements — never INSERT, UPDATE, DELETE, or DDL.
7. For date ranges, use BETWEEN or >= / <= operators.
8. When joining tables, prefer loyalty_id as the join key.
9. For aggregations, always include a meaningful ORDER BY.
10. If a column might be NULL, use COALESCE where appropriate.
11. For US data use tables ending in _us; for Canada use _ca.
""".strip()


def build_client() -> Groq:
    if not GROQ_API_KEY.startswith("gsk_"):
        raise ValueError("GROQ_API_KEY is missing or invalid. Check your .env file.")
    return Groq(api_key=GROQ_API_KEY)


def generate_sql(client: Groq, user_query: str, schema: str) -> str:
    """
    Convert a natural-language question into a PostgreSQL SELECT statement.

    Returns
    -------
    str
        - A valid SQL SELECT string
        - "NO_DATA"          if the question is out of scope
        - "ERROR: <message>" if the LLM call fails
    """
    prompt = _SYSTEM_PROMPT.format(schema=schema, row_limit=SQL_ROW_LIMIT)

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": user_query},
            ],
            model=SQL_MODEL,
            temperature=0,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content.strip()

        # Strip accidental markdown fences
        sql = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
        sql = sql.replace("```", "").strip()

        if sql.upper() == "NO_DATA":
            return "NO_DATA"

        # Safety guard
        safe, reason = is_safe_sql(sql)
        if not safe:
            log.warning("Unsafe SQL blocked: %s", reason)
            return f"ERROR: {reason}"

        return sql

    except Exception as exc:
        log.error("SQL generation error: %s", exc)
        return f"ERROR: {exc}"
