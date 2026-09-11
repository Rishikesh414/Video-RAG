"""
Response Builder — assembles the final 3-part output from the pipeline.

Part of Step 3 (Multimodal). Combines the outputs of all three steps
into the structured response the user receives:

    1. Text response   — The LLM's answer to the question
    2. Video clip       — The extracted clip file (URL + path)
    3. Timestamps       — Start/end times in the source video
"""

from typing import Dict, Optional


def build_response(
    answer_text: str,
    clip_info: Dict,
    timestamp_info: Dict,
    search_results: list = None,
) -> Dict:
    """
    Build the final 3-part response.

    Args:
        answer_text: The multimodal LLM's detailed answer.
        clip_info: Output from clip_extractor.extract_clip().
        timestamp_info: Output from timestamp_resolver.resolve().
        search_results: Optional raw search results for source attribution.

    Returns:
        Dict with three clearly separated output sections:
        - answer: Text response for the user
        - video_clip: Clip file details (URL, path, download info)
        - timestamp: Timing information from the source video
    """
    # 1. Text Response
    answer = {
        "text": answer_text,
        "confidence": timestamp_info.get("confidence", "unknown"),
        "reasoning": timestamp_info.get("reasoning", ""),
    }

    # 2. Video Clip
    video_clip = {
        "clip_id": clip_info.get("clip_id", ""),
        "clip_url": clip_info.get("clip_url", ""),
        "clip_path": clip_info.get("clip_path", ""),
        "clip_filename": clip_info.get("clip_filename", ""),
        "duration": clip_info.get("duration", 0),
    }

    # 3. Timestamp
    timestamp = {
        "start_time": clip_info.get("start_time", 0),
        "end_time": clip_info.get("end_time", 0),
        "source_video": clip_info.get("source_video", ""),
        "video_id": timestamp_info.get("video_id", ""),
        "formatted_start": _format_time(clip_info.get("start_time", 0)),
        "formatted_end": _format_time(clip_info.get("end_time", 0)),
    }

    # Sources attribution
    sources = []
    if search_results:
        seen = set()
        for r in search_results:
            vid = r.get("video_id", "unknown")
            if vid not in seen:
                seen.add(vid)
                sources.append(vid)

    return {
        "answer": answer,
        "video_clip": video_clip,
        "timestamp": timestamp,
        "sources": sources,
    }


def _format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
