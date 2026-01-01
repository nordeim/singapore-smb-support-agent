"""Test LLM integration in SupportAgent."""

from unittest.mock import Mock, patch

import pytest

from app.agent.support_agent import AgentContext, SupportAgent
from app.config import settings


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_response_with_llm():
    """Test that _generate_response uses LLM to generate responses."""
    agent = SupportAgent()

    context = AgentContext(
        session_id="test-session",
        user_id=1,
        conversation_summary="Customer asking about pricing",
        recent_messages=[
            {"role": "user", "content": "What are your prices?"},
        ],
        business_hours_status="open",
    )

    with patch("app.agent.support_agent.ChatOpenAI") as mock_llm_class:
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Our pricing starts at $99/month for basic plans."
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm

        response = agent._generate_response(
            query="What are your prices?",
            knowledge="Basic plan: $99/month\nPremium plan: $199/month",
            context=context,
        )

        mock_llm_class.assert_called_once_with(
            model=settings.LLM_MODEL_PRIMARY,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

        mock_llm.invoke.assert_called_once()
        assert response == "Our pricing starts at $99/month for basic plans."


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_response_without_knowledge():
    """Test response generation when no knowledge is retrieved."""
    agent = SupportAgent()

    context = AgentContext(
        session_id="test-session",
        user_id=1,
        conversation_summary="",
        recent_messages=[],
        business_hours_status="open",
    )

    with patch("app.agent.support_agent.ChatOpenAI") as mock_llm_class:
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "I don't have specific information about that topic."
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm

        response = agent._generate_response(
            query="Tell me about unicorns",
            knowledge="",
            context=context,
        )

        assert response == "I don't have specific information about that topic."


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_response_llm_fallback():
    """Test that _generate_response falls back to template on LLM error."""
    agent = SupportAgent()

    context = AgentContext(
        session_id="test-session",
        user_id=1,
        conversation_summary="",
        recent_messages=[],
        business_hours_status="open",
    )

    with patch("app.agent.support_agent.ChatOpenAI") as mock_llm_class:
        mock_llm_class.side_effect = Exception("API Error")

        response = agent._generate_response(
            query="What are your prices?",
            knowledge="Basic plan: $99/month",
            context=context,
        )

        assert "Based on our knowledge base" in response
        assert "Basic plan: $99/month" in response
