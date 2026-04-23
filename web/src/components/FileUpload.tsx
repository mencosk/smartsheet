import { useCallback, useRef, useState } from "react";
import { Upload, FileSpreadsheet, X } from "lucide-react";
import type { TranslationKey } from "../i18n/locales";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  t: (key: TranslationKey) => string;
}

export function FileUpload({ onFileSelect, selectedFile, onClear, t }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        onFileSelect(e.target.files[0]);
      }
    },
    [onFileSelect]
  );

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="file-upload-container">
      {!selectedFile ? (
        <div
          className={`drop-zone ${isDragging ? "drop-zone--active" : ""}`}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            onChange={handleChange}
            style={{ display: "none" }}
          />
          <div className="drop-zone__icon">
            <Upload size={48} strokeWidth={1.5} />
          </div>
          <p className="drop-zone__title">
            {isDragging ? t("dragActive") : t("uploadSubtitle")}
          </p>
          <div className="drop-zone__info">
            <span>{t("uploadFormats")}</span>
            <span>{t("uploadMaxSize")}</span>
          </div>
        </div>
      ) : (
        <div className="file-preview">
          <FileSpreadsheet size={32} />
          <div className="file-preview__info">
            <span className="file-preview__name">{selectedFile.name}</span>
            <span className="file-preview__size">{formatSize(selectedFile.size)}</span>
          </div>
          <button className="file-preview__remove" onClick={onClear} aria-label="Remove file">
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
