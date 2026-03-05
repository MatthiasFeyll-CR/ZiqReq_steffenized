# Test Architecture — Status

## Project
- **Name:** ZiqReq — AI-Powered Brainstorming Platform
- **Started:** 2026-03-04
- **Last updated:** 2026-03-05

## Input Consumed
- docs/01-requirements/ (all files — 75 features across 17 feature areas)
- docs/02-architecture/ (all files — tech stack, data model with 22 tables, API design, project structure, testing strategy)
- docs/03-design/ (component-specs.md, page-layouts.md, interactions.md, design-system.md, component-inventory.md)
- docs/03-ai/ (agent-architecture.md with 9 agents, system-prompts.md, tools-and-functions.md, model-config.md, guardrails.md)
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
- **Test Matrix:** +26 test cases (256 total, up from 230). Added F-2.2, F-3.8, F-4.12, F-5.8, F-6.6, F-11.5, F-13.3, input validation edge cases.
- **Integration Scenarios:** +5 scenarios (43 total, up from 38). Added read-only link, context re-indexing, collaborator removal, manual merge, recursive merge.
- **Runtime Safety:** +5 specifications (46 total, up from 41). Added soft delete cleanup, context re-indexing timeout, Celery memory leak, recursive merge integrity, monitoring alert singleton.
- **Test Fixtures:** +1 factory (MonitoringAlertConfigFactory), +1 composite scenario (CollaborationFlow), fixed resubmission trait version links.
- **Test Plan:** Added visual regression strategy, WebSocket coverage depth note.

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
  - Test infrastructure (18 factories, 7 mock services, 5 composite scenarios, 8 AI fixture files) should be a foundation milestone item
  - Runtime safety specs (especially AI guardrail tests) should be addressed in the same milestone as AI agent implementation
  - Integration scenarios spanning similarity detection → merge flow require both Core and AI service milestones
  - Recursive merge integrity (INTEGRITY-009) is a high-risk area requiring careful milestone scoping
  - E2E test suite requires Docker Compose test profile — should be set up in CI infrastructure milestone
  - Context re-indexing pipeline (TIMEOUT-007) needs testing alongside admin panel implementation
- **Open questions:** none
