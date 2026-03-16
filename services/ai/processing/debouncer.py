"""Per-project debounce with version counters.

Waits debounce_timer seconds after the last message before triggering
the ChatProcessingPipeline. Resets on new messages, batching rapid-fire
input into a single processing cycle.
"""

from __future__ import annotations

import asyncio
import enum
import logging
from typing import Any

from events.publishers import publish_event
from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)

# Default debounce timer (seconds) when admin param unavailable
_DEFAULT_DEBOUNCE_TIMER = 3.0


class DebouncerState(enum.Enum):
    IDLE = "idle"
    DEBOUNCING = "debouncing"
    PROCESSING = "processing"


class Debouncer:
    """Per-project debouncer that batches messages before pipeline execution.

    Attributes:
        _states: Per-project debouncer state.
        _tasks: Per-project asyncio timer tasks.
        _pipeline_callback: Async callable invoked when timer expires.
    """

    def __init__(
        self,
        pipeline_callback: Any = None,
        core_client: CoreClient | None = None,
    ) -> None:
        self._states: dict[str, DebouncerState] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._pipeline_callback = pipeline_callback
        self._core_client = core_client or CoreClient()

    @property
    def states(self) -> dict[str, DebouncerState]:
        return dict(self._states)

    def get_state(self, project_id: str) -> DebouncerState:
        return self._states.get(project_id, DebouncerState.IDLE)

    def _get_debounce_timer(self) -> float:
        """Read debounce_timer admin param, falling back to default."""
        try:
            result = self._core_client.get_admin_parameter("debounce_timer")
            value = result.get("value", "")
            if value:
                return float(value)
        except (ValueError, TypeError):
            logger.warning("Invalid debounce_timer value, using default")
        return _DEFAULT_DEBOUNCE_TIMER

    async def start(self, project_id: str) -> None:
        """Start or reset the debounce timer for a project.

        If already debouncing, cancels the existing timer and starts fresh.
        Publishes ai.processing {state: debouncing}.
        """
        # Cancel any existing timer
        self._cancel_timer(project_id)

        self._states[project_id] = DebouncerState.DEBOUNCING
        await publish_event("ai.processing", {
            "project_id": project_id,
            "state": "debouncing",
        })

        timer = self._get_debounce_timer()
        logger.info(
            "Debouncer started for project %s (timer=%.1fs)", project_id, timer,
        )

        self._tasks[project_id] = asyncio.create_task(
            self._countdown(project_id, timer),
        )

    async def reset(self, project_id: str) -> None:
        """Reset the debounce timer (new message arrived during debounce).

        Cancels the current countdown and starts a fresh one.
        """
        logger.info("Debouncer reset for project %s", project_id)
        await self.start(project_id)

    def cancel(self, project_id: str) -> None:
        """Cancel debouncing for a project entirely, returning to idle."""
        self._cancel_timer(project_id)
        self._states[project_id] = DebouncerState.IDLE
        logger.info("Debouncer cancelled for project %s", project_id)

    def cleanup(self, project_id: str) -> None:
        """Clean up state for a project (e.g. when project is closed)."""
        self._cancel_timer(project_id)
        self._states.pop(project_id, None)

    def _cancel_timer(self, project_id: str) -> None:
        """Cancel the asyncio task for a project if running."""
        task = self._tasks.pop(project_id, None)
        if task is not None and not task.done():
            task.cancel()

    async def _countdown(self, project_id: str, timer: float) -> None:
        """Wait for the debounce period, then trigger the pipeline."""
        try:
            await asyncio.sleep(timer)
        except asyncio.CancelledError:
            logger.debug("Debounce timer cancelled for project %s", project_id)
            return

        # Timer expired — transition to processing
        self._states[project_id] = DebouncerState.PROCESSING
        self._tasks.pop(project_id, None)

        logger.info("Debounce timer expired for project %s, triggering pipeline", project_id)

        if self._pipeline_callback is not None:
            try:
                await self._pipeline_callback(project_id)
            except Exception:
                logger.exception(
                    "Pipeline callback failed for project %s", project_id,
                )
            finally:
                # Return to idle after processing completes
                self._states[project_id] = DebouncerState.IDLE
        else:
            self._states[project_id] = DebouncerState.IDLE
