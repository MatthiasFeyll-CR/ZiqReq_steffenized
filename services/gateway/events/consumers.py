"""AI event consumers — bridge AI service events to Core gRPC + WebSocket broadcasts.

Subscribes to:
  - ai.chat_response.ready → Core CreateChatMessage + broadcast chat_message
  - ai.reaction.ready → Core CreateAIReaction + broadcast ai_reaction
  - ai.title.updated → Core UpdateIdeaTitle + broadcast title_update

Retry: 3 attempts (1s, 2s, 4s backoff), then dead-letter queue.
Idempotency: event_id tracking prevents duplicate processing.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from channels.layers import get_channel_layer

from grpc_clients.core_client import CoreClient

logger = logging.getLogger(__name__)

RETRY_DELAYS = [1, 2, 4]  # seconds
MAX_RETRIES = 3

_EVENT_HANDLERS = {
    "ai.chat_response.ready": "_handle_chat_response",
    "ai.reaction.ready": "_handle_reaction",
    "ai.title.updated": "_handle_title_update",
    "ai.processing.complete": "_handle_processing_complete",
    "ai.brd.ready": "_handle_brd_ready",
}


class AIEventConsumer:
    """Consumes AI service events, persists via Core gRPC, broadcasts via WebSocket.

    Runs as a background process. In M7, events are dispatched directly
    (in-memory). Future milestones will wire to RabbitMQ.
    """

    def __init__(self, core_client: CoreClient | None = None) -> None:
        self._core_client = core_client or CoreClient()
        self._processed_event_ids: set[str] = set()
        self._dead_letter_queue: list[dict[str, Any]] = []
        self._running = False

    @property
    def processed_event_ids(self) -> set[str]:
        return self._processed_event_ids

    @property
    def dead_letter_queue(self) -> list[dict[str, Any]]:
        return list(self._dead_letter_queue)

    def start(self) -> None:
        self._running = True
        logger.info("AIEventConsumer started")

    def stop(self) -> None:
        self._running = False
        logger.info("AIEventConsumer stopped")

    async def process_event(self, event: dict[str, Any]) -> bool:
        """Process a single AI event with retry and idempotency.

        Returns True if successfully processed, False if sent to DLQ.
        """
        event_id = event.get("event_id")
        event_type = event.get("event_type")

        if not event_id or not event_type:
            logger.error("Malformed event: missing event_id or event_type")
            self._dead_letter_queue.append(event)
            return False

        if event_id in self._processed_event_ids:
            logger.info("Duplicate event %s, skipping", event_id)
            return True

        handler_name = _EVENT_HANDLERS.get(event_type)
        if not handler_name:
            logger.warning("Unknown event type: %s", event_type)
            self._dead_letter_queue.append(event)
            return False

        handler = getattr(self, handler_name)

        for attempt in range(MAX_RETRIES):
            try:
                await handler(event)
                self._processed_event_ids.add(event_id)
                logger.info("Processed event %s (%s)", event_id, event_type)
                return True
            except Exception:
                delay = RETRY_DELAYS[attempt] if attempt < len(RETRY_DELAYS) else RETRY_DELAYS[-1]
                logger.warning(
                    "Event %s attempt %d failed, retrying in %ds",
                    event_id, attempt + 1, delay,
                    exc_info=True,
                )
                await asyncio.sleep(delay)

        logger.error("Event %s failed after %d retries, sending to DLQ", event_id, MAX_RETRIES)
        self._dead_letter_queue.append(event)
        return False

    async def _handle_chat_response(self, event: dict[str, Any]) -> None:
        """ai.chat_response.ready → Core CreateChatMessage + broadcast chat_message."""
        idea_id = event["idea_id"]
        content = event["content"]
        message_type = event.get("message_type", "regular")
        ai_agent = event.get("ai_agent", "facilitator")

        result = self._core_client.persist_ai_chat_message(
            idea_id=idea_id,
            content=content,
            message_type=message_type,
        )

        payload = {
            "id": result.get("message_id", ""),
            "idea_id": idea_id,
            "sender_type": "ai",
            "sender_id": None,
            "ai_agent": ai_agent,
            "content": content,
            "message_type": message_type,
            "created_at": result.get("created_at", ""),
        }

        await self._broadcast(idea_id, "chat_message", payload)

    async def _handle_reaction(self, event: dict[str, Any]) -> None:
        """ai.reaction.ready → Core CreateAIReaction + broadcast ai_reaction."""
        idea_id = event["idea_id"]
        message_id = event["message_id"]
        reaction_type = event["reaction_type"]

        result = self._core_client.persist_ai_reaction(
            idea_id=idea_id,
            message_id=message_id,
            reaction_type=reaction_type,
        )

        payload = {
            "id": result.get("reaction_id", ""),
            "message_id": message_id,
            "reaction_type": reaction_type,
        }

        await self._broadcast(idea_id, "ai_reaction", payload)

    async def _handle_title_update(self, event: dict[str, Any]) -> None:
        """ai.title.updated → Core UpdateIdeaTitle + broadcast title_update."""
        idea_id = event["idea_id"]
        title = event["title"]

        self._core_client.update_idea_title(
            idea_id=idea_id,
            new_title=title,
        )

        payload = {
            "idea_id": idea_id,
            "title": title,
        }

        await self._broadcast(idea_id, "title_update", payload)

    async def _handle_brd_ready(self, event: dict[str, Any]) -> None:
        """ai.brd.ready → persist BRD sections to brd_drafts + broadcast brd_ready."""
        idea_id = event["idea_id"]
        sections = event.get("sections", {})
        readiness_evaluation = event.get("readiness_evaluation", {})
        fabrication_flags = event.get("fabrication_flags", [])
        mode = event.get("mode", "full_generation")

        # Persist via CoreClient gRPC (stub in M9)
        self._core_client.update_brd_draft(
            idea_id=idea_id,
            sections=sections,
            readiness_evaluation_json=json.dumps(readiness_evaluation),
        )

        payload = {
            "idea_id": idea_id,
            "mode": mode,
            "sections": sections,
            "readiness_evaluation": readiness_evaluation,
            "fabrication_flags": fabrication_flags,
        }

        await self._broadcast(idea_id, "brd_ready", payload)

    async def _handle_processing_complete(self, event: dict[str, Any]) -> None:
        """ai.processing.complete → broadcast ai_processing {state: completed}.

        Rate limiting is now handled by querying unprocessed messages in the DB,
        so no explicit counter reset is needed here.
        """
        idea_id = event["idea_id"]

        payload = {
            "idea_id": idea_id,
            "state": "completed",
        }
        await self._broadcast(idea_id, "ai_processing", payload)

        # Publish AI delegation complete notification
        self._publish_ai_delegation_notification(idea_id)

    def _publish_ai_delegation_notification(self, idea_id: str) -> None:
        """Look up the idea owner and publish an AI delegation complete notification."""
        try:
            from apps.ideas.models import Idea
            from events.publisher import publish_notification_event

            idea = Idea.objects.get(id=idea_id)
            publish_notification_event(
                routing_key="notification.ai.delegation_complete",
                user_id=str(idea.owner_id),
                event_type="ai_delegation_complete",
                title="AI Processing Complete",
                body=f'AI has finished processing your request for "{idea.title}"',
                reference_id=str(idea.id),
                reference_type="idea",
            )
        except Exception:
            logger.exception(
                "Failed to publish AI delegation notification for idea %s", idea_id
            )

    async def _broadcast(
        self, idea_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        """Send event to WebSocket group idea_{idea_id}."""
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("[BROADCAST] No channel layer available, skipping broadcast")
            return

        group_name = f"idea_{idea_id}"
        logger.info(
            "[BROADCAST] Sending %s to group %s via %s",
            event_type, group_name, type(channel_layer).__name__,
        )
        await channel_layer.group_send(
            group_name,
            {
                "type": event_type,
                "idea_id": idea_id,
                "payload": payload,
            },
        )
        logger.info("[BROADCAST] Sent %s to group %s", event_type, group_name)
