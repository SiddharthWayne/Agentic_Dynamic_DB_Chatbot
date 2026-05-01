"""
answer_agent.py
---------------
LLM tool: converts raw SQL result data into a human-readable executive summary.

Uses Groq's Llama-3.1-8B-Instant for fast, cost-effective polishing.
"""

from groq import Groq

from loyalty_agent.config.settings import GROQ_API_KEY, POLISH_MODEL
from loyalty_agent.utils.logger import get_logger

log = get_logger(__name__)

_SYSTEM_PROMPT = """
You are a senior data analyst presenting findings to a business executive.
Given the user's question and the raw query results, write a clear, concise,
and insightful summary in 2–5 sentences.

Guidelines:
- Lead with the direct answer to the question.
- Highlight the most important numbers or trends.
- Use plain English — no SQL jargon.
- If the data is empty, say so clearly and suggest why.
- Format currency as $X,XXX and large numbers with commas.
- Do not repeat the raw data table — summarise it.
""".strip()


def polish_answer(client: Groq, user_query: str, data_str: str) -> str:
    """
    Convert raw tabular data into a human-readable executive summary.

    Parameters
    ----------
    client      : Groq client instance
    user_query  : The original user question
    data_str    : String representation of the query result DataFrame

    Returns
    -------
    str  — Natural language summary
    """
    user_prompt = f"Question: {user_query}\n\nData:\n{data_str}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            model=POLISH_MODEL,
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        log.error("Answer polishing error: %s", exc)
        return f"(Could not generate summary: {exc})"
