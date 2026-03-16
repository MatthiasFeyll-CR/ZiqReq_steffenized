# Milestone 19: Project Types & Structured Requirements

## Overview
- **Execution order:** 19 (runs after M18)
- **Estimated stories:** 4
- **Dependencies:** M18
- **MVP:** Yes

## Purpose
Add project type distinction (Software vs Non-Software) at creation time, replace the flat BRD model with hierarchical requirements documents (Epics/Stories or Milestones/Packages), build the structured requirements panel UI, and add per-type admin context buckets.

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| R-3.1 | Project type selection — Creation flow | Critical | REFACTORING_PLAN.md Phase 3 |
| R-3.2 | Structured requirements data model — Backend | Critical | REFACTORING_PLAN.md Phase 3 |
| R-3.3 | Structured requirements panel — Frontend | Critical | REFACTORING_PLAN.md Phase 3 |
| R-3.4 | Admin context buckets per project type | High | REFACTORING_PLAN.md Phase 3 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| requirements_document_drafts | CREATE | id, project_id, title, short_description, structure (JSON), item_locks (JSON), allow_information_gaps, readiness_evaluation (JSON) | Story 3.2 |
| requirements_document_versions | CREATE | id, project_id, version_number, title, short_description, structure (JSON), pdf_file_path | Story 3.2 |
| brd_drafts | DROP TABLE (after migration) | — | Story 3.2 |
| brd_versions | DROP TABLE (after migration) | — | Story 3.2 |
| facilitator_context_bucket | ADD COLUMN | context_type (global/software/non_software) | Story 3.4 |
| context_agent_bucket | ADD COLUMN | context_type (global/software/non_software) | Story 3.4 |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/projects/ | POST | Accept project_type, no first_message required | Auth | Story 3.1 |
| GET /api/projects/:id/requirements/ | GET | Get current requirements draft | Auth | Story 3.2 |
| PATCH /api/projects/:id/requirements/ | PATCH | Update top-level fields | Auth | Story 3.2 |
| POST /api/projects/:id/requirements/items | POST | Add epic/milestone | Auth | Story 3.2 |
| PATCH /api/projects/:id/requirements/items/:item_id | PATCH | Update epic/milestone | Auth | Story 3.2 |
| DELETE /api/projects/:id/requirements/items/:item_id | DELETE | Delete epic/milestone | Auth | Story 3.2 |
| POST /api/projects/:id/requirements/items/:item_id/children | POST | Add story/package | Auth | Story 3.2 |
| PATCH /api/projects/:id/requirements/items/:item_id/children/:child_id | PATCH | Update story/package | Auth | Story 3.2 |
| DELETE /api/projects/:id/requirements/items/:item_id/children/:child_id | DELETE | Delete story/package | Auth | Story 3.2 |
| POST /api/projects/:id/requirements/reorder | POST | Reorder items | Auth | Story 3.2 |
| POST /api/projects/:id/requirements/generate | POST | Trigger AI generation | Auth | Story 3.2 |
| GET/PATCH /api/admin/ai-context/facilitator?type= | GET/PATCH | Per-type facilitator context | Admin | Story 3.4 |
| GET/PATCH /api/admin/ai-context/company?type= | GET/PATCH | Per-type company context | Admin | Story 3.4 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| NewProjectModal | CREATE | Story 3.1 |
| HeroSection (updated) | MODIFY | Story 3.1 |
| RequirementsPanel | CREATE | Story 3.3 |
| EpicCard / MilestoneCard | CREATE | Story 3.3 |
| UserStoryCard / WorkPackageCard | CREATE | Story 3.3 |
| RequirementsItemEditor | CREATE | Story 3.3 |
| WorkspaceLayout (updated) | MODIFY | Story 3.3 |
| AIContextTab (updated) | MODIFY | Story 3.4 |

## Story Outline (Suggested Order)
1. **[Backend+Frontend] Project type selection** — Update createProject API to accept project_type (required), remove first_message requirement. Remove HeroSection textarea, create NewProjectModal with type selection cards (Software/Non-Software). Update use-create-project hook to accept projectType parameter.
2. **[Backend] Structured requirements data model** — Create RequirementsDocumentDraft and RequirementsDocumentVersion models. Create migration (new tables, migrate BRD data, drop old tables). Build serializers, validators (enforce correct structure per project type). Implement all CRUD endpoints for requirements items. Add WebSocket events (requirements_updated, requirements_generating, requirements_ready). Add gRPC RPCs for AI access.
3. **[Frontend] Structured requirements panel** — Build RequirementsPanel container (title, description, contributors, items list). Build EpicCard/MilestoneCard (accordion, inline edit, drag handle). Build UserStoryCard/WorkPackageCard (compact card, inline edit, drag-to-reorder). Implement @dnd-kit for drag-and-drop reordering. Wire WebSocket for real-time sync. Update WorkspaceLayout to chat + requirements panel split (40/60).
4. **[Backend+Frontend] Admin context buckets per type** — Add context_type to facilitator/company context bucket models. Seed 3 rows per bucket (global, software, non_software). Update API endpoints with type query parameter. Update AIContextTab with segmented control (Global/Software/Non-Software). Update embedding pipeline to tag chunks by type. Update context retrieval to combine global + type-specific.

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Project type selection | ~8,000 | Requirements, component specs | ~10 files | Medium | Low |
| 2 | Structured requirements data model | ~18,000 | Data model, API design | ~15 files | High | High — new data model, many endpoints, migration |
| 3 | Structured requirements panel | ~20,000 | Component specs, design | ~12 new files | High | High — complex UI with DnD, real-time sync |
| 4 | Admin context buckets | ~10,000 | Architecture, AI specs | ~10 files | Medium | Medium — touches embedding pipeline |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~56,000
- **Cumulative domain size:** Large (new data model + complex UI + admin changes)
- **Information loss risk:** Medium (score: 6)
- **Context saturation risk:** Medium

## Milestone Acceptance Criteria
- [ ] New project creation modal with type selection works
- [ ] RequirementsDocumentDraft/Version tables created, old BRD tables migrated and dropped
- [ ] All CRUD endpoints for requirements items functional
- [ ] Structure validation enforces correct schema per project type
- [ ] Requirements panel renders in workspace with chat (40/60 split)
- [ ] Drag-and-drop reordering works for items and children
- [ ] WebSocket real-time sync works for requirements changes
- [ ] Admin panel shows 3 context type tabs (Global/Software/Non-Software)
- [ ] Context retrieval combines global + type-specific chunks
- [ ] TypeScript typecheck passes
- [ ] No regressions on previous milestones

## Notes
- Story 2 is the heaviest — creates the foundational data model that Stories 3 and 4 depend on. Must be solid.
- Story 3 is the most complex UI story — introduces drag-and-drop and real-time sync for the requirements panel.
- The DnD library (@dnd-kit) needs to be added as a new dependency.
- Multi-user conflict resolution uses last-write-wins with toast notification.
- The "generate" endpoint (POST requirements/generate) is wired but the AI implementation comes in M20.
