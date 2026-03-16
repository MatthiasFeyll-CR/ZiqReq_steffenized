# Milestone 18: Rename Idea to Project

## Overview
- **Execution order:** 18 (runs after M17)
- **Estimated stories:** 4
- **Dependencies:** M17
- **MVP:** Yes

## Purpose
Rename the core "Idea" entity to "Project" across the entire codebase — database, backend models, API routes, frontend code, and all user-facing text. Must run after M17 (feature removal) to minimize the number of files that need renaming.

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| R-2.1 | Rename DB & backend models | Critical | REFACTORING_PLAN.md Phase 2 |
| R-2.2 | Rename API routes | Critical | REFACTORING_PLAN.md Phase 2 |
| R-2.3 | Rename frontend | Critical | REFACTORING_PLAN.md Phase 2 |
| R-2.4 | Rename terminology & translations | Critical | REFACTORING_PLAN.md Phase 2 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | RENAME TO projects | all | Story 2.1 |
| idea_collaborators | RENAME TO project_collaborators | all | Story 2.1 |
| chat_messages | RENAME COLUMN | idea_id -> project_id | Story 2.1 |
| brd_drafts | RENAME COLUMN | idea_id -> project_id | Story 2.1 |
| brd_versions | RENAME COLUMN | idea_id -> project_id | Story 2.1 |
| review_assignments | RENAME COLUMN | idea_id -> project_id | Story 2.1 |
| review_timeline_entries | RENAME COLUMN | idea_id -> project_id | Story 2.1 |
| projects (new) | ADD COLUMN | project_type (varchar, required) | Story 2.1 |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/* | ALL | RENAME to /api/projects/* | All | Story 2.2 |
| /api/projects/:project_id/* | ALL | Updated parameter names | All | Story 2.2 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| IdeaWorkspace -> ProjectWorkspace | RENAME | Story 2.3 |
| IdeaCard -> ProjectCard | RENAME | Story 2.3 |
| IdeaCardSkeleton -> ProjectCardSkeleton | RENAME | Story 2.3 |
| ideas.ts -> projects.ts (API) | RENAME | Story 2.3 |
| All idea-related hooks | RENAME | Story 2.3 |

## Story Outline (Suggested Order)
1. **[Backend] Rename DB & models** — Create migrations to rename tables (ideas->projects, idea_collaborators->project_collaborators), rename all idea_id columns to project_id, add project_type column. Rename Django apps (ideas->projects in core and gateway). Rename model classes (Idea->Project, IdeaCollaborator->ProjectCollaborator). Update all cross-references in chat, brd, review, collaboration apps. Update gRPC proto files and regenerate stubs. Rename WebSocket consumer and channel groups. Update RabbitMQ event types and notification templates.
2. **[Backend] Rename API routes** — Update URL patterns from /api/ideas/ to /api/projects/. Rename URL parameters idea_id->project_id. Update view function parameter names and error messages. Update WebSocket routing if needed.
3. **[Frontend] Rename all idea references** — Rename files (api/ideas.ts->projects.ts, IdeaWorkspace->ProjectWorkspace, IdeaCard->ProjectCard, all idea hooks). Rename types (Idea->Project interface, add projectType field). Update routing (/idea/:id -> /project/:id). Update all API calls, React Query keys, Redux slices, WebSocket events. Update component props, state variables, function names.
4. **[Both] Rename terminology & translations** — Update en.json and de.json: replace all brainstorming/idea language with project/requirements language. Update process step labels (Brainstorm->Define, Document->Structure). Update AI prompts (facilitator, summarizing AI, context agent) to use project/requirements language instead of brainstorming/idea language.

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Rename DB & backend models | ~15,000 | Data model, architecture | ~30 files | High | High — touches every service, migrations critical |
| 2 | Rename API routes | ~5,000 | API design | ~8 files | Low | Low — straightforward renames |
| 3 | Rename frontend | ~12,000 | Component specs | ~25 files | High | Medium — many file renames and cross-references |
| 4 | Rename terminology & translations | ~8,000 | Requirements, AI specs | ~10 files | Medium | Low — text changes only |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~40,000
- **Cumulative domain size:** Large (touches entire codebase)
- **Information loss risk:** Medium (score: 5) — Story 1 is heavy but subsequent stories are lighter
- **Context saturation risk:** Medium

## Milestone Acceptance Criteria
- [ ] All database tables and columns renamed, migrations run successfully
- [ ] project_type column added to projects table
- [ ] All backend models, views, serializers renamed from idea to project
- [ ] All API routes use /api/projects/ prefix
- [ ] All gRPC proto files updated and stubs regenerated
- [ ] All frontend files, types, hooks, components renamed
- [ ] Routing updated to /project/:id
- [ ] All translations updated (en.json and de.json)
- [ ] Process steps renamed: Define, Structure, Review
- [ ] AI prompts updated to use project/requirements language
- [ ] grep -r "idea\|Idea\|brainstorm" returns only intentional/comment hits
- [ ] TypeScript typecheck passes
- [ ] All services start without errors
- [ ] No regressions on previous milestones

## Notes
- Story 1 is the heaviest — it touches every backend service, migrations, gRPC, WebSocket, and events. Must be done carefully.
- The project_type column is added here but the type selection UI comes in M19.
- Story 4 updates AI prompts with terminology only — the full AI rework comes in M20.
- No backwards compatibility needed (breaking refactor, no external consumers).
