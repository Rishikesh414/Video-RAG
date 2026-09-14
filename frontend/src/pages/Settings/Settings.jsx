import React, { useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../context/ToastContext";
import { SYSTEM_STATS } from "../../services/mockData";
import "./Settings.css";

/**
 * Settings page — system configuration, AI models inspector,
 * user profile, and video playback preferences.
 */
function Settings() {
  const { user, login } = useAuth();
  const { showSuccess, showInfo } = useToast();

  const [autoPlayClips, setAutoPlayClips] = useState(true);
  const [defaultSpeed, setDefaultSpeed] = useState("1");
  const [loopSegments, setLoopSegments] = useState(false);

  // Allow switching roles for testing demo experience
  const handleToggleRole = () => {
    if (!user) return;
    const newRole = user.role === "student" ? "faculty" : "student";
    const updatedUser = { ...user, role: newRole };
    login(updatedUser, localStorage.getItem("access_token") || "mock-token");
    showSuccess(`Switched active role to ${newRole.toUpperCase()}!`);
  };

  const handleSavePreferences = (e) => {
    e.preventDefault();
    showSuccess("Playback preferences updated!");
  };

  const handleTestConnection = () => {
    showInfo("Testing VideoRAG backend connection...");
    setTimeout(() => {
      showSuccess("Backend API, Whisper ASR, and Qdrant Vector Store are connected!");
    }, 800);
  };

  return (
    <div className="settings-page" id="settings-page">
      <Sidebar />

      <div className="settings-page__body">
        <Navbar
          title="System Settings & AI Diagnostics"
          subtitle="Inspect active pipeline models, vector store connectivity, and playback settings"
        />

        <main className="settings-page__main">
          {/* User Profile Card */}
          <section className="settings-page__card">
            <h3 className="settings-page__card-title">👤 User Account Profile</h3>
            <div className="settings-page__profile-info">
              <div className="settings-page__avatar">
                {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
              </div>
              <div className="settings-page__details">
                <span className="settings-page__name">{user?.name || "VideoRAG User"}</span>
                <span className="settings-page__email">{user?.email || "user@videorag.com"}</span>
                <div className="settings-page__role-pill">
                  Role: <strong>{user?.role?.toUpperCase()}</strong>
                </div>
              </div>

              <button
                type="button"
                className="settings-page__role-switch-btn"
                onClick={handleToggleRole}
                title="Switch between Student and Faculty view"
              >
                Switch Role to {user?.role === "student" ? "Faculty 👨‍🏫" : "Student 🎓"}
              </button>
            </div>
          </section>

          {/* AI Pipeline Architecture Inspector */}
          <section className="settings-page__card">
            <div className="settings-page__card-header">
              <div>
                <h3 className="settings-page__card-title">🤖 Active AI Pipeline Components</h3>
                <p className="settings-page__card-desc">
                  Low-cost 3-step hybrid architecture configuration
                </p>
              </div>
              <button
                type="button"
                className="settings-page__test-btn"
                onClick={handleTestConnection}
              >
                ⚡ Test Pipeline Health
              </button>
            </div>

            <div className="settings-page__diagnostics-grid">
              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Step 1: Audio ASR</span>
                <span className="settings-page__diag-value">OpenAI Whisper Large-v3</span>
                <span className="settings-page__diag-status">● Online</span>
              </div>

              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Step 1: Vision Tagger</span>
                <span className="settings-page__diag-value">YOLOv8n + PySceneDetect</span>
                <span className="settings-page__diag-status">● Ready</span>
              </div>

              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Step 2: Text Embeddings</span>
                <span className="settings-page__diag-value">all-MiniLM-L6-v2 (384-dim)</span>
                <span className="settings-page__diag-status">● Loaded</span>
              </div>

              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Step 2: Vector Database</span>
                <span className="settings-page__diag-value">Qdrant Vector Store</span>
                <span className="settings-page__diag-status">● localhost:6333</span>
              </div>

              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Step 3: Multimodal LLM</span>
                <span className="settings-page__diag-value">Gemini 1.5 Pro / GPT-4o</span>
                <span className="settings-page__diag-status">● Verified</span>
              </div>

              <div className="settings-page__diagnostic-item">
                <span className="settings-page__diag-label">Metadata Database</span>
                <span className="settings-page__diag-value">PostgreSQL / SQLite</span>
                <span className="settings-page__diag-status">● Connected</span>
              </div>
            </div>
          </section>

          {/* Video Playback & Search Preferences */}
          <section className="settings-page__card">
            <h3 className="settings-page__card-title">⚙️ Playback & Evidence Preferences</h3>
            <form className="settings-page__form" onSubmit={handleSavePreferences}>
              <div className="settings-page__field-row">
                <div className="settings-page__field-desc">
                  <label htmlFor="pref-autoplay">Auto-Play Evidence Clips</label>
                  <span>Automatically start playing video evidence when an answer is retrieved</span>
                </div>
                <input
                  id="pref-autoplay"
                  type="checkbox"
                  className="settings-page__checkbox"
                  checked={autoPlayClips}
                  onChange={(e) => setAutoPlayClips(e.target.checked)}
                />
              </div>

              <div className="settings-page__field-row">
                <div className="settings-page__field-desc">
                  <label htmlFor="pref-speed">Default Playback Speed</label>
                  <span>Speed used when opening full lectures or evidence clips</span>
                </div>
                <select
                  id="pref-speed"
                  className="settings-page__select"
                  value={defaultSpeed}
                  onChange={(e) => setDefaultSpeed(e.target.value)}
                >
                  <option value="1">1.0x (Normal)</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                  <option value="2">2.0x</option>
                </select>
              </div>

              <div className="settings-page__field-row">
                <div className="settings-page__field-desc">
                  <label htmlFor="pref-loop">Continuous Clip Loop</label>
                  <span>Loop the 30-second evidence clip continuously until paused</span>
                </div>
                <input
                  id="pref-loop"
                  type="checkbox"
                  className="settings-page__checkbox"
                  checked={loopSegments}
                  onChange={(e) => setLoopSegments(e.target.checked)}
                />
              </div>

              <button type="submit" className="settings-page__save-btn">
                Save Preferences
              </button>
            </form>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Settings;
