# Milestone 21: Document View, PDF Generation & Final Polish

## Overview
- **Execution order:** 21 (runs after M20)
- **Estimated stories:** 5
- **Dependencies:** M20
- **MVP:** Yes

## Purpose
Replace the old Document step with the new Structure step, update PDF generation for type-specific templates, update the process stepper and workspace flow, refresh the landing page, and perform a comprehensive final cleanup.

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| R-5.1 | New Document/Structure step — Frontend | Critical | REFACTORING_PLAN.md Phase 5 |
| R-5.2 | PDF generation — Type-specific templates | Critical | REFACTORING_PLAN.md Phase 5 |
| R-6.1 | Update process stepper & workspace flow | High | REFACTORING_PLAN.md Phase 6 |
| R-6.2 | Landing page & project list updates | High | REFACTORING_PLAN.md Phase 6 |
| R-6.3 | Final cleanup & orphan check | High | REFACTORING_PLAN.md Phase 6 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| (No new tables — uses requirements_document_drafts/versions from M19) | — | — | — |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| PDF generation (gRPC) | RPC | Updated to accept project_type + structure JSON | Internal | Story 5.2 |
| PDF preview/download | GET | Updated for new structure | Auth | Story 5.2 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| DocumentView | REMOVE (replace with Structure step) | Story 5.1 |
| Structure step view | CREATE | Story 5.1 |
| ProcessStepper (updated) | MODIFY | Story 6.1 |
| ProjectWorkspace (updated) | MODIFY | Story 6.1 |
| LandingPage (updated) | MODIFY | Story 6.2 |
| HeroSection (updated) | MODIFY | Story 6.2 |
| ProjectCard (updated) | MODIFY | Story 6.2 |

## Story Outline (Suggested Order)
1. **[Frontend] New Structure step** — Replace DocumentView with new Structure step content: full-width RequirementsPanel in editing mode + PDF preview sidebar. Add Generate/Regenerate button, "Allow information gaps" toggle, readiness indicators per item, lock/unlock individual items, submit button to proceed to review.
2. **[Backend+Frontend] PDF generation — Type-specific templates** — Update `services/pdf/generator/builder.py` to accept project_type and structured JSON. Software template: "Software Requirements Document" header, epics with user story tables (ID, Title, Description, AC, Priority). Non-software template: "Project Requirements Document" header, milestones with work package tables (ID, Title, Description, Deliverables, Dependencies). Update CSS template, proto/pdf.proto, gateway brd views (rename to requirements_document). Update PDF preview rendering.
3. **[Frontend] Update process stepper & workspace flow** — Update ProcessStepper: step names "Define", "Structure", "Review". Update step type to "define" | "structure" | "review". Update ProjectWorkspace: define step = chat + requirements panel, structure step = full-width editor + PDF preview, review step = ReviewSection. Update gate logic (canAccessStructure, canAccessReview). Update URL params.
4. **[Frontend] Landing page & project list updates** — Update section titles ("My Projects", "Collaborating", etc.). HeroSection shows heading + "New Project" button (opens NewProjectModal). ProjectCard shows project type badge. Update filter hooks.
5. **[Full-stack] Final cleanup & orphan check** — Run comprehensive grep searches for orphaned references (idea, brainstorm, board_agent, BoardNode, xyflow, merge_synth, keyword_agent, similarity, brd_draft, BrdDraft). Verify all services start, frontend builds, tests pass. Remove unused imports, commented-out code, unused translation keys, unused CSS. Update docs to reflect new terminology.

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | New Structure step | ~12,000 | Design specs, component specs | ~5 files | Medium | Medium — reuses RequirementsPanel from M19 |
| 2 | PDF generation | ~10,000 | Architecture, PDF specs | ~8 files | Medium | Medium — template redesign |
| 3 | Process stepper update | ~8,000 | Requirements, design | ~5 files | Medium | Low — mostly string/logic updates |
| 4 | Landing page updates | ~6,000 | Design specs | ~5 files | Low | Low — cosmetic changes |
| 5 | Final cleanup | ~5,000 | All specs | ~10+ files | Low | Low — verification and cleanup |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~41,000
- **Cumulative domain size:** Medium (touches many areas but shallowly)
- **Information loss risk:** Low (score: 3)
- **Context saturation risk:** Low

## Milestone Acceptance Criteria
- [ ] Structure step shows full-width requirements editor + PDF preview sidebar
- [ ] Generate/Regenerate, lock/unlock, readiness indicators work in Structure step
- [ ] PDF generation produces correct document for software projects (Epics/Stories format)
- [ ] PDF generation produces correct document for non-software projects (Milestones/Packages format)
- [ ] Process stepper shows "Define -> Structure -> Review" with correct gate logic
- [ ] Define step renders chat + requirements panel, Structure step renders editor + PDF preview
- [ ] Landing page shows "My Projects" sections with project type badges
- [ ] New Project button opens creation modal (from M19)
- [ ] grep orphan check passes — no leftover references to old features
- [ ] All services start without errors
- [ ] Frontend builds without errors
- [ ] TypeScript typecheck passes
- [ ] Review workflow functions end-to-end
- [ ] Multi-user real-time sync works
- [ ] Admin panel loads all three context buckets
- [ ] No regressions on previous milestones

## Notes
- Story 1 reuses the RequirementsPanel built in M19 Story 3.3 — just changes the layout context.
- Story 2 requires renaming the gateway brd app to requirements_document.
- Story 5 is a comprehensive verification — run it last as a final gate before release.
- After this milestone, the full refactoring is complete.
