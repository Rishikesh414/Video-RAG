"""
LLM Provider — abstraction layer for switching between LLM backends.

Supports:
- Llama 3.1 8B Instruct (local via llama-cpp or HuggingFace)
- OpenAI GPT-4o (cloud API)
- Google Gemini 2.5 Flash (cloud API)
"""

from langchain.llms.base import BaseLLM


def get_llm(provider: str = "llama", **kwargs) -> BaseLLM:
    """
    Factory function to get an LLM instance based on the provider.

    Args:
        provider: One of 'llama', 'openai', 'gemini'.
        **kwargs: Additional provider-specific arguments.

    Returns:
        A LangChain-compatible LLM instance.

    Raises:
        ValueError: If an unknown provider is specified.
    """
    if provider == "openai":
        return _get_openai_llm(**kwargs)
    elif provider == "gemini":
        return _get_gemini_llm(**kwargs)
    elif provider == "llama":
        return _get_llama_llm(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Choose from: llama, openai, gemini")


def _get_openai_llm(**kwargs) -> BaseLLM:
    """
    Initialize OpenAI GPT-4o via LangChain.
    """
    from langchain_community.llms import OpenAI

    return OpenAI(
        model_name=kwargs.get("model_name", "gpt-4o"),
        temperature=kwargs.get("temperature", 0.1),
        max_tokens=kwargs.get("max_tokens", 1024),
    )


def _get_gemini_llm(**kwargs) -> BaseLLM:
    """
    Initialize Google Gemini 2.5 Flash via LangChain.
    """
    from langchain_community.llms import GooglePalm

    return GooglePalm(
        model_name=kwargs.get("model_name", "gemini-2.5-flash"),
        temperature=kwargs.get("temperature", 0.1),
        max_output_tokens=kwargs.get("max_tokens", 1024),
    )


def _get_llama_llm(**kwargs) -> BaseLLM:
    """
    Initialize Llama 3.1 8B Instruct via LangChain (local inference).
    """
    from langchain_community.llms import LlamaCpp

    return LlamaCpp(
        model_path=kwargs.get("model_path", "./models/llama-3.1-8b-instruct.gguf"),
        temperature=kwargs.get("temperature", 0.1),
        max_tokens=kwargs.get("max_tokens", 1024),
        n_ctx=kwargs.get("n_ctx", 4096),
        verbose=False,
    )
