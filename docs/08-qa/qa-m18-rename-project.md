# QA Report: Milestone 18 — Rename Idea to Project

**Date:** 2026-03-17
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1
**PRD:** tasks/prd-m18.json
**Progress:** .ralph/progress.txt

---

## Summary

Milestone 18 renames the core "Idea" entity to "Project" across the entire codebase — database, backend models, API routes, frontend code, and all user-facing text. The initial review found 1 defect (DEF-001: process step labels and user-facing strings still displayed old terminology). Bugfix cycle 1 successfully resolved DEF-001 — all translation keys are now present in both locale files, all fallback strings use correct "project"/"Define"/"Structure" terminology, and grep checks confirm zero remaining "your idea" or "brainstorming" hits in frontend source. **Verdict: PASS** — all 4 original stories plus the bugfix story are verified.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | [Backend] Rename database tables and models from Idea to Project | PASS | All tables renamed, FK columns renamed, project_type column added with CHECK constraint, models/proto/gRPC updated, WebSocket consumer renamed |
| US-002 | [Backend] Rename API routes from /api/ideas to /api/projects | PASS | All URL patterns, view parameters, error messages correctly use "project". Zero "idea" hits in gateway apps (excl. migrations) |
| US-003 | [Frontend] Rename all idea references to project | PASS | 109 files renamed/updated. Types, components, hooks, routes, query keys, Redux slices all correctly use "project" |
| US-004 | [Both] Rename terminology and translations from brainstorming to requirements assembly | PASS | All translation keys present, fallback strings updated, AI prompts use "project"/"requirements" language |
| BF-001 | Fix: Process step labels and user-facing strings still display old terminology | PASS | All 13 acceptance criteria verified (see details below) |

**Stories passed:** 5 / 5
**Stories with defects:** 0
**Stories with deviations:** 1

### BF-001 Acceptance Criteria Verification

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | en.json: process section with correct keys | PASS | `en.json:359-372` — all keys present: brainstorm="Define", brainstormDesc, document="Structure", documentDesc, review, reviewDesc, stepper, brainstormDoneHint, documentGate, reviewGate, continueToDocument, documentGuide |
| 2 | de.json: equivalent process section in German | PASS | `de.json:359-372` — all keys present: Definieren, Strukturieren, Uberprufung, etc. |
| 3 | en.json: review.rejectedHint and review.backToBrainstorm | PASS | `en.json:228-229` — rejectedHint="Your project was rejected...", backToBrainstorm="Back to Define" |
| 4 | de.json: equivalent review keys in German | PASS | `de.json:228-229` — "Ihr Projekt wurde abgelehnt...", "Zuruck zum Definieren" |
| 5 | en.json: submit.readyDescription | PASS | `en.json:357` — "Once submitted, your project will be sent to reviewers for evaluation." |
| 6 | de.json: equivalent submit.readyDescription | PASS | `de.json:357` — "Nach dem Einreichen wird Ihr Projekt zur Bewertung an die Prufer gesendet." |
| 7 | ProcessStepper.tsx fallback strings updated | PASS | `ProcessStepper.tsx:37-47` — "Define", "Structure", "Chat with AI to define your project" |
| 8 | ProjectWorkspace ~256: t() call with correct terminology | PASS | `ProjectWorkspace/index.tsx:254-257` — uses `t("process.documentGate", "Send at least one message in the chat...")` |
| 9 | ProjectWorkspace ~260: "Submit your project for review first." | PASS | `ProjectWorkspace/index.tsx:258-261` — uses `t("process.reviewGate", "Submit your project for review first.")` |
| 10 | All user-facing strings use "project" not "idea" | PASS | Verified across ProcessStepper, ProjectWorkspace, DocumentView, ChatMessageList |
| 11 | grep "your idea" returns zero hits (excl. __tests__) | PASS | Only hits in `__tests__/websocket-notifications.test.tsx:99,104` (excluded) |
| 12 | grep "brainstorming" returns zero hits (excl. comments/__tests__) | PASS | Zero hits in `.tsx` files |
| 13 | Typecheck passes | PASS | Frontend typecheck gate: PASSED |

---

## Test Matrix Coverage

**No test matrix IDs were referenced in this milestone's PRD stories.** This milestone is a scaffolding/rename milestone with `testIds: []` for all stories — the test matrix does not define specific test IDs for pure rename operations.

All 614 existing Python tests pass, confirming the rename did not introduce regressions.

---

## Defects

**No defects found.** DEF-001 from the initial review has been resolved by bugfix cycle 1.

---

## Deviations

### DEV-001: Internal code identifiers still use "brainstorm"/"document" as process step names

- **Story:** US-004
- **Spec document:** docs/05-milestones/milestone-18.md § Process steps renamed: Define, Structure, Review
- **Expected (per spec):** Process steps renamed
- **Actual (in code):** `type ProcessStep = "brainstorm" | "document" | "review"` in ProcessStepper.tsx. These internal identifiers are used in URL query params (`?step=brainstorm`), `data-testid` attributes, component state, and 40+ references across the codebase.
- **Why code is correct:** Renaming internal identifiers (not user-facing labels) would require updating URL query params, all test assertions, data-testid attributes, and potentially breaking bookmarks/links. The spec says "labels" should be renamed, not internal state identifiers. The user-visible labels are correct via translation keys while internal IDs remain as-is.
- **Spec update needed:** Spec Reconciler should clarify that internal step identifiers remain "brainstorm"/"document"/"review" while user-facing labels are "Define"/"Structure"/"Review".

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 614 passed, 0 failed |
| TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Zero errors |
| Backend lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend typecheck (mypy) | mypy via pytest | PASS | Clean |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | 4 errors, 6 warnings — all pre-existing, not introduced by M18 |

### ESLint Details (pre-existing, non-blocking)

The ESLint failures are identical to the initial review — all pre-existing, none introduced by M18:

**Errors (4):**
- `DocumentView.tsx:35` — `SECTION_FIELD_KEYS` assigned but only used as a type (`@typescript-eslint/no-unused-vars`)
- `CommentsPanel.tsx:153` — missing dependency `shareToken` in useEffect (`react-hooks/exhaustive-deps`) — reported as warning in gate output but counted as part of the 10 problems

**Warnings (6):**
- `AIContextTab.tsx:37`, `MonitoringTab.tsx:37`, `ParametersTab.tsx:19`, `UsersTab.tsx:21` — missing dependency `t` in useEffect
- `CommentsPanel.tsx:153` — missing dependency `shareToken` in useEffect

ESLint is marked as an optional gate check in pipeline-config.json.

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | Zero errors |
| Backend lint (Ruff) | PASSED | Clean |
| Backend typecheck (mypy) | PASSED | Clean |
| Frontend lint (ESLint) | FAILED (optional) | 4 errors, 6 warnings — all pre-existing |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Notes:** Unchanged from initial review. This milestone is a pure rename — no new attack surface, no new user inputs, no new endpoints. Migration uses parameterized `RunSQL`, no hardcoded secrets, no `dangerouslySetInnerHTML`, CHECK constraint enforces project_type at DB level.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Notes:** Pure rename/refactor — no new queries, components, or data flows. The `idx_projects_type` index was added on the new `project_type` column, correct for future query patterns.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| ProjectCard (renamed) | `docs/03-design/component-specs.md` | PASS | Component correctly renamed from IdeaCard to ProjectCard |
| ProjectWorkspace (renamed) | `docs/03-design/page-layouts.md` | PASS | Page correctly renamed from IdeaWorkspace to ProjectWorkspace |
| ProcessStepper | `docs/03-design/component-specs.md` | PASS | Labels now show "Define"/"Structure"/"Review" per spec (fixed in BF-001) |
| Landing Page | `docs/03-design/page-layouts.md` | PASS | All "idea" references updated to "project" in translations |

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### Database & Backend
- [ ] `projects` table exists with columns: id, title, description, state, project_type, owner_id, created_at, updated_at
- [ ] `project_collaborators` table exists with project_id FK to projects
- [ ] `chat_messages.project_id`, `brd_drafts.project_id`, `brd_versions.project_id`, `review_assignments.project_id`, `review_timeline_entries.project_id` columns exist
- [ ] `project_type` column has CHECK constraint allowing only 'software' and 'non_software'
- [ ] `idx_projects_type` index exists on projects.project_type
- [ ] All API routes use `/api/projects/` prefix (zero hits for `/api/ideas/` in gateway urls.py excl. migrations)
- [ ] gRPC proto files use `Project` message type (not `Idea`)

### Frontend Routes & Components
- [ ] Route `/project/:id` loads ProjectWorkspace correctly
- [ ] ProjectCard renders on landing page with project data
- [ ] ProcessStepper displays labels "Define" / "Structure" / "Review" (not "Brainstorm" / "Document")
- [ ] ChatMessageList empty state shows "Start defining your requirements..." (not "Start brainstorming...")
- [ ] DocumentView submit area shows "your project" (not "your idea")
- [ ] Review rejected hint shows "Your project was rejected..." (not "Your idea...")
- [ ] "Back to Define" button on rejected review (not "Back to Brainstorm")

### Translations
- [ ] `en.json` contains `process.*` keys (brainstorm="Define", document="Structure", review="Review", stepper, brainstormDesc, documentDesc, reviewDesc, brainstormDoneHint, documentGate, reviewGate, continueToDocument, documentGuide)
- [ ] `de.json` contains equivalent `process.*` keys in German
- [ ] `en.json` contains `review.rejectedHint` and `review.backToBrainstorm`
- [ ] `en.json` contains `submit.readyDescription`
- [ ] Zero hits for "your idea" in `frontend/src/**/*.tsx` (excluding `__tests__/`)
- [ ] Zero hits for "brainstorming" in `frontend/src/**/*.tsx` (excluding `__tests__/`)

### AI Prompts
- [ ] Facilitator prompt uses "project"/"requirements" language (not "idea"/"brainstorming")
- [ ] Summarizing AI prompt uses "project requirements" language

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 614 Python tests pass
- [ ] Ruff lint passes with zero errors
- [ ] mypy typecheck passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (DEF-001 from initial review resolved)
- **Deviations found:** 1 (DEV-001 — internal step identifiers, logged for Spec Reconciler)
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1 (completed)
