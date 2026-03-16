# Agent Architecture

> **Status:** Definitive.
>
> **Date:** 2026-03-16
> **Author:** AI Engineer (Refactored for requirements assembly platform)
> **Input:** `docs/01-requirements/`, `docs/02-architecture/`, `REFACTORING_PLAN.md`

---

## 1. Orchestration Framework

### Selected: Semantic Kernel (Python SDK)

**Usage pattern:**

| Agent Complexity | SK Usage | Agents |
|-----------------|----------|--------|
| Tool-using | Function calling with registered plugins | Facilitator (6 tools) |
| Simple | Basic chat completion (no plugins) | Context Agent, Context Extension, Summarizing AI, Context Compression |

**Why Semantic Kernel over alternatives:**

| Framework | Status | Reason |
|-----------|--------|--------|
| **Semantic Kernel** | Selected | Azure-native, automatic function calling loop for Facilitator, unified base layer (model access, token tracking, retry, logging) across all 5 agents, lightweight — works within Django microservice architecture |
| AutoGen | Rejected | Dynamic multi-agent conversations; ZiqReq's delegation flows are predefined — unnecessary complexity |
| LangChain / LangGraph | Rejected | Heavy abstraction, not Azure-native; microservice architecture (gRPC + message broker) already handles inter-agent routing |
| Direct Azure OpenAI SDK only | Rejected | Sufficient for simple agents, but Facilitator's 6-tool processing cycle benefits from SK's automatic function calling loop |

---

## 2. Agent Inventory

| Agent | Type | Purpose | Model Tier | Feature References |
|-------|------|---------|------------|-------------------|
| Facilitator | Single-shot, multi-tool (6 tools) | Requirements structuring assistant — helps users build hierarchical requirements, chat responses, reactions, title updates, delegation | Default | F-2.1–F-2.13, F-2.17 |
| Context Agent | Single-shot, no tools | Company context retrieval via RAG from knowledge base | Default | F-2.15 |
| Context Extension | Single-shot, no tools (escalated) | Full chat history search for references lost to compression | Escalated | F-2.14 |
| Summarizing AI | Single-shot, no tools | Requirements document generation — hierarchical structure (Epics/Stories or Milestones/Packages) from full project state | Default | F-4.1, F-4.2, F-4.8, F-4.9 |
| Context Compression | Autonomous background, no tools | Chat summarization for long conversations | Cheap | F-2.14 |

**Removed agents from previous design:**
- **Board Agent** — Removed entirely (board/canvas functionality eliminated)
- **Keyword Agent** — Removed entirely (similarity detection system eliminated)
- **Deep Comparison** — Removed entirely (similarity detection system eliminated)
- **Merge Synthesizer** — Removed entirely (merge functionality eliminated)

---

## 3. Agent Details

### 3.1 Facilitator

- **Type:** Single-shot with multi-tool calls (SK function calling loop, max 3 rounds)
- **Purpose:** The primary AI in ZiqReq. Helps employees structure requirements for Software Projects (Epics → User Stories) or Non-Software Projects (Milestones → Work Packages). Decides all AI actions per processing cycle: whether to respond, react, update the title, delegate to specialists, or update the requirements structure.
- **Input:**
  - System prompt (fixed, XML-structured)
  - Facilitator bucket content (admin-managed ToC/guidance, context_type: global/software/non_software)
  - Chat context summary (from `chat_context_summaries`)
  - Recent chat messages (last N via Core gRPC, admin: `recent_message_count`)
  - Requirements structure (hierarchical JSON via Core gRPC)
  - Project metadata (state, title, title_manually_edited, collaborators, agent_mode, project_type)
- **Output:** Any combination of:
  - Chat message (via `send_chat_message` tool)
  - Reaction (via `react_to_message` tool)
  - Title update (via `update_title` tool)
  - Delegation to Context Agent (via `delegate_to_context_agent` tool)
  - Delegation to Context Extension (via `delegate_to_context_extension` tool)
  - Requirements structure update (via `update_requirements_structure` tool)
  - No action (valid in Silent mode when no @ai mention)
- **Model tier:** Default (GPT-4o). User-facing, complex reasoning, 6-tool function calling.
- **Context needs:** Full project state rebuilt from scratch every cycle. No multi-turn state carried over.
- **Failure mode:** Retry 3x (admin: `max_retry_attempts`), exponential backoff (1s, 2s, 4s). On final failure: error toast to user (F-14.1).
- **Tools (6):**
  1. `send_chat_message` — post AI chat response (no board item reference syntax)
  2. `react_to_message` — react to a user message
  3. `update_title` — update project title (only when not manually edited)
  4. `delegate_to_context_agent` — trigger company context RAG retrieval
  5. `delegate_to_context_extension` — trigger full chat history search
  6. `update_requirements_structure` — send structured mutations to requirements document

### 3.2 Context Agent

- **Type:** Single-shot, no tools.
- **Purpose:** Retrieves company-specific information from the knowledge base via RAG. Called when the Facilitator detects a topic that requires company context (systems, processes, org structure, domain terminology).
- **Input:**
  - System prompt (minimal)
  - Delegation query from Facilitator (natural language)
  - Retrieved chunks from `context_chunks` table (pgvector top-K similarity search)
  - Brief project context (title, recent topic) for grounding
- **Output:** Structured findings summary with source references. Returned to pipeline orchestrator, which injects findings into a second Facilitator pass.
- **Model tier:** Default (GPT-4o). User-facing output quality matters — findings appear in the Facilitator's response.
- **Context needs:** RAG-retrieved chunks + delegation query. Lightweight.
- **Failure mode:** No retry (hardcoded). On failure: Facilitator responds without company context. Delegation message updated: "I couldn't find relevant information."

### 3.3 Context Extension

- **Type:** Single-shot, no tools (escalated context budget).
- **Purpose:** Searches the full uncompressed chat history when the Facilitator detects a user reference to conversation details that were lost during context compression. Acts as a "memory retrieval" agent.
- **Input:**
  - System prompt (minimal)
  - Facilitator's query describing what to find
  - Full uncompressed chat history (via Core gRPC `GetFullChatHistory`)
  - Requirements structure for cross-referencing
- **Output:** Targeted answer with relevant quotes/details from the full history. Returned to pipeline orchestrator for second Facilitator pass.
- **Model tier:** Escalated (GPT-4o with extended context budget). Full chat history can consume 80K+ tokens for long-running projects. This is the reason the escalated tier exists.
- **Context needs:** Full uncompressed chat (potentially very large) + requirements structure.
- **Failure mode:** No retry (hardcoded). On failure: Facilitator responds "I couldn't retrieve that detail from earlier in the conversation."

### 3.4 Summarizing AI

- **Type:** Single-shot, no tools.
- **Purpose:** Generates the hierarchical Requirements Document from the full project state. Operates in three modes: full generation, selective regeneration (only unlocked sections), and item regeneration (single epic/milestone or story/package).
- **Input:**
  - System prompt (includes mode-specific sections and project_type awareness)
  - Chat history (summary + recent messages)
  - Requirements structure (current hierarchical JSON)
  - Company context findings (from delegation results in chat, if any)
  - Current draft sections (for selective/item regeneration only)
  - Locked item list (excluded from generation)
  - Mode: `full_generation` | `selective_regeneration` | `item_regeneration`
  - Project type: `software` | `non_software`
- **Output:** Hierarchical requirements document:
  - **Software:** `{title, short_description, structure: [{epic_id, title, description, stories: [{story_id, title, description, acceptance_criteria, priority}]}], readiness_evaluation}`
  - **Non-Software:** `{title, short_description, structure: [{milestone_id, title, description, packages: [{package_id, title, description, deliverables, dependencies}]}], readiness_evaluation}`
- **Model tier:** Default (GPT-4o). Document generation quality is critical — requirements documents become formal specifications.
- **Context needs:** Full project state. Heaviest context consumer after Context Extension.
- **Failure mode:** Retry 3x (admin: `max_retry_attempts`), exponential backoff. On final failure: error toast on Review tab.
- **Post-processing:** Fabrication validation (keyword matching, source cross-reference). See `guardrails.md`.

### 3.5 Context Compression

- **Type:** Autonomous background, no tools.
- **Purpose:** Summarizes older chat messages into a narrative summary when context window usage exceeds the compression threshold. Preserves key decisions, topics discussed, and participant contributions while reducing token count.
- **Input:**
  - System prompt (minimal)
  - Previous summary (if exists — for incremental compression)
  - Messages to compress (batch of messages since last compression)
- **Output:** Narrative summary text. Stored in `chat_context_summaries` table.
- **Model tier:** Cheap (GPT-4o-mini). Background summarization. Quality is secondary — the summary supplements recent messages, doesn't replace them.
- **Context needs:** Previous summary + message batch. Moderate to high for long conversations.
- **Failure mode:** Retry once (hardcoded). On failure: uncompressed context used until next successful compression. No user-visible impact, but context window may fill faster.

---

## 4. Processing Pipelines

### 4.1 Pipeline 1: Chat Processing (Primary)

Triggered by: User sends a chat message.
Frequency: ~95% of all AI invocations.

```
User sends chat message
  → Gateway REST persists via Core gRPC
  → Core publishes chat.message.created event
  → Gateway broadcasts via WebSocket
  → Gateway calls AI Service gRPC: TriggerChatProcessing(project_id, message_id)

AI Service Pipeline:
  ┌─ DEBOUNCE (admin: debounce_timer, default 3s)
  │  If new message arrives during window → abort current, restart debounce
  │
  ├─ ABORT CHECK: If cycle already running for this project → set abort flag on running cycle
  │  Running cycle checks abort flag at each step boundary and exits gracefully
  │
  ├─ STEP 1: Context Assembly
  │   ├─ Read project metadata via Core gRPC (state, title, title_manually_edited, collaborators, agent_mode, project_type)
  │   ├─ Read chat context summary from chat_context_summaries table (AI-owned)
  │   ├─ Read recent messages via Core gRPC (last N, admin: recent_message_count, default 20)
  │   ├─ Read requirements structure via Core gRPC (hierarchical JSON)
  │   ├─ Read facilitator bucket from facilitator_context_bucket table (AI-owned, cached 5min)
  │   │   - Combine global context + project-type-specific context (software or non_software)
  │   └─ Assemble into XML-structured prompt (system prompt + context)
  │
  ├─ STEP 2: Facilitator Invocation (SK function calling loop, max 3 auto-invoke rounds)
  │   ├─ Model decides actions: any combination of:
  │   │   ├─ send_chat_message → publishes ai.chat_response.ready
  │   │   ├─ react_to_message → publishes ai.reaction.ready
  │   │   ├─ update_title → publishes ai.title.updated
  │   │   ├─ delegate_to_context_agent → triggers Step 3a
  │   │   ├─ delegate_to_context_extension → triggers Step 3b
  │   │   └─ update_requirements_structure → triggers Step 4
  │   └─ If no actions (silent mode, no @ai) → skip to Step 5
  │
  ├─ STEP 3a: Context Agent Delegation (conditional)
  │   ├─ RAG retrieval: query context_chunks via pgvector similarity search
  │   │   (top-K: admin context_rag_top_k=5, min similarity: admin context_rag_min_similarity=0.7)
  │   ├─ Context Agent invocation: generate findings from retrieved chunks
  │   ├─ Second Facilitator pass: findings injected as <delegation_results> in context
  │   ├─ Facilitator generates contextualized response → ai.chat_response.ready
  │   └─ Original delegation message de-emphasized → ai.delegation.complete
  │
  ├─ STEP 3b: Context Extension Delegation (conditional)
  │   ├─ Load full uncompressed chat via Core gRPC GetFullChatHistory
  │   ├─ Context Extension invocation: search full history for referenced detail
  │   ├─ Second Facilitator pass: findings injected as <extension_results> in context
  │   ├─ Facilitator generates response with retrieved detail → ai.chat_response.ready
  │   └─ Original delegation message de-emphasized → ai.delegation.complete
  │
  ├─ STEP 4: Requirements Structure Update (conditional — if Facilitator issued structure mutations)
  │   ├─ Input: Facilitator's structured JSON mutations
  │   ├─ Validation: ensure IDs exist, operations valid for project_type
  │   ├─ Persist mutations via Core gRPC
  │   └─ Each mutation → ai.requirements.updated event
  │
  ├─ STEP 5: Context Window Check (after Steps 2–4 complete)
  │   ├─ Calculate context utilization:
  │   │   (summary tokens + recent message tokens + requirements structure tokens) / model context window
  │   ├─ If > compression threshold (admin: context_compression_threshold, default 60%)
  │   │   ├─ Context Compression invocation: summarize oldest uncompressed messages
  │   │   └─ Upsert chat_context_summaries table (increment version)
  │   └─ If below threshold → skip
  │
  └─ STEP 6: Publish ai.processing.complete event
      → Gateway resets chat rate limit counter for this project
```

**Abort-and-Restart Semantics:**

When a new message arrives while a cycle is running:
1. The debouncer sets an abort flag on the running cycle.
2. The running cycle checks the flag at each step boundary (between Steps 2–5).
3. If abort flag is set, the cycle exits gracefully — any already-published events (chat messages, structure updates) stand. Unpublished work is discarded.
4. A new cycle starts with the full updated state (including the new message).

This ensures the AI always processes the latest state. Partial results from aborted cycles are acceptable because each event is independently valid (a chat response is useful even if the structure update didn't happen).

### 4.2 Pipeline 2: Requirements Document Generation

Triggered by: User opens Review tab or clicks Generate/Regenerate.
Entry point: Gateway REST → AI Service gRPC `TriggerRequirementsGeneration(project_id, mode, locked_item_ids)`.

```
AI Service:
  ├─ STEP 1: Context Assembly (Requirements-specific)
  │   ├─ Chat context summary + recent messages (larger window — all available)
  │   ├─ Requirements structure (current hierarchical JSON)
  │   ├─ Company context findings (extracted from delegation results in chat history)
  │   ├─ Current draft (for selective/item regeneration)
  │   ├─ Locked item IDs (excluded from generation)
  │   ├─ Mode: full_generation | selective_regeneration | item_regeneration
  │   └─ Project type: software | non_software
  │
  ├─ STEP 2: Summarizing AI Invocation
  │   ├─ Generate hierarchical requirements document (structure based on project_type)
  │   └─ Output: structured JSON with content or explicit gap markers
  │
  ├─ STEP 3: Fabrication Validation (post-processing, non-AI)
  │   ├─ Keyword extraction from generated requirements
  │   ├─ Fuzzy match against chat messages + requirements structure content
  │   ├─ Proper noun check: extract names/terms, verify against source material
  │   ├─ Section length proportionality check
  │   └─ Flag items with potential fabrication (warning indicators, not blocking)
  │
  └─ STEP 4: Publish ai.requirements_document.ready event
      ├─ Payload: generated structure + fabrication flags + readiness evaluation
      └─ Gateway persists via Core gRPC, broadcasts via WebSocket
```

**Readiness evaluation:**
- **Software:** Ready when all epics have user stories with acceptance criteria
- **Non-Software:** Ready when all milestones have work packages with deliverables

---

## 5. Inter-Agent Communication

### 5.1 Cross-Service Communication

| Direction | Mechanism | Contract Location |
|-----------|-----------|------------------|
| Gateway → AI Service (trigger processing) | gRPC `TriggerChatProcessing` | `api-design.md` — gRPC Service Definitions |
| Gateway → AI Service (trigger requirements gen) | gRPC `TriggerRequirementsGeneration` | `api-design.md` — gRPC Service Definitions |
| AI Service → Core Service (read context) | gRPC `GetProjectContext`, `GetFullChatHistory` | `api-design.md` — gRPC Service Definitions |
| AI Service → Gateway (deliver results) | Message broker events (`ai.*`) | `api-design.md` — Message Broker Event Contracts |
| Gateway → AI Service (bucket updates) | gRPC `UpdateFacilitatorBucket`, `UpdateContextAgentBucket` | `api-design.md` — AI Service gRPC — Bucket Management |

### 5.2 In-Process Communication (Within AI Service)

| From → To | Mechanism | Data Passed |
|-----------|-----------|------------|
| Pipeline orchestrator → Facilitator | Direct function call | Assembled context (XML prompt) |
| Facilitator → Pipeline orchestrator | Tool return values | Tool call results (delegation IDs, structure mutations) |
| Pipeline orchestrator → Context Agent | Direct function call | Delegation query + RAG chunks + project context |
| Pipeline orchestrator → Context Extension | Direct function call | Extension query + full chat history + requirements structure |
| Pipeline orchestrator → Context Compression | Direct function call (conditional) | Previous summary + message batch |
| Pipeline orchestrator → Summarizing AI | Direct function call | Full project context + mode + locked items + project_type |

**Contract format:** All agents inherit from `BaseAgent` and accept an `AgentInput` dataclass. Each agent type has its own input/output subclass validated by Pydantic:

```python
class FacilitatorInput(AgentInput):
    project_id: str
    system_prompt: str       # Pre-assembled XML
    recent_messages: list[ChatMessage]
    requirements_structure: RequirementsStructure
    metadata: ProjectMetadata
    facilitator_bucket: str
    context_summary: str | None
    delegation_results: str | None  # From Context Agent (second pass)
    extension_results: str | None   # From Context Extension (second pass)

class FacilitatorOutput(AgentOutput):
    tool_calls: list[ToolCallResult]  # All tool calls made in the SK loop
    delegation_requested: bool
    extension_requested: bool
    structure_mutations: list[dict] | None
```

### 5.3 Timeout Handling

| Scope | Timeout | Action on Timeout |
|-------|---------|-------------------|
| Single agent invocation | Per-agent (see Section 8) | Raise `AgentTimeoutError`, caught by pipeline orchestrator |
| Full processing cycle | 2× `ai_processing_timeout` (covers Facilitator + delegation) | Kill cycle, publish `ai.processing.error` event |
| gRPC call to Core | 10s | Retry once, then raise `ContextAssemblyError` — cycle fails |
| Message broker publish | 5s | Retry once, then log and continue — event may be lost but cycle completes |

---

## 6. Context Management

### 6.1 Conversation Context Strategy

Each processing cycle rebuilds context from scratch. There is no multi-turn state carried between cycles. This ensures every cycle sees the latest state and is immune to context drift.

**Context components per Facilitator invocation:**

| Component | Source | Token Budget |
|-----------|--------|-------------|
| System prompt | Static (AI Engineer-authored) | ~2,000–2,500 |
| Tool schemas | SK-injected function definitions (6 tools) | ~2,000 |
| Facilitator bucket | `facilitator_context_bucket` table (cached 5min, global + type-specific) | 500–2,000 |
| Chat context summary | `chat_context_summaries` table | 0–5,000 (0 for new projects) |
| Recent chat messages | Core gRPC (last N messages) | 2,000–15,000 |
| Requirements structure | Core gRPC (hierarchical JSON) | 500–10,000 |
| Project metadata + user context | Core gRPC | ~200–300 |
| Delegation results (if second pass) | Context Agent or Context Extension output | 0–1,500 |
| **Typical total** | | **~7,000–12,000** |
| **Maximum total** | | **~38,000** |

### 6.2 Context Compression

**Trigger:** Context utilization exceeds `context_compression_threshold` (admin, default 60% = ~77K tokens of 128K window).

**Process:**
1. Calculate current context size: summary + recent messages + requirements structure + fixed components.
2. If above threshold: select oldest uncompressed messages (those between last compression point and the recent message window).
3. Context Compression agent summarizes selected messages into narrative form.
4. Upsert `chat_context_summaries`: merge new summary with previous summary, increment `compression_iteration`, update `messages_covered_up_to_id`.

**Working memory indicator (F-2.14):** When a summary exists (`chat_context_summaries.compression_iteration > 0`), the frontend displays a "Working Memory" indicator on the chat. This is driven by project metadata returned from Core, not by the AI service directly.

### 6.3 RAG Pipeline (Company Context)

**Indexing (on admin bucket update):**
1. Admin updates context agent bucket via REST → Gateway → AI gRPC `UpdateContextAgentBucket`.
2. AI service persists the update and triggers re-indexing internally:
   - Parse sections from `context_agent_bucket.sections` JSONB.
   - Each named section → one chunk (preserving admin-defined boundaries).
   - Free text (`context_agent_bucket.free_text`) → chunked at ~500 tokens with 50-token overlap.
   - Each chunk embedded via text-embedding-3-small → upsert into `context_chunks`.
   - Old chunks for deleted/modified sections removed.

**Retrieval (on delegation):**
1. Facilitator calls `delegate_to_context_agent(query="...")`.
2. Pipeline orchestrator embeds the query using text-embedding-3-small.
3. pgvector similarity search on `context_chunks`:
   - Top-K: `context_rag_top_k` (admin, default 5)
   - Minimum similarity: `context_rag_min_similarity` (admin, default 0.7)
   - Index: HNSW on `embedding` column
4. Retrieved chunks passed to Context Agent along with the query.
5. Context Agent generates findings grounded in the chunks.

### 6.4 Context Bucket Structure (Project Type Awareness)

Admin context buckets now support three context types:

| Context Type | Description | Used For |
|-------------|-------------|----------|
| `global` | Guidance applicable to all projects | All projects |
| `software` | Software project-specific guidance (Epics/Stories terminology, acceptance criteria tips) | Software projects only |
| `non_software` | Non-software project-specific guidance (Milestones/Packages terminology, deliverables tips) | Non-software projects only |

**Context assembly:** When assembling the Facilitator's context, combine `global` bucket + type-specific bucket (based on `project_type`).

---

## 7. Cross-Project Isolation

Each project is an isolated workspace. AI agents must never leak information between projects.

| Boundary | Enforcement |
|----------|-------------|
| Chat history | Context assembler filters by `project_id`. Only current project's messages loaded. |
| Requirements structure | Only current project's structure loaded. |
| Requirements document content | Only current project's draft loaded. |
| Company context | Shared across all projects (intentional — company-wide knowledge). |
| Admin parameters | Shared across all projects (system configuration is global). |
| User identity | Shared across projects the user participates in (users addressed by name). |

---

## 8. Failure Handling

### 8.1 Per-Agent Failure Matrix

| Agent | Timeout | Max Retries | Backoff | On Final Failure | User Impact |
|-------|---------|------------|---------|-----------------|-------------|
| Facilitator | 60s (admin: `ai_processing_timeout`) | 3 (admin: `max_retry_attempts`) | 1s, 2s, 4s | Error toast: "AI could not process. Click Retry." (F-14.1) | User retries or continues manually |
| Context Agent | 30s (hardcoded) | 0 | — | Facilitator responds without company context | General response instead of company-specific |
| Context Extension | 90s (1.5× `ai_processing_timeout`) | 0 | — | Facilitator: "Couldn't retrieve that detail." | Incomplete answer, user can retry |
| Summarizing AI | 60s (admin: `ai_processing_timeout`) | 3 (admin: `max_retry_attempts`) | 1s, 2s, 4s | Error toast: "Requirements generation failed. Click Retry." | User retries |
| Context Compression | 30s (hardcoded) | 1 (hardcoded) | 1s | Uncompressed context used | Context window fills faster, no user impact |

### 8.2 Azure OpenAI Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| 429 Rate Limited | HTTP 429 response | Respect `Retry-After` header. Queue request. Count against agent retry budget. |
| 500 Server Error | HTTP 500/502/503 | Retry with exponential backoff. Count against agent retry budget. |
| Content Filter Block (input) | HTTP 400 with content_filter annotation | Return user-facing error: "Your message could not be processed. Please rephrase." |
| Content Filter Block (output) | HTTP 200 with empty/truncated content | Retry once. If blocked again: return error to user. |
| Timeout | No response within agent timeout | Cancel request. Count against agent retry budget. |
| Invalid Response | Malformed JSON, unexpected format | Retry once. If still invalid: treat as failure. |

### 8.3 Pipeline-Level Error Handling

| Scenario | Handling |
|----------|---------|
| Context assembly fails (Core gRPC unavailable) | Retry gRPC once (10s timeout). If still fails: publish `ai.processing.error` event. User sees error toast. |
| Facilitator succeeds but structure mutation fails | Chat response already delivered (good). Structure update skipped for this cycle. Catches up on next cycle. |
| Delegation (Context Agent) fails mid-cycle | Facilitator runs second pass without company context. User gets general response. Delegation message updated. |
| Pipeline aborted by new message | Any already-published events stand. Unpublished work discarded. New cycle starts with fresh state. |

### 8.4 Design Principle

**No AI failure blocks the user from using the platform.** Requirements assembly continues manually. Chat works without AI. Only requirements document generation requires a successful AI call (because the document is AI-generated by design). Even generation failure has a clear retry path.

---

## 9. Data Model

### 9.1 AI-Owned Tables (Existing in Architecture)

| Table | Purpose | Managed By |
|-------|---------|-----------|
| `chat_context_summaries` | Compressed chat summaries per project | Context Compression agent |
| `facilitator_context_bucket` | Admin-managed facilitator guidance content (with context_type: global/software/non_software) | Admin Panel (write), Facilitator (read) |
| `context_agent_bucket` | Admin-managed company knowledge content | Admin Panel (write), RAG pipeline (read) |
| `context_chunks` | Chunked + embedded company context for RAG | RAG indexing pipeline |

**Removed tables:**
- `idea_embeddings` — Similarity detection eliminated

### 9.2 Data Accessed via Core gRPC (Not AI-Owned)

| Data | Core Table | Access Pattern |
|------|-----------|---------------|
| Project metadata | `projects` (renamed from `ideas`) | Read via `GetProjectContext` |
| Chat messages (recent) | `chat_messages` | Read via `GetProjectContext` (last N) |
| Chat messages (full) | `chat_messages` | Read via `GetFullChatHistory` |
| Requirements structure | `requirements_structure` (new hierarchical JSON field in `projects`) | Read via `GetProjectContext` |
| Requirements document draft | `requirements_document_drafts` (renamed from `brd_drafts`) | Read via `GetProjectContext(include_requirements_draft=true)` |
| User info | `users` (shadow table) | Included in `GetProjectContext` response |

**Removed data access:**
- `board_nodes`, `board_connections` — Board eliminated
- `idea_keywords` — Keyword system eliminated

### 9.3 No Additional Tables Needed

Gap analysis confirms the 4 AI-owned tables plus Core gRPC reads cover all 5 agents' data needs. No data model additions required.

---

## 10. Admin-Configurable AI Parameters

These parameters are stored in the `admin_parameters` table (Core-owned) and read by the AI service. They are managed via the Admin Panel (F-11.3).

| Parameter Key | Default | Type | Description | Used By |
|--------------|---------|------|-------------|---------|
| `default_ai_model` | (deployment name) | string | Azure OpenAI deployment for default tier | Facilitator, Context Agent, Summarizing AI |
| `escalated_ai_model` | (deployment name) | string | Azure OpenAI deployment for escalated tier | Context Extension |
| `debounce_timer` | 3 | integer (seconds) | Seconds after last chat message before AI processes (shared with architecture) | Pipeline orchestrator (convert to ms internally) |
| `ai_processing_timeout` | 60 | integer (seconds) | Timeout for user-facing agent invocations (convert to ms internally) | Facilitator, Summarizing AI |
| `max_retry_attempts` | 3 | integer | Retry count for user-facing agents (shared with architecture) | Facilitator, Summarizing AI |
| `recent_message_count` | 20 | integer | Number of recent messages in Facilitator context | Context assembler |
| `context_compression_threshold` | 60 | integer (%) | Context utilization % that triggers compression | Pipeline orchestrator |
| `chat_message_cap` | 5 | integer | Max messages before AI completes processing (shared with architecture) | Gateway (enforced), AI service (counter reset) |
| `context_rag_top_k` | 5 | integer | Chunks retrieved per RAG query | Context Agent RAG pipeline |
| `context_rag_min_similarity` | 0.7 | float | Minimum cosine similarity for chunk retrieval | Context Agent RAG pipeline |

**Removed parameters:**
- `max_keywords_per_idea` — Keyword system eliminated
- `similarity_vector_threshold` — Similarity system eliminated

> **Convention note:** All time-based parameters use **seconds** to match the architecture's seed data convention. The AI service converts to milliseconds internally where needed (e.g., `debounce_timer * 1000` for the debouncer, `ai_processing_timeout * 1000` for agent timeouts). Parameters marked "shared with architecture" already exist in `data-model.md` application/infrastructure seed data.

---

## 11. Environment Variables (AI Service)

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI service endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | Yes | API version (e.g., `2024-12-01-preview`) |
| `AZURE_OPENAI_DEFAULT_DEPLOYMENT` | Yes | Default deployment name (fallback if admin parameter empty) |
| `AZURE_OPENAI_CHEAP_DEPLOYMENT` | Yes | Cheap tier deployment name (GPT-4o-mini, not admin-configurable) |
| `AZURE_OPENAI_ESCALATED_DEPLOYMENT` | Yes | Escalated tier deployment name (fallback if admin parameter empty) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Yes | Embedding model deployment name (text-embedding-3-small) |

**Relationship between env vars and admin parameters:**
- Environment variables set initial/fallback deployment names.
- Admin parameters (`default_ai_model`, `escalated_ai_model`) override at runtime.
- If admin parameters are empty, environment variable values are used.
- Cheap tier and embedding deployment are environment-only (not admin-configurable).

---

## 12. AI Service Internal Structure

The AI service (`services/ai/`) is a lightweight Django 5 application. The Architect defined the scaffold; this section defines the full internal structure.

```
services/ai/
├── agents/
│   ├── base.py                        # BaseAgent: SK kernel setup, token tracking, timeout, retry
│   ├── facilitator/
│   │   ├── agent.py                   # FacilitatorAgent(BaseAgent)
│   │   ├── plugins.py                 # FacilitatorPlugin: 6 SK kernel functions
│   │   └── prompt.py                  # System prompt template + context assembly
│   ├── context_agent/
│   │   ├── agent.py                   # ContextAgent(BaseAgent)
│   │   └── prompt.py                  # System prompt template
│   ├── context_extension/
│   │   ├── agent.py                   # ContextExtensionAgent(BaseAgent)
│   │   └── prompt.py                  # System prompt template
│   ├── summarizing_ai/
│   │   ├── agent.py                   # SummarizingAgent(BaseAgent)
│   │   └── prompt.py                  # System prompt template (3 modes, 2 project types)
│   └── context_compression/
│       ├── agent.py                   # ContextCompressionAgent(BaseAgent)
│       └── prompt.py                  # System prompt template
├── processing/
│   ├── pipeline.py                    # Pipeline orchestrator: steps 1–6, abort handling
│   ├── context_assembler.py           # Build XML-structured prompt from raw data
│   ├── debouncer.py                   # Debounce logic with abort-and-restart
│   ├── fabrication_validator.py       # Post-processing requirements validation (non-AI)
│   └── version_tracker.py            # Requirements document version tracking
├── embedding/
│   ├── chunker.py                     # Chunk admin bucket content (section-aware + overlap)
│   ├── embedder.py                    # Generate embeddings via Azure OpenAI
│   └── reindexer.py                   # Full re-index on bucket update
├── kernel/
│   ├── model_router.py               # Route agents to correct Azure OpenAI deployment by tier
│   ├── sk_factory.py                 # Create configured SK Kernel instances per agent type
│   └── token_tracker.py              # Per-invocation token usage tracking + metrics
├── grpc_server/
│   ├── servicer.py                    # gRPC service implementation
│   └── interceptors.py               # Logging, error handling interceptors
├── events/
│   ├── consumers.py                   # Message broker event consumers
│   └── publishers.py                 # ai.* event publishing helpers
├── models/
│   ├── context_summaries.py           # Django model for chat_context_summaries
│   ├── facilitator_bucket.py          # Django model for facilitator_context_bucket
│   ├── context_bucket.py             # Django model for context_agent_bucket
│   └── context_chunks.py             # Django model for context_chunks (pgvector)
├── fixtures/
│   └── (mock responses for E2E testing when AI_MOCK_MODE=true)
├── tasks.py                           # Celery tasks: re-indexing
├── settings.py                        # Django settings
└── urls.py                            # Minimal (health check only — primary interface is gRPC)
```

**Removed directories/modules:**
- `agents/board_agent/` — Board Agent eliminated
- `agents/keyword_agent/` — Keyword Agent eliminated
- `agents/deep_comparison/` — Deep Comparison eliminated
- `agents/merge_synthesizer/` — Merge Synthesizer eliminated
- `embedding/idea_embedder.py` — Idea similarity embedding eliminated
- `models/idea_embeddings.py` — Idea embeddings table eliminated

---

## 13. Rejected Alternatives

| Alternative | Why Rejected |
|-------------|-------------|
| **AutoGen** for multi-agent orchestration | ZiqReq's delegation flows are predefined pipelines, not dynamic conversations. AutoGen's overhead is unnecessary. |
| **LangChain/LangGraph** | Heavy abstraction layer. Not Azure-native. The microservice architecture already handles routing via gRPC + events. |
| **Single monolithic agent** | Separating Facilitator from specialist agents (Context, Extension, Summarizing, Compression) improves testability and allows different model configs. |
| **Context Extension as implicit pipeline trigger** (old design) | Making it an explicit Facilitator tool gives the model control over when to search history. Cleaner contract. |
| **Message broker between same-cycle agents** | Unnecessary serialization overhead. In-process calls are faster and simpler when agents run in the same service within a single cycle. |
| **Blocking delegation (Facilitator waits for Context Agent)** | Non-blocking delegation with second pass is cleaner. The Facilitator's first SK loop ends, Context Agent runs, then a fresh Facilitator invocation with findings. Avoids long-running function calls. |
| **Per-request AI response caching** | Every request has unique context (current project state). No two requests are identical. Caching would only add complexity. |
| **Separate vector DB (Pinecone, Weaviate)** | pgvector is sufficient for the corpus scale (hundreds of context chunks). Avoids additional infrastructure. |
