# Model Configuration & Optimization

> **Status:** Definitive. Model selection, generation parameters, token budgets, and cost projections.
>
> **Date:** 2026-03-16
> **Author:** AI Engineer (Refactored for requirements assembly platform)
> **Input:** `docs/03-ai/agent-architecture.md`, `docs/03-ai/system-prompts.md`, `docs/03-ai/tools-and-functions.md`, `REFACTORING_PLAN.md`

---

## 1. Model Selection

### Chat Completion Models

| Tier | Recommended Model | Context Window | Agents | Admin-Configurable |
|------|------------------|---------------|--------|-------------------|
| **Default** | GPT-4o (latest) | 128K tokens | Facilitator, Context Agent, Summarizing AI | Yes — `default_ai_model` parameter (F-11.3) |
| **Cheap** | GPT-4o-mini | 128K tokens | Context Compression | No — environment variable `AZURE_OPENAI_CHEAP_DEPLOYMENT` |
| **Escalated** | GPT-4o (latest) | 128K tokens | Context Extension | Yes — `escalated_ai_model` parameter (F-11.3) |

**Notes:**
- Default and Escalated use the same model family but with different token budget allocations. Escalated allows the Context Extension agent to consume a much larger portion of the context window (full uncompressed chat history).
- If Azure OpenAI releases models with larger context windows (e.g., 256K+), the Escalated tier is the natural candidate for upgrade — no architecture change needed, just update the admin parameter.
- Cheap tier uses GPT-4o-mini because Context Compression doesn't require complex reasoning and processes high volume. Cost savings are significant.

**Agent count reduction:**
- Previous design: 9 agents (Facilitator, Board Agent, Context Agent, Context Extension, Summarizing AI, Keyword Agent, Deep Comparison, Context Compression, Merge Synthesizer)
- Current design: 5 agents (Facilitator, Context Agent, Context Extension, Summarizing AI, Context Compression)
- **Removed:** Board Agent (8 tools), Keyword Agent, Deep Comparison, Merge Synthesizer

### Embedding Model

| Model | Dimensions | Use Cases | Configuration |
|-------|-----------|-----------|---------------|
| text-embedding-3-small | 1536 | Company context RAG | Environment variable `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` |

**Why text-embedding-3-small over text-embedding-3-large:**
- The corpus is small (company context: hundreds of chunks).
- 1536 dimensions provide sufficient discriminative power for this scale.
- 2x cheaper and faster than text-embedding-3-large.
- If retrieval quality is insufficient, upgrading to text-embedding-3-large requires only re-indexing — no architecture change.

**Removed embedding use case:**
- ~~Idea similarity embeddings~~ — Similarity detection system eliminated

---

## 2. Generation Parameters

### Per-Agent Configuration

| Agent | Temperature | Top-P | Max Output Tokens | Frequency Penalty | Presence Penalty | Reasoning |
|-------|------------|-------|-------------------|-------------------|-----------------|-----------|
| **Facilitator** | 0.7 | 1.0 | 1,000 | 0.3 | 0.0 | Requirements assembly benefits from moderate creativity. Frequency penalty reduces repetitive phrasing across long conversations. |
| **Context Agent** | 0.2 | 1.0 | 1,500 | 0.0 | 0.0 | Factual retrieval from RAG chunks. Minimal creativity — accuracy over variety. |
| **Context Extension** | 0.2 | 1.0 | 2,000 | 0.0 | 0.0 | Factual retrieval from full chat history. Precise and detailed. |
| **Summarizing AI** | 0.3 | 1.0 | 4,000 | 0.0 | 0.0 | Structured document generation. Consistent, professional output. High max tokens for full requirements document. |
| **Context Compression** | 0.3 | 1.0 | 3,000 | 0.0 | 0.0 | Summarization needs consistency. High max tokens for comprehensive summaries of long conversations. |

**Removed agents:**
- ~~Board Agent~~ — 0.3 temp, 2000 tokens (spatial reasoning eliminated)
- ~~Keyword Agent~~ — 0.5 temp, 300 tokens (similarity system eliminated)
- ~~Deep Comparison~~ — 0.2 temp, 500 tokens (similarity system eliminated)
- ~~Merge Synthesizer~~ — 0.4 temp, 4000 tokens (merge functionality eliminated)

### Parameter Rationale

**Temperature:**
- 0.2 for factual/retrieval agents (Context Agent, Context Extension) — precision matters, creativity does not.
- 0.3 for structured generation (Summarizing AI, Compression) — consistent output format, minimal variation.
- 0.7 for the Facilitator — conversational requirements assembly benefits from natural variation. Below 0.7, responses become formulaic. Above 0.7, responses become unreliable.

**Frequency Penalty:**
- Only applied to the Facilitator (0.3). Long requirements conversations over many cycles risk repetitive phrasing ("That's a great point", "Let me help you structure this"). Frequency penalty reduces this.
- Not applied to other agents — they run independently per invocation and don't accumulate repetition patterns.

**Max Output Tokens:**
- Set conservatively per agent to prevent runaway generation.
- Facilitator: 1,000 — chat responses should be concise (1-3 paragraphs).
- Context Extension: 2,000 — detailed findings with quotes from full chat history.
- Summarizing AI: 4,000 — full requirements document with hierarchical structure can be lengthy.
- Context Compression: 3,000 — comprehensive summaries of long conversations.

---

## 3. Token Budgets

### Per-Agent Context Budget

Estimated token usage per invocation under typical conditions.

#### Facilitator (Requirements Assistant)

| Component | Typical Tokens | Maximum Tokens | Notes |
|-----------|---------------|---------------|-------|
| System prompt | 2,200 | 2,800 | Fixed. Includes all decision rules, guidance sections, context_extension_guidance. |
| Tool schemas | 2,000 | 2,000 | Fixed. SK injects function definitions. 6 tools. |
| Facilitator bucket (ToC) | 500 | 2,000 | Varies with admin content size (global + type-specific). |
| Chat context summary | 0–3,000 | 5,000 | 0 for new projects. Grows with compression cycles. |
| Recent chat messages | 2,000 | 15,000 | Last 20 messages. Varies with message length. |
| Requirements structure | 500 | 10,000 | Grows with structure complexity. |
| Project metadata + user context | 200 | 300 | Fixed-ish. |
| Delegation/extension results (if second pass) | 0 | 1,500 | Only on second pass after delegation. |
| **Total input** | **~7,500–10,500** | **~38,600** | Typical is well within 128K. |
| **Output** | **~500–800** | **1,000** | Concise chat responses. |

**Removed from previous design:** Board state (was 500–10,000 tokens)

#### Context Agent

| Component | Typical Tokens | Maximum Tokens | Notes |
|-----------|---------------|---------------|-------|
| System prompt | 500 | 500 | Fixed. Minimal. |
| Delegation query | 50 | 200 | |
| Retrieved chunks (top-5) | 1,500 | 3,000 | 5 chunks × 200-600 tokens each. |
| Project context | 200 | 500 | Brief summary for grounding. |
| **Total input** | **~2,300** | **~4,200** | Lightweight. |
| **Output** | **~300–600** | **1,500** | Findings summary. |

#### Context Extension (Escalated)

| Component | Typical Tokens | Maximum Tokens | Notes |
|-----------|---------------|---------------|-------|
| System prompt | 400 | 400 | Fixed. |
| Facilitator query | 100 | 200 | |
| Full uncompressed chat | 10,000 | 80,000 | Entire chat history. This is why escalated tier exists. |
| Requirements structure | 1,000 | 8,000 | |
| **Total input** | **~11,500** | **~88,600** | Can be very large for long projects. |
| **Output** | **~500–1,000** | **2,000** | Targeted answer. |

**No change from previous design** — Context Extension still the largest consumer.

#### Summarizing AI

| Component | Typical Tokens | Maximum Tokens | Notes |
|-----------|---------------|---------------|-------|
| System prompt | 1,500 | 2,000 | Includes mode-specific sections and project_type awareness. |
| Chat history | 5,000 | 25,000 | Summary + recent. Longer projects = more content. |
| Requirements structure | 1,000 | 8,000 | Hierarchical JSON (epics/stories or milestones/packages). |
| Company context findings | 300 | 1,500 | From delegation results in chat. |
| Current draft (selective) | 0 | 3,000 | Only when regenerating specific items. |
| **Total input** | **~8,000** | **~39,500** | |
| **Output** | **~1,500–2,500** | **4,000** | Full requirements document. |

**Changed from previous design:** Requirements structure instead of board state (similar token range).

#### Context Compression (Cheap)

| Component | Typical Tokens | Maximum Tokens | Notes |
|-----------|---------------|---------------|-------|
| System prompt | 500 | 500 | |
| Previous summary | 0–3,000 | 5,000 | 0 on first compression. |
| Messages to compress | 3,000 | 15,000 | Batch of messages since last compression. |
| **Total input** | **~3,500–7,000** | **~20,500** | |
| **Output** | **~1,000–2,000** | **3,000** | Narrative summary. |

**No change from previous design.**

### Context Window Utilization

With the compression threshold at 60% (default), the Facilitator triggers compression when its total context usage exceeds ~77K tokens (60% of 128K). Under typical conditions (10K-25K tokens), projects would need very long conversations before compression is needed.

**When compression typically triggers:**
- Projects with 100+ messages and a complex requirements structure
- Projects with extensive delegation results (company context embedded in chat)
- Multi-user projects with rapid conversation

Most projects (~80%) will complete requirements assembly without ever triggering compression.

---

## 4. Cost Projections

### Pricing Assumptions

Azure OpenAI pricing (representative enterprise pricing, varies by agreement):

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| GPT-4o | $2.50 / 1M tokens | $10.00 / 1M tokens | Default + Escalated tier |
| GPT-4o-mini | $0.15 / 1M tokens | $0.60 / 1M tokens | Cheap tier |
| text-embedding-3-small | $0.02 / 1M tokens | — | Embeddings |

### Per-Message Cost (Single Processing Cycle)

One chat message from a user triggers this processing:

| Agent | Trigger Rate | Input Tokens | Output Tokens | Cost (Input) | Cost (Output) | Cost per Message |
|-------|-------------|-------------|--------------|-------------|--------------|-----------------|
| Facilitator | 100% | 15,000 | 750 | $0.038 | $0.008 | $0.045 |
| Context Agent | 10% | 3,000 | 500 | $0.008 | $0.005 | $0.001 |
| Context Extension | 2% | 30,000 | 1,000 | $0.075 | $0.010 | $0.002 |
| Embedding update | 0% | — | — | — | — | $0.000 |
| **Total per message** | | | | | | **~$0.048** |

**Removed from previous design:**
- Board Agent (was $0.015 per message at 50% trigger rate)
- Keyword Agent (was $0.001 per message at 100% trigger rate)
- Idea embedding update (was $0.000 per message)

**Cost reduction:** ~$0.016 per message saved (25% reduction) by removing Board Agent and Keyword Agent.

### Per-Project Cost (Full Lifecycle)

Assumptions for a typical project:
- 30 chat messages (requirements assembly session)
- 1.5 requirements document generations (initial + one regen)
- 0.5 compression cycles (50% of projects need compression)
- 0.05 context extensions (5% of projects)

| Component | Calculation | Cost |
|-----------|------------|------|
| Requirements assembly (30 messages) | 30 × $0.048 | $1.44 |
| Requirements document generation (1.5×) | 1.5 × (20K in @ $2.50/M + 2.5K out @ $10/M) | $0.11 |
| Context Compression (0.5×, cheap) | 0.5 × (7K in @ $0.15/M + 2K out @ $0.60/M) | $0.001 |
| Context Extension (0.05×) | 0.05 × (30K in @ $2.50/M + 1K out @ $10/M) | $0.004 |
| **Total per project** | | **~$1.56** |

**Previous design cost:** ~$2.04 per project
**Current design cost:** ~$1.56 per project
**Savings:** $0.48 per project (23.5% reduction)

### Monthly Projections

| Scenario | Projects/Month | Cost/Month | Notes |
|----------|------------|-----------|-------|
| **Peak adoption** | 10,000 | ~$15,600 | Initial rollout, high exploration |
| **Sustained active** | 5,000 | ~$7,800 | Established usage pattern |
| **Steady state** | 2,000 | ~$3,120 | Long-term baseline |
| **Low usage** | 500 | ~$780 | Minimal activity |

**Previous design (peak):** ~$20,400/month
**Current design (peak):** ~$15,600/month
**Savings:** ~$4,800/month (23.5% reduction)

### Cost Breakdown by Tier

At peak adoption (10,000 projects/month):

| Tier | Primary Cost Drivers | Estimated Monthly | % of Total |
|------|---------------------|------------------|-----------|
| Default (GPT-4o) | Facilitator (every message), Context Agent, Summarizing AI | ~$15,200 | 97.4% |
| Cheap (GPT-4o-mini) | Context Compression | ~$5 | 0.03% |
| Escalated (GPT-4o) | Context Extension (rare) | ~$40 | 0.26% |
| Embeddings | Context chunk indexing | ~$2 | 0.01% |
| **Total** | | **~$15,247** | |

**Previous design total:** ~$20,130/month
**Removed costs:**
- Board Agent: ~$4,500/month (22%)
- Keyword Agent + idea embeddings: ~$280/month (1.4%)
- Deep Comparison: minimal (background, <0.1%)
- Merge Synthesizer: minimal (rare, <0.1%)

The dominant cost driver is still the Facilitator (runs on every message, GPT-4o, ~15K input tokens average).

### Cost Optimization Levers

| Lever | Savings Potential | Trade-off |
|-------|------------------|-----------|
| **Prompt caching (Azure OpenAI)** | High (~27%) | Azure OpenAI caches repeated prefixes at 50% discount. System prompt + tool schemas are identical across invocations. No quality trade-off. |
| **Reduce Facilitator input context** | High | Less context → potentially lower response quality. Tune compression threshold to summarize earlier. |
| **Move Facilitator to GPT-4o-mini** | High (~80% reduction) | Quality degradation for complex requirements assembly, worse function calling reliability. Not recommended for core agent. |
| **Reduce average messages per project** | High | Not an application-level decision — depends on user behavior. Better AI (resolving requirements faster) naturally reduces message count. |

### Prompt Caching Opportunity

Azure OpenAI's prompt caching provides a 50% discount on input tokens for cached prompt prefixes. For ZiqReq:

| Agent | Cacheable Prefix | Estimated Cache Hit Rate | Monthly Savings (Peak) |
|-------|-----------------|-------------------------|----------------------|
| Facilitator | System prompt + tool schemas (~4,200 tokens) | ~95% | ~$4,300 |
| Summarizing AI | System prompt (~1,500 tokens) | ~95% | ~$55 |
| Others | Small system prompts | ~95% | ~$10 |
| **Total prompt caching savings** | | | **~$4,365/month at peak** |

With prompt caching, peak monthly cost drops from ~$15,600 to ~$11,235.

**Previous design with caching:** ~$14,700/month
**Current design with caching:** ~$11,235/month
**Total savings from refactoring + caching:** ~$3,465/month (23.5%)

---

## 5. Caching Strategy

### Application-Level Caching

| Cache Target | Storage | TTL | Invalidation | Purpose |
|-------------|---------|-----|-------------|---------|
| Admin parameters | In-memory (per-service) | 30 seconds | On admin update event | Avoid DB read on every parameter access |
| Facilitator bucket content | In-memory (AI service) | 5 minutes | On admin update event | Avoid DB read on every Facilitator cycle |
| Requirements structure (per project) | In-memory (AI service) | Duration of processing cycle | On cycle start (fresh read) | Consistent structure state within a single cycle |
| SK Kernel instances | In-memory (AI service) | Permanent (singleton per agent type) | Never (stateless) | Avoid re-initializing Azure OpenAI connectors |
| Embedding model client | In-memory (AI service) | Permanent (singleton) | Never | Connection pooling for embedding API calls |

**Removed from previous design:** Board state caching (board eliminated)

### What Is NOT Cached

| Item | Reason |
|------|--------|
| AI API responses | Every request has unique context (current project state). No two requests are identical. |
| Chat messages | Always read fresh from DB via core service gRPC. Caching risks stale messages during fast-paced collaboration. |
| Context agent bucket content | Small enough to fetch on demand. Caching risks serving stale content after admin updates. |
| pgvector search results | Queries are contextual (unique per delegation). Results are not reusable. |

### Azure OpenAI Prompt Caching

Azure OpenAI automatically caches prompt prefixes. To maximize cache hits:

1. **Static prefix first.** System prompt and tool schemas must be the first tokens in every request. These are identical across invocations of the same agent type.
2. **Dynamic context after prefix.** Project-specific data (chat, requirements structure, metadata) comes after the static prefix.
3. **Consistent formatting.** Runtime variable injection must produce identical prefix tokens when the system prompt hasn't changed. Use deterministic template rendering.

This requires no code changes — it's an API-level optimization. The token layout already follows this pattern by design (system prompt in `<system>` tags, project context in `<project_context>` tags).

---

## 6. Model Routing

### Router Implementation

```python
# services/ai/kernel/model_router.py

class ModelRouter:
    """Routes agents to the correct Azure OpenAI deployment based on model tier."""

    def __init__(self):
        self._cheap_deployment = os.environ['AZURE_OPENAI_CHEAP_DEPLOYMENT']
        self._embedding_deployment = os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT']

    def get_chat_deployment(self, tier: str) -> str:
        """Return the Azure OpenAI deployment name for a chat completion agent."""
        if tier == 'default':
            return get_parameter('default_ai_model')
        elif tier == 'cheap':
            return self._cheap_deployment
        elif tier == 'escalated':
            return get_parameter('escalated_ai_model')
        else:
            raise ValueError(f"Unknown model tier: {tier}")

    def get_embedding_deployment(self) -> str:
        """Return the Azure OpenAI deployment name for embeddings."""
        return self._embedding_deployment
```

### Tier Assignment (Fixed)

| Agent | Tier | Rationale |
|-------|------|-----------|
| Facilitator | default | User-facing, complex reasoning, function calling |
| Context Agent | default | User-facing output quality |
| Context Extension | escalated | Needs large context budget for full chat history |
| Summarizing AI | default | Document generation quality |
| Context Compression | cheap | Background summarization, quality is secondary |

**Removed from previous design:**
- Board Agent — default tier (eliminated)
- Keyword Agent — cheap tier (eliminated)
- Deep Comparison — default tier (eliminated)
- Merge Synthesizer — default tier (eliminated)

Tier assignments are hardcoded per agent in the `BaseAgent` subclass. They are not admin-configurable. Admins configure which specific model deployment each tier points to, not which tier each agent uses.

### Admin Configuration

Per F-11.3, two admin parameters control model routing:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_ai_model` | (deployment-specific) | Azure OpenAI deployment name for default tier |
| `escalated_ai_model` | (deployment-specific) | Azure OpenAI deployment name for escalated tier |

Changing these parameters takes effect immediately for all new processing cycles. In-progress cycles complete with the model they started with.

---

## 7. Timeout & Retry Configuration

### Per-Agent Timeouts

| Agent | Timeout | Source | Rationale |
|-------|---------|--------|-----------|
| Facilitator | 60s | `ai_processing_timeout` (admin-configurable) | User is waiting for response. Hard limit prevents indefinite waits. |
| Context Agent | 30s | Hardcoded | Sub-step of a delegation flow. Should be fast (RAG retrieval + short generation). |
| Context Extension | 90s | 1.5× `ai_processing_timeout` | Extended context = more tokens = longer processing. User sees a delegation message so the wait is expected. |
| Summarizing AI | 60s | `ai_processing_timeout` | User is waiting on Review tab. Same hard limit. |
| Context Compression | 30s | Hardcoded | Background, non-critical. Quick generation. |

**Removed from previous design:**
- Board Agent — 60s (eliminated)
- Keyword Agent — 30s (eliminated)
- Deep Comparison — 30s (eliminated)
- Merge Synthesizer — 60s (eliminated)

### Retry Strategy

| Agent | Max Retries | Source | Backoff | On Final Failure |
|-------|------------|--------|---------|-----------------|
| Facilitator | 3 | admin: `max_retry_attempts` | 1s, 2s, 4s (exponential) | Error toast to user (F-15.1) |
| Context Agent | 0 | hardcoded | — | Facilitator responds without company context. |
| Context Extension | 0 | hardcoded | — | Facilitator responds: "I couldn't retrieve that detail." |
| Summarizing AI | 3 | admin: `max_retry_attempts` | 1s, 2s, 4s | Error toast on Review tab. |
| Context Compression | 1 | hardcoded | 1s | Uncompressed context used until next trigger. |

**Removed from previous design:**
- Board Agent — 2 retries (eliminated)
- Keyword Agent — 0 retries (eliminated)
- Deep Comparison — 1 retry (eliminated)
- Merge Synthesizer — 3 retries (eliminated)

---

## 8. Environment Variables (AI Service)

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

## 9. Monitoring Metrics

The AI service exposes these metrics for the Admin Panel monitoring dashboard (F-11.4):

| Metric | Description | Aggregation |
|--------|-------------|-------------|
| `ai.processing.count` | Total processing cycles triggered | Count per interval |
| `ai.processing.success_rate` | Percentage of cycles completing without error | Percentage per interval |
| `ai.processing.latency_p50` | Median Facilitator response time | Percentile per interval |
| `ai.processing.latency_p95` | 95th percentile Facilitator response time | Percentile per interval |
| `ai.tokens.input_total` | Total input tokens consumed | Sum per interval, per tier |
| `ai.tokens.output_total` | Total output tokens consumed | Sum per interval, per tier |
| `ai.delegation.count` | Context Agent delegation count | Count per interval |
| `ai.extension.count` | Context Extension delegation count | Count per interval |
| `ai.compression.count` | Context compression triggers | Count per interval |
| `ai.errors.count` | Processing errors by type | Count per interval, per error code |
| `ai.abort.count` | Pipeline aborts due to new messages | Count per interval |

**Removed from previous design:**
- `ai.board_agent.count` — Board Agent eliminated

These metrics are collected by the AI service and exposed via gRPC to the gateway for the monitoring dashboard. They are also used by the Celery-based monitoring health checks (F-11.5) to trigger alerts.

### Token Tracking

Per-invocation token tracking is built into the `BaseAgent` class:

```python
class BaseAgent:
    async def process(self, input: AgentInput) -> AgentOutput:
        result = await self.kernel.invoke(...)
        self._track_tokens(
            agent=self.__class__.__name__,
            tier=self.model_tier,
            input_tokens=result.metadata.get('usage', {}).get('prompt_tokens', 0),
            output_tokens=result.metadata.get('usage', {}).get('completion_tokens', 0),
            project_id=input.project_id,
        )
        return self.parse_output(result)
```

Token counts are published as metrics and logged for cost analysis. No per-request token data is persisted to the database — only aggregated metrics.
