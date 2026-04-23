import {
  BarChart3,
  LineChart,
  PieChart,
  ScatterChart as ScatterIcon,
  AreaChart,
  Plus,
  Check,
} from "lucide-react";
import type { Suggestion } from "../api/client";
import type { TranslationKey } from "../i18n/locales";

interface AnalysisCardProps {
  suggestion: Suggestion;
  isAdded: boolean;
  onToggle: () => void;
  t: (key: TranslationKey) => string;
}

const chartIcons: Record<string, React.ReactNode> = {
  bar: <BarChart3 size={24} />,
  line: <LineChart size={24} />,
  pie: <PieChart size={24} />,
  scatter: <ScatterIcon size={24} />,
  area: <AreaChart size={24} />,
};

export function AnalysisCard({ suggestion, isAdded, onToggle, t }: AnalysisCardProps) {
  return (
    <div className={`analysis-card ${isAdded ? "analysis-card--added" : ""}`}>
      <div className="analysis-card__header">
        <div className="analysis-card__icon">
          {chartIcons[suggestion.chart_type] || <BarChart3 size={24} />}
        </div>
        <span className="analysis-card__type">{suggestion.chart_type}</span>
      </div>
      <h3 className="analysis-card__title">{suggestion.title}</h3>
      <p className="analysis-card__insight">{suggestion.insight}</p>
      <button
        className={`analysis-card__btn ${isAdded ? "analysis-card__btn--added" : ""}`}
        onClick={onToggle}
      >
        {isAdded ? (
          <>
            <Check size={16} /> {t("added")}
          </>
        ) : (
          <>
            <Plus size={16} /> {t("addToDashboard")}
          </>
        )}
      </button>
    </div>
  );
}
