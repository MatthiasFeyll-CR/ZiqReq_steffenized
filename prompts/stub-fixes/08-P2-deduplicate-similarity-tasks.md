# P2: Deduplicate Similarity Tasks Between Core and Gateway

## Goal

The `keyword_matching_sweep` and `vector_similarity_sweep` Celery tasks exist as identical copies in both the Core and Gateway services. This is a copy-paste artifact from the vibe-coding process. Only one service should own these tasks.

## Duplicated Files

### Core service (original):
- `services/core/apps/similarity/tasks.py` — `keyword_matching_sweep()` (89 lines)
- `services/core/apps/similarity/vector_similarity.py` — `vector_similarity_sweep()` (87 lines)

### Gateway service (duplicate):
- `services/gateway/apps/similarity/tasks.py` — identical `keyword_matching_sweep()` (89 lines)
- `services/gateway/apps/similarity/vector_similarity.py` — identical `vector_similarity_sweep()` (87 lines)

The code is virtually identical — same SQL queries, same logic, same task names (`"similarity.keyword_matching_sweep"` and `"similarity.vector_similarity_sweep"`).

## Celery Beat Schedule

- `services/core/core/settings/base.py` lines 44-57 registers both tasks
- Check if `services/gateway/gateway/settings/` also has a beat schedule

## Decision

These tasks should live in **one service only**. Recommended: **Core service**, since:
1. The Celery beat schedule is already in Core's settings
2. The tasks query Core's database models (`Idea`, `IdeaKeywords`, `MergeRequest`, `idea_embeddings`)
3. Core is the data layer, Gateway is the API layer

## What to Do

1. **Keep** `services/core/apps/similarity/tasks.py` and `services/core/apps/similarity/vector_similarity.py`
2. **Remove or gut** the Gateway duplicates:
   - `services/gateway/apps/similarity/tasks.py` — remove the task implementation, keep only the import if needed for test discoverability (the file header already says "Mirrors services/core/... for test discoverability")
   - `services/gateway/apps/similarity/vector_similarity.py` — same treatment
3. **Check tests**:
   - `services/gateway/apps/similarity/tests/test_keyword_matching.py`
   - `services/gateway/apps/similarity/tests/test_vector_similarity.py`
   These tests may need to import from Core instead of Gateway, or be moved to Core's test directory.
4. **Check Gateway Celery config**: If Gateway also registers these tasks in its beat schedule, remove them from there.

## Related Models

Both task versions import from these models (ensure they're accessible from whichever service you keep):
- `apps.admin_config.services.get_parameter`
- `apps.ideas.models.Idea`
- `apps.similarity.models.IdeaKeywords`
- `apps.similarity.models.MergeRequest`
- `events.publisher.publish_event`

## Event Publisher

Both versions call `publish_event(event_type="similarity.detected", ...)`. Check:
- `services/core/events/publisher.py`
- `services/gateway/events/publisher.py`
Ensure the publisher in the surviving service works correctly.
