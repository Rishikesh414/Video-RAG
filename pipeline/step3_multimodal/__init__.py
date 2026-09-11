"""
Step 3: Targeted Multimodal Analysis.

Runs on each query AFTER Step 2 has identified the exact timestamp window.
Cuts the specific clip from the source video and sends only that short
segment to an expensive Multimodal LLM (Gemini 1.5 Pro / GPT-4o) for
deep visual analysis.

Output: (1) Text answer, (2) Video clip file, (3) Timestamps
"""
