import React, { useRef, useState } from "react";
import { formatTimestamp } from "../../utils/helpers";
import { useToast } from "../../context/ToastContext";
import "./ClipViewer.css";

/**
 * Enhanced ClipViewer — displays all 3 outputs of the hybrid VideoRAG pipeline:
 * 1. Multimodal Text Answer (with confidence badge & reasoning)
 * 2. Targeted Video Clip Player (download, seek, playback speed)
 * 3. Exact Lecture Timestamp & Source metadata
 *
 * @param {Object} props
 * @param {Object} props.answer     - { text, confidence, reasoning }
 * @param {Object} props.videoClip  - { clip_id, clip_url, clip_filename, duration }
 * @param {Object} props.timestamp  - { start_time, end_time, formatted_start, formatted_end, source_video, video_id }
 * @param {Array}  props.sources    - List of source video IDs or PDF citations
 */
function ClipViewer({ answer, videoClip, timestamp, sources = [] }) {
  const videoRef = useRef(null);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isCopied, setIsCopied] = useState(false);
  const { showSuccess } = useToast();

  const handleCopyAnswer = () => {
    if (!answer?.text) return;
    navigator.clipboard.writeText(answer.text);
    setIsCopied(true);
    showSuccess("Answer copied to clipboard!");
    setTimeout(() => setIsCopied(false), 2000);
  };

  const setSpeed = (speed) => {
    setPlaybackSpeed(speed);
    if (videoRef.current) {
      videoRef.current.playbackRate = speed;
    }
  };

  if (!answer && !videoClip) {
    return (
      <div className="clip-viewer clip-viewer--empty" id="clip-viewer">
        <div className="clip-viewer__placeholder">
          <div className="clip-viewer__placeholder-icon">🎬</div>
          <h3>Evidence & Reasoning Panel</h3>
          <p className="clip-viewer__placeholder-desc">
            Ask any question about your lecture videos to see the 3-part hybrid pipeline output:
          </p>
          <div className="clip-viewer__pipeline-preview">
            <div className="clip-viewer__preview-step">
              <span className="clip-viewer__step-num">1</span>
              <span>📝 Grounded Text Answer</span>
            </div>
            <div className="clip-viewer__preview-step">
              <span className="clip-viewer__step-num">2</span>
              <span>🎥 30-Sec Video Evidence Clip</span>
            </div>
            <div className="clip-viewer__preview-step">
              <span className="clip-viewer__step-num">3</span>
              <span>⏱ Source Timestamp Navigation</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const confidenceClass =
    answer?.confidence === "high"
      ? "clip-viewer__badge--high"
      : answer?.confidence === "medium"
      ? "clip-viewer__badge--medium"
      : "clip-viewer__badge--low";

  return (
    <div className="clip-viewer" id="clip-viewer">
      {/* ── Output 1: Grounded Text Answer ─────────────────────── */}
      {answer && (
        <section className="clip-viewer__answer">
          <div className="clip-viewer__answer-header">
            <div className="clip-viewer__title-group">
              <span className="clip-viewer__section-icon">📝</span>
              <h3>Answer</h3>
              {answer.confidence && (
                <span className={`clip-viewer__badge ${confidenceClass}`}>
                  ● {answer.confidence.toUpperCase()} CONFIDENCE
                </span>
              )}
            </div>

            <button
              type="button"
              className="clip-viewer__copy-btn"
              onClick={handleCopyAnswer}
              title="Copy answer to clipboard"
            >
              {isCopied ? "✓ Copied" : "📋 Copy"}
            </button>
          </div>

          <p className="clip-viewer__answer-text">{answer.text}</p>

          {answer.reasoning && (
            <details className="clip-viewer__reasoning" open>
              <summary>
                <span>🔍 Multimodal Evidence Reasoning</span>
              </summary>
              <div className="clip-viewer__reasoning-content">
                <p>{answer.reasoning}</p>
              </div>
            </details>
          )}
        </section>
      )}

      {/* ── Output 2: Video Evidence Clip ──────────────────────── */}
      {videoClip?.clip_url && (
        <section className="clip-viewer__video">
          <div className="clip-viewer__video-header">
            <div className="clip-viewer__title-group">
              <span className="clip-viewer__section-icon">🎥</span>
              <h3>Video Clip Evidence</h3>
              {videoClip.duration && (
                <span className="clip-viewer__duration">
                  {typeof videoClip.duration === "number"
                    ? `${videoClip.duration.toFixed(1)}s segment`
                    : videoClip.duration}
                </span>
              )}
            </div>

            <div className="clip-viewer__speed-pills">
              {[1, 1.25, 1.5].map((speed) => (
                <button
                  key={speed}
                  type="button"
                  className={`clip-viewer__speed-btn ${
                    playbackSpeed === speed ? "clip-viewer__speed-btn--active" : ""
                  }`}
                  onClick={() => setSpeed(speed)}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          <div className="clip-viewer__player-wrapper">
            <video
              ref={videoRef}
              className="clip-viewer__player"
              src={videoClip.clip_url}
              controls
              autoPlay
              muted
              playsInline
              id="clip-player"
            />
          </div>

          <div className="clip-viewer__video-footer">
            <span className="clip-viewer__clip-name">
              📁 {videoClip.clip_filename || `evidence_${videoClip.clip_id || "clip"}.mp4`}
            </span>
            <a
              className="clip-viewer__download"
              href={videoClip.clip_url}
              download={videoClip.clip_filename || "videorag_evidence_clip.mp4"}
              target="_blank"
              rel="noopener noreferrer"
              id="clip-download-btn"
            >
              ⬇ Download Clip
            </a>
          </div>
        </section>
      )}

      {/* ── Output 3: Source Timestamps ──────────────────────── */}
      {timestamp && (
        <section className="clip-viewer__timestamp">
          <div className="clip-viewer__title-group">
            <span className="clip-viewer__section-icon">⏱</span>
            <h3>Source Lecture Timestamps</h3>
          </div>

          <div className="clip-viewer__timestamp-grid">
            <div className="clip-viewer__timestamp-item">
              <span className="clip-viewer__timestamp-label">Start Time</span>
              <span className="clip-viewer__timestamp-value">
                {timestamp.formatted_start || formatTimestamp(timestamp.start_time || 0)}
              </span>
            </div>

            <div className="clip-viewer__timestamp-item">
              <span className="clip-viewer__timestamp-label">End Time</span>
              <span className="clip-viewer__timestamp-value">
                {timestamp.formatted_end || formatTimestamp(timestamp.end_time || 0)}
              </span>
            </div>

            {timestamp.video_id && (
              <div className="clip-viewer__timestamp-item clip-viewer__timestamp-item--wide">
                <span className="clip-viewer__timestamp-label">Indexed Lecture</span>
                <span className="clip-viewer__timestamp-value clip-viewer__timestamp-source">
                  {timestamp.video_id}
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ── Sources & Chunk Citations ───────────────────── */}
      {sources && sources.length > 0 && (
        <section className="clip-viewer__sources-section">
          <span className="clip-viewer__sources-title">📎 Retrieved Knowledge Citations:</span>
          <div className="clip-viewer__sources-tags">
            {sources.map((src, i) => (
              <span key={i} className="clip-viewer__source-tag">
                {src}
              </span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default ClipViewer;
