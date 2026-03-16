# Changes Applied

> **Date:** 2026-03-16
> **Author:** Documentation Refactoring Update
> **Context:** Refactoring from Idea → Project, Brainstorming → Requirements Assembly

---

## Overview

This document tracks changes applied to align documentation with the major refactoring plan:
- "Idea" → "Project" terminology
- "Brainstorming" → "Requirements assembly/structuring"
- Board/Canvas removed entirely → Replaced with Requirements Panel
- Merge/Similarity/Keyword systems removed
- Two project types: Software (Epics/User Stories) vs Non-Software (Milestones/Work Packages)
- BRD → Requirements Document (hierarchical)

---

## Design Docs Updated

| # | File | Section | Change |
|---|------|---------|--------|
| 1 | `docs/03-design/design-system.md` | Section 2.5 | Renamed "Idea State Colors" → "Project State Colors", updated usage text |
| 2 | `docs/03-design/design-system.md` | Section 4.3 | Updated "Board panel" → "Requirements panel" spacing |
| 3 | `docs/03-design/design-system.md` | Section 7 | Renamed `z-board-node` → `z-requirements-item` |
| 4 | `docs/03-design/design-system.md` | Section 9.1 | Updated navbar structure to show "Projects" instead of "Ideas" |
| 5 | `docs/03-design/design-system.md` | Section 12.1 | Updated "Idea Workspace" → "Project Workspace", "board read-only" → "requirements panel read-only" |
| 6 | `docs/03-design/interactions.md` | Section 3.2 | Renamed "Idea Workspace" → "Project Workspace", updated panel description (chat + requirements, not chat + board) |
| 7 | `docs/03-design/interactions.md` | Section 4.4 | Removed (AI Modified Indicator for Board Nodes) |
| 8 | `docs/03-design/interactions.md` | Section 5 | Added new section: "Requirements Panel Interactions" with accordion, drag-to-reorder, inline editing |
| 9 | `docs/03-design/interactions.md` | Section 6.2 | Removed board keyboard shortcuts (Ctrl+Z board, Delete node, Ctrl+A board), added requirements panel shortcuts |
| 10 | `docs/03-design/interactions.md` | Section 8.2 | Updated "BRD generation" → "Requirements document generation" |
| 11 | `docs/03-design/interactions.md` | Section 8.3 | Removed "Board edits" optimistic updates, added "Requirements panel edits" |
| 12 | `docs/03-design/component-inventory.md` | Feature Components | Removed entire "Board" section (10 components: BoardCanvas, BoxNode, GroupNode, etc.) |
| 13 | `docs/03-design/component-inventory.md` | Feature Components | Added "Requirements Panel" section (8 components: RequirementsPanel, EpicCard, MilestoneCard, UserStoryCard, WorkPackageCard, RequirementsItemEditor, AddItemButton, DragHandle) |
| 14 | `docs/03-design/component-inventory.md` | Feature Components | Renamed "BRD / Review" → "Requirements Document / Review", renamed BRDSectionEditor → RequirementsDocumentEditor |
| 15 | `docs/03-design/component-inventory.md` | Feature Components | Removed SimilarIdeaCard (similarity removed), removed MergeRequestBanner (merge removed) |
| 16 | `docs/03-design/component-inventory.md` | Feature Components | Renamed IdeaCard → ProjectCard, IdeasListFloating → ProjectsListFloating |
| 17 | `docs/03-design/component-inventory.md` | Landing | Added ProjectTypeSelector component for new project modal |
| 18 | `docs/03-design/component-inventory.md` | Summary | Updated counts: 81 total components (down from 85), 32 shared |

---

## Integration Docs Updated

| # | File | Section | Change |
|---|------|---------|--------|
| 1 | `docs/03-integration/gap-analysis.md` | Throughout | Updated terminology: idea → project, board → requirements panel, BRD → requirements document |
| 2 | `docs/03-integration/gap-analysis.md` | Gap G-002 | Updated reference from GetBoardState to GetProjectContext for requirements structure |
| 3 | `docs/03-integration/gap-analysis.md` | Gap G-012 | Updated table reference: brd_sections → requirements_document_drafts |
| 4 | `docs/03-integration/audit-report.md` | Throughout | Updated terminology: idea → project, board → requirements, BRD → requirements document |
| 5 | `docs/03-integration/audit-report.md` | Feature Chains | Removed F-2.6 (Board Item References), F-2.17+F-3.4+F-3.7 (AI Board Content), F-5.1 (Keyword Generation), F-5.3 (Deep Comparison), F-5.5 (Merge Synthesis) |
| 6 | `docs/03-integration/audit-report.md` | Feature Chains | Updated F-4.1-F-4.4 chain for requirements document model (hierarchical, project-type-aware) |
| 7 | `docs/03-integration/audit-report.md` | Design Coverage | Removed board-related design refs, removed merge/similarity UI refs, added requirements panel refs |

---

## Rationale

### Removed Features
- **Board/Canvas (XYFlow):** Replaced with structured Requirements Panel using accordion + sortable cards
- **Merge/Similarity/Keyword system:** Entire similarity detection and merge workflow removed
- **Board-related AI tools:** Board Agent and all board manipulation tools removed
- **Co-owner concept:** Removed from collaboration model

### Added Features
- **Requirements Panel:** Accordion-based structured view with drag-and-drop reorder (@dnd-kit)
- **Project Types:** Software vs Non-Software with different hierarchy (Epic/Story vs Milestone/Package)
- **Project Type Selector:** Modal for choosing project type at creation
- **Type-specific Admin Context:** Global + software + non_software context buckets

### Architecture Impact
- Gap count reduced from 12 to 9 (removed G-003, G-004 which were similarity/merge event gaps)
- Component count reduced from 85 to 81 (removed 10 board components, removed 4 merge/similarity components, added 8 requirements panel components, added 1 project type selector)
- Feature chain count reduced from 12 to 7 (removed board, keyword, similarity, merge chains)

---

## Summary

- **Design files modified:** 3 (`design-system.md`, `interactions.md`, `component-inventory.md`)
- **Integration files modified:** 2 (`gap-analysis.md`, `audit-report.md`)
- **Total sections updated:** 25+
- **Terminology consistently updated:** Idea → Project, Brainstorming → Requirements Assembly, Board → Requirements Panel, BRD → Requirements Document
