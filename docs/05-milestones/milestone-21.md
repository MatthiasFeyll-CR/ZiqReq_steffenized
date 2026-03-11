# Milestone 21: E2E Error Handling, Edge Cases & User Journeys

## Overview
- **Execution order:** 21 (runs after M20)
- **Estimated stories:** 8
- **Dependencies:** M17 (test infra), M18 (workspace), M19 (review + collab), M20 (similarity + admin)
- **Type:** E2E Testing

## Purpose

Test error handling patterns, concurrency edge cases, and complete end-to-end user journeys that span the entire application. These tests validate the system's resilience and the full user experience from start to finish.

## Features Tested

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-14 | Error Handling (universal pattern, retry, logs modal) | P1 | docs/01-requirements/features.md |
| JOURNEY-001–005 | Full user journeys | P1 | docs/04-test-architecture/integration-scenarios.md |
| CONC-001–006 | Concurrency scenarios | P1 | docs/04-test-architecture/integration-scenarios.md |
| ERR-001–008 | Error propagation scenarios | P1 | docs/04-test-architecture/integration-scenarios.md |

## Story Outline

### S1: E2E Error Handling — Universal Pattern (FA-14)
- **Test: Error toast with Show Logs and Retry (F-14.1)** — Trigger an API error → error toast appears with "Show Logs" and "Retry" buttons
- **Test: Show Logs modal (F-14.1)** — Click "Show Logs" → centered modal with console output, network response, technical details, support contact
- **Test: Retry button (F-14.1)** — Click "Retry" → failed operation retried
- **Test: Max retry attempts (F-14.1)** — Retry 3 times (or admin-configured max) → after max retries, appropriate final error state
- **Test: AI processing failure (ERR-001)** — AI service returns error → error toast, chat remains functional, no partial board state
- **Test: PDF generation failure (ERR-002)** — PDF generation fails → error toast, BRD data intact, retry available
- **Test: gRPC failure between services (ERR-004)** — Core service temporarily unavailable → appropriate HTTP error, error toast, no partial writes

**Acceptance criteria:**
- [ ] Universal error pattern works (toast + logs modal + retry)
- [ ] AI failure handled gracefully (chat remains usable)
- [ ] PDF failure handled without data loss
- [ ] gRPC failures surface appropriate errors

### S2: E2E Error Handling — Network & Connection Errors
- **Test: WebSocket disconnection during editing (ERR-003)** — Disconnect WebSocket → offline banner, chat/board locked, other users see disconnect
- **Test: Reconnection syncs state (ERR-003)** — Disconnect → other user sends messages → reconnect → missed messages appear
- **Test: Offline banner with retry countdown (F-6.2)** — Disconnected → banner shows "Retrying in X seconds" with countdown
- **Test: Manual reconnect button (F-6.2, NFR-R5)** — Click manual reconnect during offline → immediate reconnection attempt
- **Test: Exponential backoff (NFR-R4)** — Multiple reconnection failures → retry intervals increase (exponential backoff)
- **Test: Auth token expiry handling (ERR-006)** — In dev bypass mode, verify auth persistence across navigation (production Azure AD flow cannot be E2E tested)

**Acceptance criteria:**
- [ ] WebSocket disconnect shows offline UI and locks editing
- [ ] Reconnection syncs all missed state
- [ ] Manual reconnect works
- [ ] Exponential backoff observed in retry intervals

### S3: E2E Concurrency Scenarios
- **Test: Simultaneous chat messages (CONC-001)** — Two users send messages at nearly the same time → both persisted in correct order, both broadcast
- **Test: Board edit during AI update (CONC-002)** — User moves node while AI creates new nodes → both changes applied, no corruption
- **Test: Concurrent review actions (CONC-003, SCN-018)** — Two reviewers act simultaneously → latest action wins, both recorded in timeline
- **Test: AI processing restart on new message (CONC-006)** — Send message during AI processing → AI restarts with all messages, only one response
- **Test: Duplicate collaboration invitation (CONC-005)** — Accept invitation while owner sends new invite → no duplicate collaborator
- **Test: Merge request while submitting for review (CONC-004)** — User A requests merge while User B submits → one succeeds, other fails gracefully

**Acceptance criteria:**
- [ ] Simultaneous operations don't cause data corruption
- [ ] Concurrent review actions follow "latest wins" rule
- [ ] AI processing restart works cleanly
- [ ] Race conditions handled gracefully

### S4: E2E User Journey — New Idea to Accepted (JOURNEY-001)
- **Test: Complete lifecycle** — Full end-to-end journey:
  1. User logs in (dev bypass) → Landing page
  2. Types first message in hero section → Idea created, navigated to workspace
  3. AI responds (mocked) → Title auto-generated
  4. User and AI exchange multiple messages → Board populated
  5. User opens Review tab → BRD generates
  6. User reviews readiness evaluation → sufficient
  7. User submits with message and reviewer assignment
  8. Reviewer opens Review page → Sees idea in "Assigned to me"
  9. Reviewer reads BRD, posts comment, accepts
  10. Owner receives acceptance notification
  11. Owner visits idea → Everything read-only

**Acceptance criteria:**
- [ ] Complete journey from creation to acceptance works without manual intervention
- [ ] All assertions pass at each step (navigation, API, WebSocket, notifications)
- [ ] Data cleanup after test

### S5: E2E User Journey — Collaborative Brainstorming (JOURNEY-002)
- **Test: Multi-user real-time collaboration** — Full journey:
  1. User A creates idea and starts brainstorming
  2. User A invites User B → Notification sent
  3. User B accepts invitation → Joins idea
  4. Both users visible in presence indicators
  5. User B sends chat message → User A sees it in real-time
  6. AI addresses both users by name in response (mocked)
  7. User A selects board node → User B sees highlight with A's name
  8. User B edits a different node → No conflict
  9. Both users see each other's board changes

**Acceptance criteria:**
- [ ] Full collaborative session works across two browser contexts
- [ ] Presence, chat, board sync all function correctly
- [ ] AI multi-user behavior works (mocked)

### S6: E2E User Journey — Rejection-Rework-Resubmission (JOURNEY-003)
- **Test: Full rejection cycle** — Full journey:
  1. Idea submitted (version 1) → In Review
  2. Reviewer rejects with feedback → Rejected
  3. Owner reworks brainstorming (adds more detail)
  4. Owner regenerates BRD selectively
  5. Owner resubmits (version 2) → In Review
  6. Reviewer sees v1 and v2 linked in timeline
  7. Reviewer downloads both PDFs for comparison
  8. Reviewer accepts → Accepted
  9. Timeline shows full history: submit → reject → resubmit → accept

**Acceptance criteria:**
- [ ] Full rejection-rework-resubmit-accept cycle works
- [ ] Both BRD versions accessible and downloadable
- [ ] Timeline shows complete audit trail

### S7: E2E User Journey — Merge Detection & Resolution (JOURNEY-004)
- **Test: Complete merge journey** — Full journey:
  1. User A creates idea about topic X
  2. User B creates idea about similar topic
  3. Both ideas develop → Keywords generated (mocked)
  4. Background matching detects overlap
  5. Deep Comparison confirms similarity (mocked)
  6. Both users notified → Can view each other's idea read-only
  7. User A requests merge → User B's idea shows merge banner
  8. User B accepts → New merged idea created
  9. Both users are co-owners of new idea
  10. Original ideas accessible read-only with reference
  11. Merged idea has synthesized context and combined board

**Acceptance criteria:**
- [ ] Complete merge detection and resolution journey works
- [ ] Merged idea valid with co-owners and combined content
- [ ] Original ideas preserved read-only

### S8: E2E User Journey — Admin Configuration & Monitoring (JOURNEY-005)
- **Test: Admin workflow** — Full journey:
  1. Admin logs in → Navbar shows Admin link
  2. Navigates to Admin Panel → 4 tabs visible
  3. AI Context tab: enters company context in both areas
  4. Parameters tab: adjusts debounce timer and message cap
  5. Monitoring tab: views active connections, ideas by state, service health
  6. Users tab: searches for a user → sees stats
  7. Returns to brainstorming → New parameters take effect immediately
- **Test: Monitoring alerts** — Admin opts into alerts → trigger health check issue (if possible) or verify alert config persists

**Acceptance criteria:**
- [ ] Full admin workflow works across all 4 tabs
- [ ] Parameter changes effective at runtime
- [ ] Monitoring dashboard shows real data
- [ ] User search returns valid results

## Execution Rule

**After implementing EACH story above:**
1. Run `npx playwright test --config=e2e/playwright.config.ts`
2. ALL tests must pass (including M17 + M18 + M19 + M20 tests)
3. If any test fails → identify root cause → fix test or production code → all green before continuing

## Per-Story Complexity Assessment

| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Error Handling — Universal | ~10,000 | FA-14, ERR-001/002/004 | 1-2 | High | Triggering errors |
| 2 | Network & Connection Errors | ~8,000 | ERR-003/006, F-6.2, NFR-R4/R5 | 1-2 | High | Network simulation |
| 3 | Concurrency Scenarios | ~12,000 | CONC-001–006, SCN-018 | 1-2 | High | Timing-sensitive |
| 4 | Journey — Idea to Accepted | ~15,000 | JOURNEY-001, many FAs | 1-2 | High | Full stack |
| 5 | Journey — Collaborative | ~12,000 | JOURNEY-002, FA-6/8 | 1-2 | High | Two contexts |
| 6 | Journey — Rejection Cycle | ~12,000 | JOURNEY-003, FA-4/10 | 1-2 | High | Multi-step state |
| 7 | Journey — Merge | ~14,000 | JOURNEY-004, FA-5 | 1-2 | High | Complex AI mock |
| 8 | Journey — Admin | ~8,000 | JOURNEY-005, FA-11 | 1-2 | Medium | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~91,000
- **Cumulative domain size:** Very Large (cross-cutting journeys)
- **Information loss risk:** High (score: 9)
- **Context saturation risk:** High — mitigated because each story is a self-contained test file

**Mitigation note:** Although the information loss risk score is 9, each test story produces an independent test file. The agent does NOT need to hold all prior stories in memory — each journey test is self-contained with its own setup/teardown. The high score comes from cross-domain knowledge requirements, not from in-milestone cumulative state. Each story references upstream requirements directly. This is acceptable.

## Milestone Acceptance Criteria
- [ ] Universal error handling pattern tested (toast + logs + retry)
- [ ] Network/connection error scenarios tested
- [ ] All 6 concurrency scenarios tested
- [ ] All 5 user journey tests pass end-to-end
- [ ] All M17 + M18 + M19 + M20 tests still pass (no regressions)
- [ ] Any production bugs discovered are fixed and documented
- [ ] FULL E2E SUITE GREEN — all ~46 test stories across M17–M21 pass

## Notes
- Error handling tests may need to inject failures (e.g., stop a service container briefly, or mock a failure response)
- Concurrency tests require precise timing — use Playwright's `Promise.all` for simultaneous actions
- User journey tests are the longest individual tests (~15s each) — they span the full application
- Journey tests should create their own isolated data and clean up after themselves
- The merge journey test (S7) is the most complex single test in the entire E2E suite
- After this milestone, the full E2E suite should cover ALL features described in the requirements docs
