# Milestone 17: E2E Foundation Tests

## Overview
- **Execution order:** 17 (runs after M16 — all implementation milestones)
- **Estimated stories:** 5
- **Dependencies:** M1–M16 (complete application), E2E test infrastructure (set up manually before this milestone)
- **Type:** E2E Testing

## Purpose

Write foundation-level E2E tests covering authentication, landing page, theme switching, and i18n. The E2E test infrastructure (Playwright config, docker-compose, seed scripts, helpers, page object models) is set up manually before this milestone begins.

## Prerequisites (Manual — done before this milestone)

The following infrastructure must already exist before M17 stories execute:
- `e2e/playwright.config.ts` — Playwright project configuration
- `docker-compose.e2e.yml` — Full stack with AI_MOCK_MODE, AUTH_BYPASS, email capture
- `e2e/global-setup.ts` / `e2e/global-teardown.ts` — Service health wait + seed + cleanup
- `e2e/helpers/` — auth, api, websocket, seed, assertions, email helpers
- `e2e/pages/` — Page Object Models for landing, workspace, review, admin, navbar, components
- A passing smoke test verifying the infrastructure works

## Features Tested

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-7 | Authentication (dev bypass) | P1 | docs/01-requirements/features.md |
| FA-9 | Landing Page | P1 | docs/01-requirements/features.md |
| FA-16 | Multi-Language Support (i18n) | P2 | docs/01-requirements/features.md |
| FA-17 | Theme Support (Light/Dark) | P2 | docs/01-requirements/features.md |

## Story Outline

### S1: E2E Auth Bypass Tests (FA-7)
- **Test: Dev user login and identity** — Select each of the 4 dev users, verify their name/role is displayed in the navbar
- **Test: User role-based access** — User1 (User role) cannot see Review or Admin links in navbar
- **Test: Reviewer role access** — User3 (Reviewer) can see Review link, can navigate to `/reviews`
- **Test: Admin role access** — User4 (Admin) can see Admin link, can navigate to `/admin`
- **Test: Dev user switching** — Switch from User1 to User3 via navbar switcher, verify identity changes, verify role-based UI updates
- **Test: Route protection (negative)** — User1 navigates to `/admin` directly, gets redirected or sees 403
- **Test: Route protection (negative)** — User1 navigates to `/reviews` directly, gets redirected or sees 403

**Acceptance criteria:**
- [ ] All 4 dev users selectable and functional
- [ ] Role-based navbar items appear/disappear correctly
- [ ] Route protection enforced for unauthorized roles

### S2: E2E Landing Page — Idea Lists & Creation (FA-9)
- **Test: Empty state** — New user sees empty "My Ideas" list with appropriate empty state message
- **Test: Idea creation from hero** — Type message in hero section, submit → navigated to `/idea/<uuid>`, first chat message visible
- **Test: My Ideas list** — Create 2 ideas, verify they appear in "My Ideas" with correct titles
- **Test: Idea card displays** — Verify idea cards show title, state badge, timestamp
- **Test: Navigate to idea** — Click idea card → navigated to correct `/idea/<uuid>`
- **Test: Multiple ideas in various states** — Create ideas, submit one for review (via API), verify state badges (Open, In Review) display correctly

**Acceptance criteria:**
- [ ] Idea creation from landing page works end-to-end
- [ ] Ideas list displays correctly with state badges
- [ ] Navigation to idea workspace works

### S3: E2E Landing Page — Search, Filter, Soft Delete (FA-9)
- **Test: Search by title** — Create 3 ideas with distinct titles, search for one → only matching idea shown
- **Test: Filter by state** — Create ideas in different states (via API), apply state filter → only matching state shown
- **Test: Filter by ownership** — Create owned idea + accept collaboration on another → filter "My Ideas" vs "Collaborating"
- **Test: Soft delete** — Delete an idea → undo toast appears, idea moves to Trash list
- **Test: Undo soft delete** — Delete idea, click undo within toast → idea restored to original list
- **Test: Trash list** — Delete idea, verify it appears in Trash section with appropriate indicator
- **Test: Soft delete does not appear in active lists** — Deleted idea not visible in My Ideas or Collaborating

**Acceptance criteria:**
- [ ] Search filters ideas by title
- [ ] State filter works for all states
- [ ] Soft delete + undo works correctly
- [ ] Trash list shows deleted ideas

### S4: E2E Theme Support (FA-17)
- **Test: Default theme (light or system preference)** — Fresh page load respects OS `prefers-color-scheme` or defaults to light
- **Test: Toggle to dark mode** — Open user menu → click theme toggle → all visible elements switch to dark theme
- **Test: Toggle back to light mode** — Switch to dark, then back to light → all elements correct
- **Test: Theme persistence** — Switch to dark, reload page → dark mode persists
- **Test: Contrast ratios in both modes** — Verify key elements meet 4.5:1 contrast ratio in both light and dark mode (axe-core spot check)
- **Test: Theme applies across pages** — Switch to dark on landing page, navigate to workspace → dark mode maintained

**Acceptance criteria:**
- [ ] Theme toggle works in both directions
- [ ] Theme persists across page reloads
- [ ] Theme applies consistently across all pages
- [ ] No critical contrast violations in either mode

### S5: E2E i18n Support (FA-16)
- **Test: Default language (German)** — Fresh page load shows German UI labels
- **Test: Switch to English** — Open user menu → select English → all visible labels change to English
- **Test: Switch back to German** — Switch to English, then back to German → all labels correct
- **Test: Language persistence** — Switch to English, reload page → English persists
- **Test: Language applies across pages** — Switch to English on landing page, navigate to workspace → English maintained
- **Test: All critical labels translated** — Verify key elements (navbar, buttons, headings, form labels) have translations in both languages (spot check, not exhaustive)

**Acceptance criteria:**
- [ ] Language toggle works in both directions
- [ ] Language persists across page reloads
- [ ] Language applies across all pages
- [ ] No untranslated key labels visible

## Execution Rule

**After implementing EACH story above:**
1. Run `npx playwright test --config=e2e/playwright.config.ts`
2. ALL tests must pass (including previously written tests)
3. If any test fails:
   - If test code bug → fix the test
   - If production code bug → fix the production code, document the fix in a comment
4. Only proceed to the next story after all tests are green

## Per-Story Complexity Assessment

| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Auth Bypass Tests | ~5,000 | FA-7 | 1-2 | Low | — |
| 2 | Landing — Lists & Creation | ~6,000 | FA-9, F-9.1, F-9.2 | 1-2 | Low | — |
| 3 | Landing — Search/Filter/Delete | ~6,000 | FA-9, F-9.3, F-9.4 | 1-2 | Low | — |
| 4 | Theme Support | ~4,000 | FA-17 | 1-2 | Low | OS preference detection |
| 5 | i18n Support | ~4,000 | FA-16 | 1-2 | Low | Translation key coverage |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~25,000
- **Cumulative domain size:** Small
- **Information loss risk:** Low (score: 1)
- **Context saturation risk:** Low

## Milestone Acceptance Criteria
- [ ] All 4 dev users tested for auth bypass
- [ ] Landing page CRUD, search, filter, soft delete tested
- [ ] Theme toggle + persistence tested (both modes)
- [ ] i18n toggle + persistence tested (both languages)
- [ ] All E2E tests pass
- [ ] No production code regressions
