# VideoRAG Architecture — 3-Step Hybrid Approach

## The Problem

Multimodal LLMs are powerful but extremely expensive when processing raw video. Sending a full 1-hour lecture video to Gemini 1.5 Pro costs thousands of tokens and takes minutes.

## The Solution: Hybrid Architecture

Instead of feeding entire videos to an expensive Multimodal LLM, we use a **3-step filter**:

1. **Index cheap text metadata** on upload (kilobytes, not gigabytes)
2. **Search text** to find the exact timestamps (milliseconds)
3. **Send only the short clip** to the Multimodal LLM (seconds, not minutes)

Think of it like library research: you don't read every page of 1,000 books — you look at the index first, then read only the 3 relevant pages.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                                │
│  ┌────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  Login Page     │    │ Student Dashboard │    │ Faculty Dashboard │  │
│  │                 │    │ Chat + ClipViewer │    │ Upload            │  │
│  └────────────────┘    └──────────────────┘    └──────────────────┘  │
│                         React.js + Vite                              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼───────────────────────────────────────┐
│                     BACKEND (FastAPI)                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Auth    │  │  Upload  │  │  Query   │  │  Chat    │            │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │            │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └──────────┘            │
│                      │              │                                │
└──────────────────────┼──────────────┼────────────────────────────────┘
                       │              │
    ┌──────────────────▼──┐  ┌────────▼─────────────────────────────┐
    │   STEP 1 (Upload)   │  │   STEPS 2 + 3 (Query)               │
    │   Low-Cost Indexing  │  │   Retrieval + Multimodal Analysis   │
    └──────────────────────┘  └────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

    ╔═══════════════════════════════════════════════════════════════╗
    ║                STEP 1: LOW-COST INDEXING                     ║
    ║                (Runs on video upload)                         ║
    ║                                                               ║
    ║   Video → ┬─ FFmpeg ──→ Audio ──→ Whisper ASR ──→ Transcript ║
    ║           ├─ YOLO ────────────────────────────→ Visual Tags   ║
    ║           └─ PySceneDetect ───────────────────→ Scene Bounds  ║
    ║                                                               ║
    ║   Transcript + Tags + Scenes → Metadata Builder → Qdrant     ║
    ║                                                               ║
    ║   Cost: 💚 Extremely cheap (KB of text, not GB of video)      ║
    ╚═══════════════════════════════════════════════════════════════╝
                               │
                               ▼
    ╔═══════════════════════════════════════════════════════════════╗
    ║                STEP 2: SEMANTIC RETRIEVAL                    ║
    ║                (Runs on each user query)                      ║
    ║                                                               ║
    ║   Question → Text Embedder → Qdrant Search → Top-K Chunks    ║
    ║                                     │                         ║
    ║   Top-K Chunks → Standard LLM → Exact Timestamps             ║
    ║                  (cheap!)       "04:15 – 04:45"               ║
    ║                                                               ║
    ║   Cost: 💚 Milliseconds (only reading text metadata)          ║
    ╚═══════════════════════════════════════════════════════════════╝
                               │
                               ▼
    ╔═══════════════════════════════════════════════════════════════╗
    ║                STEP 3: TARGETED MULTIMODAL ANALYSIS          ║
    ║                (Only on the short clip!)                      ║
    ║                                                               ║
    ║   Timestamps → FFmpeg Clip Extract → 30-second clip          ║
    ║                                          │                    ║
    ║   Clip → Gemini 1.5 Pro / GPT-4o → Deep Visual Analysis     ║
    ║                                          │                    ║
    ║   Output: ┬─ (1) Text Answer                                  ║
    ║           ├─ (2) Video Clip File (download/stream)            ║
    ║           └─ (3) Timestamps (04:15 – 04:45)                   ║
    ║                                                               ║
    ║   Cost: 🟡 Moderate (but only 30s of video, not 1 hour!)     ║
    ╚═══════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                       DATA STORES                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐       │
│  │  PostgreSQL    │  │  Qdrant Store  │  │  File System     │       │
│  │  (Users,       │  │  (Text meta-   │  │  ./data/         │       │
│  │   Uploads,     │  │   data vectors)│  │  ├── videos/     │       │
│  │   Chat)        │  │               │  │  ├── audio/      │       │
│  └────────────────┘  └────────────────┘  │  ├── transcripts/│       │
│                                           │  ├── visual_tags/│       │
│                                           │  ├── clips/      │       │
│                                           │  └── metadata/   │       │
│                                           └──────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

## Cost Comparison

| Approach | What's processed | Cost | Speed |
|----------|-----------------|------|-------|
| **Naive Multimodal** | Full 1-hour video → Multimodal LLM | 💸💸💸 $$$  | ⏱ Minutes |
| **Hybrid (this system)** | 30-second clip → Multimodal LLM | 💚 ~10x cheaper | ⚡ Seconds |

## Output Format

Every query returns **3 outputs**:

| # | Output | Description |
|---|--------|-------------|
| 1 | **Text Answer** | Detailed, evidence-based response with confidence level |
| 2 | **Video Clip** | The exact clip (MP4) used as evidence — playable and downloadable |
| 3 | **Timestamp** | Start/end times in the source video (e.g., `04:15 – 04:45`) |
