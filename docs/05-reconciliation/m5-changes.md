# Milestone 5 Spec Reconciliation

## Summary
- **Milestone:** M5 — Board Advanced
- **Date:** 2026-03-10
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 1
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Executive Summary

Milestone 5 implementation was exceptionally clean. Only one deviation was found: a text inconsistency in the milestone planning document regarding board reference format. The API design document already correctly specified the `@board[nodeId]` format, but the milestone doc incorrectly stated `[[Title]]`. This has been corrected.

**Key finding:** The bugfix BF-001 (lock toggle bypass) was NOT a deviation — the API design doc already correctly specified "Node not locked (unless toggling lock)" at line 358. The bugfix implemented exactly what was specified.

All other items in the progress file (fetch vs axios, React Flow API quirks, TypeScript lib settings, test mocking patterns) were implementation-level discoveries that do not require spec updates. They represent learned patterns, not spec deviations.

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: Board reference format | `docs/05-milestones/milestone-5.md` | Corrected line 41: "Pin button... [[Title]]" → "Reference button... @board[nodeId]" |
| 1 | D-001: Board reference format | `docs/05-milestones/milestone-5.md` | Corrected line 70: "Pin button inserts [[Title]]" → "Reference button inserts @board[nodeId]" |

### FEATURE DESIGN (Human-approved)

None.

### LARGE TECHNICAL (Human-approved)

None.

### REJECTED

None.

---

## Documents Modified
- `docs/05-milestones/milestone-5.md` — Corrected board reference format text (2 lines)

---

## Impact on Future Milestones

**None.** The board reference format is already correctly documented in:
- `docs/02-architecture/api-design.md` line 1287 (authoritative source)
- `docs/04-test-architecture/test-matrix.md` lines 127-129, 262 (test specs already use `@board[uuid]`)
- `docs/08-qa/qa-m4-board-core.md` line 58, 162 (M4 QA already verified `@board[uuid]`)

Future milestones (M6-M9) that reference board items will correctly use the `@board[nodeId]` format per the API design doc.

---

## Detailed Deviation Log

### D-001: Board Reference Format Text in Milestone Doc

- **Source:** `.ralph/archive/m5-board-advanced/progress.txt` US-007 (lines 112-122), `docs/08-qa/qa-m5-board-advanced.md` line 60
- **What the spec said:**
  - `docs/05-milestones/milestone-5.md` line 41: "Pin button on nodes, inserts [[Title]] reference into chat input"
  - `docs/05-milestones/milestone-5.md` line 70: "Pin button on nodes inserts [[Title]] reference into chat input"
- **What was actually implemented:**
  - Reference button dispatches `CustomEvent('board:reference', { detail: '@board[nodeId]' })`
  - ChatInput listens for event and inserts `@board[nodeId]` format into textarea
  - QA report verifies: "T-3.8.02 | @board[uuid] insertion"
- **Why it changed:**
  - This was already the correct format per `docs/02-architecture/api-design.md` line 1287:
    > `@board[<node_id>]` | `@board[7c9e6679-7425-40de-944b-e07fc1f90ae7]` | Reference a board item (F-2.6, F-3.9) | Rendered as clickable link showing node title; click navigates to Board tab and highlights the node
  - `docs/01-requirements/features.md` F-3.8 (line 132) does not specify an exact format, only "a formatted reference"
  - The milestone planning doc had incorrect placeholder text that didn't match the API design
- **Upstream docs affected:** `docs/05-milestones/milestone-5.md`
- **Autonomy level:** SMALL TECHNICAL — correcting text inconsistency where the authoritative API doc already had the correct format
- **Fix applied:** Auto-applied. Changed both occurrences to match the API design specification.

---

## Implementation Patterns Discovered (Not Deviations)

These items from `progress.txt` were valuable implementation learnings but do not require spec updates:

### API Patterns
- **fetch, not axios:** Already correctly specified in tech-stack.md:77
- **env.apiBaseUrl from `@/config/env`:** Standard Vite env var pattern, matches project-structure.md

### React Flow Patterns
- **`@xyflow/react` v12 API:** Node type lacks `positionAbsolute`, use `getInternalNode().internals.positionAbsolute`
- **`NodeDragHandler` type not exported:** Use inline type signature `(_event: React.MouseEvent, node: Node) => void`
- **`onNodeDragStop` fires only on drag end:** Correct for PATCH-on-end requirement
- **`expandParent: true` on child nodes:** Parent group auto-expands when child near edge
- **`SelectionMode.Partial`:** Enables Ctrl+drag selection box
- **`deleteKeyCode={null}`:** Disables built-in delete to use custom handler with lock check

### Redux Patterns
- **Undo stack bounded at 100:** Prevents memory growth
- **`useMemo` for `processedNodes`:** Injects callbacks and computed props before passing to ReactFlow
- **Pure reducer tests:** Test reducer functions directly, no component mocking needed

### Testing Patterns
- **`vi.fn<(params) => return>()` with explicit generic:** Needed for typed mock params
- **`vi.resetModules()` + `vi.doMock()` + dynamic `await import()`:** Isolate module state between tests
- **Mock `useNodesState` must be stateful:** Use module-level variable + callback-aware setter for tests verifying state mutations
- **Docker test container file sync:** Must rebuild with `--build` after changing test files
- **Test files need comprehensive React Flow mock:** `screenToFlowPosition`, `getInternalNode`, `SelectionMode`, etc.

### TypeScript Patterns
- **TS lib without es2022:** `Array.at()` unavailable, use bracket access instead

### Lock Bypass (BF-001)
- **NOT a deviation:** api-design.md:358 already correctly specified "Node not locked (unless toggling lock)"
- **Implementation:** Check `set(request.data.keys()) == {"is_locked"}` to detect lock-toggle-only requests
- **Validation:** Mixed updates (is_locked + other fields) on locked nodes still rejected with 403

---

## Validation

**All changes validated against:**
1. ✅ Progress file (`.ralph/archive/m5-board-advanced/progress.txt`) — US-007 lines 112-122
2. ✅ QA report (`docs/08-qa/qa-m5-board-advanced.md`) — T-3.8.02 verified `@board[uuid]` format
3. ✅ API design doc (`docs/02-architecture/api-design.md`) — line 1287 specifies `@board[<node_id>]` as canonical format
4. ✅ Test matrix (`docs/04-test-architecture/test-matrix.md`) — lines 127-129, 262 already use `@board[uuid]`
5. ✅ M4 QA report (`docs/08-qa/qa-m4-board-core.md`) — line 58, 162 already verified `@board[uuid]` in M4

**Spec consistency check:**
- ✅ requirements/features.md F-3.8 — does not specify exact format, delegates to design
- ✅ api-design.md — authoritative source, correctly specifies `@board[<node_id>]`
- ✅ milestone-5.md — NOW matches api-design.md (after reconciliation)
- ✅ test-matrix.md — already correct
- ✅ M4 and M5 QA reports — already correct

---

## Notes

**Why this reconciliation was so clean:**

1. **Tight spec-to-implementation alignment:** Ralph followed the architecture and design docs closely
2. **API design doc was authoritative:** When milestone text conflicted with API design, the API design was correct
3. **M4 already verified the pattern:** The `@board[uuid]` format was implemented and QA-verified in M4, so M5 inherited a correct pattern
4. **Progress file clarity:** Ralph's learnings section documented implementation discoveries clearly, making it easy to distinguish patterns from deviations
5. **No scope creep:** Ralph implemented exactly what was specified, no feature additions or "improvements"

**Lessons for future milestones:**

- Milestone planning docs can have placeholder text that doesn't match detailed specs — always defer to api-design.md as authoritative
- Implementation pattern discoveries (library API quirks, test patterns) are valuable but should stay in progress files and team knowledge bases, not specs
- A bugfix that implements already-specified behavior is not a deviation — it's a correction
