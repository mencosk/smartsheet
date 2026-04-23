import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LoadingState } from "../components/LoadingState";
import { locales } from "../i18n/locales";

const t = (key: keyof typeof locales.es) => locales.es[key];

describe("LoadingState", () => {
  it("renders the processing title", () => {
    render(<LoadingState t={t} />);
    expect(screen.getByText(locales.es.processing)).toBeInTheDocument();
  });

  it("renders the processing subtitle", () => {
    render(<LoadingState t={t} />);
    expect(screen.getByText(locales.es.processingSubtitle)).toBeInTheDocument();
  });

  it("renders a spinner element", () => {
    const { container } = render(<LoadingState t={t} />);
    expect(container.querySelector(".spinner")).toBeInTheDocument();
  });
});
