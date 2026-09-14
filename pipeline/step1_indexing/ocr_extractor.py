"""
OCR Extractor — extracts text from scene keyframes using EasyOCR.

Part of Step 1 (Indexing). Designed for education-domain lecture videos where:
- Slides show titles, bullet points, equations, code
- Whiteboards show handwritten derivations
- Screen recordings show code editors, terminals

OCR text is merged into searchable metadata chunks in Qdrant, enabling
students to search for specific slide content or equations by text.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class OCRExtractor:
    """
    EasyOCR-based text extractor for video scene keyframes.

    Extracts printed and handwritten text from slides, whiteboards,
    and screen recordings in educational lecture videos.
    """

    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """
        Initialize the OCR extractor.

        Args:
            languages: List of EasyOCR language codes (e.g., ['en']).
                       Defaults to English. Add 'hi' for Hindi, etc.
            gpu: Whether to use GPU acceleration (requires CUDA).
        """
        self.languages = languages or ["en"]
        self.gpu = gpu
        self._reader = None  # Lazy-loaded

    def _load_reader(self):
        """Load EasyOCR reader on first use."""
        try:
            import easyocr
            self._reader = easyocr.Reader(self.languages, gpu=self.gpu)
            logger.info(f"EasyOCR loaded for languages: {self.languages}")
        except ImportError:
            logger.error(
                "EasyOCR is not installed. Run: pip install easyocr\n"
                "OCR extraction will be skipped."
            )
            self._reader = None

    def extract_text_from_frame(
        self,
        frame: np.ndarray,
        confidence_threshold: float = 0.4,
    ) -> Dict:
        """
        Extract text from a single video frame (scene keyframe).

        Args:
            frame: NumPy BGR image array from OpenCV.
            confidence_threshold: Minimum confidence to include detected text.

        Returns:
            Dict with:
            - 'text': Combined cleaned text string
            - 'blocks': List of {text, confidence, bbox} per detection
            - 'word_count': Number of words found
        """
        if self._reader is None:
            self._load_reader()

        if self._reader is None:
            # EasyOCR not available — return empty result
            return {"text": "", "blocks": [], "word_count": 0}

        try:
            # Preprocess: convert to RGB for EasyOCR (it works on RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Run OCR
            results = self._reader.readtext(frame_rgb, detail=1)

            blocks = []
            text_lines = []

            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold and text.strip():
                    clean_text = text.strip()
                    blocks.append({
                        "text": clean_text,
                        "confidence": round(float(confidence), 3),
                        "bbox": [[int(p[0]), int(p[1])] for p in bbox],
                    })
                    text_lines.append(clean_text)

            # Sort blocks by vertical position (top to bottom, like reading)
            blocks = sorted(blocks, key=lambda b: b["bbox"][0][1])
            text_lines = [b["text"] for b in blocks]

            combined_text = " ".join(text_lines)
            word_count = len(combined_text.split()) if combined_text else 0

            return {
                "text": combined_text,
                "blocks": blocks,
                "word_count": word_count,
            }

        except Exception as e:
            logger.warning(f"OCR failed on frame: {e}")
            return {"text": "", "blocks": [], "word_count": 0}

    def extract_from_scenes(
        self,
        video_path: str,
        scenes: List[tuple],
        confidence_threshold: float = 0.4,
        min_word_count: int = 3,
    ) -> List[Dict]:
        """
        Extract OCR text from the keyframe of each detected scene.

        Takes one representative frame per scene (the midpoint frame)
        to capture slide/whiteboard text for that scene.

        Args:
            video_path: Path to the video file.
            scenes: List of (start_time, end_time) tuples in seconds.
            confidence_threshold: Min detection confidence.
            min_word_count: Discard results with fewer words (noise filter).

        Returns:
            List of dicts with:
            - 'scene_start': float (seconds)
            - 'scene_end': float (seconds)
            - 'timestamp': float (keyframe timestamp)
            - 'text': Extracted OCR text
            - 'blocks': Raw OCR block detections
            - 'word_count': Number of words detected
        """
        ocr_results = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            logger.warning(f"Could not read FPS from {video_path}")
            cap.release()
            return ocr_results

        for (scene_start, scene_end) in scenes:
            # Use the midpoint of the scene as the keyframe
            mid_time = (scene_start + scene_end) / 2.0
            mid_frame_idx = int(mid_time * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_idx)
            ret, frame = cap.read()

            if not ret:
                # Try scene start + 1s if midpoint fails
                start_frame_idx = int(scene_start * fps) + int(fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_idx)
                ret, frame = cap.read()

            if not ret:
                logger.debug(f"Could not read keyframe for scene {scene_start:.1f}s-{scene_end:.1f}s")
                continue

            result = self.extract_text_from_frame(frame, confidence_threshold)

            # Only include if enough words were found (filter noise)
            if result["word_count"] >= min_word_count:
                ocr_results.append({
                    "scene_start": round(scene_start, 2),
                    "scene_end": round(scene_end, 2),
                    "timestamp": round(mid_time, 2),
                    "text": result["text"],
                    "blocks": result["blocks"],
                    "word_count": result["word_count"],
                })
            else:
                # Record scene with empty OCR result so we know it was processed
                ocr_results.append({
                    "scene_start": round(scene_start, 2),
                    "scene_end": round(scene_end, 2),
                    "timestamp": round(mid_time, 2),
                    "text": "",
                    "blocks": [],
                    "word_count": 0,
                })

        cap.release()
        logger.info(
            f"OCR completed: {sum(1 for r in ocr_results if r['word_count'] > 0)} "
            f"of {len(ocr_results)} scenes had text"
        )
        return ocr_results

    def get_ocr_for_timestamp(
        self,
        ocr_results: List[Dict],
        timestamp: float,
    ) -> str:
        """
        Find the OCR text for the scene that contains a given timestamp.

        Args:
            ocr_results: Output from extract_from_scenes().
            timestamp: Timestamp in seconds.

        Returns:
            OCR text string, or empty string if no match.
        """
        for result in ocr_results:
            if result["scene_start"] <= timestamp <= result["scene_end"]:
                return result.get("text", "")
        return ""
