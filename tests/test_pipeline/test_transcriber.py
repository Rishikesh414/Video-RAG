"""
Tests for the transcriber module.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

from pipeline.step1_indexing.transcriber import save_transcript, transcribe_audio


class TestTranscriber:
    """Tests for pipeline.step1_indexing.transcriber."""

    def test_save_transcript(self, tmp_path):
        """save_transcript should write a valid JSON file."""
        transcript = {
            "text": "Hello world",
            "language": "en",
            "segments": [{"id": 0, "start": 0.0, "end": 1.5, "text": "Hello world"}],
        }

        output = str(tmp_path / "transcript.json")
        result = save_transcript(transcript, output)

        assert result == output
        assert (tmp_path / "transcript.json").exists()

    def test_transcribe_audio_returns_dict(self):
        """transcribe_audio should return a dict with text and segments."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Test",
            "language": "en",
            "segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "Test"}],
        }

        mock_whisper = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict(sys.modules, {"whisper": mock_whisper}):
            result = transcribe_audio("test.wav", model_name="tiny")

            assert "text" in result
            assert "segments" in result
            assert result["text"] == "Test"
            assert len(result["segments"]) == 1
