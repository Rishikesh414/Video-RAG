import React, { useRef, useState, useEffect } from "react";
import { formatTimestamp } from "../../utils/helpers";
import "./VideoPlayer.css";

/**
 * Enhanced VideoPlayer component — full custom lecture player
 * with timestamp seeking, speed control, and timeline markers.
 *
 * @param {Object} props
 * @param {string} props.src - Video source URL
 * @param {number} [props.startTime=0] - Start timestamp in seconds
 * @param {number} [props.endTime] - Optional segment end timestamp
 * @param {string} [props.title] - Title / lecture name
 * @param {Array}  [props.markers] - [{ time: number, label: string }]
 * @param {Function} [props.onTimeUpdate] - Time update callback
 */
function VideoPlayer({
  src,
  startTime = 0,
  endTime,
  title = "",
  markers = [],
  onTimeUpdate,
}) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Jump to startTime when changed
  useEffect(() => {
    if (videoRef.current && startTime >= 0) {
      videoRef.current.currentTime = startTime;
    }
  }, [startTime]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const cur = videoRef.current.currentTime;
    setCurrentTime(cur);
    onTimeUpdate?.(cur);

    // Auto-loop or pause at endTime if specified
    if (endTime && cur >= endTime) {
      videoRef.current.currentTime = startTime;
    }
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration || 0);
    if (startTime > 0) {
      videoRef.current.currentTime = startTime;
    }
  };

  const handleSeek = (e) => {
    const target = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = target;
      setCurrentTime(target);
    }
  };

  const changeSpeed = (rate) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setPlaybackRate(rate);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (videoRef.current) {
      videoRef.current.volume = val;
      videoRef.current.muted = val === 0;
      setIsMuted(val === 0);
    }
  };

  const jumpTo = (seconds) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const toggleFullscreen = () => {
    const el = videoRef.current?.parentElement;
    if (!el) return;
    if (!document.fullscreenElement) {
      el.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  if (!src) {
    return (
      <div className="video-player video-player--empty" id="video-player">
        <span className="video-player__empty-icon">🎬</span>
        <p>Select a lecture or ask a question to play video evidence</p>
      </div>
    );
  }

  return (
    <div className="video-player" id="video-player">
      {title && (
        <div className="video-player__header">
          <h3 className="video-player__title">{title}</h3>
          {startTime > 0 && (
            <span className="video-player__badge">
              Timestamp: {formatTimestamp(startTime)} {endTime ? `– ${formatTimestamp(endTime)}` : ""}
            </span>
          )}
        </div>
      )}

      <div className="video-player__media-container">
        <video
          ref={videoRef}
          className="video-player__video"
          src={src}
          onClick={togglePlay}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          playsInline
        />

        {/* Custom Overlay Controls */}
        <div className="video-player__controls">
          {/* Scrubber */}
          <div className="video-player__scrubber-wrapper">
            <input
              type="range"
              min="0"
              max={duration || 100}
              step="0.1"
              value={currentTime}
              onChange={handleSeek}
              className="video-player__scrubber"
            />
            {/* Timeline markers */}
            {markers.map((m, idx) => (
              <div
                key={idx}
                className="video-player__marker"
                style={{ left: `${(m.time / (duration || 1)) * 100}%` }}
                title={`${m.label} (${formatTimestamp(m.time)})`}
                onClick={() => jumpTo(m.time)}
              />
            ))}
          </div>

          <div className="video-player__control-bar">
            <div className="video-player__left-controls">
              <button
                type="button"
                className="video-player__btn"
                onClick={togglePlay}
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? "⏸" : "▶"}
              </button>

              <button
                type="button"
                className="video-player__btn"
                onClick={() => jumpTo(Math.max(0, currentTime - 10))}
                title="Rewind 10s"
              >
                ⏪ 10s
              </button>

              <button
                type="button"
                className="video-player__btn"
                onClick={() => jumpTo(Math.min(duration, currentTime + 10))}
                title="Forward 10s"
              >
                ⏩ 10s
              </button>

              {/* Time display */}
              <span className="video-player__time">
                {formatTimestamp(currentTime)} / {formatTimestamp(duration)}
              </span>
            </div>

            <div className="video-player__right-controls">
              {/* Volume */}
              <div className="video-player__volume-group">
                <button
                  type="button"
                  className="video-player__btn"
                  onClick={toggleMute}
                  title={isMuted ? "Unmute" : "Mute"}
                >
                  {isMuted || volume === 0 ? "🔇" : volume < 0.5 ? "🔉" : "🔊"}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="video-player__volume-slider"
                />
              </div>

              {/* Speed Pills */}
              <div className="video-player__speeds">
                {[1, 1.25, 1.5, 2].map((rate) => (
                  <button
                    key={rate}
                    type="button"
                    className={`video-player__speed-btn ${
                      playbackRate === rate ? "video-player__speed-btn--active" : ""
                    }`}
                    onClick={() => changeSpeed(rate)}
                  >
                    {rate}x
                  </button>
                ))}
              </div>

              {/* Fullscreen */}
              <button
                type="button"
                className="video-player__btn"
                onClick={toggleFullscreen}
                title="Toggle Fullscreen"
              >
                {isFullscreen ? "⤓" : "⤢"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Marker Jump Buttons */}
      {markers.length > 0 && (
        <div className="video-player__key-moments">
          <span className="video-player__moments-title">Key Video Moments:</span>
          <div className="video-player__moments-list">
            {markers.map((m, i) => (
              <button
                key={i}
                type="button"
                className="video-player__moment-chip"
                onClick={() => jumpTo(m.time)}
              >
                ⏱ {formatTimestamp(m.time)} — {m.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoPlayer;
