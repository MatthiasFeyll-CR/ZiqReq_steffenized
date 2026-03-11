# Milestone 15 Spec Reconciliation

## Summary
- **Milestone:** M15 — Admin Panel
- **Date:** 2026-03-11
- **Total deviations found:** 9
- **Auto-applied (SMALL TECHNICAL):** 5
- **Applied and flagged (FEATURE DESIGN):** 3
- **Applied and flagged (LARGE TECHNICAL):** 1
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

These are technical corrections with no design or behavioral impact — typos, path corrections, missing fields, query refinements.

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| D-001 | Endpoint URL renamed (context-agent → company) | `docs/02-architecture/api-design.md:1211` | Changed `/api/admin/ai-context/context-agent` to `/api/admin/ai-context/company` for more user-friendly naming |
| D-002 | HTTP method changed (PUT → PATCH) | `docs/02-architecture/api-design.md:1202,1224` | Changed `PUT` to `PATCH` for both AI context endpoints (semantically correct for partial updates) |
| D-003 | Response field added (id) | `docs/02-architecture/api-design.md:1195-1199,1215-1221` | Added `id` field to facilitator and company context GET responses (frontend needs identifier for tracking) |
| D-007 | Soft-deleted ideas filtering | `docs/02-architecture/api-design.md:1307` | Added note that `ideas_by_state` excludes soft-deleted ideas (`deleted_at IS NOT NULL`) |
| D-009 | board_nodes.created_by clarification | `docs/02-architecture/data-model.md:191` | Added note clarifying that `created_by` is a literal string ('user'/'ai'), not a user FK. To determine user, join via `idea_id` to `ideas.owner_id`/`co_owner_id` |

---

### FEATURE DESIGN (Applied and flagged)

These changes affect user-visible behavior, feature scope, or error handling. They are applied to keep specs accurate but flagged for visibility.

| # | Deviation | Document Updated | Change | Rationale |
|---|-----------|-----------------|--------|-----------|
| D-004 | Empty query returns all users | `docs/02-architecture/api-design.md:1329` | Added note that empty `?q=` param returns all users (differs from regular `/api/users/search` which requires min 2 chars) | Admin needs ability to view all users without typing a query |
| D-005 | Context re-indexing failure handling | `docs/02-architecture/api-design.md:1233-1235` | Added error table and side effects note: gRPC re-indexing failure returns 500 with `REINDEX_FAILED` but DB update persists (fire-and-fail pattern) | DB update is primary operation, re-indexing is best-effort. Avoids transactional rollback complexity across gRPC boundary |
| D-008 | Alert config returns current user only | `docs/02-architecture/api-design.md:1309-1326` | Changed response shape from `{"recipients": [...]}` (all admins) to `{"user_id": "...", "is_active": bool}` (current user only). Updated both GET and PATCH endpoints | Simpler implementation — admins only manage their own opt-in status. Notification service queries all opted-in admins separately via gRPC |

---

### LARGE TECHNICAL (Applied and flagged)

These changes affect system architecture, infrastructure patterns, or service boundaries. They are applied but prominently flagged due to their scope.

| # | Deviation | Document Updated | Change | Rationale |
|---|-----------|-----------------|--------|-----------|
| D-006 | Monitoring service architecture (namespace mirroring) | `docs/02-architecture/project-structure.md:102`<br>`docs/02-architecture/tech-stack.md:299` | Added module mirroring pattern: Core service `apps.monitoring` business logic (`health_checks.py`, `tasks.py`) is mirrored into Gateway's `apps.monitoring/` directory for test discoverability | Namespace conflict: both Core and Gateway have `apps.monitoring` packages. PYTHONPATH resolution prioritizes Gateway. Test runner needs to discover Core's modules when running under Gateway settings. Same pattern used for `similarity` app in earlier milestones |

---

### REJECTED

None.

---

## Documents Modified

All changes are limited to the `docs/` directory as required:

1. `docs/02-architecture/api-design.md`
   - Updated 4 admin API endpoint specs (facilitator, company, monitoring, monitoring/alerts, users/search)
   - Added error handling, side effects, query behavior notes

2. `docs/02-architecture/data-model.md`
   - Added clarification note to `board_nodes` table schema

3. `docs/02-architecture/project-structure.md`
   - Added module mirroring pattern documentation

4. `docs/02-architecture/tech-stack.md`
   - Added monitoring service module location note

---

## Impact on Future Milestones

**No impact on future milestones.** All deviations are isolated to M15 scope:
- Admin panel endpoints are fully implemented and tested
- Monitoring service architecture is stable
- No cascading changes needed in upstream dependencies

**Note for future admin features:** The alert configuration pattern (current user only, not all recipients) may be extended if admin user management features are added in future milestones.

---

## Detailed Deviation Analysis

### D-001: Endpoint URL renamed (context-agent → company)

**Source:** progress.txt US-001, QA report
**Original spec:** `/api/admin/ai-context/context-agent` (api-design.md line 1211)
**Actual implementation:** `/api/admin/ai-context/company`

**Before:**
```
#### GET /api/admin/ai-context/context-agent
- **Purpose:** Get context agent bucket
```

**After:**
```
#### GET /api/admin/ai-context/company
- **Purpose:** Get company context bucket
```

**Reasoning:** More user-friendly naming. "Company context" is clearer to admins than "context agent bucket".

---

### D-002: HTTP method changed (PUT → PATCH)

**Source:** progress.txt US-001
**Original spec:** `PUT /api/admin/ai-context/facilitator` and `PUT /api/admin/ai-context/context-agent`
**Actual implementation:** `PATCH` for both

**Before:**
```
#### PUT /api/admin/ai-context/facilitator
- **Purpose:** Update facilitator context bucket
```

**After:**
```
#### PATCH /api/admin/ai-context/facilitator
- **Purpose:** Update facilitator context bucket
```

**Reasoning:** PATCH is semantically correct for partial resource updates. PUT typically requires sending the entire resource representation.

---

### D-003: Response field added (id)

**Source:** progress.txt US-001
**Original spec:** Response has `content, updated_by, updated_at` (no `id` field)
**Actual implementation:** Response includes `id` field

**Before:**
```json
{
  "content": "string",
  "updated_by": { "id": "uuid", "display_name": "string" },
  "updated_at": "iso8601"
}
```

**After:**
```json
{
  "id": "uuid",
  "content": "string",
  "updated_by": { "id": "uuid", "display_name": "string" },
  "updated_at": "iso8601"
}
```

**Reasoning:** Frontend needs the bucket identifier for tracking and cache invalidation. Standard REST pattern includes resource ID in GET responses.

---

### D-004: Empty query returns all users

**Source:** progress.txt US-004 line 76
**Original spec:** Query parameter behavior not explicitly specified
**Actual implementation:** Empty search query (no `?q=` param) returns all users

**Added to spec:**
```
| q | string | Search query (name, first name, or email). **Optional** — if empty or omitted, returns all users. |
```

Plus notes section:
```
**Notes:** Empty query returns all users (different from regular `/api/users/search` which requires minimum 2 chars).
```

**Reasoning:** Admins need the ability to view all users in the system, not just search for specific ones. Different UX from regular user search (which is performance-optimized with minimum query length).

---

### D-005: Context re-indexing failure handling

**Source:** progress.txt US-005 line 90
**Original spec:** Error handling not specified in api-design.md
**Actual implementation:** gRPC re-indexing failure returns 500 with `REINDEX_FAILED` but DB update persists

**Added to spec:**
```
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 500 | REINDEX_FAILED | gRPC re-indexing failed (DB update persists) |
- **Side effects:** Triggers AI service re-indexing via gRPC `update_context_agent_bucket`.
  If re-indexing fails, returns 500 but DB update persists (fire-and-fail pattern).
```

**Reasoning:** DB update is the primary operation (source of truth). Re-indexing is a derived operation (optimization). Avoiding transactional rollback across gRPC boundary reduces complexity. Admins can retry the PATCH to re-trigger indexing if it failed.

---

### D-006: Monitoring service architecture (namespace mirroring)

**Source:** progress.txt US-006 lines 99-100
**Original spec:** Core service monitoring app (tech-stack.md line 297)
**Actual implementation:** Business logic in Core, but files mirrored to Gateway for test discoverability

**Added to project-structure.md:**
```
**Module mirroring for test discoverability (as of M15):** Some Core service modules are
mirrored into Gateway for test discoverability when namespace conflicts exist. For example,
`apps.monitoring` exists in both Core and Gateway. Core owns the business logic
(`health_checks.py`, `tasks.py`), but these files are mirrored into Gateway's
`apps.monitoring/` directory so Gateway's test runner can discover and test them.
This pattern is used sparingly when PYTHONPATH resolution would otherwise break test imports.
```

**Added to tech-stack.md:**
```
**Module location:** Core service (`services/core/apps/monitoring/`). Files are mirrored
into Gateway's `apps.monitoring/` for test discoverability due to namespace conflict
(both services have `apps.monitoring` packages). See `project-structure.md` Module Mirroring section.
```

**Reasoning:** Architectural constraint. Both Core and Gateway need an `apps.monitoring` package (Core for Celery tasks, Gateway for REST endpoints). Python's module system prioritizes the first match on PYTHONPATH. When running Gateway's test suite, Gateway's path comes first, so `import apps.monitoring.health_checks` would fail to find Core's module. Mirroring the files allows tests to import and validate the business logic without changing the service boundary.

---

### D-007: Soft-deleted ideas filtering

**Source:** progress.txt US-003 line 65
**Original spec:** Query behavior not explicitly specified
**Actual implementation:** `ideas_by_state` excludes soft-deleted ideas

**Added to spec:**
```
**Notes:** [...] `ideas_by_state` counts exclude soft-deleted ideas (`deleted_at IS NOT NULL`).
```

**Reasoning:** Soft-deleted ideas are in the trash (pending permanent deletion). Including them in state counts would be misleading for monitoring purposes.

---

### D-008: Alert config returns current user only

**Source:** api-design.md lines 1302-1312, progress.txt US-007 lines 115-116
**Original spec:** `GET /api/admin/monitoring/alerts` returns `{"recipients": [...]}`
**Actual implementation:** Returns only current user's config `{"user_id": "...", "is_active": bool}`

**Before:**
```json
{
  "recipients": [
    { "user_id": "uuid", "display_name": "string", "is_active": true }
  ]
}
```

**After:**
```json
{
  "user_id": "uuid",
  "is_active": true
}
```

Plus updated purpose and notes:
```
- **Purpose:** Get current user's alert configuration
- **Notes:** Returns only the current admin user's own alert opt-in status (not all recipients).
  Uses upsert pattern (creates config row on first access with `is_active=false`).
```

**Reasoning:** Simpler frontend UX — admins manage their own opt-in status via a personal toggle switch. The "who's opted in" question is answered server-side (notification service queries opted-in admins via gateway gRPC when sending alerts). Avoids permission complexity (can an admin disable another admin's alerts?).

---

### D-009: board_nodes.created_by clarification

**Source:** progress.txt US-004 line 74
**Original spec:** Data model didn't clarify that `created_by` is not a foreign key
**Actual implementation:** `created_by` is a CharField ('user'/'ai'), not a user FK

**Added to data-model.md:**
```
- `created_by` is a literal string ('user' or 'ai'), not a foreign key.
  To determine which user created a node, join via `idea_id` to `ideas.owner_id` or `ideas.co_owner_id`.
```

**Reasoning:** Schema clarification. The column name could be misinterpreted as a user foreign key. The note prevents future confusion and documents the join pattern needed for user attribution.

---

## Validation Checklist

All changes satisfy reconciliation constraints:

- [x] All deviations cited with exact source (progress.txt entry or QA report)
- [x] All upstream docs cited with file path and section reference
- [x] Before/after comparison shown for each change
- [x] Autonomy level justified for each deviation
- [x] Only docs/ directory modified (no source code changes)
- [x] All changes increase spec accuracy (no speculative additions)
- [x] No cascading changes needed in future milestones
- [x] Changelog is comprehensive and traceable

---

**Status:** COMPLETE
**Reviewed by:** Spec Reconciler (Claude)
**Next step:** Milestone M16 (if any) or project release preparation
