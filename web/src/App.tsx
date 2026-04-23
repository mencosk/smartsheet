import { useState, useCallback } from "react";
import { RotateCcw } from "lucide-react";
import { FileUpload } from "./components/FileUpload";
import { LoadingState } from "./components/LoadingState";
import { AnalysisCard } from "./components/AnalysisCard";
import { Dashboard } from "./components/Dashboard";
import { uploadFile, type Suggestion, type UploadResponse } from "./api/client";
import { useTranslation } from "./i18n/useTranslation";

type AppState = "upload" | "processing" | "results";

function App() {
  const { t } = useTranslation("es");
  const [state, setState] = useState<AppState>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [uploadInfo, setUploadInfo] = useState<{
    rows: number;
    columns: string[];
  } | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [dashboardItems, setDashboardItems] = useState<Suggestion[]>([]);

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
  }, []);

  const handleClear = useCallback(() => {
    setFile(null);
    setError(null);
  }, []);

  const handleProcess = useCallback(async () => {
    if (!file) return;

    setState("processing");
    setError(null);

    try {
      const response: UploadResponse = await uploadFile(file);
      setSessionId(response.session_id);
      setUploadInfo({ rows: response.rows, columns: response.columns });
      setSuggestions(response.suggestions);
      setDashboardItems([]);
      setState("results");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setState("upload");
    }
  }, [file]);

  const handleToggleSuggestion = useCallback((suggestion: Suggestion) => {
    setDashboardItems((prev) => {
      const exists = prev.some((s) => s.title === suggestion.title);
      if (exists) {
        return prev.filter((s) => s.title !== suggestion.title);
      }
      return [...prev, suggestion];
    });
  }, []);

  const handleRemoveFromDashboard = useCallback((index: number) => {
    setDashboardItems((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleReset = useCallback(() => {
    setState("upload");
    setFile(null);
    setError(null);
    setSessionId("");
    setUploadInfo(null);
    setSuggestions([]);
    setDashboardItems([]);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="header__content">
          <div className="header__brand">
            <h1 className="header__title">{t("appTitle")}</h1>
            <p className="header__subtitle">{t("appSubtitle")}</p>
          </div>
          {state === "results" && (
            <button className="btn btn--outline" onClick={handleReset}>
              <RotateCcw size={16} />
              {t("newAnalysis")}
            </button>
          )}
        </div>
      </header>

      <main className="main">
        {state === "upload" && (
          <section className="section section--upload">
            <h2 className="section__title">{t("uploadTitle")}</h2>
            <FileUpload
              onFileSelect={handleFileSelect}
              selectedFile={file}
              onClear={handleClear}
              t={t}
            />
            {error && (
              <div className="error-banner">
                <strong>{t("errorTitle")}:</strong> {error}
              </div>
            )}
            {file && (
              <button className="btn btn--primary btn--lg" onClick={handleProcess}>
                {t("processButton")}
              </button>
            )}
          </section>
        )}

        {state === "processing" && <LoadingState t={t} />}

        {state === "results" && (
          <>
            {uploadInfo && (
              <div className="data-summary">
                <div className="data-summary__item">
                  <span className="data-summary__value">
                    {uploadInfo.rows.toLocaleString()}
                  </span>
                  <span className="data-summary__label">{t("rowsLoaded")}</span>
                </div>
                <div className="data-summary__item">
                  <span className="data-summary__value">
                    {uploadInfo.columns.length}
                  </span>
                  <span className="data-summary__label">{t("columnsDetected")}</span>
                </div>
              </div>
            )}

            <section className="section">
              <h2 className="section__title">{t("suggestionsTitle")}</h2>
              <p className="section__subtitle">{t("suggestionsSubtitle")}</p>
              <div className="cards-grid">
                {suggestions.map((suggestion, index) => (
                  <AnalysisCard
                    key={index}
                    suggestion={suggestion}
                    isAdded={dashboardItems.some((s) => s.title === suggestion.title)}
                    onToggle={() => handleToggleSuggestion(suggestion)}
                    t={t}
                  />
                ))}
              </div>
            </section>

            <section className="section">
              <h2 className="section__title">{t("dashboardTitle")}</h2>
              <Dashboard
                items={dashboardItems}
                sessionId={sessionId}
                onRemove={handleRemoveFromDashboard}
                t={t}
              />
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <p>© Kevin Mencos</p>
      </footer>
    </div>
  );
}

export default App;
