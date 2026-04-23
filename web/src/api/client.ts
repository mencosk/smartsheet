const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export interface Suggestion {
  title: string;
  chart_type: "bar" | "line" | "pie" | "scatter" | "area";
  parameters: Record<string, string>;
  insight: string;
}

export interface UploadResponse {
  session_id: string;
  rows: number;
  columns: string[];
  suggestions: Suggestion[];
}

export interface ChartDataPoint {
  name?: string;
  value?: number;
  x?: number;
  y?: number;
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function fetchChartData(
  sessionId: string,
  chartType: string,
  parameters: Record<string, string>
): Promise<ChartDataPoint[]> {
  const response = await fetch(`${API_BASE}/chart-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      chart_type: chartType,
      parameters,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch data" }));
    throw new Error(error.detail || "Failed to fetch data");
  }

  const result = await response.json();
  return result.data;
}
