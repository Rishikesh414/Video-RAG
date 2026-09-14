import React, { useState, useRef } from "react";
import { formatFileSize } from "../../utils/helpers";
import { MODULES } from "../../services/mockData";
import "./FileUpload.css";

/**
 * Enhanced FileUpload component — includes module tag selection,
 * drag-and-drop zone, file preview, and upload progress feedback.
 *
 * @param {Object} props
 * @param {Function} props.onUpload - Callback with (File, selectedModule)
 * @param {string} [props.accept="video/*,.pdf"] - Accepted file types
 * @param {string} [props.label="Upload a lecture file"]
 * @param {boolean} [props.isUploading=false]
 */
function FileUpload({
  onUpload,
  accept = "video/*,.pdf",
  label = "Upload a lecture file",
  isUploading = false,
}) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedModule, setSelectedModule] = useState("m1");
  const [uploadProgress, setUploadProgress] = useState(0);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    setSelectedFile(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile || isUploading) return;

    // Simulate progress animation
    setUploadProgress(15);
    const interval = setInterval(() => {
      setUploadProgress((p) => {
        if (p >= 90) {
          clearInterval(interval);
          return 90;
        }
        return p + 25;
      });
    }, 200);

    onUpload?.(selectedFile, selectedModule);
  };

  const clearFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (inputRef.current) inputRef.current.value = "";
  };

  const isVideo = selectedFile?.type?.startsWith("video/") || selectedFile?.name?.endsWith(".mp4");

  return (
    <div className="file-upload" id="file-upload">
      {/* Module Selector */}
      <div className="file-upload__module-select">
        <label htmlFor="upload-module" className="file-upload__field-label">
          Target Curriculum Module:
        </label>
        <select
          id="upload-module"
          className="file-upload__select"
          value={selectedModule}
          onChange={(e) => setSelectedModule(e.target.value)}
          disabled={isUploading}
        >
          {MODULES.filter((m) => m.id !== "all").map((m) => (
            <option key={m.id} value={m.id}>
              [{m.code}] {m.title}
            </option>
          ))}
        </select>
      </div>

      {/* Drag & Drop Zone */}
      <div
        className={`file-upload__dropzone ${
          dragActive ? "file-upload__dropzone--active" : ""
        } ${selectedFile ? "file-upload__dropzone--has-file" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !selectedFile && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="file-upload__input"
          accept={accept}
          onChange={handleChange}
          id="file-upload-input"
          disabled={isUploading}
        />

        {!selectedFile ? (
          <>
            <div className="file-upload__icon">
              {accept.includes("video") ? "🎥" : "📄"}
            </div>
            <p className="file-upload__label">{label}</p>
            <p className="file-upload__hint">
              Drag & drop lecture video (.mp4, .mkv) or notes (.pdf) — or click to browse
            </p>
          </>
        ) : (
          <div className="file-upload__preview-box">
            <div className="file-upload__preview-icon">{isVideo ? "🎬" : "📄"}</div>
            <div className="file-upload__preview-details">
              <span className="file-upload__filename">{selectedFile.name}</span>
              <div className="file-upload__meta">
                <span>{formatFileSize(selectedFile.size)}</span>
                <span className="file-upload__tag">
                  {selectedModule.toUpperCase()} Module
                </span>
              </div>
            </div>
            {!isUploading && (
              <button
                type="button"
                className="file-upload__remove-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                title="Remove file"
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {isUploading && (
        <div className="file-upload__progress-container">
          <div className="file-upload__progress-header">
            <span>Uploading & Queueing into Pipeline...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="file-upload__progress-bar">
            <div
              className="file-upload__progress-fill"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Action Button */}
      {selectedFile && !isUploading && (
        <button
          type="button"
          className="file-upload__submit-btn"
          onClick={handleSubmit}
          id="upload-submit-btn"
        >
          🚀 Start VideoRAG Ingestion
        </button>
      )}
    </div>
  );
}

export default FileUpload;
