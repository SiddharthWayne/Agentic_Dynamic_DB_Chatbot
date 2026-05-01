"""
chart_agent.py
--------------
LLM tool: suggests the best Plotly chart type for a given result set,
then renders it.
"""

import json
import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq

from loyalty_agent.config.settings import GROQ_API_KEY, POLISH_MODEL
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)

COLOUR_SEQUENCE = [
    "#4F8EF7", "#F7874F", "#4FF7A0", "#F74F6E",
    "#A04FF7", "#F7D44F", "#4FD4F7", "#F74FA0",
]

_SYSTEM_PROMPT = """
You are a data visualisation expert. Given a user question and the column names
of the result set, decide the best chart type.

Respond with EXACTLY one of these JSON objects (no other text):
  {"chart": "bar",  "x": "<col>", "y": "<col>", "title": "<title>"}
  {"chart": "line", "x": "<col>", "y": "<col>", "title": "<title>"}
  {"chart": "pie",  "names": "<col>", "values": "<col>", "title": "<title>"}
  {"chart": "none"}

Rules:
- Use "bar"  for category comparisons (top N, by tier, by product).
- Use "line" for time-series data (date columns on x-axis).
- Use "pie"  for part-of-whole distributions (≤ 8 categories).
- Use "none" if the data is not suitable for a chart.
- Only reference columns that actually exist in the provided list.
""".strip()


def suggest_chart(client: Groq, user_query: str, columns: list[str]) -> dict:
    """Ask the LLM to suggest the best chart spec for the result columns."""
    col_list = ", ".join(columns)
    user_prompt = f"Question: {user_query}\nResult columns: {col_list}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            model=POLISH_MODEL,
            temperature=0,
            max_tokens=128,
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)

    except Exception as exc:
        log.warning("Chart suggestion failed: %s", exc)
        return {"chart": "none"}


def render_chart(spec: dict, df: pd.DataFrame) -> go.Figure | None:
    """
    Build a Plotly figure from a chart spec dict and a DataFrame.

    Returns None if chart type is "none" or rendering fails.
    """
    chart_type = spec.get("chart", "none")

    if chart_type == "none" or df.empty:
        return None

    layout = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#FAFAFA", "family": "Inter, sans-serif"},
        title_font={"size": 16},
        margin={"t": 50, "b": 30, "l": 20, "r": 20},
    )

    try:
        if chart_type == "bar":
            x, y = spec.get("x"), spec.get("y")
            if not _cols_ok(df, x, y):
                return None
            fig = px.bar(
                df, x=x, y=y,
                title=spec.get("title", ""),
                color_discrete_sequence=COLOUR_SEQUENCE,
                text_auto=True,
            )
            fig.update_layout(**layout)
            return fig

        elif chart_type == "line":
            x, y = spec.get("x"), spec.get("y")
            if not _cols_ok(df, x, y):
                return None
            fig = px.line(
                df, x=x, y=y,
                title=spec.get("title", ""),
                color_discrete_sequence=COLOUR_SEQUENCE,
                markers=True,
            )
            fig.update_layout(**layout)
            return fig

        elif chart_type == "pie":
            names, values = spec.get("names"), spec.get("values")
            if not _cols_ok(df, names, values):
                return None
            fig = px.pie(
                df, names=names, values=values,
                title=spec.get("title", ""),
                color_discrete_sequence=COLOUR_SEQUENCE,
                hole=0.35,
            )
            fig.update_layout(**layout)
            return fig

    except Exception as exc:
        log.error("Chart render error: %s", exc)

    return None


def _cols_ok(df: pd.DataFrame, *cols) -> bool:
    for col in cols:
        if col is None or col not in df.columns:
            log.warning("Column '%s' not in DataFrame.", col)
            return False
    return True
