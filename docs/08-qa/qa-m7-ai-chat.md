# QA Report: Milestone 7 — AI Core: Chat Processing Pipeline

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m7.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed all 10 user stories for Milestone 7 (AI Core — Chat Processing Pipeline), covering the full AI service setup (Semantic Kernel base, Facilitator agent, 7-step pipeline, debouncer), three AI tools (send_chat_message, react_to_message, update_title), Gateway event consumers, frontend AI processing indicator, and rate limit integration. All 240 Python tests pass, all 17 test matrix IDs are found and substantive, required gate checks pass, and code matches acceptance criteria across all stories.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | AI Service Django Setup - Semantic Kernel Base | PASS | BaseAgent ABC with async process(), SK kernel factory, model router (3 tiers), token tracker, env vars validated, admin params seeded |
| US-002 | Facilitator Agent Implementation | PASS | FacilitatorAgent extends BaseAgent, 6 @kernel_function tools in FacilitatorPlugin, events published, delegation returns queued, board stub returns accepted, SK config max_auto_invoke=3/auto |
| US-003 | Chat Processing Pipeline Orchestrator | PASS | 7-step pipeline: load, assemble, Facilitator, delegation (stub), Board Agent (stub), publish complete, cleanup. Version tracking, PipelineAborted at step boundaries |
| US-004 | Debouncer Implementation | PASS | start/reset/cancel, DebouncerState enum (IDLE/DEBOUNCING/PROCESSING), reads admin param, publishes ai.processing {state: debouncing} |
| US-005 | send_chat_message Tool | PASS | Publishes ai.chat_response.ready with all required fields, [[Item Title]] validation, returns message_id/created_at None placeholders |
| US-006 | react_to_message Tool | PASS | Publishes ai.reaction.ready, validates user-only messages, duplicate detection via has_ai_reaction flag |
| US-007 | update_title Tool | PASS | Publishes ai.title.updated with truncation at 60 chars, validates title_manually_edited=false, frontend AnimatePresence animation |
| US-008 | AI Event Consumers in Gateway | PASS | AIEventConsumer subscribes to 3 event types + processing.complete, 3 retries (1s/2s/4s), idempotency via event_id set, DLQ, background process |
| US-009 | AI Processing Indicator (Frontend) | PASS | Animated dots with motion-safe:animate-bounce, shows on started, hides on completed/failed, text-sm text-muted-foreground centered |
| US-010 | Rate Limit Integration | PASS | 429 when counter >= cap, counter increment per message, reset on ai.processing.complete, frontend overlay + toast via react-toastify |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 17 found / 0 missing out of 17 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-2.1.03 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests silent mode without @ai returns no action |
| T-2.1.04 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests silent mode with @ai forces response |
| T-2.3.01 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests update_title event published |
| T-2.3.02 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests title_manually_edited=true rejection |
| T-2.3.03 | FOUND | `frontend/src/__tests__/title-update-animation.test.tsx` | Verified — tests framer-motion AnimatePresence on title change |
| T-2.4.01 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests react without chat response (decision layer) |
| T-2.7.01 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests valid reaction types (thumbs_up/thumbs_down/heart) |
| T-2.7.02 | FOUND | `services/ai/tests/test_facilitator.py`, `services/gateway/apps/websocket/tests/test_ai_consumer.py` | Verified — tests UNIQUE duplicate check + consumer persistence |
| T-2.10.01 | FOUND | `services/ai/tests/test_debouncer.py` | Verified — tests debounce waits configurable timer before callback |
| T-2.10.02 | FOUND | `services/ai/tests/test_debouncer.py` | Verified — tests two messages result in single processing cycle |
| T-2.10.03 | FOUND | `services/ai/tests/test_pipeline.py` | Verified — tests version mismatch triggers abort |
| T-2.11.01 | FOUND | `services/gateway/apps/chat/tests/test_rate_limit.py` | Verified — tests 429 after cap messages |
| T-2.11.02 | FOUND | `services/gateway/apps/chat/tests/test_rate_limit.py` | Verified — tests counter reset on ai.processing.complete |
| T-2.11.03 | FOUND | `frontend/src/__tests__/rate-limit.test.tsx` | Verified — tests toast warning on rate_limit WebSocket event |
| T-2.12.01 | FOUND | `frontend/src/__tests__/ai-processing-indicator.test.tsx` | Verified — tests indicator visible on {state: started} |
| T-2.12.02 | FOUND | `frontend/src/__tests__/ai-processing-indicator.test.tsx` | Verified — tests indicator hidden on {state: completed} |
| T-2.15.01 | FOUND | `services/ai/tests/test_facilitator.py` | Verified — tests delegate_to_context_agent publishes event |

*All 17 expected tests found and verified as substantive.*

---

## Defects

No defects found.

---

## Deviations

No deviations found. Implementation matches upstream specs across all stories.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python Tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 240 passed, 0 failed, 4 warnings |
| Frontend Typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | FAIL (optional) | Pre-existing: "Duplicate module named events" — `services/core/events/__init__.py` vs `services/ai/events/__init__.py`. Not caused by M7 changes. |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | 2 errors + 1 warning: `nodes` unused in `ai-modified-indicator.test.tsx:186`, `absPosition` unused in `board-interactions.test.tsx:116`, missing useEffect dep in `FreeTextNode.tsx:34`. All pre-existing (not in M7-modified files). |

**Note:** Both optional gate failures are pre-existing issues in files not modified by M7. Required gates (typecheck, ruff) pass cleanly.

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | Clean |
| Backend lint (Ruff) | PASSED | Clean |
| Backend typecheck (mypy) | FAILED (optional) | Pre-existing duplicate module name (`events`) across services — not an M7 issue |
| Frontend lint (ESLint) | FAILED (optional) | Pre-existing unused vars in test files and missing dep in FreeTextNode — not in M7-modified files |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No critical or major security findings | — |

**Detailed review:**

- **Injection:** No raw SQL. Django ORM used throughout. User inputs validated via DRF serializers before persistence.
- **Broken Authentication:** Auth checks present on all REST endpoints (`_require_auth`, `_check_access`). WebSocket auth via middleware. No hardcoded credentials found.
- **Sensitive Data Exposure:** Azure OpenAI keys read from env vars (not hardcoded). No secrets in client-side code.
- **XSS:** React auto-escapes. No `dangerouslySetInnerHTML` in M7 components. Board ref `[[Title]]` validated server-side.
- **Broken Access Control:** Chat message creation checks user access to idea (owner/co-owner/collaborator). Rate limit per-idea prevents abuse.
- **CSRF:** Django REST framework handles CSRF. State-changing operations are POST with auth.
- **Security Misconfiguration:** CORS not overly permissive. No debug modes in production config.
- **Rate Limiting:** In-memory counters are per-process (not cross-process). Acceptable for M7; noted in progress.txt that future milestones should use Redis. Not a defect — spec doesn't require Redis for M7.

**Minor observations (not defects):**
- In-memory rate limit counters (`_rate_limit_counters` in views.py) don't persist across process restarts. Documented as intentional for M7.
- In-memory idempotency set (`_processed_event_ids` in consumers.py) will grow unbounded over long-running process. Acceptable for M7 scope.
- Broad `except Exception` in `_get_chat_message_cap()` at views.py:47 — this is intentional to handle missing unmanaged table in tests, documented in progress.txt.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No critical or major performance findings | — |

**Detailed review:**

- **N+1 Queries:** Chat message listing uses single queryset with `filter().order_by()`. No loop queries found.
- **Missing Indexes:** `ChatMessage.idea_id` is a ForeignKey (auto-indexed by Django). Rate limit counter uses in-memory dict (no DB queries).
- **Unnecessary Re-renders:** AIProcessingIndicator uses early return when not visible. useRateLimit hook properly memoizes reset callback. WorkspaceHeader uses useCallback for handlers.
- **Bundle Size:** No large new dependencies. framer-motion already used by project. react-toastify already present.
- **Memory Leaks:** Event listeners properly cleaned up in useEffect return functions. Debouncer cleanup() removes per-idea state. AsyncIO tasks cancelled on reset/cancel.
- **Blocking Operations:** All AI processing is async. Debouncer uses asyncio.sleep. Pipeline steps are async with abort checks between each.

**Minor observations (not defects):**
- `_processed_event_ids` set in AIEventConsumer will grow unbounded. Future milestones should implement TTL-based cleanup or Redis.
- `_rate_limit_counters` dict in views.py never cleaned up except on ai.processing.complete. Long-lived ideas accumulate entries. Not a concern at M7 scale.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| AIProcessingIndicator | `docs/03-design/component-specs.md` S5.4 | PASS | `text-sm`, `text-muted-foreground`, animated dots with sequential delay, `motion-safe:animate-bounce` respects prefers-reduced-motion |
| WorkspaceHeader (title animation) | `docs/03-design/component-specs.md` S5.4 | PASS | framer-motion AnimatePresence with cross-fade on title change |
| Rate Limit Lockout | `docs/03-design/component-specs.md` S5.8 | PASS | Overlay integration in ChatPanel, toast warning via react-toastify |
| Agent Mode Dropdown | `docs/03-design/component-specs.md` | PASS | Select with Interactive/Silent options in WorkspaceHeader |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### AI Service
- [ ] AI service Django app boots successfully with SK SDK installed
- [ ] BaseAgent abstract class available at `services/ai/agents/base.py`
- [ ] Kernel factory creates SK Kernel with Azure OpenAI config at `services/ai/kernel/sk_factory.py`
- [ ] Model router routes to 3 deployment tiers (default/cheap/escalated) at `services/ai/kernel/model_router.py`
- [ ] TokenTracker logs input/output tokens at `services/ai/kernel/token_tracker.py`
- [ ] FacilitatorAgent processes input_data and returns result with events at `services/ai/agents/facilitator/agent.py`
- [ ] FacilitatorPlugin has 6 @kernel_function tools at `services/ai/agents/facilitator/plugins.py`

### Pipeline & Debouncer
- [ ] ChatProcessingPipeline.execute() runs 7 steps: load, assemble, Facilitator, delegation, Board Agent, publish complete, cleanup
- [ ] Version tracking detects stale processing (PipelineAborted on mismatch)
- [ ] Abort flag at step boundaries exits early without persisting
- [ ] Debouncer start/reset/cancel state machine works correctly
- [ ] Debouncer reads debounce_timer admin param (default 3s)
- [ ] Multiple messages during debounce result in single processing cycle

### AI Tools & Events
- [ ] send_chat_message publishes ai.chat_response.ready with idea_id, content, message_type, sender_type, ai_agent
- [ ] react_to_message publishes ai.reaction.ready with idea_id, message_id, reaction_type
- [ ] react_to_message rejects AI messages and duplicates
- [ ] update_title publishes ai.title.updated with title truncated to 60 chars
- [ ] update_title rejects when title_manually_edited=true
- [ ] [[Item Title]] board refs validated against board state

### Gateway Event Consumers
- [ ] AIEventConsumer processes ai.chat_response.ready, ai.reaction.ready, ai.title.updated, ai.processing.complete
- [ ] Retry logic: 3 attempts with 1s, 2s, 4s backoff before DLQ
- [ ] Idempotency: duplicate event_ids are skipped
- [ ] WebSocket broadcasts include full entity data for chat_message, ai_reaction, title_update

### Frontend
- [ ] AIProcessingIndicator shows on ws:ai_processing {state: started}, hides on completed/failed
- [ ] Animated dots respect prefers-reduced-motion via motion-safe
- [ ] Rate limit overlay shows "Chat locked" when rate limited
- [ ] Rate limit toast warning appears on ws:rate_limit event
- [ ] Rate limit unlocks on ws:ai_processing completed/failed
- [ ] Title animation triggers via framer-motion AnimatePresence on title change

### API Endpoints
- [ ] POST /api/ideas/:id/chat/messages returns 429 when rate limit counter >= chat_message_cap
- [ ] Rate limit counter increments per successful message creation
- [ ] Rate limit counter resets on ai.processing.complete event

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 240 Python tests pass
- [ ] Ruff lint passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
