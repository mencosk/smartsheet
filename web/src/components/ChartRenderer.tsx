import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { fetchChartData, type ChartDataPoint, type Suggestion } from "../api/client";
import type { TranslationKey } from "../i18n/locales";

interface ChartRendererProps {
  suggestion: Suggestion;
  sessionId: string;
  t: (key: TranslationKey) => string;
}

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a855f7",
  "#d946ef",
  "#ec4899",
  "#f43f5e",
  "#f97316",
  "#eab308",
  "#22c55e",
  "#14b8a6",
  "#06b6d4",
  "#3b82f6",
];

const tooltipStyle = {
  background: "#1e293b",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "8px",
  color: "#f1f5f9",
};

export function ChartRenderer({ suggestion, sessionId, t }: ChartRendererProps) {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const chartData = await fetchChartData(
          sessionId,
          suggestion.chart_type,
          suggestion.parameters
        );
        if (!cancelled) setData(chartData);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Error loading data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [sessionId, suggestion]);

  if (loading) {
    return (
      <div className="chart-loading">
        <div className="spinner spinner--small"></div>
        <span>{t("loadingChart")}</span>
      </div>
    );
  }

  if (error) return <div className="chart-error">{error}</div>;
  if (!data.length) return <div className="chart-error">No data available</div>;

  const axisMargin = { top: 5, right: 20, bottom: 60, left: 20 };
  const axisTick = { fontSize: 11, fill: "#94a3b8" };

  const renderChart = () => {
    switch (suggestion.chart_type) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={axisMargin}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="name"
                tick={axisTick}
                angle={-35}
                textAnchor="end"
                interval={0}
                height={80}
              />
              <YAxis tick={axisTick} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={axisMargin}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="name"
                tick={axisTick}
                angle={-35}
                textAnchor="end"
                interval={0}
                height={80}
              />
              <YAxis tick={axisTick} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: "#8b5cf6", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "area":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data} margin={axisMargin}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="name"
                tick={axisTick}
                angle={-35}
                textAnchor="end"
                interval={0}
                height={80}
              />
              <YAxis tick={axisTick} />
              <Tooltip contentStyle={tooltipStyle} />
              <defs>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke="#06b6d4"
                fill="url(#areaGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={50}
                paddingAngle={2}
                label={({ name, percent }: { name?: string; percent?: number }) =>
                  `${name ?? ""} (${((percent ?? 0) * 100).toFixed(0)}%)`
                }
                labelLine={{ stroke: "#64748b" }}
              >
                {data.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            </PieChart>
          </ResponsiveContainer>
        );

      case "scatter":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 5, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="x"
                name={suggestion.parameters.x_axis}
                tick={axisTick}
              />
              <YAxis
                dataKey="y"
                name={suggestion.parameters.y_axis}
                tick={axisTick}
              />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={tooltipStyle} />
              <Scatter data={data} fill="#a855f7" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unsupported chart type: {suggestion.chart_type}</div>;
    }
  };

  return <div className="chart-renderer">{renderChart()}</div>;
}
