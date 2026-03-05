# Milestone 3: Workspace + Chat + Real-Time

## Overview
- **Execution order:** 3 (runs after M2)
- **Estimated stories:** 10
- **Dependencies:** M2
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-1.1 | Idea Page Layout | Must-have | features.md |
| F-1.2 | Section Visibility | Must-have | features.md |
| F-1.4 | Section Locking | Must-have | features.md |
| F-1.5 | Idea Lifecycle (state machine) | Must-have | features.md |
| F-1.6 | Inline Title Editing | Must-have | features.md |
| F-1.7 | UUID-Based Routing | Must-have | features.md |
| F-1.8 | Browser Tab Title | Must-have | features.md |
| F-2.1 | Agent Modes (UI only) | Must-have | features.md |
| F-2.8 | User Reactions | Must-have | features.md |
| F-2.9 | @Mentions System (UI only) | Must-have | features.md |
| F-2.11 | Rate Limiting (UI lockout) | Must-have | features.md |
| F-6.1 | Session-Level Connection | Must-have | features.md |
| F-6.2 | Offline Banner | Must-have | features.md |
| F-6.3 | Presence Tracking | Must-have | features.md |
| F-6.4 | Multi-User Collaboration (chat) | Must-have | features.md |
| F-6.5 | Offline Behavior | Must-have | features.md |
| F-6.6 | Connection State Indicator | Must-have | features.md |
| F-15.1 | Idle Detection | Must-have | features.md |
| F-15.2 | Connection Disconnect on Idle | Must-have | features.md |
| F-15.3 | Return from Idle | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | READ, UPDATE (title, state, agent_mode) | id, title, state, title_manually_edited, agent_mode, visibility | data-model.md |
| chat_messages | CREATE, READ | idea_id, sender_type, sender_id, content, message_type, created_at | data-model.md |
| user_reactions | CREATE, DELETE, READ | message_id, user_id, reaction_type | data-model.md |
| users | READ | id, display_name | data-model.md |
| admin_parameters | READ | idle_timeout, idle_disconnect, max_reconnection_backoff, chat_message_cap | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id | GET | Get full idea detail | Bearer/bypass | api-design.md |
| /api/ideas/:id | PATCH | Update title, agent_mode | Bearer/bypass | api-design.md |
| /api/ideas/:id/chat | GET | Get chat messages (paginated) | Bearer/bypass | api-design.md |
| /api/ideas/:id/chat | POST | Send chat message | Bearer/bypass | api-design.md |
| /api/ideas/:id/chat/:mid/reactions | POST | Add user reaction | Bearer/bypass | api-design.md |
| /api/ideas/:id/chat/:mid/reactions | DELETE | Remove user reaction | Bearer/bypass | api-design.md |
| /ws/ | WebSocket | Real-time connection | Token in query param | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| IdeaWorkspace | Page | page-layouts.md §4 |
| DraggableDivider | Component | component-specs.md |
| ChatPanel | Component | page-layouts.md §4, component-specs.md |
| ChatMessageList | Component | component-specs.md |
| ChatMessage | Component | component-specs.md |
| ChatInput | Component | component-specs.md |
| MentionSuggestions | Component | component-specs.md |
| ReactionButton | Component | component-specs.md |
| InlineTitle | Component | component-specs.md |
| AgentModeDropdown | Component | component-specs.md |
| PresenceIndicators | Component | component-specs.md |
| ConnectionIndicator | Component (navbar) | component-specs.md |
| OfflineBanner | Component | component-specs.md |
| RateLimitBanner | Component | component-specs.md |
| StateBadge | Component | component-specs.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| WebSocket Provider (connection lifecycle, reconnection) | New | M3 |
| Redux slices: WebSocket state, presence, UI layout | New | M3 |
| Idle detection hook | New | M3 |

## Story Outline (Suggested Order)

1. **[Backend] Chat message CRUD APIs** — Gateway REST: GET /api/ideas/:id/chat (paginated, ordered by created_at), POST /api/ideas/:id/chat (persist via Core gRPC, publish chat.message.created event). Core gRPC servicer: CreateChatMessage, GetChatMessages.
2. **[Backend] User reaction APIs** — Gateway REST: POST /api/ideas/:id/chat/:mid/reactions (add reaction), DELETE (remove). Validation: can only react to other users' messages, not AI messages. One reaction per user per message.
3. **[Backend] WebSocket consumer** — Django Channels consumer: authenticate on connect (token from query param), subscribe_idea/unsubscribe_idea messages, broadcast chat messages to idea group, presence updates (join/leave/idle). Channel layer via Redis.
4. **[Frontend] Idea workspace layout** — Two-panel layout with draggable divider (left: chat, right: tab panel with Board/Review tabs). Header area: inline title, agent mode dropdown, presence indicators, collaborator management placeholder. UUID-based routing (/idea/:uuid).
5. **[Frontend] Chat panel** — Scrollable chat message list (user + AI messages with avatars, timestamps, sender info). Chat input with send button. Auto-scroll to latest message. Empty state for new ideas.
6. **[Frontend] WebSocket provider + connection lifecycle** — WebSocket connection on app load (session-level). Subscribe to idea on workspace enter, unsubscribe on leave. Reconnection with exponential backoff (max from admin param). Redux slice for connection state.
7. **[Frontend] Real-time chat + user reactions** — WebSocket receives chat.message.created → TanStack Query cache invalidation → new message appears. User reaction UI: thumbs up/down, heart on other users' messages. Optimistic updates.
8. **[Frontend] Presence tracking + connection indicator** — Presence indicators in workspace header (online/idle avatars). Connection state indicator in navbar (green Online / red Offline). WebSocket presence events (join, idle, leave).
9. **[Frontend] Offline handling + idle detection** — Offline banner on connection loss ("Currently offline. Retrying in X seconds" + manual reconnect). Chat + board locked when offline. Idle detection: no mouse movement → idle after timeout → disconnect after prolonged idle. Return from idle: reconnect, sync state, dismiss banner.
10. **[Frontend] State machine + section visibility + locking + @mentions + rate limiting** — Idea state logic (open/in_review/accepted/dropped/rejected). Section visibility: review section hidden until submitted. Section locking per state. @mention dropdown (lists connected users + @ai, inserts @reference). Agent mode toggle (Interactive/Silent). Rate limit lockout UI (chat locked at cap, "AI is processing" note). Inline title editing with browser tab title sync.

## Milestone Acceptance Criteria
- [ ] Idea workspace renders two-panel layout with draggable divider
- [ ] Chat messages display correctly with sender info and timestamps
- [ ] Sending a message persists via API and broadcasts to other users via WebSocket
- [ ] User reactions work (add/remove thumbs up/down, heart) with validation rules
- [ ] WebSocket connects with auth token, reconnects on disconnect with backoff
- [ ] Presence indicators show online/idle users in workspace header
- [ ] Connection state indicator in navbar shows Online/Offline
- [ ] Offline banner appears on disconnect, manual reconnect button works
- [ ] Idle detection: user goes idle after timeout, disconnects after prolonged idle
- [ ] @mention dropdown shows connected users + @ai
- [ ] Agent mode dropdown toggles Interactive/Silent
- [ ] Rate limiting UI: chat input locks at message cap
- [ ] Idea state machine: correct section visibility and locking per state
- [ ] Inline title editing works, updates browser tab title
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M2

## Notes
- AI responses won't appear yet (AI service comes in M5). Chat is user-to-user only in this milestone.
- Board tab and Review tab render as empty placeholders — content in M4 and M7.
- Rate limiting locks the UI but counter reset (on AI completion) comes in M5.
- @mention dropdown shows users but @ai trigger functionality comes in M5.
- Section locking logic is implemented but submit/review state transitions come in M7/M8.
- Collaborator management area is a placeholder — full functionality in M9.
