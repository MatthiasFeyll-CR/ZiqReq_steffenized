"""BrdGenerationPipeline — orchestrates BRD generation.

Steps:
  1. Load BRD draft state (locked sections, gaps toggle) via CoreClient
  2. Assemble context for SummarizingAIAgent
  3. Invoke SummarizingAIAgent
  4. Post-processing fabrication validation
  5. Publish ai.brd.generated event
  6. Publish ai.security.fabrication_flag events (if any)
  7. Cleanup version / abort flag
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from events.publishers import publish_event
from grpc_clients.core_client import CoreClient
from processing.fabrication_validator import FabricationValidator, build_source_material

logger = logging.getLogger(__name__)


class BrdPipelineAborted(Exception):
    """Raised when the pipeline detects a version mismatch or abort flag."""


class BrdGenerationPipeline:
    """Orchestrates BRD generation with context assembly and fabrication validation.

    Attributes:
        _versions: Per-idea processing version counters.
        _abort_flags: Per-idea abort flags.
    """

    # Class-level state shared across pipeline instances (per-process)
    _versions: dict[str, int] = {}
    _abort_flags: dict[str, bool] = {}

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self.core_client = core_client or CoreClient()
        self.fabrication_validator = FabricationValidator()

    # ── Public API ──

    async def execute(
        self,
        idea_id: str,
        mode: str = "full_generation",
        section_name: str | None = None,
    ) -> dict[str, Any]:
        """Run the BRD generation pipeline.

        Args:
            idea_id: The idea UUID string.
            mode: Generation mode (full_generation, selective_regeneration,
                  section_regeneration).
            section_name: Required for section_regeneration mode.

        Returns:
            Dict with processing_id, status, sections, readiness_evaluation,
            and fabrication_flags.
        """
        processing_id = str(uuid.uuid4())
        version = self._start_processing(idea_id)

        logger.info(
            "BRD pipeline started for idea %s (processing_id=%s, mode=%s, version=%d)",
            idea_id, processing_id, mode, version,
        )

        try:
            # Step 1: Load idea context and BRD draft state
            self._check_abort(idea_id, version, step=1)
            context_data = await self._step_load_context(idea_id)

            # Step 2: Assemble agent input
            self._check_abort(idea_id, version, step=2)
            input_data = self._step_assemble_context(
                context_data, mode, section_name,
            )

            # Step 3: Invoke SummarizingAIAgent
            self._check_abort(idea_id, version, step=3)
            agent_result = await self._step_invoke_agent(input_data)

            # Step 4: Fabrication validation
            self._check_abort(idea_id, version, step=4)
            fabrication_flags = self._step_validate_fabrication(
                agent_result, context_data,
            )

            # Step 5: Publish ai.brd.generated event
            self._check_abort(idea_id, version, step=5)
            await self._step_publish_generated(
                idea_id, mode, agent_result, fabrication_flags,
            )

            # Step 6: Publish fabrication flag events
            if fabrication_flags:
                await self._step_publish_fabrication_flags(
                    idea_id, fabrication_flags,
                )

            # Step 7: Cleanup
            self._step_cleanup(idea_id)

            logger.info("BRD pipeline completed for idea %s", idea_id)
            return {
                "processing_id": processing_id,
                "status": "completed",
                "sections": {
                    k.removeprefix("section_"): v for k, v in agent_result.items()
                    if k.startswith("section_")
                },
                "readiness_evaluation": agent_result.get(
                    "readiness_evaluation", {}
                ),
                "fabrication_flags": fabrication_flags,
            }

        except BrdPipelineAborted:
            logger.warning(
                "BRD pipeline aborted for idea %s (version=%d)",
                idea_id, version,
            )
            return {
                "processing_id": processing_id,
                "status": "aborted",
                "sections": None,
                "readiness_evaluation": None,
                "fabrication_flags": [],
            }

        except Exception:
            logger.exception(
                "BRD pipeline failed for idea %s", idea_id,
            )
            self._step_cleanup(idea_id)
            return {
                "processing_id": processing_id,
                "status": "error",
                "sections": None,
                "readiness_evaluation": None,
                "fabrication_flags": [],
            }

    # ── Version tracking & abort ──

    def _start_processing(self, idea_id: str) -> int:
        """Increment and return version for this idea."""
        current = self._versions.get(idea_id, 0) + 1
        self._versions[idea_id] = current
        self._abort_flags[idea_id] = False
        return current

    def _check_abort(self, idea_id: str, expected_version: int, step: int) -> None:
        """Check version mismatch or abort flag before each step."""
        if self._abort_flags.get(idea_id, False):
            logger.info("BRD abort flag set for idea %s at step %d", idea_id, step)
            raise BrdPipelineAborted(f"Abort flag set at step {step}")

        current_version = self._versions.get(idea_id, 0)
        if current_version != expected_version:
            logger.info(
                "BRD version mismatch for idea %s at step %d: expected=%d, current=%d",
                idea_id, step, expected_version, current_version,
            )
            raise BrdPipelineAborted(
                f"Version mismatch at step {step}: "
                f"expected={expected_version}, current={current_version}"
            )

    def set_abort(self, idea_id: str) -> None:
        """Set the abort flag for an idea."""
        self._abort_flags[idea_id] = True
        logger.info("BRD abort flag set for idea %s", idea_id)

    def get_version(self, idea_id: str) -> int:
        """Get the current processing version for an idea."""
        return self._versions.get(idea_id, 0)

    # ── Step implementations ──

    async def _step_load_context(self, idea_id: str) -> dict[str, Any]:
        """Step 1: Load idea context and BRD draft state."""
        logger.info("BRD Step 1: Loading context for idea %s", idea_id)

        idea_context = self.core_client.get_idea_context(
            idea_id,
            recent_message_limit=20,
            include_brd_draft=True,
        )

        brd_draft = self.core_client.get_brd_draft(idea_id)

        return {
            "idea_context": idea_context,
            "brd_draft": brd_draft,
        }

    def _step_assemble_context(
        self,
        context_data: dict[str, Any],
        mode: str,
        section_name: str | None,
    ) -> dict[str, Any]:
        """Step 2: Assemble input data for SummarizingAIAgent."""
        logger.info("BRD Step 2: Assembling context")

        idea_context = context_data["idea_context"]
        brd_draft = context_data["brd_draft"]

        # Extract chat summary
        chat_summary_data = idea_context.get("chat_summary")
        chat_summary = ""
        if chat_summary_data:
            chat_summary = chat_summary_data.get("summary_text", "")

        recent_messages = idea_context.get("recent_messages", [])

        # Extract locked sections and gaps toggle from BRD draft
        section_locks = brd_draft.get("section_locks", {})
        locked_sections = [
            key for key, locked in section_locks.items() if locked
        ]
        allow_information_gaps = brd_draft.get("allow_information_gaps", False)

        return {
            "mode": mode,
            "chat_summary": chat_summary,
            "recent_messages": recent_messages,
            "locked_sections": locked_sections,
            "allow_information_gaps": allow_information_gaps,
            "section_name": section_name,
        }

    async def _step_invoke_agent(
        self, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 3: Invoke SummarizingAIAgent."""
        from agents.summarizing_ai.agent import SummarizingAIAgent

        logger.info("BRD Step 3: Invoking SummarizingAIAgent (mode=%s)", input_data["mode"])
        agent = SummarizingAIAgent()
        return await agent.process(input_data)

    def _step_validate_fabrication(
        self,
        agent_result: dict[str, Any],
        context_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Step 4: Post-processing fabrication validation."""
        logger.info("BRD Step 4: Validating for fabrication")

        idea_context = context_data["idea_context"]

        chat_summary_data = idea_context.get("chat_summary")
        chat_summary = ""
        if chat_summary_data:
            chat_summary = chat_summary_data.get("summary_text", "")

        recent_messages = idea_context.get("recent_messages", [])

        source_material = build_source_material(
            chat_summary, recent_messages,
        )

        # Extract only section fields for validation
        sections = {
            k: v for k, v in agent_result.items()
            if k.startswith("section_")
        }

        return self.fabrication_validator.validate(sections, source_material)

    async def _step_publish_generated(
        self,
        idea_id: str,
        mode: str,
        agent_result: dict[str, Any],
        fabrication_flags: list[dict[str, Any]],
    ) -> None:
        """Step 5: Publish ai.brd.generated event."""
        logger.info("BRD Step 5: Publishing ai.brd.generated for idea %s", idea_id)

        sections = {
            k.removeprefix("section_"): v for k, v in agent_result.items()
            if k.startswith("section_")
        }

        await publish_event("ai.brd.generated", {
            "idea_id": idea_id,
            "mode": mode,
            "sections": sections,
            "readiness_evaluation": agent_result.get("readiness_evaluation", {}),
            "fabrication_flags": fabrication_flags,
        })

    async def _step_publish_fabrication_flags(
        self,
        idea_id: str,
        fabrication_flags: list[dict[str, Any]],
    ) -> None:
        """Step 6: Publish ai.security.fabrication_flag events for monitoring."""
        logger.info(
            "BRD Step 6: Publishing %d fabrication flag events for idea %s",
            len(fabrication_flags), idea_id,
        )
        for flag in fabrication_flags:
            await publish_event("ai.security.fabrication_flag", {
                "idea_id": idea_id,
                "section": flag["section"],
                "ungrounded_keywords": flag["ungrounded_keywords"],
                "match_ratio": flag["match_ratio"],
            })

    def _step_cleanup(self, idea_id: str) -> None:
        """Step 7: Cleanup — clear abort flag."""
        logger.info("BRD Step 7: Cleanup for idea %s", idea_id)
        self._abort_flags.pop(idea_id, None)
