# Milestone 5: AI Facilitation

## Overview
- **Execution order:** 5 (runs after M4)
- **Estimated stories:** 9
- **Dependencies:** M4
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.1 | Agent Modes (AI behavior) | Must-have | features.md |
| F-2.2 | Language Detection | Must-have | features.md |
| F-2.3 | Title Generation | Must-have | features.md |
| F-2.4 | Decision Layer | Must-have | features.md |
| F-2.5 | Multi-User Awareness | Must-have | features.md |
| F-2.7 | AI Reactions | Must-have | features.md |
| F-2.10 | AI Response Timing (debounce) | Must-have | features.md |
| F-2.11 | Rate Limiting (counter reset) | Must-have | features.md |
| F-2.12 | AI Processing Indicator | Must-have | features.md |
| F-2.13 | Full State Knowledge | Must-have | features.md |
| F-2.17 | AI Board Content Rules | Must-have | features.md |
| F-3.4 | AI Modification Indicators (wiring) | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| chat_messages | CREATE (AI messages) | sender_type='ai', ai_agent, content, message_type | data-model.md |
| ai_reactions | CREATE | message_id, reaction_type | data-model.md |
| ideas | READ, UPDATE (title) | title, title_manually_edited, state, agent_mode | data-model.md |
| board_nodes | CREATE, UPDATE, DELETE (AI mutations) | created_by='ai', ai_modified_indicator=true | data-model.md |
| board_connections | CREATE, UPDATE, DELETE (AI mutations) | via Board Agent | data-model.md |
| admin_parameters | READ | debounce_timer, ai_processing_timeout, max_retry_attempts, chat_message_cap, recent_message_count | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| AI gRPC: TriggerChatProcessing | gRPC | Gateway triggers AI processing | Internal | api-design.md |
| Core gRPC: GetIdeaContext | gRPC | AI reads idea state | Internal | api-design.md |
| Core gRPC: CreateChatMessage | gRPC | AI persists chat response | Internal | api-design.md |
| Core gRPC: UpdateIdeaTitle | gRPC | AI updates title | Internal | api-design.md |
| Core gRPC: CreateBoardNode, etc. | gRPC | Board Agent mutations | Internal | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| ProcessingIndicator | Component | component-specs.md |
| AIMessage (chat message variant) | Component | component-specs.md |
| AIReaction | Component | component-specs.md |
| TitleAnimation (framer-motion) | Component | component-specs.md |

## AI Agent References

| Agent | Purpose | Source |
|-------|---------|--------|
| Facilitator | Main brainstorming AI — 6 tools, SK function calling, max 3 rounds | agent-architecture.md §3.1 |
| Board Agent | Spatial board operations — 8 tools, SK function calling, max 10 rounds | agent-architecture.md §3.2 |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| AI service: Semantic Kernel setup, BaseAgent, model routing | New | M5 |
| AI service: pipeline orchestrator (debounce, abort, steps 1-7) | New | M5 |
| AI service: context assembler (XML prompt builder) | New | M5 |
| AI service: event publishers (ai.* events) | New | M5 |
| AI guardrails (input validation, output schema enforcement, content filtering) | New | M5 |
| AI security monitoring events (content_filter, jailbreak, injection_pattern, tool_rejection, output_validation_fail) | New | M5 |
| AI application-level caching (admin params, facilitator bucket, SK kernels) | New | M5 |

## Story Outline (Suggested Order)

1. **[AI Service] Semantic Kernel setup + BaseAgent + guardrails** — Configure SK kernel with Azure OpenAI. BaseAgent base class: model routing (default/cheap/escalated tiers), token tracking, timeout handling, retry logic, logging. Model router reads admin parameters for deployment names. AgentInput/AgentOutput Pydantic base classes. AI guardrails: input validation (prompt injection detection, XML escaping), output schema enforcement (Pydantic validation on all agent outputs), Azure OpenAI content filter handling (400 input block → user error, 200 output truncation → retry). AI mock mode infrastructure: AI_MOCK_MODE=True returns fixture responses from services/ai/fixtures/ for E2E testing.
2. **[AI Service] Context assembler + pipeline orchestrator** — Context assembler: builds XML-structured prompt from Core gRPC data (idea metadata, chat summary, recent messages, board state, facilitator bucket). Pipeline orchestrator: implements Steps 1-7 from agent-architecture.md §4.1. Debouncer with abort-and-restart semantics. Version tracking per idea.
3. **[AI Service] Facilitator agent** — FacilitatorAgent(BaseAgent) with 6 SK kernel functions (send_chat_message, react_to_message, update_title, delegate_to_context_agent, delegate_to_context_extension, request_board_changes). System prompt (XML-structured). Max 3 auto-invoke rounds. Decision layer: evaluates value-to-add in Interactive mode. Silent mode: only responds on @ai.
4. **[AI Service] Board Agent** — BoardAgent(BaseAgent) with 8 SK kernel functions (create_node, update_node, delete_node, move_node, resize_group, create_connection, update_connection, delete_connection). System prompt for spatial reasoning. Receives semantic instructions from Facilitator. Max 10 auto-invoke rounds. AI board content rules enforced: one topic per Box, bullet-point format, connections for relationships, Groups for organization.
5. **[AI Service] Event publishing + Gateway event consumption** — AI publishes: ai.chat_response.ready, ai.reaction.ready, ai.title.updated, ai.board.updated, ai.processing.complete, ai.processing.error. Gateway consumes: persists AI chat messages via Core gRPC, persists reactions, updates title, broadcasts all via WebSocket. Core resets rate limit counter on ai.processing.complete.
6. **[Frontend] AI chat responses + reactions** — AI messages render with distinct styling (AI avatar, robot indicator). AI reactions display on user messages (thumbs up/down, heart). Real-time: WebSocket events trigger TanStack Query cache invalidation for new AI messages/reactions.
7. **[Frontend] AI title generation + animation** — Title updates from AI animate in (framer-motion). Title generation disabled when title_manually_edited is true. Browser tab title updates on AI title change.
8. **[Frontend] AI processing indicator + rate limit reset** — "AI is processing" indicator with gentle animation during chat-triggered processing. Visible only during processing (ai.processing.started → ai.processing.complete). Rate limit counter resets when AI completes → chat input unlocks.
9. **[Backend + Frontend] Language detection + multi-user awareness wiring** — Language detection: Facilitator detects language from chat and responds in same language. Initial language from idea creator's app language setting (from user's localStorage preference, sent in idea metadata). Multi-user awareness: Facilitator addresses users by name only when multiple collaborators exist.

## Milestone Acceptance Criteria
- [ ] AI service starts with Semantic Kernel configured and Azure OpenAI connected
- [ ] Facilitator agent processes chat messages and produces appropriate responses
- [ ] Board Agent executes board mutations from Facilitator's semantic instructions
- [ ] Debounce: AI waits configurable seconds after last message before processing
- [ ] Abort-and-restart: new message during processing restarts the cycle
- [ ] AI chat responses appear in real-time via WebSocket
- [ ] AI reactions (thumbs up/down, heart) appear on user messages
- [ ] AI title generation works for new ideas, animates changes
- [ ] Title generation permanently disabled after manual title edit
- [ ] Agent modes: Interactive (AI decides), Silent (AI only on @ai)
- [ ] AI processing indicator shows during processing
- [ ] Rate limit counter resets on AI processing complete, chat unlocks
- [ ] AI board content follows rules (one topic/Box, bullet points, Groups for organization)
- [ ] AI guardrails: input validation rejects prompt injection attempts
- [ ] AI guardrails: output schema enforcement validates all agent outputs via Pydantic
- [ ] AI guardrails: Azure OpenAI content filter errors handled correctly
- [ ] AI mock mode: AI_MOCK_MODE=True returns deterministic fixture responses for E2E
- [ ] AI modification indicators show on AI-created/modified board items
- [ ] Language detection: AI responds in user's language
- [ ] Multi-user awareness: AI addresses by name only with multiple collaborators
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M4

## Notes
- Context Agent delegation and Context Extension delegation are stubbed in the Facilitator's tools — actual implementation in M6. When called, they return "Company context not yet available" / "Extended context search not yet available."
- System prompts for all 9 agents are defined in docs/03-ai/system-prompts.md — implemented as part of each agent's prompt.py module.
- Tool/function schemas for Facilitator (6 tools) and Board Agent (8 tools) are defined in docs/03-ai/tools-and-functions.md — implemented as SK kernel functions.
- Model configuration (generation parameters: temperature, top-p, max output tokens, frequency penalty per agent) from docs/03-ai/model-config.md — configured in BaseAgent and per-agent subclasses.
- Token tracking and monitoring metrics (ai.processing.count, latency, tokens, errors) from docs/03-ai/model-config.md §9 — implemented in BaseAgent and exposed via gRPC for monitoring dashboard.
- Application-level caching (admin parameters 30s TTL, facilitator bucket 5min TTL, SK kernel singletons) from docs/03-ai/model-config.md §5 — implemented in AI service.
- Keyword Agent (Step 5 in pipeline) runs on every cycle but keyword persistence + similarity pipeline come in M10. Keywords are generated and logged but not persisted until M10.
- AI mock mode (AI_MOCK_MODE=true) must work for E2E tests — fixture responses in services/ai/fixtures/.
- This is the highest-complexity milestone. The SK function calling loop, abort-and-restart semantics, and multi-agent coordination are the riskiest parts of the system.
