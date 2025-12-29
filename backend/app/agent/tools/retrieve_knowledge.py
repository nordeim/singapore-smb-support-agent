"""Retrieve knowledge tool for Singapore SMB Support Agent."""

from typing import Optional
from pydantic import BaseModel, Field


class RetrieveKnowledgeInput(BaseModel):
    """Input for retrieve_knowledge tool."""

    query: str = Field(..., description="User query to search knowledge base")
    session_id: str = Field(..., description="Session identifier")


class RetrieveKnowledgeOutput(BaseModel):
    """Output for retrieve_knowledge tool."""

    success: bool = Field(..., description="Whether retrieval was successful")
    knowledge: str = Field(..., description="Retrieved knowledge text")
    sources: list[dict] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    message: Optional[str] = Field(None, description="Additional information")


async def retrieve_knowledge(
    query: str,
    session_id: str,
    rag_pipeline=None,
) -> RetrieveKnowledgeOutput:
    """
    Retrieve relevant knowledge from the knowledge base using RAG pipeline.

    Args:
        query: User query to search for
        session_id: Session identifier for context
        rag_pipeline: RAG pipeline instance (optional, injected)

    Returns:
        RetrieveKnowledgeOutput with retrieved knowledge and metadata
    """
    if not rag_pipeline:
        return RetrieveKnowledgeOutput(
            success=False,
            knowledge="",
            sources=[],
            confidence=0.0,
            message="RAG pipeline not available",
        )

    try:
        from app.config import settings

        result = await rag_pipeline.retrieve(
            query=query,
            session_id=session_id,
            top_k=settings.RETRIEVAL_TOP_K,
        )

        if not result or not result.get("documents"):
            return RetrieveKnowledgeOutput(
                success=True,
                knowledge="No relevant information found in the knowledge base.",
                sources=[],
                confidence=0.0,
                message="Query returned no results",
            )

        knowledge_text = result.get("context", "")
        sources = result.get("metadata", [])
        confidence = result.get("confidence", 0.7)

        return RetrieveKnowledgeOutput(
            success=True,
            knowledge=knowledge_text,
            sources=sources,
            confidence=confidence,
        )

    except Exception as e:
        return RetrieveKnowledgeOutput(
            success=False,
            knowledge="",
            sources=[],
            confidence=0.0,
            message=f"Error retrieving knowledge: {str(e)}",
        )


def get_retrieve_knowledge_tool(rag_pipeline=None):
    """Factory function to create retrieve_knowledge tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(query: str, session_id: str) -> dict:
        result = await retrieve_knowledge(
            query=query,
            session_id=session_id,
            rag_pipeline=rag_pipeline,
        )
        return result.model_dump()

    return Tool(
        name="retrieve_knowledge",
        description="Search knowledge base for relevant information about products, services, policies, and procedures",
        function=tool_wrapper,
    )
