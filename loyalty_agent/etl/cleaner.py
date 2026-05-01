"""
cleaner.py
----------
All 5 cleaning rules applied to every sheet.

Rule 1 — Column Header Standardisation
Rule 2 — Mixed Data Type Fix  (ID / code columns → string)
Rule 3 — Garbage Value Removal  (#####, NULL text, nan → real NULL)
Rule 4 — Date Standardisation  (timezone-aware → naive UTC)
Rule 5 — Numeric Type Enforcement  (comma-strings → float)
"""

import numpy as np
import pandas as pd

from loyalty_agent.config.settings import (
    DATE_KEYWORDS,
    GARBAGE_VALUES,
    NUMERIC_KEYWORDS,
)
from loyalty_agent.utils.helpers import clean_column_header, safe_clean_id
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)


def clean_sheet(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Apply all 5 cleaning rules to a single DataFrame.

    Parameters
    ----------
    df          : Raw DataFrame read directly from Excel.
    sheet_name  : Used only for log messages.

    Returns
    -------
    Cleaned DataFrame, ready for database insertion.
    """
    log.info("  Cleaning '%s'  (%d rows × %d cols)", sheet_name, *df.shape)

    # ── Rule 1: Column Header Standardisation ─────────────────────────────────
    df.columns = [clean_column_header(c) for c in df.columns]
    log.info("    ✔ Rule 1 — Headers standardised")

    # ── Rule 3: Garbage Values → NaN  (done before Rule 2 so IDs are clean) ──
    df.replace(GARBAGE_VALUES, np.nan, inplace=True)
    log.info("    ✔ Rule 3 — Garbage values removed")

    # ── Rule 2: Mixed Data Types — ID / code columns forced to string ─────────
    id_cols = [
        c for c in df.columns
        if any(kw in c for kw in ("id", "code", "number"))
        and not any(skip in c for skip in ("amount", "price", "total", "quantity"))
    ]
    for col in id_cols:
        df[col] = df[col].apply(safe_clean_id)
    log.info("    ✔ Rule 2 — %d ID/code columns converted to string", len(id_cols))

    # ── Rule 4: Date Standardisation ──────────────────────────────────────────
    date_cols = [
        c for c in df.columns
        if any(kw in c for kw in DATE_KEYWORDS)
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
        df[col] = df[col].dt.tz_localize(None)   # strip timezone → naive
    log.info("    ✔ Rule 4 — %d date columns normalised", len(date_cols))

    # ── Rule 5: Numeric Type Enforcement ──────────────────────────────────────
    numeric_cols = [
        c for c in df.columns
        if any(kw in c for kw in NUMERIC_KEYWORDS)
        and c not in id_cols
    ]
    for col in numeric_cols:
        temp = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(temp, errors="coerce")
    log.info("    ✔ Rule 5 — %d numeric columns enforced", len(numeric_cols))

    # ── Final: NaN → None  (PostgreSQL NULL) ──────────────────────────────────
    df = df.where(pd.notnull(df), None)

    log.info("  ✅ '%s' cleaned  →  %d rows ready", sheet_name, len(df))
    return df
