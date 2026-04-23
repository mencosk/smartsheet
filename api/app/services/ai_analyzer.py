import json

import pandas as pd
from google import genai

from app.config import settings


def _build_schema_summary(df: pd.DataFrame) -> str:
    """Build a textual summary of the DataFrame schema and statistics."""
    lines: list[str] = []
    lines.append(f"Dataset: {len(df)} rows × {len(df.columns)} columns\n")

    lines.append("Columns and data types:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        unique = df[col].nunique()
        lines.append(f"  - {col} (type: {dtype}, non-null: {non_null}, unique values: {unique})")

    # Numeric summary
    numeric_df = df.describe()
    if not numeric_df.empty:
        lines.append(f"\nNumeric statistics:\n{numeric_df.to_string()}")

    # Sample rows
    sample = df.head(5).to_string(index=False)
    lines.append(f"\nSample data (first 5 rows):\n{sample}")

    return "\n".join(lines)


_SYSTEM_PROMPT = """You are an expert data analyst. Given a dataset schema and statistical summary, 
your job is to identify the most interesting patterns, trends, and relationships in the data, 
then suggest 3 to 5 specific visualizations that would provide the most value to someone exploring this data.

For each visualization, return a JSON object with:
- "title": A clear, descriptive title in Spanish (e.g., "Distribución de Ventas por Región")
- "chart_type": One of "bar", "line", "pie", "scatter", "area"
- "parameters": An object with the keys needed to build the chart:
  - For bar/line/area: {"x_axis": "column_name", "y_axis": "column_name", "aggregation": "sum"|"mean"|"count"}
  - For pie: {"category": "column_name", "value": "column_name", "aggregation": "sum"|"mean"|"count"}
  - For scatter: {"x_axis": "column_name", "y_axis": "column_name"}
- "insight": A brief, insightful explanation in Spanish of what this chart reveals and why it matters.

IMPORTANT RULES:
1. Only use column names that exist in the dataset.
2. Choose chart types that best match the data types of the columns.
3. Prioritize charts that reveal actionable insights.
4. Use "count" aggregation when you want to count occurrences of categories.
5. Return ONLY a valid JSON array, no additional text or markdown."""


async def analyze_data(df: pd.DataFrame) -> list[dict]:
    """Send DataFrame summary to Gemini and get visualization suggestions."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Please set it in the .env file.")

    schema_summary = _build_schema_summary(df)

    user_prompt = f"""Analyze the following dataset and suggest the best visualizations:

{schema_summary}

Return ONLY a JSON array with 3 to 5 visualization suggestions."""

    client = genai.Client(api_key=settings.gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"role": "user", "parts": [{"text": _SYSTEM_PROMPT + "\n\n" + user_prompt}]},
        ],
    )

    # Parse the response
    text = response.text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    try:
        suggestions = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"AI returned invalid JSON. Raw response: {text[:500]}")

    if not isinstance(suggestions, list):
        raise ValueError("AI response is not a JSON array.")

    return suggestions
