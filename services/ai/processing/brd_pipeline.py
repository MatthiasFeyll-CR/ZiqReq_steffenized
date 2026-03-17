"""BrdGenerationPipeline — orchestrates requirements document generation.

Steps:
  1. Load project context and draft state via CoreClient
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
    """Orchestrates requirements document generation with context assembly and fabrication validation.

    Attributes:
        _versions: Per-project processing version counters.
        _abort_flags: Per-project abort flags.
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
        project_id: str,
        mode: str = "full_generation",
        section_name: str | None = None,
        item_id: str | None = None,
    ) -> dict[str, Any]:
        """Run the requirements document generation pipeline.

        Args:
            project_id: The project UUID string.
            mode: Generation mode (full_generation, selective_regeneration,
                  item_regeneration).
            section_name: Deprecated, kept for backward compatibility.
            item_id: Required for item_regeneration mode.

        Returns:
            Dict with processing_id, status, title, short_description,
            structure, readiness_evaluation, and fabrication_flags.
        """
        processing_id = str(uuid.uuid4())
        version = self._start_processing(project_id)

        logger.info(
            "BRD pipeline started for project %s (processing_id=%s, mode=%s, version=%d)",
            project_id, processing_id, mode, version,
        )

        try:
            # Step 1: Load project context and draft state
            self._check_abort(project_id, version, step=1)
            context_data = await self._step_load_context(project_id)

            # Step 2: Assemble agent input
            self._check_abort(project_id, version, step=2)
            input_data = self._step_assemble_context(
                context_data, mode, item_id=item_id,
            )

            # Step 3: Invoke SummarizingAIAgent
            self._check_abort(project_id, version, step=3)
            agent_result = await self._step_invoke_agent(input_data)

            # Step 4: Fabrication validation
            self._check_abort(project_id, version, step=4)
            fabrication_flags = self._step_validate_fabrication(
                agent_result, context_data,
            )

            # Step 5: Publish ai.brd.generated event
            self._check_abort(project_id, version, step=5)
            await self._step_publish_generated(
                project_id, mode, agent_result, fabrication_flags,
            )

            # Step 6: Publish fabrication flag events
            if fabrication_flags:
                await self._step_publish_fabrication_flags(
                    project_id, fabrication_flags,
                )

            # Step 7: Cleanup
            self._step_cleanup(project_id)

            logger.info("BRD pipeline completed for project %s", project_id)
            return {
                "processing_id": processing_id,
                "status": "completed",
                "title": agent_result.get("title", ""),
                "short_description": agent_result.get("short_description", ""),
                "structure": agent_result.get("structure", []),
                "readiness_evaluation": agent_result.get(
                    "readiness_evaluation", {}
                ),
                "fabrication_flags": fabrication_flags,
            }

        except BrdPipelineAborted:
            logger.warning(
                "BRD pipeline aborted for project %s (version=%d)",
                project_id, version,
            )
            return {
                "processing_id": processing_id,
                "status": "aborted",
                "title": None,
                "short_description": None,
                "structure": None,
                "readiness_evaluation": None,
                "fabrication_flags": [],
            }

        except Exception:
            logger.exception(
                "BRD pipeline failed for project %s", project_id,
            )
            self._step_cleanup(project_id)
            return {
                "processing_id": processing_id,
                "status": "error",
                "title": None,
                "short_description": None,
                "structure": None,
                "readiness_evaluation": None,
                "fabrication_flags": [],
            }

    # ── Version tracking & abort ──

    def _start_processing(self, project_id: str) -> int:
        """Increment and return version for this project."""
        current = self._versions.get(project_id, 0) + 1
        self._versions[project_id] = current
        self._abort_flags[project_id] = False
        return current

    def _check_abort(self, project_id: str, expected_version: int, step: int) -> None:
        """Check version mismatch or abort flag before each step."""
        if self._abort_flags.get(project_id, False):
            logger.info("BRD abort flag set for project %s at step %d", project_id, step)
            raise BrdPipelineAborted(f"Abort flag set at step {step}")

        current_version = self._versions.get(project_id, 0)
        if current_version != expected_version:
            logger.info(
                "BRD version mismatch for project %s at step %d: expected=%d, current=%d",
                project_id, step, expected_version, current_version,
            )
            raise BrdPipelineAborted(
                f"Version mismatch at step {step}: "
                f"expected={expected_version}, current={current_version}"
            )

    def set_abort(self, project_id: str) -> None:
        """Set the abort flag for a project."""
        self._abort_flags[project_id] = True
        logger.info("BRD abort flag set for project %s", project_id)

    def get_version(self, project_id: str) -> int:
        """Get the current processing version for a project."""
        return self._versions.get(project_id, 0)

    # ── Step implementations ──

    async def _step_load_context(self, project_id: str) -> dict[str, Any]:
        """Step 1: Load project context and draft state."""
        logger.info("BRD Step 1: Loading context for project %s", project_id)

        project_context = self.core_client.get_project_context(
            project_id,
            recent_message_limit=20,
            include_brd_draft=True,
        )

        brd_draft = self.core_client.get_brd_draft(project_id)

        return {
            "project_context": project_context,
            "brd_draft": brd_draft,
        }

    def _step_assemble_context(
        self,
        context_data: dict[str, Any],
        mode: str,
        item_id: str | None = None,
    ) -> dict[str, Any]:
        """Step 2: Assemble input data for SummarizingAIAgent."""
        logger.info("BRD Step 2: Assembling context")

        project_context = context_data["project_context"]
        brd_draft = context_data["brd_draft"]

        chat_summary_data = project_context.get("chat_summary")
        chat_summary = ""
        if chat_summary_data:
            chat_summary = chat_summary_data.get("summary_text", "")

        recent_messages = project_context.get("recent_messages", [])

        # Extract project_type from project metadata
        project = project_context.get("project", {})
        project_type = project.get("project_type", "software")

        # Extract locked items and gaps toggle from draft
        item_locks = brd_draft.get("item_locks", {})
        allow_information_gaps = brd_draft.get("allow_information_gaps", False)

        return {
            "mode": mode,
            "project_type": project_type,
            "chat_summary": chat_summary,
            "recent_messages": recent_messages,
            "locked_items": item_locks,
            "allow_information_gaps": allow_information_gaps,
            "item_id": item_id,
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
        """Step 4: Post-processing fabrication validation.

        Extracts text content from the hierarchical structure and validates
        against source material.
        """
        logger.info("BRD Step 4: Validating for fabrication")

        project_context = context_data["project_context"]

        chat_summary_data = project_context.get("chat_summary")
        chat_summary = ""
        if chat_summary_data:
            chat_summary = chat_summary_data.get("summary_text", "")

        recent_messages = project_context.get("recent_messages", [])

        source_material = build_source_material(
            chat_summary, recent_messages,
        )

        # Extract text content from hierarchical structure for validation
        text_sections = _extract_text_for_validation(agent_result)

        return self.fabrication_validator.validate(text_sections, source_material)

    async def _step_publish_generated(
        self,
        project_id: str,
        mode: str,
        agent_result: dict[str, Any],
        fabrication_flags: list[dict[str, Any]],
    ) -> None:
        """Step 5: Publish ai.brd.generated event."""
        logger.info("BRD Step 5: Publishing ai.brd.generated for project %s", project_id)

        await publish_event("ai.brd.generated", {
            "project_id": project_id,
            "mode": mode,
            "title": agent_result.get("title", ""),
            "short_description": agent_result.get("short_description", ""),
            "structure": agent_result.get("structure", []),
            "readiness_evaluation": agent_result.get("readiness_evaluation", {}),
            "fabrication_flags": fabrication_flags,
        })

    async def _step_publish_fabrication_flags(
        self,
        project_id: str,
        fabrication_flags: list[dict[str, Any]],
    ) -> None:
        """Step 6: Publish ai.security.fabrication_flag events for monitoring."""
        logger.info(
            "BRD Step 6: Publishing %d fabrication flag events for project %s",
            len(fabrication_flags), project_id,
        )
        for flag in fabrication_flags:
            await publish_event("ai.security.fabrication_flag", {
                "project_id": project_id,
                "section": flag["section"],
                "ungrounded_keywords": flag["ungrounded_keywords"],
                "match_ratio": flag["match_ratio"],
            })

    def _step_cleanup(self, project_id: str) -> None:
        """Step 7: Cleanup — clear abort flag."""
        logger.info("BRD Step 7: Cleanup for project %s", project_id)
        self._abort_flags.pop(project_id, None)


def _extract_text_for_validation(agent_result: dict[str, Any]) -> dict[str, str | None]:
    """Extract text fields from hierarchical structure for fabrication validation.

    Returns a dict with section-like keys mapping to text content,
    compatible with FabricationValidator.validate().
    """
    sections: dict[str, str | None] = {}

    title = agent_result.get("title")
    if title:
        sections["section_title"] = title

    short_desc = agent_result.get("short_description")
    if short_desc:
        sections["section_short_description"] = short_desc

    structure = agent_result.get("structure", [])
    for item in structure:
        if not isinstance(item, dict):
            continue
        item_id = item.get("epic_id") or item.get("milestone_id") or "unknown"
        item_text = f"{item.get('title', '')} {item.get('description', '')}"
        sections[f"section_{item_id}"] = item_text

        children = item.get("stories", []) or item.get("packages", [])
        for child in children:
            if not isinstance(child, dict):
                continue
            child_id = child.get("story_id") or child.get("package_id") or "unknown"
            child_text = f"{child.get('title', '')} {child.get('description', '')}"
            sections[f"section_{child_id}"] = child_text

    return sections
