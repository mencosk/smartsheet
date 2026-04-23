import { X } from "lucide-react";
import type { Suggestion } from "../api/client";
import { ChartRenderer } from "./ChartRenderer";
import type { TranslationKey } from "../i18n/locales";

interface DashboardProps {
  items: Suggestion[];
  sessionId: string;
  onRemove: (index: number) => void;
  t: (key: TranslationKey) => string;
}

export function Dashboard({ items, sessionId, onRemove, t }: DashboardProps) {
  if (items.length === 0) {
    return (
      <div className="dashboard-empty">
        <p>{t("dashboardEmpty")}</p>
      </div>
    );
  }

  return (
    <div className="dashboard-grid">
      {items.map((item, index) => (
        <div key={`${item.title}-${index}`} className="dashboard-card">
          <div className="dashboard-card__header">
            <h3 className="dashboard-card__title">{item.title}</h3>
            <button
              className="dashboard-card__remove"
              onClick={() => onRemove(index)}
              aria-label={t("removeFromDashboard")}
            >
              <X size={16} />
            </button>
          </div>
          <ChartRenderer suggestion={item} sessionId={sessionId} t={t} />
          <p className="dashboard-card__insight">{item.insight}</p>
        </div>
      ))}
    </div>
  );
}
