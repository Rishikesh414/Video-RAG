"""
Visual Tagger — lightweight computer vision object detection for video frames.

Part of Step 1 (Indexing). Samples frames at a low rate and runs a fast
object detector (YOLOv8-nano) to produce time-stamped text tags like:

    [00:12] car, person, road
    [03:45] person, package, door

These tags are stored as text metadata (kilobytes) instead of raw frames
(gigabytes), enabling cheap semantic retrieval in Step 2.
"""

import json
from pathlib import Path
from typing import List, Dict

import cv2


class VisualTagger:
    """
    Lightweight visual tagger using YOLOv8-nano for fast object detection.
    Produces timestamped text tags from sampled video frames.
    """

    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        Initialize the visual tagger.

        Args:
            model_name: YOLO model identifier. Use 'yolov8n.pt' (nano)
                        for maximum speed or 'yolov8s.pt' (small) for
                        slightly better accuracy.
        """
        self.model_name = model_name
        self.model = None  # Lazy-loaded

    def _load_model(self):
        """Load the YOLO model on first use."""
        from ultralytics import YOLO
        self.model = YOLO(self.model_name)

    def tag_video(
        self,
        video_path: str,
        sample_interval_sec: float = 2.0,
        confidence_threshold: float = 0.35,
    ) -> List[Dict]:
        """
        Sample frames from a video and detect objects in each frame.

        Args:
            video_path: Path to the video file.
            sample_interval_sec: Seconds between sampled frames (default 2s).
            confidence_threshold: Min confidence to include a detection.

        Returns:
            List of dicts, each with:
            - 'timestamp': float (seconds)
            - 'objects': list of detected object labels
            - 'details': list of {label, confidence, bbox}
        """
        if self.model is None:
            self._load_model()

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * sample_interval_sec) if fps > 0 else 60

        tags: List[Dict] = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps if fps > 0 else 0

                # Run YOLO detection
                results = self.model(frame, verbose=False)

                objects = []
                details = []
                for result in results:
                    for box in result.boxes:
                        conf = float(box.conf[0])
                        if conf >= confidence_threshold:
                            label = result.names[int(box.cls[0])]
                            objects.append(label)
                            details.append({
                                "label": label,
                                "confidence": round(conf, 3),
                                "bbox": box.xyxy[0].tolist(),
                            })

                # Deduplicate object labels while preserving order
                seen = set()
                unique_objects = []
                for obj in objects:
                    if obj not in seen:
                        seen.add(obj)
                        unique_objects.append(obj)

                tags.append({
                    "timestamp": round(timestamp, 2),
                    "objects": unique_objects,
                    "details": details,
                })

            frame_count += 1

        cap.release()
        return tags

    def save_tags(self, tags: List[Dict], output_path: str) -> str:
        """
        Save visual tags to a JSON file.

        Args:
            tags: Output from tag_video().
            output_path: Path to save the JSON file.

        Returns:
            The output file path.
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            json.dump(tags, f, indent=2)

        return str(output)

    def tags_to_text(self, tags: List[Dict]) -> str:
        """
        Convert visual tags to a human-readable text format for embedding.

        Example output:
            [00:12] car, person, road
            [03:45] person, package, door

        Args:
            tags: Output from tag_video().

        Returns:
            Formatted text string.
        """
        lines = []
        for tag in tags:
            ts = tag["timestamp"]
            minutes = int(ts // 60)
            seconds = int(ts % 60)
            objects_str = ", ".join(tag["objects"]) if tag["objects"] else "no objects detected"
            lines.append(f"[{minutes:02d}:{seconds:02d}] {objects_str}")
        return "\n".join(lines)
