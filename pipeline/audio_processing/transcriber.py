"""
Transcriber — converts speech to text using OpenAI Whisper Large-v3.

Generates timestamped transcripts for video content, enabling
precise retrieval of video segments based on spoken content.
"""

import json
from pathlib import Path
from typing import List, Dict

import whisper


def transcribe_audio(
    audio_path: str,
    model_name: str = "large-v3",
    language: str = None,
) -> Dict:
    """
    Transcribe an audio file to text using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file (WAV recommended).
        model_name: Whisper model size (tiny, base, small, medium, large-v3).
        language: Language code (e.g., 'en'). Auto-detected if None.

    Returns:
        Dict with 'text' (full transcript) and 'segments' (timestamped chunks).
    """
    model = whisper.load_model(model_name)

    result = model.transcribe(
        audio_path,
        language=language,
        verbose=False,
    )

    return {
        "text": result["text"],
        "language": result.get("language", "unknown"),
        "segments": [
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result["segments"]
        ],
    }


def save_transcript(transcript: Dict, output_path: str) -> str:
    """
    Save a transcript to a JSON file.

    Args:
        transcript: The transcript dict from transcribe_audio().
        output_path: Path to save the JSON file.

    Returns:
        The output file path.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    return str(output)
