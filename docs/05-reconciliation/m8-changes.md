# Milestone 8 Spec Reconciliation

## Summary
- **Milestone:** M8 — AI Board Agent & Context
- **Date:** 2026-03-11
- **Reconciliation Result:** CLEAN — Zero deviations found
- **Total deviations found:** 0
- **Auto-applied (SMALL TECHNICAL):** 0
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

---

## Reconciliation Analysis

### Sources Reviewed
1. **Progress file:** `.ralph/archive/m8-ai-context/progress.txt` (181 lines, 10 user stories)
2. **QA report:** `docs/08-qa/qa-m8-ai-context.md` (180 lines, PASS verdict)
3. **Upstream specs:** `docs/02-architecture/`, `docs/03-ai/`, `docs/03-design/`, `docs/05-milestones/milestone-8.md`
4. **Implementation code:** AI service agents, Gateway views, Frontend components

### QA Report Conclusion
> "No deviations found. All 10 user stories passed with 0 defects and 0 deviations."

All 10 user stories passed QA with zero defects and zero deviations. The QA engineer verified implementation against PRD acceptance criteria and upstream specification documents.

---

## Changes Applied

**No changes applied.** All upstream specification documents remain accurate and require no updates.

---

## Documents Reviewed (No Modifications)

The following upstream documents were reviewed and found to accurately describe the M8 implementation:

- `docs/02-architecture/api-design.md` — Context-window endpoint, event contracts (ai.board.updated, ai.delegation.complete)
- `docs/02-architecture/data-model.md` — context_agent_buckets, context_chunks, chat_context_summaries, idea_embeddings, idea_keywords
- `docs/02-architecture/project-structure.md` — AI service agent structure, embedding pipeline
- `docs/03-ai/agent-architecture.md` — BoardAgent, ContextAgent, ContextExtensionAgent, ContextCompressionAgent, KeywordAgent
- `docs/03-ai/system-prompts.md` — Agent system prompts
- `docs/03-ai/tools-and-functions.md` — Board Agent 8 tools, Facilitator delegation tools
- `docs/03-design/component-specs.md` — ContextWindowIndicator (S5.7), SVG progress ring, 80% warning threshold
- `docs/05-milestones/milestone-8.md` — M8 scope, acceptance criteria

---

## Implementation Patterns Discovered

The following implementation patterns were discovered during M8 and documented in progress.txt for future reference:

### Testing Infrastructure
- AI service tests require `DJANGO_SETTINGS_MODULE=ai_service.settings.test` (not gateway.settings.test)
- Docker compose build needed between test runs to pick up source changes (COPY layer)
- Running individual AI test files via pytest path fails with ModuleNotFoundError — run all tests via `pytest` without path filter
- Radix Tooltip renders duplicate content (visible + screen reader) — use `getAllByText` in tests, not `getByText`

### Agent Architecture
- All new agents (Board, Context, Context Extension, Context Compression, Keyword) inherit BaseAgent
- Context-focused agents use no tools (direct chat completion via SK)
- BoardAgent uses max_auto_invoke_attempts=10 (vs Facilitator's 3) and lower temperature (0.3 vs 0.7)
- ContextExtensionAgent uses escalated model tier for larger context window
- KeywordAgent uses temperature 0.3 for deterministic extraction

### Pipeline Integration
- Pipeline Step 4 routes by delegation_type: "context_agent" → ContextAgent, "context_extension" → ContextExtensionAgent
- Pipeline Step 5 loads fresh board state via CoreClient.get_board_state() at invocation time (not cached from Step 1)
- Pipeline Step 6 runs compression check, then keyword extraction, before ai.processing.complete event
- Board Agent invocation publishes ai.board.updated event only when mutation_count > 0
- Delegation results wrapped in XML tags: `<context_agent_findings>` or `<extension_results>`

### Embedding & RAG
- Retriever uses pgvector CosineDistance annotation and filters by max_distance = 1.0 - min_similarity
- Embedder uses openai AsyncAzureOpenAI directly (not SK) because SK embedding support is limited
- Chunker uses word-based splitting with ~0.75 words per token ratio, overlap in words not tokens
- Token estimation: ~4 chars per token (OpenAI heuristic) against 128k context limit
- Reindexer uses atomic transaction for DELETE+INSERT — no partial updates on failure
- IdeaEmbedder generates embedding from concatenated title + chat_summary + board_content

### Plugin Patterns
- BoardPlugin follows same pattern as FacilitatorPlugin: @kernel_function decorators, _error_response helper, mutations tracked on plugin instance
- Facilitator plugin validation methods query Django models directly (must be mocked in tests):
  - `_context_bucket_has_content()` queries ContextAgentBucket model
  - `_has_compressed_context()` queries ChatContextSummary model

### Lazy Import Strategies
- BoardAgent is lazily imported inside pipeline _step_board_agent to avoid circular imports
- IdeaEmbedder is lazily imported inside KeywordAgent._execute — must patch at source (embedding.idea_embedder.IdeaEmbedder)
- Reindexer lazily imports Chunker/Embedder in __init__ — cannot patch at module level
- Servicer imports are lazy (from ... import inside methods) — use patch.dict(sys.modules, ...) to mock modules

### Mock Mode Behavior
- In mock mode (AI_MOCK_MODE=True), Board Agent delegation returns stub results (goes through _load_mock_response path)
- Context Agent/Extension delegation returns empty findings without invoking agent
- Compression check skipped entirely in mock mode — no admin param read, no agent invocation
- Keyword extraction skipped in mock mode (same pattern as compression check)

### Frontend Implementation
- ContextWindowIndicator uses SVG progress ring with strokeDasharray/strokeDashoffset for percentage fill
- Component polls every 30s, hidden when idea state is not 'open'
- At usage >= 80%, ring color changes from primary (gold) to amber warning
- ChatContextSummary added as unmanaged model in gateway to read AI service's chat_context_summaries table
- Gateway context-window endpoint estimates tokens using ~4 chars/token heuristic against 128k limit

---

## Test Coverage

### Test Matrix
- **T-2.14.01** — Context window indicator renders progress ring at correct percentage
- **T-2.14.02** — Shows tooltip with context details on hover
- **T-2.14.03** — Compression triggers above threshold
- **T-2.15.01** — delegate_to_context_agent tool called
- **T-2.15.02** — Delegation empty bucket rejected
- **T-2.15.03** — No chunks returns refusal (grounding)
- **T-2.17.01** — Create box node publishes event
- **T-2.17.02** — Body contains bullet points
- **T-2.17.03** — Create group node
- **T-5.1.01** — Extracts keywords via SK
- **T-5.1.02** — Parse max keywords cap
- **T-5.1.03** — Parse multi-word filtered

All 12 test matrix IDs registered in `.ralph/test-manifest.json` with correct file paths and function names.

---

## Impact on Future Milestones

### No Upstream Changes Required
All implemented features match the upstream specifications. No spec updates are needed for future milestones.

### gRPC Wire-up (Future Milestone)
Several CoreClient stub methods were added in M8 for future gRPC implementation:
- `CoreClient.get_full_chat_history()` — returns full chat history for Context Extension Agent
- `CoreClient.upsert_context_summary()` — persists compression summary
- `CoreClient.upsert_keywords()` — persists extracted keywords
- `CoreClient.upsert_idea_embedding()` — persists idea vector embedding

These methods currently return mock data. A future milestone will wire them to actual gRPC servicers in the Core service.

### Admin Parameters
M8 added the following admin parameters (defaults in code):
- `context_rag_top_k` (default 5) — Number of chunks to retrieve for Context Agent
- `context_rag_min_similarity` (default 0.7) — Minimum similarity threshold for chunk retrieval
- `max_chunk_tokens` (default 512) — Maximum tokens per context chunk
- `chunk_overlap` (default 50) — Overlap in words between chunks

---

## Regression Validation

The following M8 components must continue to work correctly after future milestones:

### Board Agent
- [ ] BoardAgent creates/updates/deletes nodes via 8 @kernel_function tools
- [ ] BoardAgent validates locked nodes (rejects modifications)
- [ ] BoardAgent publishes ai.board.updated event when mutation_count > 0
- [ ] Pipeline Step 5 invokes BoardAgent with fresh board state when instructions present
- [ ] request_board_changes tool validates intent enum and stores instructions

### Context Agents
- [ ] ContextAgent retrieves chunks via pgvector cosine similarity
- [ ] ContextAgent returns grounding refusal when no chunks found
- [ ] ContextExtensionAgent loads full chat history with escalated model tier (90s timeout)
- [ ] ContextCompressionAgent produces incremental summaries at 60% threshold
- [ ] KeywordAgent extracts max 20 lowercase single-word keywords, sorted alphabetically

### Delegation Tools
- [ ] delegate_to_context_agent validates bucket has content
- [ ] delegate_to_context_extension validates compressed context exists
- [ ] Pipeline Step 4 routes delegation by type: context_agent or context_extension
- [ ] Pipeline Step 4 re-invokes Facilitator with delegation results wrapped in XML tags
- [ ] Pipeline publishes ai.delegation.complete event after delegation resolution

### Embedding Pipeline
- [ ] Chunker splits context by sections with configurable max_tokens and overlap
- [ ] Embedder calls Azure OpenAI embedding API for each chunk
- [ ] Reindexer performs atomic DELETE+INSERT (no partial updates on failure)
- [ ] IdeaEmbedder generates idea embedding from title + chat_summary + board_content
- [ ] Context embedding triggered via gRPC servicer when bucket content changes

### Frontend
- [ ] ContextWindowIndicator shows SVG progress ring (20px) with correct percentage
- [ ] Ring color changes to amber at 80% usage threshold
- [ ] Tooltip shows message_count, compression_iterations, recent_message_count
- [ ] Component polls every 30s, hidden when idea state is not 'open'
- [ ] GET /api/ideas/:id/context-window returns usage_percentage with auth + ownership check

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 381 Python tests pass
- [ ] All 265 Node tests pass
- [ ] Ruff lint passes

---

## Verdict

**M8 implementation is CLEAN.**

- ✅ Zero spec deviations
- ✅ All upstream specs remain accurate
- ✅ QA verified: 10/10 stories passed, 0 defects, 0 deviations
- ✅ No reconciliation updates required
- ✅ All test matrix IDs implemented and verified

**Next milestone:** M9 will build on M8's AI capabilities with additional features while all M8 components remain regression-tested.
