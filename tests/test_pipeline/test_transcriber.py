"""
Tests for the transcriber module.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestTranscriber:
    """Tests for pipeline.audio_processing.transcriber."""

    def test_save_transcript(self, tmp_path):
        """save_transcript should write a valid JSON file."""
        from pipeline.audio_processing.transcriber import save_transcript

        transcript = {
            "text": "Hello world",
            "language": "en",
            "segments": [{"id": 0, "start": 0.0, "end": 1.5, "text": "Hello world"}],
        }

        output = str(tmp_path / "transcript.json")
        result = save_transcript(transcript, output)

        assert result == output
        assert (tmp_path / "transcript.json").exists()

    @patch("whisper.load_model")
    def test_transcribe_audio_returns_dict(self, mock_load):
        """transcribe_audio should return a dict with text and segments."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Test",
            "language": "en",
            "segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "Test"}],
        }
        mock_load.return_value = mock_model

        from pipeline.audio_processing.transcriber import transcribe_audio

        result = transcribe_audio("test.wav", model_name="tiny")

        assert "text" in result
        assert "segments" in result
