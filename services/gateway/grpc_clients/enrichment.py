"""Bulk UUID to display name resolution via Gateway user lookups.

This module provides enrichment utilities for resolving user UUIDs
to display names across gRPC responses. Full implementation in later milestones.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def enrich_with_display_names(user_ids: list[str]) -> dict[str, str]:
    """Resolve a list of user UUIDs to display names.

    Returns a dict mapping user_id -> display_name.
    Stub returns empty dict; full implementation queries the users table.
    """
    logger.warning("enrich_with_display_names stub called")
    return {}
