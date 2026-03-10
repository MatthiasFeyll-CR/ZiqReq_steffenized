# Milestone 4 Spec Reconciliation

## Summary
- **Milestone:** M4 — Board Core
- **Date:** 2026-03-10
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 0
- **Applied and flagged (FEATURE DESIGN):** 0
- **Applied and flagged (LARGE TECHNICAL):** 1
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

No small technical deviations found. Implementation file paths, parameter names, and schema field names all matched specifications.

### FEATURE DESIGN (Applied and flagged)

No feature design deviations found. All user-facing behavior, UI components, and API response shapes matched specifications.

### LARGE TECHNICAL (Applied and flagged)

| # | Deviation | Document Updated | Change | Applied By |
|---|-----------|-----------------|--------|-------------|
| 1 | D-001: Gateway board mirror model test pattern | `docs/02-architecture/project-structure.md` | Clarified that Gateway mirror models for Core tables require migrations when used in test suites | System (pipeline) |

---

## Detailed Deviation Analysis

### D-001: Gateway Board Mirror Model Test Database Pattern

- **Source:** `.ralph/archive/m4-board-core/progress.txt` — US-001: Board Nodes REST API
- **What the spec said:** `docs/02-architecture/project-structure.md` (lines 74-97) documented the mirror model pattern with the rule "Gateway's mirror model has no migrations" (line 75). The AdminParameter example (line 273) showed a mirror model with `managed=False`. The pattern implied Gateway board models would follow the same approach.
- **What was actually implemented:** Gateway board models (`services/gateway/apps/board/models.py`) use `db_table = "board_nodes"` and `db_table = "board_connections"` WITHOUT `managed=False`, and Gateway's board app includes migrations (`0001_initial.py`, `0002_boardconnection.py`).
- **Why it changed:** Django's test infrastructure requires the ability to create tables in the test database. With `managed=False`, Django skips table creation during test database setup, causing all board endpoint tests to fail with "relation does not exist" errors. Tests need Django to manage the table lifecycle.
- **Upstream docs affected:** `docs/02-architecture/project-structure.md` (Django Model Sharing Pattern section)
- **Category:** LARGE TECHNICAL — affects architectural pattern for Gateway-Core integration, impacts future milestones

**Impact on Future Milestones:**
- M10 (Review System) will need Gateway mirror models for `review_assignments` and `review_timeline_entries`
- Any future Core-owned tables exposed via Gateway REST endpoints should follow the M4 pattern (mirror models with migrations for test compatibility) rather than the `managed=False` pattern

---

## Documents Modified

1. `docs/02-architecture/project-structure.md` — Updated Django Model Sharing Pattern section to clarify test database requirements

---

## QA Report Reconciliation

The QA report (`docs/08-qa/qa-m4-board-core.md`) stated "No deviations found. Implementation matches specifications." This is accurate at the **functional specification level** — all API endpoints, data model fields, UI components, and user-facing behavior matched the spec.

The D-001 deviation is an **architectural implementation detail** discovered during testing. The spec correctly predicted that Gateway would need mirror models for board tables (project-structure.md line 97), but did not specify the `managed=False` vs migrations trade-off. The implementation refined this pattern based on test infrastructure requirements.

---

## Implementation Notes from Progress File

The following implementation patterns were established during M4 and should inform future milestones:

1. **Gateway mirror models for Core tables:**
   - Use `db_table = "table_name"` to point to Core's table
   - Include migrations in Gateway's app (required for test database creation)
   - Do NOT use `managed=False` (breaks test infrastructure)
   - Core still owns schema authority — Gateway migrations must stay in sync with Core's schema

2. **React Flow integration patterns:**
   - Custom nodes require `memo()` wrapper for performance
   - NodeTypes map must be defined outside component (not in `useMemo`) to avoid re-renders
   - ResizeObserver required for canvas rendering — mock `@/components/board/BoardCanvas` in any test that renders workspace layout

3. **Board API patterns:**
   - Board URLs nested under ideas: `/api/ideas/:id/board/...`
   - Reuse MiddlewareAuthentication and access check patterns from chat endpoints
   - Duplicate connection prevention checked at application level (return 409) before DB insert to provide proper error response
   - CASCADE delete on board_nodes cleans up connections automatically

4. **Test infrastructure:**
   - Docker node-tests image requires rebuild after adding new test files (no volume mount)
   - Docker python-tests image requires rebuild after adding migration files
   - React Flow components need module-level mocks in tests (ResizeObserver not available in jsdom)

---

## Cascade Effects

### Project Structure Pattern

The M4 implementation establishes the canonical pattern for Gateway mirror models of Core-owned tables. The updated pattern is:

**When Gateway exposes REST endpoints for Core-owned tables:**
1. Core creates and owns the table (schema authority)
2. Core generates and runs migrations for the table
3. Gateway creates a mirror Django model with identical schema and `db_table` pointing to Core's table
4. Gateway creates migrations for the mirror model (required for test database)
5. Both services connect to the same PostgreSQL database in all environments
6. Core owns schema changes — Gateway's mirror must be updated manually when Core schema changes

This differs from the `managed=False` pattern used for read-only admin access (e.g., AdminParameter), where Gateway only reads and never runs tests against the table.

### Test Strategy

Django test suites that test Gateway endpoints for Core-owned tables now follow this pattern:
- Test database is created fresh per test run
- Django runs migrations for both Gateway apps (creates mirror tables) and Core apps (if Core is included in test environment)
- Tests use Gateway's mirror models via DRF serializers
- Table lifecycle (create/destroy) managed by Django test framework

---

## Upstream Spec Updates Applied

### docs/02-architecture/project-structure.md

**Section: Django Model Sharing Pattern (lines 43-97)**

Updated to distinguish between two mirror model patterns:

1. **REST API mirror models** (board_nodes, board_connections, ideas, chat_messages) — Gateway runs tests against these tables, requires migrations
2. **Read-only mirror models** (admin_parameters) — Gateway only reads, uses `managed=False`, no migrations

See git diff for exact changes.
