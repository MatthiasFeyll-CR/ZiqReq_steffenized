# P3: has_been_submitted — Always Returns False

## Goal

The `has_been_submitted` function always returns `False`, meaning the backend always reports that an idea has never been submitted for review. The frontend works around this with a heuristic (`state !== 'open'`), but the backend API data is incorrect.

Per requirement F-1.2, the review section should be hidden until the idea is submitted for review at least once. Once submitted, it persists on the page regardless of current state (even if rejected and reworked).

## Files to Modify

### Primary file:
- `services/gateway/apps/ideas/_brd_check.py`
  ```python
  def has_been_submitted(idea_id: str) -> bool:
      """Stub — real implementation in M7."""
      return False
  ```

### Where it's used:
- Search for `has_been_submitted` imports across the codebase
- The API response for `GET /api/ideas/:id` includes `has_been_submitted` in the response body (per `docs/02-architecture/api-design.md` line 161)

### Frontend workaround:
- `frontend/src/components/workspace/useSectionVisibility.ts` line 18:
  ```typescript
  // M3 heuristic: has_been_submitted = idea.state !== "open"
  ```
- `frontend/src/pages/IdeaWorkspace/index.tsx` line 175:
  ```typescript
  // has_been_submitted heuristic: state !== 'open' means it was submitted at least once
  ```

## Implementation

An idea "has been submitted" if it has ever transitioned to the `in_review` state. There are several ways to determine this:

### Option A: Check if any BRD version exists
```python
def has_been_submitted(idea_id: str) -> bool:
    from apps.brd.models import BrdVersion  # or BrdDraft
    return BrdVersion.objects.filter(idea_id=idea_id).exists()
```

### Option B: Check if idea state is not 'open' OR if review records exist
```python
def has_been_submitted(idea_id: str) -> bool:
    from apps.ideas.models import Idea
    try:
        idea = Idea.objects.get(id=idea_id, deleted_at__isnull=True)
        # If state is anything other than 'open', it was submitted at some point
        if idea.state != 'open':
            return True
        # Also check for review timeline entries or state transitions
        from apps.review.models import ReviewAction  # or equivalent
        return ReviewAction.objects.filter(idea_id=idea_id).exists()
    except Idea.DoesNotExist:
        return False
```

### Option C: Check for a `submitted_at` timestamp on the Idea model
Check if the `Idea` model has a `submitted_at` or `first_submitted_at` field. If not, this might need to be added.

## Before Implementing

1. Check the `Idea` model fields: `services/core/apps/ideas/models.py`
2. Check the review models: `services/core/apps/review/models.py`
3. Check if there's a `BrdVersion` model for submitted BRD versions
4. Check `services/gateway/apps/review/views.py` for submit flow — what happens when a user submits for review? Does it create a version record?

## Spec QA Note

From `docs/04-spec-qa/spec-qa-report.md` line 77:
> API response includes `has_been_submitted: boolean` but no backing column exists. Must be derived (e.g., check if `brd_versions` exist for this idea). Derivation logic not documented.

This confirms the field is derived, not stored. The recommended approach per the spec QA is to check `brd_versions`.

## Related Requirements

- **F-1.2:** Section Visibility — The review section is hidden/inaccessible until the idea is submitted for review at least once. Once submitted, both sections persist on the page regardless of current state.
- **F-1.4:** Section Locking — Different lock states based on idea lifecycle state
