# QA Report: Milestone 3 — Workspace Chat

**Date:** 2026-03-09
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1
**PRD:** tasks/prd-m3.json
**Progress:** .ralph/progress.txt

---

## Summary

Milestone 3 implements the Idea Workspace page with two-panel layout, chat messaging, reactions, inline title editing, agent mode dropdown, @mentions, and section visibility/locking. This is **bugfix cycle 1** following the initial review which found 2 defects: 21 missing frontend tests (DEF-001) and an ESLint rules-of-hooks violation (DEF-002). Both defects have been resolved. All 10 user stories pass acceptance criteria, all 26 test matrix tests are implemented with real assertions, all 63 Python tests pass, and all required gate checks pass. The milestone **PASSES** this QA cycle.

---

## Bugfix Verification

### DEF-001 (Cycle 0): 21 missing frontend unit tests — FIXED
All 21 frontend tests have been implemented across 5 new test files:
- `frontend/src/__tests__/workspace-layout.test.tsx` — T-1.1.01, T-1.1.02, T-1.1.03
- `frontend/src/__tests__/section-visibility.test.tsx` — T-1.2.01, T-1.2.02, T-1.2.03, T-1.4.01, T-1.4.02, T-1.4.03, T-1.4.04, T-1.4.05
- `frontend/src/__tests__/workspace-header.test.tsx` — T-1.6.01, T-1.6.02, T-1.6.03, T-2.1.01, T-2.1.02
- `frontend/src/__tests__/idea-workspace.test.tsx` — T-1.7.01, T-1.7.02
- `frontend/src/__tests__/mention-dropdown.test.tsx` — T-2.9.01, T-2.9.02, T-2.9.03

All tests contain real assertions (not stubs) using React Testing Library. Verified by code review.

### DEF-002 (Cycle 0): ESLint rules-of-hooks violation — FIXED
`useCallback` at `frontend/src/pages/IdeaWorkspace/index.tsx:51` is now called unconditionally before any early returns. ESLint passes clean on the file.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Chat Messages API | PASS | POST creates message (201), GET lists with pagination, validates content/access |
| US-002 | User Reactions API | PASS | POST/DELETE reactions, validates AI/self/duplicate rules (400/409), 12 tests pass |
| US-003 | Workspace Page Route | PASS | Route renders, fetches idea, loading/error states, document.title updates. Hooks violation fixed. |
| US-004 | Two-Panel Layout with Draggable Divider | PASS | Chat/board panels, divider drag, localStorage, double-click reset, Board tab default |
| US-005 | Workspace Header | PASS | Back button, editable title, agent mode dropdown, optimistic updates |
| US-006 | Section Visibility + Locking | PASS | State-based visibility/locking, LockOverlay with bg-card/80. All 8 tests implemented. |
| US-007 | Chat Message Display | PASS | User/AI/delegation bubbles, auto-scroll, empty state |
| US-008 | ChatInput with Send Button | PASS | Auto-grow textarea, Enter sends, send button, loading state |
| US-009 | @Mention Dropdown | PASS | @ trigger, filter, keyboard nav, insert, close on Escape/outside. All 3 tests implemented. |
| US-010 | User Reactions UI | PASS | Reaction chips, toggle, optimistic updates, error toast |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 26 found / 0 missing out of 26 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-1.1.01 | FOUND | `frontend/src/__tests__/workspace-layout.test.tsx` | Verified — renders chat and context panels with divider |
| T-1.1.02 | FOUND | `frontend/src/__tests__/workspace-layout.test.tsx` | Verified — drag resizes, localStorage persistence, double-click reset |
| T-1.1.03 | FOUND | `frontend/src/__tests__/workspace-layout.test.tsx` | Verified — Board tab default active, Review tab visibility |
| T-1.2.01 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — review hidden when state=open |
| T-1.2.02 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — review visible for in_review, rejected, accepted |
| T-1.2.03 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — review visibility across all non-open states |
| T-1.4.01 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — open state: no lock overlay, chat enabled |
| T-1.4.02 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — in_review: lock overlay with explanation text |
| T-1.4.03 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — rejected: no lock overlay, chat enabled |
| T-1.4.04 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — accepted: lock overlay, all read-only |
| T-1.4.05 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Verified — dropped: lock overlay, all read-only |
| T-1.6.01 | FOUND | `frontend/src/__tests__/workspace-header.test.tsx` | Verified — title click-to-edit, Enter saves, Escape cancels, readOnly guard |
| T-1.6.02 | FOUND | `frontend/src/__tests__/workspace-header.test.tsx` | Verified — PATCH with title, optimistic update, revert on failure |
| T-1.6.03 | FOUND | `frontend/src/__tests__/workspace-header.test.tsx` | Verified — onIdeaUpdate called with updated title for document.title flow |
| T-1.7.01 | FOUND | `frontend/src/__tests__/idea-workspace.test.tsx` | Verified — loading skeleton then workspace render, document.title update |
| T-1.7.02 | FOUND | `frontend/src/__tests__/idea-workspace.test.tsx` | Verified — 404 and 403 error states |
| T-2.1.01 | FOUND | `frontend/src/__tests__/workspace-header.test.tsx` | Verified — agent mode trigger renders, shows current value, disabled when readOnly |
| T-2.1.02 | FOUND | `frontend/src/__tests__/workspace-header.test.tsx` | Verified — dropdown selection calls patchIdea, optimistic update, revert on failure |
| T-2.8.01 | FOUND | `services/gateway/apps/chat/tests/test_reactions.py` | Verified — react to other user's message (201) |
| T-2.8.02 | FOUND | `services/gateway/apps/chat/tests/test_reactions.py` | Verified — cannot react to AI (400) |
| T-2.8.03 | FOUND | `services/gateway/apps/chat/tests/test_reactions.py` | Verified — cannot react to own (400) |
| T-2.8.04 | FOUND | `services/gateway/apps/chat/tests/test_reactions.py` | Verified — duplicate reaction (409) |
| T-2.8.05 | FOUND | `services/gateway/apps/chat/tests/test_reactions.py` | Verified — remove reaction (204) |
| T-2.9.01 | FOUND | `frontend/src/__tests__/mention-dropdown.test.tsx` | Verified — @ opens dropdown, @ai first with Bot icon, Escape closes, filter works |
| T-2.9.02 | FOUND | `frontend/src/__tests__/mention-dropdown.test.tsx` | Verified — click/Enter inserts @username, arrow key navigation |
| T-2.9.03 | FOUND | `frontend/src/__tests__/mention-dropdown.test.tsx` | Verified — display names rendered, alphabetical order, initials avatar |

---

## Defects

No defects found. Both defects from cycle 0 have been resolved.

---

## Deviations

No deviations found. Implementation matches specifications.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 63 passed in 2.75s |
| Frontend typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend typecheck (mypy) | `mypy services/` | FAIL (optional) | 1 error: duplicate module "events" (pre-existing, not M3-related) |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | PASS | Clean (DEF-002 fixed) |
| Node tests (Vitest) | `docker compose -f docker-compose.test.yml run --rm node-tests npx vitest run` | PASS | All tests pass including new M3 frontend tests |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| -- | -- | -- | -- | No security issues found | -- |

**Analysis:**
- **Injection:** Chat message content is validated via DRF serializer (min_length=1). No raw SQL. Parameterized ORM queries throughout.
- **Authentication:** All endpoints require authentication via `MiddlewareAuthentication`. Unauthenticated requests return 401.
- **Access Control:** `_check_access()` verifies owner/co-owner/collaborator on every chat and reaction endpoint. Tested with 403 cases.
- **Input Validation:** `ReactionCreateSerializer` validates `reaction_type` against allowed choices. UUID validation on path parameters.
- **XSS:** React's default escaping handles user content. No `dangerouslySetInnerHTML` usage.
- **CSRF:** Cookie-based auth with `credentials: "include"`. Django's CSRF middleware applies.
- **Sensitive Data:** No hardcoded secrets. API base URL from environment config.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| -- | -- | -- | -- | No significant performance issues found | -- |

**Analysis:**
- Chat messages fetched with pagination (limit/offset) -- no unbounded queries.
- `ChatMessageList` deduplication uses `Set` for O(1) lookups.
- Auto-scroll uses `useRef` with `scrollIntoView` -- appropriate pattern.
- `WorkspaceLayout` clamps ratio on resize with proper cleanup.
- `PanelDivider` attaches document listeners only during drag (proper cleanup).
- `useSectionVisibility` uses `useMemo` for derived state.
- `MentionDropdown` filtered items use `useMemo`.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| WorkspaceLayout | PRD US-004 | PASS | Two panels, draggable divider, Board tab default, localStorage |
| PanelDivider | PRD US-004 | PASS | 4px visual, 12px hit area (4px padding each side), gold on hover/drag |
| WorkspaceHeader | PRD US-005 | PASS | Back button, editable title, agent mode Select, presence placeholder |
| LockOverlay | PRD US-006 | PASS | bg-card/80, Lock icon, explanation text |
| ChatMessageList | PRD US-007 | PASS | Right-aligned user bubbles (bg-secondary, rounded-tr-sm), left AI (bg-card+border, rounded-tl-sm, Bot icon) |
| DelegationMessage | PRD US-007 | PASS | opacity-60, italic |
| ChatInput | PRD US-008 | PASS | Auto-grow textarea, 20px circle placeholder, send button with ArrowRight/Loader2 |
| MentionDropdown | PRD US-009 | PASS | @ trigger, @ai with Bot icon first, keyboard nav |
| ReactionChips | PRD US-010 | PASS | 3 emoji buttons, count, active highlight (bg-primary/20), rounded-full |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] `/idea/:uuid` route renders IdeaWorkspacePage with loading skeleton, then content
- [ ] Invalid UUID at `/idea/not-a-uuid` shows 404 error state
- [ ] Non-accessible idea at `/idea/:uuid` shows 403 error state
- [ ] Back button navigates to `/`
- [ ] `document.title` updates to idea title and resets to "ZiqReq" on unmount

### API Endpoints
- [ ] `POST /api/ideas/:id/chat` creates message, returns 201 with correct shape
- [ ] `GET /api/ideas/:id/chat` returns paginated messages ordered by created_at ASC
- [ ] `POST /api/ideas/:id/chat/:msgId/reactions` creates reaction (201), validates AI (400), self (400), duplicate (409)
- [ ] `DELETE /api/ideas/:id/chat/:msgId/reactions` removes reaction (204)
- [ ] `PATCH /api/ideas/:id` updates title and agent_mode

### Features
- [ ] Two-panel layout resizes via draggable divider, ratio persisted in localStorage
- [ ] Double-click divider resets to 40/60 split
- [ ] Board tab is default active in context panel
- [ ] Title click-to-edit: Enter saves, Escape cancels, blur saves
- [ ] Agent mode dropdown: Interactive/Silent, change sends PATCH
- [ ] Section visibility: review hidden for open/never-submitted, visible after submission
- [ ] Chat locked during in_review, all read-only for accepted/dropped
- [ ] Chat messages display correctly: user right, AI left with Bot icon, delegation italic/opacity-60
- [ ] Auto-scroll on load (instant) and new messages (smooth)
- [ ] Empty state shows "Start brainstorming..." with Lightbulb icon
- [ ] ChatInput: Enter sends, Shift+Enter newline, auto-grow, disabled when sending
- [ ] @ mention dropdown opens with collaborators + @ai, keyboard nav, filter, insert
- [ ] Reaction chips toggle add/remove with optimistic updates, error toast on failure

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 63 Python tests pass
- [ ] All Vitest frontend tests pass (including M3 tests)
- [ ] Ruff lint passes
- [ ] ESLint passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (2 from cycle 0 resolved)
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1
