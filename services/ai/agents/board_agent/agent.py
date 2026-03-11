"""BoardAgent — executes spatial board operations from Facilitator instructions.

Extends BaseAgent with SK function-calling loop (max_auto_invoke_attempts=10),
system prompt rendering, and the BoardPlugin (8 tools).
"""

from __future__ import annotations

import logging
from typing import Any

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

from agents.base import BaseAgent
from agents.board_agent.plugins import BoardPlugin
from agents.board_agent.prompt import build_system_prompt
from kernel.model_router import get_deployment
from kernel.sk_factory import create_kernel

logger = logging.getLogger(__name__)


class BoardAgent(BaseAgent):
    """Board Agent — manipulates the digital board via 8 tools.

    Uses SK's automatic function-calling loop with max_auto_invoke_attempts=10
    because complex board reorganizations may need many rounds.
    """

    agent_name: str = "board_agent"
    fixture_file: str = "board_agent_response.json"

    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the Board Agent via Semantic Kernel function-calling loop.

        Args:
            input_data: Dict with keys:
                - idea_id: str
                - board_state: dict (nodes, connections)
                - instructions: list[dict] (semantic intent from Facilitator)
        """
        idea_id: str = input_data["idea_id"]
        board_state: dict[str, Any] = input_data.get("board_state", {})
        instructions: list[dict[str, Any]] = input_data.get("instructions", [])

        # Build system prompt
        system_prompt = build_system_prompt(board_state, instructions)

        # Create kernel with default tier deployment
        deployment = get_deployment("default")
        kernel = create_kernel(deployment, service_id="board_agent")

        # Create and register plugin
        plugin = BoardPlugin(idea_id=idea_id, board_state=board_state)
        kernel.add_plugin(plugin, plugin_name="Board")

        # Configure execution settings
        service = kernel.get_service("board_agent")
        assert isinstance(service, AzureChatCompletion)

        settings = service.get_prompt_execution_settings_class()(service_id="board_agent")
        settings.max_tokens = 1000
        settings.temperature = 0.3
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto(
            auto_invoke=True,
            maximum_auto_invoke_attempts=10,
        )

        # Build chat history with system prompt and instruction summary
        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(
            "Execute the board instructions provided in the system prompt. "
            "Use the available tools to create, update, move, or delete nodes and connections as needed."
        )

        # Invoke SK chat completion (result unused — mutations tracked via plugin)
        await service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings,
            kernel=kernel,
        )

        return {
            "mutations": plugin.mutations,
            "mutation_count": len(plugin.mutations),
        }
