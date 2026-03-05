# Wave 0 Spec Reconciliation

## Summary
- **Wave:** 0
- **Milestones included:** M1 (Foundation & Scaffold)
- **Date:** 2026-03-05
- **Total deviations found:** 9
- **Auto-applied (SMALL TECHNICAL):** 9
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: Core gRPC uses single servicer | `docs/02-architecture/project-structure.md` | Replaced 8 separate servicer files (`idea_servicer.py`, `chat_servicer.py`, etc.) with single `core_servicer.py`. Added `tests/test_core_grpc.py`. |
| 2 | D-002: Core events file naming | `docs/02-architecture/project-structure.md` | Changed `events/publishers.py` to `events/publisher.py` (singular). Added `events/broker.py` for exchange/queue/DLQ topology. |
| 3 | D-003: Test settings added for all services | `docs/02-architecture/project-structure.md` | Added `settings/test.py` entry under gateway, core, and AI service settings directories. |
| 4 | D-004: Root test infrastructure | `docs/02-architecture/project-structure.md` | Added `conftest.py`, `pyproject.toml`, and `scripts/run-tests.sh` to root directory layout. |
| 5 | D-005: NotificationBell moved to layout/ | `docs/02-architecture/project-structure.md`, `docs/03-design/component-inventory.md` | Moved NotificationBell from `components/notification/` to `components/layout/` (navbar element). Updated inventory category from Notifications to Layout. |
| 6 | D-006: IdeasListFloating moved to layout/ | `docs/02-architecture/project-structure.md`, `docs/03-design/component-inventory.md` | Moved IdeasListFloating from `components/landing/` to `components/layout/` (navbar-anchored panel). Updated inventory category from Landing to Layout. |
| 7 | D-007: AuthenticatedLayout added | `docs/02-architecture/project-structure.md`, `docs/03-design/component-inventory.md` | Added new AuthenticatedLayout component in `components/layout/`. Layout route with auth guard + Outlet replaces per-route AuthGuard wrappers. |
| 8 | D-008: globals.css for Tailwind CSS 4 | `docs/02-architecture/project-structure.md` | Added `frontend/src/app/globals.css` to directory layout (Tailwind CSS 4 @theme config, CSS custom properties, @font-face). |
| 9 | D-009: test-setup.ts for vitest | `docs/02-architecture/project-structure.md` | Added `frontend/src/test-setup.ts` to directory layout (matchMedia polyfill, @testing-library/jest-dom/vitest). |

### FEATURE DESIGN (Human-approved)

None.

### LARGE TECHNICAL (Human-approved)

None.

### REJECTED

None.

## Documents Modified

- `docs/02-architecture/project-structure.md` — 7 edits (D-001 through D-004, D-005, D-006, D-007, D-008, D-009)
- `docs/03-design/component-inventory.md` — 4 edits (D-005, D-006, D-007 + summary counts)

## Impact on Future Milestones

- **M2 (Landing Page):** `components/landing/` no longer contains IdeasListFloating — it lives in `components/layout/`. M2 should import from there.
- **M10 (Notification System):** NotificationBell already exists in `components/layout/`. M10 only needs to implement NotificationPanel and NotificationItem in `components/notification/`.
- **All milestones:** Test settings (`settings/test.py`) are available for all 3 Django services. Use `DJANGO_SETTINGS_MODULE=<service>.settings.test` for lightweight SQLite-based testing.
- **All milestones:** Root `conftest.py` uses `collect_ignore_glob` to prevent cross-service test collection. New services should be added to the ignore list if needed.
