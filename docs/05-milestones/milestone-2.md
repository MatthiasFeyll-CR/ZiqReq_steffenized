# Milestone 2: Landing Page & Idea CRUD

## Overview
- **Execution order:** 2 (runs after M1)
- **Estimated stories:** 8
- **Dependencies:** M1
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-9.1 | Landing Page Structure | P1 | features.md FA-9 |
| F-9.2 | Idea Creation | P1 | features.md FA-9 |
| F-9.3 | Soft Delete | P1 | features.md FA-9 |
| F-9.4 | Search & Filter | P1 | features.md FA-9 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | INSERT, SELECT, UPDATE, SOFT DELETE | id, title, state, visibility, owner_id, deleted_at | data-model.md |
| collaboration_invitations | SELECT (pending for invitee) | invitee_id, status, idea_id | data-model.md |
| idea_collaborators | SELECT (user's collaborations) | user_id, idea_id | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas | GET | List user's ideas (owned + collaborating) | Bearer | api-design.md |
| /api/ideas | POST | Create new idea | Bearer | api-design.md |
| /api/ideas/:id | GET | Get idea details | Bearer | api-design.md |
| /api/ideas/:id | DELETE | Soft delete idea | Bearer | api-design.md |
| /api/ideas/:id/restore | POST | Restore from trash | Bearer | api-design.md |
| /api/invitations | GET | List pending invitations for current user | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Landing Page (/) | Page | page-layouts.md S1 |
| HeroSection | Feature | component-inventory.md |
| IdeaCard | Feature (shared) | component-specs.md S2.2 |
| InvitationCard | Feature | component-inventory.md |
| FilterBar | Feature | component-inventory.md |
| IdeasListFloating | Layout | component-inventory.md |

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Built | M1 |
| Navbar, PageShell | Built | M1 |
| IdeaCard | To be built | M2 |

## Story Outline (Suggested Order)
1. **[API]** Ideas REST API — CRUD endpoints (create, list with filters, get, soft delete, restore)
2. **[API]** Invitations list endpoint — GET /api/invitations for pending invitations
3. **[Frontend — Page]** Landing page layout — hero section, ordered list sections (My Ideas, Collaborating, Invitations, Trash)
4. **[Frontend — Component]** IdeaCard component — state dot, title, timestamp, state badge, three-dot menu
5. **[Frontend — Feature]** Idea creation flow — hero input, POST /api/ideas, redirect to /idea/:uuid
6. **[Frontend — Feature]** Idea lists — My Ideas + Collaborating + Trash with TanStack Query, soft delete with undo toast
7. **[Frontend — Feature]** Search & filter bar — search by title, filter by state, filter by ownership
8. **[Frontend — Feature]** Ideas list floating window — navbar button, tabbed panel (Active, In Review, Accepted, Closed)

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Ideas REST API | ~8,000 | api-design.md (ideas section), data-model.md (ideas) | 6-8 files | Medium | Filter/sort logic |
| 2 | Invitations list API | ~3,000 | api-design.md (invitations) | 2-3 files | Low | — |
| 3 | Landing page layout | ~6,000 | page-layouts.md (S1), design-system.md | 3-5 files | Medium | Responsive layout |
| 4 | IdeaCard component | ~4,000 | component-specs.md (S2.2, S3.1) | 2-3 files | Low | — |
| 5 | Idea creation flow | ~5,000 | page-layouts.md (hero), api-design.md | 3-4 files | Medium | Seamless transition to workspace |
| 6 | Idea lists | ~5,000 | page-layouts.md (S1), api-design.md | 4-6 files | Medium | TanStack Query cache management |
| 7 | Search & filter | ~3,000 | features.md (F-9.4) | 2-3 files | Low | — |
| 8 | Ideas list floating | ~4,000 | page-layouts.md (floating windows), component-inventory.md | 3-4 files | Medium | Tabbed panel, conditionally hidden tabs |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~38,000
- **Cumulative domain size:** Small-Medium (ideas CRUD + landing page)
- **Information loss risk:** Low (2)
- **Context saturation risk:** Low
- **Heavy stories:** 0

## Milestone Acceptance Criteria
- [ ] Landing page renders with hero section and 4 ordered lists
- [ ] Creating an idea from hero input transitions seamlessly to workspace
- [ ] Ideas appear in correct lists based on ownership and state
- [ ] Soft delete moves idea to Trash with undo toast
- [ ] Search filters ideas by title
- [ ] State and ownership filters work correctly
- [ ] Ideas list floating window shows tabbed categories
- [ ] InvitationCard shows pending invitations with accept/decline (wired in M11)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1

## Notes
- Invitation accept/decline buttons are rendered but not wired — full invitation flow is M11 (Collaboration).
- The workspace redirect after idea creation goes to a placeholder page until M3 builds the full workspace.
- Soft delete cleanup Celery job (permanent deletion after countdown) can be implemented here or deferred to M15 (Admin) where the countdown parameter is configurable.
