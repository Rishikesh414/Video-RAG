"""
Tests for the Qdrant VectorStore and SemanticSearch retriever modules.
"""

import unittest
from unittest.mock import MagicMock
import numpy as np

from pipeline.step2_retrieval.vector_store import VectorStore
from pipeline.step2_retrieval.semantic_search import SemanticSearch


class TestVectorStore(unittest.TestCase):
    """Tests for pipeline.step2_retrieval.vector_store.VectorStore using Qdrant."""

    def test_add_and_search(self):
        """Adding vectors and searching should return matching results."""
        store = VectorStore(embedding_dim=4, location=":memory:", collection_name="test_chunks")

        embeddings = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ], dtype=np.float32)

        metadata = [
            {"content": "chunk_1", "start_time": 0.0, "end_time": 10.0, "video_id": "v1", "video_path": "v1.mp4"},
            {"content": "chunk_2", "start_time": 10.0, "end_time": 20.0, "video_id": "v2", "video_path": "v2.mp4"},
            {"content": "chunk_3", "start_time": 20.0, "end_time": 30.0, "video_id": "v3", "video_path": "v3.mp4"},
        ]

        store.add_embeddings(embeddings, metadata)
        self.assertEqual(store.total_vectors, 3)

        query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        results = store.search(query, top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["content"], "chunk_1")
        self.assertGreater(results[0]["score"], 0.9)

    def test_semantic_search_integration(self):
        """SemanticSearch should combine embedder and vector store correctly."""
        store = VectorStore(embedding_dim=4, location=":memory:", collection_name="test_semantic")

        embeddings = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ], dtype=np.float32)

        metadata = [
            {"content": "intro chunk", "start_time": 0.0, "end_time": 15.0, "video_id": "vid1", "video_path": "/path/v1.mp4"},
            {"content": "advanced chunk", "start_time": 15.0, "end_time": 30.0, "video_id": "vid1", "video_path": "/path/v1.mp4"},
        ]
        store.add_embeddings(embeddings, metadata)

        # Mock embedder
        mock_embedder = MagicMock()
        mock_embedder.embed_text.return_value = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

        searcher = SemanticSearch(embedder=mock_embedder, store=store)
        results = searcher.search(query="tell me about intro", top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "intro chunk")
        self.assertEqual(results[0]["start_time"], 0.0)
        self.assertEqual(results[0]["end_time"], 15.0)
        self.assertEqual(results[0]["video_id"], "vid1")

        # Test context formatting
        context = searcher.format_context(results)
        self.assertIn("[Result 1 | Video: vid1 | 0.0s – 15.0s]", context)
        self.assertIn("intro chunk", context)


if __name__ == "__main__":
    unittest.main()
