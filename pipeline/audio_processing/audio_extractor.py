"""
Audio Extractor — extracts audio tracks from video files using FFmpeg.
"""

import subprocess
from pathlib import Path


def extract_audio(
    video_path: str,
    output_path: str = None,
    audio_format: str = "wav",
    sample_rate: int = 16000,
) -> str:
    """
    Extract the audio track from a video file using FFmpeg.

    Args:
        video_path: Path to the source video file.
        output_path: Path for the output audio file. Auto-generated if None.
        audio_format: Output format (wav, mp3, flac).
        sample_rate: Audio sample rate in Hz (16000 for Whisper).

    Returns:
        Path to the extracted audio file.
    """
    video_path = Path(video_path)

    if output_path is None:
        output_path = str(video_path.with_suffix(f".{audio_format}"))

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                   # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit encoding
        "-ar", str(sample_rate), # Sample rate
        "-ac", "1",              # Mono channel
        "-y",                    # Overwrite output
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    return output_path
