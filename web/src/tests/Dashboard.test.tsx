import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Dashboard } from "../components/Dashboard";
import { locales } from "../i18n/locales";
import type { Suggestion } from "../api/client";

// Mock ChartRenderer since it makes API calls
vi.mock("../components/ChartRenderer", () => ({
  ChartRenderer: ({ suggestion }: { suggestion: Suggestion }) => (
    <div data-testid={`chart-${suggestion.chart_type}`}>Mock Chart</div>
  ),
}));

const t = (key: keyof typeof locales.es) => locales.es[key];

const mockItems: Suggestion[] = [
  {
    title: "Chart 1",
    chart_type: "bar",
    parameters: { x_axis: "A", y_axis: "B", aggregation: "sum" },
    insight: "Insight 1",
  },
  {
    title: "Chart 2",
    chart_type: "pie",
    parameters: { category: "C", value: "D", aggregation: "count" },
    insight: "Insight 2",
  },
];

describe("Dashboard", () => {
  it("renders empty state when no items", () => {
    render(
      <Dashboard items={[]} sessionId="test" onRemove={vi.fn()} t={t} />
    );
    expect(screen.getByText(locales.es.dashboardEmpty)).toBeInTheDocument();
  });

  it("renders dashboard cards for each item", () => {
    render(
      <Dashboard items={mockItems} sessionId="test" onRemove={vi.fn()} t={t} />
    );
    expect(screen.getByText("Chart 1")).toBeInTheDocument();
    expect(screen.getByText("Chart 2")).toBeInTheDocument();
    expect(screen.getByText("Insight 1")).toBeInTheDocument();
    expect(screen.getByText("Insight 2")).toBeInTheDocument();
  });

  it("renders chart components for each item", () => {
    render(
      <Dashboard items={mockItems} sessionId="test" onRemove={vi.fn()} t={t} />
    );
    expect(screen.getByTestId("chart-bar")).toBeInTheDocument();
    expect(screen.getByTestId("chart-pie")).toBeInTheDocument();
  });

  it("calls onRemove with correct index when remove button is clicked", async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();
    render(
      <Dashboard items={mockItems} sessionId="test" onRemove={onRemove} t={t} />
    );
    const removeButtons = screen.getAllByLabelText(locales.es.removeFromDashboard);
    await user.click(removeButtons[1]);
    expect(onRemove).toHaveBeenCalledWith(1);
  });

  it("renders correct number of remove buttons", () => {
    render(
      <Dashboard items={mockItems} sessionId="test" onRemove={vi.fn()} t={t} />
    );
    const removeButtons = screen.getAllByLabelText(locales.es.removeFromDashboard);
    expect(removeButtons).toHaveLength(2);
  });
});
