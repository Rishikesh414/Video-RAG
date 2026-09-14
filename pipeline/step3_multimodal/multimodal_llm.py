"""
Multimodal LLM — analyzes extracted video clips by sampling key frames
and sending them to a Vision Language Model (VLM) for deep analysis.

Part of Step 3 (Multimodal). Only called on short clips (15-60s) identified
by Steps 1 and 2.

Supported providers:
  - ollama  : Local Ollama VLM (llama3.2-vision, llava, etc.) — DEFAULT, no API key
  - gemini  : Google Gemini 1.5 Pro (API key required)
  - openai  : GPT-4o (API key required)

For an RTX 3050 6GB, use: provider='ollama', model='llama3.2-vision:11b'
"""

import base64
import logging
from pathlib import Path
from typing import Optional

import cv2

logger = logging.getLogger(__name__)


class MultimodalLLM:
    """
    Abstraction layer for multimodal LLM providers that analyze video clips.

    Default: Ollama (local, no API key needed).
    Ollama samples key frames from the clip and sends them as images.
    """

    def __init__(
        self,
        provider: str = "ollama",
        api_key: str = "",
        model: str = "llama3.2-vision:11b",
        ollama_base_url: str = "http://localhost:11434",
    ):
        """
        Args:
            provider: 'ollama' (local), 'gemini', or 'openai'.
            api_key: API key (only for gemini/openai).
            model: Model name. Defaults to llama3.2-vision:11b for Ollama.
            ollama_base_url: Ollama server URL.
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.ollama_base_url = ollama_base_url
        self.client = None  # Lazy-loaded

    def _init_client(self):
        """Initialize the provider client on first use."""
        if self.provider == "ollama":
            try:
                import ollama as ollama_sdk
                self.client = ollama_sdk.Client(host=self.ollama_base_url)
                logger.info(
                    f"MultimodalLLM: Using Ollama model '{self.model}' "
                    f"at {self.ollama_base_url}"
                )
            except ImportError:
                raise ImportError(
                    "ollama Python package not installed. "
                    "Run: pip install ollama"
                )

        elif self.provider == "gemini":
            try:
                import google.genai as genai
                self.client = genai.Client(api_key=self.api_key)
            except ImportError:
                import google.generativeai as genai
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel("gemini-1.5-pro")

        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)

        else:
            raise ValueError(f"Unknown multimodal provider: {self.provider}")

    def analyze_clip(
        self,
        clip_path: str,
        question: str,
        transcript_context: str = "",
    ) -> str:
        """
        Analyze a video clip by sampling key frames and sending to the VLM.

        Args:
            clip_path: Path to the extracted video clip file.
            question: The user's original question.
            transcript_context: Relevant transcript text for context.

        Returns:
            Detailed text answer grounded in the visual evidence.
        """
        if self.client is None:
            self._init_client()

        if self.provider == "ollama":
            return self._analyze_with_ollama(clip_path, question, transcript_context)
        elif self.provider == "gemini":
            return self._analyze_with_gemini(clip_path, question, transcript_context)
        elif self.provider == "openai":
            return self._analyze_with_openai(clip_path, question, transcript_context)

        return "Analysis unavailable."

    # ─── Ollama (local, default) ──────────────────────────────────────

    def _analyze_with_ollama(
        self,
        clip_path: str,
        question: str,
        transcript_context: str,
    ) -> str:
        """
        Analyze clip using a local Ollama VLM (e.g. llama3.2-vision:11b).

        Samples 6 evenly-spaced key frames from the clip and sends them
        alongside the transcript context for analysis.
        """
        # Sample key frames from the clip
        frames_b64 = self._sample_frames_as_base64(clip_path, max_frames=6)

        if not frames_b64:
            logger.warning(f"No frames extracted from clip: {clip_path}")
            return "Could not extract frames from the video clip for analysis."

        prompt = self._build_prompt(question, transcript_context)

        # Ollama vision: pass images as base64 in the 'images' field
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": frames_b64,  # list of base64 strings
                }
            ],
            options={
                "temperature": 0.2,
                "num_predict": 1024,
            },
        )
        return response["message"]["content"].strip()

    # ─── Gemini ───────────────────────────────────────────────────────

    def _analyze_with_gemini(
        self,
        clip_path: str,
        question: str,
        transcript_context: str,
    ) -> str:
        """Analyze clip using Gemini 1.5 Pro's native video understanding."""
        try:
            # New SDK
            import google.genai as genai
            from google.genai import types
            prompt = self._build_prompt(question, transcript_context)
            with open(clip_path, "rb") as f:
                video_bytes = f.read()
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
                ],
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=2048),
            )
            return response.text.strip()
        except ImportError:
            # Legacy SDK
            import google.generativeai as genai
            video_file = genai.upload_file(clip_path)
            prompt = self._build_prompt(question, transcript_context)
            response = self.client.generate_content(
                [video_file, prompt],
                generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=2048),
            )
            return response.text.strip()

    # ─── OpenAI ───────────────────────────────────────────────────────

    def _analyze_with_openai(
        self,
        clip_path: str,
        question: str,
        transcript_context: str,
    ) -> str:
        """Analyze clip using GPT-4o (sampled frames as images)."""
        frames_b64 = self._sample_frames_as_base64(clip_path, max_frames=8)
        prompt = self._build_prompt(question, transcript_context)
        content = [{"type": "text", "text": prompt}]
        for frame_b64 in frames_b64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "high",
                },
            })
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    # ─── Shared Utilities ─────────────────────────────────────────────

    def _build_prompt(self, question: str, transcript_context: str) -> str:
        """Build the analysis prompt for the VLM."""
        transcript_section = ""
        if transcript_context:
            transcript_section = f"""

TRANSCRIPT FROM THIS CLIP:
{transcript_context}
"""
        return f"""You are VideoRAG, an AI tutor that answers student questions by analyzing lecture video evidence.

You are being shown key frames from a specific lecture video clip that was identified as containing the answer to the student's question. Analyze the visual content carefully.

RULES:
1. Answer based ONLY on what you can see in these frames and the transcript.
2. Describe relevant visual details (slides, diagrams, equations, code, whiteboard writing, etc.).
3. Be precise and educational — this clip was selected as evidence for a student.
4. If the frames don't contain the answer, say so clearly.
{transcript_section}
STUDENT QUESTION: {question}

Provide a detailed, evidence-based answer:"""

    @staticmethod
    def _sample_frames_as_base64(video_path: str, max_frames: int = 6) -> list:
        """
        Sample evenly-spaced frames from a video clip.

        Returns:
            List of base64-encoded JPEG strings (not data URLs — raw base64).
        """
        if not Path(video_path).exists():
            logger.warning(f"Clip not found: {video_path}")
            return []

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(1, total_frames // max_frames)

        frames_b64 = []
        frame_count = 0

        while cap.isOpened() and len(frames_b64) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % interval == 0:
                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frames_b64.append(base64.b64encode(buffer).decode("utf-8"))
            frame_count += 1

        cap.release()
        logger.debug(f"Sampled {len(frames_b64)} frames from {video_path}")
        return frames_b64
