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


_SYSTEM_PROMPT = """You are generating visualization suggestions for a React frontend that supports ONLY these chart types:
["bar", "line", "pie", "scatter", "area"].

You will receive a dataset schema summary. Based on that summary, return visualization suggestions that are:
1) buildable by the downstream chart-data builder,
2) analytically useful,
3) diverse in both chart type and analytical angle.

OUTPUT RULES:
- Return ONLY a valid JSON array.
- No markdown.
- No code fences.
- No explanation before or after the JSON.
- The top-level value must be an array of 1 to 5 objects.
- Prefer 3 to 5 suggestions when enough valid, distinct charts exist.
- If fewer than 3 valid chart suggestions exist, return only the valid ones.
- If no valid chart can be built, return [].

EACH ARRAY ITEM MUST BE AN OBJECT WITH EXACTLY THESE KEYS:
1. "title"
2. "chart_type"
3. "parameters"
4. "insight"

FIELD CONSTRAINTS:
- "title": non-empty string in Spanish.
- "chart_type": exactly one of "bar", "line", "pie", "scatter", "area".
- "insight": non-empty string in Spanish, concise and specific.

"parameters" MUST MATCH THE CHART TYPE EXACTLY:

A) For "bar", "line", or "area":
{
  "x_axis": "<existing column name>",
  "y_axis": "<existing column name>",
  "aggregation": "sum" | "mean" | "count"
}

B) For "pie":
{
  "category": "<existing column name>",
  "value": "<existing column name>",
  "aggregation": "sum" | "mean" | "count"
}

C) For "scatter":
{
  "x_axis": "<existing column name>",
  "y_axis": "<existing column name>"
}

STRICT VALIDATION RULES:
- Use ONLY column names that exist exactly as written in the dataset summary.
- Do NOT invent, rename, translate, or normalize column names.
- Do NOT include extra keys.
- Do NOT include null, undefined, comments, or trailing commas.
- Use only double-quoted JSON strings.

DIVERSITY RULES:
- Each suggestion should represent a DIFFERENT analytical angle when possible.
- Cover distinct angles from this set when possible:
  - comparison
  - trend
  - composition
  - correlation
  - distribution
- Do NOT repeat a chart type until all other viable chart types have been used.
- If 4 or 5 valid chart types are possible, use different chart types for every suggestion.

CHART SELECTION RULES:
- "scatter" only if there are at least 2 numeric columns suitable for correlation.
- "line" or "area" only if the x-axis is naturally ordered (date/time, year/month/period, or numeric sequence) AND the y-axis is suitable for numeric aggregation.
- "pie" only for composition with a low-cardinality category; avoid pie for very high-cardinality fields.
- "bar" is preferred for category comparisons and count-based summaries.
- Prefer x-axis/category columns with manageable cardinality:
  - bar/line/area: ideally 20 or fewer unique values
  - pie: ideally 10 or fewer unique values
- Avoid using identifier-like columns (id, code, key, uuid, consecutivo, etc.) as the main analytical dimension unless no better option exists.
- Avoid sum/mean on clearly non-numeric or identifier-like fields.
- For "sum" and "mean", the aggregated y/value column must be numeric.
- For "count", count occurrences of the grouping/category column.

IMPORTANT DOWNSTREAM COMPATIBILITY RULES:
- For "bar", "line", and "area", if "aggregation" = "count", you MUST still provide a valid existing "y_axis" because downstream validation requires it.
  - Prefer a meaningful existing numeric column.
  - If no better option exists, set "y_axis" equal to "x_axis".
- For "pie", if "aggregation" = "count", you MUST still provide a valid existing "value".
  - Set "value" equal to "category".

EDGE-CASE RULES:
- If the dataset has very few rows, prefer simple comparison/composition charts and avoid weak scatter plots.
- If only categorical columns exist, prefer bar and pie with "count".
- If only numeric columns exist, prefer scatter and, only if clearly sensible, line/area using an ordered numeric x-axis.
- If only one column is usable, return only the best valid chart(s) for that column.
- It is better to return fewer valid suggestions than to include a weak or invalid chart.

FINAL CHECK BEFORE OUTPUT:
- Ensure the result is valid JSON.
- Ensure every object uses the exact required schema.
- Ensure every chart is buildable from the provided columns.
- Ensure suggestions are diverse in both chart type and analytical angle when possible.

Return ONLY the JSON array."""


async def analyze_data(df: pd.DataFrame) -> list[dict]:
    """Send DataFrame summary to Gemini and get visualization suggestions."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Please set it in the .env file.")

    schema_summary = _build_schema_summary(df)

    user_prompt = f"""DATASET SUMMARY:

{schema_summary}

Analyze the dataset and return ONLY a JSON array with visualization suggestions."""

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
