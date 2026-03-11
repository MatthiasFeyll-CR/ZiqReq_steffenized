"""Tests for the Board Agent (US-001).

Test IDs: T-2.17.01, T-2.17.02, T-2.17.03

These tests validate the BoardPlugin tools, prompt rendering, and
BoardAgent mock mode — all without hitting Azure OpenAI.
"""

from __future__ import annotations

import uuid

import pytest

from agents.board_agent.agent import BoardAgent
from agents.board_agent.plugins import BoardPlugin
from agents.board_agent.prompt import build_system_prompt
from events.publishers import clear_published_events, get_published_events


@pytest.fixture(autouse=True)
def _clear_events():
    """Clear published events before each test."""
    clear_published_events()
    yield
    clear_published_events()


def _make_node(
    node_id: str | None = None,
    node_type: str = "box",
    title: str = "Test Node",
    body: str = "",
    is_locked: bool = False,
    parent_id: str | None = None,
    position_x: float = 0.0,
    position_y: float = 0.0,
) -> dict:
    return {
        "id": node_id or str(uuid.uuid4()),
        "node_type": node_type,
        "title": title,
        "body": body,
        "is_locked": is_locked,
        "parent_id": parent_id,
        "position_x": position_x,
        "position_y": position_y,
    }


def _make_connection(
    conn_id: str | None = None,
    source_node_id: str = "src-1",
    target_node_id: str = "tgt-1",
    label: str = "",
) -> dict:
    return {
        "id": conn_id or str(uuid.uuid4()),
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "label": label,
    }


# ── T-2.17.01: Board Agent creates one topic per box ──


class TestCreateNode:
    """T-2.17.01: Board Agent creates one topic per box."""

    @pytest.mark.asyncio
    async def test_create_box_node_publishes_event(self):
        """T-2.17.01: create_node publishes ai.board.updated event."""
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.create_node(
            node_type="box",
            title="Manual Approvals",
            body="- Slow turnaround\n- Paper-based",
            position_x=100.0,
            position_y=200.0,
        )

        assert "node_id" in result
        assert len(plugin.mutations) == 1
        assert plugin.mutations[0]["action"] == "create_node"
        assert plugin.mutations[0]["node_type"] == "box"
        assert plugin.mutations[0]["title"] == "Manual Approvals"

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.board.updated"
        assert events[0]["idea_id"] == "idea-1"

    @pytest.mark.asyncio
    async def test_create_multiple_boxes_separate_topics(self):
        """T-2.17.01: Multiple topics get separate box nodes."""
        plugin = BoardPlugin(idea_id="idea-1")

        await plugin.create_node(node_type="box", title="Topic A", body="- Point 1")
        await plugin.create_node(node_type="box", title="Topic B", body="- Point 2")
        await plugin.create_node(node_type="box", title="Topic C", body="- Point 3")

        assert len(plugin.mutations) == 3
        titles = [m["title"] for m in plugin.mutations]
        assert titles == ["Topic A", "Topic B", "Topic C"]
        assert all(m["node_type"] == "box" for m in plugin.mutations)

    @pytest.mark.asyncio
    async def test_create_node_invalid_type_rejected(self):
        """Invalid node_type returns error."""
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.create_node(node_type="invalid", title="Oops")
        assert "error" in result
        assert result["error"]["code"] == "validation_error"
        assert len(plugin.mutations) == 0


# ── T-2.17.02: Board Agent uses bullet-point format for body ──


class TestBulletPointFormat:
    """T-2.17.02: Board Agent uses bullet-point format for body."""

    @pytest.mark.asyncio
    async def test_body_contains_bullet_points(self):
        """T-2.17.02: Box creation with bullet-point body."""
        plugin = BoardPlugin(idea_id="idea-1")
        bullet_body = "- First point\n- Second point\n- Third point"
        result = await plugin.create_node(
            node_type="box",
            title="Pain Points",
            body=bullet_body,
        )

        assert "node_id" in result
        assert len(plugin.mutations) == 1

    @pytest.mark.asyncio
    async def test_system_prompt_includes_bullet_rule(self):
        """T-2.17.02: System prompt instructs bullet-point format."""
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": []},
            instructions=[{"intent": "add_topic", "description": "Add pain points"}],
        )
        assert "Bullet-point format" in prompt
        assert "- " in prompt


# ── T-2.17.03: Board Agent organizes boxes into groups ──


class TestOrganizeIntoGroups:
    """T-2.17.03: Board Agent organizes boxes into groups."""

    @pytest.mark.asyncio
    async def test_create_group_node(self):
        """T-2.17.03: Group node can be created for organizing boxes."""
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.create_node(
            node_type="group",
            title="Pain Points",
            position_x=50.0,
            position_y=50.0,
            width=600.0,
            height=400.0,
        )

        assert "node_id" in result
        assert plugin.mutations[0]["node_type"] == "group"
        assert plugin.mutations[0]["title"] == "Pain Points"

    @pytest.mark.asyncio
    async def test_move_box_into_group(self):
        """T-2.17.03: Existing boxes can be moved into a group."""
        box_id = str(uuid.uuid4())
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={"nodes": [_make_node(node_id=box_id, title="Topic A")], "connections": []},
        )
        group_id = "group-1"
        result = await plugin.move_node(
            node_id=box_id,
            position_x=100.0,
            position_y=100.0,
            new_parent_id=group_id,
        )

        assert "parent_changed" in result
        assert len(plugin.mutations) == 1
        assert plugin.mutations[0]["action"] == "move_node"

    @pytest.mark.asyncio
    async def test_system_prompt_includes_group_rule(self):
        """T-2.17.03: System prompt instructs grouping when 3+ related boxes."""
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": []},
            instructions=[{"intent": "reorganize", "description": "Group related topics"}],
        )
        assert "groups" in prompt.lower()
        assert "3+" in prompt


# ── Locked node validation ──


class TestLockedNodeValidation:
    @pytest.mark.asyncio
    async def test_update_locked_node_rejected(self):
        """Locked nodes cannot be updated."""
        node_id = "locked-node-1"
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={
                "nodes": [_make_node(node_id=node_id, is_locked=True)],
                "connections": [],
            },
        )
        result = await plugin.update_node(node_id=node_id, title="New Title")
        assert "error" in result
        assert result["error"]["code"] == "node_locked"
        assert len(plugin.mutations) == 0
        assert len(get_published_events()) == 0

    @pytest.mark.asyncio
    async def test_delete_locked_node_rejected(self):
        """Locked nodes cannot be deleted."""
        node_id = "locked-node-1"
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={
                "nodes": [_make_node(node_id=node_id, is_locked=True)],
                "connections": [],
            },
        )
        result = await plugin.delete_node(node_id=node_id)
        assert "error" in result
        assert result["error"]["code"] == "node_locked"
        assert len(plugin.mutations) == 0

    @pytest.mark.asyncio
    async def test_move_locked_node_rejected(self):
        """Locked nodes cannot be moved."""
        node_id = "locked-node-1"
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={
                "nodes": [_make_node(node_id=node_id, is_locked=True)],
                "connections": [],
            },
        )
        result = await plugin.move_node(node_id=node_id, position_x=100.0, position_y=100.0)
        assert "error" in result
        assert result["error"]["code"] == "node_locked"
        assert len(plugin.mutations) == 0


# ── Connection operations ──


class TestConnectionOperations:
    @pytest.mark.asyncio
    async def test_create_connection_publishes_event(self):
        """create_connection publishes ai.board.updated event."""
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.create_connection(
            source_node_id="node-a",
            target_node_id="node-b",
            label="depends on",
        )
        assert "connection_id" in result
        assert len(plugin.mutations) == 1
        assert plugin.mutations[0]["action"] == "create_connection"

        events = get_published_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "ai.board.updated"

    @pytest.mark.asyncio
    async def test_update_connection(self):
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.update_connection(connection_id="conn-1", label="new label")
        assert result["success"] is True
        assert plugin.mutations[0]["action"] == "update_connection"
        assert plugin.mutations[0]["label"] == "new label"

    @pytest.mark.asyncio
    async def test_delete_connection(self):
        plugin = BoardPlugin(idea_id="idea-1")
        result = await plugin.delete_connection(connection_id="conn-1")
        assert result["success"] is True
        assert plugin.mutations[0]["action"] == "delete_connection"


# ── Resize group ──


class TestResizeGroup:
    @pytest.mark.asyncio
    async def test_resize_group_succeeds(self):
        node_id = "group-1"
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={
                "nodes": [_make_node(node_id=node_id, node_type="group", title="Group A")],
                "connections": [],
            },
        )
        result = await plugin.resize_group(node_id=node_id, width=600.0, height=400.0)
        assert result["success"] is True
        assert plugin.mutations[0]["action"] == "resize_group"

    @pytest.mark.asyncio
    async def test_resize_non_group_rejected(self):
        """resize_group on a box node returns error."""
        node_id = "box-1"
        plugin = BoardPlugin(
            idea_id="idea-1",
            board_state={
                "nodes": [_make_node(node_id=node_id, node_type="box", title="Box A")],
                "connections": [],
            },
        )
        result = await plugin.resize_group(node_id=node_id, width=600.0, height=400.0)
        assert "error" in result
        assert result["error"]["code"] == "validation_error"


# ── System prompt rendering ──


class TestSystemPrompt:
    def test_prompt_includes_board_state(self):
        """System prompt renders current board state."""
        node = _make_node(title="Existing Box", body="- Some content")
        prompt = build_system_prompt(
            board_state={"nodes": [node], "connections": []},
            instructions=[],
        )
        assert "Existing Box" in prompt
        assert "Some content" in prompt

    def test_prompt_includes_instructions(self):
        """System prompt renders instructions."""
        instructions = [
            {"intent": "add_topic", "description": "Add a box about automation"},
        ]
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": []},
            instructions=instructions,
        )
        assert "add_topic" in prompt
        assert "automation" in prompt

    def test_prompt_includes_locked_indicator(self):
        """System prompt marks locked nodes."""
        node = _make_node(title="Locked Node", is_locked=True)
        prompt = build_system_prompt(
            board_state={"nodes": [node], "connections": []},
            instructions=[],
        )
        assert "LOCKED" in prompt

    def test_prompt_includes_spatial_reasoning(self):
        """System prompt includes spatial reasoning rules."""
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": []},
            instructions=[],
        )
        assert "spatial_reasoning" in prompt
        assert "origin (0,0)" in prompt

    def test_prompt_empty_board(self):
        """System prompt handles empty board."""
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": []},
            instructions=[],
        )
        assert "(empty board)" in prompt
        assert "(no connections)" in prompt


# ── BoardAgent mock mode ──


class TestBoardAgentMockMode:
    @pytest.mark.asyncio
    async def test_mock_mode_returns_fixture(self, settings):
        """BoardAgent.process() in mock mode returns fixture data."""
        from pathlib import Path

        settings.AI_MOCK_MODE = True
        settings.BASE_DIR = Path(__file__).resolve().parent.parent
        agent = BoardAgent()
        result = await agent.process({
            "idea_id": "test-idea",
            "board_state": {"nodes": [], "connections": []},
            "instructions": [{"intent": "add_topic", "description": "test"}],
        })
        assert "mutations" in result
        assert result["mutation_count"] == 3
        assert result["mutations"][0]["action"] == "create_node"


# ── Board state formatting ──


class TestBoardStateFormatting:
    def test_format_nodes_with_parent(self):
        """Nodes with parent_id show parent attribute in prompt."""
        node = _make_node(title="Child", parent_id="parent-1")
        prompt = build_system_prompt(
            board_state={"nodes": [node], "connections": []},
            instructions=[],
        )
        assert 'parent="parent-1"' in prompt

    def test_format_connections(self):
        """Connections are rendered in prompt."""
        conn = _make_connection(source_node_id="a", target_node_id="b", label="relates to")
        prompt = build_system_prompt(
            board_state={"nodes": [], "connections": [conn]},
            instructions=[],
        )
        assert 'source="a"' in prompt
        assert 'target="b"' in prompt
        assert 'label="relates to"' in prompt
