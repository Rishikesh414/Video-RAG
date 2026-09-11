"""
Tests for the pipeline orchestrator.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestOrchestrator:
    """Tests for pipeline.orchestrator.VideoRAGOrchestrator."""

    def test_response_builder_format(self):
        """response_builder should produce the 3-part output structure."""
        from pipeline.step3_multimodal.response_builder import build_response

        result = build_response(
            answer_text="The package was dropped at the door.",
            clip_info={
                "clip_id": "abc123",
                "clip_url": "/static/clips/clip_abc123.mp4",
                "clip_path": "/data/clips/clip_abc123.mp4",
                "clip_filename": "clip_abc123.mp4",
                "duration": 30.0,
                "start_time": 255.0,
                "end_time": 285.0,
                "source_video": "lecture_01.mp4",
            },
            timestamp_info={
                "video_id": "vid_001",
                "confidence": "high",
                "reasoning": "Matched transcript mentions delivery.",
            },
            search_results=[
                {"video_id": "vid_001", "content": "...", "start_time": 255, "end_time": 285},
            ],
        )

        # Verify 3-part structure
        assert "answer" in result
        assert "video_clip" in result
        assert "timestamp" in result
        assert "sources" in result

        # Output 1: Text answer
        assert result["answer"]["text"] == "The package was dropped at the door."
        assert result["answer"]["confidence"] == "high"

        # Output 2: Video clip
        assert result["video_clip"]["clip_id"] == "abc123"
        assert result["video_clip"]["duration"] == 30.0

        # Output 3: Timestamp
        assert result["timestamp"]["start_time"] == 255.0
        assert result["timestamp"]["formatted_start"] == "04:15"

    def test_metadata_builder_chunks(self):
        """metadata_to_searchable_chunks should produce indexed chunks."""
        from pipeline.step1_indexing.metadata_builder import metadata_to_searchable_chunks

        metadata = {
            "video_id": "test_vid",
            "video_path": "/data/videos/test.mp4",
            "segments": [
                {"start": 0, "end": 5, "combined_text": "Hello world " * 50},
                {"start": 5, "end": 10, "combined_text": "Second segment " * 50},
            ],
        }

        chunks = metadata_to_searchable_chunks(metadata, chunk_size=200)
        assert len(chunks) > 0
        assert chunks[0]["video_id"] == "test_vid"
        assert "start_time" in chunks[0]
        assert "end_time" in chunks[0]
