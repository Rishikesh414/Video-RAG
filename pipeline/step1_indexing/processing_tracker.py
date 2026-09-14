"""
Processing Tracker — lightweight JSON-based status tracker for video pipeline stages.

Part of Step 1 (Indexing). Writes status JSON files so the backend API
can report real-time processing progress to the frontend.

Pipeline stages (in order):
    queued → audio_extraction → transcription → scene_detection
    → ocr → visual_description → indexing → done

On error, status is set to 'failed' with an error message.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Ordered pipeline stages for progress calculation
PIPELINE_STAGES = [
    "queued",
    "audio_extraction",
    "transcription",
    "scene_detection",
    "ocr",
    "visual_description",
    "yolo_tagging",
    "indexing",
    "done",
]


class ProcessingTracker:
    """
    Tracks video processing pipeline stage and writes status to disk.

    Status files are stored at: {status_dir}/{video_id}_status.json
    The backend API reads these files to report progress to the frontend.
    """

    def __init__(self, status_dir: str = "./data/processing"):
        """
        Args:
            status_dir: Directory to store status JSON files.
        """
        self.status_dir = Path(status_dir)
        self.status_dir.mkdir(parents=True, exist_ok=True)

    def _status_path(self, video_id: str) -> Path:
        return self.status_dir / f"{video_id}_status.json"

    def initialize(self, video_id: str, filename: str = "") -> None:
        """Create initial 'queued' status for a new video."""
        self._write(video_id, {
            "video_id": video_id,
            "filename": filename,
            "stage": "queued",
            "progress_pct": 0,
            "message": "Video queued for processing",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
            "stats": {},
        })

    def update(
        self,
        video_id: str,
        stage: str,
        message: str = "",
        stats: dict = None,
    ) -> None:
        """
        Update the processing stage for a video.

        Args:
            video_id: The video's unique ID.
            stage: Current pipeline stage (must be in PIPELINE_STAGES).
            message: Human-readable status message.
            stats: Optional dict of stats (e.g., {'segments': 42}).
        """
        existing = self._read(video_id) or {}

        # Calculate progress percentage
        try:
            stage_idx = PIPELINE_STAGES.index(stage)
            progress_pct = int((stage_idx / (len(PIPELINE_STAGES) - 1)) * 100)
        except ValueError:
            progress_pct = existing.get("progress_pct", 0)

        existing.update({
            "stage": stage,
            "progress_pct": progress_pct,
            "message": message or f"Processing: {stage.replace('_', ' ').title()}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
        })

        if stats:
            existing.setdefault("stats", {}).update(stats)

        self._write(video_id, existing)
        logger.info(f"[{video_id[:8]}] Stage: {stage} ({progress_pct}%) — {message}")

    def mark_done(self, video_id: str, stats: dict = None) -> None:
        """Mark processing as complete with final stats."""
        existing = self._read(video_id) or {}
        existing.update({
            "stage": "done",
            "progress_pct": 100,
            "message": "Processing complete — video is searchable",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error": None,
        })
        if stats:
            existing.setdefault("stats", {}).update(stats)
        self._write(video_id, existing)
        logger.info(f"[{video_id[:8]}] Processing DONE")

    def mark_failed(self, video_id: str, error: str) -> None:
        """Mark processing as failed with error details."""
        existing = self._read(video_id) or {}
        existing.update({
            "stage": "failed",
            "message": f"Processing failed: {error}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "error": error,
        })
        self._write(video_id, existing)
        logger.error(f"[{video_id[:8]}] Processing FAILED: {error}")

    def get_status(self, video_id: str) -> Optional[dict]:
        """
        Get the current processing status for a video.

        Returns:
            Status dict, or None if no status file exists.
        """
        return self._read(video_id)

    def _write(self, video_id: str, data: dict) -> None:
        """Write status dict to JSON file."""
        try:
            with open(self._status_path(video_id), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not write status for {video_id}: {e}")

    def _read(self, video_id: str) -> Optional[dict]:
        """Read status dict from JSON file."""
        path = self._status_path(video_id)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read status for {video_id}: {e}")
            return None
