# Milestone 3: Idea Workspace — Layout & Chat

## Overview
- **Execution order:** 3 (runs after M2)
- **Estimated stories:** 10
- **Dependencies:** M2
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-1.1 | Idea Page Layout | P1 | features.md FA-1 |
| F-1.2 | Section Visibility | P1 | features.md FA-1 |
| F-1.3 | Auto-Scroll on State Transition | P2 | features.md FA-1 |
| F-1.4 | Section Locking | P1 | features.md FA-1 |
| F-1.6 | Inline Title Editing | P1 | features.md FA-1 |
| F-1.7 | UUID-Based Routing | P1 | features.md FA-1 |
| F-1.8 | Browser Tab Title | P1 | features.md FA-1 |
| F-2.1 | Agent Modes (dropdown, no AI yet) | P1 | features.md FA-2 |
| F-2.8 | User Reactions | P1 | features.md FA-2 |
| F-2.9 | @Mentions System (UI only) | P1 | features.md FA-2 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | SELECT, UPDATE (title, agent_mode) | id, title, title_manually_edited, state, agent_mode | data-model.md |
| chat_messages | INSERT, SELECT | id, idea_id, sender_type, sender_id, content, created_at | data-model.md |
| user_reactions | INSERT, DELETE, SELECT | message_id, user_id, reaction_type | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id | GET | Full idea data for workspace | Bearer | api-design.md |
| /api/ideas/:id | PATCH | Update title, agent_mode | Bearer | api-design.md |
| /api/ideas/:id/chat | GET | List chat messages | Bearer | api-design.md |
| /api/ideas/:id/chat | POST | Send chat message | Bearer | api-design.md |
| /api/ideas/:id/chat/:msgId/reactions | POST | Add user reaction | Bearer | api-design.md |
| /api/ideas/:id/chat/:msgId/reactions | DELETE | Remove user reaction | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Idea Workspace (/idea/:uuid) | Page | page-layouts.md S2 |
| PanelDivider | Layout | component-specs.md S13 |
| ChatPanel | Feature | component-inventory.md |
| ChatMessage (User/AI bubbles) | Feature | component-specs.md S5 |
| ChatInput | Feature | component-specs.md S5.8 |
| ReactionChips | Feature | component-specs.md S5.5 |
| MentionDropdown | Feature | component-specs.md S5.6 |
| RateLimitOverlay | Feature | component-specs.md S5.8 |

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Built | M1 |
| IdeaCard | Built | M2 |

## Story Outline (Suggested Order)
1. **[API]** Chat messages REST API — POST (send), GET (list with pagination)
2. **[API]** User reactions REST API — POST (add), DELETE (remove), validation (user messages only, not own)
3. **[Frontend — Page]** Workspace page structure — /idea/:uuid route, two-section vertical layout, GET idea data
4. **[Frontend — Layout]** Two-panel layout with draggable divider — chat left, tabs right (Board placeholder, Review placeholder), localStorage persistence
5. **[Frontend — Header]** Workspace header — inline title editing (with title_manually_edited flag), agent mode dropdown, presence area placeholder, back button
6. **[Frontend — Feature]** Section visibility + locking — review hidden until submitted, locking per state (open/in_review/rejected/accepted/dropped)
7. **[Frontend — Component]** Chat message display — UserMessageBubble, AIMessageBubble, DelegationMessage, message list with scroll-to-bottom
8. **[Frontend — Component]** ChatInput with send button — POST /api/ideas/:id/chat, auto-grow textarea, disabled states
9. **[Frontend — Component]** @Mention dropdown — triggered by @, lists users in idea + @ai, keyboard navigation, filter
10. **[Frontend — Component]** User reactions — ReactionChips below messages, add/remove toggle, validation (not on AI messages)

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Chat messages API | ~5,000 | api-design.md (chat), data-model.md (chat_messages) | 4-6 files | Low | — |
| 2 | User reactions API | ~4,000 | api-design.md (reactions), data-model.md | 3-4 files | Low | Validation rules |
| 3 | Workspace page | ~6,000 | page-layouts.md (S2), api-design.md | 3-5 files | Medium | Complex layout |
| 4 | Two-panel layout | ~5,000 | component-specs.md (S13), page-layouts.md | 3-4 files | Medium | Draggable divider |
| 5 | Workspace header | ~5,000 | page-layouts.md (header), features.md (F-1.6) | 4-5 files | Medium | Inline editing |
| 6 | Section visibility | ~4,000 | features.md (F-1.2, F-1.4) | 2-3 files | Medium | State machine logic |
| 7 | Chat message display | ~5,000 | component-specs.md (S5.1-5.3) | 4-5 files | Medium | Multiple variants |
| 8 | ChatInput | ~4,000 | component-specs.md (S5.8) | 2-3 files | Low | — |
| 9 | @Mention dropdown | ~4,000 | component-specs.md (S5.6) | 2-3 files | Medium | Keyboard nav, filter |
| 10 | User reactions | ~3,000 | component-specs.md (S5.5), features.md (F-2.8) | 2-3 files | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~45,000
- **Cumulative domain size:** Medium (workspace + chat + reactions)
- **Information loss risk:** Low (3)
- **Context saturation risk:** Low
- **Heavy stories:** 0

## Milestone Acceptance Criteria
- [ ] Workspace page loads at /idea/:uuid with correct idea data
- [ ] Two-panel layout with functional draggable divider
- [ ] Inline title editing works, sets title_manually_edited flag on manual edit
- [ ] Agent mode dropdown toggles between Interactive/Silent
- [ ] Chat messages can be sent and appear in real-time (via polling, WebSocket in M6)
- [ ] User message bubbles right-aligned, AI bubbles left-aligned
- [ ] @mention dropdown appears on typing @, lists users + @ai
- [ ] User reactions can be added/removed on other users' messages (not AI, not own)
- [ ] Section visibility: review hidden when never submitted
- [ ] Section locking per idea state works correctly
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M2

## Notes
- Board tab shows a placeholder until M4. Review tab shows a placeholder until M9.
- Chat currently uses polling for updates. WebSocket broadcast comes in M6.
- AI message display is prepared but no AI generates messages until M7.
- Auto-scroll on state transition (F-1.3) is partially implemented here (scroll logic) but full state transitions come in M10.
