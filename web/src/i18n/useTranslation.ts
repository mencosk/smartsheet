import { useState, useCallback } from "react";
import { locales, type Locale, type TranslationKey } from "./locales";

export function useTranslation(defaultLocale: Locale = "es") {
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  const t = useCallback(
    (key: TranslationKey): string => {
      return locales[locale][key];
    },
    [locale]
  );

  return { t, locale, setLocale };
}
