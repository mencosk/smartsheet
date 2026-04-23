import pandas as pd


def build_chart_data(df: pd.DataFrame, chart_type: str, parameters: dict) -> list[dict]:
    """Build aggregated, chart-ready data from the DataFrame."""
    if chart_type in ("bar", "line", "area"):
        return _build_axis_chart(df, parameters)
    elif chart_type == "pie":
        return _build_pie_chart(df, parameters)
    elif chart_type == "scatter":
        return _build_scatter_chart(df, parameters)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")


def _build_axis_chart(df: pd.DataFrame, params: dict) -> list[dict]:
    """Build data for bar, line, and area charts."""
    x = params["x_axis"]
    y = params["y_axis"]
    agg = params.get("aggregation", "sum")

    _validate_columns(df, [x, y])

    if agg == "count":
        grouped = df.groupby(x, dropna=False).size().reset_index(name="count")
        grouped = grouped.rename(columns={x: "name"})
        grouped["value"] = grouped["count"]
        grouped = grouped[["name", "value"]]
    else:
        grouped = df.groupby(x, dropna=False)[y].agg(agg).reset_index()
        grouped.columns = ["name", "value"]

    # Sort by name if possible, otherwise by value
    try:
        grouped = grouped.sort_values("name")
    except TypeError:
        grouped = grouped.sort_values("value", ascending=False)

    # Limit to top 20 categories for readability
    if len(grouped) > 20:
        grouped = grouped.nlargest(20, "value")

    grouped["name"] = grouped["name"].astype(str)
    grouped["value"] = pd.to_numeric(grouped["value"], errors="coerce").fillna(0)

    return grouped.to_dict(orient="records")


def _build_pie_chart(df: pd.DataFrame, params: dict) -> list[dict]:
    """Build data for pie charts."""
    category = params["category"]
    value = params.get("value", category)
    agg = params.get("aggregation", "count")

    _validate_columns(df, [category])

    if agg == "count":
        grouped = df.groupby(category, dropna=False).size().reset_index(name="value")
        grouped = grouped.rename(columns={category: "name"})
    else:
        _validate_columns(df, [value])
        grouped = df.groupby(category, dropna=False)[value].agg(agg).reset_index()
        grouped.columns = ["name", "value"]

    # Top 10 + "Others"
    if len(grouped) > 10:
        top = grouped.nlargest(9, "value")
        others_val = grouped.loc[~grouped.index.isin(top.index), "value"].sum()
        others_row = pd.DataFrame([{"name": "Otros", "value": others_val}])
        grouped = pd.concat([top, others_row], ignore_index=True)

    grouped["name"] = grouped["name"].astype(str)
    grouped["value"] = pd.to_numeric(grouped["value"], errors="coerce").fillna(0)

    return grouped.to_dict(orient="records")


def _build_scatter_chart(df: pd.DataFrame, params: dict) -> list[dict]:
    """Build data for scatter charts."""
    x = params["x_axis"]
    y = params["y_axis"]

    _validate_columns(df, [x, y])

    scatter_df = df[[x, y]].dropna()
    scatter_df.columns = ["x", "y"]

    # Limit to 500 points for performance
    if len(scatter_df) > 500:
        scatter_df = scatter_df.sample(500, random_state=42)

    scatter_df["x"] = pd.to_numeric(scatter_df["x"], errors="coerce")
    scatter_df["y"] = pd.to_numeric(scatter_df["y"], errors="coerce")
    scatter_df = scatter_df.dropna()

    return scatter_df.to_dict(orient="records")


def _validate_columns(df: pd.DataFrame, columns: list[str]):
    """Check that all requested columns exist in the DataFrame."""
    for col in columns:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found. Available: {list(df.columns)}")
