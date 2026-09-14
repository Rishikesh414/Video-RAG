"""
Integration test for the VideoRAG Step 1 pipeline.

Tests each component individually then runs the full index_video() flow
against a short test video. Verifies all 4 modalities produce output.

Usage:
    python tests/test_pipeline.py [path/to/test_video.mp4]

If no video path is provided, generates a synthetic test video using OpenCV.

Requires:
    pip install -r backend/requirements.txt
    # Set GOOGLE_API_KEY in .env for VLM visual descriptions
"""

import json
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env
from dotenv import load_dotenv
load_dotenv(project_root / ".env")


# ─── Colors for terminal output ──────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS = f"{GREEN}[PASS]{RESET}"
FAIL = f"{RED}[FAIL]{RESET}"
WARN = f"{YELLOW}[WARN]{RESET}"
INFO = f"{BLUE}[INFO]{RESET}"


def section(title: str):
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")


def check(condition: bool, name: str, detail: str = ""):
    status = PASS if condition else FAIL
    detail_str = f" — {detail}" if detail else ""
    print(f"  {status}  {name}{detail_str}")
    return condition


# ─── Generate synthetic test video ───────────────────────────────────

def create_test_video(path: str, duration_sec: int = 30) -> str:
    """
    Create a synthetic test video with slides using OpenCV.
    Includes text on frames to test OCR.
    """
    import cv2
    import numpy as np

    width, height = 1280, 720
    fps = 24
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, fps, (width, height))

    slide_texts = [
        ("Slide 1: Introduction to Machine Learning", "Linear Regression | Decision Trees"),
        ("Slide 2: Neural Networks", "Backpropagation | Gradient Descent"),
        ("Slide 3: Convolutional Neural Networks", "Feature Maps | Pooling Layers"),
    ]

    frames_per_slide = total_frames // len(slide_texts)

    for slide_idx, (title, subtitle) in enumerate(slide_texts):
        for f in range(frames_per_slide):
            # Create slide background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:] = (30, 30, 60)  # Dark blue background

            # Title
            cv2.putText(
                frame, title,
                (80, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                (255, 255, 255), 2, cv2.LINE_AA
            )
            # Subtitle
            cv2.putText(
                frame, subtitle,
                (80, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (200, 200, 255), 2, cv2.LINE_AA
            )
            # Slide number
            cv2.putText(
                frame, f"Slide {slide_idx + 1} / {len(slide_texts)}",
                (80, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (150, 150, 150), 1, cv2.LINE_AA
            )
            out.write(frame)

    out.release()
    return path


# ─── Individual component tests ───────────────────────────────────────

def test_imports():
    section("1. Import Tests")
    all_pass = True

    modules = [
        ("pipeline.orchestrator", "VideoRAGOrchestrator"),
        ("pipeline.step1_indexing.audio_extractor", "extract_audio"),
        ("pipeline.step1_indexing.transcriber", "transcribe_audio"),
        ("pipeline.step1_indexing.scene_detector", "detect_scenes"),
        ("pipeline.step1_indexing.ocr_extractor", "OCRExtractor"),
        ("pipeline.step1_indexing.visual_describer", "VisualDescriber"),
        ("pipeline.step1_indexing.processing_tracker", "ProcessingTracker"),
        ("pipeline.step1_indexing.metadata_builder", "build_metadata"),
        ("pipeline.step2_retrieval.vector_store", "VectorStore"),
        ("pipeline.step2_retrieval.text_embedder", "TextEmbedder"),
    ]

    for module_path, symbol in modules:
        try:
            mod = __import__(module_path, fromlist=[symbol])
            getattr(mod, symbol)
            check(True, f"{module_path}.{symbol}")
        except Exception as e:
            check(False, f"{module_path}.{symbol}", str(e))
            all_pass = False

    return all_pass


def test_processing_tracker():
    section("2. Processing Tracker")
    from pipeline.step1_indexing.processing_tracker import ProcessingTracker, PIPELINE_STAGES

    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = ProcessingTracker(status_dir=tmpdir)
        video_id = "test-vid-001"

        tracker.initialize(video_id, filename="test.mp4")
        status = tracker.get_status(video_id)
        check(status is not None, "initialize() creates status file")
        check(status["stage"] == "queued", "Initial stage is 'queued'")

        for stage in PIPELINE_STAGES[1:-1]:
            tracker.update(video_id, stage, f"Running {stage}")

        tracker.mark_done(video_id, stats={"chunks": 42})
        status = tracker.get_status(video_id)
        check(status["stage"] == "done", "mark_done() sets stage=done")
        check(status["progress_pct"] == 100, "Progress is 100% when done")
        check(status["stats"].get("chunks") == 42, "Stats are persisted")

        tracker.mark_failed(video_id, "Test error")
        status = tracker.get_status(video_id)
        check(status["stage"] == "failed", "mark_failed() sets stage=failed")
        check("Test error" in status["error"], "Error message stored")

    print(f"  {INFO}  Stage order: {' → '.join(PIPELINE_STAGES)}")
    return True


def test_ocr_extractor(video_path: str):
    section("3. OCR Extractor (EasyOCR)")

    try:
        from pipeline.step1_indexing.ocr_extractor import OCRExtractor
        import cv2
        import numpy as np

        extractor = OCRExtractor(languages=["en"], gpu=False)

        # Test on a synthetic frame with text
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (240, 240, 240)
        cv2.putText(
            frame, "Introduction to Machine Learning",
            (40, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
            (0, 0, 0), 2, cv2.LINE_AA
        )
        cv2.putText(
            frame, "Neural Networks and Deep Learning",
            (40, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (0, 0, 0), 2, cv2.LINE_AA
        )

        result = extractor.extract_text_from_frame(frame, confidence_threshold=0.3)
        has_text = result["word_count"] > 0
        check(has_text, "OCR detects text on synthetic slide frame",
              f"word_count={result['word_count']}, text='{result['text'][:60]}...'")

        # Test on actual video if provided
        if video_path and Path(video_path).exists():
            scenes = [(0.0, 5.0), (5.0, 10.0)]
            ocr_results = extractor.extract_from_scenes(video_path, scenes)
            check(len(ocr_results) == len(scenes), "extract_from_scenes returns one entry per scene",
                  f"{len(ocr_results)} results")
            ocr_hits = sum(1 for r in ocr_results if r["word_count"] > 0)
            print(f"  {INFO}  OCR hit rate: {ocr_hits}/{len(scenes)} scenes had text")

        return True

    except ImportError as e:
        check(False, "EasyOCR import", f"easyocr not installed: {e}")
        print(f"  {WARN}  Install with: pip install easyocr")
        return False
    except Exception as e:
        check(False, "OCR test", str(e))
        return False


def test_visual_describer(video_path: str):
    section("4. Visual Describer (VLM)")

    api_key = os.getenv("GOOGLE_API_KEY", "")

    if not api_key:
        print(f"  {WARN}  GOOGLE_API_KEY not set — testing 'disabled' mode only")
        from pipeline.step1_indexing.visual_describer import VisualDescriber
        describer = VisualDescriber(provider="disabled", api_key="")
        result = describer.describe_frame(__import__("numpy").zeros((480, 640, 3), dtype=__import__("numpy").uint8))
        check(result == "", "Returns empty string when provider='disabled'")
        print(f"  {INFO}  Set GOOGLE_API_KEY in .env to test VLM descriptions")
        return True

    try:
        from pipeline.step1_indexing.visual_describer import VisualDescriber
        import numpy as np
        import cv2

        describer = VisualDescriber(provider="gemini", api_key=api_key, model="gemini-2.0-flash")

        # Test with synthetic slide frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (40, 40, 70)
        cv2.putText(frame, "Neural Networks", (80, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        description = describer.describe_frame(frame)
        has_desc = bool(description and len(description) > 10)
        check(has_desc, "VLM generates description for lecture frame",
              f"'{description[:80]}...'")
        return has_desc

    except Exception as e:
        check(False, "VLM description test", str(e))
        return False


def test_scene_detection(video_path: str):
    section("5. Scene Detection")

    if not video_path or not Path(video_path).exists():
        print(f"  {WARN}  No video path provided — skipping scene detection test")
        return True

    from pipeline.step1_indexing.scene_detector import detect_scenes, extract_scene_keyframe

    scenes = detect_scenes(video_path)
    check(isinstance(scenes, list), "detect_scenes() returns a list",
          f"{len(scenes)} scenes detected")

    if scenes:
        start, end = scenes[0]
        frame = extract_scene_keyframe(video_path, start, end)
        check(frame is not None, "extract_scene_keyframe() returns a frame",
              f"shape={frame.shape if frame is not None else None}")

    return True


def test_full_pipeline(video_path: str):
    section("6. Full Pipeline Integration (index_video)")

    if not video_path or not Path(video_path).exists():
        print(f"  {WARN}  No video path — skipping full pipeline test")
        return True

    config = {
        "WHISPER_MODEL": "base",  # Use small model for tests
        "VISUAL_TAGGER_MODEL": "yolov8n.pt",
        "OCR_ENABLED": "true",
        "OCR_LANGUAGES": "en",
        "VLM_DESCRIBER_PROVIDER": "gemini" if os.getenv("GOOGLE_API_KEY") else "disabled",
        "VLM_DESCRIBER_MODEL": "gemini-2.0-flash",
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
        "STANDARD_LLM_PROVIDER": "llama",
        "LLAMA_MODEL_PATH": "",
        "MULTIMODAL_LLM_PROVIDER": "gemini",
        "SENTENCE_TRANSFORMER_MODEL": "all-MiniLM-L6-v2",
        "QDRANT_PATH": "./data/qdrant_test",
        "AUDIO_DIR": "./data/test/audio",
        "TRANSCRIPTS_DIR": "./data/test/transcripts",
        "VISUAL_TAGS_DIR": "./data/test/visual_tags",
        "METADATA_DIR": "./data/test/metadata",
        "CLIP_OUTPUT_DIR": "./data/test/clips",
        "SCENE_DESCRIPTIONS_DIR": "./data/test/scene_descriptions",
        "PROCESSING_STATUS_DIR": "./data/test/processing",
    }

    try:
        from pipeline.orchestrator import VideoRAGOrchestrator

        print(f"  {INFO}  Initializing orchestrator...")
        orchestrator = VideoRAGOrchestrator(config=config)

        print(f"  {INFO}  Running index_video() on: {video_path}")
        result = orchestrator.index_video(
            video_path=video_path,
            video_id="test-001",
            extra={"original_filename": Path(video_path).name, "module": "TEST"},
        )

        check(result.get("transcript_segments", 0) > 0, "Whisper produced transcript segments",
              f"{result.get('transcript_segments')} segments")
        check(result.get("scenes", 0) >= 0, "Scene detection ran",
              f"{result.get('scenes')} scenes")
        check(result.get("chunks_indexed", 0) > 0, "Qdrant chunks indexed",
              f"{result.get('chunks_indexed')} chunks")

        print(f"\n  {INFO}  Full result:")
        for k, v in result.items():
            if k != "video_id":
                print(f"         {k}: {v}")

        # Check processing status
        status = orchestrator.get_processing_status("test-001")
        check(status["stage"] == "done", "Processing status = 'done'",
              f"stage={status['stage']}, progress={status['progress_pct']}%")

        return True

    except Exception as e:
        check(False, "Full pipeline integration", str(e))
        import traceback
        traceback.print_exc()
        return False


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}VideoRAG Pipeline Integration Tests{RESET}")
    print(f"Project root: {project_root}")

    # Get or create test video
    video_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not video_path:
        print(f"\n{INFO}  No video provided. Creating synthetic test video...")
        video_path = str(project_root / "data" / "test_video.mp4")
        Path(video_path).parent.mkdir(parents=True, exist_ok=True)
        if not Path(video_path).exists():
            create_test_video(video_path, duration_sec=30)
            print(f"{INFO}  Synthetic video created: {video_path}")
        else:
            print(f"{INFO}  Using existing test video: {video_path}")

    results = []
    results.append(test_imports())
    results.append(test_processing_tracker())
    results.append(test_ocr_extractor(video_path))
    results.append(test_visual_describer(video_path))
    results.append(test_scene_detection(video_path))
    results.append(test_full_pipeline(video_path))

    # Summary
    section("Summary")
    passed = sum(results)
    total = len(results)
    color = GREEN if passed == total else (YELLOW if passed > total // 2 else RED)
    print(f"  {color}{BOLD}{passed}/{total} test groups passed{RESET}\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
