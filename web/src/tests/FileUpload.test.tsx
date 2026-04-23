import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { FileUpload } from "../components/FileUpload";
import { locales } from "../i18n/locales";

const t = (key: keyof typeof locales.es) => locales.es[key];

describe("FileUpload", () => {
  it("renders the drop zone when no file is selected", () => {
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={null} onClear={vi.fn()} t={t} />
    );
    expect(screen.getByText(locales.es.uploadSubtitle)).toBeInTheDocument();
    expect(screen.getByText(locales.es.uploadFormats)).toBeInTheDocument();
    expect(screen.getByText(locales.es.uploadMaxSize)).toBeInTheDocument();
  });

  it("shows file preview when a file is selected", () => {
    const file = new File(["content"], "data.csv", { type: "text/csv" });
    Object.defineProperty(file, "size", { value: 2048 });
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={file} onClear={vi.fn()} t={t} />
    );
    expect(screen.getByText("data.csv")).toBeInTheDocument();
    expect(screen.getByText("2.0 KB")).toBeInTheDocument();
  });

  it("calls onClear when remove button is clicked", async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    const file = new File(["content"], "data.csv", { type: "text/csv" });
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={file} onClear={onClear} t={t} />
    );
    await user.click(screen.getByLabelText("Remove file"));
    expect(onClear).toHaveBeenCalledTimes(1);
  });

  it("calls onFileSelect when a file is dropped", () => {
    const onFileSelect = vi.fn();
    render(
      <FileUpload onFileSelect={onFileSelect} selectedFile={null} onClear={vi.fn()} t={t} />
    );
    const dropZone = screen.getByText(locales.es.uploadSubtitle).closest(".drop-zone")!;
    const file = new File(["data"], "test.xlsx", {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    fireEvent.drop(dropZone, {
      dataTransfer: { files: [file] },
    });

    expect(onFileSelect).toHaveBeenCalledWith(file);
  });

  it("shows drag active text when dragging over", () => {
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={null} onClear={vi.fn()} t={t} />
    );
    const dropZone = screen.getByText(locales.es.uploadSubtitle).closest(".drop-zone")!;
    fireEvent.dragEnter(dropZone);
    expect(screen.getByText(locales.es.dragActive)).toBeInTheDocument();
  });

  it("formats bytes correctly", () => {
    const file = new File(["x"], "small.csv", { type: "text/csv" });
    Object.defineProperty(file, "size", { value: 500 });
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={file} onClear={vi.fn()} t={t} />
    );
    expect(screen.getByText("500 B")).toBeInTheDocument();
  });

  it("formats MB correctly", () => {
    const file = new File(["x"], "big.csv", { type: "text/csv" });
    Object.defineProperty(file, "size", { value: 5 * 1024 * 1024 });
    render(
      <FileUpload onFileSelect={vi.fn()} selectedFile={file} onClear={vi.fn()} t={t} />
    );
    expect(screen.getByText("5.0 MB")).toBeInTheDocument();
  });
});
