"""
Adaptive Framing — uses K-Means Clustering to select the most informative
key frames from thousands of extracted frames.

This is the core visual compression technique described in VideoRAG:
reduce N frames down to K representative frames (default K=32) while
preserving maximum visual diversity and information.
"""

from typing import List

import cv2
import numpy as np
from sklearn.cluster import KMeans


def select_key_frames(
    frame_paths: List[str],
    n_keyframes: int = 32,
) -> List[str]:
    """
    Apply K-Means clustering to select the most representative key frames.

    Algorithm:
    1. Load all frames and compute a compact feature vector for each
       (resized + flattened pixel values).
    2. Run K-Means with K = n_keyframes clusters.
    3. For each cluster, select the frame closest to the centroid.

    Args:
        frame_paths: List of file paths to extracted frames.
        n_keyframes: Number of key frames to select (default 32).

    Returns:
        List of file paths to the selected key frames, ordered by their
        original position in the video.
    """
    if len(frame_paths) <= n_keyframes:
        return frame_paths

    # Compute feature vectors for all frames
    features = []
    for path in frame_paths:
        img = cv2.imread(path)
        img_resized = cv2.resize(img, (64, 64))  # Small fixed size for clustering
        features.append(img_resized.flatten().astype(np.float32))

    features_array = np.array(features)

    # Normalize features
    norms = np.linalg.norm(features_array, axis=1, keepdims=True)
    norms[norms == 0] = 1
    features_array = features_array / norms

    # K-Means clustering
    kmeans = KMeans(n_clusters=n_keyframes, random_state=42, n_init=10)
    kmeans.fit(features_array)

    # Select frame closest to each cluster centroid
    selected_indices = []
    for cluster_idx in range(n_keyframes):
        cluster_mask = kmeans.labels_ == cluster_idx
        cluster_features = features_array[cluster_mask]
        cluster_indices = np.where(cluster_mask)[0]

        centroid = kmeans.cluster_centers_[cluster_idx]
        distances = np.linalg.norm(cluster_features - centroid, axis=1)
        closest_idx = cluster_indices[np.argmin(distances)]
        selected_indices.append(closest_idx)

    # Sort by original order to preserve temporal sequence
    selected_indices.sort()

    return [frame_paths[i] for i in selected_indices]
