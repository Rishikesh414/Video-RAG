"""
VideoRAG Orchestrator — master controller for the 3-step hybrid pipeline.

Coordinates the entire flow:
    Step 1 (on upload):  Index video → transcript + OCR + visual description
                         + visual tags + scenes → enriched metadata → Qdrant
    Step 2 (on query):   Semantic search → timestamp resolution
    Step 3 (on query):   Clip extraction → multimodal LLM analysis → 3-part response

Education-domain enhancements in Step 1:
    - EasyOCR extracts slide/whiteboard text per scene keyframe
    - Gemini Flash generates 2-3 sentence visual descriptions per scene
    - Processing tracker reports pipeline stage progress via JSON status files
"""

import logging
from pathlib import Path
from typing import Dict

from pipeline.step1_indexing.audio_extractor import extract_audio
from pipeline.step1_indexing.transcriber import transcribe_audio, save_transcript
from pipeline.step1_indexing.visual_tagger import VisualTagger
from pipeline.step1_indexing.scene_detector import detect_scenes
from pipeline.step1_indexing.ocr_extractor import OCRExtractor
from pipeline.step1_indexing.visual_describer import VisualDescriber
from pipeline.step1_indexing.processing_tracker import ProcessingTracker
from pipeline.step1_indexing.metadata_builder import (
    build_metadata, save_metadata, metadata_to_searchable_chunks,
)

from pipeline.step2_retrieval.text_embedder import TextEmbedder
from pipeline.step2_retrieval.vector_store import VectorStore
from pipeline.step2_retrieval.semantic_search import SemanticSearch
from pipeline.step2_retrieval.timestamp_resolver import TimestampResolver, get_standard_llm

from pipeline.step3_multimodal.clip_extractor import extract_clip, get_clip_url
from pipeline.step3_multimodal.multimodal_llm import MultimodalLLM
from pipeline.step3_multimodal.response_builder import build_response

logger = logging.getLogger(__name__)


class VideoRAGOrchestrator:
    """
    Master orchestrator for the VideoRAG hybrid pipeline.

    Usage:
        orchestrator = VideoRAGOrchestrator(config)

        # On video upload (Step 1):
        orchestrator.index_video(video_path, video_id)

        # On student query (Steps 2 + 3):
        result = orchestrator.query(question)
    """

    def __init__(self, config: Dict):
        """
        Initialize the orchestrator with configuration.

        Args:
            config: Dict with keys matching the backend Settings fields.
        """
        self.config = config

        # Step 1 components
        self.visual_tagger = VisualTagger(
            model_name=config.get("VISUAL_TAGGER_MODEL", "yolov8n.pt")
        )

        # OCR extractor (EasyOCR)
        ocr_enabled = str(config.get("OCR_ENABLED", "true")).lower() == "true"
        ocr_langs = config.get("OCR_LANGUAGES", ["en"])
        if isinstance(ocr_langs, str):
            ocr_langs = [lang.strip() for lang in ocr_langs.split(",")]

        self.ocr_extractor = OCRExtractor(
            languages=ocr_langs,
            gpu=False,
        ) if ocr_enabled else None

        # VLM visual describer — default: Ollama local model
        vlm_provider = config.get("VLM_DESCRIBER_PROVIDER", "ollama")
        vlm_model = config.get("VLM_DESCRIBER_MODEL", "llama3.2-vision:11b")
        vlm_api_key = config.get("GOOGLE_API_KEY", "") or config.get("OPENAI_API_KEY", "")
        ollama_base_url = config.get("OLLAMA_BASE_URL", "http://localhost:11434")

        self.visual_describer = VisualDescriber(
            provider=vlm_provider,
            api_key=vlm_api_key,
            model=vlm_model,
            ollama_base_url=ollama_base_url,
        )

        # Processing tracker
        processing_status_dir = config.get("PROCESSING_STATUS_DIR", "./data/processing")
        self.tracker = ProcessingTracker(status_dir=processing_status_dir)

        # Step 2 components
        self.embedder = TextEmbedder(
            model_name=config.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        )
        self.vector_store = VectorStore(
            embedding_dim=self.embedder.embedding_dim,
            host=config.get("QDRANT_HOST", "localhost"),
            port=int(config.get("QDRANT_PORT", 6333)),
            collection_name=config.get("QDRANT_COLLECTION", "videorag_chunks"),
            url=config.get("QDRANT_URL"),
            api_key=config.get("QDRANT_API_KEY"),
            path=config.get("QDRANT_PATH"),
        )
        self.semantic_search = SemanticSearch(self.embedder, self.vector_store)

        # Step 2: Timestamp resolver — default: Ollama qwen2.5:7b
        standard_llm = get_standard_llm(
            provider=config.get("STANDARD_LLM_PROVIDER", "ollama"),
            model=config.get("STANDARD_LLM_MODEL", "qwen2.5:7b"),
            base_url=ollama_base_url,
            model_path=config.get("LLAMA_MODEL_PATH", ""),
        )
        self.timestamp_resolver = TimestampResolver(llm=standard_llm)

        # Step 3: Multimodal LLM — default: Ollama llama3.2-vision:11b
        self.multimodal_llm = MultimodalLLM(
            provider=config.get("MULTIMODAL_LLM_PROVIDER", "ollama"),
            api_key=config.get("GOOGLE_API_KEY", "") or config.get("OPENAI_API_KEY", ""),
            model=config.get("MULTIMODAL_LLM_MODEL", "llama3.2-vision:11b"),
            ollama_base_url=ollama_base_url,
        )

        # Directories
        self.audio_dir = config.get("AUDIO_DIR", "./data/audio")
        self.transcripts_dir = config.get("TRANSCRIPTS_DIR", "./data/transcripts")
        self.visual_tags_dir = config.get("VISUAL_TAGS_DIR", "./data/visual_tags")
        self.metadata_dir = config.get("METADATA_DIR", "./data/metadata")
        self.clips_dir = config.get("CLIP_OUTPUT_DIR", "./data/clips")
        self.scene_descriptions_dir = config.get(
            "SCENE_DESCRIPTIONS_DIR", "./data/scene_descriptions"
        )

    # ─── Step 1: Index Video (runs on upload) ────────────────────────

    def index_video(self, video_path: str, video_id: str, extra: Dict = None) -> Dict:
        """
        Process a newly uploaded video through Step 1: Rich Indexing.

        Extracts and indexes:
        1. Audio → Whisper transcript (timestamped segments)
        2. Scene boundaries → PySceneDetect
        3. OCR text → EasyOCR per scene keyframe (slides, whiteboards)
        4. Visual descriptions → Gemini Flash per scene keyframe
        5. Visual tags → YOLO object detection on sampled frames
        6. Unified enriched metadata → Qdrant embeddings

        Args:
            video_path: Path to the uploaded video file.
            video_id: Unique video identifier.
            extra: Additional metadata (uploader, module, etc.).

        Returns:
            Dict with indexing results and stats.
        """
        filename = extra.get("original_filename", video_id) if extra else video_id

        # Initialize processing tracker
        self.tracker.initialize(video_id=video_id, filename=filename)

        try:
            # ── 1a. Extract audio ─────────────────────────────────────
            self.tracker.update(video_id, "audio_extraction", "Extracting audio track...")
            audio_path = extract_audio(
                video_path,
                output_path=str(Path(self.audio_dir) / f"{video_id}.wav"),
            )
            logger.info(f"[{video_id[:8]}] Audio extracted: {audio_path}")

            # ── 1b. Transcribe audio (Whisper) ────────────────────────
            self.tracker.update(video_id, "transcription", "Transcribing with Whisper...")
            transcript = transcribe_audio(
                audio_path,
                model_name=self.config.get("WHISPER_MODEL", "large-v3"),
            )
            save_transcript(
                transcript,
                str(Path(self.transcripts_dir) / f"{video_id}.json"),
            )
            segment_count = len(transcript.get("segments", []))
            logger.info(f"[{video_id[:8]}] Transcription done: {segment_count} segments")

            # ── 1c. Scene detection ───────────────────────────────────
            self.tracker.update(video_id, "scene_detection", "Detecting scene boundaries...")
            scenes = detect_scenes(video_path)
            logger.info(f"[{video_id[:8]}] Scene detection done: {len(scenes)} scenes")

            # ── 1d. OCR extraction (per scene keyframe) ───────────────
            ocr_results = []
            if self.ocr_extractor and scenes:
                self.tracker.update(
                    video_id, "ocr",
                    f"Extracting text from {len(scenes)} scene keyframes via OCR..."
                )
                ocr_results = self.ocr_extractor.extract_from_scenes(
                    video_path=video_path,
                    scenes=scenes,
                )
                ocr_hits = sum(1 for r in ocr_results if r.get("word_count", 0) > 0)
                logger.info(
                    f"[{video_id[:8]}] OCR done: {ocr_hits}/{len(scenes)} scenes had text"
                )
                self.tracker.update(
                    video_id, "ocr",
                    f"OCR complete — {ocr_hits} scenes with slide/screen text",
                    stats={"ocr_scenes_with_text": ocr_hits},
                )

            # ── 1e. Visual descriptions (VLM per scene) ───────────────
            scene_descriptions = []
            if scenes:
                self.tracker.update(
                    video_id, "visual_description",
                    f"Generating visual descriptions for {len(scenes)} scenes..."
                )
                scene_descriptions = self.visual_describer.describe_scenes(
                    video_path=video_path,
                    scenes=scenes,
                )
                desc_count = sum(1 for d in scene_descriptions if d.get("description"))
                logger.info(
                    f"[{video_id[:8]}] Visual descriptions: {desc_count}/{len(scenes)} scenes"
                )
                self.tracker.update(
                    video_id, "visual_description",
                    f"Visual descriptions complete — {desc_count} scenes described",
                    stats={"scenes_described": desc_count},
                )

                # Optionally save scene descriptions to disk
                self._save_scene_descriptions(video_id, scene_descriptions)

            # ── 1f. YOLO visual tagging ───────────────────────────────
            self.tracker.update(video_id, "yolo_tagging", "Running YOLO visual tagging...")
            visual_tags = self.visual_tagger.tag_video(video_path)
            self.visual_tagger.save_tags(
                visual_tags,
                str(Path(self.visual_tags_dir) / f"{video_id}.json"),
            )
            logger.info(f"[{video_id[:8]}] YOLO tagging done: {len(visual_tags)} tag frames")

            # ── 1g. Build enriched unified metadata ───────────────────
            self.tracker.update(video_id, "indexing", "Building metadata and indexing...")
            metadata = build_metadata(
                video_id=video_id,
                video_path=video_path,
                transcript=transcript,
                visual_tags=visual_tags,
                scenes=scenes,
                extra=extra,
                ocr_results=ocr_results,
                scene_descriptions=scene_descriptions,
            )
            save_metadata(
                metadata,
                str(Path(self.metadata_dir) / f"{video_id}.json"),
            )

            # ── 1h. Chunk and embed metadata into Qdrant ──────────────
            chunks = metadata_to_searchable_chunks(metadata)
            if chunks:
                texts = [c["content"] for c in chunks]
                embeddings = self.embedder.embed_texts(texts)
                self.vector_store.add_embeddings(embeddings, chunks)

            total_vectors = self.vector_store.total_vectors
            logger.info(
                f"[{video_id[:8]}] Indexing done: {len(chunks)} chunks → Qdrant "
                f"(total vectors: {total_vectors})"
            )

            # Mark complete
            final_stats = {
                "transcript_segments": segment_count,
                "scenes": len(scenes),
                "visual_tags": len(visual_tags),
                "ocr_scenes_with_text": sum(
                    1 for r in ocr_results if r.get("word_count", 0) > 0
                ),
                "scenes_described": sum(
                    1 for d in scene_descriptions if d.get("description")
                ),
                "chunks_indexed": len(chunks),
                "total_vectors": total_vectors,
            }
            self.tracker.mark_done(video_id, stats=final_stats)

            return {"video_id": video_id, **final_stats}

        except Exception as e:
            logger.error(f"[{video_id[:8]}] Indexing FAILED: {e}", exc_info=True)
            self.tracker.mark_failed(video_id, error=str(e))
            raise

    def _save_scene_descriptions(self, video_id: str, descriptions: list) -> None:
        """Save scene descriptions to disk as JSON."""
        import json
        output_dir = Path(self.scene_descriptions_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{video_id}_scenes.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(descriptions, f, indent=2, ensure_ascii=False)

    # ─── Steps 2 + 3: Query (runs on each question) ─────────────────

    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Process a user question through Steps 2 and 3.

        Step 2: Semantic retrieval → timestamp resolution (cheap, text-only)
        Step 3: Clip extraction → multimodal LLM analysis (expensive, targeted)

        Args:
            question: The user's natural language question.
            top_k: Number of chunks to retrieve from Qdrant.

        Returns:
            3-part response dict with 'answer', 'video_clip', 'timestamp', 'sources'.
        """
        # ── Step 2: Semantic Retrieval ───────────────────────────────

        # 2a. Search Qdrant for relevant metadata chunks
        search_results = self.semantic_search.search(question, top_k=top_k)

        if not search_results:
            return build_response(
                answer_text="No relevant video content found for your question.",
                clip_info={},
                timestamp_info={"confidence": "low", "reasoning": "No search results"},
                search_results=[],
            )

        # 2b. Format context and resolve exact timestamps
        context_text = self.semantic_search.format_context(search_results)
        timestamp_info = self.timestamp_resolver.resolve(
            question=question,
            search_results=search_results,
            context_text=context_text,
        )

        # ── Step 3: Targeted Multimodal Analysis ─────────────────────

        # 3a. Extract the video clip at the resolved timestamps
        video_path = timestamp_info.get("video_path", "")
        start = timestamp_info.get("start_time", 0)
        end = timestamp_info.get("end_time", 0)

        # Apply minimum clip duration
        min_duration = self.config.get("CLIP_DURATION_SECONDS", 30)
        if (end - start) < min_duration:
            midpoint = (start + end) / 2
            start = max(0, midpoint - min_duration / 2)
            end = midpoint + min_duration / 2

        clip_info = extract_clip(
            video_path=video_path,
            start_time=start,
            end_time=end,
            output_dir=self.clips_dir,
        )

        # Add serving URL
        clip_info["clip_url"] = get_clip_url(clip_info["clip_filename"])

        # 3b. Get transcript context for the clip window
        clip_transcript = self._get_transcript_for_window(
            search_results, start, end
        )

        # 3c. Send clip to Multimodal LLM for deep analysis
        answer_text = self.multimodal_llm.analyze_clip(
            clip_path=clip_info["clip_path"],
            question=question,
            transcript_context=clip_transcript,
        )

        # 3d. Build the 3-part response
        return build_response(
            answer_text=answer_text,
            clip_info=clip_info,
            timestamp_info=timestamp_info,
            search_results=search_results,
        )

    def get_processing_status(self, video_id: str) -> dict:
        """
        Get the current processing status for a video.

        Args:
            video_id: The video's unique ID.

        Returns:
            Status dict with stage, progress_pct, message, and stats.
            Returns {'stage': 'unknown'} if no status file exists.
        """
        status = self.tracker.get_status(video_id)
        if status is None:
            return {"video_id": video_id, "stage": "unknown", "progress_pct": 0}
        return status

    def _get_transcript_for_window(
        self, search_results: list, start: float, end: float
    ) -> str:
        """Extract transcript text that falls within the clip window."""
        relevant_texts = []
        for r in search_results:
            r_start = r.get("start_time", 0)
            r_end = r.get("end_time", 0)
            # Check for overlap
            if r_start <= end and r_end >= start:
                relevant_texts.append(r.get("content", ""))
        return " ".join(relevant_texts)
