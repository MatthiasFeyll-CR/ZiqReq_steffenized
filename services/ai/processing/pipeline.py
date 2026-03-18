"""ChatProcessingPipeline (7-step) — end-to-end AI processing orchestrator.

Steps:
  1. Load project state via GetProjectContext + GetRequirementsState
  2. Assemble context for Facilitator
  3. Invoke Facilitator agent
  4. If delegation requested → invoke delegate → re-invoke Facilitator
  5. Requirements structure mutation handler (apply Facilitator mutations via Core)
  6. Publish ai.processing.complete
  7. Cleanup version / abort flag
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from events.publishers import publish_event
from grpc_clients.core_client import CoreClient
from processing.context_assembler import ContextAssembler

logger = logging.getLogger(__name__)


class PipelineAborted(Exception):
    """Raised when the pipeline detects a version mismatch or abort flag."""


class ChatProcessingPipeline:
    """Orchestrates the 6-step chat processing pipeline.

    Attributes:
        _versions: Per-project processing version counters.
        _abort_flags: Per-project abort flags (set when new message arrives mid-processing).
    """

    # Class-level state shared across pipeline instances (per-process)
    _versions: dict[str, int] = {}
    _abort_flags: dict[str, bool] = {}

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self.core_client = core_client or CoreClient()
        self.context_assembler = ContextAssembler()

    # ── Public API ──

    async def execute(self, project_id: str) -> dict[str, Any]:
        """Run the full 6-step pipeline for a given project.

        Returns:
            Dict with processing_id, status, and result details.

        Raises:
            PipelineAborted: If version mismatch or abort flag detected.
        """
        processing_id = str(uuid.uuid4())
        version = self._start_processing(project_id)

        logger.info(
            "Pipeline started for project %s (processing_id=%s, version=%d)",
            project_id, processing_id, version,
        )

        try:
            # Step 1: Load project state + requirements state
            self._check_abort(project_id, version, step=1)
            project_context_response = await self._step_load_context(project_id)

            # Step 2: Assemble context
            self._check_abort(project_id, version, step=2)
            input_data = self._step_assemble_context(project_id, project_context_response)

            # Step 3: Invoke Facilitator
            self._check_abort(project_id, version, step=3)
            facilitator_result = await self._step_invoke_facilitator(input_data)

            # Step 4: Delegation continuation
            self._check_abort(project_id, version, step=4)
            facilitator_result = await self._step_delegation(
                project_id, input_data, facilitator_result,
            )

            # Fallback: if the LLM didn't call send_chat_message but returned
            # text, publish it as a chat response so the user always gets a reply.
            if not facilitator_result.get("chat_message_sent") and facilitator_result.get("response"):
                response_text = facilitator_result["response"].strip()
                if response_text:
                    logger.info(
                        "Facilitator did not call send_chat_message for project %s — "
                        "publishing text response as fallback",
                        project_id,
                    )
                    await publish_event("ai.chat_response.ready", {
                        "project_id": project_id,
                        "content": response_text,
                        "message_type": "regular",
                        "sender_type": "ai",
                        "ai_agent": "facilitator",
                    })

            # Step 5: Requirements structure mutation handler
            self._check_abort(project_id, version, step=5)
            await self._step_apply_mutations(project_id, facilitator_result)

            # Step 6: Publish completion
            self._check_abort(project_id, version, step=6)
            await self._step_publish_complete(project_id)

            # Step 7: Cleanup
            self._step_cleanup(project_id)

            logger.info("Pipeline completed for project %s", project_id)
            return {
                "processing_id": processing_id,
                "status": "completed",
                "result": facilitator_result,
            }

        except PipelineAborted:
            logger.warning(
                "Pipeline aborted for project %s (version=%d)", project_id, version,
            )
            return {
                "processing_id": processing_id,
                "status": "aborted",
                "result": None,
            }

    # ── Version tracking & abort ──

    def _start_processing(self, project_id: str) -> int:
        """Increment and return version for this project."""
        current = self._versions.get(project_id, 0) + 1
        self._versions[project_id] = current
        self._abort_flags[project_id] = False
        return current

    def _check_abort(self, project_id: str, expected_version: int, step: int) -> None:
        """Check version mismatch or abort flag before each step.

        Raises PipelineAborted if stale or aborted.
        """
        if self._abort_flags.get(project_id, False):
            logger.info("Abort flag set for project %s at step %d", project_id, step)
            raise PipelineAborted(f"Abort flag set at step {step}")

        current_version = self._versions.get(project_id, 0)
        if current_version != expected_version:
            logger.info(
                "Version mismatch for project %s at step %d: expected=%d, current=%d",
                project_id, step, expected_version, current_version,
            )
            raise PipelineAborted(
                f"Version mismatch at step {step}: "
                f"expected={expected_version}, current={current_version}"
            )

    def set_abort(self, project_id: str) -> None:
        """Set the abort flag for a project (called when new message arrives mid-processing)."""
        self._abort_flags[project_id] = True
        logger.info("Abort flag set for project %s", project_id)

    def get_version(self, project_id: str) -> int:
        """Get the current processing version for a project."""
        return self._versions.get(project_id, 0)

    # ── Step implementations ──

    # Extraction wait constants
    EXTRACTION_POLL_INTERVAL = 2  # seconds
    EXTRACTION_POLL_TIMEOUT = 30  # seconds

    async def _step_load_context(self, project_id: str) -> dict[str, Any]:
        """Step 1: Load project state via Core gRPC GetProjectContext + GetRequirementsState.

        Also waits for pending/processing attachment extractions on the most recent
        user message (the triggering message) to complete, polling every 2s up to 30s.
        """
        logger.info("Step 1: Loading context for project %s", project_id)
        project_context = self.core_client.get_project_context(project_id)

        # Wait for extraction of attachments on the triggering (most recent user) message
        project_context = await self._wait_for_extraction(project_id, project_context)

        # Fetch requirements state and inject into response for context_assembler
        try:
            requirements_state = self.core_client.get_requirements_state(project_id)
        except Exception:
            logger.warning("Failed to fetch requirements state for project %s", project_id)
            requirements_state = {}
        project_context["requirements_state"] = requirements_state

        # Ensure project_type is available in project metadata
        project = project_context.get("project", {})
        if "project_type" not in project:
            try:
                project["project_type"] = self.core_client._get_project_type(project_id)
            except Exception:
                project["project_type"] = "software"

        return project_context

    async def _wait_for_extraction(
        self, project_id: str, project_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Wait for pending/processing extractions on the triggering message's attachments.

        Polls every 2 seconds, up to 30 seconds. If timeout, proceeds with partial context.
        Returns an updated project_context with refreshed attachment statuses.
        """
        # Find the most recent user message (the triggering message)
        recent_messages = project_context.get("recent_messages", [])
        triggering_message = None
        for msg in reversed(recent_messages):
            if msg.get("sender_type") == "user":
                triggering_message = msg
                break

        if not triggering_message:
            return project_context

        attachments = triggering_message.get("attachments", [])
        if not attachments:
            return project_context

        # Check if any attachments are still pending/processing
        pending_statuses = {"pending", "processing"}
        pending_ids = [
            a["id"] for a in attachments
            if a.get("extraction_status") in pending_statuses
        ]

        if not pending_ids:
            return project_context

        logger.info(
            "Step 1: Waiting for extraction of %d attachments on triggering message",
            len(pending_ids),
        )

        start = time.monotonic()
        while time.monotonic() - start < self.EXTRACTION_POLL_TIMEOUT:
            await asyncio.sleep(self.EXTRACTION_POLL_INTERVAL)

            # Re-fetch context to check updated extraction statuses
            project_context = self.core_client.get_project_context(project_id)
            recent_messages = project_context.get("recent_messages", [])

            # Re-find triggering message
            triggering_message = None
            for msg in reversed(recent_messages):
                if msg.get("sender_type") == "user":
                    triggering_message = msg
                    break

            if not triggering_message:
                break

            attachments = triggering_message.get("attachments", [])
            still_pending = [
                a["id"] for a in attachments
                if a.get("extraction_status") in pending_statuses
                and a["id"] in pending_ids
            ]

            if not still_pending:
                logger.info("Step 1: All attachment extractions completed")
                break

            elapsed = time.monotonic() - start
            logger.debug(
                "Step 1: Still waiting for %d extractions (%.1fs elapsed)",
                len(still_pending), elapsed,
            )
        else:
            logger.warning(
                "Step 1: Extraction wait timed out after %ds, proceeding with partial context",
                self.EXTRACTION_POLL_TIMEOUT,
            )

        return project_context

    def _step_assemble_context(
        self, project_id: str, project_context_response: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 2: Assemble context for Facilitator."""
        logger.info("Step 2: Assembling context for project %s", project_id)
        return self.context_assembler.assemble(project_id, project_context_response)

    async def _step_invoke_facilitator(
        self, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 3: Invoke Facilitator agent."""
        from agents.facilitator.agent import FacilitatorAgent

        logger.info("Step 3: Invoking Facilitator for project %s", input_data["project_id"])
        agent = FacilitatorAgent()
        return await agent.process(input_data)

    async def _step_delegation(
        self,
        project_id: str,
        input_data: dict[str, Any],
        facilitator_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Step 4: Handle delegation if requested.

        Routes delegation to the appropriate agent (Context Agent or
        Context Extension) and re-invokes Facilitator with results.
        """
        delegations = facilitator_result.get("delegations", [])
        if not delegations:
            logger.info("Step 4: No delegations for project %s", project_id)
            return facilitator_result

        for delegation in delegations:
            d_type = delegation.get("delegation_type", "unknown")
            d_query = delegation.get("query", "")

            if d_type == "context_agent":
                delegation_results = await self._invoke_context_agent(
                    project_id, d_query,
                )
                input_data["delegation_results"] = delegation_results
            elif d_type == "context_extension":
                extension_results = await self._invoke_context_extension(
                    project_id, d_query,
                )
                input_data["extension_results"] = extension_results
            else:
                logger.warning(
                    "Step 4: Unknown delegation type '%s' for project %s",
                    d_type, project_id,
                )

        # Re-invoke Facilitator with delegation results
        from agents.facilitator.agent import FacilitatorAgent

        logger.info("Step 4: Re-invoking Facilitator with delegation results")
        agent = FacilitatorAgent()
        result = await agent.process(input_data)

        # Publish delegation complete event
        for delegation in delegations:
            await publish_event("ai.delegation.complete", {
                "project_id": project_id,
                "delegation_id": delegation.get("delegation_id", ""),
                "delegation_type": delegation.get("delegation_type", "unknown"),
            })

        return result

    async def _invoke_context_agent(
        self, project_id: str, query: str,
    ) -> str:
        """Invoke the Context Agent with a query and return formatted results.

        In mock mode, returns empty findings without invoking the agent.
        """
        from django.conf import settings as django_settings

        if getattr(django_settings, "AI_MOCK_MODE", False):
            logger.info(
                "Step 4: Context Agent delegation for project %s in mock mode — "
                "returning empty findings",
                project_id,
            )
            return "(No context findings available in mock mode.)"

        logger.info(
            "Step 4: Invoking Context Agent for project %s",
            project_id,
        )

        try:
            from agents.context_agent.agent import ContextAgent

            agent = ContextAgent()
            result = await agent.process({
                "query": query,
                "project_id": project_id,
            })

            response = result.get("response", "")
            chunks_used = result.get("chunks_used", [])

            if response:
                return (
                    f"<context_agent_findings>\n"
                    f"{response}\n"
                    f"(Based on {len(chunks_used)} knowledge base chunks)\n"
                    f"</context_agent_findings>"
                )
            return "(Context Agent found no relevant information.)"

        except Exception:
            logger.exception(
                "Step 4: Context Agent failed for project %s", project_id,
            )
            return "(Context Agent encountered an error. No findings available.)"

    async def _invoke_context_extension(
        self, project_id: str, query: str,
    ) -> str:
        """Invoke the Context Extension Agent with a query and return formatted results.

        In mock mode, returns empty findings without invoking the agent.
        """
        from django.conf import settings as django_settings

        if getattr(django_settings, "AI_MOCK_MODE", False):
            logger.info(
                "Step 4: Context Extension delegation for project %s in mock mode — "
                "returning empty findings",
                project_id,
            )
            return "(No context extension findings available in mock mode.)"

        logger.info(
            "Step 4: Invoking Context Extension Agent for project %s",
            project_id,
        )

        try:
            from agents.context_extension.agent import ContextExtensionAgent

            agent = ContextExtensionAgent()
            result = await agent.process({
                "query": query,
                "project_id": project_id,
            })

            response = result.get("response", "")
            messages_cited = result.get("messages_cited", [])

            if response:
                return (
                    f"<extension_results>\n"
                    f"{response}\n"
                    f"(Based on {len(messages_cited)} cited messages from full history)\n"
                    f"</extension_results>"
                )
            return "(Context Extension found no relevant information in chat history.)"

        except Exception:
            logger.exception(
                "Step 4: Context Extension Agent failed for project %s", project_id,
            )
            return "(Context Extension Agent encountered an error. No findings available.)"

    async def _step_apply_mutations(
        self,
        project_id: str,
        facilitator_result: dict[str, Any],
    ) -> None:
        """Step 5: Apply requirements structure mutations from Facilitator.

        Extracts mutations stored by FacilitatorPlugin.update_requirements_structure,
        applies them via CoreClient, and publishes events for each successful mutation.
        """
        mutations = facilitator_result.get("requirements_mutations", [])
        if not mutations:
            logger.info("Step 5: No requirements mutations for project %s", project_id)
            return

        logger.info(
            "Step 5: Applying %d requirements mutations for project %s",
            len(mutations), project_id,
        )

        result = self.core_client.apply_requirements_mutations(project_id, mutations)

        if result.get("accepted"):
            # Publish ai.requirements.updated with summary of applied mutations
            await publish_event("ai.requirements.updated", {
                "project_id": project_id,
                "mutation_count": result.get("mutation_count", 0),
                "mutations_applied": result.get("mutations_applied", []),
            })
            logger.info(
                "Step 5: Applied %d/%d mutations for project %s",
                result.get("mutation_count", 0), len(mutations), project_id,
            )
        else:
            logger.warning(
                "Step 5: All mutations failed for project %s: %s",
                project_id, result.get("mutations_applied", []),
            )

    async def _step_publish_complete(self, project_id: str) -> None:
        """Step 6: Check compression threshold, then publish ai.processing.complete."""
        # Compression check before publishing
        await self._check_and_compress(project_id)

        logger.info("Step 6: Publishing completion for project %s", project_id)
        await publish_event("ai.processing.complete", {
            "project_id": project_id,
            "counter_reset": True,
        })

    async def _check_and_compress(self, project_id: str) -> None:
        """Check if context window utilization exceeds threshold and trigger compression.

        Reads context_compression_threshold admin param (default 60%).
        Estimates token usage from recent messages and existing summary.
        """
        from django.conf import settings as django_settings

        if getattr(django_settings, "AI_MOCK_MODE", False):
            logger.info(
                "Step 6: Compression check skipped in mock mode for project %s",
                project_id,
            )
            return

        # Read compression threshold from admin params (default 60%)
        threshold = 60
        try:
            param_result = self.core_client.get_admin_parameter(
                "context_compression_threshold"
            )
            value = param_result.get("value", "")
            if value:
                threshold = int(value)
        except Exception:
            logger.debug(
                "Could not read context_compression_threshold — using default %d",
                threshold,
            )

        # Load project context to estimate utilization
        project_context = self.core_client.get_project_context(project_id)
        recent_messages = project_context.get("recent_messages", [])
        chat_summary = project_context.get("chat_summary")

        # Estimate context window usage (tokens approximated at ~4 chars/token)
        total_chars = sum(
            len(m.get("content", "")) for m in recent_messages
        )
        if chat_summary:
            total_chars += len(chat_summary.get("summary_text", ""))

        estimated_tokens = total_chars / 4
        # Default context window limit ~128k tokens for most models
        context_limit = 128000
        usage_pct = (estimated_tokens / context_limit) * 100

        logger.info(
            "Step 6: Context usage for project %s: %.1f%% (threshold: %d%%)",
            project_id, usage_pct, threshold,
        )

        if usage_pct < threshold:
            return

        # Trigger compression
        logger.info(
            "Step 6: Triggering compression for project %s (usage %.1f%% > %d%%)",
            project_id, usage_pct, threshold,
        )

        previous_summary_text: str | None = None
        compression_iteration = 0
        if chat_summary:
            previous_summary_text = chat_summary.get("summary_text")
            compression_iteration = chat_summary.get("compression_iteration", 0)

        try:
            from agents.context_compression.agent import ContextCompressionAgent

            agent = ContextCompressionAgent(core_client=self.core_client)
            await agent.process({
                "project_id": project_id,
                "messages_to_compress": recent_messages,
                "previous_summary": previous_summary_text,
                "compression_iteration": compression_iteration,
                "context_window_usage": usage_pct,
            })
        except Exception:
            logger.exception(
                "Step 6: Compression failed for project %s", project_id,
            )

    def _step_cleanup(self, project_id: str) -> None:
        """Step 7: Cleanup — clear abort flag."""
        logger.info("Step 7: Cleanup for project %s", project_id)
        self._abort_flags.pop(project_id, None)
