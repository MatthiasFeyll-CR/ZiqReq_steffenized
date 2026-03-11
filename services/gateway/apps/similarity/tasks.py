"""Celery tasks: similarity detection sweeps.

Mirrors services/core/apps/similarity/tasks.py for test discoverability.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.similarity.vector_similarity import vector_similarity_sweep  # noqa: F401

logger = logging.getLogger(__name__)


@shared_task(name="similarity.keyword_matching_sweep")
def keyword_matching_sweep() -> dict:
    """Compare keyword sets across ideas and publish similarity.detected events.

    Reads admin_parameters for min_keyword_overlap and similarity_time_limit.
    Skips pairs with a declined merge request.
    """
    from apps.admin_config.services import get_parameter
    from apps.ideas.models import Idea
    from apps.similarity.models import IdeaKeywords, MergeRequest

    min_overlap: int = get_parameter("min_keyword_overlap", default=7, cast=int)
    time_limit_days: int = get_parameter("similarity_time_limit", default=180, cast=int)
    cutoff = timezone.now() - timedelta(days=time_limit_days)

    # Get declined pairs to skip
    declined_qs = MergeRequest.objects.filter(status="declined").values_list(
        "requesting_idea_id", "target_idea_id"
    )
    declined_pairs: set[tuple[str, str]] = set()
    for req_id, tgt_id in declined_qs:
        a, b = str(req_id), str(tgt_id)
        declined_pairs.add((a, b))
        declined_pairs.add((b, a))

    # Ideas within time window (not soft-deleted)
    valid_idea_ids = set(
        Idea.objects.filter(
            updated_at__gte=cutoff,
            deleted_at__isnull=True,
        ).values_list("id", flat=True)
    )

    # All keyword records for valid ideas
    keyword_records = list(
        IdeaKeywords.objects.filter(idea_id__in=valid_idea_ids)
        .values_list("idea_id", "keywords")
    )

    events_published = 0

    for i, (idea_a_id, keywords_a) in enumerate(keyword_records):
        if not keywords_a:
            continue
        set_a = set(keywords_a)
        for j in range(i + 1, len(keyword_records)):
            idea_b_id, keywords_b = keyword_records[j]
            if not keywords_b:
                continue

            pair_key = (str(idea_a_id), str(idea_b_id))
            if pair_key in declined_pairs:
                continue

            overlap = set_a & set(keywords_b)
            if len(overlap) >= min_overlap:
                from events.publisher import publish_event

                publish_event(
                    event_type="similarity.detected",
                    payload={
                        "requesting_idea_id": str(idea_a_id),
                        "target_idea_id": str(idea_b_id),
                        "keyword_overlap_count": len(overlap),
                    },
                )
                events_published += 1

    logger.info("Keyword matching sweep complete: %d events published", events_published)
    return {"events_published": events_published}
