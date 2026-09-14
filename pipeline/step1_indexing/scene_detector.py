"""
Scene Detector — splits videos into meaningful scenes using PySceneDetect.

Part of Step 1 (Indexing). Identifies scene boundaries (cuts, fades) to
segment long videos into coherent sections. Scene boundaries are stored
as metadata to help Step 2 find natural clip boundaries.

Provides keyframe extraction utilities used by the OCR extractor and
Visual Describer to sample representative frames from each scene.
"""

import logging
from typing import List, Tuple, Optional

import cv2
import numpy as np
from scenedetect import detect, ContentDetector, AdaptiveDetector

logger = logging.getLogger(__name__)


def detect_scenes(
    video_path: str,
    threshold: float = 27.0,
    method: str = "content",
) -> List[Tuple[float, float]]:
    """
    Detect scene boundaries in a video file.

    Args:
        video_path: Path to the video file.
        threshold: Sensitivity threshold for scene detection.
        method: Detection method — "content" or "adaptive".

    Returns:
        List of (start_time, end_time) tuples in seconds for each scene.
    """
    if method == "adaptive":
        detector = AdaptiveDetector()
    else:
        detector = ContentDetector(threshold=threshold)

    scene_list = detect(video_path, detector)

    scenes: List[Tuple[float, float]] = []
    for scene in scene_list:
        start_time = scene[0].get_seconds()
        end_time = scene[1].get_seconds()
        scenes.append((start_time, end_time))

    return scenes


def extract_scene_keyframe(
    video_path: str,
    scene_start: float,
    scene_end: float,
    position: str = "mid",
) -> Optional[np.ndarray]:
    """
    Extract a representative keyframe from a scene.

    Shared utility used by OCRExtractor and VisualDescriber to sample
    the best frame from a scene boundary for analysis.

    Args:
        video_path: Path to the video file.
        scene_start: Scene start time in seconds.
        scene_end: Scene end time in seconds.
        position: Where to sample — "mid" (midpoint), "start" (+1s), "end" (-1s).

    Returns:
        NumPy BGR image array, or None if frame could not be read.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        cap.release()
        return None

    if position == "mid":
        target_time = (scene_start + scene_end) / 2.0
    elif position == "start":
        target_time = scene_start + min(1.0, (scene_end - scene_start) * 0.1)
    elif position == "end":
        target_time = scene_end - min(1.0, (scene_end - scene_start) * 0.1)
    else:
        target_time = (scene_start + scene_end) / 2.0

    frame_idx = int(target_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()

    if not ret:
        # Fallback: try start + 0.5s
        fallback_idx = int(scene_start * fps) + int(fps * 0.5)
        cap.set(cv2.CAP_PROP_POS_FRAMES, fallback_idx)
        ret, frame = cap.read()

    cap.release()

    if ret:
        return frame
    else:
        logger.debug(
            f"Could not extract keyframe for scene "
            f"{scene_start:.1f}s-{scene_end:.1f}s from {video_path}"
        )
        return None


def get_all_scene_keyframes(
    video_path: str,
    scenes: List[Tuple[float, float]],
    position: str = "mid",
) -> List[dict]:
    """
    Extract keyframes for all scenes in a single pass through the video.

    More efficient than calling extract_scene_keyframe() per scene
    as it keeps the VideoCapture open across all scenes.

    Args:
        video_path: Path to the video file.
        scenes: List of (start_time, end_time) tuples.
        position: Keyframe position ("mid", "start", "end").

    Returns:
        List of dicts with 'scene_start', 'scene_end', 'timestamp', 'frame'.
        'frame' is a NumPy array or None if extraction failed.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    keyframes = []

    if fps <= 0:
        cap.release()
        return keyframes

    for scene_start, scene_end in scenes:
        if position == "mid":
            target_time = (scene_start + scene_end) / 2.0
        elif position == "start":
            target_time = scene_start + min(1.0, (scene_end - scene_start) * 0.1)
        else:
            target_time = scene_end - min(1.0, (scene_end - scene_start) * 0.1)

        frame_idx = int(target_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if not ret:
            fallback_idx = int(scene_start * fps) + int(fps * 0.5)
            cap.set(cv2.CAP_PROP_POS_FRAMES, fallback_idx)
            ret, frame = cap.read()

        keyframes.append({
            "scene_start": round(scene_start, 2),
            "scene_end": round(scene_end, 2),
            "timestamp": round(target_time, 2),
            "frame": frame if ret else None,
        })

    cap.release()
    return keyframes


def get_scene_for_timestamp(
    scenes: List[Tuple[float, float]],
    timestamp: float,
) -> Tuple[float, float]:
    """
    Find which scene a given timestamp belongs to.

    Args:
        scenes: List of (start, end) scene boundaries.
        timestamp: The timestamp to look up.

    Returns:
        The (start, end) tuple of the matching scene.

    Raises:
        ValueError: If the timestamp doesn't fall within any scene.
    """
    for start, end in scenes:
        if start <= timestamp <= end:
            return (start, end)
    raise ValueError(f"Timestamp {timestamp}s not found in any scene")
