import React, { useRef } from "react";
import "./VideoPlayer.css";

/**
 * VideoPlayer component — renders a video with optional timestamp seeking.
 *
 * @param {Object} props
 * @param {string} props.src - Video source URL
 * @param {number} props.startTime - Start time in seconds for the relevant segment
 * @param {string} props.title - Title/filename of the video
 */
function VideoPlayer({ src, startTime = 0, title = "" }) {
  const videoRef = useRef(null);

  const handleLoadedMetadata = () => {
    if (videoRef.current && startTime > 0) {
      videoRef.current.currentTime = startTime;
    }
  };

  if (!src) {
    return (
      <div className="video-player video-player--empty" id="video-player">
        <p>No video selected</p>
      </div>
    );
  }

  return (
    <div className="video-player" id="video-player">
      {title && <h3 className="video-player__title">{title}</h3>}
      <video
        ref={videoRef}
        className="video-player__video"
        src={src}
        controls
        onLoadedMetadata={handleLoadedMetadata}
      />
    </div>
  );
}

export default VideoPlayer;
