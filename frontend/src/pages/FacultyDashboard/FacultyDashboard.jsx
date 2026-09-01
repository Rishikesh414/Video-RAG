import React, { useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import FileUpload from "../../components/FileUpload/FileUpload";
import { uploadAPI } from "../../services/api";
import "./FacultyDashboard.css";

/**
 * FacultyDashboard page — the admin interface for faculty members.
 * Allows uploading lecture videos and PDF notes for processing
 * by the VideoRAG pipeline.
 */
function FacultyDashboard() {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleVideoUpload = async (file) => {
    setIsUploading(true);
    setUploadStatus(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await uploadAPI.uploadVideo(formData);
      setUploadStatus({ type: "success", message: `Video "${file.name}" uploaded successfully!` });
    } catch (error) {
      setUploadStatus({ type: "error", message: "Failed to upload video. Please try again." });
    } finally {
      setIsUploading(false);
    }
  };

  const handlePDFUpload = async (file) => {
    setIsUploading(true);
    setUploadStatus(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await uploadAPI.uploadPDF(formData);
      setUploadStatus({ type: "success", message: `PDF "${file.name}" uploaded successfully!` });
    } catch (error) {
      setUploadStatus({ type: "error", message: "Failed to upload PDF. Please try again." });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="faculty-dashboard" id="faculty-dashboard">
      <Sidebar />
      <main className="faculty-dashboard__main">
        <header className="faculty-dashboard__header">
          <h1>Faculty Dashboard</h1>
          <p>Upload lecture recordings and PDF notes for the VideoRAG system</p>
        </header>

        {uploadStatus && (
          <div className={`faculty-dashboard__status faculty-dashboard__status--${uploadStatus.type}`}>
            {uploadStatus.message}
          </div>
        )}

        <div className="faculty-dashboard__uploads">
          <section className="faculty-dashboard__section">
            <h2>Upload Lecture Video</h2>
            <p>Upload recorded lectures (M1–M4). Subtitles will be auto-generated via Whisper ASR.</p>
            <FileUpload
              onUpload={handleVideoUpload}
              accept="video/*"
              label="Upload Lecture Video"
            />
          </section>

          <section className="faculty-dashboard__section">
            <h2>Upload PDF Notes</h2>
            <p>Upload course notes or slides to supplement the video knowledge base.</p>
            <FileUpload
              onUpload={handlePDFUpload}
              accept=".pdf"
              label="Upload PDF Notes"
            />
          </section>
        </div>

        {isUploading && (
          <div className="faculty-dashboard__loading">
            <p>Processing upload...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default FacultyDashboard;
