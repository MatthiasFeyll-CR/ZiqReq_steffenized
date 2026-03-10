# QA Report: Milestone 4 — Board Core

**Date:** 2026-03-09
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m4.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed 9 user stories covering Board Nodes REST API, Board Connections REST API, React Flow Canvas, BoxNode, GroupNode, FreeTextNode, ConnectionEdge, BoardToolbar, and Minimap/Zoom Controls. All acceptance criteria are met in the implementation. All 108 backend tests and 107 frontend tests pass. However, 13 of 15 test matrix test IDs are missing from the codebase — Ralph implemented tests under API-BOARD/DB-NODE/DB-CONN IDs for backend but did not implement the 13 frontend unit tests specified in the test matrix (T-3.1.01-04, T-3.2.02-06/08, T-3.3.03, T-3.8.01-02).

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Board Nodes REST API | PASS | All CRUD endpoints implemented with proper validation (node_type, parent_id group check, locked nodes, title/body max length). 25 backend tests cover API-BOARD.01-06, DB-NODE.01-04. |
| US-002 | Board Connections REST API | PASS | All CRUD endpoints with self-connection prevention, duplicate detection (409), CASCADE delete. Backend tests cover API-BOARD.08-11, DB-CONN.01-03. |
| US-003 | React Flow Canvas Setup | PASS | ReactFlow canvas with dot grid (20px gap), zoom 25%-200%, var(--foreground) background color. T-3.3.01 and T-3.3.02 tests exist. |
| US-004 | BoxNode Component | PASS | Title bar with border-b, bullet body, min 192px/max 320px, border/rounded-md/shadow-sm/bg-card, Pin reference button, Bot AI badge, Lock icon. |
| US-005 | GroupNode Component | PASS | 2px dashed border var(--border-strong), bg var(--muted) opacity-30, label badge top-left, min 200x150, NodeResizer for resize. |
| US-006 | FreeTextNode Component | PASS | Transparent bg, no border (dashed on hover), text-sm text-foreground, click-to-edit textarea with auto-grow. |
| US-007 | ConnectionEdge Component | PASS | Smoothstep edges with ArrowClosed marker, 1.5px gray stroke, 2.5px on select, double-click label editor with bg-card/border/rounded-sm/text-xs, selected stroke var(--primary). |
| US-008 | BoardToolbar Component | PASS | border-b bg-card h-10 px-2, Plus/Trash2/Maximize2 icons, ghost icon-sm buttons, dividers between groups, delete disabled when selectedCount=0. |
| US-009 | Minimap and Zoom Controls | PASS | MiniMap bottom-right 120x80px with border/rounded-sm/shadow-sm/bg-card, Controls bottom-left. |

**Stories passed:** 9 / 9
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 2 found / 13 missing out of 15 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-3.1.01 | MISSING | -- | DEF-001: Unit test for BoxNode rendering (title + body) not implemented |
| T-3.1.02 | MISSING | -- | DEF-002: Unit test for GroupNode rendering as container not implemented |
| T-3.1.03 | MISSING | -- | DEF-003: Unit test for FreeTextNode rendering without border not implemented |
| T-3.1.04 | MISSING | -- | DEF-004: Unit test for nested groups rendering not implemented |
| T-3.2.02 | MISSING | -- | DEF-005: Unit test for drag-into-group attach not implemented |
| T-3.2.03 | MISSING | -- | DEF-006: Unit test for drag-out-of-group detach not implemented |
| T-3.2.04 | MISSING | -- | DEF-007: Unit test for double-click content editor not implemented |
| T-3.2.05 | MISSING | -- | DEF-008: Unit test for connection rendering as edge not implemented |
| T-3.2.06 | MISSING | -- | DEF-009: Unit test for double-click connection label editor not implemented |
| T-3.2.08 | MISSING | -- | DEF-010: Unit test for AI-created items showing robot badge not implemented |
| T-3.3.01 | FOUND | `frontend/src/__tests__/board-canvas.test.tsx` | Verified -- tests canvas rendering with dot grid and zoom range |
| T-3.3.02 | FOUND | `frontend/src/__tests__/board-canvas.test.tsx` | Verified -- tests minimap and controls rendering with correct positioning |
| T-3.3.03 | MISSING | -- | DEF-011: Unit test for toolbar button actions not implemented |
| T-3.8.01 | MISSING | -- | DEF-012: Unit test for reference button visibility not implemented |
| T-3.8.02 | MISSING | -- | DEF-013: Unit test for reference button inserting @board[uuid] not implemented |

*Note: Ralph implemented extensive backend tests (25 node tests, 20 connection tests) under API-BOARD/DB-NODE/DB-CONN IDs, but the 13 frontend unit tests from the test matrix were not implemented.*

---

## Defects

### DEF-001: Missing test T-3.1.01 — BoxNode render test
- **Severity:** Major
- **Story:** US-004
- **File(s):** Missing `frontend/src/__tests__/box-node.test.tsx`
- **Expected (per test matrix):** Unit test verifying box node renders with title + body
- **Actual (in code):** No test file exists for BoxNode component
- **Suggested Fix:** Create `frontend/src/__tests__/box-node.test.tsx` with test: render BoxNode with title and body data, verify title visible, body bullets rendered

### DEF-002: Missing test T-3.1.02 — GroupNode render test
- **Severity:** Major
- **Story:** US-005
- **File(s):** Missing `frontend/src/__tests__/group-node.test.tsx`
- **Expected (per test matrix):** Unit test verifying group node renders as container
- **Actual (in code):** No test file exists for GroupNode component
- **Suggested Fix:** Create test rendering GroupNode with title, verify dashed border container and label badge

### DEF-003: Missing test T-3.1.03 — FreeTextNode render test
- **Severity:** Major
- **Story:** US-006
- **File(s):** Missing `frontend/src/__tests__/free-text-node.test.tsx`
- **Expected (per test matrix):** Unit test verifying free text renders without card border
- **Actual (in code):** No test file exists for FreeTextNode component
- **Suggested Fix:** Create test rendering FreeTextNode with body text, verify transparent background, no border by default

### DEF-004: Missing test T-3.1.04 — Nested groups render test
- **Severity:** Minor
- **Story:** US-005
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test verifying nested groups render correctly
- **Actual (in code):** No test exists
- **Suggested Fix:** Add test in group-node test file rendering a group inside another group, verify correct visual nesting

### DEF-005: Missing test T-3.2.02 — Drag into group test
- **Severity:** Major
- **Story:** US-005
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test for drag box into group sets parent_id
- **Actual (in code):** No test exists
- **Suggested Fix:** Create test simulating drag event that attaches box to group. Note: drag-in/out is deferred to M5 per PRD notes, so this test should verify the parent_id prop mechanism exists

### DEF-006: Missing test T-3.2.03 — Drag out of group test
- **Severity:** Major
- **Story:** US-005
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test for drag box out of group sets parent_id to null
- **Actual (in code):** No test exists
- **Suggested Fix:** Same as DEF-005 — test the parent_id detach mechanism. Note drag-in/out deferred to M5

### DEF-007: Missing test T-3.2.04 — Double-click content editor test
- **Severity:** Major
- **Story:** US-006
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test for double-click opens content editor
- **Actual (in code):** FreeTextNode uses click-to-edit (not double-click). No test exists.
- **Suggested Fix:** Create test clicking FreeTextNode to enter edit mode, verify textarea appears

### DEF-008: Missing test T-3.2.05 — Connection rendering test
- **Severity:** Major
- **Story:** US-007
- **File(s):** Missing `frontend/src/__tests__/connection-edge.test.tsx`
- **Expected (per test matrix):** Unit test verifying connection renders as edge between two nodes
- **Actual (in code):** No test file exists for ConnectionEdge component
- **Suggested Fix:** Create test rendering ConnectionEdge with source/target props, verify SVG path rendered

### DEF-009: Missing test T-3.2.06 — Connection label editor test
- **Severity:** Minor
- **Story:** US-007
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test for double-click connection opens label editor
- **Actual (in code):** No test exists
- **Suggested Fix:** Create test simulating double-click on edge label, verify input field appears

### DEF-010: Missing test T-3.2.08 — AI badge test
- **Severity:** Major
- **Story:** US-004
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test verifying AI-created items show robot badge
- **Actual (in code):** BoxNode implements the AI badge (data-testid="ai-badge") but no test verifies it
- **Suggested Fix:** Add test in box-node test file rendering BoxNode with created_by="ai", verify Bot icon visible

### DEF-011: Missing test T-3.3.03 — Toolbar button actions test
- **Severity:** Major
- **Story:** US-008
- **File(s):** Missing `frontend/src/__tests__/board-toolbar.test.tsx`
- **Expected (per test matrix):** Unit test verifying toolbar buttons trigger correct actions
- **Actual (in code):** No test file exists for BoardToolbar component
- **Suggested Fix:** Create test rendering BoardToolbar, click Add Box / Delete / Fit View buttons, verify callbacks called

### DEF-012: Missing test T-3.8.01 — Reference button visibility test
- **Severity:** Major
- **Story:** US-004
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test verifying reference button visible on node
- **Actual (in code):** BoxNode implements reference button (data-testid="reference-button") but no test verifies it
- **Suggested Fix:** Add test in box-node test file verifying reference button renders with Pin icon

### DEF-013: Missing test T-3.8.02 — Reference button inserts @board[uuid] test
- **Severity:** Major
- **Story:** US-004
- **File(s):** Missing in test suite
- **Expected (per test matrix):** Unit test verifying click reference inserts @board[uuid] into chat
- **Actual (in code):** BoxNode dispatches CustomEvent "board:reference" but no test verifies it
- **Suggested Fix:** Add test clicking reference button, verify CustomEvent dispatched with correct @board[uuid] payload

---

## Deviations

No deviations found. Implementation matches specifications.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python Tests | `pytest` (Docker) | PASS | 108 passed in 3.37s |
| Frontend Tests | `vitest run` (Docker) | PASS | 107 passed |
| Frontend TypeScript | `npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Frontend Lint (ESLint) | `npx eslint src/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | FAILED (optional) | Pre-existing: duplicate module "events" in services/core and services/ai — not introduced by M4 |

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | |
| Backend lint (Ruff) | PASSED | |
| Backend typecheck (mypy) | FAILED (optional) | Pre-existing duplicate module issue, not M4-related |
| Frontend lint (ESLint) | PASSED | |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Summary:** All board endpoints use MiddlewareAuthentication. Every view function checks auth (401), validates idea existence (404), checks access control against owner/co-owner/collaborator (403). UUID inputs are validated before DB queries. No raw SQL. No user input rendered unsanitized. Serializers enforce field max lengths. No hardcoded secrets.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Summary:** Queries are simple filtered lookups on indexed columns (idea_id). No N+1 patterns. React Flow nodeTypes/edgeTypes/proOptions defined outside component (stable references). Nodes use memo() wrappers. No unnecessary re-renders identified.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| BoxNode | `docs/03-design/component-specs.md` S6.1 | PASS | bg-card, border, rounded-md, shadow-sm, min 192px/max 320px, title bar border-b, Pin reference, Bot AI badge, Lock icon |
| GroupNode | S6.2 | PASS | 2px dashed var(--border-strong), bg var(--muted) 30% opacity, label badge top-left bg-muted px-2 py-0.5 rounded, min 200x150, NodeResizer |
| FreeTextNode | S6.3 | PASS | Transparent bg, no border, dashed on hover, text-sm text-foreground, click-to-edit textarea |
| ConnectionEdge | S6.4 | PASS | Smoothstep, 1.5px gray, 2.5px selected var(--primary), ArrowClosed marker, double-click label editor bg-card border rounded-sm text-xs |
| BoardToolbar | S6.5 | PASS | border-b bg-card h-10 px-2, ghost icon-sm, Plus/Trash2/Maximize2, dividers between groups |
| BoardCanvas | S6.6 | PASS | var(--background) dot grid 20px gap, zoom 25%-200%, MiniMap 120x80 bottom-right, Controls bottom-left |

---

## Verdict

- **Result:** FAIL
- **Defects found:** 13 (all missing frontend unit tests from test matrix)
- **Deviations found:** 0
- **Bugfix PRD required:** yes
- **Bugfix cycle:** 1
