import React, { useState, useEffect } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";
import FileUpload from "../../components/FileUpload/FileUpload";
import { uploadAPI } from "../../services/api";
import { SYSTEM_STATS } from "../../services/mockData";
import { formatFileSize } from "../../utils/helpers";
import { useToast } from "../../context/ToastContext";
import "./FacultyDashboard.css";

/**
 * Enhanced FacultyDashboard page — admin control panel for faculty members.
 * Uploads lectures/PDFs, visualizes the 5-step VideoRAG pipeline,
 * and manages indexed course content.
 */
function FacultyDashboard() {
  const [uploads, setUploads] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [activePipelineStep, setActivePipelineStep] = useState(null);
  const [activeTab, setActiveTab] = useState("all"); // "all", "video", "pdf"
  const [searchQuery, setSearchQuery] = useState("");

  const { showSuccess, showError, showInfo } = useToast();

  const fetchUploads = async () => {
    try {
      const response = await uploadAPI.listUploads();
      setUploads(response.data?.uploads || []);
    } catch {
      // Handled inside uploadAPI fallback
    }
  };

  useEffect(() => {
    fetchUploads();
  }, []);

  const simulatePipeline = async (callback) => {
    setIsUploading(true);

    // Step 1: Audio extraction
    setActivePipelineStep(1);
    await new Promise((r) => setTimeout(r, 600));

    // Step 2: Whisper ASR
    setActivePipelineStep(2);
    await new Promise((r) => setTimeout(r, 800));

    // Step 3: YOLO & Scene Frames
    setActivePipelineStep(3);
    await new Promise((r) => setTimeout(r, 700));

    // Step 4: Text Embeddings
    setActivePipelineStep(4);
    await new Promise((r) => setTimeout(r, 600));

    // Step 5: Qdrant Indexing
    setActivePipelineStep(5);
    await new Promise((r) => setTimeout(r, 500));

    await callback();

    setActivePipelineStep(null);
    setIsUploading(false);
  };

  const handleVideoUpload = async (file, module) => {
    simulatePipeline(async () => {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("module", module);
        await uploadAPI.uploadVideo(formData);
        showSuccess(`Video "${file.name}" uploaded and indexed into [${module.toUpperCase()}]!`);
        fetchUploads();
      } catch (err) {
        showError("Failed to upload video.");
      }
    });
  };

  const handlePDFUpload = async (file, module) => {
    simulatePipeline(async () => {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("module", module);
        await uploadAPI.uploadPDF(formData);
        showSuccess(`PDF "${file.name}" uploaded and indexed into [${module.toUpperCase()}]!`);
        fetchUploads();
      } catch (err) {
        showError("Failed to upload PDF.");
      }
    });
  };

  const handleDeleteUpload = (id) => {
    setUploads((prev) => prev.filter((u) => u.id !== id));
    showInfo("Content removed from local view.");
  };

  const filteredUploads = uploads.filter((u) => {
    if (activeTab !== "all" && u.file_type !== activeTab) return false;
    if (searchQuery.trim() && !u.filename.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="faculty-dashboard" id="faculty-dashboard">
      <Sidebar />

      <div className="faculty-dashboard__body">
        <Navbar
          title="Faculty Ingestion & Pipeline Admin"
          subtitle="Upload course materials, monitor the 5-step indexing pipeline, and manage vector indices"
        />

        <main className="faculty-dashboard__main">
          {/* Top Metric Cards */}
          <div className="faculty-dashboard__stats-grid">
            <div className="faculty-dashboard__stat-card">
              <div className="faculty-dashboard__stat-icon">🎬</div>
              <div className="faculty-dashboard__stat-info">
                <span className="faculty-dashboard__stat-value">{SYSTEM_STATS.totalVideos}</span>
                <span className="faculty-dashboard__stat-label">Indexed Lectures</span>
              </div>
            </div>

            <div className="faculty-dashboard__stat-card">
              <div className="faculty-dashboard__stat-icon">⏱</div>
              <div className="faculty-dashboard__stat-info">
                <span className="faculty-dashboard__stat-value">{SYSTEM_STATS.totalHours}</span>
                <span className="faculty-dashboard__stat-label">Video Content</span>
              </div>
            </div>

            <div className="faculty-dashboard__stat-card">
              <div className="faculty-dashboard__stat-icon">🧠</div>
              <div className="faculty-dashboard__stat-info">
                <span className="faculty-dashboard__stat-value">{SYSTEM_STATS.indexedChunks}</span>
                <span className="faculty-dashboard__stat-label">Vector Chunks (Qdrant)</span>
              </div>
            </div>

            <div className="faculty-dashboard__stat-card">
              <div className="faculty-dashboard__stat-icon">💬</div>
              <div className="faculty-dashboard__stat-info">
                <span className="faculty-dashboard__stat-value">{SYSTEM_STATS.questionsAnswered}</span>
                <span className="faculty-dashboard__stat-label">Student Q&A Answered</span>
              </div>
            </div>
          </div>

          {/* Pipeline Live Visualizer */}
          <section className="faculty-dashboard__pipeline-card">
            <div className="faculty-dashboard__pipeline-header">
              <div>
                <h3>⚡ 5-Step Low-Cost Ingestion Pipeline</h3>
                <p>
                  Converts raw lectures into searchable vector metadata — saving 10x multimodal API tokens.
                </p>
              </div>
              {isUploading && (
                <span className="faculty-dashboard__pipeline-active-badge">
                  ● Processing Ingestion
                </span>
              )}
            </div>

            <div className="faculty-dashboard__steps">
              <div
                className={`faculty-dashboard__step ${
                  activePipelineStep === 1
                    ? "faculty-dashboard__step--active"
                    : activePipelineStep > 1
                    ? "faculty-dashboard__step--done"
                    : ""
                }`}
              >
                <span className="faculty-dashboard__step-num">1</span>
                <div className="faculty-dashboard__step-details">
                  <span className="faculty-dashboard__step-name">Audio Extraction</span>
                  <span className="faculty-dashboard__step-tool">FFmpeg (16kHz WAV)</span>
                </div>
              </div>

              <div className="faculty-dashboard__step-arrow">→</div>

              <div
                className={`faculty-dashboard__step ${
                  activePipelineStep === 2
                    ? "faculty-dashboard__step--active"
                    : activePipelineStep > 2
                    ? "faculty-dashboard__step--done"
                    : ""
                }`}
              >
                <span className="faculty-dashboard__step-num">2</span>
                <div className="faculty-dashboard__step-details">
                  <span className="faculty-dashboard__step-name">Speech-to-Text</span>
                  <span className="faculty-dashboard__step-tool">Whisper Large-v3</span>
                </div>
              </div>

              <div className="faculty-dashboard__step-arrow">→</div>

              <div
                className={`faculty-dashboard__step ${
                  activePipelineStep === 3
                    ? "faculty-dashboard__step--active"
                    : activePipelineStep > 3
                    ? "faculty-dashboard__step--done"
                    : ""
                }`}
              >
                <span className="faculty-dashboard__step-num">3</span>
                <div className="faculty-dashboard__step-details">
                  <span className="faculty-dashboard__step-name">Visual & Scene Tags</span>
                  <span className="faculty-dashboard__step-tool">YOLOv8 + PySceneDetect</span>
                </div>
              </div>

              <div className="faculty-dashboard__step-arrow">→</div>

              <div
                className={`faculty-dashboard__step ${
                  activePipelineStep === 4
                    ? "faculty-dashboard__step--active"
                    : activePipelineStep > 4
                    ? "faculty-dashboard__step--done"
                    : ""
                }`}
              >
                <span className="faculty-dashboard__step-num">4</span>
                <div className="faculty-dashboard__step-details">
                  <span className="faculty-dashboard__step-name">Chunk Embedding</span>
                  <span className="faculty-dashboard__step-tool">Sentence-Transformers</span>
                </div>
              </div>

              <div className="faculty-dashboard__step-arrow">→</div>

              <div
                className={`faculty-dashboard__step ${
                  activePipelineStep === 5
                    ? "faculty-dashboard__step--active"
                    : ""
                }`}
              >
                <span className="faculty-dashboard__step-num">5</span>
                <div className="faculty-dashboard__step-details">
                  <span className="faculty-dashboard__step-name">Vector Indexing</span>
                  <span className="faculty-dashboard__step-tool">Qdrant Collection</span>
                </div>
              </div>
            </div>
          </section>

          {/* Upload Cards Grid */}
          <div className="faculty-dashboard__uploads-grid">
            {/* Video Upload Card */}
            <div className="faculty-dashboard__upload-card">
              <div className="faculty-dashboard__card-header">
                <h3>📹 Upload Lecture Recording</h3>
                <p>Supports MP4, MKV, AVI. Whisper subtitles & YOLO tags generated automatically.</p>
              </div>
              <FileUpload
                onUpload={handleVideoUpload}
                accept="video/*"
                label="Select Lecture Video"
                isUploading={isUploading}
              />
            </div>

            {/* PDF Notes Upload Card */}
            <div className="faculty-dashboard__upload-card">
              <div className="faculty-dashboard__card-header">
                <h3>📄 Upload PDF Course Notes</h3>
                <p>Upload slides, problem sets, and textbook chapters to supplement the knowledge base.</p>
              </div>
              <FileUpload
                onUpload={handlePDFUpload}
                accept=".pdf"
                label="Select Course Notes PDF"
                isUploading={isUploading}
              />
            </div>
          </div>

          {/* Indexed Content Table */}
          <section className="faculty-dashboard__table-card">
            <div className="faculty-dashboard__table-header">
              <div>
                <h3>📚 Indexed Course Catalog</h3>
                <p>Manage uploaded files and their pipeline indexing statuses</p>
              </div>

              <div className="faculty-dashboard__table-actions">
                {/* Search */}
                <input
                  type="text"
                  placeholder="Filter files..."
                  className="faculty-dashboard__table-search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />

                {/* Tabs */}
                <div className="faculty-dashboard__tabs">
                  <button
                    type="button"
                    className={`faculty-dashboard__tab ${
                      activeTab === "all" ? "faculty-dashboard__tab--active" : ""
                    }`}
                    onClick={() => setActiveTab("all")}
                  >
                    All ({uploads.length})
                  </button>
                  <button
                    type="button"
                    className={`faculty-dashboard__tab ${
                      activeTab === "video" ? "faculty-dashboard__tab--active" : ""
                    }`}
                    onClick={() => setActiveTab("video")}
                  >
                    Videos
                  </button>
                  <button
                    type="button"
                    className={`faculty-dashboard__tab ${
                      activeTab === "pdf" ? "faculty-dashboard__tab--active" : ""
                    }`}
                    onClick={() => setActiveTab("pdf")}
                  >
                    PDFs
                  </button>
                </div>
              </div>
            </div>

            <div className="faculty-dashboard__table-responsive">
              <table className="faculty-dashboard__table">
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Module</th>
                    <th>Type</th>
                    <th>File Size</th>
                    <th>Uploaded</th>
                    <th>Pipeline Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUploads.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="faculty-dashboard__table-empty">
                        No uploaded course files found matching filter.
                      </td>
                    </tr>
                  ) : (
                    filteredUploads.map((item) => (
                      <tr key={item.id}>
                        <td className="faculty-dashboard__cell-filename">
                          <span className="faculty-dashboard__type-icon">
                            {item.file_type === "video" ? "🎬" : "📄"}
                          </span>
                          <span title={item.filename}>{item.filename}</span>
                        </td>
                        <td>
                          <span className="faculty-dashboard__module-badge">
                            {item.module || "M1"}
                          </span>
                        </td>
                        <td>
                          <span className="faculty-dashboard__type-badge">
                            {item.file_type?.toUpperCase()}
                          </span>
                        </td>
                        <td>{formatFileSize(item.file_size || 0)}</td>
                        <td>
                          {item.created_at
                            ? new Date(item.created_at).toLocaleDateString()
                            : "Recent"}
                        </td>
                        <td>
                          <span className="faculty-dashboard__status-badge faculty-dashboard__status-badge--completed">
                            ✓ Ready in Index
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            className="faculty-dashboard__action-btn"
                            onClick={() => handleDeleteUpload(item.id)}
                            title="Remove file"
                          >
                            🗑
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default FacultyDashboard;
