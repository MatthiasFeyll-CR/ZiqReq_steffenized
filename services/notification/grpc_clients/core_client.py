"""Core service client — direct database access (notification service side).

Queries the shared PostgreSQL database directly instead of making gRPC calls.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreClient:
    """Client for Core service data — uses direct DB access (notification service side)."""

    def __init__(self, address: str = "localhost:50051") -> None:
        self.address = address

    def get_idea_context(
        self,
        idea_id: str,
        recent_message_limit: int = 0,
        include_board: bool = False,
        include_brd_draft: bool = False,
    ) -> dict[str, Any]:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, state, owner_id FROM ideas "
                "WHERE id = %s AND deleted_at IS NULL",
                [idea_id],
            )
            row = cursor.fetchone()
            if not row:
                return {}

            return {
                "metadata": {
                    "idea_id": str(row[0]),
                    "title": row[1] or "",
                    "state": row[2] or "open",
                    "owner_id": str(row[3]) if row[3] else "",
                },
            }
