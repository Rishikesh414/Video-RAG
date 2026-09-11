"""
Video Utilities — common helpers shared across pipeline steps.
"""

import cv2
from pathlib import Path


def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file in seconds.

    Args:
        video_path: Path to the video file.

    Returns:
        Duration in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    if fps > 0:
        return frame_count / fps
    return 0.0


def get_video_info(video_path: str) -> dict:
    """
    Get basic info about a video file.

    Returns:
        Dict with fps, width, height, frame_count, duration.
    """
    cap = cv2.VideoCapture(video_path)
    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    info["duration"] = info["frame_count"] / info["fps"] if info["fps"] > 0 else 0
    cap.release()
    return info


def ensure_dir(path: str) -> Path:
    """Create a directory if it doesn't exist and return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
