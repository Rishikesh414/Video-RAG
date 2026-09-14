"""
Visual Describer — generates natural-language descriptions of scene keyframes
using a Vision Language Model (VLM) during Step 1 indexing.

Part of Step 1 (Indexing). Designed for education-domain lecture videos.
Runs at INDEX TIME (not query time), generating 2-3 sentence descriptions
of each scene's keyframe.

Supported providers:
  - ollama  : Local Ollama VLM (llama3.2-vision, llava, etc.) — DEFAULT
  - gemini  : Google Gemini Flash (API key required)
  - openai  : GPT-4o-mini (API key required)
  - disabled: Skips visual description (fallback when no GPU/API)

For RTX 3050 6GB: use provider='ollama', model='llama3.2-vision:11b'
"""

import base64
import logging
from typing import List, Dict

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Education-domain system prompt
EDUCATION_DESCRIBER_PROMPT = """You are an AI assistant helping index educational lecture videos for a RAG search system.

Analyze this scene keyframe from a lecture video and provide a brief, searchable description (2-3 sentences) that captures:
1. The visual content (slide content, whiteboard writing, demo, code on screen, professor, etc.)
2. What educational concept or topic appears to be covered
3. Any text, diagrams, equations, or key visual elements visible

Focus on content that would help a student search for this moment in the lecture.
Be specific and educational. Do NOT describe camera angles or production quality.

Respond with ONLY the description text, no preamble."""


class VisualDescriber:
    """
    VLM-based scene describer for educational lecture video indexing.

    Default: Ollama local model (no API key needed).
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
            provider: 'ollama' (default, local), 'gemini', 'openai', or 'disabled'.
            api_key: API key (only for gemini/openai; empty for ollama).
            model: Model name for the chosen provider.
            ollama_base_url: Ollama server base URL.
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.ollama_base_url = ollama_base_url
        self._client = None  # Lazy-loaded

    def _init_client(self):
        """Initialize the provider client on first use."""
        if self.provider == "ollama":
            try:
                import ollama as ollama_sdk
                self._client = ollama_sdk.Client(host=self.ollama_base_url)
                logger.info(
                    f"VisualDescriber: Using Ollama '{self.model}' at {self.ollama_base_url}"
                )
            except ImportError:
                logger.error(
                    "ollama Python package not installed. Run: pip install ollama\n"
                    "Visual descriptions will be disabled."
                )
                self.provider = "disabled"

        elif self.provider == "gemini":
            if not self.api_key:
                logger.warning("VisualDescriber: No GOOGLE_API_KEY set. Disabling VLM.")
                self.provider = "disabled"
                return
            try:
                import google.genai as genai
                self._client = genai.Client(api_key=self.api_key)
                self._sdk = "new"
                logger.info(f"VisualDescriber: Using Gemini '{self.model}' (google.genai SDK)")
            except ImportError:
                try:
                    import google.generativeai as genai
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", FutureWarning)
                        genai.configure(api_key=self.api_key)
                        self._client = genai.GenerativeModel(self.model)
                    self._sdk = "legacy"
                    logger.info(f"VisualDescriber: Using Gemini '{self.model}' (legacy SDK)")
                except Exception as e:
                    logger.error(f"Gemini init failed: {e}. Disabling VLM.")
                    self.provider = "disabled"

        elif self.provider == "openai":
            if not self.api_key:
                logger.warning("VisualDescriber: No OPENAI_API_KEY set. Disabling VLM.")
                self.provider = "disabled"
                return
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
                logger.info(f"VisualDescriber: Using OpenAI '{self.model}'")
            except ImportError:
                logger.error("openai not installed. Disabling VLM.")
                self.provider = "disabled"

    def describe_frame(self, frame: np.ndarray) -> str:
        """
        Generate a scene description for a single video frame.

        Args:
            frame: NumPy BGR image array from OpenCV.

        Returns:
            2-3 sentence description, or "" if disabled/error.
        """
        if self.provider == "disabled":
            return ""

        if self._client is None:
            self._init_client()

        if self.provider == "disabled":
            return ""

        try:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            image_bytes = buffer.tobytes()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            if self.provider == "ollama":
                return self._describe_with_ollama(image_b64)
            elif self.provider == "gemini":
                return self._describe_with_gemini(image_bytes)
            elif self.provider == "openai":
                return self._describe_with_openai(image_b64)

        except Exception as e:
            logger.warning(f"Visual description failed: {e}")
            return ""

        return ""

    def _describe_with_ollama(self, image_b64: str) -> str:
        """Describe frame using a local Ollama vision model."""
        response = self._client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": EDUCATION_DESCRIBER_PROMPT,
                    "images": [image_b64],
                }
            ],
            options={
                "temperature": 0.2,
                "num_predict": 200,  # Short descriptions only
            },
        )
        return response["message"]["content"].strip()

    def _describe_with_gemini(self, image_bytes: bytes) -> str:
        """Send frame to Gemini Flash for description."""
        try:
            import google.genai as genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=[
                    EDUCATION_DESCRIBER_PROMPT,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                ],
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=256),
            )
            return response.text.strip() if response.text else ""
        except ImportError:
            import google.generativeai as genai
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(
                    [EDUCATION_DESCRIBER_PROMPT, {"mime_type": "image/jpeg", "data": image_bytes}],
                    generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=256),
                )
                return response.text.strip() if response.text else ""

    def _describe_with_openai(self, image_b64: str) -> str:
        """Send frame to GPT-4o-mini for description."""
        response = self._client.chat.completions.create(
            model=self.model or "gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": EDUCATION_DESCRIBER_PROMPT},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}",
                        "detail": "low",
                    }},
                ],
            }],
            max_tokens=256,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def describe_scenes(
        self,
        video_path: str,
        scenes: List[tuple],
    ) -> List[Dict]:
        """
        Generate visual descriptions for each scene's keyframe.

        Args:
            video_path: Path to the video file.
            scenes: List of (start_time, end_time) tuples in seconds.

        Returns:
            List of dicts: scene_start, scene_end, timestamp, description.
        """
        descriptions = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            logger.warning(f"Could not read FPS from {video_path}")
            cap.release()
            return descriptions

        total = len(scenes)
        for i, (scene_start, scene_end) in enumerate(scenes):
            mid_time = (scene_start + scene_end) / 2.0
            mid_frame_idx = int(mid_time * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_idx)
            ret, frame = cap.read()
            if not ret:
                alt_idx = int(scene_start * fps) + int(fps * 0.5)
                cap.set(cv2.CAP_PROP_POS_FRAMES, alt_idx)
                ret, frame = cap.read()

            description = ""
            if ret:
                description = self.describe_frame(frame)
                logger.debug(
                    f"Scene {i+1}/{total} ({scene_start:.1f}s-{scene_end:.1f}s): "
                    f"{'OK' if description else 'empty'}"
                )

            descriptions.append({
                "scene_start": round(scene_start, 2),
                "scene_end": round(scene_end, 2),
                "timestamp": round(mid_time, 2),
                "description": description,
            })

        cap.release()
        described = sum(1 for d in descriptions if d["description"])
        logger.info(f"Visual descriptions: {described}/{total} scenes described")
        return descriptions

    def get_description_for_timestamp(self, descriptions: List[Dict], timestamp: float) -> str:
        """Get the visual description for the scene containing a timestamp."""
        for d in descriptions:
            if d["scene_start"] <= timestamp <= d["scene_end"]:
                return d.get("description", "")
        return ""
