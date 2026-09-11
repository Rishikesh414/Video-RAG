"""
Vector Store — Qdrant client for storing and searching text metadata embeddings.

Part of Step 2 (Retrieval). Stores embeddings of the enriched metadata
chunks from Step 1 and enables fast cosine similarity search via Qdrant.
"""

import uuid
import logging
from typing import List, Dict, Optional, Union

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

logger = logging.getLogger(__name__)

COLLECTION_NAME = "videorag_chunks"


class VectorStore:
    """
    Qdrant vector store for semantic search over video metadata embeddings.
    Uses cosine similarity for nearest-neighbor retrieval.
    """

    def __init__(
        self,
        embedding_dim: int = 384,
        host: Optional[str] = "localhost",
        port: int = 6333,
        collection_name: str = COLLECTION_NAME,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        path: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """
        Args:
            embedding_dim: Dimension of the embedding vectors.
            host: Qdrant server host.
            port: Qdrant server gRPC/REST port.
            collection_name: Name of the Qdrant collection.
            url: Full Qdrant Cloud or REST URL (overrides host/port).
            api_key: API key for Qdrant Cloud.
            path: Local disk directory for embedded Qdrant storage.
            location: Specific location (e.g., ":memory:" for in-memory).
        """
        self.embedding_dim = embedding_dim
        self.collection_name = collection_name

        # Flexible client initialization
        if location:
            self.client = QdrantClient(location=location)
        elif path:
            self.client = QdrantClient(path=path)
        elif url:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            try:
                self.client = QdrantClient(host=host, port=port, api_key=api_key, timeout=2.0)
                # Test connectivity
                self.client.get_collections()
            except Exception as e:
                logger.warning(
                    f"Could not connect to Qdrant at {host}:{port} ({e}). "
                    "Falling back to in-memory Qdrant instance."
                )
                self.client = QdrantClient(location=":memory:")

        # Create collection if it doesn't exist
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the Qdrant collection if it doesn't already exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection '{self.collection_name}': {e}")
            raise

    def add_embeddings(
        self,
        embeddings: Union[np.ndarray, List[List[float]]],
        metadata_list: List[Dict],
    ) -> None:
        """
        Add embeddings and metadata to the Qdrant collection.

        Args:
            embeddings: Array of shape (n, embedding_dim) or list of vector floats.
            metadata_list: Parallel list of metadata dicts (one per embedding).
        """
        assert len(embeddings) == len(metadata_list), "Embeddings and metadata must have same length"

        points = []
        for i, (emb, meta) in enumerate(zip(embeddings, metadata_list)):
            point_id = str(uuid.uuid4())
            vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload=meta,
                )
            )

        # Upsert in batches of 100
        batch_size = 100
        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

    def search(
        self,
        query_embedding: Union[np.ndarray, List[float]],
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search for the most similar vectors in Qdrant.

        Args:
            query_embedding: Query vector of shape (embedding_dim,).
            top_k: Number of results to return.

        Returns:
            List of dicts with 'score' and 'metadata' keys.
        """
        query_vec = query_embedding.tolist() if hasattr(query_embedding, "tolist") else list(query_embedding)

        if hasattr(self.client, "query_points"):
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vec,
                limit=top_k,
            ).points
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vec,
                limit=top_k,
            )

        return [
            {
                "score": float(hit.score),
                "metadata": hit.payload or {},
            }
            for hit in results
        ]

    def delete_collection(self) -> None:
        """Delete the entire collection. USE WITH CAUTION."""
        self.client.delete_collection(collection_name=self.collection_name)

    @property
    def total_vectors(self) -> int:
        """Return the total number of vectors in the collection."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            count = getattr(info, "points_count", None)
            if count is None:
                count = getattr(info, "vectors_count", 0)
            return count or 0
        except Exception:
            return 0
