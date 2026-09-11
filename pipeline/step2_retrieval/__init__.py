"""
Step 2: Semantic Retrieval.

Runs on each user query. Scans only the text metadata from Step 1
to find the most relevant video segments:
- Embeds the query and searches Qdrant for matching chunks
- Uses a standard LLM to pinpoint exact timestamps

Speed: Milliseconds — only reading and reasoning over text.
"""
