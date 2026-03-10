# QA Engineer — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-09
- **Last updated:** 2026-03-10

## Current Review
- **Milestone:** 6 — WebSocket & Real-Time
- **Phase:** 6 (verdict delivered)
- **Bugfix cycle:** 5 (BF-001 for DEF-003)
- **Status:** failed

## Milestone QA History
| Milestone | QA Report | Bugfix Cycles | Final Verdict | Date |
|-----------|-----------|---------------|---------------|------|
| M1 — Foundation | `qa-m1-foundation.md` | 2 (post-escalation) | PASS | 2026-03-09 |
| M2 — Landing | `qa-m2-landing.md` | 0 | PASS | 2026-03-09 |
| M3 — Workspace Chat | `qa-m3-workspace-chat.md` | 1 | PASS | 2026-03-09 |
| M4 — Board Core | `qa-m4-board-core.md` | 2 | PASS | 2026-03-10 |
| M5 — Board Advanced | `qa-m5-board-advanced.md` | 1 | PASS | 2026-03-10 |
| M6 — WebSocket | `qa-m6-websocket.md` | 5 | FAIL | 2026-03-10 |

## Input Consumed
- .ralph/prd.json
- .ralph/progress.txt
- docs/01-requirements/*.md
- docs/02-architecture/api-design.md
- docs/02-architecture/tech-stack.md
- docs/03-design/component-specs.md
- docs/04-test-architecture/test-matrix.md
- docs/04-test-architecture/runtime-safety.md
- tasks/prd-m6.json
- services/gateway/apps/websocket/consumers.py
- services/gateway/apps/websocket/middleware.py
- services/gateway/apps/websocket/routing.py
- services/gateway/apps/websocket/tests/test_consumers.py
- services/gateway/conftest.py
- services/gateway/gateway/settings/test.py
- services/gateway/gateway/asgi.py

## Handoff
- **Ready for merge:** false
- **Next phase:** Bugfix cycle 5 — Ralph implements BF-001 from tasks/prd-m6.json (add DB connection cleanup fixture)
- **Files produced:** docs/08-qa/qa-m6-websocket.md, docs/08-qa/_status.md
- **Deviations for Spec Reconciler:** 2 (DEV-001: OfflineBanner color, DEV-002: ConnectionIndicator tokens)

## Open Issues
- DEF-003 (Critical): 8 backend consumer tests FAIL with connection/access assertion errors. Root cause: stale DB connections between async TransactionTestCase tests. Fix: add connections.close_all() autouse fixture to conftest.py.
- DEF-002 (RESOLVED): IntegrityError on auth_permission — fixed by BF-001 (post_migrate signal disconnect).
- DEF-001 (RESOLVED): FK constraint violation — fixed in cycle 1.
