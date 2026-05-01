"""
settings.py
-----------
Single source of truth for all configuration.
Values are read from environment variables or a .env file.
Never hard-code secrets here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq LLM ───────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
SQL_MODEL:    str = os.getenv("SQL_MODEL",    "llama-3.3-70b-versatile")
POLISH_MODEL: str = os.getenv("POLISH_MODEL", "llama-3.1-8b-instant")

# ── PostgreSQL ─────────────────────────────────────────────────────────────────
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASS: str = os.getenv("DB_PASS", "")
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = os.getenv("DB_NAME", "Loyalty_Dataset")

# ── File Paths ─────────────────────────────────────────────────────────────────
# Raw source file  (ETL reads this, cleans it, saves cleaned output)
RAW_DATA_FILE:      str = os.getenv(
    "RAW_DATA_FILE",
    r"I:\April_VH\SQL_Agent\Loyalty Data.xlsx"
)
# Cleaned output written by ETL
CLEANED_XLSX_OUTPUT: str = os.getenv(
    "CLEANED_XLSX_OUTPUT",
    r"I:\April_VH\SQL_Agent\Loyalty_Data_Cleaned_All.xlsx"
)
# Already-cleaned file used for DB push
CLEANED_SOURCE_FILE: str = os.getenv(
    "CLEANED_SOURCE_FILE",
    r"I:\April_VH\SQL_Agent\Loyalty_Data_Cleaned_All.xlsx"
)

# ── Agent Behaviour ────────────────────────────────────────────────────────────
SQL_ROW_LIMIT:   int = int(os.getenv("SQL_ROW_LIMIT",   "50"))
CHART_ROW_LIMIT: int = int(os.getenv("CHART_ROW_LIMIT", "500"))

# ── ETL Constants ──────────────────────────────────────────────────────────────
GARBAGE_VALUES: list[str] = [
    "NULL", "null", "#####", "##", "N/A", "na",
    "NaN", "nan", "none", "None", "",
]

DATE_KEYWORDS:    list[str] = ["date", "_at", "time", "cdr"]
NUMERIC_KEYWORDS: list[str] = [
    "amount", "points", "quantity", "price",
    "ratio", "percentage", "multiplier",
]

# Sheet → DB table name mapping (all 10 sheets)
SHEET_TABLE_MAP: dict[str, str] = {
    "Transaction - US":        "transactions_us",
    "Loyalty Account - US":    "loyalty_accounts_us",
    "Loyalty Affiliation -US": "loyalty_affiliations_us",
    "Credit Sales - US":       "credit_sales_us",
    "Sales - US":              "sales_us",
    "TH - CA":                 "transactions_ca",
    "Loyalty Account - CA":    "loyalty_accounts_ca",
    "Loyalty Affiliation -CA": "loyalty_affiliations_ca",
    "Sales - CA":              "sales_ca",
    "Credit sales -CA":        "credit_sales_ca",
}
