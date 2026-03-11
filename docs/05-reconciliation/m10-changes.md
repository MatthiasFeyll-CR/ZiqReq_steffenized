# Milestone 10 Spec Reconciliation

## Summary
- **Milestone:** M10 — Review Workflow
- **Date:** 2026-03-11
- **Total deviations found:** 4
- **Auto-applied (SMALL TECHNICAL):** 1
- **Applied and flagged (FEATURE DESIGN):** 3
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-003: Extended API Response | `docs/02-architecture/api-design.md:722` | Added `owner_id` and `co_owner_id` fields to GET /api/reviews response schema |

**Rationale:** Additional fields added to support frontend conflict-of-interest checks. No behavior change, purely additive. Frontend compares current user.id against idea.owner_id/co_owner_id to disable assign button for own ideas.

---

### FEATURE DESIGN (Applied — flagged for review)

| # | Deviation | Document Updated | Change | Impact |
|---|-----------|-----------------|--------|--------|
| 1 | D-001: New Endpoint | `docs/02-architecture/api-design.md` | Added GET /api/ideas/:id/review/reviewers endpoint | New data exposure |
| 2 | D-002: New Endpoint | `docs/02-architecture/api-design.md` | Added GET /api/reviews/reviewers endpoint | New data exposure |
| 3 | D-004: Missing Feature | `docs/02-architecture/api-design.md` | Marked GET /api/ideas/:id/review/similar as "deferred" | Feature gap |

---

## Detailed Change Descriptions

### D-001: GET /api/ideas/:id/review/reviewers

**Added to:** `docs/02-architecture/api-design.md` (Review Workflow section, after timeline endpoints)

**Purpose:** Fetch the list of assigned reviewers for a specific idea, used to display reviewer names/avatars in the ReviewSection header component.

**Endpoint spec:**
```
#### GET /api/ideas/:id/review/reviewers
- **Purpose:** Get assigned reviewers for an idea (ReviewSection header display)
- **Auth:** Idea access (review section visible)
- **Response (200):**
  ```json
  {
    "reviewers": [
      { "id": "uuid", "display_name": "string" }
    ]
  }
  ```
```

**Why added:** US-008 required displaying reviewer names in the ReviewSection header. Without this endpoint, the frontend would need to fetch the full idea object or timeline just to get reviewer names, which is inefficient.

**Source:** progress.txt line 137 (US-008)

---

### D-002: GET /api/reviews/reviewers

**Added to:** `docs/02-architecture/api-design.md` (Review Page section, after unassign endpoint)

**Purpose:** Fetch all users with reviewer role for populating the reviewer multi-select in SubmitArea.

**Endpoint spec:**
```
#### GET /api/reviews/reviewers
- **Purpose:** List all users with reviewer role (for submit flow multi-select)
- **Auth:** Authenticated (owner/co-owner submitting idea)
- **Response (200):**
  ```json
  {
    "reviewers": [
      { "id": "uuid", "display_name": "string" }
    ]
  }
  ```
```

**Why added:** US-010 required a reviewer multi-select dropdown in the SubmitArea component. The submit flow allows owners to assign specific reviewers when submitting. This endpoint provides the list of available reviewers.

**Backend implementation:** Filters by `roles__contains=["reviewer"]` using PostgreSQL array containment.

**Source:** progress.txt line 174 (US-010)

---

### D-003: Extended Response — owner_id/co_owner_id

**Modified:** `docs/02-architecture/api-design.md:722-732` (GET /api/reviews response schema)

**Before:**
```json
{
  "assigned_to_me": [
    {
      "idea_id": "uuid",
      "title": "string",
      "state": "in_review",
      "owner": { "id": "uuid", "display_name": "string" },
      ...
    }
  ]
}
```

**After:**
```json
{
  "assigned_to_me": [
    {
      "idea_id": "uuid",
      "title": "string",
      "state": "in_review",
      "owner": { "id": "uuid", "display_name": "string" },
      "owner_id": "uuid",
      "co_owner_id": "uuid | null",
      ...
    }
  ]
}
```

**Why changed:** Frontend ReviewCard component needs to compare `current_user.id` against both `idea.owner_id` and `idea.co_owner_id` to implement conflict-of-interest check (disable assign button + show tooltip for own ideas). Extracting IDs from nested objects in React is awkward; flat UUID fields simplify comparison.

**Source:** progress.txt line 127 (US-007)

---

### D-004: Missing Feature — Similar Ideas Endpoint

**Modified:** `docs/02-architecture/api-design.md:687-703` (GET /api/ideas/:id/review/similar)

**Status:** Marked as **DEFERRED** (not implemented in M10)

**Original spec:** Feature F-4.12 required similar ideas display in review section based on declined merges and keyword overlap.

**Why deferred:** Scope prioritization during milestone planning. Core review workflow (submit, assign, accept/reject/drop, timeline, review page) was prioritized. Similar ideas is a value-add feature that can be implemented in a future milestone without blocking the primary workflow.

**Impact:** Review section does not show similar ideas panel. No functional gap for core review workflow. Feature can be added in M11+ without breaking changes.

**Recommendation:** Add to future milestone scope (M14: Advanced Review Features or M15: Admin & Monitoring).

---

## Documents Modified

The following specification documents were updated to match the actual implementation:

1. **docs/02-architecture/api-design.md**
   - Added GET /api/ideas/:id/review/reviewers endpoint specification
   - Added GET /api/reviews/reviewers endpoint specification
   - Extended GET /api/reviews response schema with owner_id/co_owner_id fields
   - Marked GET /api/ideas/:id/review/similar as "deferred to future milestone"

---

## Impact on Future Milestones

### No Breaking Changes
All changes are additive or clarifications. No future milestones are blocked.

### Considerations
- **M11 (Merge Workflow):** No impact — merge workflow is independent of review endpoints.
- **M12 (Notifications):** Review state change notifications already covered by existing timeline events.
- **M14/15 (Admin/Advanced Features):** If similar ideas feature (D-004) is added later, it will be a net-new endpoint with no dependencies on M10 implementation.

---

## Implementation Notes

### Patterns Discovered
From `.ralph/archive/m10-review/progress.txt`, these reusable patterns were established:

1. **Batch-loading users:** Collect all user IDs from query results, fetch User objects in single query, build users_map for O(1) lookups. Prevents N+1 queries. Used in list_reviews, get_timeline, get_idea_reviewers.

2. **Role-based authorization:** `_require_reviewer()` helper checks `user.roles` array for "reviewer" role. Returns 403 if not present. Reused across all reviewer-only endpoints.

3. **Conflict of interest check:** Backend validates `idea.owner_id` and `idea.co_owner_id` against current user. Frontend disables assign button with tooltip for own ideas.

4. **Timeline entry immutability:** `ReviewTimelineEntry.save()` raises `ValidationError` on update attempts. Enforces append-only timeline.

5. **State machine validation:** Review actions use explicit valid-state maps (accept/reject/drop from in_review only; undo from accepted/dropped/rejected). Invalid transitions return 400.

6. **Atomic transactions:** Submit flow and review actions use `transaction.atomic()` to ensure BRD version creation, state transitions, and timeline entries are committed together or rolled back.

### Testing Coverage
- 566 Python tests pass (100% for M10 changes)
- 361 frontend tests pass (100% for M10 changes)
- All 22 test matrix IDs verified (see docs/08-qa/qa-m10-review.md)
- Zero security findings (OWASP compliance verified)
- Zero performance issues (N+1 queries eliminated via batch-loading)

---

## Changelog Signature

**Reconciled by:** Spec Reconciler (Claude)
**Date:** 2026-03-11
**QA Report:** docs/08-qa/qa-m10-review.md (PASS, 0 defects, 0 deviations)
**Progress Log:** .ralph/archive/m10-review/progress.txt
**Commit Range:** User stories US-001 through US-010
