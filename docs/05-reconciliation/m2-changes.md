# Milestone 2 Spec Reconciliation

## Summary
- **Milestone:** M2 — Landing Page & Idea CRUD
- **Date:** 2026-03-09
- **Total deviations found:** 2
- **Auto-applied (SMALL TECHNICAL):** 0
- **Applied with flag (FEATURE DESIGN):** 0
- **Applied with flag (LARGE TECHNICAL):** 1
- **Cannot fix (outside docs/ scope):** 1

---

## Changes Applied

### LARGE TECHNICAL (Applied — Flagged for Review)

| # | Deviation | Document Updated | Change | Reason |
|---|-----------|-----------------|--------|--------|
| D-001 | Gateway service has duplicate Django models for core-owned tables | `docs/02-architecture/data-model.md`, `docs/02-architecture/project-structure.md` | Documented the cross-service model sharing pattern: Gateway service creates mirror Django models pointing to Core-owned tables via `db_table` | Microservice isolation — Gateway and Core are separate Django projects that cannot import each other's models. This is the correct implementation but was not explicitly documented in the architecture. |

### CANNOT FIX (Outside docs/ Scope)

| # | Deviation | File | Reason Cannot Fix |
|---|-----------|------|-------------------|
| D-002 | PRD passes field not updated for US-006, US-007, US-008 | `tasks/prd-m2.json` | File is outside docs/ directory. Spec reconciler is restricted to docs-only modifications per pipeline design. This is a Ralph bookkeeping error — all three stories are fully implemented and passing all tests. |

---

## Documents Modified

### docs/02-architecture/data-model.md
- **Section modified:** Table ownership notes at top of document
- **Change:** Added explicit documentation of the Gateway mirror model pattern
- **Rationale:** The spec stated Core owns these tables but didn't explain how Gateway accesses them without code sharing

### docs/02-architecture/project-structure.md
- **Section modified:** § Database Strategy (line ~30-50)
- **Change:** Added subsection documenting Django model sharing pattern across services
- **Rationale:** Critical architecture pattern that was implicit in implementation but not documented

---

## Impact on Future Milestones

**M3-M15 (All remaining milestones):** Any milestone that requires Gateway to expose REST endpoints for Core-owned tables will follow the same pattern:
1. Core service owns the table and manages migrations in production
2. Gateway service creates a mirror Django model with matching `db_table` attribute
3. Gateway uses its mirror model for DRF serializers and ORM queries
4. Both services connect to the same PostgreSQL database

**Specific impacts:**
- **M3 (Workspace Chat)**: Gateway will need mirror models for board nodes, connections
- **M4-M5 (Board Editor)**: Already covered by M3 mirror models
- **M8 (Collaboration)**: Gateway already has CollaborationInvitation mirror (created in M2)
- **M10 (Review)**: Gateway will need mirror models for ReviewAssignment, ReviewTimelineEntry
- **M12 (Notifications)**: No impact (notifications table is Gateway-owned)
- **M15 (Admin)**: Gateway will need mirror models for AdminParameter, MonitoringAlertConfig

---

## Detailed Deviation Analysis

### D-001: Gateway Service Duplicate Django Models

**Discovery source:**
- `.ralph/archive/m2-landing/progress.txt` lines 373-374 (US-001)
- `.ralph/archive/m2-landing/progress.txt` lines 393-394 (US-002)
- `services/gateway/apps/ideas/models.py` (implementation evidence)
- `services/gateway/apps/collaboration/models.py` (implementation evidence)

**What the spec said:**
- `docs/02-architecture/data-model.md` § ideas: "Service Owner: core"
- `docs/02-architecture/data-model.md` § idea_collaborators: "Service Owner: core"
- `docs/02-architecture/data-model.md` § chat_messages: "Service Owner: core"
- `docs/02-architecture/data-model.md` § collaboration_invitations: "Service Owner: core"
- `docs/02-architecture/data-model.md` top note: "Each table is owned by one service. Only the owning service reads/writes that table directly."

**What was actually implemented:**
```python
# services/gateway/apps/ideas/models.py
class Idea(models.Model):
    # ... full model definition ...
    class Meta:
        db_table = "ideas"  # Points to Core's table

class IdeaCollaborator(models.Model):
    # ... full model definition ...
    class Meta:
        db_table = "idea_collaborators"  # Points to Core's table

class ChatMessage(models.Model):
    # ... full model definition ...
    class Meta:
        db_table = "chat_messages"  # Points to Core's table
```

```python
# services/gateway/apps/collaboration/models.py
class CollaborationInvitation(models.Model):
    # ... full model definition ...
    class Meta:
        db_table = "collaboration_invitations"  # Points to Core's table
```

**Why it changed:**
From progress.txt: "Gateway ideas app needs its own models for Idea, IdeaCollaborator, ChatMessage since it can't import from core service."

Root cause: Gateway and Core are separate Django projects (`services/gateway/gateway/` vs `services/core/core/`). Python imports don't cross service boundaries in the monorepo structure. Django REST Framework serializers require Django model classes for the ORM. Solution: Gateway creates mirror models with identical schemas pointing to the same database tables.

**Why this is correct:**
1. Maintains microservice isolation (no code coupling)
2. Both services connect to the same PostgreSQL instance
3. Core manages migrations (owns the table definition authority)
4. Gateway reads/writes via its mirror models using Django ORM
5. No data duplication — both models point to the same physical table via `db_table`

**Autonomy classification:** LARGE TECHNICAL
- Affects system architecture pattern
- Impacts database ownership model
- Creates precedent for all future Gateway endpoints accessing Core tables
- Changes mental model: "table ownership" means "migration ownership", not "exclusive model definition"

**Upstream docs affected:**
1. `docs/02-architecture/data-model.md` — Update ownership note to clarify mirror model pattern
2. `docs/02-architecture/project-structure.md` — Add explicit section on Django model sharing

---

### D-002: PRD Passes Field Not Updated

**Discovery source:**
- `docs/08-qa/qa-m2-landing.md` lines 61-67 (DEV-001)
- `tasks/prd-m2.json` lines 247, 295, 339 (US-006, US-007, US-008 have `"passes": false`)

**What the spec said:**
Per `.ralph/CLAUDE.md` Ralph agent instructions:
> Update `.ralph/prd.json` to set `"passes": true` for the completed story.

**What was actually implemented:**
Ralph completed US-006, US-007, US-008 successfully (all tests passing, all acceptance criteria met) but did not update the PRD passes field.

**Why it changed:**
Human error in the Ralph agent execution loop — the agent finished the stories but skipped the PRD update step.

**Why this cannot be fixed by Spec Reconciler:**
Per pipeline constraints: "You may ONLY create or modify files under the docs/ directory. Do NOT modify source code, test files, configuration files, or any file outside docs/."

The PRD file is at `tasks/prd-m2.json` (not in docs/), so it is outside the Spec Reconciler's modification scope.

**Recommended action:**
Manual correction by human operator or pipeline script:
```json
# tasks/prd-m2.json
{
  "id": "US-006",
  "passes": true  // Change false → true
}
{
  "id": "US-007",
  "passes": true  // Change false → true
}
{
  "id": "US-008",
  "passes": true  // Change false → true
}
```

**Autonomy classification:** SMALL TECHNICAL
- Pure bookkeeping correction
- No code or behavior impact
- Implementation is already complete and passing

---

## Verification Checklist

- [x] All deviations from progress.txt reviewed
- [x] All deviations from QA report reviewed
- [x] Deviations categorized by autonomy level
- [x] LARGE TECHNICAL changes flagged prominently
- [x] Documents updated with corrections
- [x] Changelog includes rationale for each change
- [x] Impact on future milestones assessed
- [x] Files outside docs/ scope identified and documented

---

## Notes for Next Reconciliation (M3)

1. **Watch for:** Gateway mirror models for board_nodes, board_connections when M3 exposes board API endpoints
2. **Pattern confirmation:** If M3 follows the same mirror model pattern, this confirms it as a stable architecture decision (not a one-off deviation)
3. **Migration coordination:** Monitor for any migration conflicts if Core and Gateway both try to modify the same table schema
