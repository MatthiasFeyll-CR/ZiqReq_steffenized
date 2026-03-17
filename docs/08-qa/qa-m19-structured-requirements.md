# QA Report: Milestone 19 — Structured Requirements

**Date:** 2026-03-17
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1
**PRD:** tasks/prd-m19.json
**Progress:** .ralph/progress.txt

---

## Summary

Bugfix cycle 1 review of M19 (3 bugfix stories: BF-001, BF-002, BF-003). All 3 defects from the initial review have been resolved. Tests went from 666 passed / 3 failed (cycle 0) to 669 passed / 0 failed. DEF-003 was confirmed as a false positive — the imports are actively used. All gate checks pass. **Verdict: PASS.**

---

## Bugfix Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| BF-001 | Fix: Pre-existing tests broken by required project_type field | PASS | `test_visibility.py:43` now sends `project_type`; `test_views.py:53` now sends `project_type` alongside `first_message`. Both tests pass. |
| BF-002 | Fix: Context agent test assertion missing project_type parameter | PASS | `test_context_agent.py:159-162` now asserts `project_type=None`. Test passes. |
| BF-003 | Fix: Unused imports in ai-context-tab test | PASS | Confirmed false positive — `vi`, `screen`, and `userEvent` are all used in the file. ESLint reports 0 errors on this file. No code changes needed. |

**Stories passed:** 3 / 3
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Original Story Verification (carried forward from cycle 0)

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Project type selection at creation | PASS | DEF-001 fixed in BF-001 |
| US-002 | Structured requirements data model | PASS | No defects in cycle 0 |
| US-003 | Structured requirements panel UI | PASS | No defects in cycle 0 |
| US-004 | Admin context buckets per project type | PASS | DEF-002 fixed in BF-002; DEF-003 was false positive |

**Stories passed:** 4 / 4

---

## Test Matrix Coverage

**Pipeline scan results:** 14 found / 0 missing out of 14 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-3.1.01 | FOUND | `frontend/src/components/landing/__tests__/NewProjectModal.test.tsx` | Verified |
| T-3.1.02 | FOUND | `frontend/src/components/landing/__tests__/NewProjectModal.test.tsx` | Verified |
| T-3.1.03 | FOUND | `frontend/src/components/landing/__tests__/NewProjectModal.test.tsx` | Verified |
| T-3.2.01 | FOUND | `services/core/apps/projects/tests/test_requirements_models.py` | Verified |
| T-3.2.02 | FOUND | `services/core/apps/projects/tests/test_requirements_models.py` | Verified |
| T-3.2.03 | FOUND | `services/core/apps/projects/tests/test_requirements_models.py` | Verified |
| T-3.3.01 | FOUND | `frontend/src/components/workspace/__tests__/RequirementsPanel.test.tsx` | Verified |
| T-3.3.02 | FOUND | `frontend/src/components/workspace/__tests__/RequirementsPanel.test.tsx` | Verified |
| T-3.3.03 | FOUND | `frontend/src/components/workspace/__tests__/RequirementsPanel.test.tsx` | Verified |
| T-3.4.01 | FOUND | `services/ai/tests/test_context_buckets.py` | Verified |
| T-3.4.02 | FOUND | `services/ai/tests/test_context_buckets.py` | Verified |
| API-3.01 | FOUND | `services/gateway/apps/projects/tests/test_requirements_views.py` | Verified |
| API-3.02 | FOUND | `services/gateway/apps/projects/tests/test_requirements_views.py` | Verified |
| API-3.03 | FOUND | `services/ai/tests/test_context_retrieval.py` | Verified |

---

## Defects

All 3 defects from cycle 0 have been resolved:

- **DEF-001** (Major): Fixed in BF-001 — tests now include `project_type` in POST payloads
- **DEF-002** (Major): Fixed in BF-002 — assertion now expects `project_type=None`
- **DEF-003** (Minor): False positive — imports are actively used; no fix needed

No new defects found in bugfix cycle 1.

---

## Deviations

None identified.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| TypeScript | `npx tsc --noEmit` | PASS | Clean |
| Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Mypy | `mypy` | PASS | Clean |
| Tests (Python) | `pytest` | PASS | 669 passed, 0 failed (was 666/3 in cycle 0) |
| Tests (Node) | `npx vitest run` | PASS | All passed |
| Lint (ESLint) | `npx eslint src/` | FAIL (optional) | 4 errors (all pre-existing), 5 warnings (pre-existing). Zero M19-related errors. |

### Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | |
| Backend lint (Ruff) | PASSED | |
| Backend typecheck (mypy) | PASSED | |
| Frontend lint (ESLint) | FAILED (optional) | Pre-existing: `SECTION_FIELD_KEYS` in BRDSectionEditor.tsx + DocumentView.tsx, useless escapes in CommentContent.tsx + CommentInput.tsx. None from M19. |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

No new security concerns. Carried forward from cycle 0: `ChoiceField` validates `project_type`, JSONB validated server-side, no raw SQL, no `dangerouslySetInnerHTML`, no hardcoded secrets.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

No N+1 queries, missing indexes, or re-render issues in M19 changes.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| NewProjectModal | `docs/03-design/component-specs.md` § Modal/Dialog | PASS | Two cards, disabled create button |
| RequirementsPanel | `docs/03-design/component-specs.md` § Requirements Panel | PASS | Accordion, drag-and-drop, inline edit |
| WorkspaceLayout | `docs/03-design/page-layouts.md` § Project Workspace | PASS | 40/60 split with draggable divider |
| AIContextTab | `docs/03-design/component-specs.md` § Tabs | PASS | Segmented control for context types |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] NewProjectModal opens from HeroSection and creates projects at POST `/api/projects/` with `project_type`
- [ ] ProjectWorkspace loads with 40/60 chat/requirements split layout
- [ ] RequirementsPanel renders accordion with epics/milestones based on project type
- [ ] AIContextTab renders segmented control for global/software/non_software context types

### API Endpoints
- [ ] POST `/api/projects/` requires `project_type` field (returns 400 without it)
- [ ] POST `/api/projects/` accepts both `"software"` and `"non_software"` types
- [ ] GET `/api/projects/{id}/requirements/draft/` returns current requirements draft
- [ ] PUT `/api/projects/{id}/requirements/draft/structure/` updates draft structure
- [ ] POST `/api/projects/{id}/requirements/versions/` creates a version snapshot
- [ ] GET/PATCH `/api/admin/ai-context/facilitator/` supports `context_type` parameter
- [ ] GET/PATCH `/api/admin/ai-context/company/` supports `context_type` parameter

### Data Integrity
- [ ] `RequirementsDocumentDraft` table exists with `project_id`, `structure` (JSONB), `updated_at` columns
- [ ] `RequirementsDocumentVersion` table exists with `draft_id`, `version_number`, `snapshot` columns
- [ ] `FacilitatorContextBucket.context_type` field exists with choices: global, software, non_software
- [ ] `ContextChunk.context_type` field exists

### Features
- [ ] Drag-and-drop reordering of requirements items within RequirementsPanel
- [ ] WebSocket events `requirements_updated`, `requirements_generating`, `requirements_ready` fire correctly
- [ ] Context agent retriever passes `project_type` parameter to filter chunks
- [ ] Admin AI context tab allows managing buckets per context type (global, software, non_software)

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 669 Python tests pass
- [ ] All Node tests pass
- [ ] Ruff lint clean
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (all 3 from cycle 0 resolved)
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1 (final)

### Cycle Timeline
| Cycle | Tests | Defects | Verdict |
|-------|-------|---------|---------|
| 0 (initial) | 666 passed, 3 failed | 3 (DEF-001, DEF-002, DEF-003) | FAIL |
| 1 (bugfix) | 669 passed, 0 failed | 0 (DEF-003 was false positive) | PASS |
