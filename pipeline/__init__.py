"""
VideoRAG Processing Pipeline — Hybrid Architecture.

A 3-step pipeline that uses cheap text-based filtering before
expensive multimodal analysis:

    Step 1 (Indexing):    ASR transcript + CV object tags → text metadata
    Step 2 (Retrieval):   Vector search → timestamp resolution via standard LLM
    Step 3 (Multimodal):  Clip extraction → Multimodal LLM deep analysis

Output: (1) Text answer, (2) Video clip, (3) Timestamps
"""
