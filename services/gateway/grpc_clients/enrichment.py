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
    """
    if not user_ids:
        return {}

    from apps.authentication.models import User

    users = User.objects.filter(id__in=user_ids).values_list("id", "display_name")
    return {str(uid): name for uid, name in users}
