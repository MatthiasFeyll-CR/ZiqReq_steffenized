# Milestone 9: Collaboration + Notifications

## Overview
- **Execution order:** 9 (runs after M8)
- **Estimated stories:** 10
- **Dependencies:** M3 (WebSocket), M8 (review events)
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-8.1 | Visibility Modes | Must-have | features.md |
| F-8.2 | Invite Flow | Must-have | features.md |
| F-8.3 | Read-Only Link Sharing | Must-have | features.md |
| F-8.4 | Collaborator Management | Must-have | features.md |
| F-12.1 | Notification Bell | Must-have | features.md |
| F-12.2 | Toast Notification Wiring (all events) | Must-have | features.md |
| F-12.3 | Floating Banner (Invitation) | Must-have | features.md |
| F-12.5 | All Notification Events | Must-have | features.md |
| F-13.1 | Email Notification Settings | Must-have | features.md |
| F-13.2 | Grouped Toggles | Must-have | features.md |
| F-13.3 | Role-Based Notification Groups | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | UPDATE (visibility, co_owner_id) | visibility, share_link_token, co_owner_id | data-model.md |
| idea_collaborators | CREATE, READ, DELETE | idea_id, user_id, joined_at | data-model.md |
| collaboration_invitations | CREATE, READ, UPDATE | idea_id, inviter_id, invitee_id, status | data-model.md |
| notifications | CREATE, READ, UPDATE | user_id, event_type, title, body, reference_id, is_read, action_taken | data-model.md |
| users | READ, UPDATE | email_notification_preferences, display_name, roles | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/collaborators/invite | POST | Send collaboration invitation | Bearer/bypass | api-design.md |
| /api/ideas/:id/collaborators/:uid | DELETE | Remove collaborator | Bearer/bypass | api-design.md |
| /api/ideas/:id/collaborators/transfer | POST | Transfer ownership | Bearer/bypass | api-design.md |
| /api/ideas/:id/collaborators/leave | POST | Leave idea | Bearer/bypass | api-design.md |
| /api/invitations | GET | List pending invitations for current user | Bearer/bypass | api-design.md |
| /api/invitations/:id/accept | POST | Accept invitation | Bearer/bypass | api-design.md |
| /api/invitations/:id/decline | POST | Decline invitation | Bearer/bypass | api-design.md |
| /api/invitations/:id/revoke | POST | Revoke sent invitation | Bearer/bypass | api-design.md |
| /api/ideas/:id/share-link | POST | Generate read-only share link | Bearer/bypass | api-design.md |
| /api/ideas/:id/share-link | DELETE | Revoke share link | Bearer/bypass | api-design.md |
| /api/notifications | GET | List notifications for current user | Bearer/bypass | api-design.md |
| /api/notifications/:id/read | POST | Mark notification as read | Bearer/bypass | api-design.md |
| /api/notifications/:id/action | POST | Mark notification as acted on | Bearer/bypass | api-design.md |
| /api/users/me/notification-preferences | GET | Get email preferences | Bearer/bypass | api-design.md |
| /api/users/me/notification-preferences | PUT | Update email preferences | Bearer/bypass | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| NotificationBell | Component (navbar) | component-specs.md |
| NotificationFloatingWindow | Component | component-specs.md |
| NotificationItem | Component | component-specs.md |
| InvitationBanner | Component (idea page) | component-specs.md |
| InviteDialog | Component | component-specs.md |
| CollaboratorDropdown | Component | component-specs.md |
| ShareLinkButton | Component | component-specs.md |
| EmailPrefsModal | Component | component-specs.md |
| GroupedToggle | Component | component-specs.md |
| InvitationCard (landing page) | Component | component-specs.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| Notification service (event consumer → email + notification creation) | Activated | M9 (scaffold from M1) |
| Email templating (i18n-aware) | New | M9 |

## Story Outline (Suggested Order)

1. **[Backend] Collaboration invitation APIs** — Gateway REST: POST invite (search users from directory/dev users), GET /api/invitations (pending for current user), POST accept, POST decline, POST revoke. Core gRPC: create invitation, update status. On accept: add to idea_collaborators, update idea visibility to 'collaborating' if first collaborator. Publish collaboration.* events. Owner can re-invite after decline.
2. **[Backend] Collaborator management APIs** — DELETE /api/ideas/:id/collaborators/:uid (remove). POST transfer (transfer ownership to collaborator). POST leave (collaborator leaves). Co-owner rules: co-owner can leave without transferring, single owner must transfer before leaving. On remove: delete from idea_collaborators, publish event.
3. **[Backend] Read-only link sharing** — POST /api/ideas/:id/share-link (generate unique token, store in ideas.share_link_token). DELETE to revoke. Access via /idea/:uuid?token=:token — validates token, grants read-only access. Requires Azure AD authentication (no anonymous access).
4. **[Backend] Notification service activation** — Activate Notification service from M1 scaffold. Event consumer: listens to all events from message broker. For each event: create persistent notification record (via Gateway gRPC), send email (if user's email_notification_preferences allow). Email templates (HTML) with i18n support (de/en based on recipient's language preference).
5. **[Backend] Notification CRUD APIs + email preferences** — Gateway REST: GET /api/notifications (list, paginated, unread count), POST mark read, POST mark acted on. GET/PUT /api/users/me/notification-preferences (JSONB grouped toggles). WebSocket broadcast for new notifications (bell badge increment).
6. **[Frontend] Collaboration UI** — Invite dialog: user search (name/email), send invitation. Collaborator dropdown in workspace header: list collaborators, remove button (owner only), transfer ownership, leave button. Invitation cards on landing page (Invitations list) with accept/decline buttons.
7. **[Frontend] Invitation banner + read-only link** — Floating banner when user with pending invitation navigates to idea: accept/decline buttons. Accept → become collaborator, banner disappears, idea unlocks. Decline → redirect to landing page. Share link: generate button, copy link, revoke. Read-only mode: all editing disabled, view-only indicator.
8. **[Frontend] Notification bell + persistent notifications** — Bell icon in navbar with unread count badge. Click opens floating window with notification list. Inline action buttons (accept/decline on invitation notifications). Click navigates to relevant context. Notifications dismissed after action taken.
9. **[Frontend] Toast notification wiring (all events)** — Wire all FA-12.5 notification events to toast types: toast-only events (trash, restore, PDF, connection, rate limit) and dual events (collaboration, review, @mention, similarity). Toast types: success/info/warning/error with correct auto-dismiss behavior.
10. **[Frontend] Email notification preferences** — Modal accessible from user menu dropdown. Grouped toggles: All Users (Collaboration, Review, Chat, Similarity), Reviewer-only (Review Management), Admin-only (System). Group toggle switches all items on/off. Individual toggles per notification type. Indeterminate state when mixed.

## Milestone Acceptance Criteria
- [ ] Owner can invite users, invitee receives in-app notification + email
- [ ] Invitee can accept/decline from landing page or idea banner
- [ ] Collaborator management: remove, transfer ownership, leave all work
- [ ] Co-owner rules enforced (can leave without transferring, etc.)
- [ ] Read-only link sharing generates authenticated read-only access
- [ ] Notification bell shows unread count, floating window lists notifications
- [ ] Inline actions on notifications (accept/decline invitations) work
- [ ] Toast notifications fire for all specified event types
- [ ] Email notifications dispatch via Notification service with i18n templates
- [ ] Email preferences: grouped toggles with role-based groups work
- [ ] Notification service consumes all events from message broker
- [ ] WebSocket broadcasts notification events for real-time bell updates
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M8

## Notes
- Merge request banner (F-12.4) is included in the component structure but merge request events come in M10.
- Similar idea notifications come in M10.
- The co-owner model is fully implemented here (rules for merged ideas) even though merge itself comes in M10 — the data model supports it.
- Email service requires Azure Communication Services configuration. If not available, emails are logged but not sent (graceful degradation).
