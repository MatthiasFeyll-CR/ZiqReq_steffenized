# Milestone 6: AI Context & Knowledge

## Overview
- **Execution order:** 6 (runs after M5)
- **Estimated stories:** 7
- **Dependencies:** M5
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.14 | Long Conversation Support | Must-have | features.md |
| F-2.15 | Company Context Awareness | Must-have | features.md |
| F-2.6 | Board Item References in Chat (AI resolution) | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| chat_context_summaries | CREATE, UPDATE, READ | idea_id, summary_text, messages_covered_up_to_id, compression_iteration | data-model.md |
| facilitator_context_bucket | READ | content | data-model.md |
| context_agent_bucket | READ | sections, free_text | data-model.md |
| context_chunks | CREATE (bulk), DELETE (bulk), READ | chunk_text, embedding, source_section, token_count | data-model.md |
| chat_messages | READ (full history for Context Extension) | all columns | data-model.md |
| admin_parameters | READ | context_compression_threshold, recent_message_count, context_rag_top_k, context_rag_min_similarity | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/context-window | GET | Get context utilization for working memory indicator | Bearer/bypass | api-design.md |
| Core gRPC: GetFullChatHistory | gRPC | Full uncompressed chat for Context Extension | Internal | api-design.md |
| AI gRPC: UpdateFacilitatorBucket | gRPC | Admin updates facilitator context | Internal | api-design.md |
| AI gRPC: UpdateContextAgentBucket | gRPC | Admin updates detailed context (triggers re-indexing) | Internal | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| WorkingMemoryIndicator | Component | component-specs.md |
| DelegationMessage (de-emphasized chat message) | Component | component-specs.md |
| BoardRefLink (clickable board reference in chat) | Component | component-specs.md |

## AI Agent References

| Agent | Purpose | Source |
|-------|---------|--------|
| Context Agent | Company context retrieval via RAG | agent-architecture.md §3.3 |
| Context Extension | Full chat history search for lost references | agent-architecture.md §3.4 |
| Context Compression | Chat summarization for long conversations | agent-architecture.md §3.8 |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| RAG pipeline (chunker, embedder, reindexer) | New | M6 |
| Embedding utility (Azure OpenAI text-embedding-3-small) | New | M6 |
| Context window calculator | New | M6 |
| Context Extension output validation (fabrication flag for unverifiable quotes) | New | M6 |
| Context Agent output validation (source traceability against chunks) | New | M6 |

## Story Outline (Suggested Order)

1. **[AI Service] RAG indexing pipeline** — Chunker: parse context_agent_bucket sections → one chunk per named section. Free text → chunked at ~500 tokens with 50-token overlap. Embedder: embed each chunk via text-embedding-3-small → upsert into context_chunks. Reindexer: on bucket update, delete old chunks → insert new chunks. HNSW index on embedding column for fast similarity search.
2. **[AI Service] Context Agent** — ContextAgent(BaseAgent). On Facilitator delegation: embed query → pgvector top-K similarity search on context_chunks (admin: context_rag_top_k, context_rag_min_similarity) → Context Agent generates findings from retrieved chunks. Return findings to pipeline orchestrator.
3. **[AI Service] Context Agent delegation flow** — Wire Facilitator's delegate_to_context_agent tool. Pipeline orchestrator: Facilitator first pass → delegation requested → publish delegation placeholder message (de-emphasized) → Context Agent runs → second Facilitator pass with findings injected as <delegation_results> → contextualized response published → delegation message de-emphasized (ai.delegation.complete event).
4. **[AI Service] Context Extension agent + delegation flow** — ContextExtensionAgent(BaseAgent) with escalated model tier. On Facilitator delegation: load full uncompressed chat via Core gRPC GetFullChatHistory → search for referenced detail → return findings. Wire delegate_to_context_extension tool. Second Facilitator pass with <extension_results>. Failure mode: "Couldn't retrieve that detail."
5. **[AI Service] Context Compression agent** — ContextCompressionAgent(BaseAgent) with cheap model tier. Pipeline Step 6: after Facilitator/Board Agent complete, calculate context utilization. If > threshold (admin: context_compression_threshold, default 60%): select oldest uncompressed messages → compress into narrative summary → upsert chat_context_summaries (merge with previous summary, increment compression_iteration, update messages_covered_up_to_id).
6. **[Backend + Frontend] Working memory indicator** — Backend: GET /api/ideas/:id/context-window returns context utilization stats (summary exists, compression_iteration, estimated usage %). Frontend: filling circle indicator in chat panel showing working memory usage. Hover for details (compression count, estimated tokens). Updates when summary changes.
7. **[Frontend] Delegation messages + board item references** — Delegation message styling: de-emphasized appearance for placeholder messages (message_type='delegation'). Final response appears normally. Board item references in AI chat messages: clickable links that navigate to Board tab and highlight the referenced item. AI resolves board item references mentioned by users in chat.

## Milestone Acceptance Criteria
- [ ] RAG indexing: admin bucket content is chunked, embedded, and stored in context_chunks
- [ ] Context Agent retrieves relevant chunks and generates grounded findings
- [ ] Delegation flow: placeholder → Context Agent → second Facilitator pass → contextualized response
- [ ] Context Extension searches full chat history for references lost to compression
- [ ] Context Compression summarizes older messages when context threshold exceeded
- [ ] Working memory indicator shows context utilization, updates on compression
- [ ] Delegation messages render de-emphasized, final response renders normally
- [ ] Board item references in chat are clickable and navigate to the referenced item
- [ ] Facilitator bucket content (cached 5min) is included in Facilitator context
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M5

## Notes
- Admin UI for editing facilitator/detailed company context comes in M11 (Admin Panel). For now, context buckets are seeded empty and can be populated via direct DB insertion or a temporary API endpoint for testing.
- The re-indexing pipeline (triggered on bucket update) is implemented here but the admin trigger endpoint comes in M11. A gRPC endpoint exists for Gateway to call.
- Context Extension uses the escalated model tier (larger context window) for full chat history processing.
- pgvector HNSW indexes should already exist from M1 schema migrations.
