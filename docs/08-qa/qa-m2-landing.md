# QA Report: Milestone 2 — Landing Page & Idea CRUD

**Date:** 2026-03-09
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m2.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed 8 user stories covering the Ideas REST API (CRUD + soft delete/restore), Invitations List API, Landing Page layout, IdeaCard component, idea creation flow, TanStack Query data fetching, search & filter bar, and Ideas List floating window. All 36 Python tests pass, frontend typecheck passes, Ruff passes, ESLint passes. All 6 test matrix items found and verified. **Zero defects.** Two deviations logged (PRD bookkeeping, mypy optional gate).

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Ideas REST API — CRUD Endpoints | PASS | All 11 acceptance criteria verified in code and tests. POST creates with first_message (201), GET lists with pagination/filter/search, GET/:id with 403 for non-auth, DELETE soft-deletes, POST restore clears deleted_at, 401 for unauth, 404 for missing. |
| US-002 | Invitations List API | PASS | All 6 criteria verified. GET /api/invitations returns pending only, correct response shape, 401 for unauth, empty list when none. |
| US-003 | Landing Page Layout | PASS | All 8 criteria verified. Hero section present, 4 lists render (My Ideas, Collaborating, Invitations, Trash), section headings with count badge, empty states with Lucide icons, IdeaCard navigates to /idea/:uuid, PageShell wraps page. |
| US-004 | IdeaCard Component | PASS | All 9 criteria verified. State dot 8px with correct colors, title truncation, relative timestamp, state badge, three-dot menu with Delete/Restore, click navigation, stopPropagation on menu. |
| US-005 | Idea Creation Flow | PASS | All 8 criteria verified. Hero textarea captures input, POST /api/ideas on submit, redirect to /idea/:uuid on success, Loader2 spinner during pending, empty input validation, error with retry button. |
| US-006 | Idea Lists with TanStack Query | PASS | All 10 criteria verified in code. Four separate hooks fetch correct endpoints, IdeaCardSkeleton for loading, EmptyState for empty lists, undo toast with 5s autoClose on delete, cache invalidation via queryClient on create/delete/restore. DEV-001: PRD has passes=false but story is implemented and passing. |
| US-007 | Search & Filter Bar | PASS | All 9 criteria verified. Search debounced at 300ms, state dropdown with all 5 states + All, ownership dropdown with My Ideas/Collaborating/All, filters only apply to My Ideas and Collaborating lists, clear button resets, URL params synced via useSearchParams. DEV-001: PRD has passes=false. |
| US-008 | Ideas List Floating Window | PASS | All 10 criteria verified. Navbar 'Ideas' button toggles floating panel, 4 tabs (Active/In Review/Accepted/Closed), IdeaCardCompact with state dot + title, click navigates + closes, empty tab messages, Escape/click-outside closes. DEV-001: PRD has passes=false. |

**Stories passed:** 8 / 8
**Stories with defects:** 0
**Stories with deviations:** 1 (DEV-001 affects US-006, US-007, US-008)

---

## Test Matrix Coverage

**Pipeline scan results:** 6 found / 0 missing out of 6 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-9.1.01 | FOUND | `frontend/src/__tests__/landing-page.test.tsx` | Verified — renders all 4 lists with section headings |
| T-9.2.01 | FOUND | `frontend/src/__tests__/idea-creation-flow.test.tsx` | Verified — types message, submits, mocks API, asserts navigation |
| T-9.3.01 | FOUND | `services/gateway/apps/ideas/tests/test_views.py` | Verified — soft delete sets deleted_at, appears in trash list |
| T-9.3.02 | FOUND | `services/gateway/apps/ideas/tests/test_views.py` | Verified — restore clears deleted_at, no longer in trash |
| T-9.4.01 | FOUND | `services/gateway/apps/ideas/tests/test_views.py` | Verified — search=machine returns filtered results |
| T-9.4.02 | FOUND | `services/gateway/apps/ideas/tests/test_views.py` | Verified — state=open returns only open ideas |

All test IDs registered in `.ralph/test-manifest.json` with correct file paths and function names.

---

## Defects

None.

---

## Deviations

### DEV-001: PRD passes field not updated for US-006, US-007, US-008
- **Story:** US-006, US-007, US-008
- **Spec document:** tasks/prd-m2.json
- **Expected (per spec):** `"passes": true` after successful implementation
- **Actual (in code):** `"passes": false` in prd-m2.json, but `.ralph/progress.txt` shows all three stories as Status: PASS with all tests green
- **Why code is correct:** All three stories are fully implemented, all tests pass (52 Node tests, 36 Python tests at completion), all acceptance criteria met. This is a bookkeeping error — Ralph implemented the stories but did not update the PRD's passes field.
- **Spec update needed:** Set `"passes": true` for US-006, US-007, US-008 in tasks/prd-m2.json

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python Tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 36 passed in 1.11s (17 ideas + 5 collaboration + 13 auth + 1 smoke) |
| Frontend Typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | SKIPPED | Optional gate. Fails with duplicate module "events" (pre-existing issue from M1 — `services/core/events/__init__.py` vs `services/ai/events/__init__.py`). Not an M2 concern. |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | PASS | Clean |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | CSRF Protection | Minor | `services/gateway/apps/ideas/views.py` | DRF `@api_view` decorator applies `@csrf_exempt` by default. State-changing endpoints (POST, DELETE) are not CSRF-protected when using session auth. | This is standard DRF behavior and acceptable for APIs consumed by SPA with session auth + CORS. If CSRF protection is desired later, add `CsrfViewMiddleware` and send CSRF token from frontend. Low risk in current architecture (dev bypass + Azure AD JWT primary). |

**No critical or major security findings. Minor finding is informational only.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Notes:**
- Backend list endpoints batch user lookups to avoid N+1 (`services/gateway/apps/ideas/views.py:157-159`, `services/gateway/apps/collaboration/views.py:32-33`).
- Invitations endpoint also batches idea and inviter lookups.
- Frontend uses TanStack Query for caching and deduplication.
- Filter hook uses `useCallback`/`useMemo` to minimize re-renders.
- Debounce (300ms) prevents excessive API calls on search input.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| Landing Page | `docs/03-design/page-layouts.md` S1 | PASS | Hero section centered with heading/subtext/input/button. 4 ordered lists in 2-column grid (md:grid-cols-2). Mobile stacks to single column. |
| HeroSection | `docs/03-design/page-layouts.md` S1.2 | PASS | Large textarea (min-h-24), 'Begin' button, centered layout. |
| IdeaCard | `docs/03-design/component-specs.md` 2.2 | PASS | State dot 8px circle with correct colors (open=#0284C7, in_review=#F59E0B, accepted=#16A34A, dropped=#9CA3AF, rejected=#F97316). Title truncated. Timestamp relative. Badge with state variant. Three-dot menu. |
| FilterBar | `docs/03-design/component-inventory.md` FilterBar | PASS | Search input with Search icon (left) and X clear button (right). State dropdown. Ownership dropdown. Clear all button. |
| Empty States | `docs/03-design/component-specs.md` 11.3 | PASS | Appropriate Lucide icons per list (Lightbulb, Users, Mail, Trash2). EmptyState component from M1 reused. |
| Skeleton Loading | `docs/03-design/component-specs.md` 11.2 | PASS | IdeaCardSkeleton component for loading states. |
| Ideas List Floating | `docs/03-design/page-layouts.md` S10 | PASS | 320px wide (w-80), shadow-lg, rounded-lg. 4 tabs (Active/In Review/Accepted/Closed). Compact items (state dot + title only). Click-outside and Escape close. |
| Idea State Colors | `docs/03-design/design-system.md` 2.5 | PASS | Colors match spec: open=#0284C7 (sky-600), in_review=#F59E0B (amber-500), accepted=#16A34A (green-600), dropped=#9CA3AF (gray-400), rejected=#F97316 (orange-500). |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Landing page loads at `/` with all 4 list sections (My Ideas, Collaborating, Invitations, Trash)
- [ ] HeroSection renders centered heading, subtext, textarea, and submit button
- [ ] IdeaCard click navigates to `/idea/:uuid`
- [ ] Ideas List Floating window opens from Navbar 'Ideas' button

### API Endpoints
- [ ] `POST /api/ideas/` with `{first_message: "text"}` returns 201 with idea object
- [ ] `POST /api/ideas/` with empty first_message returns 400
- [ ] `GET /api/ideas/` returns paginated results with `{results, count, next, previous}`
- [ ] `GET /api/ideas/?filter=my_ideas` returns only owned ideas
- [ ] `GET /api/ideas/?filter=collaborating` returns only collaborating ideas
- [ ] `GET /api/ideas/?filter=trash` returns only soft-deleted ideas
- [ ] `GET /api/ideas/?state=open` filters by idea state
- [ ] `GET /api/ideas/?search=keyword` searches by title (case-insensitive)
- [ ] `GET /api/ideas/:id` returns full idea for owner/collaborator, 403 for others
- [ ] `DELETE /api/ideas/:id` soft-deletes (sets deleted_at), returns 200
- [ ] `POST /api/ideas/:id/restore` clears deleted_at, returns 200
- [ ] `GET /api/invitations/` returns pending invitations with correct shape
- [ ] All endpoints return 401 for unauthenticated requests
- [ ] Non-existent idea UUID returns 404

### Data Integrity
- [ ] Ideas table supports soft delete via `deleted_at` nullable timestamp
- [ ] ChatMessage created as side effect of POST /api/ideas
- [ ] IdeaCollaborator join table correctly filters collaborating ideas

### Features
- [ ] Search & filter bar: debounced search (300ms), state dropdown, ownership dropdown, clear button
- [ ] URL params sync: `?search=X&state=Y&filter=Z` reflect filter state
- [ ] Undo toast appears on soft delete with 5s countdown and undo button
- [ ] Ideas List Floating: 4 tabs (Active, In Review, Accepted, Closed), closes on Escape/click-outside
- [ ] Empty states render appropriate messages and icons for each list

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 36 Python tests pass
- [ ] All frontend tests pass
- [ ] Ruff lint passes
- [ ] ESLint passes

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 1 (DEV-001 — PRD passes field not updated for 3 stories)
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
