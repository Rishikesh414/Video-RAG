"""
Frame Extractor — extracts frames from video files using OpenCV.

Supports configurable FPS-based extraction and saves frames to disk
for downstream processing by the embedding and OCR pipelines.
"""

from pathlib import Path
from typing import List

import cv2
import numpy as np


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: int = 1,
) -> List[str]:
    """
    Extract frames from a video file at the specified frames-per-second rate.

    Args:
        video_path: Path to the source video file.
        output_dir: Directory to save extracted frame images.
        fps: Number of frames to extract per second of video.

    Returns:
        List of file paths to the extracted frame images.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps) if video_fps > 0 else 30

    frame_paths: List[str] = []
    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_filename = output_path / f"frame_{saved_count:06d}.jpg"
            cv2.imwrite(str(frame_filename), frame)
            frame_paths.append(str(frame_filename))
            saved_count += 1

        frame_count += 1

    cap.release()
    return frame_paths


def get_frame_at_timestamp(video_path: str, timestamp_sec: float) -> np.ndarray:
    """
    Extract a single frame at a specific timestamp.

    Args:
        video_path: Path to the video file.
        timestamp_sec: Timestamp in seconds.

    Returns:
        The frame as a numpy array (BGR).
    """
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError(f"Could not extract frame at {timestamp_sec}s from {video_path}")

    return frame
