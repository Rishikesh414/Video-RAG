"""
Multimodal LLM — sends extracted video clips to a Multimodal LLM
(Gemini 1.5 Pro or GPT-4o) for deep visual analysis.

Part of Step 3 (Multimodal). This is the EXPENSIVE step — only called
on short clips (15-60 seconds) identified by Steps 1 and 2.
The LLM watches the clip and generates a detailed, grounded answer.
"""

import base64
from pathlib import Path
from typing import Dict, Optional


class MultimodalLLM:
    """
    Abstraction layer for multimodal LLM providers that can analyze video clips.
    Supports Gemini 1.5 Pro and GPT-4o.
    """

    def __init__(self, provider: str = "gemini", api_key: str = ""):
        """
        Args:
            provider: 'gemini' for Gemini 1.5 Pro, 'openai' for GPT-4o.
            api_key: API key for the provider.
        """
        self.provider = provider
        self.api_key = api_key
        self.client = None  # Lazy-loaded

    def _init_client(self):
        """Initialize the provider client."""
        if self.provider == "gemini":
            import google.generativeai as genai
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
        Send a video clip to the Multimodal LLM for deep analysis.

        Args:
            clip_path: Path to the extracted video clip file.
            question: The user's original question.
            transcript_context: Relevant transcript text for additional context.

        Returns:
            The LLM's detailed text answer grounded in the video evidence.
        """
        if self.client is None:
            self._init_client()

        if self.provider == "gemini":
            return self._analyze_with_gemini(clip_path, question, transcript_context)
        elif self.provider == "openai":
            return self._analyze_with_openai(clip_path, question, transcript_context)

    def _analyze_with_gemini(
        self,
        clip_path: str,
        question: str,
        transcript_context: str,
    ) -> str:
        """Analyze clip using Gemini 1.5 Pro's native video understanding."""
        import google.generativeai as genai

        # Upload the video clip to Gemini
        video_file = genai.upload_file(clip_path)

        prompt = self._build_prompt(question, transcript_context)

        response = self.client.generate_content(
            [video_file, prompt],
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )

        return response.text

    def _analyze_with_openai(
        self,
        clip_path: str,
        question: str,
        transcript_context: str,
    ) -> str:
        """
        Analyze clip using GPT-4o.
        Note: GPT-4o processes video as sampled frames, not native video.
        We extract key frames and send them as images.
        """
        import cv2

        frames_b64 = self._sample_frames_as_base64(clip_path, max_frames=8)

        prompt = self._build_prompt(question, transcript_context)

        # Build message with images
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

        return response.choices[0].message.content

    def _build_prompt(self, question: str, transcript_context: str) -> str:
        """Build the analysis prompt for the multimodal LLM."""
        transcript_section = ""
        if transcript_context:
            transcript_section = f"""

TRANSCRIPT FROM THIS CLIP:
{transcript_context}
"""

        return f"""You are VideoRAG, an AI that answers questions by analyzing video evidence.

You are being shown a specific video clip that was identified as containing
the answer to the user's question. Analyze the visual content carefully.

RULES:
1. Answer based ONLY on what you see in this video clip and the transcript.
2. Describe relevant visual details (objects, actions, text on screen, etc.).
3. Be precise and specific — this clip was selected as evidence.
4. If the clip doesn't contain the answer, say so clearly.
{transcript_section}
USER QUESTION: {question}

Provide a detailed, evidence-based answer:"""

    @staticmethod
    def _sample_frames_as_base64(video_path: str, max_frames: int = 8) -> list:
        """Sample frames from a clip and encode as base64 JPEG for GPT-4o."""
        import cv2

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
        return frames_b64
