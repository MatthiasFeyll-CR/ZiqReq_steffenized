# Milestone 12: Company Context & AI Polish

## Overview
- **Wave:** 4
- **Estimated stories:** 7
- **Must complete before starting:** M6
- **Can run parallel with:** M7, M8
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.5 | Multi-User AI Awareness | P1 | features.md |
| F-2.6 | Board Item References in Chat | P1 | features.md |
| F-2.15 | Company Context Retrieval (RAG) | P1 | features.md |
| F-2.16 | Admin Context Management (AI wiring) | P1 | features.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| context_agent_bucket | READ | sections, free_text | data-model.md |
| context_chunks | CRUD | bucket_id, chunk_text, section_name, embedding, chunk_order | data-model.md |
| facilitator_context_bucket | READ (already cached in M6) | content | data-model.md |
| chat_context_summaries | READ (already used in M6) | summary_text | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| gRPC UpdateContextAgentBucket | gRPC | Trigger RAG re-indexing on bucket save | Internal (gateway → ai) | api-design.md |
| gRPC UpdateFacilitatorBucket | gRPC | Notify AI of facilitator bucket update | Internal (gateway → ai) | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Context Agent | Company context retrieval via RAG | agent-architecture.md §3.3 |
| Context Extension | Full chat history search for lost references | agent-architecture.md §3.4 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| DelegationMessage | Feature (render variant) | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend] Context Agent** — ContextAgent(BaseAgent): system prompt (minimal), input = delegation query + retrieved chunks + brief idea context (title, recent topic). Output = structured findings summary with source references. Default model tier. No tools. Failure mode: no retry, Facilitator responds without company context on failure.
2. **[Backend] RAG indexing pipeline** — Triggered by gRPC UpdateContextAgentBucket (wires M3 Admin save → AI re-index). Chunker: parse sections from context_agent_bucket.sections JSONB, each named section = one chunk (preserve admin boundaries). Free text (context_agent_bucket.free_text) chunked at ~500 tokens with 50-token overlap. Embedder: embed each chunk via text-embedding-3-small. Reindexer: upsert into context_chunks table, remove old chunks for deleted/modified sections. HNSW index on embedding column for fast similarity search.
3. **[Backend] Context Agent delegation flow** — Wire Facilitator's `delegate_to_context_agent` tool (replace M6 stub). On tool call: pipeline orchestrator embeds the query via text-embedding-3-small, pgvector similarity search on context_chunks (top-K: admin context_rag_top_k, min similarity: admin context_rag_min_similarity). Pass retrieved chunks to Context Agent. Context Agent generates findings. Pipeline runs second Facilitator pass with findings injected as `<delegation_results>` in context. Original delegation message de-emphasized → ai.delegation.complete event.
4. **[Backend] Context Extension agent** — ContextExtensionAgent(BaseAgent): system prompt (minimal), input = Facilitator's search query + full uncompressed chat history (via Core gRPC GetFullChatHistory) + board state for cross-referencing. Output = targeted answer with relevant quotes from full history. Escalated model tier (extended context budget for 80K+ token histories). No retry on failure.
5. **[Backend] Context Extension delegation flow** — Wire Facilitator's `delegate_to_context_extension` tool (replace M6 stub). On tool call: load full uncompressed chat via Core gRPC GetFullChatHistory. Pass to Context Extension agent. Agent searches history for referenced detail. Pipeline runs second Facilitator pass with extension results injected as `<extension_results>` in context. Original delegation message de-emphasized.
6. **[Frontend] Delegation message UI** — DelegationMessage rendering in ChatPanel: when delegation occurs, placeholder message appears immediately (e.g., "Searching company context..." or "Searching conversation history..."). Visually de-emphasized (muted colors, smaller text, italic). After delegation complete: full AI response message follows. Delegation message retains de-emphasized styling. Both messages linked visually (timeline connection or grouping).
7. **[Backend+Frontend] AI polish** — Board item references in chat: when AI mentions a board node by title, render as clickable link in chat message. Click navigates to Board tab and highlights/zooms to the referenced node. Parse board node references from AI message content (match against current board node titles). Multi-user AI awareness (F-2.5): AI detects single-user vs multi-user via collaborator count + presence data. Single user: no name addressing. Multi-user: address users by name, track who said what in context. AI language detection polish (F-2.2): detect user's language from message content + i18n preference, match response language. AI board content rules enforcement (F-2.17): board content uses concise language (max 15 words per title, max 80 words per body), no markdown, no special formatting.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| AI service scaffold + pipeline | Available | M6 |
| Facilitator with 6 tools | Available | M6 |
| ChatPanel + message rendering | Available | M4 |
| Board canvas | Available | M5 |
| Admin AI Context tab | Available | M3 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `services/ai/agents/context_agent/`
- `services/ai/agents/context_extension/`
- `services/ai/embedding/chunker.py` (implementation)
- `services/ai/embedding/embedder.py` (implementation)
- `services/ai/embedding/reindexer.py` (implementation)
- `frontend/src/features/delegation/`

Shared files (merge-conflict-aware — keep changes additive):
- `services/ai/agents/facilitator/plugins.py` (replace delegate stub implementations)
- `services/ai/processing/pipeline.py` (add delegation steps 3a, 3b)
- `services/ai/grpc_server/servicer.py` (implement UpdateContextAgentBucket, UpdateFacilitatorBucket)
- `frontend/src/features/chat/` (add DelegationMessage rendering, board item reference links)
- `services/gateway/apps/admin/` (add gRPC call on AI context save)

## Milestone Acceptance Criteria
- [ ] Context Agent retrieves relevant company context via RAG
- [ ] RAG re-indexes on admin bucket save (end-to-end: save in Admin → chunks updated)
- [ ] Context delegation flow: Facilitator delegates → placeholder message → findings → full response
- [ ] Context Extension searches full chat history and returns relevant detail
- [ ] Extension delegation flow works end-to-end
- [ ] Delegation messages render de-emphasized in chat
- [ ] Board item references in AI chat messages are clickable (navigate to Board + highlight)
- [ ] Multi-user AI awareness: addresses users by name in multi-user mode
- [ ] AI language detection matches user's language
- [ ] AI board content follows conciseness rules
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M6

## Notes
- No stubs — M12 is a leaf milestone with no downstream dependencies.
- The delegation message UI (DelegationMessage component) was already defined in M4's message bubble variants but never rendered with real data. M12 wires it to actual delegation events.
- RAG re-indexing performance: for the expected corpus size (hundreds of chunks), a full re-index on bucket save is acceptable. No incremental indexing needed.
- Context Extension uses escalated model tier — ensure AZURE_OPENAI_ESCALATED_DEPLOYMENT env var is configured.
