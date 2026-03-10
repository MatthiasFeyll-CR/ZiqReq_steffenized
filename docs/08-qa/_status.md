# QA Engineer — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-09
- **Last updated:** 2026-03-10

## Current Review
- **Milestone:** 6 — WebSocket & Real-Time
- **Phase:** 6 (verdict delivered)
- **Bugfix cycle:** 4 (post-escalation human fix)
- **Status:** failed

## Milestone QA History
| Milestone | QA Report | Bugfix Cycles | Final Verdict | Date |
|-----------|-----------|---------------|---------------|------|
| M1 — Foundation | `qa-m1-foundation.md` | 2 (post-escalation) | PASS | 2026-03-09 |
| M2 — Landing | `qa-m2-landing.md` | 0 | PASS | 2026-03-09 |
| M3 — Workspace Chat | `qa-m3-workspace-chat.md` | 1 | PASS | 2026-03-09 |
| M4 — Board Core | `qa-m4-board-core.md` | 2 | PASS | 2026-03-10 |
| M5 — Board Advanced | `qa-m5-board-advanced.md` | 1 | PASS | 2026-03-10 |
| M6 — WebSocket | `qa-m6-websocket.md` | 4 (post-escalation) | FAIL | 2026-03-10 |

## Input Consumed
- .ralph/prd.json
- docs/01-requirements/*.md
- docs/02-architecture/api-design.md
- docs/02-architecture/tech-stack.md
- docs/03-design/component-specs.md
- docs/04-test-architecture/test-matrix.md
- docs/04-test-architecture/runtime-safety.md
- tasks/prd-m6.json
- services/gateway/apps/websocket/consumers.py
- services/gateway/apps/websocket/middleware.py
- services/gateway/apps/websocket/tests/test_consumers.py
- services/gateway/conftest.py
- services/gateway/gateway/settings/test.py
- infra/docker/init-test-db.sql
- docker-compose.test.yml
- frontend/src/store/websocket-slice.ts
- frontend/src/hooks/use-websocket.ts
- frontend/src/components/common/OfflineBanner.tsx
- frontend/src/components/layout/ConnectionIndicator.tsx
- frontend/src/components/workspace/PresenceIndicators.tsx
- frontend/src/components/board/UserSelectionHighlight.tsx

## Handoff
- **Ready for merge:** false
- **Next phase:** Bugfix cycle 4 — Ralph implements BF-001 from tasks/prd-m6.json (replace serialized_rollback with app-table TRUNCATE)
- **Files produced:** docs/08-qa/qa-m6-websocket.md, docs/08-qa/_status.md
- **Deviations for Spec Reconciler:** 2 (DEV-001: OfflineBanner color, DEV-002: ConnectionIndicator tokens)

## Open Issues
- DEF-002 (Critical): 11 backend consumer tests ERROR with `IntegrityError: auth_permission_pkey` during `deserialize_db_from_string()`. Root cause: `serialized_rollback=True` causes `_fixture_setup` to INSERT auth_permission rows into a non-empty DB. Fix: replace serialized_rollback with app-table-only TRUNCATE fixture.
- Human fix (commit 1b3e5dc) improved from 17 affected (cycle 3) to 11 affected (cycle 4). Convergence confirmed — one more targeted fix should resolve.
