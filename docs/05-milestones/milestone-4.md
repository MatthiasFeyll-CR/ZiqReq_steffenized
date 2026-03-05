# Milestone 4: Chat System

## Overview
- **Wave:** 2
- **Estimated stories:** 8
- **Must complete before starting:** M1, M2
- **Can run parallel with:** M5
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.7 | AI Reactions | P1 | features.md |
| F-2.8 | User Reactions | P1 | features.md |
| F-2.9 | @Mentions System | P1 | features.md |
| F-2.11 | Rate Limiting | P1 | features.md |
| F-2.12 | AI Processing Indicator (partial — UI only) | P1 | features.md |
| F-6.4 | Multi-User Chat Broadcast (real-time) | P1 | features.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| chat_messages | CREATE, READ | id, idea_id, sender_type, sender_id, ai_agent, content, message_type, created_at | data-model.md |
| ai_reactions | CREATE, READ | id, message_id, reaction_type | data-model.md |
| user_reactions | CRUD | id, message_id, user_id, reaction_type | data-model.md |
| ideas | READ | id, state (for locking check) | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/ideas/:id/chat | POST | Send chat message | User (owner/collaborator) | api-design.md |
| GET /api/ideas/:id/chat | GET | List chat messages (paginated) | User (any access) | api-design.md |
| POST /api/ideas/:id/chat/:msgId/reactions | POST | Add user reaction | User | api-design.md |
| DELETE /api/ideas/:id/chat/:msgId/reactions | DELETE | Remove user reaction | User (own reaction) | api-design.md |
| GET /api/ideas/:id/chat/:msgId/reactions | GET | Get reactions for message | User | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| ChatPanel | Feature | component-inventory.md |
| ChatMessage | Feature | component-inventory.md |
| UserMessageBubble | Feature | component-inventory.md |
| AIMessageBubble | Feature | component-inventory.md |
| DelegationMessage | Feature | component-inventory.md |
| AIProcessingIndicator | Feature | component-inventory.md |
| ReactionChips | Feature | component-inventory.md |
| MentionDropdown | Feature | component-inventory.md |
| ChatInput | Feature | component-inventory.md |
| RateLimitOverlay | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API] Chat messages REST API** — POST /api/ideas/:id/chat (create message, validate idea access, check idea not locked per state, check rate limit). GET /api/ideas/:id/chat (paginated, ordered by created_at ASC, cursor-based pagination). DRF serializers with sender info (user display_name, avatar initials). Immutable messages — no UPDATE/DELETE. gRPC PersistChatMessage in Core service for AI-created messages.
2. **[Frontend] Chat panel UI** — ChatPanel component in workspace left panel (replaces M2 placeholder). Message list with auto-scroll to bottom on new messages. Scroll-to-bottom button when scrolled up. Timestamp grouping (today, yesterday, date). Loading skeleton on initial load. Infinite scroll upward for history (cursor pagination).
3. **[Frontend] Message bubbles** — UserMessageBubble (right-aligned, teal/gold background per design-system.md). AIMessageBubble (left-aligned, card background, subtle border, robot avatar). DelegationMessage (de-emphasized variant — muted colors, smaller text, italic). Display sender name, timestamp, content with markdown support.
4. **[WebSocket] Chat real-time events** — On message creation: publish `chat.message.created` event to idea channel group via WebSocket. All subscribed clients receive the event and append to message list. Optimistic update on sender side (show immediately, confirm on broadcast). Handle out-of-order delivery gracefully.
5. **[Frontend] @mentions system** — MentionDropdown: typing `@` in ChatInput opens suggestion dropdown. Lists all users with access to the idea + `@ai`. Filter as user types. Selection inserts `@username` or `@ai` into message. Store mentions in message content as plain text. Highlight @mentions in rendered messages with distinct styling.
6. **[Frontend+API] User reactions** — POST/DELETE endpoints for user reactions. ReactionChips component below user messages (not AI messages). Enforce: can't react to own messages, can't react to AI messages (application-level). One reaction per user per message (UNIQUE constraint). Three reaction types: 👍, 👎, ❤️. Toggle behavior (click again to remove). WebSocket broadcast on reaction change.
7. **[Frontend+API] AI reactions display** — AI reactions rendered below user messages (read-only for users). ReactionChips with AI indicator. AI reactions created via gRPC (by AI service in M6). API supports creating ai_reactions via internal gRPC only (not REST-exposed for user creation). One AI reaction per message max.
8. **[Frontend+API] Chat rate limiting** — Backend: track message count per idea since last AI processing complete. On POST /api/ideas/:id/chat: if count >= admin_parameter('chat_message_cap'), return 429. Frontend: RateLimitOverlay on ChatInput when locked out. Warning toast on lockout (F-12.5). WebSocket broadcasts `chat.rate_limited` and `chat.rate_limit_cleared` events. Counter reset mechanism exposed via internal API (called by AI service in M6 on ai.processing.complete).

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Toast | Available | M1 |
| Workspace page shell | Available | M2 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/features/chat/`
- `services/gateway/apps/chat/`
- `services/core/apps/chat/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/pages/IdeaWorkspace/` (replace ChatPanel placeholder with real component)
- `services/gateway/apps/websocket/consumers.py` (add chat event broadcasting)
- `proto/core.proto` (add PersistChatMessage if not already stubbed)

## Milestone Acceptance Criteria
- [ ] Chat messages send and persist to database
- [ ] Messages appear in real-time for all connected users via WebSocket
- [ ] Message bubbles render correctly (user vs AI vs delegation variants)
- [ ] @mentions dropdown appears on typing @, selection inserts mention
- [ ] User reactions: add/remove works, enforces one-per-user-per-message
- [ ] Cannot react to own messages or AI messages
- [ ] AI reactions display correctly (read-only)
- [ ] Rate limiting: 429 after cap reached, RateLimitOverlay displays, lockout toast shown
- [ ] Rate limit counter reset endpoint works
- [ ] Chat pagination loads history correctly
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1, M2

## Notes
- **Stub: AI message creation** — AI messages can be created via gRPC PersistChatMessage (sender_type='ai', ai_agent='facilitator'). No AI agent generates them yet — the Facilitator (M6) will call send_chat_message tool which publishes through this gRPC. For testing, manually create AI messages via admin/shell.
- **Stub: @ai mention triggering AI response** — @ai is parsed and stored in message content. No AI processing is triggered. In M6, the pipeline checks for @ai mentions to force a response in silent mode.
- **Stub: Rate limit counter auto-reset** — Counter is reset via an internal endpoint/gRPC call. In M6, the ai.processing.complete event handler calls this to auto-reset. For testing in M4, reset manually.
- **Stub: AIProcessingIndicator** — Component exists in ChatPanel but is never shown (no AI processing yet). Triggered by WebSocket `ai.processing.started`/`ai.processing.completed` events in M6.
- **Stub: ContextWindowIndicator** — Space reserved in ChatInput area. Component hidden. Shown when chat_context_summaries data exists (M6).
- **Stub: Notification for @mentions** — @mention is parsed but no notification is dispatched. Persistent notification created in M10.
- **Stub: First message from landing page** — When navigating from landing page hero section (M2), the first message text should be sent as a chat message via POST /api/ideas/:id/chat immediately after idea creation. Wire this in M4: landing page creation flow calls ideas API then chat API sequentially.
