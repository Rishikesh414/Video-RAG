"""
Timestamp Resolver — uses a standard (cheap) LLM to pinpoint exact timestamps
from the semantic search results.

Part of Step 2 (Retrieval). After Qdrant returns relevant text chunks,
this module asks a standard LLM to reason over the metadata and determine
the precise start/end timestamps for the relevant video clip.

This is CHEAP — the LLM is only reading text metadata, not watching video.
"""

from typing import Dict, List, Optional

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate


# ─── Prompt Template ─────────────────────────────────────────────────

TIMESTAMP_RESOLVER_PROMPT = PromptTemplate(
    template="""You are a timestamp resolver for a video search system.

Given a user's question and relevant text chunks from video metadata
(including transcripts and visual object tags), determine the EXACT
timestamp window that most likely contains the answer.

RULES:
1. Return a single JSON object with: start_time, end_time, video_id, confidence, reasoning
2. start_time and end_time are in seconds (float)
3. confidence is "high", "medium", or "low"
4. Keep the window as tight as possible (ideally 15-60 seconds)
5. If multiple segments match, pick the single best match

--- SEARCH RESULTS (metadata from videos) ---
{context}
--- END SEARCH RESULTS ---

USER QUESTION: {question}

Respond with ONLY a valid JSON object:""",
    input_variables=["context", "question"],
)


class TimestampResolver:
    """
    Uses a standard LLM to analyze text metadata and pinpoint exact
    timestamp windows for video clip extraction in Step 3.
    """

    def __init__(self, llm):
        """
        Args:
            llm: A LangChain-compatible LLM instance (cheap/standard model).
        """
        self.llm = llm
        self.prompt = TIMESTAMP_RESOLVER_PROMPT

    def resolve(
        self,
        question: str,
        search_results: List[Dict],
        context_text: str,
    ) -> Dict:
        """
        Determine the exact timestamp window for a query.

        Args:
            question: The user's question.
            search_results: Raw results from SemanticSearch.search().
            context_text: Formatted context from SemanticSearch.format_context().

        Returns:
            Dict with:
            - start_time (float): Clip start in seconds
            - end_time (float): Clip end in seconds
            - video_id (str): Which video the clip belongs to
            - video_path (str): Path to the source video
            - confidence (str): high/medium/low
            - reasoning (str): Why this timestamp was chosen
        """
        import json as json_module

        # Ask the LLM to reason over the text metadata
        prompt_text = self.prompt.format(context=context_text, question=question)
        if hasattr(self.llm, "invoke"):
            resp = self.llm.invoke(prompt_text)
            raw_response = getattr(resp, "content", str(resp))
        elif callable(self.llm):
            raw_response = str(self.llm(prompt_text))
        else:
            raw_response = str(self.llm)

        # Parse LLM output
        try:
            parsed = json_module.loads(raw_response.strip())
        except json_module.JSONDecodeError:
            # Fallback: use the best search result's timestamps directly
            if search_results:
                best = search_results[0]
                parsed = {
                    "start_time": best["start_time"],
                    "end_time": best["end_time"],
                    "video_id": best.get("video_id", ""),
                    "confidence": "low",
                    "reasoning": "LLM output could not be parsed; using best search result.",
                }
            else:
                parsed = {
                    "start_time": 0,
                    "end_time": 0,
                    "video_id": "",
                    "confidence": "low",
                    "reasoning": "No results found.",
                }

        # Ensure video_path is included
        if "video_path" not in parsed and search_results:
            # Find the matching video path from search results
            video_id = parsed.get("video_id", "")
            for r in search_results:
                if r.get("video_id") == video_id:
                    parsed["video_path"] = r.get("video_path", "")
                    break
            else:
                parsed["video_path"] = search_results[0].get("video_path", "")

        return parsed


def get_standard_llm(provider: str = "llama", **kwargs):
    """
    Factory to get a cheap/standard LLM for timestamp resolution.

    Args:
        provider: 'llama' (local), 'openai' (GPT-4o-mini), or 'gemini' (Flash).

    Returns:
        LangChain-compatible LLM instance.
    """
    if provider == "openai":
        from langchain_community.llms import OpenAI
        return OpenAI(
            model_name=kwargs.get("model_name", "gpt-4o-mini"),
            temperature=0.1,
            max_tokens=512,
        )
    elif provider == "gemini":
        from langchain_community.llms import GooglePalm
        return GooglePalm(
            model_name=kwargs.get("model_name", "gemini-2.0-flash"),
            temperature=0.1,
            max_output_tokens=512,
        )
    elif provider == "llama":
        from langchain_community.llms import LlamaCpp
        return LlamaCpp(
            model_path=kwargs.get("model_path", "./models/llama-3.1-8b-instruct.gguf"),
            temperature=0.1,
            max_tokens=512,
            n_ctx=4096,
            verbose=False,
        )
    else:
        raise ValueError(f"Unknown standard LLM provider: {provider}")
