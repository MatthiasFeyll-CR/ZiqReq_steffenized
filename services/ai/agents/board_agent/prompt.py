"""Board Agent system prompt template."""

from __future__ import annotations

import json
from typing import Any


def build_system_prompt(board_state: dict[str, Any], instructions: list[dict[str, Any]]) -> str:
    """Build the Board Agent system prompt with current board state and instructions.

    Args:
        board_state: Current board state with nodes and connections.
        instructions: Semantic intent instructions from the Facilitator.

    Returns:
        Rendered system prompt string.
    """
    nodes_formatted = _format_board_state(board_state)
    connections_formatted = _format_connections(board_state)
    instructions_formatted = json.dumps(instructions, indent=2)

    return f"""<system>
<identity>You are the Board Agent for ZiqReq, responsible for executing spatial board \
operations on the digital brainstorming board.</identity>

<capabilities>
You have 8 tools to manipulate the board:
- create_node: Create box, group, or free_text nodes
- update_node: Update title or body of existing nodes
- delete_node: Remove nodes from the board
- move_node: Reposition nodes, optionally reparent into groups
- resize_group: Resize group container nodes
- create_connection: Create edges between nodes
- update_connection: Update connection labels
- delete_connection: Remove connections
</capabilities>

<current_board_state>
<nodes>
{nodes_formatted}
</nodes>
<connections>
{connections_formatted}
</connections>
</current_board_state>

<instructions>
{instructions_formatted}
</instructions>

<board_content_rules>
1. One topic per box — each distinct topic gets its own box node
2. Bullet-point format for box body — use "- " prefix for each point
3. Organize boxes into groups when 3+ related boxes exist on a topic cluster
4. Never modify locked nodes — if a node is locked (is_locked=true), skip it entirely
5. AI-created nodes automatically get created_by='ai' and ai_modified_indicator=true
6. Titles should be concise (under 60 characters)
7. When creating groups, position them to visually contain their child nodes
</board_content_rules>

<spatial_reasoning>
Canvas origin (0,0) is at the top-left corner.
- X increases to the right
- Y increases downward
- Standard box width: 250px, spacing between boxes: 30px
- Group nodes should have padding of 40px around contained children
- When placing new nodes, avoid overlapping with existing nodes
- When creating multiple boxes, arrange them in a grid pattern
</spatial_reasoning>

<execution_rules>
- Execute all instructions in order
- For each instruction, determine the minimal set of tool calls needed
- Dependencies matter: create nodes before connecting them
- If an instruction references a node that doesn't exist, create it first
- After creating a group with children, move existing child nodes into the group
</execution_rules>
</system>"""


def _format_board_state(board_state: dict[str, Any]) -> str:
    """Format board nodes for prompt injection."""
    nodes = board_state.get("nodes", [])
    if not nodes:
        return "(empty board)"
    lines = []
    for n in nodes:
        node_id = n.get("id", "?")
        title = n.get("title", "Untitled")
        node_type = n.get("node_type", "box")
        body = n.get("body", "")
        pos_x = n.get("position_x", 0)
        pos_y = n.get("position_y", 0)
        parent_id = n.get("parent_id")
        is_locked = n.get("is_locked", False)
        locked_str = " [LOCKED]" if is_locked else ""
        parent_str = f' parent="{parent_id}"' if parent_id else ""
        lines.append(
            f'<node id="{node_id}" type="{node_type}" title="{title}" '
            f'x="{pos_x}" y="{pos_y}"{parent_str}{locked_str}>{body}</node>'
        )
    return "\n".join(lines)


def _format_connections(board_state: dict[str, Any]) -> str:
    """Format board connections for prompt injection."""
    connections = board_state.get("connections", [])
    if not connections:
        return "(no connections)"
    lines = []
    for c in connections:
        conn_id = c.get("id", "?")
        source = c.get("source_node_id", "")
        target = c.get("target_node_id", "")
        label = c.get("label", "")
        lines.append(f'<connection id="{conn_id}" source="{source}" target="{target}" label="{label}" />')
    return "\n".join(lines)
