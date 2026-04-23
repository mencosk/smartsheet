import io
import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.file_processor import process_file
from app.services.chart_data_builder import build_chart_data
from app.services.ai_analyzer import _build_schema_summary, analyze_data


class TestFileProcessor:
    def test_parse_csv(self):
        content = b"name,age\nAlice,30\nBob,25"
        df = process_file(content, ".csv")
        assert len(df) == 2
        assert list(df.columns) == ["name", "age"]

    def test_parse_csv_latin1(self):
        content = "name,city\nAlice,São Paulo\nBob,Zürich".encode("latin-1")
        df = process_file(content, ".csv")
        assert len(df) == 2
        assert "São Paulo" in df["city"].values

    def test_unsupported_extension(self):
        with pytest.raises(ValueError, match="Unsupported file extension"):
            process_file(b"data", ".json")


class TestChartDataBuilder:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "Region": ["A", "B", "A", "B", "C"],
                "Sales": [10, 20, 30, 40, 50],
                "Quantity": [1, 2, 3, 4, 5],
            }
        )

    def test_bar_chart_sum(self, sample_df):
        result = build_chart_data(sample_df, "bar", {
            "x_axis": "Region", "y_axis": "Sales", "aggregation": "sum"
        })
        assert isinstance(result, list)
        a = next(r for r in result if r["name"] == "A")
        assert a["value"] == 40

    def test_bar_chart_count(self, sample_df):
        result = build_chart_data(sample_df, "bar", {
            "x_axis": "Region", "y_axis": "Sales", "aggregation": "count"
        })
        a = next(r for r in result if r["name"] == "A")
        assert a["value"] == 2

    def test_pie_chart_sum(self, sample_df):
        result = build_chart_data(sample_df, "pie", {
            "category": "Region", "value": "Sales", "aggregation": "sum"
        })
        assert len(result) == 3

    def test_pie_chart_count(self, sample_df):
        result = build_chart_data(sample_df, "pie", {
            "category": "Region", "aggregation": "count"
        })
        a = next(r for r in result if r["name"] == "A")
        assert a["value"] == 2

    def test_pie_chart_groups_others(self):
        df = pd.DataFrame({
            "Cat": [f"cat_{i}" for i in range(15)],
            "Val": list(range(15)),
        })
        result = build_chart_data(df, "pie", {
            "category": "Cat", "value": "Val", "aggregation": "sum"
        })
        names = [r["name"] for r in result]
        assert "Otros" in names
        assert len(result) == 10

    def test_scatter_chart(self, sample_df):
        result = build_chart_data(sample_df, "scatter", {
            "x_axis": "Sales", "y_axis": "Quantity"
        })
        assert len(result) == 5
        assert "x" in result[0]
        assert "y" in result[0]

    def test_scatter_limits_to_500(self):
        df = pd.DataFrame({
            "x": range(1000),
            "y": range(1000),
        })
        result = build_chart_data(df, "scatter", {"x_axis": "x", "y_axis": "y"})
        assert len(result) == 500

    def test_bar_limits_to_20(self):
        df = pd.DataFrame({
            "Cat": [f"c{i}" for i in range(30)],
            "Val": list(range(30)),
        })
        result = build_chart_data(df, "bar", {
            "x_axis": "Cat", "y_axis": "Val", "aggregation": "sum"
        })
        assert len(result) == 20

    def test_invalid_column_raises_key_error(self, sample_df):
        with pytest.raises(KeyError, match="Column 'Missing'"):
            build_chart_data(sample_df, "bar", {
                "x_axis": "Missing", "y_axis": "Sales", "aggregation": "sum"
            })

    def test_unsupported_chart_type(self, sample_df):
        with pytest.raises(ValueError, match="Unsupported chart type"):
            build_chart_data(sample_df, "heatmap", {"x_axis": "Region", "y_axis": "Sales"})


class TestSchemaBuilder:
    def test_builds_summary(self):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        summary = _build_schema_summary(df)
        assert "2 rows" in summary
        assert "2 columns" in summary
        assert "a" in summary
        assert "b" in summary


class TestAIAnalyzer:
    @pytest.mark.asyncio
    async def test_missing_api_key_raises(self):
        df = pd.DataFrame({"a": [1]})
        with patch("app.services.ai_analyzer.settings") as mock_settings:
            mock_settings.gemini_api_key = ""
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                await analyze_data(df)

    @pytest.mark.asyncio
    async def test_parses_valid_json_response(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        expected = [{"title": "Test", "chart_type": "bar", "parameters": {}, "insight": "x"}]

        mock_response = MagicMock()
        mock_response.text = json.dumps(expected)

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_client = MagicMock()
        mock_client.models = mock_model

        with patch("app.services.ai_analyzer.settings") as mock_settings, \
             patch("app.services.ai_analyzer.genai.Client", return_value=mock_client):
            mock_settings.gemini_api_key = "test-key"
            result = await analyze_data(df)

        assert result == expected

    @pytest.mark.asyncio
    async def test_strips_markdown_fences(self):
        df = pd.DataFrame({"a": [1]})
        expected = [{"title": "T", "chart_type": "bar", "parameters": {}, "insight": "i"}]
        raw = f"```json\n{json.dumps(expected)}\n```"

        mock_response = MagicMock()
        mock_response.text = raw

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_client = MagicMock()
        mock_client.models = mock_model

        with patch("app.services.ai_analyzer.settings") as mock_settings, \
             patch("app.services.ai_analyzer.genai.Client", return_value=mock_client):
            mock_settings.gemini_api_key = "test-key"
            result = await analyze_data(df)

        assert result == expected

    @pytest.mark.asyncio
    async def test_invalid_json_raises(self):
        df = pd.DataFrame({"a": [1]})

        mock_response = MagicMock()
        mock_response.text = "not valid json at all"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_client = MagicMock()
        mock_client.models = mock_model

        with patch("app.services.ai_analyzer.settings") as mock_settings, \
             patch("app.services.ai_analyzer.genai.Client", return_value=mock_client):
            mock_settings.gemini_api_key = "test-key"
            with pytest.raises(ValueError, match="invalid JSON"):
                await analyze_data(df)

    @pytest.mark.asyncio
    async def test_non_array_response_raises(self):
        df = pd.DataFrame({"a": [1]})

        mock_response = MagicMock()
        mock_response.text = '{"not": "an array"}'

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_client = MagicMock()
        mock_client.models = mock_model

        with patch("app.services.ai_analyzer.settings") as mock_settings, \
             patch("app.services.ai_analyzer.genai.Client", return_value=mock_client):
            mock_settings.gemini_api_key = "test-key"
            with pytest.raises(ValueError, match="not a JSON array"):
                await analyze_data(df)
