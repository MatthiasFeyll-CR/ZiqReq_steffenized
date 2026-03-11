# QA Report: Milestone 12 — Notification System

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 2 (re-review after bugfix cycle 2)
**PRD:** tasks/prd-m12.json
**Progress:** .ralph/progress.txt

---

## Summary

Re-reviewed M12 (Notification System) after bugfix cycle 2. The sole remaining defect from previous cycles — DEF-001 (EmailPreferencesPanel crash due to backend/frontend response shape mismatch) — has been **fixed**. The backend `_build_preferences_response()` now returns the nested `{label, preferences}` structure the frontend expects, and all backend tests have been updated accordingly. All 639 Python tests pass, all 403 Node tests pass (1 pre-existing failure). All required gate checks pass. **9 of 9 stories pass. Verdict: PASS.**

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Notification REST API | PASS | All 6 ACs verified. Paginated list, unread_count, mark read/acted, mark-all-read, 404 for wrong user. 12 tests pass. |
| US-002 | Notification Creation Service (Gateway gRPC) | PASS | CreateNotification gRPC implemented in `gateway_servicer.py`. Accepts all fields, creates row, returns ID. |
| US-003 | Notification Service Consumer — Event Processing & Email Dispatch | PASS | Consumer entry point, 6 routing key prefixes, `notify_user()` helper creates notification + checks email prefs + sends email. |
| US-004 | Email Notification Preferences API | PASS | GET/PATCH endpoints with categorized nested response. Missing keys default to True. gRPC GetUserPreferences implemented. 7 tests pass. |
| US-005 | Wire All Notification Events | PASS | Events wired for collaboration (7 events), review (3 events), chat (@mention), AI (delegation complete). Lazy import pattern. |
| US-006 | NotificationBell Component | PASS | Lucide Bell in navbar, badge with 99+ cap, scale-in animation, click opens panel, WebSocket count update. |
| US-007 | NotificationPanel Component | PASS | Floating panel with icon/title/body/timestamp, click navigates + marks actioned, empty state with Check icon "All caught up", WebSocket refetch. |
| US-008 | WebSocket Notification Delivery | PASS | `ws:notification` CustomEvent handler, toast with severity mapping, optimistic count increment, 5s autoClose. |
| US-009 | EmailPreferencesPanel Component | PASS | **DEF-001 FIXED.** Backend now returns `{label, preferences}` nesting. Frontend useEffect sync works correctly. Dialog opens without crash, displays all toggles. |

**Stories passed:** 9 / 9
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Bugfix Verification: BF-001 (DEF-001 Resolution)

**Defect:** Backend `_build_preferences_response()` returned flat dicts per category; frontend expected `{label, preferences}` nesting, causing TypeError crash.

**Fix applied in:** `services/gateway/apps/authentication/views.py:201`, `services/gateway/apps/authentication/tests/test_notification_prefs.py`

**Verification of acceptance criteria:**

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | GET returns nested `{label, preferences}` structure | PASS | `views.py:201`: `categories[cat_name] = {"label": cat_name, "preferences": prefs}` |
| 2 | EmailPreferencesPanel opens without crashing | PASS | `EmailPreferencesPanel.tsx:100-104` iterates `cat.preferences` which now resolves correctly |
| 3 | Tests updated and pass | PASS | All 7 tests in `test_notification_prefs.py` use nested path (e.g., `cats["Collaboration"]["preferences"]["collaboration_invitation"]`). 639 Python tests pass. |
| 4 | PATCH still works with partial merge | PASS | `test_update_preferences` and `test_partial_merge_preserves_existing` both pass |
| 5 | Typecheck passes | PASS | Frontend typecheck PASSED |

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in this milestone's PRD stories.

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| API-NOTIF.01 | FOUND | `services/gateway/apps/notifications/tests/test_notification_api.py` | Verified — `test_list_notifications` tests paginated list with unread_count |
| API-NOTIF.02 | FOUND | `services/gateway/apps/notifications/tests/test_notification_api.py` | Verified — `test_unread_count` tests badge count |
| API-NOTIF.03 | FOUND | `services/gateway/apps/notifications/tests/test_notification_api.py` | Verified — `test_mark_as_read` tests mark read/acted |
| API-NOTIF.04 | FOUND | `services/gateway/apps/notifications/tests/test_notification_api.py` | Verified — `test_mark_all_read` tests bulk mark read |
| API-USER.02 | FOUND | `services/gateway/apps/authentication/tests/test_notification_prefs.py` | Verified — `test_get_preferences_default` tests categorized GET with nested structure |
| API-USER.03 | FOUND | `services/gateway/apps/authentication/tests/test_notification_prefs.py` | Verified — `test_update_preferences` tests partial merge PATCH |

All test matrix IDs are registered in `.ralph/test-manifest.json`. No missing tests.

---

## Defects

None. DEF-001 from previous cycles has been resolved.

---

## Deviations

None.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| TypeScript | `npx tsc --noEmit` | PASS | Clean |
| Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Tests (Python) | `pytest` | PASS | 639 passed |
| Tests (Node) | `npx vitest run` | PASS | 403 passed (1 pre-existing failure) |
| Build (Docker) | — | SKIPPED | Condition not met |
| Lint (ESLint) | `npx eslint src/` | FAIL (optional) | 3 errors, 2 warnings — all pre-existing in files not touched by M12 |
| Typecheck (mypy) | `mypy services/` | FAIL (optional) | Duplicate module "events" — pre-existing |

**Gate check summary:** All required gates pass. Optional gates have pre-existing failures only.

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | — |
| Backend lint (Ruff) | PASSED | — |
| Backend typecheck (mypy) | FAILED (optional) | `services/core/events/__init__.py` duplicate module — pre-existing, not M12-related |
| Frontend lint (ESLint) | FAILED (optional) | 3 errors + 2 warnings in `ai-modified-indicator.test.tsx`, `board-interactions.test.tsx`, `BRDSectionEditor.tsx`, `FreeTextNode.tsx`, `IdeaWorkspace/index.tsx` — all pre-existing, none in M12 files |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | XSS (Email) | Minor | `services/notification/email/renderer.py` | HTML email body embeds `body` and `recipient_name` via f-string without HTML escaping. | Use `html.escape()` on user-generated content before HTML embedding. |
| SEC-002 | Input Validation | Minor | `services/gateway/apps/notifications/views.py:51-52` | `page` and `page_size` parsed with `int()` without try/except. No upper bound on `page_size`. | Wrap in try/except with defaults. Add `page_size = min(page_size, 100)` cap. |

**No critical or major security findings. Minor findings are recommendations, not blocking defects.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Connection Pooling | Minor | `services/gateway/events/publisher.py` | `publish_notification_event` creates a new RabbitMQ connection per event. | Consider connection pool or singleton pattern. Non-blocking for MVP. |

**No critical or major performance findings.**

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| NotificationBell (badge) | `docs/03-design/component-specs.md` S3.3 | PASS | Position, size, color, animation, 99+ max all match spec |
| Toast Notifications | `docs/03-design/component-specs.md` S11.1 | PASS | react-toastify, autoClose 5s, severity mapping |
| Empty State (notifications) | `docs/03-design/component-specs.md` S11.3 | PASS | Lucide Check icon + "All caught up" message |
| EmailPreferencesPanel | `docs/03-design/component-specs.md` S11.4 | PASS | Dialog with grouped toggles, group checkbox with indeterminate, save button with dirty tracking |

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### Pages & Navigation
- [ ] NotificationBell renders in Navbar with correct badge count at all routes
- [ ] NotificationPanel opens/closes on bell click and Escape key
- [ ] EmailPreferencesPanel opens from UserDropdown without crashing

### API Endpoints
- [ ] `GET /api/notifications/` returns paginated list with `unread_count`, `count`, `page`, `page_size`
- [ ] `GET /api/notifications/?unread_only=true` filters to unread only
- [ ] `GET /api/notifications/unread-count` returns `{unread_count: N}`
- [ ] `PATCH /api/notifications/:id` with `{is_read: true}` marks notification read
- [ ] `PATCH /api/notifications/:id` with `{action_taken: true}` marks notification actioned
- [ ] `POST /api/notifications/mark-all-read` bulk-marks current user's notifications
- [ ] `GET /api/users/me/notification-preferences` returns `{categories: {Name: {label, preferences: {...}}}}` nested structure
- [ ] `PATCH /api/users/me/notification-preferences` partial-merges boolean values into stored prefs
- [ ] Notification endpoints return 404 (not 403) for other users' notifications
- [ ] Preference endpoints return 401 for unauthenticated requests

### Data Integrity
- [ ] `notifications_notification` table has correct schema (id, user_id, event_type, title, body, reference_id, reference_type, is_read, action_taken, created_at)
- [ ] `email_notification_preferences` jsonb column on User model stores preference overrides

### Features
- [ ] WebSocket `ws:notification` event increments bell badge count and triggers toast
- [ ] Toast severity mapping: review_state* -> warning, removed/declined/monitoring -> warning, joined/accepted/ai_delegation -> success, default -> info
- [ ] Notification click navigates to `/ideas/:id` for idea/invitation/merge_request reference types
- [ ] EmailPreferencesPanel group checkbox shows indeterminate state when items are mixed
- [ ] Missing preference keys default to True (enabled) in both backend and frontend

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 639 Python tests pass
- [ ] All 403 Node tests pass (1 pre-existing failure in `information-gaps-toggle.test.tsx`)
- [ ] Ruff lint passes with zero errors
- [ ] Frontend builds successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (DEF-001 resolved in this cycle)
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 2 (final)
