# Milestone 8: AI Board Agent & Context

## Overview
- **Execution order:** 8 (runs after M7)
- **Estimated stories:** 10
- **Dependencies:** M7
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-2.6 | Board Item References in Chat (AI resolution) | P1 | features.md FA-2 |
| F-2.14 | Long Conversation Support (compression + indicator) | P1 | features.md FA-2 |
| F-2.15 | Company Context Awareness (RAG) | P1 | features.md FA-2 |
| F-2.17 | AI Board Content Rules | P1 | features.md FA-2 |
| F-5.1 | Keyword Generation | P1 | features.md FA-5 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| board_nodes | INSERT, UPDATE, DELETE (via Board Agent) | All content columns | data-model.md |
| board_connections | INSERT, UPDATE, DELETE (via Board Agent) | All columns | data-model.md |
| chat_context_summaries | INSERT, UPDATE | idea_id, summary_text, messages_covered_up_to_id, compression_iteration | data-model.md |
| context_chunks | DELETE + INSERT (re-index) | chunk_text, embedding, source_section | data-model.md |
| idea_keywords | INSERT, UPDATE | idea_id, keywords | data-model.md |
| idea_embeddings | INSERT, UPDATE | idea_id, embedding, source_text_hash | data-model.md |
| facilitator_context_bucket | SELECT (cached) | content | data-model.md |
| context_agent_bucket | SELECT | sections, free_text | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| UpdateFacilitatorBucket | gRPC | Update facilitator context | Internal | api-design.md (AI gRPC) |
| UpdateContextAgentBucket | gRPC | Update company context + re-index | Internal | api-design.md (AI gRPC) |
| GetFullChatHistory | gRPC | Full uncompressed chat for Context Extension | Internal | api-design.md (Core gRPC) |
| /api/ideas/:id/context-window | GET | Context utilization stats for indicator | Bearer | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Board Agent | 8-tool spatial board operations | agent-architecture.md S3.2 |
| Context Agent | RAG retrieval from company knowledge | agent-architecture.md S3.3 |
| Context Extension | Full chat history search | agent-architecture.md S3.4 |
| Context Compression | Chat summarization | agent-architecture.md S3.8 |
| Keyword Agent | Abstract keyword extraction | agent-architecture.md S3.6 |

## Story Outline (Suggested Order)
1. **[Backend — AI]** Board Agent implementation — agent.py, prompt.py, plugins.py (BoardPlugin with 8 tools)
2. **[Backend — AI]** request_board_changes tool (Facilitator) — hand off semantic instructions to Board Agent, execute mutations
3. **[Backend — AI]** Context Agent — RAG retrieval agent, system prompt, chunk retrieval via pgvector
4. **[Backend — AI]** Context chunks embedding pipeline — chunker.py, embedder.py, reindexer.py (on bucket update)
5. **[Backend — AI]** delegate_to_context_agent tool — trigger RAG, second Facilitator pass with findings, delegation message de-emphasis
6. **[Backend — AI]** Context Extension agent — full chat history search, escalated model tier
7. **[Backend — AI]** delegate_to_context_extension tool — load full history, second Facilitator pass, delegation message de-emphasis
8. **[Backend — AI]** Context Compression agent — summarize older messages, upsert chat_context_summaries, context window check (Step 6)
9. **[Backend — AI]** Keyword Agent — extract abstract keywords, persist via Core gRPC, trigger idea embedding generation
10. **[Frontend]** Context window indicator — filling circle showing usage percentage, hover tooltip with details

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Board Agent | ~10,000 | agent-architecture.md (S3.2), tools-and-functions.md (Board Plugin) | 4-6 files | High | 8 tools, spatial reasoning |
| 2 | request_board_changes | ~5,000 | tools-and-functions.md (S6), agent-architecture.md (S4.1 Step 4) | 2-3 files | Medium | Pipeline integration |
| 3 | Context Agent | ~5,000 | agent-architecture.md (S3.3), system-prompts.md | 3-4 files | Medium | RAG retrieval |
| 4 | Embedding pipeline | ~6,000 | agent-architecture.md (S6.3), data-model.md (context_chunks) | 4-5 files | High | pgvector, chunking strategy |
| 5 | delegate_to_context_agent | ~5,000 | tools-and-functions.md (S4), agent-architecture.md (S4.1 Step 3a) | 3-4 files | Medium | Second Facilitator pass |
| 6 | Context Extension | ~4,000 | agent-architecture.md (S3.4), system-prompts.md | 2-3 files | Medium | Escalated model tier |
| 7 | delegate_to_context_extension | ~5,000 | tools-and-functions.md (S5), agent-architecture.md (S4.1 Step 3b) | 3-4 files | Medium | Full history loading |
| 8 | Context Compression | ~5,000 | agent-architecture.md (S3.8, S6.2) | 3-4 files | Medium | Incremental summarization |
| 9 | Keyword Agent | ~5,000 | agent-architecture.md (S3.6, S6.4) | 3-4 files | Medium | Embedding generation |
| 10 | Context window indicator | ~3,000 | component-specs.md (S5.7) | 2-3 files | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~53,000
- **Cumulative domain size:** Large (5 AI agents + embedding pipeline + frontend indicator)
- **Information loss risk:** Medium (6)
- **Context saturation risk:** Medium
- **Heavy stories:** 2 (Board Agent, embedding pipeline)

## Milestone Acceptance Criteria
- [ ] Board Agent creates/updates/deletes nodes and connections from Facilitator instructions
- [ ] AI board changes broadcast via WebSocket with ai_modified_indicator
- [ ] Context Agent retrieves company context via RAG when Facilitator delegates
- [ ] Delegation messages appear and de-emphasize after real response arrives
- [ ] Context Extension searches full chat history for lost details
- [ ] Context Compression summarizes older messages when threshold exceeded
- [ ] Keyword Agent generates abstract keywords after each processing cycle
- [ ] Idea embeddings generated and updated per cycle
- [ ] Context window indicator shows usage percentage
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M7

## Notes
- Deep Comparison agent (which uses keywords + embeddings) comes in M13 (Similarity).
- Admin UI for managing context buckets comes in M15 (Admin Panel). For now, buckets are updated via direct DB or test fixtures.
- Keyword matching sweep (Celery job) comes in M13. Keywords are generated here but background matching is later.
