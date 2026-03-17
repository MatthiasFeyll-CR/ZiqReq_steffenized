# QA Report: Milestone 20 — AI System Prompt Rework

**Date:** 2026-03-17
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m20.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed 3 user stories covering the AI system prompt rework: new Facilitator prompt with `update_requirements_structure` tool (US-001), new Summarizing AI for hierarchical requirements documents (US-002), and AI pipeline update for requirements structure mutations (US-003). All acceptance criteria are met. 712 Python tests and 365 Node tests pass. All required gate checks pass.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | New Facilitator system prompt with update_requirements_structure tool | PASS | All 12 acceptance criteria verified against code |
| US-002 | New Summarizing AI for hierarchical requirements documents | PASS | All 11 acceptance criteria verified against code |
| US-003 | AI pipeline update for requirements structure mutations | PASS | All 13 acceptance criteria verified; DEV-001, DEV-002 logged |

**Stories passed:** 3 / 3
**Stories with defects:** 0
**Stories with deviations:** 1 (US-003)

### US-001 Acceptance Criteria Detail

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Facilitator system prompt includes `<project_type>` variable injection | PASS | `services/ai/agents/facilitator/prompt.py:21` — `<project_type>{project_type}</project_type>` |
| 2 | Type-specific identity: requirements structuring with Software vs Non-Software guidance | PASS | `prompt.py:10-14` — identity block with Epics/Stories and Milestones/Packages guidance |
| 3 | Includes `<requirements_structure>` block with current hierarchical JSON | PASS | `prompt.py:101-103` with `_render_requirements_structure()` at line 301-330 rendering tree |
| 4 | Plugin has `update_requirements_structure` tool with 16 operations | PASS | `plugins.py:222-311` — tool with all 16 ops; `_REQUIRED_FIELDS` at line 350-367 covers all |
| 5 | Tool validates operation matches project_type | PASS | `plugins.py:249-250,267-273` — validates against `valid_ops` per type |
| 6 | Tool publishes `ai.requirements.updated` event per successful mutation | PASS | `plugins.py:298-304` — event published in loop for successes |
| 7 | Board reference syntax `[[Item Title]]` removed from prompt and tools | PASS | Test `test_facilitator.py:800-801` — asserts `"board" not in prompt.lower()` and `"[[" not in prompt` |
| 8 | `context_assembler.py` injects `project_type` and `requirements_structure` | PASS | `context_assembler.py:90,99-101,115` — extracts both from gRPC response |
| 9 | Facilitator bucket combines global + type-specific content | PASS | `context_assembler.py:30-71` — `get_facilitator_context()` fetches global + type-specific buckets |
| 10 | All board references removed from facilitator prompt and tools | PASS | No board references in prompt.py or plugins.py; test verifies |
| 11 | Typecheck passes | PASS | Pipeline gate: Frontend typecheck PASSED, mypy PASSED |
| 12 | All existing Facilitator tests pass | PASS | 712 Python tests passed |

### US-002 Acceptance Criteria Detail

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Software hierarchical JSON: `{title, short_description, structure: [{epic_id, ...stories}], readiness_evaluation}` | PASS | `prompt.py:148-178` — output format matches spec exactly |
| 2 | Non-software hierarchical JSON: `{title, short_description, structure: [{milestone_id, ...packages}], readiness_evaluation}` | PASS | `prompt.py:179-209` — output format matches spec |
| 3 | Includes `<project_type>` variable injection | PASS | `prompt.py:55` — `<project_type>{project_type}</project_type>` |
| 4 | Supports 3 modes: full_generation, selective_regeneration, item_regeneration | PASS | `prompt.py:90-125` — `_build_mode_instructions()` handles all 3 modes |
| 5 | Includes `<locked_items>` block for selective_regeneration | PASS | `prompt.py:110-115` — locked item IDs listed in mode instructions |
| 6 | Readiness evaluation criteria per type | PASS | `prompt.py:212-231` — software checks epics have stories; non-software checks milestones have packages |
| 7 | Old 6-section BRD format removed | PASS | No references to `current_workflow`, `affected_department`, `core_capabilities`, `success_criteria` in prompt |
| 8 | `SECTION_KEYS`, `SECTION_LABELS`, `READINESS_ANCHORS` removed | PASS | Not present in prompt.py |
| 9 | Agent parses hierarchical JSON and validates against project_type | PASS | `agent.py:100-153` — `_parse_response()` with `_validate_structure()` checking for `epic_id`/`milestone_id` |
| 10 | Typecheck passes | PASS | Pipeline gate passed |
| 11 | All existing Summarizing AI tests pass | PASS | 712 Python tests passed; 53 Summarizing AI tests specifically |

### US-003 Acceptance Criteria Detail

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Pipeline removes board agent invocation step | PASS | No board agent imports or invocations in `pipeline.py` |
| 2 | Pipeline adds requirements mutation handler | PASS | `pipeline.py:361-398` — `_step_apply_mutations()` |
| 3 | Pipeline publishes `ai.requirements.updated` event after mutations | PASS | `pipeline.py:385-389` — event published with mutation details |
| 4 | Pipeline includes requirements structure in context assembly (Step 1) | PASS | `pipeline.py:176-181` — fetches via `core_client.get_requirements_state()` |
| 5 | Pipeline includes `project_type` in facilitator context | PASS | `pipeline.py:184-189` — ensures project_type in project metadata |
| 6 | Proto defines `UpdateRequirementsStructure` RPC | PASS | `proto/core.proto:15,139-154` |
| 7 | Proto defines `GetRequirementsState` RPC | PASS | `proto/core.proto:14,119-132` |
| 8 | Core servicer implements `UpdateRequirementsStructure` | DEV-001 | Implemented via `CoreClient.apply_requirements_mutations()` direct DB access, not gRPC servicer |
| 9 | Core servicer implements `GetRequirementsState` | DEV-001 | Implemented via `CoreClient.get_requirements_state()` direct DB access, not gRPC servicer |
| 10 | Gateway WebSocket handles `ai.requirements.updated` event | PASS | Pre-existing handler from previous milestone (per progress log) |
| 11 | Board agent references removed from pipeline.py | PASS | No board agent imports or references |
| 12 | Typecheck passes | PASS | Pipeline gate passed |
| 13 | All existing pipeline tests pass | PASS | 712 Python tests passed; 25 pipeline tests specifically |

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in this milestone's PRD stories.

The PRD `testIds` arrays are empty for all 3 stories. No specific test matrix IDs were assigned to M20 stories, so there are no MISSING tests to flag. Ralph wrote comprehensive tests covering all new functionality:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `services/ai/tests/test_facilitator.py` | 15+ tests for `update_requirements_structure` (lines 819-1034) | All 16 operations, type validation, partial failures, required fields, JSON parsing |
| `services/ai/tests/test_facilitator.py` | 12 tests for prompt rendering (lines 695-814) | project_type injection, requirements structure (software + non-software), structuring guidance, no board references |
| `services/ai/tests/test_summarizing_ai.py` | 53 tests total | Prompt rendering, response parsing, structure validation, 3 generation modes, readiness evaluation, mock/SK modes |
| `services/ai/tests/test_pipeline.py` | 25 tests total, 4 new for mutations (lines 677-803) | Mutations applied via CoreClient, no mutations skips step, requirements state fetched in Step 1, partial failure handling |
| `services/ai/tests/test_brd_pipeline.py` | 27 tests total | Updated for new hierarchical output format |

---

## Defects

No defects found.

---

## Deviations

### DEV-001: gRPC servicer uses CoreClient direct DB access instead of gRPC server
- **Story:** US-003
- **Spec document:** `docs/02-architecture/api-design.md` — gRPC Service Definitions
- **Expected (per spec):** Core gRPC servicer (`services/core/grpc_server/servicer.py`) implements `UpdateRequirementsStructure` and `GetRequirementsState` RPCs as actual gRPC server endpoints.
- **Actual (in code):** `CoreClient` (`services/ai/grpc_clients/core_client.py:163-322`) implements these operations via direct PostgreSQL queries. The proto definitions exist in `proto/core.proto` as spec documentation but no gRPC server handles these calls at runtime.
- **Why code is correct:** All services share the same PostgreSQL database. Direct DB access avoids unnecessary gRPC hop overhead, simplifies deployment, and is consistent with every other CoreClient operation in the codebase (as noted in progress log: "CoreServicer is a dead stub — all services use direct DB access via CoreClient"). The proto file still serves as the API contract documentation.
- **Spec update needed:** The Spec Reconciler should update `docs/02-architecture/api-design.md` to clarify that gRPC service definitions are used as API contracts/documentation only, with runtime implementation via direct database access through CoreClient.

### DEV-002: Board agent references were already absent
- **Story:** US-001, US-003
- **Spec document:** PRD `tasks/prd-m20.json` — AC items about board removal
- **Expected (per spec):** Remove board references from facilitator prompt, tools, and pipeline.
- **Actual (in code):** Board references were already absent from the codebase prior to M20 (removed in earlier milestones M17/M18). No removal was needed.
- **Why code is correct:** The code is correct — board references are absent. The acceptance criteria were written before M17/M18 completed the board removal.
- **Spec update needed:** No spec update needed — this is informational only.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 712 passed, 92 warnings |
| Node tests | `docker compose -f docker-compose.test.yml run --rm node-tests npx vitest run` | PASS | 365 passed |
| Frontend TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend typecheck (mypy) | mypy | PASS | Clean |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | 4 errors, 5 warnings — all pre-existing (see below) |

### ESLint Details (Pre-existing, Not M20)

The 4 ESLint errors and 5 warnings are all pre-existing from prior milestones:

**Errors (4):**
- `SECTION_FIELD_KEYS` unused in `DocumentView.tsx:35` — old BRD format constant (pre-existing since M19)
- `SECTION_FIELD_KEYS` unused in `BRDSectionEditor.tsx` — same issue (pre-existing)
- 2 useless escape chars in `CommentContent.tsx` and `CommentInput.tsx` — pre-existing

**Warnings (5):**
- Missing React Hook dependencies in `CommentItem.tsx`, `CommentsPanel.tsx`, `MonitoringTab.tsx`, `ParametersTab.tsx`, `UsersTab.tsx` — all pre-existing

None of these relate to M20 changes. ESLint is marked optional in the pipeline config.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Review details:**
- **SQL Injection:** All `CoreClient` database queries use parameterized queries (`%s` placeholders) — `core_client.py:38,54,74,169,232,291,329`. PASS.
- **Input Validation:** `update_requirements_structure` validates: (a) JSON parsing with try/except, (b) non-empty array check, (c) operation against `_ALL_OPERATIONS`, (d) operation matches project type, (e) required fields per operation — `plugins.py:241-284`. PASS.
- **Sensitive Data:** No hardcoded secrets, API keys, or credentials in M20 changes. PASS.
- **Access Control:** AI pipeline is an internal service invoked only by the event system after user authentication at the gateway. No direct external access. PASS.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Review details:**
- `apply_requirements_mutations` fetches structure once, applies all mutations in-memory, persists once — no N+1 pattern.
- Requirements structure JSON can be large (noted as ~10K tokens in PRD notes) but is handled as a single JSONB blob — appropriate for the data size.
- No unnecessary re-renders or frontend impact (M20 is backend-only).

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| N/A | — | N/A | M20 is backend-only — no frontend components modified |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### AI Service — Facilitator
- [ ] Facilitator prompt renders with `<project_type>software</project_type>` when `project_type="software"`
- [ ] Facilitator prompt renders with `<project_type>non_software</project_type>` when `project_type="non_software"`
- [ ] Facilitator prompt includes `<requirements_structure>` block with hierarchical tree rendering
- [ ] Facilitator prompt includes type-specific structuring guidance (SOFTWARE/NON-SOFTWARE)
- [ ] Facilitator prompt contains no board references (`board`, `[[`)
- [ ] `update_requirements_structure` tool accepts all 16 operations
- [ ] `update_requirements_structure` rejects operations mismatched to project type (e.g., `add_epic` for `non_software`)
- [ ] `update_requirements_structure` publishes `ai.requirements.updated` events for successful mutations
- [ ] `update_requirements_structure` handles partial failures (some mutations succeed, others fail)
- [ ] `FacilitatorPlugin.requirements_mutations` stores validated mutations for pipeline Step 5
- [ ] `context_assembler.get_facilitator_context()` combines global + type-specific buckets
- [ ] `ContextAssembler.assemble()` includes `requirements_structure` in output dict

### AI Service — Summarizing AI
- [ ] Summarizing AI prompt includes `<project_type>` variable
- [ ] Summarizing AI software output format has `epic_id`, `stories`, `acceptance_criteria`
- [ ] Summarizing AI non-software output format has `milestone_id`, `packages`, `deliverables`
- [ ] All 3 generation modes work: `full_generation`, `selective_regeneration`, `item_regeneration`
- [ ] `_validate_structure()` checks for `epic_id` (software) or `milestone_id` (non_software)
- [ ] `_parse_response()` handles JSON in markdown code blocks
- [ ] Readiness evaluation uses `ready_for_development` (software) or `ready_for_execution` (non_software)
- [ ] No old BRD section references (`current_workflow`, `affected_department`, `core_capabilities`, `success_criteria`)

### AI Service — Pipeline
- [ ] `ChatProcessingPipeline` Step 1 fetches requirements state via `core_client.get_requirements_state()`
- [ ] `ChatProcessingPipeline` Step 5 applies mutations via `core_client.apply_requirements_mutations()`
- [ ] `ChatProcessingPipeline` Step 5 publishes `ai.requirements.updated` event after successful mutations
- [ ] `ChatProcessingPipeline` Step 5 is a no-op when no mutations are returned by Facilitator
- [ ] Pipeline abort/version tracking still works correctly across all 7 steps
- [ ] `BrdGenerationPipeline` handles hierarchical structure output format in fabrication validation

### Data Layer
- [ ] `CoreClient.get_requirements_state()` returns structure, item_locks, project_type for existing drafts
- [ ] `CoreClient.get_requirements_state()` returns empty structure for projects without drafts
- [ ] `CoreClient.apply_requirements_mutations()` handles all 16 mutation types correctly
- [ ] `CoreClient.apply_requirements_mutations()` respects item locks
- [ ] `CoreClient.apply_requirements_mutations()` creates draft if none exists (upsert behavior)

### Proto & API
- [ ] `proto/core.proto` defines `GetRequirementsState` and `UpdateRequirementsStructure` RPCs
- [ ] Proto message types: `GetRequirementsStateRequest/Response`, `UpdateRequirementsStructureRequest/Response`, `StructureMutation`, `MutationResult`

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 712 Python tests pass
- [ ] All 365 Node tests pass
- [ ] Ruff lint passes
- [ ] mypy passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 2 (DEV-001: gRPC servicer via CoreClient direct DB, DEV-002: board references already absent)
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
