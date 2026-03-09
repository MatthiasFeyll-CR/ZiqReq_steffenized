"""gRPC client for Core — read idea details, reviewer assignments.

Provides typed methods for CoreService RPCs needed by the notification service.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """gRPC client for Core service (notification service side)."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_idea_context(
        self,
        idea_id: str,
        recent_message_limit: int = 0,
        include_board: bool = False,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        logger.warning(
            "Notification CoreClient.get_idea_context stub called"
        )
        return {}
