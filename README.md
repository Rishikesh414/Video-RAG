# 🎬 VideoRAG: Next-Gen Video Search & Generation

An advanced **Retrieval-Augmented Generation (RAG)** framework that enables AI to understand video content — retrieving relevant video evidence, processing visual frames and audio, and generating accurate, hallucination-free answers grounded in real-world evidence.

## ✨ Key Features

- **Dynamic Retrieval** — Vector search to find the most relevant video segments for any query
- **Adaptive Framing** — K-Means clustering to compress thousands of frames into the 32 most informative key frames
- **Multimodal Understanding** — Combines video frames, audio transcripts, and OCR text into a unified knowledge base
- **Evidence-Based Answers** — Generates grounded step-by-step responses with source video timestamps

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Frontend   │◄──►│   Backend API    │◄──►│   VideoRAG       │
│  (React.js)  │    │   (FastAPI)      │    │   Pipeline       │
└──────────────┘    └──────────────────┘    └──────────────────┘
                           │                        │
                    ┌──────┴──────┐          ┌──────┴──────┐
                    │ PostgreSQL  │          │   Qdrant    │
                    │ (Users,     │          │   Vector    │
                    │  History)   │          │   Store     │
                    └─────────────┘          └─────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React.js (Vite) |
| Backend | FastAPI (Python 3.11) |
| LLM | Llama 3.1 8B / GPT-4o / Gemini 2.5 Flash |
| Embeddings | Qwen3-Embedding-8B / Sentence Transformers |
| Video Understanding | InternVideo2 / YOLOv8 |
| Frame Extraction | OpenCV |
| Scene Detection | PySceneDetect |
| Speech-to-Text | OpenAI Whisper Large-v3 |
| OCR | EasyOCR |
| Vector Database | Qdrant |
| RAG Framework | LangChain |
| Database | PostgreSQL |
| Deployment | Docker |

## 🚀 Quickstart

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- FFmpeg installed and on PATH

### 1. Clone & Configure

```bash
git clone <repository-url>
cd VIDEO_RAG
cp .env.example .env
# Edit .env with your actual keys and paths
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Docker (Full Stack)

```bash
cd docker
docker-compose up --build
```

## 📁 Project Structure

```
VIDEO_RAG/
├── frontend/          # React.js UI (Student & Faculty dashboards)
├── backend/           # FastAPI REST API
├── pipeline/          # Core VideoRAG processing engine
├── database/          # PostgreSQL connection & migrations
├── data/              # Runtime data (videos, frames, embeddings, etc.)
├── tests/             # Pytest test suite
├── docker/            # Docker deployment configs
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 📖 Modules

1. **Faculty / Admin Module** — Upload lecture recordings and PDF notes
2. **Core VideoRAG Engine** — Process videos, extract frames, generate embeddings, build Qdrant index
3. **Student Dashboard** — Ask questions and receive evidence-based answers with video snippets

## 👥 Team

**Team Name:** Tech Nerds
- Thanush Kumar P
- Rishikesh K

## 📄 License

MIT
