"""Tests for the Facilitator agent (US-002).

Test IDs: T-2.1.03, T-2.1.04, T-2.3.01, T-2.3.02, T-2.4.01, T-2.7.01, T-2.15.01

These tests validate the FacilitatorPlugin tools, prompt rendering, and
FacilitatorAgent mock mode — all without hitting Azure OpenAI.
"""

from __future__ import annotations

import uuid

import pytest

from agents.facilitator.agent import FacilitatorAgent
from agents.facilitator.plugins import FacilitatorPlugin, _validate_board_refs
from agents.facilitator.prompt import build_system_prompt
from events.publishers import clear_published_events, get_published_events


@pytest.fixture(autouse=True)
def _clear_events():
    """Clear published events before each test."""
    clear_published_events()
    yield
    clear_published_events()


def _make_user_message(msg_id: str | None = None, content: str = "Hello", sender_name: str = "Lisa") -> dict:
    return {
        "id": msg_id or str(uuid.uuid4()),
        "content": content,
        "sender_type": "user",
        "sender_name": sender_name,
        "has_ai_reaction": False,
    }


def _make_ai_message(msg_id: str | None = None, content: str = "Sure!") -> dict:
    return {
        "id": msg_id or str(uuid.uuid4()),
        "content": content,
        "sender_type": "ai",
        "sender_name": "facilitator",
        "has_ai_reaction": False,
    }


# ── T-2.1.03: Silent mode no response without @ai ──


class TestSilentModePrompt:
    """T-2.1.03: In silent mode without @ai, prompt instructs no action."""

    def test_silent_mode_no_ai_mention(self):
        prompt = build_system_prompt({
            "agent_mode": "silent",
            "idea_title": "Test",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "recent_messages_formatted": '<message id="1" sender="Lisa" type="user">Hello</message>',
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
        })
        assert "SILENT MODE RULES" in prompt
        assert "take NO action" in prompt

    # T-2.1.04: Silent mode with @ai forces response
    def test_silent_mode_with_ai_mention(self):
        prompt = build_system_prompt({
            "agent_mode": "silent",
            "idea_title": "Test",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "recent_messages_formatted": '<message id="1" sender="Lisa" type="user">@ai what do you think?</message>',
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
        })
        assert "SILENT MODE RULES" in prompt
        assert "you MUST respond" in prompt


# ── T-2.3.01 / T-2.3.02: Title management ──


class TestUpdateTitle:
    @pytest.mark.asyncio
    async def test_update_title_publishes_event(self):
        """T-2.3.01: update_title publishes ai.title.updated."""
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={"title_manually_edited": False},
        )
        result = await plugin.update_title(title="Automate Invoice Approval")
        assert result["success"] is True
        assert result["title"] == "Automate Invoice Approval"

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.title.updated"
        assert events[0]["title"] == "Automate Invoice Approval"

    @pytest.mark.asyncio
    async def test_update_title_truncates_long_title(self):
        """Title > 60 chars gets truncated."""
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={"title_manually_edited": False},
        )
        long_title = "A" * 80
        result = await plugin.update_title(title=long_title)
        assert len(result["title"]) == 60

    @pytest.mark.asyncio
    async def test_update_title_rejected_when_manually_edited(self):
        """T-2.3.02: update_title returns error when title_manually_edited=true."""
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={"title_manually_edited": True},
        )
        result = await plugin.update_title(title="New Title")
        assert "error" in result
        assert result["error"]["code"] == "title_locked"
        assert len(get_published_events()) == 0


# ── T-2.4.01: AI can decide no action (react instead of respond) ──


class TestReactToMessage:
    @pytest.mark.asyncio
    async def test_react_to_user_message(self):
        """T-2.4.01 / T-2.7.01: react_to_message publishes ai.reaction.ready."""
        msg_id = str(uuid.uuid4())
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={
                "recent_messages": [_make_user_message(msg_id=msg_id, content="ok")],
            },
        )
        result = await plugin.react_to_message(message_id=msg_id, reaction_type="thumbs_up")
        assert result["success"] is True

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.reaction.ready"
        assert events[0]["reaction_type"] == "thumbs_up"
        assert events[0]["message_id"] == msg_id

    @pytest.mark.asyncio
    async def test_react_to_ai_message_rejected(self):
        """Cannot react to AI messages."""
        msg_id = str(uuid.uuid4())
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={
                "recent_messages": [_make_ai_message(msg_id=msg_id)],
            },
        )
        result = await plugin.react_to_message(message_id=msg_id, reaction_type="thumbs_up")
        assert "error" in result
        assert result["error"]["code"] == "invalid_message"

    @pytest.mark.asyncio
    async def test_react_invalid_reaction_type(self):
        """Invalid reaction_type is rejected."""
        msg_id = str(uuid.uuid4())
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={
                "recent_messages": [_make_user_message(msg_id=msg_id)],
            },
        )
        result = await plugin.react_to_message(message_id=msg_id, reaction_type="invalid")
        assert "error" in result
        assert result["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_react_duplicate_rejected(self):
        """Already reacted message returns error."""
        msg_id = str(uuid.uuid4())
        msg = _make_user_message(msg_id=msg_id)
        msg["has_ai_reaction"] = True
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={"recent_messages": [msg]},
        )
        result = await plugin.react_to_message(message_id=msg_id, reaction_type="heart")
        assert "error" in result
        assert result["error"]["code"] == "already_reacted"


# ── send_chat_message ──


class TestSendChatMessage:
    """US-005: send_chat_message tool acceptance criteria."""

    @pytest.mark.asyncio
    async def test_send_chat_message_publishes_event(self):
        """AC-1: Publishes ai.chat_response.ready with full payload."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.send_chat_message(content="Hello user!", message_type="regular")
        assert result["message_id"] is None  # placeholder — Gateway fills
        assert result["created_at"] is None  # placeholder — Gateway fills

        events = get_published_events()
        assert len(events) == 1
        evt = events[0]
        assert evt["event_type"] == "ai.chat_response.ready"
        assert evt["idea_id"] == "idea-1"
        assert evt["content"] == "Hello user!"
        assert evt["sender_type"] == "ai"
        assert evt["ai_agent"] == "facilitator"
        assert evt["message_type"] == "regular"
        assert "event_id" in evt  # auto-generated by publisher

    @pytest.mark.asyncio
    async def test_send_delegation_message_type(self):
        """AC-1: delegation message_type is preserved in event."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.send_chat_message(content="Delegated result", message_type="delegation")
        assert result["message_id"] is None

        events = get_published_events()
        assert events[0]["message_type"] == "delegation"

    @pytest.mark.asyncio
    async def test_send_invalid_message_type_defaults_regular(self):
        """Invalid message_type silently defaults to regular."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        await plugin.send_chat_message(content="Hi", message_type="bogus")
        events = get_published_events()
        assert events[0]["message_type"] == "regular"

    @pytest.mark.asyncio
    async def test_send_empty_content_rejected(self):
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.send_chat_message(content="", message_type="regular")
        assert "error" in result
        assert len(get_published_events()) == 0

    @pytest.mark.asyncio
    async def test_send_whitespace_only_rejected(self):
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.send_chat_message(content="   ", message_type="regular")
        assert "error" in result
        assert len(get_published_events()) == 0

    @pytest.mark.asyncio
    async def test_board_ref_validation_strips_invalid(self):
        """AC-2: [[Title]] references not on board are stripped to plain text."""
        content = "Check out [[Valid Item]] and [[Nonexistent]]"
        board_state = {"nodes": [{"title": "Valid Item", "node_type": "box"}]}
        result = _validate_board_refs(content, board_state)
        assert "[[Valid Item]]" in result
        assert "[[Nonexistent]]" not in result
        assert "Nonexistent" in result

    @pytest.mark.asyncio
    async def test_board_ref_validated_through_send(self):
        """AC-2: Board refs validated end-to-end through send_chat_message."""
        plugin = FacilitatorPlugin(
            idea_id="idea-1",
            idea_context={
                "board_state": {"nodes": [{"title": "Auth Module", "node_type": "box"}]},
            },
        )
        await plugin.send_chat_message(
            content="Let's discuss [[Auth Module]] and [[Missing Item]]",
            message_type="regular",
        )
        events = get_published_events()
        assert "[[Auth Module]]" in events[0]["content"]
        assert "[[Missing Item]]" not in events[0]["content"]
        assert "Missing Item" in events[0]["content"]

    @pytest.mark.asyncio
    async def test_board_ref_no_board_state(self):
        """AC-2: No board state means all refs are stripped."""
        plugin = FacilitatorPlugin(idea_id="idea-1", idea_context={})
        await plugin.send_chat_message(content="See [[Item A]]", message_type="regular")
        events = get_published_events()
        assert "[[Item A]]" not in events[0]["content"]
        assert "Item A" in events[0]["content"]


# ── T-2.15.01: Facilitator delegates ──


class TestDelegation:
    @pytest.mark.asyncio
    async def test_delegate_to_context_agent(self):
        """T-2.15.01: delegate_to_context_agent publishes ai.delegation.started."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.delegate_to_context_agent(
            query="What document management system does Commerz Real use?"
        )
        assert result["status"] == "queued"
        assert "delegation_id" in result

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.delegation.started"
        assert events[0]["delegation_type"] == "context_agent"
        assert plugin.delegations[0]["delegation_type"] == "context_agent"

    @pytest.mark.asyncio
    async def test_delegate_to_context_extension(self):
        """delegate_to_context_extension publishes ai.delegation.started."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.delegate_to_context_extension(
            query="What did Lisa say about digital signatures?"
        )
        assert result["status"] == "queued"
        assert "delegation_id" in result

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.delegation.started"
        assert events[0]["delegation_type"] == "context_extension"

    @pytest.mark.asyncio
    async def test_delegation_empty_query_rejected(self):
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.delegate_to_context_agent(query="")
        assert "error" in result


# ── request_board_changes ──


class TestBoardChanges:
    @pytest.mark.asyncio
    async def test_request_board_changes_accepted(self):
        """request_board_changes returns accepted (Board Agent stub in M7)."""
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.request_board_changes(
            instructions=[{"intent": "add_topic", "description": "Add pain point about manual approvals"}]
        )
        assert result["accepted"] is True
        assert result["instruction_count"] == 1
        assert len(plugin.board_instructions) == 1

    @pytest.mark.asyncio
    async def test_request_board_changes_empty_rejected(self):
        plugin = FacilitatorPlugin(idea_id="idea-1")
        result = await plugin.request_board_changes(instructions=[])
        assert "error" in result


# ── FacilitatorAgent mock mode ──


class TestFacilitatorAgentMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        """FacilitatorAgent.process() in mock mode returns fixture data."""
        from pathlib import Path

        settings.AI_MOCK_MODE = True
        # BASE_DIR in tests points to gateway; override to AI service root
        settings.BASE_DIR = Path(__file__).resolve().parent.parent
        agent = FacilitatorAgent()
        result = await agent.process({"idea_id": "test-idea"})
        assert "response" in result
        assert result["delegations"] == []


# ── System prompt rendering ──


class TestSystemPromptRendering:
    def test_interactive_mode_prompt(self):
        prompt = build_system_prompt({
            "agent_mode": "interactive",
            "idea_title": "Invoice Automation",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "facilitator_bucket_content": "Systems: SAP, DocuSign",
            "recent_messages_formatted": "(no messages yet)",
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
            "no_messages_yet": True,
            "creator_language": "German",
        })
        assert "INTERACTIVE MODE RULES" in prompt
        assert "Invoice Automation" in prompt
        assert "SAP, DocuSign" in prompt
        assert "German" in prompt
        assert "SILENT MODE RULES" not in prompt

    def test_prompt_with_compressed_summary(self):
        prompt = build_system_prompt({
            "agent_mode": "interactive",
            "idea_title": "Test",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "chat_summary": "Previous discussion about workflows.",
            "recent_messages_formatted": "",
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
        })
        assert "<compressed_summary>" in prompt
        assert "Previous discussion about workflows." in prompt
        assert "context extension agent" in prompt

    def test_prompt_with_delegation_results(self):
        prompt = build_system_prompt({
            "agent_mode": "interactive",
            "idea_title": "Test",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "delegation_results": "Commerz Real uses SAP for ERP.",
            "recent_messages_formatted": "",
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
        })
        assert "<delegation_results>" in prompt
        assert "Commerz Real uses SAP for ERP." in prompt

    def test_prompt_multi_user(self):
        prompt = build_system_prompt({
            "agent_mode": "interactive",
            "idea_title": "Test",
            "idea_state": "brainstorming",
            "title_manually_edited": False,
            "is_multi_user": True,
            "user_names_list": "Lisa, Max",
            "recent_messages_formatted": "",
            "board_nodes_formatted": "(empty board)",
            "board_connections_formatted": "(no connections)",
        })
        assert "Lisa, Max" in prompt
        assert "Multiple users" in prompt
