# Milestone 12: Notification System

## Overview
- **Execution order:** 12 (runs after M6)
- **Estimated stories:** 9
- **Dependencies:** M6
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-12.1 | Notification Bell | P1 | features.md FA-12 |
| F-12.2 | Toast Notifications | P1 | features.md FA-12 |
| F-12.5 | All Notification Events | P1 | features.md FA-12 |
| F-13.1 | Email Notification Settings | P1 | features.md FA-13 |
| F-13.2 | Grouped Toggles | P1 | features.md FA-13 |
| F-13.3 | Role-Based Notification Groups | P1 | features.md FA-13 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| notifications | INSERT, SELECT, UPDATE | user_id, event_type, title, body, reference_id, is_read, action_taken | data-model.md |
| users | SELECT, UPDATE (email_notification_preferences) | email_notification_preferences | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/notifications | GET | List notifications for user | Bearer | api-design.md |
| /api/notifications/unread-count | GET | Unread count for badge | Bearer | api-design.md |
| /api/notifications/:id | PATCH | Mark as read / acted | Bearer | api-design.md |
| /api/users/me/notification-preferences | GET | Get email preferences | Bearer | api-design.md |
| /api/users/me/notification-preferences | PATCH | Update email preferences | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| NotificationBell | Layout | component-inventory.md |
| NotificationPanel | Feature | component-inventory.md |
| NotificationItem | Feature | component-inventory.md |
| EmailPreferencesPanel | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend — Gateway]** Notification REST API — list (paginated), unread count, mark read/acted
2. **[Backend — Gateway]** Notification creation service — create notification record from event payload
3. **[Backend — Notification]** Notification service consumer — consume events from broker, create notifications via gateway gRPC, dispatch emails
4. **[Backend — Gateway]** Email notification preferences API — GET/PATCH, respect preferences before email dispatch
5. **[Backend]** Wire all notification events — collaboration (invite, join, leave, remove), review (submitted, accepted, rejected, dropped, undo, comment), chat (@mention), AI (delegation complete)
6. **[Frontend]** NotificationBell — navbar bell icon with unread count badge (scale-in animation)
7. **[Frontend]** NotificationPanel — floating window with notification items, inline action buttons, click-to-navigate
8. **[Frontend]** WebSocket notification delivery — real-time bell count update + toast on new notification
9. **[Frontend]** EmailPreferencesPanel — floating window from user dropdown, grouped toggles, role-based sections

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Notification API | ~4,000 | api-design.md (notifications) | 3-4 files | Low | — |
| 2 | Creation service | ~5,000 | api-design.md, features.md (F-12.5 events) | 3-4 files | Medium | Event-to-notification mapping |
| 3 | Notification consumer | ~6,000 | api-design.md (events), project-structure.md (notification service) | 4-6 files | Medium | Broker consumer, email dispatch |
| 4 | Email preferences API | ~4,000 | api-design.md, data-model.md (users.email_notification_preferences) | 2-3 files | Low | — |
| 5 | Wire all events | ~8,000 | features.md (F-12.5 full event table) | 8-12 files | High | Many event sources across services |
| 6 | NotificationBell | ~3,000 | component-specs.md (S3.3), component-inventory.md | 2-3 files | Low | — |
| 7 | NotificationPanel | ~5,000 | page-layouts.md (floating windows), component-inventory.md | 3-4 files | Medium | Action buttons, navigation |
| 8 | WS notification delivery | ~4,000 | api-design.md (WS notification events) | 2-3 files | Medium | Real-time badge update |
| 9 | EmailPreferencesPanel | ~5,000 | features.md (F-13.1-13.3), component-inventory.md | 3-4 files | Medium | Grouped toggles, role-based |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~44,000
- **Cumulative domain size:** Medium-Large (notification system + email service + preferences)
- **Information loss risk:** Medium (5)
- **Context saturation risk:** Low-Medium
- **Heavy stories:** 1 (wire all events)

## Milestone Acceptance Criteria
- [ ] Notification bell shows unread count badge
- [ ] Notification panel lists persistent notifications with actions
- [ ] Clicking a notification navigates to relevant context
- [ ] Notifications arrive in real-time via WebSocket
- [ ] Toast notifications appear for transient events
- [ ] Email dispatched for enabled notification types
- [ ] Email preferences panel with grouped toggles per role
- [ ] All notification events from F-12.5 wired (collaboration, review, chat, AI)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M11

## Notes
- Similarity/merge notification events (similar idea detected, merge request, merge accepted/declined) are wired in M13-M14.
- Monitoring alert notifications are wired in M15 (Admin Panel).
- The notification service is a stateless consumer — it reads events from the broker and dispatches.
