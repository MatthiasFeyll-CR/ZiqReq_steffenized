# Milestone 21 Spec Reconciliation — Document View, PDF Generation & Final Polish

## Summary
- **Milestone:** M21 — polish-final
- **Date:** 2026-03-17
- **Total deviations found:** 21
- **Auto-applied (SMALL TECHNICAL):** 4
- **Applied with changelog flag (FEATURE DESIGN):** 8
- **Applied with changelog flag (LARGE TECHNICAL):** 9
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

Minor technical corrections with no behavioral or design impact.

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| D-001 | Proto stubs location | `docs/02-architecture/project-structure.md` | Corrected: stubs generated into `proto/` directly, not `proto/generated/` subdirectory |
| D-002 | PDF preview endpoint path | `docs/02-architecture/api-design.md` | `/brd/preview-pdf` → `/brd/pdf/preview` |
| D-003 | CSS file references | `docs/02-architecture/project-structure.md` | Deleted: `brd_styles.css`. Created: `requirements_styles.css` (Gotham font, Commerz Real branding) |
| D-004 | Test ID updates | `docs/03-design/component-specs.md` | `step-document` → `step-structure`, `step-brainstorm` → `step-define`, `go-back-to-brainstorm` → `go-back-to-define` |

---

### FEATURE DESIGN (Applied — flagged for review)

Changes that affect user-visible behavior, UI structure, or feature semantics.

| # | Deviation | Document Updated | Change | Impact |
|---|-----------|-----------------|--------|--------|
| D-005 | ProcessStep type enum | `docs/01-requirements/features.md`, `docs/03-design/component-specs.md`, `docs/03-design/page-layouts.md` | ProcessStep type changed from `"brainstorm" \| "document" \| "review"` to `"define" \| "structure" \| "review"`. Reflects refactoring from brainstorming tool to requirements assembly platform. | **FEATURE DESIGN** — User flow terminology changed. Process labels updated throughout UI. |
| D-006 | Process step props renamed | `docs/03-design/component-specs.md` | ProcessStepper props: `canAccessDocument` → `canAccessStructure`, `documentGateMessage` → `structureGateMessage` | **FEATURE DESIGN** — Component API aligned with new step names. |
| D-007 | Translation keys renamed | `docs/03-design/component-specs.md` | `process.brainstorm` → `process.define`, `process.document` → `process.structure`, `review.backToBrainstorm` → `review.backToDefine` | **FEATURE DESIGN** — i18n keys updated for new terminology (de/en translations updated). |
| D-008 | URL params updated | `docs/03-design/interactions.md`, `docs/01-requirements/features.md` | `?step=define` activates define step (was `?step=brainstorm` in old flow, though brainstorm was default and rarely used in URLs) | **FEATURE DESIGN** — URL routing updated to reflect new step names. |
| D-009 | Landing page section titles | `docs/03-design/page-layouts.md` | Section titles: "My Projects", "Collaborating", "Pending Invitations", "Trash" (previously: "MY PROJECTS", "COLLABORATING PROJECTS", "INVITATIONS", "TRASH") | **FEATURE DESIGN** — Improved readability with sentence-case headers. |
| D-010 | ProjectCard type badge added | `docs/03-design/component-specs.md`, `docs/03-design/page-layouts.md` | Optional `projectType` prop displays "Software" or "Non-Software" badge on ProjectCard | **FEATURE DESIGN** — Visual indicator for project type added to all project cards. |
| D-011 | New component: StructureStepView | `docs/03-design/page-layouts.md`, `docs/02-architecture/project-structure.md` | Replaces DocumentView.tsx. 60/40 split layout: RequirementsPanel (left, 60%) + PDFPreviewPanel (right, 40%). Includes Generate/Regenerate button, gaps toggle, readiness indicators, lock/unlock, Submit for Review. | **FEATURE DESIGN** — New dedicated view for Structure step. Separates requirements editing from chat. |
| D-012 | New component: PDFPreviewPanel | `docs/03-design/component-specs.md`, `docs/03-design/page-layouts.md` | PDF preview with download button embedded in Structure step. Uses `<object>` tag with `/api/projects/:id/requirements/pdf/preview` endpoint. | **FEATURE DESIGN** — In-line PDF preview for requirements document during assembly (before submit). |

---

### LARGE TECHNICAL (Applied — flagged for review)

Changes that affect system architecture, data models, or service boundaries.

| # | Deviation | Document Updated | Change | Impact |
|---|-----------|-----------------|--------|--------|
| D-013 | Gateway app namespace rename | `docs/02-architecture/project-structure.md`, `docs/02-architecture/api-design.md` | `services/gateway/apps/brd` → `services/gateway/apps/requirements_document`. All BRD API endpoints remain under `/api/projects/:id/requirements/` (no breaking changes to frontend). | **LARGE TECHNICAL** — Internal service app renamed for clarity. API routes unchanged (backward compatible). |
| D-014 | BrdDraft backward-compat alias | `docs/02-architecture/data-model.md` | Added note: `BrdDraft = RequirementsDocumentDraft` alias retained in gateway models for backward compatibility with review module and internal references. | **LARGE TECHNICAL** — Alias pattern documented. Physical table name `brd_drafts` not renamed (migration complexity). |
| D-015 | BrdVersion model schema change | `docs/02-architecture/data-model.md` | `requirements_document_versions` (table: `brd_versions`) schema changed: replaced 6 flat section columns (overview, background, objectives, scope, constraints, success_criteria) with hierarchical structure (title, short_description, structure JSONB). | **LARGE TECHNICAL** — Breaking schema change. Old BRD flat sections replaced with hierarchical JSON structure for type-specific rendering (Epics/Stories vs Milestones/Packages). |
| D-016 | RequirementsDocumentDraft schema change | `docs/02-architecture/data-model.md` | `requirements_document_drafts` (table: `brd_drafts`) schema: `structure` is JSONB list (hierarchical), `item_locks` is JSONB dict (replaces `section_locks`). | **LARGE TECHNICAL** — Data model now supports hierarchical requirements with per-item locking instead of per-section locking. |
| D-017 | PDF rendering architecture | `docs/02-architecture/project-structure.md` | PDF service uses type-specific rendering: `_render_epic()` for Software projects (Epics → User Stories), `_render_milestone()` for Non-Software projects (Milestones → Work Packages). | **LARGE TECHNICAL** — PDF generation logic branched by project type. |
| D-018 | ProjectListItem API response | `docs/02-architecture/api-design.md` | Added `project_type` field to `/api/projects` response (ProjectListItem interface). Backend now includes project_type in list queries. | **LARGE TECHNICAL** — API response expanded to support frontend type filtering and badge display. |
| D-019 | Database table name policy | `docs/02-architecture/data-model.md` | Documented: `brd_drafts` table name not renamed (backward compat constraint). Gateway uses unmanaged mirror model, AI service uses raw SQL against physical table. Full rename would require cross-service migration. | **LARGE TECHNICAL** — Pragmatic decision: internal DB table names unchanged, application-layer aliases used instead. |
| D-020 | DocumentView.tsx deleted | `docs/03-design/page-layouts.md`, `docs/02-architecture/project-structure.md` | Removed DocumentView.tsx component (no longer referenced). Replaced by StructureStepView.tsx. | **LARGE TECHNICAL** — Component deleted. Old "document" step view replaced with new "structure" step architecture. |
| D-021 | Orphan component policy | `docs/02-architecture/project-structure.md` | Documented orphan components: ReviewTab.tsx, BRDSectionEditor.tsx, `frontend/src/api/brd.ts` (old BRD API client) exist but are only imported by test files, not production code paths. Retained for test coverage of legacy UI behavior. | **LARGE TECHNICAL** — Orphan components from old BRD flow documented. Future cleanup story could remove these + associated tests. |

---

## Documents Modified

All changes applied to `docs/` directory only (no source code modified by Spec Reconciler).

| Document | Changes Applied |
|----------|----------------|
| `docs/01-requirements/features.md` | FA-1.1 updated: Process flow now Define → Structure → Review |
| `docs/02-architecture/project-structure.md` | Proto stubs location, PDF rendering architecture, CSS file references, StructureStepView added, orphan components documented, app namespace rename |
| `docs/02-architecture/data-model.md` | BrdVersion schema change, RequirementsDocumentDraft schema change, BrdDraft alias, table name policy |
| `docs/02-architecture/api-design.md` | PDF preview endpoint path, ProjectListItem project_type field, app namespace rename |
| `docs/03-design/component-specs.md` | ProcessStepper props renamed, translation keys renamed, ProjectCard type badge, PDFPreviewPanel added |
| `docs/03-design/page-layouts.md` | Landing page section titles, StructureStepView layout, DocumentView removed |
| `docs/03-design/interactions.md` | URL params for step navigation |

---

## Impact on Future Milestones

**None.** M21 was the final polish milestone. All future milestones will start from this corrected spec baseline.

---

## Deviations Not Found (QA Report References)

The QA report documented two additional deviations (DEV-001, DEV-002) that are **implementation-level details** rather than spec deviations:

### DEV-001: brd_draft/BrdDraft references remain in internal code
- **Reason:** Not a spec deviation. The spec **never mandated** complete removal of internal database table names or backward-compat aliases. This is an internal implementation detail for migration compatibility.
- **Spec alignment:** Documented as D-014 and D-019 above. The spec now explicitly notes the backward-compat alias pattern and table name policy.

### DEV-002: Orphan components from old BRD flow still exist
- **Reason:** Not a spec deviation. The spec **never mandated** deletion of orphan components. US-005 AC was "orphan check" (identify orphans), not "delete all orphans."
- **Spec alignment:** Documented as D-021 above. Orphans are test-only imports (no production code paths) and are intentionally retained for test coverage.

---

## Notes

1. **All changes are corrections to spec, not changes to implementation.** The implementation (M21 code) is verified correct by QA. The spec is updated to match reality.

2. **FEATURE DESIGN and LARGE TECHNICAL flags** are for visibility, not approval gates. M21 QA has passed. These flags help readers understand the scope of changes when reviewing the spec.

3. **No cascading spec changes required.** All referenced documents have been checked and updated where needed.

4. **ProcessStep rename (brainstorm→define, document→structure)** is the most visible change. This reflects the broader platform refactoring from "AI brainstorming tool" to "requirements assembly platform."

5. **Database table names (`brd_drafts`, `brd_versions`)** remain unchanged from legacy naming. Application code uses modern names (`RequirementsDocumentDraft`, `requirements_document` app). This is a pragmatic decision to avoid complex cross-service migrations.

6. **Orphan components** (ReviewTab, BRDSectionEditor) are from the old flat BRD editing flow. They exist only in test imports and could be removed in a future cleanup story along with their tests.

---

**Reconciliation complete.** All upstream spec documents now accurately reflect the M21 implementation.
