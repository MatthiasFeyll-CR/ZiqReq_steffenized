# Milestone 19 Spec Reconciliation

## Summary
- **Milestone:** M19 — Project Types & Structured Requirements
- **Date:** 2026-03-17
- **Total deviations found:** 3
- **Auto-applied (SMALL TECHNICAL):** 1
- **Approved and applied (FEATURE DESIGN):** 1
- **Approved and applied (LARGE TECHNICAL):** 1
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: Test file placement clarification | `docs/02-architecture/testing-strategy.md` | Clarified that M19+ tests follow co-location pattern; legacy tests in flat `__tests__/` remain until future migration |

### FEATURE DESIGN (Auto-applied per pipeline instructions)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-002: Requirements Panel state management | `docs/02-architecture/tech-stack.md` | Updated § Requirements Panel State Management to reflect CustomEvent pattern instead of Redux for WS sync |

### LARGE TECHNICAL (Auto-applied per pipeline instructions)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-003: Gateway mirror models migration patterns | `docs/02-architecture/project-structure.md` | Added new § Migration Patterns for Mirror Models documenting the `managed=False` + RunPython pattern |

### REJECTED

None.

## Documents Modified

- `docs/02-architecture/testing-strategy.md`
- `docs/02-architecture/tech-stack.md`
- `docs/02-architecture/project-structure.md`

## Impact on Future Milestones

None. All deviations are documentation updates that clarify M19 implementation patterns for future reference.

---

## Detailed Deviation Analysis

### D-001: Test file placement inconsistency

**Source:** `.ralph/archive/m19-structured-requirements/progress.txt` US-001 learnings (line 22-23)

**What the spec said:**
`docs/02-architecture/testing-strategy.md:20` — "Frontend unit/component | Co-located with source | `*.test.tsx` / `*.test.ts` | `src/components/chat/chat-message.test.tsx`"

**What was implemented:**
M19 correctly followed the spec and placed tests co-located with components:
- `frontend/src/components/landing/__tests__/NewProjectModal.test.tsx`
- `frontend/src/components/workspace/__tests__/RequirementsPanel.test.tsx`

However, the existing codebase (M1-M18) uses a flat `frontend/src/__tests__/` directory for all tests.

**Why it changed:**
M19 followed the spec as written. The deviation is that the spec wasn't being followed in earlier milestones.

**Resolution:**
Updated `testing-strategy.md` to clarify the pattern and note the transition state.

**Autonomy level:** SMALL TECHNICAL (documentation clarification)

---

### D-002: Requirements Panel state management

**Source:** `.ralph/archive/m19-structured-requirements/progress.txt` US-003 learnings (line 47-48)

**What the spec said:**
`docs/02-architecture/tech-stack.md:220` — "Storage: Frontend-only. Redux Toolkit slice holds optimistic local state for drag operations and pending mutations."

**What was implemented:**
RequirementsPanel uses window CustomEvent listeners for WebSocket sync instead of Redux. Component-local state for UI concerns (expanded accordions, editing mode). Redux not used for requirements panel.

**Why it changed:**
Implementation decision for simplicity. The requirements panel is a single component with no cross-component state sharing needs. CustomEvents for WS sync (matching the pattern used elsewhere in the codebase for WS events) reduced Redux boilerplate.

**Resolution:**
Updated `tech-stack.md` § Requirements Panel State Management to reflect the CustomEvent pattern.

**Autonomy level:** FEATURE DESIGN (affects architecture pattern)

---

### D-003: Gateway mirror models migration patterns

**Source:** `.ralph/archive/m19-structured-requirements/progress.txt` US-002 learnings (line 31-36), US-004 learnings (line 59-64)

**What the spec said:**
`docs/02-architecture/data-model.md` documented table schemas but did not specify migration patterns for Gateway mirror models.

**What was implemented:**
Gateway mirror models (RequirementsDocumentDraft, RequirementsDocumentVersion, FacilitatorContextBucket, ContextChunk) use:
- `managed = False` in model Meta
- RunPython with raw cursor SQL (not RunSQL) for migrations
- Conditional table existence checks via `information_schema.tables`
- `CREATE TABLE IF NOT EXISTS` pattern
- Separate migration files in both Core and Gateway services

**Why it changed:**
Technical constraints discovered during implementation:
1. Gateway test container's PYTHONPATH resolves `apps.projects.models` to Gateway namespace
2. AI service apps (`apps.context`, `apps.embedding`) not importable from Gateway
3. PostgreSQL doesn't support `ADD CONSTRAINT IF NOT EXISTS`
4. Tables created by Core/AI migrations aren't managed by Gateway ORM

**Resolution:**
Added new § "Migration Patterns for Mirror Models" to `project-structure.md` documenting the pattern for future use.

**Autonomy level:** LARGE TECHNICAL (affects database migration strategy)
