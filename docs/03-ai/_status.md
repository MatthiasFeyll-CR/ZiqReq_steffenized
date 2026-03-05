# AI Engineer — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-02
- **Last updated:** 2026-03-02

## Input Consumed
- docs/01-requirements/vision.md
- docs/01-requirements/user-roles.md
- docs/01-requirements/features.md
- docs/01-requirements/pages.md
- docs/01-requirements/data-entities.md
- docs/01-requirements/nonfunctional.md
- docs/01-requirements/constraints.md
- docs/01-requirements/traceability.md
- docs/02-architecture/tech-stack.md
- docs/02-architecture/data-model.md
- docs/02-architecture/api-design.md
- docs/02-architecture/project-structure.md
- docs/02-architecture/testing-strategy.md
- docs_old/03-ai/agent-architecture.md
- docs_old/03-ai/system-prompts.md
- docs_old/03-ai/tools-and-functions.md
- docs_old/03-ai/model-config.md
- docs_old/03-ai/guardrails.md
- docs_old/03-ai/_status.md

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Agent Architecture | complete | 2026-03-02 |
| 2 | System Prompts | complete | 2026-03-02 |
| 3 | Tools & Function Definitions | complete | 2026-03-02 |
| 4 | Model Configuration & Optimization | complete | 2026-03-02 |
| 5 | Guardrails & Safety | complete | 2026-03-02 |
| 6 | Architecture Sync & Handoff | complete | 2026-03-02 |

## Deliverables
| File | Description |
|------|-------------|
| agent-architecture.md | 9 agents, 4 pipelines, Semantic Kernel orchestration, context management, RAG + similarity, failure handling, full internal directory structure |
| system-prompts.md | Production-ready XML-structured prompts for all 9 agents with runtime variables, example interactions, and anti-patterns. New: context_extension_guidance section in Facilitator, delegation/extension_results injection. |
| tools-and-functions.md | Exact JSON schemas for all 14 SK plugins (6 Facilitator + 8 Board Agent). New: delegate_to_context_extension tool. Error codes, SK implementation pattern, execution flows. |
| model-config.md | Model selection per agent, generation parameters, token budgets, cost projections (~$2.04/idea, ~$20.4K/month at peak), prompt caching (~27% savings), model routing, timeout/retry config, monitoring metrics. New: Context Extension in cost model and metrics. |
| guardrails.md | 7-layer defense-in-depth safety architecture. Input validation, structural prompt isolation, system prompt rules, Azure content filtering, output validation, tool execution guards, security monitoring. New: Context Extension fabrication guards, extension output validation, extension-specific abuse prevention. |

## Architecture Sync Gaps

### Gap 1: Missing gRPC Method — `GetFullChatHistory`
- **Source:** agent-architecture.md Section 3.4 (Context Extension), Section 4.1 Pipeline Step 3b
- **Issue:** Context Extension agent requires full uncompressed chat history via Core gRPC `GetFullChatHistory`. api-design.md only defines `GetIdeaContext` with `recent_message_limit`. A separate method is needed to return ALL chat messages for an idea without limit.
- **Resolution:** Add `GetFullChatHistory(idea_id) → repeated ChatMessage` to `proto/core.proto` and api-design.md.

### Gap 2: gRPC Method Naming — `GetBoardState` / `GetBrdDraft`
- **Source:** agent-architecture.md Section 5.1, Section 9.2
- **Issue:** AI docs reference `GetBoardState` and `GetBrdDraft` as standalone Core gRPC methods. Architecture provides these as fields within `GetIdeaContext` (`include_board`, `include_brd_draft`).
- **Resolution:** Clarify whether separate methods are needed or `GetIdeaContext` with appropriate flags suffices for all AI service use cases. If `GetIdeaContext` is sufficient, update AI docs to use correct method name. If separate methods are needed (e.g., Deep Comparison needs board for 2 ideas without full context), add them to core.proto.

### Gap 3: Event Name Mismatches (3 events)
- **Source:** agent-architecture.md Section 4.3, Section 4.4, Section 5.1, Section 6.3
- **Issue:** Three event names in AI docs don't match api-design.md:
  1. `similarity.candidates` (AI) → `similarity.detected` (architecture)
  2. `idea.merge.accepted` (AI) → `merge.request.resolved` with status='accepted' (architecture)
  3. `admin.context_bucket.updated` (AI, referenced as incoming broker event) → Architecture shows this as a synchronous gRPC flow (`UpdateContextAgentBucket`), not a broker event
- **Resolution:** Reconcile event names. For #3, update AI docs to reflect gRPC-based bucket update flow instead of event-based.

### Gap 4: Missing Security Monitoring Event
- **Source:** guardrails.md Section 5.4, Section 12
- **Issue:** `ai.security.extension_fabrication_flag` event introduced for Context Extension fabrication detection. Not in api-design.md security monitoring events.
- **Resolution:** Add to api-design.md "Events Published by AI Service (Security Monitoring)" table with payload: `{ idea_id, query, flagged_quotes: [...], timestamp }`.

### Gap 5: AI Admin Parameters Not in Seed Data
- **Source:** agent-architecture.md Section 10
- **Issue:** 8 new AI-specific admin parameters not in data-model.md seed data:
  - `default_ai_model` — Azure OpenAI deployment name for default tier
  - `escalated_ai_model` — Azure OpenAI deployment name for escalated tier
  - `ai_processing_timeout` — 60000ms (timeout for user-facing agent invocations)
  - `recent_message_count` — 20 (recent messages in Facilitator context)
  - `context_compression_threshold` — 60 (% context utilization triggering compression)
  - `context_rag_top_k` — 5 (chunks retrieved per RAG query)
  - `context_rag_min_similarity` — 0.7 (minimum cosine similarity for RAG retrieval)
  - `similarity_vector_threshold` — 0.75 (cosine similarity threshold for idea similarity)
- **Naming conflict:** Architecture uses `debounce_timer` (3 seconds), AI docs use `ai_debounce_delay` (3000ms). Same concept, different name and unit. Needs reconciliation — recommend keeping architecture's `debounce_timer` name and having AI service read it (converting to ms internally).
- **Resolution:** Add 8 new parameters to data-model.md admin_parameters seed data. Resolve `debounce_timer` / `ai_debounce_delay` naming conflict.

### Gap 6: AI Environment Variables Not in project-structure.md
- **Source:** agent-architecture.md Section 11
- **Issue:** 4 new AI service env vars not in project-structure.md AI Service table:
  - `AZURE_OPENAI_DEFAULT_DEPLOYMENT` — Default deployment name (fallback if admin parameter empty)
  - `AZURE_OPENAI_CHEAP_DEPLOYMENT` — Cheap tier deployment name (GPT-4o-mini)
  - `AZURE_OPENAI_ESCALATED_DEPLOYMENT` — Escalated tier deployment name (fallback if admin parameter empty)
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` — Embedding model deployment name (text-embedding-3-small)
- **Note:** Architecture explicitly deferred: "Additional AI-specific environment variables... defined by the AI Engineer in docs/03-ai/."
- **Resolution:** Add 4 env vars to project-structure.md AI Service environment variables table.

### Gap 7: AI Orchestration Framework Not in tech-stack.md
- **Source:** agent-architecture.md Section 1
- **Issue:** Semantic Kernel (Python SDK) selected as orchestration framework. tech-stack.md still shows "TBD by AI Engineer".
- **Note:** Architecture explicitly deferred: "Agent framework selection... is the AI Engineer's decision."
- **Resolution:** Update tech-stack.md row: `AI Orchestration | Semantic Kernel (Python SDK) | latest | Azure-native, automatic function calling for Facilitator/Board Agent, unified base layer across all 9 agents`

### Gap 8: AiMetricsResponse Extension
- **Source:** model-config.md Section 7
- **Issue:** `ai.extension.count` metric added for Context Extension invocations. `AiMetricsResponse` in api-design.md needs a new field.
- **Note:** Architecture noted: "The AI Engineer may extend AiMetricsResponse with additional fields."
- **Resolution:** Add `int64 extension_count = 12;` to `AiMetricsResponse` in api-design.md.

## Key Decisions
| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Semantic Kernel (Python SDK) for orchestration | Azure-native, automatic function calling for Facilitator/Board Agent, unified base layer. AutoGen, LangChain rejected. |
| 2 | 9 agents with clear separation | Facilitator (conversation) vs Board Agent (spatial) vs specialist agents. Independent testability, different model configs. |
| 3 | Facilitator gets 6 tools (up from 5 in old design) | Added delegate_to_context_extension as explicit tool vs old implicit trigger. Model controls when to search history. |
| 4 | Vector similarity threshold 0.75 (down from 0.85) | Wider net for similarity detection. More Deep Comparison invocations, negligible cost. |
| 5 | Admin-configurable retries for user-facing agents only | max_retry_attempts for Facilitator, Summarizing AI, Merge Synthesizer. Hardcoded for background agents. |
| 6 | In-process orchestration within cycles | No message broker between same-cycle agents. Direct function calls for speed and simplicity. |
| 7 | No data model additions needed | Architecture's 5 AI-owned tables + Core gRPC reads cover all agents. |

## Architecture Additions

Changes introduced by the AI Engineer that extend the Software Architect's baseline:

### New Database Tables
None. All 9 agents operate within the existing 5 AI-owned tables.

### New Environment Variables
| Variable | Purpose | Integrated In |
|----------|---------|---------------|
| `AZURE_OPENAI_DEFAULT_DEPLOYMENT` | Default Azure OpenAI deployment name | Gap — needs integration (project-structure.md) |
| `AZURE_OPENAI_CHEAP_DEPLOYMENT` | Cheap tier deployment name (GPT-4o-mini) | Gap — needs integration (project-structure.md) |
| `AZURE_OPENAI_ESCALATED_DEPLOYMENT` | Escalated tier deployment name | Gap — needs integration (project-structure.md) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment name | Gap — needs integration (project-structure.md) |

### New Dependencies
| Dependency | Purpose | Integrated In |
|-----------|---------|---------------|
| `semantic-kernel` (Python SDK) | AI agent orchestration framework | Gap — needs integration (tech-stack.md) |

### New Admin Parameters
| Parameter | Default | Integrated In |
|-----------|---------|---------------|
| `default_ai_model` | (deployment name) | Gap — needs integration (data-model.md seed data) |
| `escalated_ai_model` | (deployment name) | Gap — needs integration (data-model.md seed data) |
| `ai_processing_timeout` | 60000 | Gap — needs integration (data-model.md seed data) |
| `recent_message_count` | 20 | Gap — needs integration (data-model.md seed data) |
| `context_compression_threshold` | 60 | Gap — needs integration (data-model.md seed data) |
| `context_rag_top_k` | 5 | Gap — needs integration (data-model.md seed data) |
| `context_rag_min_similarity` | 0.7 | Gap — needs integration (data-model.md seed data) |
| `similarity_vector_threshold` | 0.75 | Gap — needs integration (data-model.md seed data) |

### New gRPC Methods Needed
| Method | Purpose | Integrated In |
|--------|---------|---------------|
| `GetFullChatHistory` | Full uncompressed chat for Context Extension | Gap — needs integration (api-design.md, core.proto) |

### New Broker Events
| Event | Purpose | Integrated In |
|-------|---------|---------------|
| `ai.security.extension_fabrication_flag` | Context Extension fabrication detection | Gap — needs integration (api-design.md) |

## Handoff
- **Ready:** true
- **Next specialist(s):** Arch+AI Integrator (`/arch_ai_integrator`) — 8 gaps found requiring reconciliation
- **Files produced:**
  - docs/03-ai/agent-architecture.md
  - docs/03-ai/system-prompts.md
  - docs/03-ai/tools-and-functions.md
  - docs/03-ai/model-config.md
  - docs/03-ai/guardrails.md
- **Required input for next specialist:**
  - All files in docs/02-architecture/ and docs/03-ai/
  - Architecture Sync Gaps list (in this _status.md)
- **Briefing for next specialist:**
  - 9 agents designed: 2 tool-using (Facilitator 6 tools, Board Agent 8 tools), 7 simple (no tools)
  - Azure OpenAI provider: GPT-4o (default/escalated), GPT-4o-mini (cheap), text-embedding-3-small (embeddings)
  - Semantic Kernel (Python SDK) selected for orchestration
  - 7-layer defense-in-depth guardrails with fabrication prevention as top priority
  - 8 architecture sync gaps found — 3 were explicitly deferred by the Architect, 5 are new
  - Cost projections: ~$2.04/idea, ~$20.4K/month at peak, ~27% savings with prompt caching
- **Open questions:** None
