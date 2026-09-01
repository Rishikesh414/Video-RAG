"""
RAG Chain — orchestrates the full retrieval-augmented generation pipeline
using LangChain to connect retrieval, prompt construction, and LLM generation.
"""

from langchain.chains import LLMChain
from langchain.schema import HumanMessage

from pipeline.rag.prompt_templates import get_videorag_prompt
from pipeline.rag.llm_provider import get_llm
from pipeline.vectorstore.retriever import VideoRetriever


class VideoRAGChain:
    """
    End-to-end RAG chain that:
    1. Retrieves relevant content from the FAISS vector store
    2. Constructs a grounded prompt with video evidence
    3. Generates a hallucination-free answer via the LLM
    """

    def __init__(
        self,
        retriever: VideoRetriever,
        llm_provider: str = "llama",
        top_k: int = 5,
    ):
        """
        Initialize the RAG chain.

        Args:
            retriever: The video retriever instance.
            llm_provider: Which LLM to use (llama, openai, gemini).
            top_k: Number of chunks to retrieve per query.
        """
        self.retriever = retriever
        self.llm = get_llm(llm_provider)
        self.top_k = top_k
        self.prompt_template = get_videorag_prompt()

    def run(self, question: str) -> dict:
        """
        Process a question through the full RAG pipeline.

        Args:
            question: The user's natural language question.

        Returns:
            Dict with 'answer', 'sources', and 'context'.
        """
        # Step 1: Retrieve relevant context
        context = self.retriever.retrieve_with_context(question, top_k=self.top_k)
        results = self.retriever.retrieve(question, top_k=self.top_k)

        # Step 2: Format the prompt
        prompt = self.prompt_template.format(context=context, question=question)

        # Step 3: Generate answer
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        answer = chain.run(context=context, question=question)

        # Step 4: Extract sources
        sources = [
            r["metadata"].get("source", "Unknown")
            for r in results
        ]

        return {
            "answer": answer,
            "sources": list(set(sources)),
            "context": context,
        }
