"""
Prompt Templates — structured prompt engineering for the VideoRAG LLM.

Uses LangChain PromptTemplate to build grounded prompts that
instruct the LLM to answer based only on retrieved evidence.
"""

from langchain.prompts import PromptTemplate


def get_videorag_prompt() -> PromptTemplate:
    """
    Get the main VideoRAG prompt template.

    This prompt instructs the LLM to:
    - Answer based ONLY on the provided context (video evidence)
    - Provide step-by-step explanations when relevant
    - Reference the source video timestamps
    - Explicitly state when the answer is not found in the evidence
    """
    template = """You are VideoRAG, an AI assistant that answers questions based on video lecture content.

You have been provided with relevant context extracted from lecture videos, including transcripts, 
on-screen text (OCR), and visual descriptions. Your answers must be grounded in this evidence.

RULES:
1. Answer ONLY based on the provided context. Do NOT use prior knowledge.
2. If the context does not contain enough information, say: "I could not find relevant information in the lecture videos for this question."
3. When applicable, provide step-by-step explanations.
4. Reference the source and timestamp when available (e.g., "[Source: lecture_01.mp4 @ 120s]").
5. Be concise but thorough.

--- CONTEXT FROM VIDEO LECTURES ---
{context}
--- END CONTEXT ---

QUESTION: {question}

ANSWER:"""

    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )


def get_summary_prompt() -> PromptTemplate:
    """
    Prompt template for generating video summaries.
    """
    template = """Summarize the following transcript from a lecture video.
Provide a clear, structured summary with key points.

TRANSCRIPT:
{transcript}

SUMMARY:"""

    return PromptTemplate(
        template=template,
        input_variables=["transcript"],
    )
