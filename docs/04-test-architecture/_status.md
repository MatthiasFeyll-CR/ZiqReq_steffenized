# Test Architecture — Status

## Project
- **Name:** ZiqReq — Requirements Assembly Platform
- **Started:** 2026-03-04
- **Last updated:** 2026-03-05

## Input Consumed
- docs/01-requirements/ (all files — 75 features across 17 feature areas)
- docs/02-architecture/ (all files — tech stack, data model with 22 tables, API design, project structure, testing strategy)
- docs/03-design/ (component-specs.md, page-layouts.md, interactions.md, design-system.md, component-inventory.md)
- docs/03-ai/ (agent-architecture.md with agents, system-prompts.md, tools-and-functions.md, model-config.md, guardrails.md)
- docs/03-integration/ (gap-analysis.md, changes-applied.md, audit-report.md, integration-report.md)
- docs/04-spec-qa/spec-qa-report.md (CONDITIONAL PASS — 27 warnings, 0 critical)

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Test Plan | complete | 2026-03-04 (revised 2026-03-05) |
| 2 | Test Matrix | complete | 2026-03-04 (revised 2026-03-05) |
| 3 | Test Fixtures & Mocks | complete | 2026-03-04 (revised 2026-03-05) |
| 4 | Integration Scenarios | complete | 2026-03-04 (revised 2026-03-05) |
| 5 | Runtime Safety Specs | complete | 2026-03-04 (revised 2026-03-05) |
| 6 | Summary & Handoff | complete | 2026-03-05 |

## Revision Summary (2026-03-05)
- **Test Matrix:** +26 test cases (256 total, up from 230). Updated project terminology, removed board/merge/similarity tests, added requirements panel tests.
- **Integration Scenarios:** +5 scenarios (43 total, up from 38). Updated to reflect requirements assembly workflow, removed board/merge scenarios, added requirements panel interaction scenarios.
- **Runtime Safety:** +5 specifications (46 total, up from 41). Updated project references, removed board agent tests, updated requirements structure tests.
- **Test Fixtures:** Updated factories (ProjectFactory, RequirementItemFactory, etc.), removed board/merge fixtures, added requirements structure fixtures.
- **Test Plan:** Updated to reflect requirements panel instead of board, removed merge/similarity references.

## Handoff
- **Ready:** true
- **Next specialist:** Strategy Planner (`/strategy_planner`)
- **Files produced:**
  - docs/04-test-architecture/test-plan.md
  - docs/04-test-architecture/test-matrix.md
  - docs/04-test-architecture/test-fixtures.md
  - docs/04-test-architecture/integration-scenarios.md
  - docs/04-test-architecture/runtime-safety.md
  - docs/04-test-architecture/handover.json
- **Required input for next specialist:**
  - All files in docs/01-requirements/, docs/02-architecture/, docs/03-design/, docs/03-ai/, docs/04-test-architecture/
- **Briefing for next specialist:**
  - 345 total test specifications: 256 feature/API/entity/UI tests + 43 integration scenarios + 46 runtime safety specs
  - 8 testing layers: Frontend Unit, Frontend E2E, Backend Unit, Backend Integration, gRPC Contract, WebSocket, Cross-Service E2E, AI Agent
  - Test infrastructure (18 factories, 7 mock services, 5 composite scenarios, AI fixture files) should be a foundation milestone item
  - Runtime safety specs (especially AI guardrail tests) should be addressed in the same milestone as AI agent implementation
  - Integration scenarios spanning requirements structuring flow require both Core and AI service milestones
  - E2E test suite requires Docker Compose test profile — should be set up in CI infrastructure milestone
  - Context re-indexing pipeline (TIMEOUT-007) needs testing alongside admin panel implementation
- **Open questions:** none
