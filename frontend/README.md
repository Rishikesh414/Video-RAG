# VideoRAG Frontend

React.js frontend built with **Vite** for the VideoRAG project.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

The dev server starts at `http://localhost:3000` and proxies API requests to the FastAPI backend at `http://localhost:8000`.

## Pages

- **Student Dashboard** — Query interface with chat and video evidence playback
- **Faculty Dashboard** — Upload lecture videos and PDF notes
- **Login** — Authentication page for students and faculty
