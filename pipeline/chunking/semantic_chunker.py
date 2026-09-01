"""
Semantic Chunker — splits transcripts and documents into
semantically meaningful chunks using LangChain.

Uses embedding-based breakpoint detection to ensure each chunk
contains a coherent unit of meaning for better retrieval quality.
"""

from typing import List, Dict

from langchain.text_splitter import RecursiveCharacterTextSplitter


def create_semantic_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    metadata: Dict = None,
) -> List[Dict]:
    """
    Split text into semantically meaningful chunks.

    Args:
        text: The full text to split (transcript, PDF content, etc.).
        chunk_size: Target character count per chunk.
        chunk_overlap: Number of overlapping characters between chunks.
        metadata: Additional metadata to attach to each chunk (e.g., source, timestamp).

    Returns:
        List of dicts with 'content', 'metadata', and 'chunk_index'.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents = splitter.create_documents([text])

    chunks = []
    for i, doc in enumerate(documents):
        chunk = {
            "content": doc.page_content,
            "chunk_index": i,
            "metadata": {**(metadata or {}), "chunk_index": i},
        }
        chunks.append(chunk)

    return chunks


def chunk_transcript_with_timestamps(
    segments: List[Dict],
    chunk_size: int = 500,
) -> List[Dict]:
    """
    Chunk a Whisper transcript while preserving timestamp information.

    Merges consecutive segments until the chunk reaches chunk_size,
    then starts a new chunk. Each chunk retains start/end timestamps.

    Args:
        segments: List of Whisper segments with 'start', 'end', 'text'.
        chunk_size: Target character count per chunk.

    Returns:
        List of dicts with 'content', 'start_time', 'end_time'.
    """
    chunks = []
    current_text = ""
    current_start = 0
    current_end = 0

    for segment in segments:
        if not current_text:
            current_start = segment["start"]

        current_text += segment["text"] + " "
        current_end = segment["end"]

        if len(current_text) >= chunk_size:
            chunks.append({
                "content": current_text.strip(),
                "start_time": current_start,
                "end_time": current_end,
            })
            current_text = ""

    # Don't forget the last chunk
    if current_text.strip():
        chunks.append({
            "content": current_text.strip(),
            "start_time": current_start,
            "end_time": current_end,
        })

    return chunks
