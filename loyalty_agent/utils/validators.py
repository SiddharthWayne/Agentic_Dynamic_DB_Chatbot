"""
validators.py
-------------
Input validation helpers used by the FastAPI layer.
"""

import re


def is_safe_sql(sql: str) -> tuple[bool, str]:
    """
    Lightweight guard: ensure the LLM only produced a SELECT statement.

    Returns (True, "") if safe, or (False, reason) if not.
    """
    stripped = sql.strip().upper()

    # Must start with SELECT
    if not stripped.startswith("SELECT"):
        return False, "Only SELECT statements are allowed."

    # Block destructive keywords
    forbidden = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b",
        r"\bINSERT\b", r"\bUPDATE\b", r"\bALTER\b",
        r"\bCREATE\b", r"\bGRANT\b",  r"\bREVOKE\b",
        r"\bEXEC\b",   r"\bEXECUTE\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, stripped):
            return False, f"Forbidden keyword detected: {pattern}"

    return True, ""


def is_valid_table_name(name: str) -> bool:
    """Allow only alphanumeric + underscore table names (prevents injection)."""
    return bool(re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name))
