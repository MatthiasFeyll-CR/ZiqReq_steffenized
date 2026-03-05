# Changes Applied

> **Date:** 2026-03-02
> **Author:** Arch+AI Integrator (Phase 3c)

---

## Architecture Docs Updated

| # | File | Section | Change | Gap Ref |
|---|------|---------|--------|---------|
| 1 | `docs/02-architecture/tech-stack.md` | Tech Stack table | Updated `AI Orchestration` row from "TBD by AI Engineer" to "Semantic Kernel (Python SDK) \| latest \| Azure-native, automatic function calling for Facilitator/Board Agent, unified base layer across all 9 agents" | G-010 |
| 2 | `docs/02-architecture/project-structure.md` | Environment Variables — AI Service | Added 4 env vars: `AZURE_OPENAI_DEFAULT_DEPLOYMENT`, `AZURE_OPENAI_CHEAP_DEPLOYMENT`, `AZURE_OPENAI_ESCALATED_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`. Removed deferral note. | G-009 |
| 3 | `docs/02-architecture/data-model.md` | admin_parameters — Seed data | Added "AI-specific parameters" seed data table with 8 parameters: `default_ai_model`, `escalated_ai_model`, `ai_processing_timeout` (60 seconds), `recent_message_count` (20), `context_compression_threshold` (60%), `context_rag_top_k` (5), `context_rag_min_similarity` (0.7), `similarity_vector_threshold` (0.75). Replaced deferral note. | G-008 |
| 4 | `docs/02-architecture/api-design.md` | Core Service gRPC — AI-Relevant Methods | Added `GetFullChatHistory` gRPC method with `FullChatHistoryRequest`/`FullChatHistoryResponse` protobuf messages. Inserted between `GetIdeaContext` and `PersistAiOutput`. | G-001 |
| 5 | `docs/02-architecture/api-design.md` | AI Service gRPC — AiMetricsResponse | Added `int64 extension_count = 12;` field. Removed deferral note. | G-011 |
| 6 | `docs/02-architecture/api-design.md` | Events Published by AI Service (Security Monitoring) | Added 3 events: `ai.security.extension_fabrication_flag`, `ai.security.tool_rejection`, `ai.security.output_validation_fail` with full payloads. | G-006, G-007 |

## AI Docs Updated

| # | File | Section | Change | Gap Ref |
|---|------|---------|--------|---------|
| 1 | `docs/03-ai/agent-architecture.md` | Section 4.3 (Deep Comparison Pipeline) | Renamed `similarity.candidates` → `similarity.detected` (2 occurrences: entry point label and pipeline diagram). | G-003 |
| 2 | `docs/03-ai/agent-architecture.md` | Section 4.4 (Merge Synthesis Pipeline) | Renamed `idea.merge.accepted` → `merge.request.resolved` with `status='accepted'` filter note. | G-004 |
| 3 | `docs/03-ai/agent-architecture.md` | Section 5.1 (Cross-Service Communication) | Updated 4 rows: removed `GetBoardState` from gRPC methods list, renamed `similarity.candidates` → `similarity.detected`, renamed `idea.merge.accepted` → `merge.request.resolved`, replaced `admin.context_bucket.updated` broker event with gRPC `UpdateFacilitatorBucket`/`UpdateContextAgentBucket`. | G-002, G-003, G-004, G-005 |
| 4 | `docs/03-ai/agent-architecture.md` | Section 6.3 (RAG Pipeline) | Updated indexing trigger from `admin.context_bucket.updated` event to gRPC-based flow: "Admin updates via REST → Gateway → AI gRPC `UpdateContextAgentBucket`". | G-005 |
| 5 | `docs/03-ai/agent-architecture.md` | Section 9.2 (Data Accessed via Core gRPC) | Replaced `GetBoardState` with `GetIdeaContext(include_board=true)` for board nodes/connections. Replaced `brd_sections` / `GetBrdDraft` with `brd_drafts` (`sections_json` JSONB) / `GetIdeaContext(include_brd_draft=true)`. | G-002, G-012 |
| 6 | `docs/03-ai/agent-architecture.md` | Section 10 (Admin-Configurable AI Parameters) | Replaced `ai_debounce_delay` (3000ms) with `debounce_timer` (3 seconds, shared with architecture). Changed `ai_processing_timeout` from 60000ms to 60 seconds. Added "shared with architecture" annotations to 4 params that exist in both docs. Added convention note about seconds-to-ms conversion. | G-008 |

## Summary

- **Architecture files modified:** 4 (`tech-stack.md`, `project-structure.md`, `data-model.md`, `api-design.md`)
- **AI files modified:** 1 (`agent-architecture.md`)
- **Total edits:** 12 (6 architecture, 6 AI)
- **All 12 gaps resolved**
