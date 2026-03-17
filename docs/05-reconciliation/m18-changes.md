# Milestone 18 Spec Reconciliation

## Summary
- **Milestone:** M18 — Rename Idea to Project
- **Date:** 2026-03-17
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 1
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: Process step terminology ambiguity | `docs/05-milestones/milestone-18.md` | Clarified acceptance criteria line 76: "Process steps renamed" → "Process step labels renamed" with note that internal identifiers remain unchanged until M21 |

**Diff:**
```diff
- [ ] Process steps renamed: Define, Structure, Review
+ [ ] Process step labels renamed: Define, Structure, Review (internal identifiers remain "brainstorm"/"document"/"review" — to be renamed in M21)
```

**Rationale:** The acceptance criteria was ambiguous. Story 4 (line 51) correctly specifies "Update process step **labels**" but the acceptance criteria omitted the word "labels", implying a full rename. The implementation correctly renamed only the user-facing labels via translation keys (`process.brainstorm="Define"`, `process.document="Structure"`, `process.review="Review"`). Internal TypeScript identifiers (`type ProcessStep = "brainstorm" | "document" | "review"`) were intentionally left unchanged because:
- They are used in URL query parameters (`?step=brainstorm`)
- They are used in `data-testid` attributes for E2E tests
- They appear in 40+ references across the codebase
- Milestone 21 is planned to rename the internal step types to `"define"` | `"structure"` | `"review"`

The updated acceptance criteria now matches the story scope and implementation.

### FEATURE DESIGN (Human-approved)

_None_

### LARGE TECHNICAL (Human-approved)

_None_

### REJECTED

_None_

## Learnings from Implementation (Not Requiring Spec Updates)

### L-001: Table naming convention (brd_* vs requirements_document_*)
**Source:** Progress.txt US-001

The PRD for M18 referenced tables as "requirements_document_drafts" and "requirements_document_versions", but the actual database tables are named "brd_drafts" and "brd_versions".

**Why no spec update is needed:**
- This is intentional forward-looking documentation
- Architecture docs (data-model.md) describe the **target architecture** using final table names "requirements_document_drafts" and "requirements_document_versions"
- Milestone docs correctly reference the **current state** at each point in time
- M18 correctly kept table names as "brd_drafts" and "brd_versions" (only renamed `idea_id` columns to `project_id`)
- M19 will create/migrate to the new table names
- Both documentation styles are correct in their respective contexts

### L-002: No notification templates directory
**Source:** Progress.txt US-004

Implementation discovered that `services/notification/templates/` directory does not exist. Notification content is generated from translation files and event payloads, not server-side template files.

**Why no spec update is needed:**
- No spec document explicitly claimed this directory exists
- References to "email templates" in QA reports refer to email generation code (e.g., `similarity_events.py:296-310`), not template files
- The implementation pattern (code-generated HTML) is correct and matches the actual architecture

## Documents Modified

1. `docs/05-milestones/milestone-18.md` — Clarified acceptance criteria for process step label rename

## Impact on Future Milestones

### Milestone 21 (Requirements Document MVP)
The clarification in M18's acceptance criteria aligns with M21's planned work:
- M21 Story outline (line 46) states: "Update step type to 'define' | 'structure' | 'review'"
- This confirms M21 will rename the internal step identifiers that M18 intentionally left unchanged
- No changes to M21 scope needed — it already correctly plans to complete the internal identifier rename

## QA Deviation Cross-Reference

This reconciliation addresses QA report deviation:
- **DEV-001** (qa-m18-rename-project.md) — Internal code identifiers still use "brainstorm"/"document"/"review"
  - **Resolution:** Spec clarified that M18 scope was labels only; internal identifiers are M21 scope

## Verification

To verify the reconciliation is accurate:

```bash
# Confirm internal identifiers remain unchanged (expected)
grep -r "type ProcessStep" frontend/src/
# Output: "brainstorm" | "document" | "review" ✓

# Confirm user-facing labels use new terminology (expected)
grep "process.brainstorm" frontend/src/i18n/locales/en.json
# Output: "Define" ✓

# Confirm M21 plans to rename internal types
grep "define.*structure.*review" docs/05-milestones/milestone-21.md
# Output: step type to "define" | "structure" | "review" ✓
```

## Notes

- This was a small, surgical reconciliation — only 1 deviation from an otherwise highly successful milestone
- All 5 stories (US-001 through US-004 plus BF-001) passed QA with 614 Python tests and 341 Node tests passing
- The rename was comprehensive: 109 frontend files, all backend services, all proto files, all translations
- The only ambiguity was a missing word ("labels") in one acceptance criterion
