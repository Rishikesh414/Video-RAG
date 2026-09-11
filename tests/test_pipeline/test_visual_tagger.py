"""
Tests for the visual tagger module (Step 1).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestVisualTagger:
    """Tests for pipeline.step1_indexing.visual_tagger."""

    def test_tags_to_text_format(self):
        """tags_to_text should produce [MM:SS] formatted lines."""
        from pipeline.step1_indexing.visual_tagger import VisualTagger

        tagger = VisualTagger.__new__(VisualTagger)
        tags = [
            {"timestamp": 12.5, "objects": ["car", "person", "road"]},
            {"timestamp": 225.0, "objects": ["person", "package", "door"]},
            {"timestamp": 0.0, "objects": []},
        ]

        result = tagger.tags_to_text(tags)

        assert "[00:12] car, person, road" in result
        assert "[03:45] person, package, door" in result
        assert "no objects detected" in result

    def test_save_tags(self, tmp_path):
        """save_tags should write a valid JSON file."""
        from pipeline.step1_indexing.visual_tagger import VisualTagger

        tagger = VisualTagger.__new__(VisualTagger)
        tags = [{"timestamp": 5.0, "objects": ["person"]}]

        output = str(tmp_path / "tags.json")
        result = tagger.save_tags(tags, output)

        assert result == output
        assert (tmp_path / "tags.json").exists()
