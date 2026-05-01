"""
helpers.py
----------
Pure utility functions shared across ETL, API, and frontend.
No side-effects, no imports from other project modules.
"""

import re
import numpy as np


def clean_column_header(col_name: str) -> str:
    """
    Standardise a raw Excel column header to a SQL-safe snake_case name.

    Examples
    --------
    'Total Amount ($)'  →  'total_amount_usd'
    'Date Of Transaction'  →  'date_of_transaction'
    'Points (%)'  →  'points_pct'
    """
    s = str(col_name).strip().lower()
    # Replace special symbols BEFORE the regex pass (plain string replace, no regex)
    s = s.replace("$", "usd").replace("%", "pct")
    # Replace any run of whitespace, dots, parens, slashes, dashes → underscore
    s = re.sub(r"[\s.()/\-]+", "_", s)
    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def safe_clean_id(value) -> str | None:
    """
    Safely convert an ID / code value to a clean string.

    Handles:
    - float NaN  (numpy / pandas)
    - None
    - '123.0'  →  '123'   (Excel stores integers as floats)
    - 'nan', 'NULL', ''  →  None
    """
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None

    s = str(value).strip()

    if s.lower() in ("nan", "none", "null", ""):
        return None

    # Strip trailing '.0' from integer-looking floats  e.g. '123.0' → '123'
    if "." in s:
        parts = s.split(".")
        if len(parts) == 2 and parts[1] == "0" and parts[0].lstrip("-").isdigit():
            return parts[0]

    return s


def format_number(value: float | int) -> str:
    """Format a number with commas for display.  1234567.89 → '1,234,567.89'"""
    try:
        return f"{value:,.2f}" if isinstance(value, float) else f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def truncate_string(s: str, max_len: int = 80) -> str:
    """Truncate a string and append '…' if it exceeds max_len."""
    return s if len(s) <= max_len else s[: max_len - 1] + "…"
