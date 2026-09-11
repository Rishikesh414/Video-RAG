import React from "react";
import "./ClipViewer.css";

/**
 * ClipViewer — displays all 3 outputs from the hybrid VideoRAG pipeline:
 *
 * 1. Text answer (with confidence badge)
 * 2. Embedded video clip player with download button
 * 3. Timestamp display with source video info
 *
 * @param {Object} props
 * @param {Object} props.answer     - { text, confidence, reasoning }
 * @param {Object} props.videoClip  - { clip_id, clip_url, clip_filename, duration }
 * @param {Object} props.timestamp  - { start_time, end_time, formatted_start, formatted_end, source_video, video_id }
 * @param {Array}  props.sources    - List of source video IDs
 */
function ClipViewer({ answer, videoClip, timestamp, sources = [] }) {
  if (!answer && !videoClip) {
    return (
      <div className="clip-viewer clip-viewer--empty" id="clip-viewer">
        <div className="clip-viewer__placeholder">
          <span className="clip-viewer__placeholder-icon">🎬</span>
          <p>Ask a question to see video evidence here</p>
        </div>
      </div>
    );
  }

  const confidenceClass = answer?.confidence === "high"
    ? "clip-viewer__badge--high"
    : answer?.confidence === "medium"
      ? "clip-viewer__badge--medium"
      : "clip-viewer__badge--low";

  return (
    <div className="clip-viewer" id="clip-viewer">
      {/* ── Output 1: Text Answer ─────────────────────── */}
      {answer && (
        <section className="clip-viewer__answer">
          <div className="clip-viewer__answer-header">
            <h3>📝 Answer</h3>
            {answer.confidence && (
              <span className={`clip-viewer__badge ${confidenceClass}`}>
                {answer.confidence} confidence
              </span>
            )}
          </div>
          <p className="clip-viewer__answer-text">{answer.text}</p>
          {answer.reasoning && (
            <details className="clip-viewer__reasoning">
              <summary>View reasoning</summary>
              <p>{answer.reasoning}</p>
            </details>
          )}
        </section>
      )}

      {/* ── Output 2: Video Clip ──────────────────────── */}
      {videoClip?.clip_url && (
        <section className="clip-viewer__video">
          <div className="clip-viewer__video-header">
            <h3>🎥 Evidence Clip</h3>
            <span className="clip-viewer__duration">
              {videoClip.duration ? `${videoClip.duration.toFixed(1)}s` : ""}
            </span>
          </div>
          <video
            className="clip-viewer__player"
            src={videoClip.clip_url}
            controls
            id="clip-player"
          />
          <a
            className="clip-viewer__download"
            href={videoClip.clip_url}
            download={videoClip.clip_filename || "clip.mp4"}
            id="clip-download-btn"
          >
            ⬇ Download Clip
          </a>
        </section>
      )}

      {/* ── Output 3: Timestamps ──────────────────────── */}
      {timestamp && (timestamp.start_time > 0 || timestamp.end_time > 0) && (
        <section className="clip-viewer__timestamp">
          <h3>⏱ Source Timestamp</h3>
          <div className="clip-viewer__timestamp-grid">
            <div className="clip-viewer__timestamp-item">
              <span className="clip-viewer__timestamp-label">Start</span>
              <span className="clip-viewer__timestamp-value">
                {timestamp.formatted_start || formatTime(timestamp.start_time)}
              </span>
            </div>
            <div className="clip-viewer__timestamp-item">
              <span className="clip-viewer__timestamp-label">End</span>
              <span className="clip-viewer__timestamp-value">
                {timestamp.formatted_end || formatTime(timestamp.end_time)}
              </span>
            </div>
            {timestamp.video_id && (
              <div className="clip-viewer__timestamp-item clip-viewer__timestamp-item--wide">
                <span className="clip-viewer__timestamp-label">Source</span>
                <span className="clip-viewer__timestamp-value clip-viewer__timestamp-source">
                  {timestamp.video_id}
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ── Sources ───────────────────────────────────── */}
      {sources.length > 0 && (
        <div className="clip-viewer__sources">
          📎 Sources: {sources.join(", ")}
        </div>
      )}
    </div>
  );
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default ClipViewer;
