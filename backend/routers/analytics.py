"""
routers/analytics.py
--------------------
POST /analytics/query  — the core NL → SQL → answer pipeline.
GET  /analytics/schema — return the live DB schema.
"""

from fastapi import APIRouter, HTTPException

from backend.schemas import QueryRequest, QueryResponse, SchemaResponse
from backend.state import AppState
from loyalty_agent.config.settings import SQL_ROW_LIMIT
from loyalty_agent.db.queries import run_query
from loyalty_agent.tools.answer_agent import polish_answer
from loyalty_agent.tools.chart_agent import suggest_chart
from loyalty_agent.tools.sql_agent import generate_sql

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Full pipeline:
      1. Generate SQL from the natural-language question
      2. Execute SQL against PostgreSQL
      3. Polish the result into a human-readable summary
      4. Suggest a chart spec
    """
    if AppState.engine is None:
        raise HTTPException(status_code=503, detail="Database not connected.")
    if AppState.groq_client is None:
        raise HTTPException(status_code=503, detail="LLM client not initialised.")

    question = request.question.strip()

    # ── Step 1: Generate SQL ───────────────────────────────────────────────────
    sql = generate_sql(AppState.groq_client, question, AppState.db_schema)

    if sql == "NO_DATA":
        return QueryResponse(
            question=question,
            sql="NO_DATA",
            row_count=0,
            data=[],
            summary=(
                "That question doesn't relate to the Loyalty database. "
                "Try asking about transactions, members, points, tiers, or sales."
            ),
            chart_spec=None,
        )

    if sql.startswith("ERROR:"):
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {sql}")

    # ── Step 2: Execute SQL ────────────────────────────────────────────────────
    df, db_error = run_query(AppState.engine, sql)

    if db_error:
        return QueryResponse(
            question=question,
            sql=sql,
            row_count=0,
            data=[],
            summary="",
            error=f"SQL execution failed: {db_error}",
        )

    if df.empty:
        return QueryResponse(
            question=question,
            sql=sql,
            row_count=0,
            data=[],
            summary="The query ran successfully but returned no matching records.",
            chart_spec=None,
        )

    # ── Step 3: Polish answer ──────────────────────────────────────────────────
    data_str = df.head(SQL_ROW_LIMIT).to_string(index=False)
    summary  = polish_answer(AppState.groq_client, question, data_str)

    # ── Step 4: Chart suggestion ───────────────────────────────────────────────
    chart_spec = suggest_chart(AppState.groq_client, question, list(df.columns))

    # Serialise DataFrame (NaT / NaN → None for JSON)
    records = df.head(SQL_ROW_LIMIT).where(df.notna(), None).to_dict(orient="records")

    return QueryResponse(
        question=question,
        sql=sql,
        row_count=len(df),
        data=records,
        summary=summary,
        chart_spec=chart_spec,
    )


@router.get("/schema", response_model=SchemaResponse)
def schema():
    """Return the live database schema and table list."""
    if AppState.engine is None:
        raise HTTPException(status_code=503, detail="Database not connected.")
    return SchemaResponse(
        schema_text=AppState.db_schema,
        tables=AppState.table_list,
    )


@router.post("/refresh-schema", tags=["Analytics"])
def refresh_schema():
    """Force a schema refresh (useful after running the ETL push)."""
    AppState.refresh_schema()
    return {"message": f"Schema refreshed. {len(AppState.table_list)} tables found."}
