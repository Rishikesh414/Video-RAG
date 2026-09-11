"""
Metadata Builder — combines transcript, visual tags, and scene boundaries
into a unified text metadata document for each video.

Part of Step 1 (Indexing). This is the final output of the indexing step:
a structured JSON metadata file that represents the entire video as a few
kilobytes of searchable text instead of gigabytes of raw video.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple


def build_metadata(
    video_id: str,
    video_path: str,
    transcript: Dict,
    visual_tags: List[Dict],
    scenes: List[Tuple[float, float]],
    extra: Dict = None,
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

    Returns:
        Unified metadata dict ready for embedding and storage.
    """
    # Merge transcript segments and visual tags by timestamp proximity
    enriched_segments = _enrich_segments(transcript.get("segments", []), visual_tags)

    metadata = {
        "video_id": video_id,
        "video_path": video_path,
        "language": transcript.get("language", "unknown"),
        "full_transcript": transcript.get("text", ""),
        "segments": enriched_segments,
        "scenes": [{"start": s, "end": e} for s, e in scenes],
        "visual_tags_summary": _summarize_tags(visual_tags),
        "total_duration": _get_duration(transcript, scenes),
        **(extra or {}),
    }

    return metadata


def _enrich_segments(
    transcript_segments: List[Dict],
    visual_tags: List[Dict],
) -> List[Dict]:
    """
    Merge transcript segments with visual tags that fall within each
    segment's time window, creating enriched searchable text.
    """
    enriched = []

    for seg in transcript_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]

        # Find visual tags that overlap with this transcript segment
        relevant_tags = [
            tag for tag in visual_tags
            if seg_start <= tag["timestamp"] <= seg_end
        ]

        objects_in_segment = set()
        for tag in relevant_tags:
            objects_in_segment.update(tag.get("objects", []))

        # Build combined text for this segment
        visual_context = f" [Visual: {', '.join(sorted(objects_in_segment))}]" if objects_in_segment else ""
        combined_text = f"{seg['text']}{visual_context}"

        enriched.append({
            "id": seg["id"],
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"],
            "combined_text": combined_text,
            "visual_objects": sorted(objects_in_segment),
        })

    return enriched


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
        })

    return chunks
