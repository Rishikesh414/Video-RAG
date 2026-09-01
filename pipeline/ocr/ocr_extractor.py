"""
OCR Extractor — extracts text visible in video frames using EasyOCR.

Captures on-screen text such as slide titles, code snippets,
formulas, and annotations from lecture video frames.
"""

from typing import List, Dict

import easyocr


# Lazy-loaded reader instance
_reader = None


def get_reader(languages: List[str] = None) -> easyocr.Reader:
    """Get or initialize the EasyOCR reader."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(languages or ["en"], gpu=True)
    return _reader


def extract_text_from_frame(
    frame_path: str,
    languages: List[str] = None,
    confidence_threshold: float = 0.3,
) -> List[Dict]:
    """
    Extract text from a single video frame image.

    Args:
        frame_path: Path to the frame image file.
        languages: List of language codes for OCR.
        confidence_threshold: Minimum confidence to include a detection.

    Returns:
        List of dicts with 'text', 'confidence', and 'bbox' for each detection.
    """
    reader = get_reader(languages)
    results = reader.readtext(frame_path)

    detections = []
    for bbox, text, confidence in results:
        if confidence >= confidence_threshold:
            detections.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox,
            })

    return detections


def extract_text_from_frames(
    frame_paths: List[str],
    languages: List[str] = None,
) -> Dict[str, str]:
    """
    Extract text from multiple frames and aggregate by frame.

    Args:
        frame_paths: List of paths to frame images.
        languages: Language codes for OCR.

    Returns:
        Dict mapping frame_path -> extracted text string.
    """
    results = {}
    for path in frame_paths:
        detections = extract_text_from_frame(path, languages)
        combined_text = " ".join(det["text"] for det in detections)
        results[path] = combined_text.strip()
    return results
