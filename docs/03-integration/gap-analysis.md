# Gap Analysis

> **Status:** Complete.
>
> **Date:** 2026-03-02
> **Author:** Arch+AI Integrator (Phase 3c)
> **Input:** All files in `docs/02-architecture/`, `docs/03-ai/`, `docs/03-ai/_status.md` Architecture Sync Gaps

---

## Summary

| Category | Gaps Found |
|----------|-----------|
| Database Tables | 0 |
| API Endpoints / gRPC Methods | 3 (G-001, G-002, G-011) |
| Environment Variables | 1 (G-009) |
| Dependencies | 1 (G-010) |
| Event Contracts | 5 (G-003, G-004, G-005, G-006, G-007) |
| Admin Parameters / Data | 1 (G-008) |
| Data Reference Corrections | 1 (G-012) |
| **Total** | **12** |

---

## Category 1: Database Tables

No gaps. The AI Engineer confirmed all 9 agents operate within the existing 5 AI-owned tables (`chat_context_summaries`, `facilitator_context_bucket`, `context_agent_bucket`, `context_chunks`, `idea_embeddings`). No new tables required.

---

## Category 2: API Endpoints / gRPC Methods

### Gap G-001: Missing gRPC Method — `GetFullChatHistory`

- **Category:** API Endpoint
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 3.4 (Context Extension Agent), Section 4.1 (Pipeline Step 3b), Section 9.2 (Data Accessed via Core gRPC)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Core Service (`proto/core.proto`) — AI-Relevant Methods"
- **Details:** The Context Extension agent requires the full uncompressed chat history for an idea (no message limit) to search for specific details in long conversations. Architecture only defines `GetIdeaContext` which has a `recent_message_limit` parameter. A separate method is needed to return ALL chat messages without limit.
- **Authoritative source:** AI — the AI Engineer designed the Context Extension agent's data needs.
- **Resolution:** Add `GetFullChatHistory(idea_id) → repeated ChatMessage` to `docs/02-architecture/api-design.md` Core Service gRPC section, and reference it in `proto/core.proto` definitions.

---

### Gap G-002: gRPC Method Naming — `GetBoardState` / `GetBrdDraft`

- **Category:** API Endpoint
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 9.2 (Data Accessed via Core gRPC)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Core Service — AI-Relevant Methods"
- **Details:** The AI docs reference `GetBoardState` and `GetBrdDraft` as standalone Core gRPC methods. The architecture provides board state and BRD draft as optional fields within `GetIdeaContext` (via `include_board` and `include_brd_draft` flags). All AI service use cases (Facilitator, Board Agent, Summarizing AI, Deep Comparison) can use `GetIdeaContext` with appropriate flags — no standalone methods needed.
- **Authoritative source:** Architecture — `GetIdeaContext` with flags is the correct API surface.
- **Resolution:** Update `docs/03-ai/agent-architecture.md` Section 9.2 to replace `GetBoardState` and `GetBrdDraft` with `GetIdeaContext(include_board=true)` and `GetIdeaContext(include_brd_draft=true)` respectively. Deep Comparison calls `GetIdeaContext` twice (once per idea).

---

### Gap G-011: AiMetricsResponse Missing `extension_count` Field

- **Category:** API Endpoint
- **Source (AI doc):** `docs/03-ai/model-config.md`, Section 9 (Monitoring Metrics) — defines `ai.extension.count` metric
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, `AiMetricsResponse` protobuf message
- **Details:** The AI Engineer added Context Extension invocation tracking (`ai.extension.count`). The `AiMetricsResponse` message in `api-design.md` has 11 fields but is missing `extension_count`. Architecture explicitly noted: "The AI Engineer may extend AiMetricsResponse with additional fields."
- **Authoritative source:** AI — the AI Engineer defines which metrics to expose.
- **Resolution:** Add `int64 extension_count = 12;` to `AiMetricsResponse` in `docs/02-architecture/api-design.md`.

---

## Category 3: Environment Variables

### Gap G-009: AI Environment Variables Not in `project-structure.md`

- **Category:** Env Var
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 11 (Environment Variables); `docs/03-ai/model-config.md`, Section 8 (Environment Variables)
- **Expected in (Arch doc):** `docs/02-architecture/project-structure.md`, Section "Environment Variables — AI Service"
- **Details:** 4 new AI service environment variables not in the architecture's env var table:
  1. `AZURE_OPENAI_DEFAULT_DEPLOYMENT` — Default tier deployment name (fallback if admin parameter empty)
  2. `AZURE_OPENAI_CHEAP_DEPLOYMENT` — Cheap tier deployment name (GPT-4o-mini, not admin-configurable)
  3. `AZURE_OPENAI_ESCALATED_DEPLOYMENT` — Escalated tier deployment name (fallback if admin parameter empty)
  4. `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` — Embedding model deployment name (text-embedding-3-small)
- **Note:** Architecture explicitly deferred these: "Additional AI-specific environment variables... defined by the AI Engineer in docs/03-ai/. They will be added to this table after Arch+AI integration."
- **Authoritative source:** AI — the AI Engineer defines deployment-specific env vars.
- **Resolution:** Add all 4 env vars to the AI Service table in `docs/02-architecture/project-structure.md`.

---

## Category 4: Dependencies

### Gap G-010: AI Orchestration Framework Not in `tech-stack.md`

- **Category:** Dependency
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 1 (Orchestration Framework)
- **Expected in (Arch doc):** `docs/02-architecture/tech-stack.md`, AI Orchestration row
- **Details:** Semantic Kernel (Python SDK) was selected as the AI orchestration framework. The architecture's tech-stack.md still shows "TBD by AI Engineer" for the AI Orchestration row. Architecture explicitly deferred: "Agent framework selection... is the AI Engineer's decision."
- **Authoritative source:** AI — the AI Engineer selected Semantic Kernel.
- **Resolution:** Update the `AI Orchestration` row in `docs/02-architecture/tech-stack.md` from "TBD by AI Engineer" to "Semantic Kernel (Python SDK)" with version "latest" and rationale "Azure-native, automatic function calling for Facilitator/Board Agent, unified base layer across all 9 agents."

---

## Category 5: Event Contracts

### Gap G-003: Event Name Mismatch — `similarity.candidates` vs `similarity.detected`

- **Category:** Event Contract
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 4.3 (Similarity Pipeline), Section 5.1 (Inter-Service Contracts)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Events Published by Core Service"
- **Details:** The AI docs reference consuming `similarity.candidates` as the event that triggers the Deep Comparison pipeline. The architecture defines this event as `similarity.detected`. Same semantic meaning, different name.
- **Authoritative source:** Architecture — event naming is an architecture-level concern. Architecture's naming convention is `<domain>.<entity>.<action>`.
- **Resolution:** Update `docs/03-ai/agent-architecture.md` to replace all references to `similarity.candidates` with `similarity.detected`.

---

### Gap G-004: Event Name Mismatch — `idea.merge.accepted` vs `merge.request.resolved`

- **Category:** Event Contract
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 4.4 (Merge Pipeline), Section 5.1 (Inter-Service Contracts)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Events Published by Core Service"
- **Details:** The AI docs reference consuming `idea.merge.accepted` as the event that triggers the Merge Synthesizer. The architecture defines this event as `merge.request.resolved` with `status='accepted'` in the payload. The Merge Synthesizer should filter on `status='accepted'` from the `merge.request.resolved` event.
- **Authoritative source:** Architecture — event naming and payload design is an architecture-level concern.
- **Resolution:** Update `docs/03-ai/agent-architecture.md` to replace all references to `idea.merge.accepted` with `merge.request.resolved` (filtering on `status='accepted'`).

---

### Gap G-005: Incorrect Event Reference — `admin.context_bucket.updated` as Incoming Event

- **Category:** Event Contract
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 5.1 (Inter-Service Contracts), Section 7 (RAG Pipeline)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "AI Service gRPC — Bucket Management"
- **Details:** The AI docs reference `admin.context_bucket.updated` as an incoming message broker event that triggers the AI service's re-indexing pipeline. In the architecture, the flow is:
  1. Admin updates bucket via REST → Gateway → AI gRPC `UpdateContextAgentBucket`
  2. AI service persists bucket → triggers re-indexing internally
  3. AI service publishes `ai.context_bucket.updated` event (outgoing, confirms save)

  The bucket update arrives via synchronous gRPC, not an async broker event. The AI service is the **publisher** of `ai.context_bucket.updated`, not the consumer.
- **Authoritative source:** Architecture — the inter-service communication flow is an architecture-level concern.
- **Resolution:** Update `docs/03-ai/agent-architecture.md` Section 5.1 and Section 7 to reference the gRPC-based bucket update flow (`UpdateContextAgentBucket` / `UpdateFacilitatorBucket`) instead of a broker event. The re-indexing is triggered internally as a side-effect of the gRPC update, not by an event.

---

### Gap G-006: Missing Security Event — `ai.security.extension_fabrication_flag`

- **Category:** Event Contract
- **Source (AI doc):** `docs/03-ai/guardrails.md`, Section 10.1 (Logged Events)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Events Published by AI Service (Security Monitoring)"
- **Details:** The AI Engineer introduced `ai.security.extension_fabrication_flag` for Context Extension fabrication detection (when Extension output contains claims not matchable to chat history). The architecture's security monitoring events table has 4 events but is missing this one.
- **Authoritative source:** AI — the AI Engineer defines security event types and detection mechanisms.
- **Resolution:** Add `ai.security.extension_fabrication_flag` to the security monitoring events table in `docs/02-architecture/api-design.md` with payload: `{ idea_id, query, flagged_quotes: [...], timestamp }`.

---

### Gap G-007: Missing Security Events — `tool_rejection` and `output_validation_fail`

- **Category:** Event Contract
- **Source (AI doc):** `docs/03-ai/guardrails.md`, Section 10.1 (Logged Events)
- **Expected in (Arch doc):** `docs/02-architecture/api-design.md`, Section "Events Published by AI Service (Security Monitoring)"
- **Details:** The guardrails doc defines 7 security events in Section 10.1 and states: "All security events are defined as message broker events in `docs/02-architecture/api-design.md`." The architecture only has 4. Two additional events are missing:
  1. `ai.security.tool_rejection` — Tool plugin rejects an invalid operation (payload: `{ idea_id, agent, tool_name, error_code, timestamp }`)
  2. `ai.security.output_validation_fail` — Agent output fails format or constraint validation (payload: `{ idea_id, agent, validation_type, timestamp }`)
- **Authoritative source:** AI — the AI Engineer defines security event types. These are operational events that feed the monitoring dashboard.
- **Resolution:** Add both events to the security monitoring events table in `docs/02-architecture/api-design.md`.

---

## Category 6: Admin Parameters / Data

### Gap G-008: AI Admin Parameters Not in Seed Data + Naming/Unit Reconciliation

- **Category:** Admin Parameters
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 10 (Admin-Configurable AI Parameters)
- **Expected in (Arch doc):** `docs/02-architecture/data-model.md`, Section "admin_parameters — Seed data"
- **Details:** 8 new AI-specific admin parameters defined by the AI Engineer are not in the architecture's seed data:

  | Parameter Key | AI Default | Type | Description |
  |--------------|-----------|------|-------------|
  | `default_ai_model` | (deployment name) | string | Azure OpenAI deployment for default tier |
  | `escalated_ai_model` | (deployment name) | string | Azure OpenAI deployment for escalated tier |
  | `ai_processing_timeout` | 60000 (ms) | integer | Timeout for user-facing agent invocations |
  | `recent_message_count` | 20 | integer | Recent messages in Facilitator context |
  | `context_compression_threshold` | 60 | integer (%) | Context utilization % triggering compression |
  | `context_rag_top_k` | 5 | integer | Chunks retrieved per RAG query |
  | `context_rag_min_similarity` | 0.7 | float | Min cosine similarity for chunk retrieval |
  | `similarity_vector_threshold` | 0.75 | float | Cosine similarity for idea similarity detection |

  **Sub-issue A — Naming conflict:** The AI doc defines `ai_debounce_delay` (3000ms). The architecture already has `debounce_timer` (3 seconds) in the seed data. Same concept, different name and unit. Architecture is authoritative — the parameter already exists.

  **Sub-issue B — Unit convention:** The architecture's existing parameters consistently use seconds for time values (idle_timeout: 300, idle_disconnect: 120, debounce_timer: 3, health_check_interval: 60). The AI doc defines `ai_processing_timeout` as 60000 (ms). For consistency, this should be stored as 60 (seconds). The AI service converts to ms internally.

- **Note:** Architecture explicitly deferred: "AI-specific parameters... will be added to this seed data by the Arch+AI Integrator during reconciliation."
- **Authoritative source:** AI for parameter definitions; Architecture for naming convention and storage format.
- **Resolution:**
  1. Add 8 new parameters to `data-model.md` seed data (AI-specific parameters section).
  2. Use `ai_processing_timeout` with value `60` (seconds, matching architecture convention).
  3. Update `docs/03-ai/agent-architecture.md` Section 10: remove `ai_debounce_delay` (use `debounce_timer`), update `ai_processing_timeout` to 60 (seconds), note that AI service converts to ms internally.

---

## Category 7: Data Reference Corrections

### Gap G-012: Incorrect Table Reference — `brd_sections` Should Be `brd_drafts`

- **Category:** Data Reference
- **Source (AI doc):** `docs/03-ai/agent-architecture.md`, Section 9.2 (Data Accessed via Core gRPC)
- **Expected in (Arch doc):** `docs/02-architecture/data-model.md`, Table definitions
- **Details:** The AI doc references `brd_sections` as a Core table in the "Data Accessed via Core gRPC" table. The architecture's data model has no `brd_sections` table. The correct table is `brd_drafts`, which stores BRD sections in a `sections_json` JSONB column with structure `{ section_key: { content, is_locked, last_edited_by, last_edited_at } }`.
- **Authoritative source:** Architecture — the data model is an architecture-level concern.
- **Resolution:** Update `docs/03-ai/agent-architecture.md` Section 9.2 to replace `brd_sections` with `brd_drafts` and note that sections are accessed via the `sections_json` JSONB column.

---

## Gaps Not Found (Explicitly Verified)

| Check | Result |
|-------|--------|
| AI-owned DB tables match between both docs | PASS — all 5 tables consistent |
| AI service container topology matches | PASS — `ai` container in both docs |
| gRPC service boundary (AI service has gRPC interface) | PASS — consistent |
| Message broker as async communication | PASS — consistent |
| PostgreSQL with pgvector for embeddings | PASS — consistent |
| Azure OpenAI as AI provider | PASS — consistent |
| Cross-service data access via gRPC only | PASS — consistent |
| Context assembler architecture | PASS — internal to AI service, correctly deferred |
| Celery tasks NOT used by AI service | PASS — AI service uses its own gRPC + event consumers |
| PDF service remains separate from AI | PASS — consistent |
