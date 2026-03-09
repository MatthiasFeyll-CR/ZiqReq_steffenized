# Milestone 7: AI Core — Chat Processing Pipeline

## Overview
- **Execution order:** 7 (runs after M5 and M6)
- **Estimated stories:** 10
- **Dependencies:** M5, M6
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.2 | Language Detection | P1 | features.md FA-2 |
| F-2.3 | Title Generation | P1 | features.md FA-2 |
| F-2.4 | Decision Layer | P1 | features.md FA-2 |
| F-2.5 | Multi-User Awareness | P1 | features.md FA-2 |
| F-2.7 | AI Reactions | P1 | features.md FA-2 |
| F-2.10 | AI Response Timing (debounce, abort-and-restart) | P1 | features.md FA-2 |
| F-2.11 | Rate Limiting (counter reset) | P1 | features.md FA-2 |
| F-2.12 | AI Processing Indicator | P1 | features.md FA-2 |
| F-2.13 | Full State Knowledge | P1 | features.md FA-2 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| chat_messages | INSERT (AI messages) | sender_type='ai', ai_agent='facilitator' | data-model.md |
| ai_reactions | INSERT | message_id, reaction_type | data-model.md |
| ideas | UPDATE (title) | title, title_manually_edited | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| TriggerChatProcessing | gRPC | Trigger AI processing for idea | Internal | api-design.md (AI gRPC) |
| GetIdeaContext | gRPC | Read idea state for AI | Internal | api-design.md (Core gRPC) |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Facilitator | Main brainstorming AI — 6 tools, SK function calling | agent-architecture.md S3.1 |

## Story Outline (Suggested Order)
1. **[Backend — AI]** AI service Django setup — Semantic Kernel base (BaseAgent, kernel factory, model router, token tracker)
2. **[Backend — AI]** Facilitator agent implementation — agent.py, prompt.py (XML system prompt), plugins.py (FacilitatorPlugin class)
3. **[Backend — AI]** Chat processing pipeline orchestrator — steps 1-7 skeleton, context assembler, version tracker
4. **[Backend — AI]** Debouncer — configurable timer (admin: debounce_timer), abort-and-restart on new message, abort flag at step boundaries
5. **[Backend — AI]** send_chat_message tool — publish ai.chat_response.ready event, gateway persists + broadcasts
6. **[Backend — AI]** react_to_message tool — publish ai.reaction.ready event, validate user message only
7. **[Backend — AI]** update_title tool — title generation, respect title_manually_edited, publish ai.title.updated
8. **[Backend — Gateway]** AI event consumers — consume ai.chat_response.ready, ai.reaction.ready, ai.title.updated, persist and broadcast via WebSocket
9. **[Frontend]** AI processing indicator — "AI is processing" animation, visible during processing, processing state from WebSocket
10. **[Frontend + Backend]** Rate limit integration — counter tracks messages since last AI completion, lockout at cap, reset on ai.processing.complete

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | AI service setup | ~10,000 | agent-architecture.md (S1, S12), tech-stack.md (SK) | 8-12 files | High | SK kernel config, model routing |
| 2 | Facilitator agent | ~12,000 | agent-architecture.md (S3.1), system-prompts.md, tools-and-functions.md | 4-6 files | High | Complex system prompt, 6 tools |
| 3 | Pipeline orchestrator | ~10,000 | agent-architecture.md (S4.1) | 4-6 files | High | Multi-step pipeline, abort handling |
| 4 | Debouncer | ~5,000 | agent-architecture.md (S4.1 debounce) | 2-3 files | Medium | Concurrent state management |
| 5 | send_chat_message | ~4,000 | tools-and-functions.md (S1) | 2-3 files | Low | — |
| 6 | react_to_message | ~3,000 | tools-and-functions.md (S2) | 2-3 files | Low | — |
| 7 | update_title | ~3,000 | tools-and-functions.md (S3) | 2-3 files | Low | — |
| 8 | AI event consumers | ~6,000 | api-design.md (events), agent-architecture.md | 4-6 files | Medium | Event handling chain |
| 9 | Processing indicator | ~3,000 | component-specs.md (S5.4) | 2-3 files | Low | — |
| 10 | Rate limit | ~5,000 | features.md (F-2.11), api-design.md | 3-5 files | Medium | Concurrent counter accuracy |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~61,000
- **Cumulative domain size:** Large (AI service + pipeline + events + frontend indicators)
- **Information loss risk:** Medium (6) — cross-domain stories (AI + Gateway + Frontend)
- **Context saturation risk:** Medium
- **Heavy stories:** 3 (AI service setup, Facilitator agent, pipeline orchestrator)

## Milestone Acceptance Criteria
- [ ] AI service boots with Semantic Kernel configured
- [ ] Facilitator agent invokes successfully with mock Azure OpenAI
- [ ] Chat processing pipeline runs end-to-end: message → debounce → Facilitator → events → broadcast
- [ ] Debounce: new message during timer restarts the timer
- [ ] Abort-and-restart: new message during processing aborts current cycle
- [ ] AI chat responses appear in real-time via WebSocket
- [ ] AI reactions appear on user messages
- [ ] AI generates/updates title (unless manually edited)
- [ ] AI responds in the user's language
- [ ] AI processing indicator shows during processing
- [ ] Rate limit: chat locks after cap, unlocks on AI completion
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M6

## Notes
- This milestone is the highest-risk in the project. The AI service setup, SK function calling loop, pipeline orchestration, and debounce/abort logic are all complex.
- Board Agent tool (request_board_changes) is registered but not implemented until M8.
- Delegation tools (delegate_to_context_agent, delegate_to_context_extension) are registered but return "not available" until M8.
- Testing uses mocked Azure OpenAI responses (fixture files).
