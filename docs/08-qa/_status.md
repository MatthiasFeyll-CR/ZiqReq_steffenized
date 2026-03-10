# QA Engineer — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-09
- **Last updated:** 2026-03-10

## Current Review
- **Milestone:** 6 — WebSocket & Real-Time
- **Phase:** 6 (verdict delivered)
- **Bugfix cycle:** 3 (FINAL — ESCALATED)
- **Status:** escalated

## Milestone QA History
| Milestone | QA Report | Bugfix Cycles | Final Verdict | Date |
|-----------|-----------|---------------|---------------|------|
| M1 — Foundation | `qa-m1-foundation.md` | 2 (post-escalation) | PASS | 2026-03-09 |
| M2 — Landing | `qa-m2-landing.md` | 0 | PASS | 2026-03-09 |
| M3 — Workspace Chat | `qa-m3-workspace-chat.md` | 1 | PASS | 2026-03-09 |
| M4 — Board Core | `qa-m4-board-core.md` | 2 | PASS | 2026-03-10 |
| M5 — Board Advanced | `qa-m5-board-advanced.md` | 1 | PASS | 2026-03-10 |
| M6 — WebSocket | `qa-m6-websocket.md` | 3 | ESCALATE | 2026-03-10 |

## Input Consumed
- .ralph/prd.json
- .ralph/progress.txt
- docs/01-requirements/*.md
- docs/02-architecture/api-design.md
- docs/02-architecture/tech-stack.md
- docs/03-design/component-specs.md
- docs/04-test-architecture/test-matrix.md
- tasks/prd-m6.json
- services/gateway/apps/websocket/consumers.py
- services/gateway/apps/websocket/middleware.py
- services/gateway/apps/websocket/tests/test_consumers.py
- services/gateway/conftest.py
- services/gateway/gateway/settings/test.py
- services/gateway/pyproject.toml
- pyproject.toml
- docker-compose.test.yml
- frontend/src/store/websocket-slice.ts
- frontend/src/hooks/use-websocket.ts
- frontend/src/components/common/OfflineBanner.tsx
- frontend/src/components/layout/ConnectionIndicator.tsx
- frontend/src/components/workspace/PresenceIndicators.tsx
- frontend/src/components/board/UserSelectionHighlight.tsx

## Handoff
- **Ready for merge:** false
- **Escalated:** true
- **Next phase:** Human intervention required — restructure test infrastructure for async Django Channels + PostgreSQL in Docker (see Escalation Report in qa-m6-websocket.md)
- **Files produced:** docs/08-qa/qa-m6-websocket.md, docs/08-qa/_status.md
- **Deviations for Spec Reconciler:** 2 (DEV-001: OfflineBanner color, DEV-002: ConnectionIndicator tokens)

## Open Issues
- DEF-002 (Critical, ESCALATED): Backend WebSocket consumer tests fail in Docker PostgreSQL due to test DB lifecycle issues. Three bugfix cycles have each changed the error type without converging:
  - Cycle 1: FK constraint → fixed
  - Cycle 2: content type dup key → changed to auth_permission dup key (keepdb issue)
  - Cycle 3: auth_permission dup key → changed to DB "test_ziqreq_test" does not exist (REGRESSED)
  - Root cause: fragile interaction between pytest-asyncio, Django TransactionTestCase, serialized_rollback, and PostgreSQL in Docker
  - Application code is correct — only test infrastructure needs fixing
  - See Escalation Report in qa-m6-websocket.md for recommended approaches
- DEF-001 (RESOLVED): FK constraint violations fixed in cycle 1 by consolidating DB setup.
