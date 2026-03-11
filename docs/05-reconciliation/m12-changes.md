# Milestone 12 Spec Reconciliation

## Summary
- **Milestone:** M12 — Notification System
- **Date:** 2026-03-11
- **Total deviations found:** 7
- **Auto-applied (SMALL TECHNICAL):** 2
- **Applied and flagged (FEATURE DESIGN):** 2
- **Applied and flagged (LARGE TECHNICAL):** 3
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-007: URL Ordering for Django Routing | — | No spec change needed. Django best practice: specific paths (`unread-count`, `mark-all-read`) must come before parameterized path `<str:notification_id>` in urls.py. Implementation detail, not spec-level. |
| 2 | D-005: Email Preferences Default Behavior | — | No spec change needed. Spec at `docs/02-architecture/api-design.md:1114` already correctly documents "Missing preference keys default to true (all enabled)". Implementation matches spec. |

### FEATURE DESIGN (Applied and flagged)

| # | Deviation | Document Updated | Change | Reason |
|---|-----------|-----------------|--------|--------|
| 1 | D-001: Email Preferences Response Shape | `docs/02-architecture/api-design.md:1099-1128` | Changed response structure from flat per-category to nested `{label, preferences}` structure. Each category now returns `{"label": "CategoryName", "preferences": {...}}` instead of just `{...}`. | Frontend `EmailPreferencesPanel` needed category labels for display. Nesting allows category metadata expansion in future. Backend changed at `services/gateway/apps/authentication/views.py:201` to match frontend expectations. |
| 2 | D-006: Notification Ownership 404 Pattern | `docs/02-architecture/api-design.md:1059-1070` | Added error codes table for `PATCH /api/notifications/:id` endpoint. Returns 404 (not 403) when notification belongs to another user. | Security best practice to prevent information leakage. Don't reveal that a notification exists for a different user. |

### LARGE TECHNICAL (Applied and flagged)

| # | Deviation | Document Updated | Change | Reason |
|---|-----------|-----------------|--------|--------|
| 1 | D-002: Events Publisher Utility Created | `docs/02-architecture/project-structure.md:346` | Added `services/gateway/events/publisher.py` to Gateway service structure. Shared RabbitMQ publisher utility with `publish_notification_event()` function. | Multiple views (collaboration, review, chat) needed to publish events. Extracted to DRY pattern to avoid code duplication across view files. |
| 2 | D-003: Lazy Import Pattern for Event Publisher | `docs/02-architecture/project-structure.md:131-170` | Added new section "Event Publisher Import Pattern (CRITICAL)" documenting that views MUST use lazy imports (inside function body) for `events.publisher`, not top-level imports. | `test_ai_consumer.py` manipulates `sys.modules` for `events` package at collection time, breaking top-level imports when pytest collects all tests. Lazy import pattern (via helper function) is required. |
| 3 | D-004: CSS Animation in globals.css | `docs/03-design/component-specs.md:151-158` | Updated Notification Count Badge spec to document that custom animations must be defined in `globals.css` using `@keyframes` and `animation` property (Tailwind v4 constraint). | Tailwind v4 uses `@theme` and doesn't have `tailwind.config.js` for custom animations. All custom animations must go in CSS file. Added implementation note to spec. |

### REJECTED

None.

## Documents Modified

1. `docs/02-architecture/api-design.md`
   - Lines 1099-1128: Updated `GET /api/users/me/notification-preferences` response structure to nested `{label, preferences}` format
   - Lines 1059-1070: Added error codes table for `PATCH /api/notifications/:id` (404 for ownership checks)

2. `docs/02-architecture/project-structure.md`
   - Line 346: Added `publisher.py` file to Gateway events directory structure
   - Lines 131-170: Added "Event Publisher Import Pattern (CRITICAL)" section documenting lazy import requirement

3. `docs/03-design/component-specs.md`
   - Lines 151-158: Added note about Tailwind v4 animation location requirement in Notification Count Badge spec

## Impact on Future Milestones

### Email Preferences Response Shape (D-001)
- **Affected milestones:** Any future milestone that adds new notification preference categories
- **Action required:** New categories must follow the `{label, preferences}` nested structure
- **Test pattern:** Backend tests must access nested path: `response["categories"]["CategoryName"]["preferences"]["pref_key"]`

### Events Publisher Pattern (D-002, D-003)
- **Affected milestones:** Any future milestone that publishes notification events from Gateway views
- **Action required:** All view files that import from `events.publisher` MUST use lazy imports via helper functions
- **Code pattern:**
  ```python
  def _publish_notification(**kwargs):
      from events.publisher import publish_notification_event
      publish_notification_event(**kwargs)
  ```
- **Testing note:** Ensures pytest collection doesn't fail due to `sys.modules` manipulation in other tests

### Tailwind v4 Animation Pattern (D-004)
- **Affected milestones:** Any future milestone that requires custom CSS animations
- **Action required:** Define animations in `globals.css` using `@keyframes`, not in a Tailwind config file
- **Rationale:** Tailwind v4 architecture constraint — no `tailwind.config.js` for custom animations

## Security Findings (from QA Report)

These were NOT spec deviations but are noted here for visibility:

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | XSS (Email) | Minor | `services/notification/email/renderer.py` | HTML email body embeds `body` and `recipient_name` via f-string without HTML escaping. | Use `html.escape()` on user-generated content before HTML embedding. |
| SEC-002 | Input Validation | Minor | `services/gateway/apps/notifications/views.py:51-52` | `page` and `page_size` parsed with `int()` without try/except. No upper bound on `page_size`. | Wrap in try/except with defaults. Add `page_size = min(page_size, 100)` cap. |

**Note:** These are recommendations for future improvement, not blocking defects. They were not fixed in M12 and do not require spec changes.

## Performance Findings (from QA Report)

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Connection Pooling | Minor | `services/gateway/events/publisher.py` | `publish_notification_event` creates a new RabbitMQ connection per event. | Consider connection pool or singleton pattern. Non-blocking for MVP. |

**Note:** This is a recommendation for future improvement, not a blocking defect. It was not fixed in M12 and does not require spec changes.

## Bugfix Cycle Summary

M12 had 2 bugfix cycles:

### Bugfix Cycle 1 (US-003)
- **Issue:** TEST_INFRASTRUCTURE/DB_LIFECYCLE — Gateway test settings had `TEST.NAME = ziqreq_test` (same as main DB name), causing Django to use the main DB as the test DB
- **Fix:** Removed `TEST` dict from `services/gateway/gateway/settings/test.py`, letting Django use default prefix naming which matches `init-test-db.sql`
- **Also added:** `--reuse-db` to `pyproject.toml` pytest addopts to skip DB teardown (Docker manages DB lifecycle)
- **Result:** Resolved PytestWarning for all stories

### Bugfix Cycle 2 (BF-001)
- **Issue:** DEF-001 — EmailPreferencesPanel crash due to backend/frontend response shape mismatch
- **Root cause:** Backend `_build_preferences_response()` at `views.py:201` returned flat dict per category; frontend expected `{label, preferences}` nesting
- **Fix:** Backend changed to `categories[cat_name] = {"label": cat_name, "preferences": prefs}`
- **Also updated:** All 7 tests in `test_notification_prefs.py` to access nested path
- **Result:** All 9 stories passed, QA verdict PASS

**Deviation D-001 reflects this bugfix** — the backend response shape was changed to match frontend expectations, and the spec has been updated accordingly.

## Verification

All changes have been applied to upstream docs. Future milestones should reference the updated specs:

- ✅ Email preferences API now documented with nested `{label, preferences}` structure
- ✅ Notification ownership 404 pattern documented in API error codes
- ✅ Events publisher utility documented in Gateway project structure
- ✅ Lazy import pattern documented with code examples
- ✅ Tailwind v4 animation constraint documented in component specs

**Next milestone implementer:** Read this changelog before starting work to understand M12's architectural decisions and patterns.
