"""
pipeline.py
-----------
ETL entry point.

Two modes:
  1. CLEAN  — reads raw Loyalty Data.xlsx, applies all 5 rules, saves
              Loyalty_Data_Cleaned_All.xlsx
  2. PUSH   — reads the already-cleaned xlsx and loads every sheet into
              the local PostgreSQL database (table-per-sheet, replace strategy)

Run from project root:
    python -m loyalty_agent.etl.pipeline --mode clean
    python -m loyalty_agent.etl.pipeline --mode push
    python -m loyalty_agent.etl.pipeline --mode clean --push   # both at once
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from loyalty_agent.config.settings import (
    CLEANED_SOURCE_FILE,
    CLEANED_XLSX_OUTPUT,
    RAW_DATA_FILE,
    SHEET_TABLE_MAP,
)
from loyalty_agent.etl.cleaner import clean_sheet
from loyalty_agent.etl.db_loader import push_to_postgres
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)


# ── Mode 1: CLEAN ──────────────────────────────────────────────────────────────

def run_clean(
    input_file: str = RAW_DATA_FILE,
    output_file: str = CLEANED_XLSX_OUTPUT,
) -> dict[str, pd.DataFrame]:
    """
    Read every sheet from the raw Excel file, apply all 5 cleaning rules,
    and save the result as a new Excel workbook.

    Returns a dict of {sheet_name: cleaned_DataFrame}.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        log.error("Raw file not found: %s", input_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("🚀  ETL CLEAN MODE")
    log.info("    Source  : %s", input_path)
    log.info("    Output  : %s", output_file)
    log.info("=" * 60)

    xls = pd.ExcelFile(input_file)
    found_sheets = xls.sheet_names
    log.info("Found %d sheets: %s", len(found_sheets), found_sheets)

    cleaned: dict[str, pd.DataFrame] = {}

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet in found_sheets:
            try:
                df_raw = pd.read_excel(input_file, sheet_name=sheet)
                df_clean = clean_sheet(df_raw, sheet)

                safe_tab = sheet[:31]          # Excel tab name limit
                df_clean.to_excel(writer, sheet_name=safe_tab, index=False)
                cleaned[sheet] = df_clean

                log.info("  💾 Saved sheet '%s'  →  tab '%s'", sheet, safe_tab)

            except Exception as exc:
                log.error("  ❌ Error on sheet '%s': %s", sheet, exc)

    log.info("=" * 60)
    log.info("✅  CLEAN COMPLETE  →  %s", output_file)
    log.info("=" * 60)
    return cleaned


# ── Mode 2: PUSH ───────────────────────────────────────────────────────────────

def run_push(source_file: str = CLEANED_SOURCE_FILE) -> None:
    """
    Read the already-cleaned Excel file and push every sheet into PostgreSQL.
    Each sheet maps to a table name defined in SHEET_TABLE_MAP.
    """
    source_path = Path(source_file)
    if not source_path.exists():
        log.error("Cleaned file not found: %s", source_path)
        sys.exit(1)

    log.info("=" * 60)
    log.info("🚀  ETL PUSH MODE")
    log.info("    Source  : %s", source_path)
    log.info("=" * 60)

    xls = pd.ExcelFile(source_file)

    tables: dict[str, pd.DataFrame] = {}
    for sheet in xls.sheet_names:
        table_name = SHEET_TABLE_MAP.get(sheet)
        if not table_name:
            log.warning("No table mapping for sheet '%s' — skipping.", sheet)
            continue
        try:
            df = pd.read_excel(source_file, sheet_name=sheet)
            tables[table_name] = df
            log.info("  📖 Loaded sheet '%s'  →  table '%s'  (%d rows)", sheet, table_name, len(df))
        except Exception as exc:
            log.error("  ❌ Could not read sheet '%s': %s", sheet, exc)

    push_to_postgres(tables)

    log.info("=" * 60)
    log.info("✅  PUSH COMPLETE")
    log.info("=" * 60)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Loyalty Data ETL Pipeline",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["clean", "push"],
        required=True,
        help=(
            "clean  — Read raw xlsx, apply 5 cleaning rules, save cleaned xlsx\n"
            "push   — Read cleaned xlsx, load all sheets into PostgreSQL"
        ),
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="After cleaning, also push to PostgreSQL (only valid with --mode clean)",
    )
    parser.add_argument("--input",  default=RAW_DATA_FILE,       help="Override raw input file path")
    parser.add_argument("--output", default=CLEANED_XLSX_OUTPUT,  help="Override cleaned output file path")
    parser.add_argument("--source", default=CLEANED_SOURCE_FILE,  help="Override cleaned source for push mode")

    args = parser.parse_args()

    if args.mode == "clean":
        run_clean(input_file=args.input, output_file=args.output)
        if args.push:
            run_push(source_file=args.output)

    elif args.mode == "push":
        run_push(source_file=args.source)
