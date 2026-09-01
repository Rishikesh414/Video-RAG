import React, { useState, useRef } from "react";
import { formatFileSize } from "../../utils/helpers";
import "./FileUpload.css";

/**
 * FileUpload component — drag-and-drop and click-to-browse file upload.
 *
 * @param {Object} props
 * @param {Function} props.onUpload - Callback with selected File object
 * @param {string} props.accept - Accepted file types (e.g., "video/*,.pdf")
 * @param {string} props.label - Upload area label text
 */
function FileUpload({ onUpload, accept = "video/*,.pdf", label = "Upload a file" }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
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
    onUpload?.(file);
  };

  return (
    <div className="file-upload" id="file-upload">
      <div
        className={`file-upload__dropzone ${dragActive ? "file-upload__dropzone--active" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="file-upload__input"
          accept={accept}
          onChange={handleChange}
          id="file-upload-input"
        />
        <div className="file-upload__icon">📁</div>
        <p className="file-upload__label">{label}</p>
        <p className="file-upload__hint">Drag & drop or click to browse</p>
      </div>

      {selectedFile && (
        <div className="file-upload__preview">
          <span className="file-upload__filename">{selectedFile.name}</span>
          <span className="file-upload__size">{formatFileSize(selectedFile.size)}</span>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
