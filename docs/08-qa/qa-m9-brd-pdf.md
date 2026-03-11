# QA Report: Milestone 9 — BRD & PDF Generation

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m9.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed Milestone 9 (BRD & PDF Generation) covering 9 user stories: Summarizing AI agent with 3 generation modes, BRD generation pipeline with fabrication validation, BRD Draft REST API, PDF generation service with WeasyPrint, BRD generation trigger endpoint, Review Tab UI, BRD Section Editor, Readiness Evaluation, and Information Gaps toggle. All 9 stories pass acceptance criteria verification. All 495 backend tests and 308 frontend tests pass. All 44 test matrix IDs found. Zero defects identified.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Summarizing AI Agent — 3 Generation Modes | PASS | SummarizingAIAgent extends BaseAgent, 3 modes implemented, temp 0.3, fabrication rule in prompt, /TODO markers, readiness evaluation, mock mode |
| US-002 | BRD Generation Pipeline — Context Assembly & Fabrication Validation | PASS | BrdGenerationPipeline with version tracking/abort, FabricationValidator (heuristic, no AI), event publishing, error handling |
| US-003 | BRD Draft REST API — GET/PATCH | PASS | GET with get_or_create, PATCH with auto-lock on edit, section_locks, allow_information_gaps toggle, access control, mirror model |
| US-004 | PDF Generation Service — WeasyPrint gRPC | PASS | PdfServicer with GeneratePdf, HTML builder with html.escape, /TODO marker validation, A4 portrait CSS, stateless |
| US-005 | BRD Generation Trigger — REST POST | PASS | POST /generate returns 202, gRPC to AI service, idea state validation, mode/section_name validation, 503 on failure |
| US-006 | Review Tab UI — PDF Preview & Action Bar | PASS | Review tab with TanStack Query, WebSocket cache invalidation, empty/loading/error states, Download + Generate + Edit buttons |
| US-007 | BRD Section Editor — Expandable Edit Area | PASS | Slide-in editor with framer-motion, 6 sections with lock/regenerate icons, auto-save on blur, debounced onChange 300ms, auto-lock on edit |
| US-008 | Readiness Evaluation — Progress Indicator | PASS | Segmented progress bar (6 segments, h-2, gap-0.5=2px), green/gray, label "X/6 sections ready", shadcn Tooltip on hover, per-section status dots |
| US-009 | Allow Information Gaps — Toggle Switch & /TODO Handling | PASS | Switch toggle, /TODO frontend validation dialog, PDF service /TODO rejection, progress indicator "Gaps allowed" label |

**Stories passed:** 9 / 9
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 44 found / 0 missing out of 44 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-1.2.01 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Review section hidden for never-submitted idea |
| T-1.2.02 | FOUND | `frontend/src/__tests__/section-visibility.test.tsx` | Review section visible after first submission |
| T-4.1.01 | FOUND | `services/ai/tests/test_summarizing_ai.py` | Agent supports all 3 generation modes |
| T-4.1.02 | FOUND | `services/ai/tests/test_summarizing_ai.py` | All 6 sections generated |
| T-4.1.03 | FOUND | `services/ai/tests/test_brd_pipeline.py` | Context assembly loads all required fields |
| T-4.2.01 | FOUND | `services/ai/tests/test_summarizing_ai.py` | Insufficient sections show 'Not enough information' |
| T-4.2.02 | FOUND | `services/ai/tests/test_summarizing_ai.py` | No fabrication when gaps disallowed |
| T-4.2.03 | FOUND | `services/ai/tests/test_brd_pipeline.py` | Fabrication validation flags suspicious sections |
| T-4.3.01 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | POST triggers AI generation |
| T-4.3.02 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | ai.brd.ready event persists to DB |
| T-4.4.01 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | Section edit auto-locks that section |
| T-4.4.02 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | Lock toggle works |
| T-4.4.03 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | Unlocked sections regenerate, locked preserved |
| T-4.4.04 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Lock toggle updates section_locks |
| T-4.4.05 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Regenerate triggers section_regeneration |
| T-4.4.06 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Auto-save on blur |
| T-4.5.01 | FOUND | `frontend/src/__tests__/review-tab.test.tsx` | PDF preview renders |
| T-4.5.02 | FOUND | `frontend/src/__tests__/review-tab.test.tsx` | Action bar visible |
| T-4.5.03 | FOUND | `frontend/src/__tests__/review-tab.test.tsx` | Download button works |
| T-4.7.01 | FOUND | `services/pdf/tests/test_pdf_service.py` | PDF generated from BRD content |
| T-4.7.02 | FOUND | `services/pdf/tests/test_pdf_service.py` | PDF includes all 6 sections |
| T-4.8.01 | FOUND | `services/ai/tests/test_summarizing_ai.py` | Readiness evaluation included in output |
| T-4.8.02 | FOUND | `frontend/src/__tests__/readiness-evaluation.test.tsx` | Progress indicator updates |
| T-4.8.03 | FOUND | `frontend/src/__tests__/readiness-evaluation.test.tsx` | Progress bar reflects readiness |
| T-4.8.04 | FOUND | `frontend/src/__tests__/readiness-evaluation.test.tsx` | Label updates on readiness change |
| T-4.9.01 | FOUND | `services/ai/tests/test_summarizing_ai.py` | /TODO markers when gaps allowed |
| T-4.9.02 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | Gaps toggle persists |
| T-4.9.03 | FOUND | `frontend/src/__tests__/information-gaps-toggle.test.tsx` | Gaps toggle works |
| T-4.9.04 | FOUND | `services/ai/tests/test_summarizing_ai.py` | Gaps toggle ON produces /TODO markers |
| T-4.9.05 | FOUND | `services/ai/tests/test_summarizing_ai.py` | Gaps toggle OFF produces 'Not enough information' |
| T-4.9.06 | FOUND | `services/pdf/tests/test_pdf_service.py` | PDF generation rejected if /TODO remains |
| UI-4.01 | FOUND | `frontend/src/__tests__/review-tab.test.tsx` | Review tab appears in workspace |
| UI-4.02 | FOUND | `frontend/src/__tests__/review-tab.test.tsx` | PDF preview shows generated BRD |
| UI-4.03 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Editor slides in |
| UI-4.04 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Section edit auto-locks |
| UI-4.05 | FOUND | `frontend/src/__tests__/brd-section-editor.test.tsx` | Regenerate icon triggers generation |
| UI-4.06 | FOUND | `frontend/src/__tests__/readiness-evaluation.test.tsx` | Progress indicator visible in editor |
| UI-4.07 | FOUND | `frontend/src/__tests__/information-gaps-toggle.test.tsx` | Gaps toggle visible in editor |
| API-4.01 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | GET returns all BRD fields |
| API-4.02 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | PATCH updates sections |
| API-4.03 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | Auto-lock on edit |
| API-4.04 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | 403 if not collaborator |
| API-4.05 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | POST /generate returns 202 |
| API-4.06 | FOUND | `services/gateway/apps/brd/tests/test_views.py` | gRPC call to AI service succeeds |

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
| Backend Tests | `pytest` (Docker) | PASS | 495 passed, 0 failed in 22.97s |
| Frontend Tests | `npx vitest run` | PASS | 308 passed, 0 failed |
| Frontend TypeScript | `npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | SKIP (optional) | Pre-existing: duplicate module "events" between services/core and services/ai |
| Frontend Lint (ESLint) | `npx eslint src/` | SKIP (optional) | 1 M9 issue: `SECTION_FIELD_KEYS` in BRDSectionEditor.tsx only used as type; 3 pre-existing issues |

### ESLint Detail (optional, non-blocking)

The M9-introduced ESLint error in `frontend/src/components/brd/BRDSectionEditor.tsx:13` — `SECTION_FIELD_KEYS` is defined as a `const` array but only used via `typeof` for type derivation. This is a minor code quality issue (could be replaced with an inline type), not a functional defect. The 3 other ESLint issues (ai-modified-indicator.test.tsx, board-interactions.test.tsx, FreeTextNode.tsx) are pre-existing from earlier milestones.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | XSS Prevention | N/A (positive) | `services/pdf/generator/builder.py` | All user content passed through `html.escape()` before HTML rendering — title, sections, dates. Correct. | — |
| — | Authentication | N/A (positive) | `services/gateway/apps/brd/views.py` | All endpoints use `@authentication_classes([MiddlewareAuthentication])` with `_require_auth()` check. Returns 401 for unauthenticated. | — |
| — | Authorization | N/A (positive) | `services/gateway/apps/brd/views.py` | `_check_access()` verifies user is owner, co-owner, or collaborator. Returns 403 for unauthorized users. | — |
| — | Input Validation | N/A (positive) | `services/gateway/apps/brd/serializers.py` | `BrdGenerateSerializer` validates mode (3 choices) and section_name (6 valid values). `BrdDraftPatchSerializer` validates field types. | — |
| — | Injection | N/A (positive) | `services/gateway/apps/brd/views.py:48` | idea_id validated as UUID before database query. Django ORM uses parameterized queries. | — |
| — | Sensitive Data | N/A (positive) | `frontend/src/api/brd.ts` | API calls use `credentials: "include"` (cookie-based auth). No API keys in client code. | — |
| — | Fabrication Guard | N/A (positive) | `services/ai/processing/fabrication_validator.py` | Lightweight heuristic (no AI invocation) flags ungrounded claims. Non-blocking warning. | — |

No security defects found. All OWASP basics are properly handled.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Fuzzy Matching | Minor | `services/ai/processing/fabrication_validator.py:161-164` | `_is_grounded()` iterates over all source_words with `SequenceMatcher` per keyword. For large brainstorming sessions this is O(keywords * source_words). | Acceptable for M9 scope — keyword count is bounded by 6 short BRD sections. Monitor if sessions grow very large. |
| PERF-002 | Re-render | Info | `frontend/src/components/brd/BRDSectionEditor.tsx:100` | `patchMutation` in `useCallback` dependency array — mutation object identity changes could cause re-creation. | Minor — React Query mutation objects are stable. No action needed. |

No critical or major performance issues. All findings are informational/minor.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| Review Tab | `docs/03-design/component-specs.md` S12.1 | PASS | bg-white preview container, border, rounded, shadow, action bar below |
| BRD Section Editor | `docs/03-design/component-specs.md` S12.2 | PASS | Slide-in from right (framer-motion), 6 sections with label + textarea + lock + regenerate, close button |
| Progress Indicator | `docs/03-design/component-specs.md` S12.3 | PASS | h-2 rounded-full segments, gap-0.5 (2px), green/gray, "X/6 sections ready" label, Tooltip on hover |
| Section Fields | `docs/03-design/component-specs.md` S12.2 | PASS | Auto-grow textarea, text-base, border, rounded, bg-card, Lock/LockOpen icons, RefreshCw regenerate |
| Switch Toggle | `docs/03-design/component-specs.md` S4.4 | PASS | shadcn Switch component for allow_information_gaps |
| Empty State | `docs/03-design/component-specs.md` | PASS | EmptyState component with FileText icon |
| PDF Template | Architecture spec | PASS | A4 portrait, Commerz Real branding, section headers, semantic HTML |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Review tab renders in workspace right panel at `/ideas/:id`
- [ ] Review tab visibility: shown when idea.state is 'open' (Review tab always visible in M9)
- [ ] Board tab still renders correctly alongside Review tab

### API Endpoints
- [ ] GET /api/ideas/:id/brd returns BRD draft with all 6 sections + section_locks + allow_information_gaps + readiness_evaluation + last_evaluated_at
- [ ] GET /api/ideas/:id/brd creates empty draft if none exists (get_or_create)
- [ ] PATCH /api/ideas/:id/brd updates sections, toggles locks, toggles allow_information_gaps
- [ ] PATCH /api/ideas/:id/brd auto-locks section on edit
- [ ] POST /api/ideas/:id/brd/generate returns 202 for valid mode
- [ ] POST /api/ideas/:id/brd/generate returns 400 for non-open idea state
- [ ] POST /api/ideas/:id/brd/generate returns 403 for unauthorized user
- [ ] POST /api/ideas/:id/brd/generate returns 503 when AI service unavailable

### AI Service
- [ ] SummarizingAIAgent supports 3 modes: full_generation, selective_regeneration, section_regeneration
- [ ] SummarizingAIAgent uses temperature 0.3 and default model tier
- [ ] BrdGenerationPipeline assembles context (chat_summary, recent_messages, board_state, locked_sections, allow_information_gaps)
- [ ] FabricationValidator detects ungrounded claims via keyword extraction + fuzzy matching
- [ ] ai.brd.generated event published with idea_id, mode, sections, readiness_evaluation, fabrication_flags

### PDF Service
- [ ] PdfServicer.GeneratePdf renders PDF from 6 sections via WeasyPrint
- [ ] PDF generation rejects content with /TODO markers (TodoMarkerError)
- [ ] HTML builder escapes all user content via html.escape()

### Data Integrity
- [ ] brd_drafts table: id, idea_id (UNIQUE), 6 section fields, section_locks (JSONB), allow_information_gaps (boolean), readiness_evaluation (JSONB), last_evaluated_at
- [ ] BrdDraft mirror model (managed=False, db_table='brd_drafts') in Gateway

### Features
- [ ] BRD Section Editor slides in from right with framer-motion animation
- [ ] Section lock toggle updates section_locks and UI immediately (optimistic)
- [ ] Regenerate icon (RefreshCw) triggers section_regeneration for unlocked sections
- [ ] Auto-save: debounced 300ms on change, immediate on blur
- [ ] Auto-lock on edit: typing in section textarea auto-locks that section
- [ ] Progress indicator shows 6 segments (green=ready, gray=insufficient)
- [ ] Allow Information Gaps toggle: ON shows "Gaps allowed", all segments gray
- [ ] /TODO warning dialog shown before PDF download when markers present
- [ ] WebSocket brd_ready event invalidates TanStack Query cache

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 495 backend tests pass
- [ ] All 308 frontend tests pass
- [ ] Ruff lint clean
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
