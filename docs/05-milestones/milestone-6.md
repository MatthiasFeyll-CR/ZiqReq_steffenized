# Milestone 6: AI Processing Pipeline

## Overview
- **Wave:** 3
- **Estimated stories:** 10
- **Must complete before starting:** M4, M5
- **Can run parallel with:** None
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.1 | Agent Modes (Interactive/Silent) | P1 | features.md |
| F-2.2 | Language Detection | P1 | features.md |
| F-2.3 | Title Generation | P1 | features.md |
| F-2.4 | Decision Layer | P1 | features.md |
| F-2.10 | AI Response Timing (debounce, abort-and-restart) | P1 | features.md |
| F-2.12 | AI Processing Indicator | P1 | features.md |
| F-2.13 | Full State Knowledge | P1 | features.md |
| F-2.14 | Long Conversation Support (compression + indicator) | P1 | features.md |
| F-2.17 | AI Board Content Rules | P1 | features.md |
| F-5.1 | Keyword Generation | P1 | features.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| chat_messages | READ (via gRPC), CREATE (AI messages) | idea_id, sender_type, ai_agent, content, message_type | data-model.md |
| board_nodes | READ (via gRPC), CREATE/UPDATE (AI mutations) | idea_id, all columns | data-model.md |
| board_connections | READ (via gRPC), CREATE/UPDATE/DELETE (AI mutations) | idea_id, all columns | data-model.md |
| ideas | READ (via gRPC), UPDATE (title) | id, title, title_manually_edited, state, agent_mode | data-model.md |
| chat_context_summaries | CRUD | idea_id, summary_text, messages_covered_up_to_id, compression_iteration | data-model.md |
| idea_keywords | CRUD | idea_id, keywords | data-model.md |
| idea_embeddings | CRUD | idea_id, embedding, source_text_hash | data-model.md |
| facilitator_context_bucket | READ (cached) | content | data-model.md |
| ai_reactions | CREATE (via gRPC) | message_id, reaction_type | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| gRPC TriggerChatProcessing | gRPC | Trigger AI processing for an idea | Internal (gateway → ai) | api-design.md |
| gRPC GetIdeaContext | gRPC | Read idea metadata + chat + board | Internal (ai → core) | api-design.md |
| gRPC PersistChatMessage | gRPC | Save AI chat message | Internal (ai → core) | api-design.md |
| gRPC PersistBoardUpdate | gRPC | Save AI board mutations | Internal (ai → core) | api-design.md |
| gRPC UpdateIdeaTitle | gRPC | Update idea title from AI | Internal (ai → core) | api-design.md |
| gRPC UpdateIdeaKeywords | gRPC | Save generated keywords | Internal (ai → core) | api-design.md |
| GET /api/ideas/:id/context-window | GET | Get context window utilization | User | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Facilitator | Main brainstorming AI — 6 tools, SK function calling | agent-architecture.md §3.1 |
| Board Agent | Spatial board operations — 8 tools, SK function calling | agent-architecture.md §3.2 |
| Keyword Agent | Abstract keyword extraction | agent-architecture.md §3.6 |
| Context Compression | Chat summarization | agent-architecture.md §3.8 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| AIProcessingIndicator | Feature | component-inventory.md |
| ContextWindowIndicator | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend] AI service scaffold + Semantic Kernel + BaseAgent** — AI Django app internal structure per agent-architecture.md §12. BaseAgent class: SK kernel setup (model router for 3 tiers: default/cheap/escalated), token tracking, timeout handling, retry logic per §8.1. SK factory: create configured Kernel instances per agent type. Model router: read admin_parameters (default_ai_model, escalated_ai_model) with env var fallback. Token tracker: per-invocation usage tracking + metrics. AI_MOCK_MODE environment flag for returning fixture responses in E2E tests.
2. **[Backend] Context assembler** — Build XML-structured prompt from raw data. Read idea metadata via Core gRPC GetIdeaContext. Read chat context summary from chat_context_summaries table (AI-owned). Read recent messages via Core gRPC (last N, admin: recent_message_count). Read board state via Core gRPC (all nodes + connections). Read facilitator bucket from facilitator_context_bucket (cached 5min). Assemble into XML per system-prompts.md structure.
3. **[Backend] Facilitator agent** — FacilitatorAgent(BaseAgent) with FacilitatorPlugin: 6 SK kernel functions. Tools: send_chat_message (publishes ai.chat_response.ready), react_to_message (publishes ai.reaction.ready), update_title (publishes ai.title.updated, checks title_manually_edited), delegate_to_context_agent (stub: returns not-available message), delegate_to_context_extension (stub: returns not-available message), request_board_changes (passes instructions to Board Agent). System prompt loaded from system-prompts.md. SK function calling loop max 3 rounds.
4. **[Backend] Board Agent** — BoardAgent(BaseAgent) with BoardPlugin: 8 SK kernel functions. Tools: create_node, update_node, delete_node, move_node, resize_group, create_connection, update_connection, delete_connection. Each mutation persisted via Core gRPC PersistBoardUpdate. Each mutation publishes ai.board.updated event. System prompt loaded from system-prompts.md. SK function calling loop max 10 rounds. Input: Facilitator's semantic instructions JSON + full board state + 5 recent messages.
5. **[Backend] Chat processing pipeline orchestrator** — Pipeline per agent-architecture.md §4.1 (steps 1–7). Step 1: context assembly. Step 2: Facilitator invocation. Step 3a/3b: delegation stubs (skip). Step 4: Board Agent (if board instructions returned). Step 5: Keyword Agent (parallel). Step 6: context window check. Step 7: publish ai.processing.complete. gRPC entry point: TriggerChatProcessing(idea_id, message_id). Event publishing for all ai.* events.
6. **[Backend] Debounce + abort-and-restart** — Debouncer: configurable wait (admin: debounce_timer, default 3s) after last message. If new message during debounce window → restart timer. If new message during processing → set abort flag on running cycle. Running cycle checks abort flag at each step boundary (between steps 2–6). On abort: already-published events stand, unpublished work discarded. New cycle starts with fresh state. Ensure no partial state or duplicate responses.
7. **[Backend+Frontend] Agent mode + title generation + AI reactions** — Agent mode: read ideas.agent_mode. Interactive: AI processes all inputs, decides autonomously. Silent: AI only responds when @ai mentioned (check message content). Title generation (F-2.3): Facilitator's update_title tool auto-generates title from first message, re-evaluates periodically, respects title_manually_edited flag. Frontend: title animation on AI update (framer-motion). AI reactions: Facilitator's react_to_message tool creates ai_reactions via Core gRPC, WebSocket broadcasts reaction.
8. **[Backend] Keyword Agent + idea embeddings pipeline** — KeywordAgent(BaseAgent): input = chat summary + recent messages + board content + current keywords. Output = JSON array of keyword strings (max admin: max_keywords_per_idea). Cheap model tier (GPT-4o-mini). Runs as Step 5 in pipeline (parallel with Board Agent). After keywords generated: persist via Core gRPC UpdateIdeaKeywords. Then: concatenate summary + board titles/content + keywords, embed via text-embedding-3-small, upsert into idea_embeddings table. source_text_hash to skip re-embedding if unchanged.
9. **[Backend] Context Compression + context window check** — ContextCompressionAgent(BaseAgent): input = previous summary + message batch. Output = narrative summary text. Cheap model tier. Step 6 in pipeline: calculate context utilization (summary + recent + board + fixed) / model window. If above admin: context_compression_threshold (default 60%): select oldest uncompressed messages, run compression agent, upsert chat_context_summaries (increment compression_iteration, update messages_covered_up_to_id). GET /api/ideas/:id/context-window endpoint returns utilization data for frontend indicator.
10. **[Frontend] AI integration UI** — AIProcessingIndicator: animated dots in ChatPanel, shown during ai.processing.started → ai.processing.completed WebSocket events. ContextWindowIndicator: filling circle in ChatInput area, shows context utilization %, details on hover (summary tokens, recent tokens, board tokens). Shown when compression_iteration > 0. Wire rate limit counter auto-reset: on ai.processing.completed WebSocket event, clear rate limit lockout. Wire AI title updates: on ai.title.updated WebSocket event, update title in workspace header with animation.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| Chat system (messages, WebSocket) | Available | M4 |
| Board system (nodes, connections, React Flow) | Available | M5 |
| Workspace page shell | Available | M2 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `services/ai/agents/` (all agent subdirectories)
- `services/ai/processing/`
- `services/ai/embedding/`
- `services/ai/kernel/`
- `services/ai/grpc_server/`
- `services/ai/events/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/features/chat/` (add AIProcessingIndicator, ContextWindowIndicator)
- `frontend/src/pages/IdeaWorkspace/` (wire AI title updates)
- `services/gateway/apps/websocket/consumers.py` (add ai.* event broadcasting)
- `services/gateway/apps/chat/` (add rate limit reset on ai.processing.complete)
- `proto/ai.proto` (implement TriggerChatProcessing)
- `proto/core.proto` (implement AI-facing gRPC methods)

## Milestone Acceptance Criteria
- [ ] User sends chat message → AI responds after debounce (3s default)
- [ ] AI creates/modifies board nodes via Board Agent
- [ ] Title auto-generates from first message, re-evaluates, respects manual edit flag
- [ ] Agent mode switch works: Interactive (auto-respond) vs Silent (only on @ai)
- [ ] AI reactions appear on user messages
- [ ] Keywords generated and stored after each processing cycle
- [ ] Idea embeddings generated and stored
- [ ] Context compression triggers when threshold exceeded
- [ ] Context window indicator shows utilization
- [ ] AI processing indicator animates during processing
- [ ] Rate limit resets on AI processing complete
- [ ] Debounce resets on new message during wait
- [ ] Abort-and-restart works: new message during processing restarts cycle
- [ ] AI_MOCK_MODE returns fixture responses
- [ ] No duplicate AI responses
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M5

## Notes
- **Stub: Facilitator delegate_to_context_agent** — Tool exists in FacilitatorPlugin but returns: "I don't have access to company context information yet. I'll help based on what's in our conversation." Delegation message NOT created (no DelegationMessage in chat). Full RAG delegation implemented in M12.
- **Stub: Facilitator delegate_to_context_extension** — Tool exists but returns: "I can't search through earlier parts of our conversation right now. Could you remind me of the detail you're referring to?" Full implementation in M12.
- **Stub: Multi-user AI awareness (F-2.5)** — System prompt includes user names from idea metadata. AI may address users by name but does not intelligently detect single-user vs multi-user mode. Polish in M12.
- **Stub: Board item references from AI (F-2.6)** — AI can mention board item titles in chat text. References are plain text, not clickable links. Clickable navigation implemented in M12.
- **Stub: similarity.detected event** — Keyword Agent generates keywords and embeddings. No similarity.detected event is published. Background matching that publishes this event is in M11.
- **Stub: AI language detection (F-2.2)** — System prompt instructs language matching. Basic implementation works but not polished. Refined in M12.
- **Stub: Notification triggers for AI events** — ai.chat_response.ready, ai.delegation.complete events published to broker. No notification consumer processes them yet. Wired in M10.
