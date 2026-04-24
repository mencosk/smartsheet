import type { TranslationKey } from "../i18n/locales";

interface LoadingStateProps {
  t: (key: TranslationKey) => string;
}

export function LoadingState({ t }: LoadingStateProps) {
  return (
    <div className="loading-state" role="status" aria-live="polite" aria-busy="true">
      <div className="loading-state__spinner">
        <div className="spinner"></div>
      </div>
      <h2 className="loading-state__title">{t("processing")}</h2>
      <p className="loading-state__subtitle">{t("processingSubtitle")}</p>
    </div>
  );
}
