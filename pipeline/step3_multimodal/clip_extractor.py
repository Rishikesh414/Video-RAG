"""
Clip Extractor — cuts a specific time window from a video using FFmpeg.

Part of Step 3 (Multimodal). After Step 2 identifies the exact timestamps,
this module extracts just that short clip (typically 15-60 seconds) from
the full video. The clip is what gets sent to the Multimodal LLM and
returned to the user.
"""

import uuid
import subprocess
from pathlib import Path


def extract_clip(
    video_path: str,
    start_time: float,
    end_time: float,
    output_dir: str,
    clip_id: str = None,
    output_format: str = "mp4",
) -> dict:
    """
    Extract a video clip at the specified time window using FFmpeg.

    Uses stream copy (-c copy) for speed when possible, falling back
    to re-encoding for precise timestamp cuts.

    Args:
        video_path: Path to the source video file.
        start_time: Start timestamp in seconds.
        end_time: End timestamp in seconds.
        output_dir: Directory to save the output clip.
        clip_id: Unique identifier for the clip. Auto-generated if None.
        output_format: Output video format (default: mp4).

    Returns:
        Dict with:
        - clip_id (str): Unique clip identifier
        - clip_path (str): Absolute path to the extracted clip file
        - duration (float): Clip duration in seconds
        - start_time (float): Start timestamp
        - end_time (float): End timestamp
        - source_video (str): Path to the original video
    """
    if clip_id is None:
        clip_id = str(uuid.uuid4())[:12]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    clip_filename = f"clip_{clip_id}.{output_format}"
    clip_path = output_path / clip_filename

    duration = end_time - start_time

    cmd = [
        "ffmpeg",
        "-ss", str(start_time),       # Seek to start (before input for speed)
        "-i", str(video_path),
        "-t", str(duration),           # Duration of clip
        "-c:v", "libx264",            # Re-encode video for precise cuts
        "-c:a", "aac",                # Re-encode audio
        "-preset", "fast",            # Fast encoding
        "-movflags", "+faststart",    # Web-optimized MP4
        "-y",                          # Overwrite output
        str(clip_path),
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    return {
        "clip_id": clip_id,
        "clip_path": str(clip_path.resolve()),
        "clip_filename": clip_filename,
        "duration": round(duration, 2),
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
        "source_video": str(video_path),
    }


def get_clip_url(clip_filename: str, base_url: str = "/static/clips") -> str:
    """
    Generate a URL for serving the clip to the frontend.

    Args:
        clip_filename: The filename of the clip (e.g., clip_abc123.mp4).
        base_url: Base URL path for static clip serving.

    Returns:
        Full URL path for the clip.
    """
    return f"{base_url}/{clip_filename}"
