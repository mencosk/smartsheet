import { describe, it, expect, vi, beforeEach } from "vitest";
import { uploadFile, fetchChartData } from "../api/client";

describe("API client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("uploadFile", () => {
    it("sends a POST request with the file as FormData", async () => {
      const mockResponse = {
        session_id: "abc-123",
        rows: 10,
        columns: ["a", "b"],
        suggestions: [],
      };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const file = new File(["test"], "test.csv", { type: "text/csv" });
      const result = await uploadFile(file);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/upload"),
        expect.objectContaining({ method: "POST" })
      );
      expect(result).toEqual(mockResponse);
    });

    it("throws an error on non-ok response", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ detail: "Bad file" }),
      });

      const file = new File(["test"], "test.csv", { type: "text/csv" });
      await expect(uploadFile(file)).rejects.toThrow("Bad file");
    });

    it("handles JSON parse failure gracefully", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.reject(new Error("parse error")),
      });

      const file = new File(["test"], "test.csv", { type: "text/csv" });
      await expect(uploadFile(file)).rejects.toThrow("Upload failed");
    });
  });

  describe("fetchChartData", () => {
    it("sends correct JSON body", async () => {
      const mockData = [{ name: "A", value: 10 }];
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: mockData }),
      });

      const result = await fetchChartData("session-1", "bar", {
        x_axis: "Region",
        y_axis: "Sales",
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/chart-data"),
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
        })
      );
      expect(result).toEqual(mockData);
    });

    it("throws on error response", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ detail: "Column not found" }),
      });

      await expect(
        fetchChartData("session-1", "bar", { x_axis: "Bad" })
      ).rejects.toThrow("Column not found");
    });
  });
});
