# Milestone 2: Landing Page & Idea Workspace Shell

## Overview
- **Wave:** 1
- **Estimated stories:** 8
- **Must complete before starting:** M1
- **Can run parallel with:** M3
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-1 | Idea Workspace (layout, visibility, locking, auto-scroll) | P1 | F-1.1–F-1.8 |
| FA-9 | Landing Page (lists, creation, search, filter, trash) | P1 | F-9.1–F-9.4 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | CRUD | id, title, state, visibility, agent_mode, owner_id, deleted_at | data-model.md |
| idea_collaborators | READ (list) | idea_id, user_id | data-model.md |
| users | READ | id, display_name, roles | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/ideas | POST | Create new idea | User | api-design.md |
| GET /api/ideas | GET | List user's ideas (owned, collaborating, trash) | User | api-design.md |
| GET /api/ideas/:id | GET | Get idea details | User (owner/collaborator/viewer) | api-design.md |
| PATCH /api/ideas/:id | PATCH | Update title, agent_mode, visibility | Owner | api-design.md |
| DELETE /api/ideas/:id | DELETE | Soft delete (set deleted_at) | Owner | api-design.md |
| POST /api/ideas/:id/restore | POST | Restore from trash (clear deleted_at) | Owner | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Landing Page (/) | Page | pages.md |
| HeroSection | Feature | component-inventory.md |
| IdeaCard | Feature (shared) | component-inventory.md |
| InvitationCard | Feature | component-inventory.md |
| FilterBar | Feature | component-inventory.md |
| Idea Workspace (/idea/:id) | Page | pages.md |
| PanelDivider | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API] Ideas REST API** — Create, list (with filters: state, ownership, trash), get single idea, update (title, agent_mode), soft delete, restore. DRF ViewSet + serializers. Permission classes (owner, collaborator, read-only viewer). Query filters: `?state=open`, `?ownership=mine|collaborating`, `?search=title`, `?trash=true`. Derived fields in GET response: `has_been_submitted` (check brd_versions exists), `is_locked` (derive from state). Pagination.
2. **[gRPC] Core gRPC service — GetIdeaContext** — Implement GetIdeaContext in Core service returning idea metadata (state, title, title_manually_edited, agent_mode, visibility, owner, co_owner, collaborators). This is consumed by the AI service in M6. Return structure per api-design.md gRPC definitions.
3. **[Frontend] Landing page — hero section + idea creation** — HeroSection component with heading, subtext, and chat-style input field. On submit: POST /api/ideas → navigate to /idea/:uuid. First message becomes the first chat message (seamless transition — message text passed via navigation state, persisted by Chat API in M4; for now, store in idea title or hold in state).
4. **[Frontend] Landing page — idea lists + IdeaCard** — My Ideas list, Collaborating list, Trash list. IdeaCard component (state dot, title, timestamp, badge, three-dot menu with delete/restore). Lists populated from GET /api/ideas with appropriate filters. Empty states for each list.
5. **[Frontend] Landing page — search + filters** — FilterBar component: search input (by title, debounced), state dropdown (Open/In Review/Accepted/Dropped/Rejected), ownership dropdown (My Ideas/Collaborating). Filters update query parameters and re-fetch.
6. **[Frontend] Soft delete + trash + undo toast** — Delete action: PATCH deleted_at → show undo toast (info type, timed). Undo: POST /api/ideas/:id/restore within toast duration. Trash list shows deleted ideas with restore button. Implement Celery task body for soft_delete_cleanup (query ideas where deleted_at + soft_delete_countdown exceeded, permanently delete with CASCADE).
7. **[Frontend] Idea workspace page shell** — Two-section layout: brainstorming (top, fills viewport) and review (bottom, below fold). Brainstorming has two-panel layout with PanelDivider (draggable, localStorage persistence, 40/60 default). Left panel: placeholder for ChatPanel (M4). Right panel: Tabs component with Board tab (placeholder for BoardCanvas, M5) and Review tab (placeholder). Workspace header: inline-editable title (F-1.6), agent mode dropdown (interactive/silent, persists to DB), presence area (placeholder), collaborator invite button (placeholder).
8. **[Frontend] Section visibility + auto-scroll + section locking + browser tab** — Review section hidden when `has_been_submitted=false` (F-1.2). Auto-scroll to active section based on idea state (F-1.3). Section locking per state: open=brainstorm editable, in_review=brainstorm locked, rejected=brainstorm editable, accepted/dropped=all read-only (F-1.4). Browser tab title shows idea name, updates dynamically (F-1.8). UUID-based routing /idea/:uuid (F-1.7).

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Layout (Navbar, PageShell) | Available | M1 |
| Toast | Available | M1 |
| EmptyState | Available | M1 |
| IdeaCard | **New (shared)** | M2 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/pages/LandingPage/`
- `frontend/src/pages/IdeaWorkspace/`
- `frontend/src/features/ideas/`
- `services/gateway/apps/ideas/`
- `services/core/apps/ideas/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/router.tsx` (add routes for / and /idea/:id)
- `frontend/src/components/shared/IdeaCard/` (new shared component)
- `services/core/grpc_server/servicer.py` (add GetIdeaContext implementation)
- `proto/core.proto` (already defined in M1)

## Milestone Acceptance Criteria
- [ ] Ideas CRUD API works (create, list, get, update, soft-delete, restore)
- [ ] Landing page renders with hero section, idea lists (My Ideas, Collaborating, Trash)
- [ ] Creating an idea from hero section navigates to workspace
- [ ] Search by title and filter by state/ownership work
- [ ] Soft delete moves to trash with undo toast, restore works
- [ ] Celery soft_delete_cleanup job permanently deletes expired items
- [ ] Workspace loads with two-panel layout, draggable divider
- [ ] Inline title editing works (saves to DB)
- [ ] Agent mode dropdown persists selection
- [ ] Review section hidden for never-submitted ideas
- [ ] Section locking per state renders correctly (read-only overlays)
- [ ] Browser tab title updates on idea name change
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1

## Notes
- **Stub: Invitations list on landing page** — Renders "Invitations" section with EmptyState "No pending invitations". Real invitation data wired in M8 when collaboration_invitations API exists.
- **Stub: Collaborating list** — Queries idea_collaborators table but no invitation flow creates collaborators yet. Shows existing data (from DB seed or direct DB insertion for testing). Full flow in M8.
- **Stub: Agent mode dropdown** — Renders and persists interactive/silent to ideas.agent_mode. AI doesn't read this value yet — M6 wires agent mode to Facilitator behavior.
- **Stub: Presence indicators area** — Shows current user avatar only. Multi-user presence tracking in M8.
- **Stub: Collaborator invite button** — Renders button in workspace header. Click shows placeholder modal "Collaboration features coming soon". Full modal in M8.
- **Stub: Review tab content** — Tab renders with EmptyState "BRD generation available after brainstorming". Real content in M7.
- **Stub: Board tab content** — Tab renders with EmptyState "Board loading...". Real React Flow canvas in M5.
- **Stub: Chat panel** — Left panel renders with EmptyState "Chat loading...". Real chat in M4.
- **Stub: First message from hero** — On idea creation, the first message text is stored in a URL parameter or local state. When Chat API exists (M4), the landing page creation flow will POST the first chat message after idea creation. For now, the text is shown as the idea title if no title is set.
- **Stub: Notification triggers** — Soft delete/restore show toast-only. No persistent notifications dispatched. Wired in M10.
