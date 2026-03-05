# Milestone 8: Collaboration & Presence

## Overview
- **Wave:** 4
- **Estimated stories:** 8
- **Must complete before starting:** M6
- **Can run parallel with:** M7, M12
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-6 | Real-Time Collaboration (presence, offline, reconnect) | P1 | F-6.1–F-6.5 |
| FA-8 | Visibility & Sharing (invite, collaborate, read-only) | P1 | F-8.1–F-8.2 |
| FA-15 | Idle State Detection | P1 | F-15.1 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| collaboration_invitations | CRUD | idea_id, inviter_id, invitee_id, status | data-model.md |
| idea_collaborators | CREATE, READ, DELETE | idea_id, user_id, role | data-model.md |
| ideas | READ, UPDATE | visibility, owner_id, co_owner_id | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/ideas/:id/collaborators/invite | POST | Send invitation | Owner | api-design.md |
| GET /api/ideas/:id/collaborators | GET | List collaborators | User (with access) | api-design.md |
| POST /api/ideas/:id/collaborators/accept | POST | Accept invitation | Invitee | api-design.md |
| POST /api/ideas/:id/collaborators/decline | POST | Decline invitation | Invitee | api-design.md |
| DELETE /api/ideas/:id/collaborators/:userId | DELETE | Remove collaborator | Owner | api-design.md |
| POST /api/ideas/:id/collaborators/transfer | POST | Transfer ownership | Owner | api-design.md |
| POST /api/ideas/:id/collaborators/leave | POST | Leave idea | Collaborator | api-design.md |
| DELETE /api/ideas/:id/collaborators/invitations/:invId | DELETE | Revoke pending invitation | Owner | api-design.md |
| GET /api/ideas/:id/share-link | GET | Generate share link | Owner | api-design.md |
| GET /api/shared/:token | GET | Access shared view | Public (token-based) | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| CollaboratorModal | Feature | component-inventory.md |
| PresenceIndicators | Feature | component-inventory.md |
| InvitationBanner | Feature | component-inventory.md |
| OfflineBanner | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API] Collaboration invitations API** — POST invite (validate: idea exists, user not already collaborator/invited, idea in open state). Accept → create idea_collaborators record, update invitation status, update ideas.visibility to 'collaborating' if first collaborator. Decline → update invitation status. Revoke → delete pending invitation. List pending invitations for user: GET /api/invitations (for landing page). List collaborators for idea: GET with roles and online status.
2. **[Frontend] Collaborator management UI** — CollaboratorModal (replace M2 stub): user search input (search /api/users?q=), invite button, pending invitations list with revoke, current collaborators list with role badges and remove button. Transfer ownership action (owner only, target becomes owner, original becomes collaborator). Leave idea action (collaborator removes self). Wire landing page invitation card (M2 InvitationCard): show pending invitations, accept/decline actions navigate to idea on accept.
3. **[WebSocket] Presence tracking** — WebSocket events: presence_update (online/idle/offline), subscribe_idea, unsubscribe_idea. Server-side: track connected users per idea channel group. Broadcast presence changes to all subscribers. PresenceIndicators component in workspace header: stacked avatars with overflow count (+N), presence dot (green=online, yellow=idle, gray=offline). Gateway exposes active connection count for monitoring dashboard (M3).
4. **[Frontend+WebSocket] Multi-user board sync** — UserSelectionHighlight: when User A selects a board node, broadcast selection event via WebSocket. Other users see colored border with User A's name on that node. Color assignment per user (consistent across session). Selection cleared when user deselects or disconnects. Build on M5's awareness event pattern (ephemeral, WebSocket-only).
5. **[API+Frontend] Visibility modes** — Private: only owner sees idea (default on creation). Collaborating: owner + collaborators see idea (automatic on first accepted invitation). Collaborating ideas appear in "Collaborating" list on landing page. Wire M2's Collaborating list with real invitation/collaborator data. Permission checks updated: collaborators have full edit access to chat and board.
6. **[API+Frontend] Read-only link sharing** — Generate share_link_token for idea (random UUID). GET /api/shared/:token returns read-only view (idea metadata + chat + board, no editing). Frontend: shared view page renders workspace in read-only mode (no ChatInput, board not editable, no admin actions). Share link button in CollaboratorModal. Token revocable by owner.
7. **[Frontend] Offline behavior** — OfflineBanner: red banner across top of workspace when WebSocket disconnects. Shows countdown to next reconnection attempt. Reconnect button for manual retry. Chat input disabled (gray overlay "You're offline"). Board interactions disabled. On reconnect: full state sync from server (re-fetch latest messages via REST, re-fetch board state, compare and reconcile). Offline banner dismisses on successful reconnect.
8. **[Frontend] Idle detection + disconnect** — Frontend inactivity timer: no mouse/keyboard/scroll → idle after admin: idle_timeout (default 5min). Send presence_update(idle) on idle transition. Tab visibility API: when tab hidden, send idle after shorter timeout. WebSocket: server closes connection after extended idle (default 120s with no client heartbeat). Client reconnection with exponential backoff (max 30s, admin-configurable). Return-from-idle: mouse movement → reconnect if needed → presence_update(online).

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Workspace page shell | Available | M2 |
| WebSocket infrastructure | Available | M1 |
| Board canvas + sync | Available | M5 |
| Chat panel | Available | M4 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/features/collaboration/`
- `frontend/src/features/presence/`
- `services/gateway/apps/collaboration/`
- `services/core/apps/collaboration/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/pages/IdeaWorkspace/` (wire CollaboratorModal, PresenceIndicators, OfflineBanner, InvitationBanner)
- `frontend/src/pages/LandingPage/` (wire invitation cards with real data)
- `frontend/src/features/board/` (add UserSelectionHighlight multi-user)
- `frontend/src/store/` (add websocket slice: connection state, presence)
- `services/gateway/apps/websocket/consumers.py` (add presence events, connection tracking)
- `frontend/src/router.tsx` (add /shared/:token route)

## Milestone Acceptance Criteria
- [ ] Invitation flow: invite → accept/decline → collaborator record created
- [ ] CollaboratorModal: search, invite, revoke, remove, transfer, leave all work
- [ ] Landing page shows pending invitations with accept/decline
- [ ] Presence indicators show online/idle/offline users in real-time
- [ ] Multi-user board selection highlights visible to all connected users
- [ ] Visibility auto-transitions from private to collaborating
- [ ] Read-only share link generates and provides read-only access
- [ ] Offline banner appears on disconnect, disappears on reconnect
- [ ] Chat/board disabled during offline state
- [ ] State syncs correctly on reconnect (no missing messages)
- [ ] Idle detection transitions presence correctly
- [ ] WebSocket reconnection with exponential backoff works
- [ ] Gateway reports active connection count to monitoring API
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M6

## Notes
- **Stub: Notification triggers for collaboration events** — Invitation sent, accepted, declined, revoked; collaborator removed; ownership transferred. All fire toast-only. No persistent notifications or emails dispatched. Full notification wiring in M10.
- **Stub: Email notifications for invitations** — No email sent on invitation. Only in-app toast on the sender's side. Email dispatch implemented in M10 notification service.
- **Stub: Multi-user AI awareness** — AI already has user names from M6 metadata. After M8, presence tracking makes multi-user detection possible (>1 online user). AI doesn't yet intelligently switch behavior. Polished in M12 (system prompt adjustments, address by name, track who said what).
- **Stub: InvitationBanner on workspace** — Renders when user has pending invitation for this idea. Accept/decline actions work and update collaborator status. This is complete in M8, not a stub.
- **Stub: MergeRequestBanner** — Component exists but is never rendered (no merge requests exist until M11). Rendered when merge_request data present for the idea.
