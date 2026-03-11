# QA Report: Milestone 10 — Review Workflow

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m10.json
**Progress:** .ralph/progress.txt

---

## Summary

Milestone 10 implements the complete review workflow: submit flow, reviewer self-assignment/unassignment, review actions (accept/reject/drop/undo), review timeline with comments and nested replies, review page with categorized lists, and all corresponding frontend UI. All 10 user stories were implemented and verified. 566 Python tests pass, all frontend tests pass, typecheck is clean, and all 22 test matrix IDs are accounted for. No defects found.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Submit Idea for Review | PASS | POST /api/ideas/:id/submit creates BRD version, transitions state, creates assignments and timeline entries. Atomic transaction. Resubmission logic verified. PDF generation with error handling (503). 13 tests. |
| US-002 | Self-Assignment & Unassignment API | PASS | POST assign/unassign with conflict-of-interest check (owner + co-owner), duplicate check, state validation, role check. Unique partial index on active assignments. 13 tests. |
| US-003 | Review Actions API | PASS | Accept (no comment), reject/drop/undo (mandatory comment). State machine validated. Timeline entries created atomically. 19 tests. |
| US-004 | Review Timeline API | PASS | GET returns chronological entries with batch-loaded authors. POST creates comment with 201. Nested replies via parent_entry_id with cross-idea validation. 15 tests. |
| US-005 | Review Page List API | PASS | GET /api/reviews returns 5 categories. Reviewer role required. Batch-loaded users. Correct categorization logic (assigned_to_me vs unassigned vs final states). 11 tests. |
| US-006 | Review Page Layout — Frontend | PASS | /reviews route with 5 collapsible categories, counts in headers, empty states, ReviewCard component, default open for Assigned/Unassigned. 9 tests. |
| US-007 | Self-Assignment UI | PASS | Assign/Unassign buttons on ReviewCard, loading states, error toast with Retry, conflict-of-interest disabled + tooltip. Query invalidation on success. 11 tests. |
| US-008 | Review Section Below Fold | PASS | ReviewSection renders below brainstorming with PDF thumbnail, title, state badge, reviewers, timeline. has_been_submitted heuristic. Auto-scroll on state transitions. 9 tests. |
| US-009 | Review Timeline UI | PASS | 3 entry types rendered (comment, state_change, resubmission). Nested replies indented 24px. Reply button + inline CommentInput. WebSocket invalidation. Top-level CommentInput. 14 tests. |
| US-010 | Submit Flow UI — SubmitArea in Review Tab | PASS | SubmitArea in ReviewTab for open/rejected states. Message textarea, reviewer multi-select, submit button with loading. Success toast + query invalidation. Error toast with Retry. 10 tests. |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 22 found / 0 missing out of 22 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-1.2.01 | FOUND | `frontend/src/__tests__/review-section.test.tsx` | Verified — review section hidden for never-submitted idea |
| T-1.2.02 | FOUND | `frontend/src/__tests__/review-section.test.tsx` | Verified — review section visible after first submission |
| T-1.3.01 | FOUND | `frontend/src/__tests__/review-section.test.tsx` | Verified — auto-scroll on state transition |
| T-1.5.01 | FOUND | `services/gateway/apps/review/tests/test_submit.py` | Verified — open to in_review via submit |
| T-1.5.02 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — in_review to accepted |
| T-1.5.03 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — in_review to dropped |
| T-1.5.04 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — in_review to rejected |
| T-1.5.05 | FOUND | `services/gateway/apps/review/tests/test_submit.py` | Verified — rejected to in_review via resubmit |
| T-1.5.06 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — accepted to in_review via undo |
| T-1.5.07 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — dropped to in_review via undo |
| T-1.5.08 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — invalid transition returns 400 |
| T-1.5.09 | FOUND | `services/gateway/apps/review/tests/test_review_actions.py` | Verified — multiple reviewers, latest action wins |
| T-4.7.01 | FOUND | `services/gateway/apps/review/tests/test_submit.py` | Verified — submit creates immutable BRD version |
| T-4.10.01 | FOUND | `services/gateway/apps/review/tests/test_submit.py` | Verified — submit with reviewer IDs creates assignments |
| T-4.10.02 | FOUND | `services/gateway/apps/review/tests/test_submit.py` | Verified — submit without reviewers goes to shared queue |
| T-10.1.01 | FOUND | `services/gateway/apps/review/tests/test_review_list.py` | Verified — review page requires reviewer role |
| T-10.2.01 | FOUND | `services/gateway/apps/review/tests/test_review_list.py` | Verified — ideas grouped correctly into 5 categories |
| T-10.2.02 | FOUND | `frontend/src/__tests__/review-page.test.tsx` | Verified — categories render with counts |
| T-10.2.03 | FOUND | `frontend/src/__tests__/review-page.test.tsx` | Verified — collapsible categories |
| T-10.3.01 | FOUND | `services/gateway/apps/review/tests/test_review_assignments.py` | Verified — self-assignment works |
| T-10.3.02 | FOUND | `services/gateway/apps/review/tests/test_review_assignments.py` | Verified — unassign works |
| T-10.4.01 | FOUND | `services/gateway/apps/review/tests/test_review_assignments.py` | Verified — conflict of interest blocked |

*All expected tests implemented and verified.*

---

## Defects

None.

---

## Deviations

None.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 566 passed, 89 warnings |
| Frontend typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend typecheck (mypy) | `mypy services/` | FAIL (optional) | Pre-existing: duplicate module "events" between services/core and services/ai — not caused by M10 |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | Pre-existing: 3 errors + 1 warning in files not touched by M10 (ai-modified-indicator.test.tsx, board-interactions.test.tsx, FreeTextNode.tsx, BRDSectionEditor.tsx) |

**Note:** Both optional gate check failures are pre-existing and unrelated to M10 changes. No new lint or type errors were introduced.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Detailed review:**

- **Authentication:** All API endpoints use `@authentication_classes([MiddlewareAuthentication])` and `_require_auth()`. Unauthenticated requests return 401.
- **Authorization:** Role-based access control via `_require_reviewer()` on reviewer-only endpoints (assign, unassign, accept, reject, drop, undo, list_reviews). Owner-only submit via owner/co-owner check.
- **Conflict of interest:** Properly checks both `owner_id` and `co_owner_id` in backend assign endpoint and frontend ReviewCard.
- **Input validation:** All user inputs validated through DRF serializers (SubmitIdeaSerializer, ReviewActionCommentSerializer, TimelineCommentSerializer). UUID fields validated.
- **SQL injection:** No raw SQL in view code. All queries use Django ORM with parameterized lookups.
- **XSS:** No `dangerouslySetInnerHTML`. All user content rendered as text nodes in React JSX.
- **CSRF:** REST API uses token-based auth; no session-based CSRF vector.
- **State machine integrity:** State transitions validated server-side with explicit valid-state maps. Invalid transitions return 400.
- **Atomic transactions:** Submit flow and review actions use `transaction.atomic()` for multi-table writes.
- **Immutability:** ReviewTimelineEntry.save() raises ValidationError on update attempts.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Detailed review:**

- **N+1 queries:** Batch-loading pattern used throughout — `list_reviews` collects all user IDs and fetches in one query; `_get_timeline` batch-loads authors; `get_idea_reviewers` batch-loads users.
- **Database indexes:** Migration creates `idx_timeline_idea` (idea_id, created_at), `idx_timeline_parent` (parent_entry_id), and partial unique index `uq_active_review_assignment` on active assignments. These cover the primary query patterns.
- **React re-renders:** `useCallback` used for event handlers in ReviewTimeline. `useMutation` pattern from TanStack Query handles cache invalidation efficiently.
- **Query invalidation:** Targeted — only invalidates specific query keys (["reviews"], ["timeline", ideaId], ["brd", ideaId], ["idea", ideaId]) rather than broad invalidation.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| Review Page (/reviews) | `docs/03-design/page-layouts.md` S3 | PASS | 5 collapsible categories, counts in headers, default open for Assigned/Unassigned |
| ReviewCard | `docs/03-design/component-specs.md` S2.3 | PASS | State dot, title, author + date, badge, action button (Assign/Open pattern) |
| ReviewTimeline | `docs/03-design/component-specs.md` S10 | PASS | 3 entry types (comment, state_change, resubmission), chronological order |
| TimelineEntry | `docs/03-design/component-specs.md` S10.2 | PASS | Comment: avatar + name + content + reply. State change: system icon + italic text. Resubmission: version download buttons. |
| CommentInput | `docs/03-design/component-specs.md` S10.3 | PASS | Textarea + send button, supports parent_entry_id for replies, cancel button |
| SubmitArea | `docs/03-design/component-inventory.md` | PASS | Message textarea, reviewer multi-select with checkboxes, submit button, visible for open/rejected states |
| ReviewSection | `docs/03-design/page-layouts.md` S2 | PASS | PDF thumbnail, title, state badge, reviewer list, timeline below |
| Nested replies | `docs/03-design/component-specs.md` S10 | PASS | 24px left indent via `marginLeft: 24` style |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Review page loads at `/reviews` route
- [ ] Review page is only accessible to users with Reviewer role (403 for non-reviewers)
- [ ] Navbar shows "Reviews" link only for Reviewer role
- [ ] Clicking ReviewCard navigates to `/idea/:id`
- [ ] IdeaWorkspace page renders ReviewSection below fold for non-open ideas

### API Endpoints
- [ ] `POST /api/ideas/:id/submit` creates BRD version, transitions state, creates assignments and timeline entries
- [ ] `POST /api/ideas/:id/submit` returns 400 for non-open/rejected states
- [ ] `POST /api/ideas/:id/submit` returns 403 for non-owner/co-owner
- [ ] `POST /api/reviews/:id/assign` creates active assignment for reviewer
- [ ] `POST /api/reviews/:id/assign` returns 400 CONFLICT_OF_INTEREST for own idea
- [ ] `POST /api/reviews/:id/assign` returns 400 ALREADY_ASSIGNED for duplicate
- [ ] `POST /api/reviews/:id/unassign` sets unassigned_at timestamp
- [ ] `POST /api/ideas/:id/review/accept` transitions in_review to accepted
- [ ] `POST /api/ideas/:id/review/reject` requires comment, transitions to rejected
- [ ] `POST /api/ideas/:id/review/drop` requires comment, transitions to dropped
- [ ] `POST /api/ideas/:id/review/undo` requires comment, transitions back to in_review
- [ ] `GET /api/ideas/:id/review/timeline` returns chronological entries
- [ ] `POST /api/ideas/:id/review/timeline` creates comment entry (201)
- [ ] `GET /api/reviews` returns 5 categories for reviewer role

### Data Integrity
- [ ] `brd_versions` table has UNIQUE(idea_id, version_number) constraint
- [ ] `review_assignments` table has partial unique index on active assignments
- [ ] `review_timeline_entries` table is immutable (no updates allowed via model)
- [ ] State transitions are atomic with timeline entries (transaction.atomic)

### Features
- [ ] Submit flow creates immutable BRD version with sequential version_number
- [ ] Resubmission creates new version and resubmission timeline entry linking old and new version IDs
- [ ] Review timeline supports nested replies via parent_entry_id
- [ ] Conflict of interest check blocks reviewer from reviewing own idea (both owner and co-owner)
- [ ] SubmitArea only visible for open and rejected states
- [ ] WebSocket timeline_update events trigger timeline cache invalidation
- [ ] Collapsible categories on review page (Assigned/Unassigned default open, others collapsed)

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 566+ Python tests pass
- [ ] All frontend tests pass
- [ ] Ruff lint passes
- [ ] No new lint errors introduced

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
