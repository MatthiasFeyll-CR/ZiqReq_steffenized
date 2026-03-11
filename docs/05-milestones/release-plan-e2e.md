# Release Plan — E2E Test Milestones (M17–M21)

## Purpose

These milestones add comprehensive end-to-end test coverage to the already-implemented ZiqReq application. They do NOT modify production code — they only add test infrastructure, helpers, fixtures, and Playwright test specs. Bug fixes discovered during E2E testing ARE expected and required.

## Milestone Execution Order

### M17: E2E Test Infrastructure & Foundation Tests
- **Purpose:** Set up Playwright, docker-compose for E2E, seed scripts, page object models, auth bypass tests, landing page tests, theme & i18n tests
- **Dependencies:** M1–M16 (all implementation milestones complete)

### M18: E2E Workspace, Chat & Board Tests
- **Purpose:** Test the core idea workspace — layout, chat, AI facilitation (mocked), digital board, real-time/WebSocket, idle state
- **Dependencies:** M17

### M19: E2E BRD, Review & Collaboration Tests
- **Purpose:** Test BRD generation, PDF, review workflow, collaboration/sharing, notifications, user preferences
- **Dependencies:** M18

### M20: E2E Similarity, Merge & Admin Tests
- **Purpose:** Test similarity detection, merge flows, append, manual merge, admin panel, monitoring
- **Dependencies:** M19

### M21: E2E Error Handling, Edge Cases & User Journeys
- **Purpose:** Test error propagation, concurrency scenarios, full end-to-end user journeys, cross-cutting edge cases
- **Dependencies:** M20

## Milestone Summary

| Milestone | Name | Features Tested | Est. Stories | Dependencies | Type |
|-----------|------|----------------|-------------|-------------|------|
| M17 | E2E Test Infra & Foundation | FA-7, FA-9, FA-16, FA-17 | 9 | M1–M16 | E2E Test |
| M18 | E2E Workspace, Chat & Board | FA-1, FA-2, FA-3, FA-6, FA-15 | 10 | M17 | E2E Test |
| M19 | E2E BRD, Review & Collab | FA-4, FA-8, FA-10, FA-12, FA-13 | 10 | M18 | E2E Test |
| M20 | E2E Similarity, Merge & Admin | FA-5, FA-11 | 9 | M19 | E2E Test |
| M21 | E2E Errors, Journeys & Edge Cases | FA-14, journeys, concurrency | 8 | M20 | E2E Test |

**Totals:** 5 milestones, ~46 estimated stories

## Dependency Flow Diagram

```
M1–M16 (Implementation — READ ONLY)
 └── M17 (Test Infra + Foundation Tests)
      └── M18 (Workspace + Chat + Board + Real-Time)
           └── M19 (BRD + Review + Collaboration + Notifications)
                └── M20 (Similarity + Merge + Admin)
                     └── M21 (Error Handling + Journeys + Edge Cases)
```

## Execution Guide

### Branch Strategy

| Milestone | Branch Pattern | Base Branch | Merge Target |
|-----------|---------------|-------------|-------------|
| M17 | ralph/m17-e2e-foundation | master | master |
| M18 | ralph/m18-e2e-workspace | master (after M17 merge) | master |
| M19 | ralph/m19-e2e-review-collab | master (after M18 merge) | master |
| M20 | ralph/m20-e2e-similarity-admin | master (after M19 merge) | master |
| M21 | ralph/m21-e2e-journeys-edge | master (after M20 merge) | master |

### Acceptance Criteria per Milestone

**Every E2E test milestone must pass:**
- All new E2E tests pass (`npx playwright test --config=e2e/playwright.config.ts`)
- All previously written E2E tests still pass (no regressions)
- No production code regressions (existing unit/integration tests still pass)
- Bug fixes found during E2E testing are committed and documented

### Critical Rule: Fix Before Continue

After EACH implemented E2E test:
1. Run the full E2E test suite
2. If any test fails, identify the root cause
3. If it's a test bug: fix the test
4. If it's a production bug: fix the production code and document the fix
5. Only proceed to the next E2E test after all tests pass
