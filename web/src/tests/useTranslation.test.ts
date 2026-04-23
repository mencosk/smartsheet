import { renderHook, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useTranslation } from "../i18n/useTranslation";
import { locales } from "../i18n/locales";

describe("useTranslation", () => {
  it("defaults to Spanish", () => {
    const { result } = renderHook(() => useTranslation());
    expect(result.current.locale).toBe("es");
    expect(result.current.t("appTitle")).toBe(locales.es.appTitle);
  });

  it("returns Spanish translations", () => {
    const { result } = renderHook(() => useTranslation("es"));
    expect(result.current.t("processButton")).toBe("Procesar Archivo");
    expect(result.current.t("uploadTitle")).toBe("Sube tu archivo");
  });

  it("returns English translations when set", () => {
    const { result } = renderHook(() => useTranslation("en"));
    expect(result.current.t("processButton")).toBe("Process File");
    expect(result.current.t("uploadTitle")).toBe("Upload your file");
  });

  it("can switch locale dynamically", () => {
    const { result } = renderHook(() => useTranslation("es"));
    expect(result.current.t("appTitle")).toBe("SmartSheet");

    act(() => {
      result.current.setLocale("en");
    });

    expect(result.current.locale).toBe("en");
    expect(result.current.t("processButton")).toBe("Process File");
  });
});
