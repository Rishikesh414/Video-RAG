"""
Step 1: Rich Indexing & Extraction (Education Domain).

Runs on video upload. Strips each video into lightweight text-based metadata:
- ASR transcript (Whisper) — timestamped speech-to-text
- Visual object tags with timestamps (YOLOv8-nano)
- Scene boundaries (PySceneDetect)
- OCR text from scene keyframes (EasyOCR) — slides, whiteboards, equations
- VLM visual descriptions per scene (Gemini Flash) — educational context

All output is a few kilobytes of text — orders of magnitude cheaper
than storing or processing raw video frames.
"""
