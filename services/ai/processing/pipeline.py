"""ChatProcessingPipeline (7-step) — end-to-end AI processing orchestrator.

Steps:
  1. Load idea state via GetIdeaContext gRPC
  2. Assemble context for Facilitator
  3. Invoke Facilitator agent
  4. If delegation requested → invoke delegate (M7 stub) → re-invoke Facilitator
  5. If board changes requested → invoke Board Agent with fresh board state
  6. Publish ai.processing.complete
  7. Cleanup version / abort flag
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from events.publishers import publish_event
from grpc_clients.core_client import CoreClient
from processing.context_assembler import ContextAssembler

logger = logging.getLogger(__name__)


class PipelineAborted(Exception):
    """Raised when the pipeline detects a version mismatch or abort flag."""


class ChatProcessingPipeline:
    """Orchestrates the 7-step chat processing pipeline.

    Attributes:
        _versions: Per-idea processing version counters.
        _abort_flags: Per-idea abort flags (set when new message arrives mid-processing).
    """

    # Class-level state shared across pipeline instances (per-process)
    _versions: dict[str, int] = {}
    _abort_flags: dict[str, bool] = {}

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self.core_client = core_client or CoreClient()
        self.context_assembler = ContextAssembler()

    # ── Public API ──

    async def execute(self, idea_id: str) -> dict[str, Any]:
        """Run the full 7-step pipeline for a given idea.

        Returns:
            Dict with processing_id, status, and result details.

        Raises:
            PipelineAborted: If version mismatch or abort flag detected.
        """
        processing_id = str(uuid.uuid4())
        version = self._start_processing(idea_id)

        logger.info(
            "Pipeline started for idea %s (processing_id=%s, version=%d)",
            idea_id, processing_id, version,
        )

        try:
            # Step 1: Load idea state
            self._check_abort(idea_id, version, step=1)
            idea_context_response = await self._step_load_context(idea_id)

            # Step 2: Assemble context
            self._check_abort(idea_id, version, step=2)
            input_data = self._step_assemble_context(idea_id, idea_context_response)

            # Step 3: Invoke Facilitator
            self._check_abort(idea_id, version, step=3)
            facilitator_result = await self._step_invoke_facilitator(input_data)

            # Step 4: Delegation continuation
            self._check_abort(idea_id, version, step=4)
            facilitator_result = await self._step_delegation(
                idea_id, input_data, facilitator_result,
            )

            # Step 5: Board Agent
            self._check_abort(idea_id, version, step=5)
            await self._step_board_agent(idea_id, facilitator_result)

            # Step 6: Publish completion
            self._check_abort(idea_id, version, step=6)
            await self._step_publish_complete(idea_id)

            # Step 7: Cleanup
            self._step_cleanup(idea_id)

            logger.info("Pipeline completed for idea %s", idea_id)
            return {
                "processing_id": processing_id,
                "status": "completed",
                "result": facilitator_result,
            }

        except PipelineAborted:
            logger.warning(
                "Pipeline aborted for idea %s (version=%d)", idea_id, version,
            )
            return {
                "processing_id": processing_id,
                "status": "aborted",
                "result": None,
            }

    # ── Version tracking & abort ──

    def _start_processing(self, idea_id: str) -> int:
        """Increment and return version for this idea."""
        current = self._versions.get(idea_id, 0) + 1
        self._versions[idea_id] = current
        self._abort_flags[idea_id] = False
        return current

    def _check_abort(self, idea_id: str, expected_version: int, step: int) -> None:
        """Check version mismatch or abort flag before each step.

        Raises PipelineAborted if stale or aborted.
        """
        if self._abort_flags.get(idea_id, False):
            logger.info("Abort flag set for idea %s at step %d", idea_id, step)
            raise PipelineAborted(f"Abort flag set at step {step}")

        current_version = self._versions.get(idea_id, 0)
        if current_version != expected_version:
            logger.info(
                "Version mismatch for idea %s at step %d: expected=%d, current=%d",
                idea_id, step, expected_version, current_version,
            )
            raise PipelineAborted(
                f"Version mismatch at step {step}: "
                f"expected={expected_version}, current={current_version}"
            )

    def set_abort(self, idea_id: str) -> None:
        """Set the abort flag for an idea (called when new message arrives mid-processing)."""
        self._abort_flags[idea_id] = True
        logger.info("Abort flag set for idea %s", idea_id)

    def get_version(self, idea_id: str) -> int:
        """Get the current processing version for an idea."""
        return self._versions.get(idea_id, 0)

    # ── Step implementations ──

    async def _step_load_context(self, idea_id: str) -> dict[str, Any]:
        """Step 1: Load idea state via Core gRPC GetIdeaContext."""
        logger.info("Step 1: Loading context for idea %s", idea_id)
        return self.core_client.get_idea_context(idea_id)

    def _step_assemble_context(
        self, idea_id: str, idea_context_response: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 2: Assemble context for Facilitator."""
        logger.info("Step 2: Assembling context for idea %s", idea_id)
        return self.context_assembler.assemble(idea_id, idea_context_response)

    async def _step_invoke_facilitator(
        self, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 3: Invoke Facilitator agent."""
        from agents.facilitator.agent import FacilitatorAgent

        logger.info("Step 3: Invoking Facilitator for idea %s", input_data["idea_id"])
        agent = FacilitatorAgent()
        return await agent.process(input_data)

    async def _step_delegation(
        self,
        idea_id: str,
        input_data: dict[str, Any],
        facilitator_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 4: Handle delegation if requested.

        In M7, delegation agents are stubs — log 'not available' and
        re-invoke Facilitator with empty delegation results.
        """
        delegations = facilitator_result.get("delegations", [])
        if not delegations:
            logger.info("Step 4: No delegations for idea %s", idea_id)
            return facilitator_result

        for delegation in delegations:
            d_type = delegation.get("delegation_type", "unknown")
            d_query = delegation.get("query", "")
            logger.warning(
                "Step 4: Delegation '%s' requested for idea %s (query: %s) — "
                "agent not available in M7, returning empty results",
                d_type, idea_id, d_query,
            )

        # Re-invoke Facilitator with empty delegation results
        input_data["delegation_results"] = (
            "(Delegation agents are not available in this milestone. "
            "No additional context could be retrieved.)"
        )
        from agents.facilitator.agent import FacilitatorAgent

        logger.info("Step 4: Re-invoking Facilitator with delegation stub results")
        agent = FacilitatorAgent()
        return await agent.process(input_data)

    async def _step_board_agent(
        self, idea_id: str, facilitator_result: dict[str, Any],
    ) -> None:
        """Step 5: Invoke Board Agent with instructions + fresh board state."""
        board_instructions = facilitator_result.get("board_instructions", [])
        if not board_instructions:
            logger.info("Step 5: No board changes for idea %s", idea_id)
            return

        logger.info(
            "Step 5: Board Agent invoked for idea %s (%d instructions)",
            idea_id, len(board_instructions),
        )

        # Load fresh board state at invocation time (not cached from Step 1)
        board_state = self.core_client.get_board_state(idea_id)

        from agents.board_agent.agent import BoardAgent

        agent = BoardAgent()
        result = await agent.process({
            "idea_id": idea_id,
            "board_state": board_state,
            "instructions": board_instructions,
        })

        mutation_count = result.get("mutation_count", 0)
        logger.info(
            "Step 5: Board Agent completed for idea %s — %d mutations",
            idea_id, mutation_count,
        )

        # Publish board updated event with mutation details
        if mutation_count > 0:
            await publish_event("ai.board.updated", {
                "idea_id": idea_id,
                "mutation_count": mutation_count,
                "mutations": result.get("mutations", []),
            })

    async def _step_publish_complete(self, idea_id: str) -> None:
        """Step 6: Publish ai.processing.complete event."""
        logger.info("Step 6: Publishing completion for idea %s", idea_id)
        await publish_event("ai.processing.complete", {
            "idea_id": idea_id,
            "counter_reset": True,
        })

    def _step_cleanup(self, idea_id: str) -> None:
        """Step 7: Cleanup — clear abort flag."""
        logger.info("Step 7: Cleanup for idea %s", idea_id)
        self._abort_flags.pop(idea_id, None)
