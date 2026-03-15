# P1: Soft Delete Cleanup Celery Task

## Goal

Per requirement F-9.3, ideas moved to trash should be permanently deleted after a configurable countdown (default: 30 days, admin-configurable via `soft_delete_countdown` parameter). The Celery task file exists but is **completely empty** — it contains only a docstring.

Implement the `soft_delete_cleanup` Celery task that permanently deletes ideas whose `deleted_at` timestamp exceeds the configured countdown.

## Files to Modify

### Primary file (empty stub):
- `services/core/apps/ideas/tasks.py`
  Current content:
  ```python
  """Celery tasks: soft delete cleanup."""
  ```
  That's it — no actual task code.

### Celery beat schedule (needs new entry):
- `services/core/core/settings/base.py` lines 44-57
  Current schedule includes `keyword-matching-sweep`, `vector-similarity-sweep`, and `health-check-sweep` but NO soft delete cleanup task. Add it.

### Admin parameter for countdown:
- `services/core/apps/admin_config/migrations/0001_create_admin_parameters_table.py` — check if `soft_delete_countdown` is already seeded
- `services/core/apps/admin_config/migrations/0002_seed_parameters.py` — check here too
- The admin parameter service: search for `get_parameter` usage pattern in existing tasks like:
  ```python
  from apps.admin_config.services import get_parameter
  min_overlap: int = get_parameter("min_keyword_overlap", default=7, cast=int)
  ```

### Idea model:
- `services/core/apps/ideas/models.py` — the `Idea` model has a `deleted_at` nullable DateTimeField
  - Soft-deleted ideas have `deleted_at` set to a timestamp
  - Non-deleted ideas have `deleted_at = NULL`

### Related views (for context on soft delete flow):
- `services/gateway/apps/ideas/views.py` — contains `restore_idea` at line 69, and soft delete logic
  - Soft delete sets `deleted_at = timezone.now()`
  - Restore sets `deleted_at = None`

## Implementation

Create a Celery shared_task that:
1. Reads the `soft_delete_countdown` admin parameter (default: 30 days)
2. Calculates the cutoff: `timezone.now() - timedelta(days=countdown_days)`
3. Finds all ideas where `deleted_at IS NOT NULL AND deleted_at < cutoff`
4. Permanently deletes them (cascade should handle related records)
5. Logs the count of deleted ideas
6. Returns a summary dict

```python
from celery import shared_task

@shared_task(name="ideas.soft_delete_cleanup")
def soft_delete_cleanup() -> dict:
    """Permanently delete ideas that have been in trash beyond the countdown."""
    from apps.admin_config.services import get_parameter
    from apps.ideas.models import Idea
    # ... implement
```

Then add to `CELERY_BEAT_SCHEDULE` in `services/core/core/settings/base.py`:
```python
"soft-delete-cleanup": {
    "task": "ideas.soft_delete_cleanup",
    "schedule": 86400.0,  # daily
},
```

## Related Requirements

- **F-9.3:** Soft Delete — Ideas move to Trash with an undo toast. Permanent deletion after a configurable countdown (default: 30 days, admin-configurable).
- **F-11.3:** Parameters Tab — `soft_delete_countdown` parameter (default: 30 days) — "Days before permanent deletion from trash"

## Cascade Considerations

When permanently deleting an idea, ensure cascading deletes cover:
- Chat messages (`chat_messages` table, FK to idea)
- Board nodes and connections
- BRD drafts
- Reactions
- Collaborators
- Review records
- Keywords
- Notifications referencing the idea

Check the model definitions and migration files for `on_delete=CASCADE` settings. If cascades are properly set up in Django models, a simple `Idea.objects.filter(...).delete()` will handle everything.
