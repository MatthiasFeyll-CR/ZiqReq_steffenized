"""Append event consumer — append.accepted events trigger append execution.

Mirrors services/core/events/consumers.py handle_append_accepted for test discoverability.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def handle_append_accepted(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle append.accepted event.

    Invokes the append execution service to flag the requesting idea
    and add its owner as collaborator on the target idea.

    Args:
        payload: Event payload with merge_request_id, requesting_idea_id,
                 target_idea_id.

    Returns:
        Dict with target_idea_id and collaborator info.
    """
    from apps.similarity.append_service import execute_append

    merge_request_id: str = payload["merge_request_id"]
    requesting_idea_id: str = payload["requesting_idea_id"]
    target_idea_id: str = payload["target_idea_id"]

    logger.info(
        "[append_consumer] Processing append.accepted for MR %s",
        merge_request_id,
    )

    result = execute_append(
        merge_request_id=merge_request_id,
        requesting_idea_id=requesting_idea_id,
        target_idea_id=target_idea_id,
    )

    logger.info(
        "[append_consumer] Append complete for MR %s — idea %s appended to %s",
        merge_request_id,
        requesting_idea_id,
        target_idea_id,
    )

    return result
