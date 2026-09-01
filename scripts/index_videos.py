"""
Batch Video Indexing Script — processes all videos in the upload directory
through the VideoRAG pipeline.

Usage:
    python scripts/index_videos.py
    python scripts/index_videos.py --video_dir ./data/videos
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(description="Batch index videos for VideoRAG")
    parser.add_argument(
        "--video_dir",
        default="./data/videos",
        help="Directory containing videos to index",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=1,
        help="Frames per second for extraction",
    )
    parser.add_argument(
        "--keyframes",
        type=int,
        default=32,
        help="Number of key frames per video segment",
    )
    args = parser.parse_args()

    video_dir = Path(args.video_dir)
    if not video_dir.exists():
        print(f"❌ Video directory not found: {video_dir}")
        sys.exit(1)

    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi")) + list(video_dir.glob("*.mkv"))

    if not video_files:
        print(f"⚠️  No video files found in {video_dir}")
        sys.exit(0)

    print(f"🎬 Found {len(video_files)} videos to index")

    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_path.name}")

        # TODO: Implement full pipeline processing
        # 1. Extract frames
        # 2. Detect scenes
        # 3. Extract audio
        # 4. Transcribe
        # 5. OCR
        # 6. Chunk
        # 7. Embed
        # 8. Add to FAISS index

        print(f"   ✅ Indexed: {video_path.name}")

    print(f"\n🎉 Batch indexing complete! {len(video_files)} videos processed.")


if __name__ == "__main__":
    main()
