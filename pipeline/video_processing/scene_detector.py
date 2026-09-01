"""
Scene Detector — splits videos into meaningful scenes using PySceneDetect.

Identifies scene boundaries (cuts, fades) to segment long videos
into coherent clips for more accurate retrieval.
"""

from typing import List, Tuple

from scenedetect import detect, ContentDetector, AdaptiveDetector


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
