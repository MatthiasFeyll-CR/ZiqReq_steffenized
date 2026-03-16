# Release Plan — Refactoring (M17-M21)

## Context
Milestones M1-M16 implemented the original ZiqReq platform. The previous M17-M21 (E2E tests) have been superseded. This release plan covers the refactoring from brainstorming platform to requirements assembly platform.

## MVP Boundary
- **All milestones are MVP** — the refactoring must be completed in full
- **MVP features:** Feature removal, entity rename, project types, structured requirements, AI rework, PDF generation, process flow update

## Milestone Execution Order

### M17: Remove Features (Clean Slate)
- **Purpose:** Remove merge/similarity/keyword system and Board (XYFlow) from entire codebase
- **Dependencies:** M16 (existing implementation complete)
- **Stories:** 4

### M18: Rename Idea to Project
- **Purpose:** Rename core entity from "Idea" to "Project" across DB, API, frontend, translations
- **Dependencies:** M17
- **Stories:** 4

### M19: Project Types & Structured Requirements
- **Purpose:** Add project type distinction, new hierarchical requirements data model, requirements panel UI, per-type admin context
- **Dependencies:** M18
- **Stories:** 4

### M20: AI System Prompt Rework
- **Purpose:** Rewrite Facilitator and Summarizing AI for requirements structuring, update pipeline
- **Dependencies:** M19
- **Stories:** 3

### M21: Document View, PDF Generation & Final Polish
- **Purpose:** New Structure step, type-specific PDF templates, process stepper update, landing page refresh, final cleanup
- **Dependencies:** M20
- **Stories:** 5

## Milestone Summary

| Milestone | Name | Stories | Dependencies | MVP |
|-----------|------|---------|-------------|-----|
| M17 | Remove Features (Clean Slate) | 4 | M16 | Yes |
| M18 | Rename Idea to Project | 4 | M17 | Yes |
| M19 | Project Types & Structured Requirements | 4 | M18 | Yes |
| M20 | AI System Prompt Rework | 3 | M19 | Yes |
| M21 | Document View, PDF & Polish | 5 | M20 | Yes |

**Total: 5 milestones, 20 stories**

## Dependency Flow
```
M16 (existing) → M17 → M18 → M19 → M20 → M21
```

Strictly sequential — each milestone builds on the previous.

## Branch Strategy
| Milestone | Branch Pattern | Base Branch | Merge Target |
|-----------|---------------|-------------|-------------|
| M17 | ralph/m17-remove-features | master | master |
| M18 | ralph/m18-rename-project | master (after M17 merge) | master |
| M19 | ralph/m19-structured-requirements | master (after M18 merge) | master |
| M20 | ralph/m20-ai-rework | master (after M19 merge) | master |
| M21 | ralph/m21-polish-final | master (after M20 merge) | master |
