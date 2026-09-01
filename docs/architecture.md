# VideoRAG Architecture

## System Overview

VideoRAG is a **Retrieval-Augmented Generation** framework for intelligent video question answering. It processes lecture videos to enable students to ask natural language questions and receive evidence-based answers with source video timestamps.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                                │
│  ┌────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  Login Page     │    │ Student Dashboard │    │ Faculty Dashboard │  │
│  │  (Auth)         │    │ (Chat + Video)    │    │ (Upload)          │  │
│  └────────────────┘    └──────────────────┘    └──────────────────┘  │
│                         React.js + Vite                              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼───────────────────────────────────────┐
│                        BACKEND (FastAPI)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Auth    │  │  Upload  │  │  Query   │  │  Chat    │            │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │              │              │              │                  │
│  ┌────▼──────────────▼──────────────▼──────────────▼─────┐          │
│  │                   Services Layer                       │          │
│  └───────────────────────┬───────────────────────────────┘          │
└──────────────────────────┼───────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────────┐
│                    VIDEORAG PIPELINE                                  │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐                  │
│  │   Video     │  │    Audio     │  │    OCR     │                  │
│  │ Processing  │  │  Processing  │  │ Extraction │                  │
│  │ (OpenCV,    │  │ (FFmpeg,     │  │ (EasyOCR)  │                  │
│  │ PyScene,    │  │  Whisper)    │  │            │                  │
│  │  K-Means)   │  │              │  │            │                  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘                  │
│         │                │                 │                         │
│  ┌──────▼────────────────▼─────────────────▼──────┐                 │
│  │              Semantic Chunking                  │                 │
│  └──────────────────────┬─────────────────────────┘                 │
│                         │                                            │
│  ┌──────────────────────▼─────────────────────────┐                 │
│  │           Embedding Generation                  │                 │
│  │     (Qwen3 / Sentence Transformers)             │                 │
│  └──────────────────────┬─────────────────────────┘                 │
│                         │                                            │
│  ┌──────────────────────▼─────────────────────────┐                 │
│  │            FAISS Vector Store                   │                 │
│  │        (Cosine Similarity Search)               │                 │
│  └──────────────────────┬─────────────────────────┘                 │
│                         │                                            │
│  ┌──────────────────────▼─────────────────────────┐                 │
│  │              RAG Chain                          │                 │
│  │   (LangChain + Llama/GPT-4o/Gemini)            │                 │
│  └────────────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────────┐
│                       DATA STORES                                    │
│  ┌────────────────┐           ┌─────────────────────┐               │
│  │  PostgreSQL    │           │  FAISS Index         │               │
│  │  (Users,       │           │  (Vector Embeddings) │               │
│  │   Uploads,     │           │                      │               │
│  │   Chat History)│           │  JSON Metadata       │               │
│  └────────────────┘           └──────────────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Faculty uploads** lecture video → saved to `data/videos/`
2. **Pipeline processes** the video:
   - Frame extraction (OpenCV) → `data/frames/`
   - Scene detection (PySceneDetect)
   - Audio extraction (FFmpeg) → `data/audio/`
   - Transcription (Whisper) → `data/transcripts/`
   - OCR (EasyOCR) → `data/ocr_output/`
   - Semantic chunking → text chunks with timestamps
   - Embedding generation → `data/embeddings/`
   - FAISS indexing → `data/faiss_index/`
3. **Student asks a question**:
   - Question embedded → FAISS similarity search
   - Top-K relevant chunks retrieved
   - K-Means adaptive framing selects 32 key frames
   - LLM generates grounded answer with evidence
   - Response includes answer + source video timestamp
