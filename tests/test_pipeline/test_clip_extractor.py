"""
Tests for the clip extractor module (Step 3).
"""

import pytest
from unittest.mock import patch


class TestClipExtractor:
    """Tests for pipeline.step3_multimodal.clip_extractor."""

    def test_get_clip_url(self):
        """get_clip_url should build the correct static URL."""
        from pipeline.step3_multimodal.clip_extractor import get_clip_url

        url = get_clip_url("clip_abc123.mp4")
        assert url == "/static/clips/clip_abc123.mp4"

    def test_get_clip_url_custom_base(self):
        """get_clip_url should respect custom base URL."""
        from pipeline.step3_multimodal.clip_extractor import get_clip_url

        url = get_clip_url("clip_test.mp4", base_url="/media/clips")
        assert url == "/media/clips/clip_test.mp4"

    @patch("subprocess.run")
    def test_extract_clip_returns_dict(self, mock_run, tmp_path):
        """extract_clip should return a dict with clip info."""
        mock_run.return_value = None

        from pipeline.step3_multimodal.clip_extractor import extract_clip

        result = extract_clip(
            video_path="test.mp4",
            start_time=10.0,
            end_time=40.0,
            output_dir=str(tmp_path),
            clip_id="testclip",
        )

        assert result["clip_id"] == "testclip"
        assert result["duration"] == 30.0
        assert result["start_time"] == 10.0
        assert result["end_time"] == 40.0
        assert "clip_testclip.mp4" in result["clip_filename"]
