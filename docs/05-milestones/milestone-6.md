# Milestone 6: WebSocket & Real-Time

## Overview
- **Execution order:** 6 (runs after M3)
- **Estimated stories:** 10
- **Dependencies:** M3
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-6.1 | Session-Level Connection | P1 | features.md FA-6 |
| F-6.2 | Offline Banner | P1 | features.md FA-6 |
| F-6.3 | Presence Tracking | P1 | features.md FA-6 |
| F-6.4 | Multi-User Collaboration (transport layer) | P1 | features.md FA-6 |
| F-6.5 | Offline Behavior | P1 | features.md FA-6 |
| F-6.6 | Connection State Indicator | P1 | features.md FA-6 |
| F-3.5 | Multi-User Board Editing (selection highlights) | P1 | features.md FA-3 |
| F-3.6 | Board Sync (hybrid model) | P1 | features.md FA-3 |
| F-15.1 | Idle Detection (partial) | P2 | features.md FA-15 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| — | No direct DB writes from WebSocket | — | — |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /ws/ | WebSocket | Session-level connection | Token in query param | api-design.md (WebSocket) |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| OfflineBanner | Common | component-inventory.md |
| ConnectionIndicator | Layout | component-specs.md S14 |
| PresenceIndicators | Feature | component-specs.md S9.2 |
| UserSelectionHighlight | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend]** Django Channels WebSocket consumer — connect (token auth), disconnect, error handling
2. **[Backend]** Channel group management — subscribe_idea, unsubscribe_idea messages, group join/leave
3. **[Backend]** Chat message broadcast — on REST POST success, broadcast chat.message.created to idea group
4. **[Backend]** Board sync — broadcast board.node.updated / board.connection.updated after REST persistence
5. **[Backend]** Board awareness events — selection/deselection, lock state changes (WebSocket-only, no persistence)
6. **[Frontend]** WebSocket connection manager — connect on auth, reconnect with exponential backoff, session-level
7. **[Frontend]** Presence tracking — online/idle/offline states, stacked avatars in workspace header, multi-tab dedup
8. **[Frontend]** User selection highlights on board — colored borders with username when another user selects a node
9. **[Frontend]** Offline banner + behavior — "Currently offline" with countdown, chat/board locked, reconnect button
10. **[Frontend]** Connection state indicator — navbar green/red dot + Online/Offline label

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | WS consumer | ~8,000 | api-design.md (WS protocol), tech-stack.md (Channels) | 4-6 files | High | Auth on handshake, error handling |
| 2 | Channel groups | ~4,000 | api-design.md (WS events) | 2-3 files | Medium | Group lifecycle |
| 3 | Chat broadcast | ~4,000 | api-design.md (WS events) | 2-3 files | Medium | Event serialization |
| 4 | Board sync | ~5,000 | tech-stack.md (Board Sync Protocol) | 3-4 files | Medium | Hybrid broadcast model |
| 5 | Board awareness | ~3,000 | api-design.md (WS ephemeral events) | 2-3 files | Low | — |
| 6 | WS connection manager | ~6,000 | tech-stack.md (Connection Lifecycle) | 3-5 files | High | Reconnection, state management |
| 7 | Presence tracking | ~5,000 | features.md (F-6.3), component-specs.md (S9) | 4-5 files | High | Multi-tab dedup, idle states |
| 8 | Selection highlights | ~3,000 | component-inventory.md | 2-3 files | Medium | React Flow custom rendering |
| 9 | Offline banner | ~3,000 | component-specs.md (S11.5), features.md (F-6.2, F-6.5) | 2-3 files | Low | — |
| 10 | Connection indicator | ~2,000 | component-specs.md (S14) | 1-2 files | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~43,000
- **Cumulative domain size:** Medium (WebSocket lifecycle + presence + sync)
- **Information loss risk:** Medium (5)
- **Context saturation risk:** Low-Medium
- **Heavy stories:** 3 (WS consumer, connection manager, presence)

## Milestone Acceptance Criteria
- [ ] WebSocket connects on app load with token authentication
- [ ] Chat messages broadcast in real-time to all subscribers on an idea
- [ ] Board changes broadcast after REST persistence
- [ ] User selections visible to other users with colored borders + names
- [ ] Presence indicators show online/idle users in workspace header
- [ ] Multi-tab shows single presence per user
- [ ] Offline banner appears on connection loss with countdown
- [ ] Chat and board locked during offline state
- [ ] Reconnection with exponential backoff (max configurable)
- [ ] State syncs on reconnect (fetch latest via REST)
- [ ] Connection indicator in navbar shows Online/Offline
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M5

## Notes
- Idle detection is partially implemented (presence state change). Full idle disconnect comes in M16 (Polish).
- The WebSocket consumer handles chat and board events. AI processing events come in M7.
- Notification delivery via WebSocket comes in M12.
