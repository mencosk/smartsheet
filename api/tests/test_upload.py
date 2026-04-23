import io
from unittest.mock import AsyncMock, patch

import pandas as pd


def _make_csv(content: str = "name,value\nAlice,10\nBob,20\nCharlie,30") -> io.BytesIO:
    """Helper to create a CSV file-like object."""
    return io.BytesIO(content.encode("utf-8"))


def _make_upload(client, filename="test.csv", content=None):
    """Helper to upload a file."""
    if content is None:
        content = _make_csv()
    return client.post(
        "/api/upload",
        files={"file": (filename, content, "text/csv")},
    )


class TestUploadValidation:
    def test_rejects_unsupported_extension(self, client):
        file = io.BytesIO(b"some data")
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", file, "text/plain")},
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    def test_rejects_empty_file(self, client):
        mock_suggestions = [{"title": "Test", "chart_type": "bar", "parameters": {}, "insight": "x"}]
        with patch("app.routers.upload.process_file") as mock_proc:
            mock_proc.return_value = pd.DataFrame()
            response = _make_upload(client)
        assert response.status_code == 400
        assert "no data" in response.json()["detail"].lower()

    def test_rejects_oversized_file(self, client):
        with patch("app.routers.upload.settings") as mock_settings:
            mock_settings.max_file_size_mb = 0.0001  # Tiny limit
            mock_settings.allowed_extensions = [".csv", ".xlsx"]
            large = io.BytesIO(b"x" * 1024)
            response = client.post(
                "/api/upload",
                files={"file": ("test.csv", large, "text/csv")},
            )
        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"]

    def test_rejects_no_extension(self, client):
        file = io.BytesIO(b"some data")
        response = client.post(
            "/api/upload",
            files={"file": ("testfile", file, "application/octet-stream")},
        )
        assert response.status_code == 400


class TestUploadSuccess:
    def test_successful_csv_upload(self, client):
        mock_suggestions = [
            {
                "title": "Test Chart",
                "chart_type": "bar",
                "parameters": {"x_axis": "name", "y_axis": "value", "aggregation": "sum"},
                "insight": "Test insight",
            }
        ]
        with patch("app.routers.upload.analyze_data", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = mock_suggestions
            response = _make_upload(client)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["rows"] == 3
        assert data["columns"] == ["name", "value"]
        assert len(data["suggestions"]) == 1
        assert data["suggestions"][0]["title"] == "Test Chart"

    def test_stores_session_for_later_retrieval(self, client):
        mock_suggestions = []
        with patch("app.routers.upload.analyze_data", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = mock_suggestions
            response = _make_upload(client)

        session_id = response.json()["session_id"]
        assert session_id

        # Verify the session exists by requesting chart data
        chart_response = client.post(
            "/api/chart-data",
            json={
                "session_id": session_id,
                "chart_type": "bar",
                "parameters": {"x_axis": "name", "y_axis": "value", "aggregation": "sum"},
            },
        )
        assert chart_response.status_code == 200

    def test_ai_failure_returns_500(self, client):
        with patch("app.routers.upload.analyze_data", new_callable=AsyncMock) as mock_ai:
            mock_ai.side_effect = Exception("Gemini API error")
            response = _make_upload(client)

        assert response.status_code == 500
        assert "AI analysis failed" in response.json()["detail"]
