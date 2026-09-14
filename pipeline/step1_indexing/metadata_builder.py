"""
Metadata Builder — combines transcript, visual tags, OCR text, and visual
descriptions into a unified text metadata document for each video.

Part of Step 1 (Indexing). This is the final output of the indexing step:
a structured JSON metadata file that represents the entire video as a few
kilobytes of searchable text instead of gigabytes of raw video.

Education-domain enhancements:
- OCR text from scene keyframes (slides, whiteboard text, equations)
- VLM visual descriptions per scene (scene context for non-speech content)
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def build_metadata(
    video_id: str,
    video_path: str,
    transcript: Dict,
    visual_tags: List[Dict],
    scenes: List[Tuple[float, float]],
    extra: Dict = None,
    ocr_results: List[Dict] = None,
    scene_descriptions: List[Dict] = None,
) -> Dict:
    """
    Combine all Step 1 outputs into a single metadata document.

    Args:
        video_id: Unique identifier for the video.
        video_path: Original path to the video file.
        transcript: Whisper transcript with segments.
        visual_tags: Visual tagger output (timestamped object tags).
        scenes: Scene boundary list from scene detector.
        extra: Any additional metadata (uploader, module, etc.).
        ocr_results: OCR text per scene (from OCRExtractor.extract_from_scenes).
        scene_descriptions: VLM descriptions per scene (from VisualDescriber.describe_scenes).

    Returns:
        Unified metadata dict ready for embedding and storage.
    """
    # Merge transcript segments and visual tags by timestamp proximity
    enriched_segments = _enrich_segments(
        transcript.get("segments", []),
        visual_tags,
        scenes,
        ocr_results or [],
        scene_descriptions or [],
    )

    # Build OCR summary from all scene text
    ocr_summary = _build_ocr_summary(ocr_results or [])

    # Build scene descriptions summary
    descriptions_summary = _build_descriptions_summary(scene_descriptions or [])

    metadata = {
        "video_id": video_id,
        "video_path": video_path,
        "language": transcript.get("language", "unknown"),
        "full_transcript": transcript.get("text", ""),
        "segments": enriched_segments,
        "scenes": [{
            "start": s,
            "end": e,
            "ocr_text": _get_ocr_for_scene(ocr_results or [], s, e),
            "visual_description": _get_description_for_scene(scene_descriptions or [], s, e),
        } for s, e in scenes],
        "visual_tags_summary": _summarize_tags(visual_tags),
        "ocr_summary": ocr_summary,
        "scene_descriptions_summary": descriptions_summary,
        "total_duration": _get_duration(transcript, scenes),
        **(extra or {}),
    }

    return metadata


def _enrich_segments(
    transcript_segments: List[Dict],
    visual_tags: List[Dict],
    scenes: List[Tuple[float, float]],
    ocr_results: List[Dict],
    scene_descriptions: List[Dict],
) -> List[Dict]:
    """
    Merge transcript segments with all available metadata sources:
    - Visual tags (YOLO object detection)
    - OCR text (slides/whiteboard text)
    - VLM scene descriptions

    Creates rich combined_text per segment for high-quality semantic search.
    """
    enriched = []

    for seg in transcript_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]

        # 1. Visual tags (YOLO objects) that overlap with this segment
        relevant_tags = [
            tag for tag in visual_tags
            if seg_start <= tag["timestamp"] <= seg_end
        ]
        objects_in_segment = set()
        for tag in relevant_tags:
            objects_in_segment.update(tag.get("objects", []))

        # 2. OCR text: find the scene that contains this segment's midpoint
        seg_mid = (seg_start + seg_end) / 2.0
        ocr_text = _get_ocr_for_timestamp(ocr_results, seg_mid)

        # 3. Visual description: find the scene containing this segment
        visual_desc = _get_description_for_timestamp(scene_descriptions, seg_mid)

        # 4. Build enriched combined_text (for Qdrant embedding)
        #    Priority: transcript text > OCR text > visual description > object tags
        parts = [seg["text"].strip()]

        if ocr_text:
            parts.append(f"[Slide/Screen Text: {ocr_text}]")

        if visual_desc:
            parts.append(f"[Visual: {visual_desc}]")
        elif objects_in_segment:
            parts.append(f"[Objects: {', '.join(sorted(objects_in_segment))}]")

        combined_text = " ".join(p for p in parts if p)

        enriched.append({
            "id": seg["id"],
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"],
            "combined_text": combined_text,
            "visual_objects": sorted(objects_in_segment),
            "ocr_text": ocr_text,
            "visual_description": visual_desc,
        })

    return enriched


def _get_ocr_for_timestamp(ocr_results: List[Dict], timestamp: float) -> str:
    """Get OCR text for the scene containing a timestamp."""
    for result in ocr_results:
        if result["scene_start"] <= timestamp <= result["scene_end"]:
            return result.get("text", "")
    return ""


def _get_description_for_timestamp(scene_descriptions: List[Dict], timestamp: float) -> str:
    """Get visual description for the scene containing a timestamp."""
    for d in scene_descriptions:
        if d["scene_start"] <= timestamp <= d["scene_end"]:
            return d.get("description", "")
    return ""


def _get_ocr_for_scene(ocr_results: List[Dict], scene_start: float, scene_end: float) -> str:
    """Get OCR text for a specific scene boundary."""
    for result in ocr_results:
        if (abs(result["scene_start"] - scene_start) < 1.0 and
                abs(result["scene_end"] - scene_end) < 1.0):
            return result.get("text", "")
    return ""


def _get_description_for_scene(
    scene_descriptions: List[Dict],
    scene_start: float,
    scene_end: float,
) -> str:
    """Get VLM description for a specific scene boundary."""
    for d in scene_descriptions:
        if (abs(d["scene_start"] - scene_start) < 1.0 and
                abs(d["scene_end"] - scene_end) < 1.0):
            return d.get("description", "")
    return ""


def _build_ocr_summary(ocr_results: List[Dict]) -> str:
    """Build a text summary of all OCR-detected text across the video."""
    texts = [r["text"] for r in ocr_results if r.get("text")]
    return " | ".join(texts) if texts else ""


def _build_descriptions_summary(scene_descriptions: List[Dict]) -> str:
    """Build a summary of all VLM scene descriptions."""
    descs = [d["description"] for d in scene_descriptions if d.get("description")]
    return " ".join(descs) if descs else ""


def _summarize_tags(visual_tags: List[Dict]) -> str:
    """Create a text summary of all visual detections across the video."""
    all_objects = set()
    for tag in visual_tags:
        all_objects.update(tag.get("objects", []))
    return ", ".join(sorted(all_objects)) if all_objects else "none"


def _get_duration(transcript: Dict, scenes: List[Tuple[float, float]]) -> float:
    """Estimate total video duration from available data."""
    duration = 0.0

    segments = transcript.get("segments", [])
    if segments:
        duration = max(seg["end"] for seg in segments)

    if scenes:
        scene_end = max(end for _, end in scenes)
        duration = max(duration, scene_end)

    return round(duration, 2)


def save_metadata(metadata: Dict, output_path: str) -> str:
    """
    Save metadata to a JSON file.

    Args:
        metadata: The metadata dict from build_metadata().
        output_path: Path to save the JSON file.

    Returns:
        The output file path.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return str(output)


def load_metadata(metadata_path: str) -> Dict:
    """Load metadata from a JSON file."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def metadata_to_searchable_chunks(
    metadata: Dict,
    chunk_size: int = 500,
) -> List[Dict]:
    """
    Convert metadata into searchable text chunks for Qdrant indexing.

    Groups consecutive enriched segments until they reach chunk_size,
    preserving timestamp boundaries.

    Each chunk's content now includes OCR text and visual descriptions,
    making them semantically richer and more retrievable.

    Args:
        metadata: The full metadata document.
        chunk_size: Target character count per chunk.

    Returns:
        List of dicts with 'content', 'start_time', 'end_time', 'video_id'.
    """
    segments = metadata.get("segments", [])
    video_id = metadata.get("video_id", "")
    chunks = []

    current_text = ""
    current_start = 0.0
    current_end = 0.0

    for seg in segments:
        if not current_text:
            current_start = seg["start"]

        current_text += seg.get("combined_text", seg.get("text", "")) + " "
        current_end = seg["end"]

        if len(current_text) >= chunk_size:
            chunks.append({
                "content": current_text.strip(),
                "start_time": current_start,
                "end_time": current_end,
                "video_id": video_id,
                "video_path": metadata.get("video_path", ""),
                # Extra metadata for filtering/display
                "language": metadata.get("language", ""),
                "module": metadata.get("module", ""),
            })
            current_text = ""

    # Last chunk
    if current_text.strip():
        chunks.append({
            "content": current_text.strip(),
            "start_time": current_start,
            "end_time": current_end,
            "video_id": video_id,
            "video_path": metadata.get("video_path", ""),
            "language": metadata.get("language", ""),
            "module": metadata.get("module", ""),
        })

    return chunks

