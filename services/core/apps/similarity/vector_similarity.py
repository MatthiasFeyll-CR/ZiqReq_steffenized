"""Celery task: vector similarity sweep using pgvector cosine similarity."""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)

_SIMILARITY_SQL = """
SELECT
    a.idea_id  AS requesting_idea_id,
    b.idea_id  AS target_idea_id,
    1 - (a.embedding <=> b.embedding) AS similarity_score
FROM idea_embeddings a
JOIN idea_embeddings b ON a.idea_id <> b.idea_id
JOIN ideas ia ON ia.id = a.idea_id
    AND ia.deleted_at IS NULL
    AND ia.updated_at >= %s
JOIN ideas ib ON ib.id = b.idea_id
    AND ib.deleted_at IS NULL
    AND ib.updated_at >= %s
WHERE a.idea_id < b.idea_id
  AND (1 - (a.embedding <=> b.embedding)) >= %s
"""


@shared_task(name="similarity.vector_similarity_sweep")
def vector_similarity_sweep() -> dict:
    """Find semantically similar ideas via pgvector cosine similarity.

    Reads admin_parameters for similarity_vector_threshold and
    similarity_time_limit.  Skips declined merge-request pairs.
    Publishes similarity.detected for each match above threshold.
    """
    from apps.admin_config.services import get_parameter
    from apps.similarity.models import MergeRequest

    threshold: float = get_parameter(
        "similarity_vector_threshold", default=0.75, cast=float
    )
    time_limit_days: int = get_parameter(
        "similarity_time_limit", default=180, cast=int
    )
    cutoff = timezone.now() - timedelta(days=time_limit_days)

    declined_qs = MergeRequest.objects.filter(status="declined").values_list(
        "requesting_idea_id", "target_idea_id"
    )
    declined_pairs: set[tuple[str, str]] = set()
    for req_id, tgt_id in declined_qs:
        a, b = str(req_id), str(tgt_id)
        declined_pairs.add((a, b))
        declined_pairs.add((b, a))

    with connection.cursor() as cursor:
        cursor.execute(_SIMILARITY_SQL, [cutoff, cutoff, threshold])
        rows = cursor.fetchall()

    events_published = 0

    for requesting_id, target_id, score in rows:
        pair_key = (str(requesting_id), str(target_id))
        if pair_key in declined_pairs:
            continue

        from events.publisher import publish_event

        publish_event(
            event_type="similarity.detected",
            payload={
                "requesting_idea_id": str(requesting_id),
                "target_idea_id": str(target_id),
                "similarity_score": round(float(score), 4),
            },
        )
        events_published += 1

    logger.info(
        "Vector similarity sweep complete: %d events published", events_published
    )
    return {"events_published": events_published}
