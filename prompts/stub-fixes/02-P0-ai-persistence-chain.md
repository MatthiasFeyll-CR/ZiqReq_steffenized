# P0: AI Persistence Chain — Keywords, BRD Draft, Context Summary

## Goal

The AI service generates three critical data artifacts during processing, but the persistence methods are all stubs that log warnings and return fake success responses. This breaks the entire downstream data flow:

1. **Keywords** — KeywordAgent generates abstract keywords per idea, but `upsert_keywords` is a no-op. This means the `keyword_matching_sweep` Celery task (which queries `IdeaKeywords` in DB) never finds any data, so similarity detection (FA-5) never fires.

2. **BRD Draft** — SummarizingAI generates BRD sections, but `upsert_brd_draft` is a no-op. The BRD is broadcast via WebSocket but never persisted. It's lost on page refresh.

3. **Context Summary** — ContextCompressionAgent compresses long conversations, but `upsert_context_summary` is a no-op. Compression results are never saved, so the system re-compresses endlessly without effect.

## Files to Modify

### Primary file — AI service CoreClient:
- `services/ai/grpc_clients/core_client.py`
  - `upsert_keywords()` at line ~350-356 — stub, returns `{"success": True}`
  - `upsert_brd_draft()` at line ~382-390 — stub, returns `{"success": True}`
  - `upsert_context_summary()` at line ~394-403 — stub, returns `{"success": True}`

### Database models to persist into:
- `services/core/apps/ideas/models.py` — look for keyword storage (may need to check similarity models)
- `services/core/apps/brd/models.py` — `BrdDraft` model with fields:
  - `section_title`, `section_short_description`, `section_current_workflow`
  - `section_affected_department`, `section_core_capabilities`, `section_success_criteria`
  - `section_locks` (JSONField), `allow_information_gaps` (bool), `readiness_evaluation` (JSONField)

### Similarity models (for keywords):
- Check `services/core/apps/similarity/models.py` or search for `IdeaKeywords` model
- The `keyword_matching_sweep` task at `services/core/apps/similarity/tasks.py` queries `IdeaKeywords.objects.filter(idea_id__in=...)` expecting `idea_id` and `keywords` (list) fields

### Context summary storage:
- Search for `ChatContextSummary` model or `chat_context_summaries` table
- The AI CoreClient's `get_idea_context()` (line ~67-80) already reads from this table:
  ```sql
  SELECT summary_text, compression_iteration FROM chat_context_summaries
  WHERE idea_id = %s ORDER BY created_at DESC LIMIT 1
  ```
  So the table exists with at least: `idea_id`, `summary_text`, `compression_iteration`, `created_at`

## Implementation Pattern

The AI CoreClient already has working direct-DB implementations for board operations (lines 106-346). Follow the same pattern using `from django.db import connection` with raw SQL. Example from existing code:

```python
def create_board_node(self, idea_id, node_type, title, ...):
    from django.db import connection
    node_id = str(uuid.uuid4())
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO board_nodes (...) VALUES (%s, ...) RETURNING created_at",
            [node_id, idea_id, ...],
        )
    return {"node_id": node_id, ...}
```

## What Each Method Should Do

### `upsert_keywords(idea_id, keywords: list[str])`
- INSERT or UPDATE into the `IdeaKeywords` table (or equivalent)
- `keywords` is a Python list of strings — store as a PostgreSQL array or JSONField
- Return `{"success": True}` on success

### `upsert_brd_draft(idea_id, sections: dict, readiness_evaluation: dict)`
- Get or create a `BrdDraft` row for `idea_id`
- Map section keys to model fields (see `services/gateway/grpc_clients/core_client.py` lines 85-132 for the working Gateway implementation that does exactly this — copy that pattern)
- Respect `section_locks` — don't overwrite locked sections
- Return `{"success": True}` on success

### `upsert_context_summary(idea_id, summary_text, messages_covered_up_to_id, compression_iteration, context_window_usage)`
- INSERT into `chat_context_summaries` table
- Fields: `idea_id`, `summary_text`, `messages_covered_up_to_id`, `compression_iteration`, `context_window_usage`, `created_at`
- Return `{"success": True}` on success

## Reference: Working Gateway Implementation for BRD

The Gateway CoreClient at `services/gateway/grpc_clients/core_client.py` lines 85-132 has a fully working `update_brd_draft()` using Django ORM. The AI service version should do the same thing:

```python
def update_brd_draft(self, idea_id, sections, readiness_evaluation_json=""):
    from apps.brd.models import BrdDraft
    draft, _created = BrdDraft.objects.get_or_create(idea_id=idea_id, defaults={...})
    field_map = {
        "title": "section_title",
        "short_description": "section_short_description",
        "current_workflow": "section_current_workflow",
        "affected_department": "section_affected_department",
        "core_capabilities": "section_core_capabilities",
        "success_criteria": "section_success_criteria",
    }
    # ... update non-locked fields, save
```

## Downstream Consumers That Depend on This Data

- `services/core/apps/similarity/tasks.py` — `keyword_matching_sweep()` reads `IdeaKeywords`
- `services/core/apps/similarity/vector_similarity.py` — reads `idea_embeddings` table
- `services/gateway/apps/ideas/views.py` — context window endpoint reads `chat_context_summaries`
- `services/gateway/apps/brd/views.py` — BRD API reads `BrdDraft`
- `frontend/src/api/brd.ts` — frontend fetches BRD draft via API

## Also Fix: `get_brd_draft` Stub (line ~369-380)

This method also returns fake data. It should query the `BrdDraft` model and return the actual section locks and allow_information_gaps flag, as the Summarizing AI uses this to decide which sections to regenerate.
