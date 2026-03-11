"""Tests for the Context Extension Agent (US-006).

Covers: prompt rendering, full history retrieval, mock mode,
empty history handling, gRPC failure handling.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.context_extension.agent import ContextExtensionAgent
from agents.context_extension.prompt import build_system_prompt


def _make_message(
    msg_id: str = "msg-001",
    sender_type: str = "user",
    sender_id: str = "user-1",
    ai_agent: str = "",
    content: str = "Hello, what about the project timeline?",
    created_at: str = "2026-03-10T14:32:00Z",
) -> dict:
    return {
        "id": msg_id,
        "sender_type": sender_type,
        "sender_id": sender_id,
        "ai_agent": ai_agent,
        "content": content,
        "created_at": created_at,
    }


# ── System prompt rendering ──


class TestSystemPrompt:
    def test_prompt_includes_query(self):
        """System prompt renders the search query."""
        prompt = build_system_prompt(
            query="What did we decide about authentication?",
            messages=[],
        )
        assert "What did we decide about authentication?" in prompt

    def test_prompt_includes_messages(self):
        """System prompt renders chat messages."""
        messages = [
            _make_message(
                msg_id="msg-1",
                content="We should use JWT tokens.",
                sender_type="user",
                sender_id="alice",
            ),
            _make_message(
                msg_id="msg-2",
                content="Agreed, with 24h expiry.",
                sender_type="ai",
                ai_agent="facilitator",
            ),
        ]
        prompt = build_system_prompt(query="test", messages=messages)
        assert "We should use JWT tokens." in prompt
        assert "Agreed, with 24h expiry." in prompt
        assert 'id="msg-1"' in prompt
        assert 'id="msg-2"' in prompt

    def test_prompt_no_messages(self):
        """System prompt handles empty history."""
        prompt = build_system_prompt(query="test", messages=[])
        assert "(no messages in chat history)" in prompt

    def test_prompt_includes_retrieval_rules(self):
        """System prompt includes retrieval and citation rules."""
        prompt = build_system_prompt(query="test", messages=[])
        assert "retrieval_rules" in prompt
        assert "NEVER fabricate" in prompt
        assert "citation_rules" in prompt

    def test_prompt_message_shows_sender(self):
        """Messages in prompt show sender information."""
        msg = _make_message(sender_type="user", sender_id="alice")
        prompt = build_system_prompt(query="test", messages=[msg])
        assert 'sender="alice"' in prompt

    def test_prompt_ai_message_shows_agent_name(self):
        """AI messages show the agent name as sender."""
        msg = _make_message(
            sender_type="ai", ai_agent="facilitator", sender_id=""
        )
        prompt = build_system_prompt(query="test", messages=[msg])
        assert 'sender="facilitator"' in prompt

    def test_prompt_identity(self):
        """System prompt includes agent identity."""
        prompt = build_system_prompt(query="test", messages=[])
        assert "Context Extension Agent" in prompt
        assert "Full chat history search" in prompt


# ── Agent execution ──


class _MockSettings:
    """Minimal mock for prompt execution settings."""

    def __init__(self, service_id: str = "default") -> None:
        self.service_id = service_id
        self.max_tokens = 1000
        self.temperature = 0.7
        self.timeout = 90


class TestContextExtensionAgent:
    @pytest.mark.asyncio
    async def test_empty_history_returns_early(self):
        """Agent returns early message when no messages in history."""
        mock_client = MagicMock()
        mock_client.get_full_chat_history.return_value = {"messages": []}

        agent = ContextExtensionAgent(core_client=mock_client)
        result = await agent._execute({
            "query": "What did we discuss?",
            "idea_id": "idea-1",
        })

        assert "empty" in result["response"]
        assert result["messages_cited"] == []
        mock_client.get_full_chat_history.assert_called_once_with("idea-1")

    @pytest.mark.asyncio
    async def test_grpc_failure_returns_error(self):
        """Agent returns error message when gRPC call fails."""
        mock_client = MagicMock()
        mock_client.get_full_chat_history.side_effect = Exception("gRPC unavailable")

        agent = ContextExtensionAgent(core_client=mock_client)
        result = await agent._execute({
            "query": "What did we discuss?",
            "idea_id": "idea-1",
        })

        assert "Unable to retrieve" in result["response"]
        assert result["messages_cited"] == []

    @pytest.mark.asyncio
    async def test_messages_passed_to_sk_and_ids_returned(self):
        """Agent passes messages to prompt, uses escalated tier, returns response."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [
            _make_message(msg_id="msg-1", content="Let's use JWT."),
            _make_message(msg_id="msg-2", content="Agreed."),
        ]
        mock_client = MagicMock()
        mock_client.get_full_chat_history.return_value = {"messages": messages}

        agent = ContextExtensionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "The team decided to use JWT tokens."

        with (
            patch(
                "agents.context_extension.agent.get_deployment",
                return_value="escalated-deploy",
            ) as mock_deploy,
            patch(
                "agents.context_extension.agent.create_kernel"
            ) as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            result = await agent._execute({
                "query": "What authentication approach?",
                "idea_id": "idea-1",
            })

        # Verify escalated tier used
        mock_deploy.assert_called_once_with("escalated")
        # Verify response
        assert result["response"] == "The team decided to use JWT tokens."
        assert result["messages_cited"] == ["msg-1", "msg-2"]

    @pytest.mark.asyncio
    async def test_uses_escalated_model_tier(self):
        """Agent requests escalated deployment for larger context window."""
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

        messages = [_make_message()]
        mock_client = MagicMock()
        mock_client.get_full_chat_history.return_value = {"messages": messages}

        agent = ContextExtensionAgent(core_client=mock_client)

        mock_message = AsyncMock()
        mock_message.__str__ = lambda self: "response"

        with (
            patch(
                "agents.context_extension.agent.get_deployment",
                return_value="escalated-deploy",
            ) as mock_deploy,
            patch(
                "agents.context_extension.agent.create_kernel"
            ) as mock_kernel_factory,
        ):
            mock_service = AsyncMock(spec=AzureChatCompletion)
            mock_service.get_prompt_execution_settings_class.return_value = (
                _MockSettings
            )
            mock_service.get_chat_message_contents = AsyncMock(
                return_value=[mock_message]
            )

            mock_kernel = MagicMock()
            mock_kernel.get_service.return_value = mock_service
            mock_kernel_factory.return_value = mock_kernel

            await agent._execute({
                "query": "test",
                "idea_id": "idea-1",
            })

        mock_deploy.assert_called_once_with("escalated")


# ── Mock mode ──


class TestContextExtensionMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        """ContextExtensionAgent.process() in mock mode returns fixture data."""
        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent

        agent = ContextExtensionAgent()
        result = await agent.process({
            "query": "test question",
            "idea_id": "test-idea",
        })
        assert "response" in result
        assert "messages_cited" in result
        assert isinstance(result["messages_cited"], list)
        assert len(result["messages_cited"]) == 3
