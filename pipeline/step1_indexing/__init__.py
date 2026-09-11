"""
Step 1: Low-Cost Indexing & Extraction.

Runs on video upload. Strips each video into lightweight text-based metadata:
- ASR transcript (Whisper)
- Visual object tags with timestamps (lightweight CV model)
- Scene boundaries (PySceneDetect)

All output is a few kilobytes of text — orders of magnitude cheaper
than storing or processing raw video frames.
"""
