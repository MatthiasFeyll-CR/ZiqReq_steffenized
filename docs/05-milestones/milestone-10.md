# Milestone 10: Notification System

## Overview
- **Wave:** 5
- **Estimated stories:** 8
- **Must complete before starting:** M8
- **Can run parallel with:** M9
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-12 | Notification System (bell, panel, toast, email, banners) | P1 | F-12.1–F-12.5 |
| FA-13 | User Notification Preferences (email settings) | P1 | F-13.1 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| notifications | CRUD | user_id, type, title, description, idea_id, action_url, is_read, is_acted_on, created_at | data-model.md |
| users | READ, UPDATE | email_notification_preferences (JSONB) | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| GET /api/notifications | GET | List notifications (paginated, filterable) | User | api-design.md |
| GET /api/notifications/unread-count | GET | Get unread notification count | User | api-design.md |
| PATCH /api/notifications/:id/read | PATCH | Mark notification as read | User | api-design.md |
| PATCH /api/notifications/mark-all-read | PATCH | Mark all as read | User | api-design.md |
| PATCH /api/notifications/:id/acted | PATCH | Mark as acted on | User | api-design.md |
| PATCH /api/users/me/preferences | PATCH | Update email notification preferences | User | api-design.md |
| GET /api/users/me/preferences | GET | Get email notification preferences | User | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| NotificationBell (replace stub) | Feature | component-inventory.md |
| NotificationPanel | Feature | component-inventory.md |
| NotificationItem | Feature | component-inventory.md |
| EmailPreferencesPanel | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API] Notifications REST API** — CRUD for notifications table. GET /api/notifications: paginated list, filter by is_read, ordered by created_at DESC. GET unread-count: COUNT where is_read=false. PATCH read: set is_read=true, update read_at. PATCH mark-all-read: bulk update. PATCH acted: set is_acted_on=true. Notifications created by notification service (not by user REST calls). DRF serializers with type-specific rendering hints.
2. **[Frontend] NotificationBell + NotificationPanel** — Replace M1 bell stub. NotificationBell: bell icon in navbar with unread count badge (red circle, number). Click opens floating NotificationPanel. Panel: list of NotificationItem components, "Mark All Read" header action, infinite scroll. NotificationItem: type-specific icon, title, description, relative timestamp ("2m ago"), click navigates to action_url and marks as read. Unread items have subtle background highlight. WebSocket: listen for `notification.created` event to increment count and optionally show toast.
3. **[Frontend] Toast notification system integration** — Wire react-toastify with 4 semantic variants per design-system.md: success (green), error (red), warning (gold), info (blue). Auto-dismiss configurable per type (success: 5s, info: 5s, warning: 10s, error: persistent until dismissed or action taken). Stacking: max 3 visible, queued. Position: top-right. Specific toast patterns: undo toast (info type with undo action button, timed), error toast (persistent, "Show Logs" + "Retry"), success toast (auto-dismiss). Ensure all existing toast-only stubs from M2–M9 use this system consistently.
4. **[Backend] Notification service** — Implement services/notification/ (replace M1 skeleton). Message broker event consumer. For each consumed event: determine notification type from event, look up target users (event-specific logic), for each target user: create persistent notification via gateway gRPC CreateNotification, check user's email_notification_preferences, if email enabled for this type: dispatch email. Consumer listens to: collaboration events (invitation.sent, invitation.accepted, collaborator.removed), review events (idea.state.changed, review.assignment.created, review.timeline.comment), AI events (ai.processing.failed), monitoring events (monitoring.alert), similarity events (similarity.confirmed — stub consumer, no events published until M11).
5. **[Backend] Email dispatch service** — Azure Communication Services Email integration. HTML email templates (base template + per-notification-type content). i18n support: render email in user's language preference (read from users.email_notification_preferences or default). Email types: invitation, review assignment, review decision, monitoring alert. Configurable: ACS_EMAIL_ENDPOINT, ACS_EMAIL_ACCESS_KEY, EMAIL_FROM env vars. If env vars empty: email dispatch disabled (log only). Rate limiting: batch emails per user (max 1 email per event type per minute).
6. **[Frontend+API] Email notification preferences** — EmailPreferencesPanel in UserDropdown (replace M1 placeholder). Grouped toggles per FA-13.1: Collaboration (invitation received, invitation accepted/declined, removed from idea), Review (assigned for review, review decision on my idea, timeline comment on my idea), System (monitoring alerts — admin only). GET /api/users/me/preferences returns current JSONB. PATCH updates individual preference keys. Indeterminate state for group toggle (some on, some off).
7. **[Backend+Frontend] All notification event wiring** — Wire all FA-12.5 notification events. Toast-only events (no persistent notification, no email): trash/restore (already works), PDF generation success/error, connection status changes, rate limit lockout/unlock. Dual events (persistent + optional email): collaboration invitation sent/accepted/declined/revoked, collaborator removed, ownership transferred, review submission, review decision (accept/reject/drop/undo), review assignment, timeline comment, @mention in chat. Ensure each event type maps to correct notification template (title, description, icon, action_url).
8. **[Frontend] Floating banners finalization** — InvitationBanner (M8): ensure action wiring complete — accept creates collaborator + dismiss banner, decline updates invitation + dismiss. MergeRequestBanner: component renders when idea has pending merge_request targeting it. Shows merge request info + accept/decline buttons. Accept/decline are stubs (no merge_request API until M11). Banner shows warning icon and locks idea editing. Ensure both banners stack correctly if both conditions met.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Toast (react-toastify) | Available | M1 |
| Navbar + UserDropdown | Available | M1 |
| WebSocket infrastructure | Available | M1 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `services/notification/` (implementation of M1 skeleton)
- `frontend/src/features/notifications/`
- `services/gateway/apps/notifications/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/components/layout/Navbar/` (replace NotificationBell stub, wire panel)
- `frontend/src/components/layout/UserDropdown/` (add EmailPreferencesPanel)
- `services/gateway/apps/websocket/consumers.py` (add notification.created broadcast)
- `services/gateway/grpc_server/servicer.py` (add CreateNotification gRPC method)
- `proto/notification.proto` (implement service methods)

## Milestone Acceptance Criteria
- [ ] Notifications API: create, list, mark read, mark acted on, unread count
- [ ] NotificationBell shows unread count, click opens panel
- [ ] NotificationPanel lists notifications with type-specific icons and navigation
- [ ] Toast notifications render with correct variants and auto-dismiss behavior
- [ ] Notification service consumes events and creates persistent notifications
- [ ] Email dispatch works (or logs when ACS not configured)
- [ ] Email preferences: toggles work, preferences respected by notification service
- [ ] All FA-12.5 events wired (toast-only and dual)
- [ ] Collaboration events trigger notifications to correct users
- [ ] Review events trigger notifications to correct users
- [ ] @mention in chat triggers notification to mentioned user
- [ ] MergeRequestBanner renders (stub — no merge requests yet)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M8, M12

## Notes
- **Stub: MergeRequestBanner actions** — Accept/decline buttons render but actions call stub endpoints that return 501 "Not Implemented". Full merge request API in M11. QA should verify the banner renders when a merge_request record exists for the idea.
- **Stub: similarity.confirmed notification consumer** — Event handler registered in notification service but similarity.confirmed events are not published until M11. Once M11 merges, notifications fire automatically.
- **Stub: Monitoring email alerts** — monitoring.alert event consumer creates persistent notification and dispatches email to opted-in admins. The monitoring service (M3) already publishes these events. Full flow works end-to-end after M10 merges.
- Email dispatch is gracefully degraded: if ACS env vars are not set, all emails are logged but not sent. This supports development without Azure credentials.
- Notification service is stateless — it creates notifications via gateway gRPC, not by direct DB access. This maintains the service boundary.
