"""
Tests for the frame extractor module.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestFrameExtractor:
    """Tests for pipeline.video_processing.frame_extractor."""

    @patch("cv2.VideoCapture")
    def test_extract_frames_creates_output_dir(self, mock_cap, tmp_path):
        """Frame extraction should create the output directory if missing."""
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = False
        mock_instance.get.return_value = 30.0
        mock_cap.return_value = mock_instance

        from pipeline.video_processing.frame_extractor import extract_frames

        output_dir = str(tmp_path / "frames")
        extract_frames("test.mp4", output_dir)

        assert (tmp_path / "frames").exists()

    @patch("cv2.VideoCapture")
    def test_extract_frames_returns_list(self, mock_cap, tmp_path):
        """Frame extraction should return a list of file paths."""
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = False
        mock_instance.get.return_value = 30.0
        mock_cap.return_value = mock_instance

        from pipeline.video_processing.frame_extractor import extract_frames

        result = extract_frames("test.mp4", str(tmp_path / "frames"))
        assert isinstance(result, list)
