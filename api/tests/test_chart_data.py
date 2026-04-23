from unittest.mock import AsyncMock, patch

import pandas as pd

from app.routers.upload import _dataframes


def _seed_session(session_id: str = "test-session"):
    """Seed a DataFrame into the in-memory store."""
    df = pd.DataFrame(
        {
            "Region": ["North", "South", "East", "West", "North", "South"],
            "Sales": [100, 200, 150, 300, 250, 175],
            "Category": ["A", "B", "A", "B", "A", "B"],
            "Price": [10.5, 20.3, 15.0, 30.0, 25.0, 17.5],
        }
    )
    _dataframes[session_id] = df
    return session_id


class TestChartDataEndpoint:
    def test_session_not_found(self, client):
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": "nonexistent",
                "chart_type": "bar",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_bar_chart_sum_aggregation(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "bar",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 4
        names = {item["name"] for item in data}
        assert names == {"North", "South", "East", "West"}
        north = next(item for item in data if item["name"] == "North")
        assert north["value"] == 350

    def test_bar_chart_mean_aggregation(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "bar",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "mean"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        north = next(item for item in data if item["name"] == "North")
        assert north["value"] == 175.0

    def test_bar_chart_count_aggregation(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "bar",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "count"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        north = next(item for item in data if item["name"] == "North")
        assert north["value"] == 2

    def test_pie_chart(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "pie",
                "parameters": {"category": "Category", "value": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        cat_a = next(item for item in data if item["name"] == "A")
        assert cat_a["value"] == 500

    def test_pie_chart_count(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "pie",
                "parameters": {"category": "Region", "aggregation": "count"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        north = next(item for item in data if item["name"] == "North")
        assert north["value"] == 2

    def test_scatter_chart(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "scatter",
                "parameters": {"x_axis": "Sales", "y_axis": "Price"},
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 6
        assert "x" in data[0]
        assert "y" in data[0]

    def test_line_chart(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "line",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) == 4

    def test_area_chart(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "area",
                "parameters": {"x_axis": "Region", "y_axis": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) == 4

    def test_invalid_column(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "bar",
                "parameters": {"x_axis": "NonExistent", "y_axis": "Sales", "aggregation": "sum"},
            },
        )
        assert response.status_code == 400
        assert "Column not found" in response.json()["detail"]

    def test_unsupported_chart_type(self, client):
        sid = _seed_session()
        response = client.post(
            "/api/chart-data",
            json={
                "session_id": sid,
                "chart_type": "radar",
                "parameters": {"x_axis": "Region", "y_axis": "Sales"},
            },
        )
        assert response.status_code == 400
        assert "Unsupported chart type" in response.json()["detail"]

    def test_missing_required_fields(self, client):
        response = client.post(
            "/api/chart-data",
            json={"chart_type": "bar", "parameters": {}},
        )
        assert response.status_code == 422
