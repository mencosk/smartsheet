import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { AnalysisCard } from "../components/AnalysisCard";
import { locales } from "../i18n/locales";
import type { Suggestion } from "../api/client";

const t = (key: keyof typeof locales.es) => locales.es[key];

const mockSuggestion: Suggestion = {
  title: "Ventas por Región",
  chart_type: "bar",
  parameters: { x_axis: "Region", y_axis: "Sales", aggregation: "sum" },
  insight: "La región Norte lidera las ventas.",
};

describe("AnalysisCard", () => {
  it("renders the suggestion title", () => {
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={false} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText("Ventas por Región")).toBeInTheDocument();
  });

  it("renders the insight text", () => {
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={false} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText("La región Norte lidera las ventas.")).toBeInTheDocument();
  });

  it("renders chart type label", () => {
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={false} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText("bar")).toBeInTheDocument();
  });

  it("shows 'add to dashboard' button when not added", () => {
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={false} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText(locales.es.addToDashboard)).toBeInTheDocument();
  });

  it("shows 'added' button when added", () => {
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={true} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText(locales.es.added)).toBeInTheDocument();
  });

  it("applies added class when isAdded is true", () => {
    const { container } = render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={true} onToggle={vi.fn()} t={t} />
    );
    expect(container.querySelector(".analysis-card--added")).toBeInTheDocument();
  });

  it("calls onToggle when button is clicked", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    render(
      <AnalysisCard suggestion={mockSuggestion} isAdded={false} onToggle={onToggle} t={t} />
    );
    await user.click(screen.getByText(locales.es.addToDashboard));
    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it("renders different chart types correctly", () => {
    const pieSuggestion: Suggestion = {
      ...mockSuggestion,
      chart_type: "pie",
    };
    render(
      <AnalysisCard suggestion={pieSuggestion} isAdded={false} onToggle={vi.fn()} t={t} />
    );
    expect(screen.getByText("pie")).toBeInTheDocument();
  });
});
