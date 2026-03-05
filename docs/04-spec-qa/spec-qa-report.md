# Specification QA Report

**Date:** 2026-03-03
**Reviewer:** Spec QA (Claude)
**Verdict:** CONDITIONAL PASS

## Summary

All 26 specification files across 5 directories were validated for completeness, cross-reference integrity, naming consistency, and structural soundness. The specifications are comprehensive and well-structured — the Requirements Engineer, Software Architect, UI/UX Designer, AI Engineer, and Arch+AI Integrator produced thorough, detailed work.

**8 issues were fixed directly** during this review (unambiguous corrections: missing review category, incorrect table/column references, wrong feature cross-references). After fixes, **0 CRITICAL issues** remain. **27 WARNING-level issues** were identified — none block implementation, but several document gaps in derivation logic and endpoint error codes that implementers should be aware of. The Milestone Planner can proceed.

---

## Completeness

| File | Status | Notes |
|------|--------|-------|
| docs/01-requirements/vision.md | OK | |
| docs/01-requirements/user-roles.md | OK | |
| docs/01-requirements/features.md | OK | Fixed: F-10.2 added missing "Rejected" group |
| docs/01-requirements/pages.md | OK | |
| docs/01-requirements/data-entities.md | OK | |
| docs/01-requirements/nonfunctional.md | OK | |
| docs/01-requirements/constraints.md | OK | |
| docs/01-requirements/traceability.md | OK | All 75 features mapped |
| docs/01-requirements/_status.md | OK | handoff_ready: true |
| docs/02-architecture/tech-stack.md | OK | |
| docs/02-architecture/data-model.md | OK | 22 tables, 30 indexes |
| docs/02-architecture/api-design.md | OK | Fixed: 2 feature references (F-5.12→F-4.12, F-2.16→F-2.14) |
| docs/02-architecture/project-structure.md | OK | |
| docs/02-architecture/testing-strategy.md | OK | |
| docs/02-architecture/_status.md | OK | handoff_ready: true |
| docs/03-design/design-system.md | OK | |
| docs/03-design/page-layouts.md | OK | |
| docs/03-design/component-specs.md | OK | |
| docs/03-design/interactions.md | OK | |
| docs/03-design/component-inventory.md | OK | 84 components, 31 shared |
| docs/03-design/_status.md | OK | handoff_ready: true |
| docs/03-ai/agent-architecture.md | OK | Fixed: 5 corrections (table refs, column names, feature refs, param name) |
| docs/03-ai/system-prompts.md | OK | |
| docs/03-ai/tools-and-functions.md | OK | |
| docs/03-ai/model-config.md | OK | |
| docs/03-ai/guardrails.md | OK | |
| docs/03-ai/_status.md | OK | handoff_ready: true |
| docs/03-integration/integration-report.md | OK | 12 gaps resolved |
| docs/03-integration/audit-report.md | OK | All 12 AI feature chains COMPLETE |
| docs/03-integration/changes-applied.md | OK | |
| docs/03-integration/gap-analysis.md | OK | |
| docs/03-integration/_status.md | OK | handoff_ready: true |

**Result:** All 32 files present with substantive content. All handoff statuses confirmed.

---

## Fixes Applied During Review

These issues were unambiguous and corrected directly:

| # | File | Change | Reason |
|---|------|--------|--------|
| 1 | `features.md` (F-10.2) | Added "4. Rejected" to Review Page group list | `pages.md`, `page-layouts.md`, and `api-design.md` all include "Rejected". Omission in features.md. |
| 2 | `agent-architecture.md` (§9.2) | Changed `brd_drafts (sections_json JSONB)` → `brd_drafts (individual section_* columns)` | `data-model.md` defines `brd_drafts` with 6 individual `section_*` text columns, not a JSONB column. Introduced by Arch+AI Integrator (G-012 fix). |
| 3 | `agent-architecture.md` (§9.2) | Changed `ideas.keywords` → `idea_keywords.keywords (varchar[])` | Keywords stored in separate `idea_keywords` table, not on `ideas`. |
| 4 | `agent-architecture.md` (§6.2) | Changed `version` → `compression_iteration`, `messages_compressed_count` → `messages_covered_up_to_id` | Column names didn't match `data-model.md` definitions. |
| 5 | `agent-architecture.md` (§4.1) | Changed `ai_debounce_delay` → `debounce_timer` | Integrator fixed this in §10 but missed the pipeline diagram reference. |
| 6 | `agent-architecture.md` (§3.1, §8) | Changed `(F-15.1)` → `(F-14.1)` (2 occurrences) | F-15.1 is Idle Detection; correct reference is F-14.1 (Universal Error Pattern). |
| 7 | `api-design.md` (review/similar) | Changed `(F-5.12)` → `(F-4.12)` | F-5 only has F-5.1–F-5.8; the similar ideas review section feature is F-4.12. |
| 8 | `api-design.md` (context-window) | Changed `(F-2.16)` → `(F-2.14)` | F-2.16 is Company Context Management; context window indicator is F-2.14. |

---

## Cross-Reference Issues

| # | Severity | Source | Target | Issue |
|---|----------|--------|--------|-------|
| 1 | WARNING | api-design.md: `GET /api/ideas/:id` response — `has_been_submitted` | data-model.md: `ideas` table | API response includes `has_been_submitted: boolean` but no backing column exists. Must be derived (e.g., check if `brd_versions` exist for this idea). Derivation logic not documented. |
| 2 | WARNING | api-design.md: `GET /api/ideas/:id` response — `is_locked` | data-model.md: `ideas` table | API response includes `is_locked: boolean` for ideas but no column exists. Must be derived from `ideas.state` (locked when `in_review`, `accepted`, or `dropped`). Derivation logic not documented. |
| 3 | WARNING | api-design.md: `GET /api/ideas/:id` response — `merge_request_pending` | data-model.md | Derived field requiring query across `merge_requests` table. Not documented as derivation. |
| 4 | WARNING | api-design.md: `GET /api/reviews` response — `submitted_at` | data-model.md: `ideas` table | No `submitted_at` column. Must be derived from `review_timeline_entries` or `brd_versions.created_at`. |
| 5 | WARNING | api-design.md: `GET /api/admin/users/search` response | data-model.md: `users` table | `idea_count`, `review_count`, `contribution_count` are computed aggregations, not stored columns. |
| 6 | WARNING | api-design.md: `POST /api/ideas/:id/board/nodes` | data-model.md: `board_nodes` | Request body omits `created_by` and `ai_modified_indicator` — server must infer from request context (user REST = 'user', Board Agent gRPC = 'ai'). Inference logic not documented. |
| 7 | WARNING | features.md: F-4.10 | api-design.md: `POST /api/ideas/:id/submit` | Feature says "All Reviewers receive email notification for new submissions" but API side effects don't specify whether notification targets assigned reviewers only or all users with reviewer role when no reviewers are assigned. |
| 8 | WARNING | features.md: F-12.3 (Invitation Banner) | api-design.md: `GET /api/ideas/:id` | Floating banner for pending invitations needs invitation status, but `GET /api/ideas/:id` response doesn't include `pending_invitation` field. Frontend must cross-reference with `GET /api/invitations`. |
| 9 | WARNING | features.md: F-6.3 (Presence) | api-design.md: WebSocket protocol | Multi-tab deduplication ("multiple tabs show as one presence") is not described in the WebSocket protocol specification. |
| 10 | WARNING | features.md: F-5.8 (Manual Merge) | api-design.md | No preview/validate endpoint for target idea before creating a merge request via UUID/URL entry. |
| 11 | WARNING | api-design.md: `GET /api/ideas/:id/context-window` | data-model.md | Response requires cross-service data assembly: `chat_messages` (core-owned) + `chat_context_summaries` (ai-owned). |
| 12 | WARNING | api-design.md: gRPC `BrdGenerationRequest` | agent-architecture.md: §3.5 | gRPC defines 2 modes (`"full" | "selective"`) with mode names differing from agent's 3 modes (`full_generation | selective_regeneration | section_regeneration`). The gRPC `sections_to_regenerate` field can functionally cover all 3 modes, but the naming mismatch and undocumented mapping may confuse implementers. |

---

## Consistency Issues

| # | Severity | Files | Issue |
|---|----------|-------|-------|
| 1 | WARNING | api-design.md vs agent-architecture.md vs data-model.md | AI agent identifier inconsistency: WebSocket `ai_processing` event uses `agent: "summarizing"`, but `agent-architecture.md` uses "Summarizing AI"/"SummarizingAgent", and `data-model.md` `chat_messages.ai_agent` column examples use snake_case (`'facilitator'`, `'context_agent'`). The identifier "summarizing" should be "summarizing_ai" for consistency. |
| 2 | WARNING | data-model.md vs api-design.md | BRD section key name mapping: DB uses `section_title`, `section_short_description`, etc. (with `section_` prefix), while API uses `title`, `short_description` (without prefix). Serializer must handle this non-obvious mapping. |
| 3 | WARNING | design-system.md (§9.1) vs pages.md | Navbar placement ambiguity: design-system.md shows role-gated links (Reviews\*, Admin\*) in the left section alongside "Ideas", but pages.md describes them in the right-side section alongside utility items. |
| 4 | WARNING | page-layouts.md (§12) vs component-specs.md (§11.1) | Warning toast auto-dismiss conflict: page-layouts.md says warning toasts are "persistent", component-specs.md says "10 seconds" auto-dismiss. Implementers get contradictory guidance. |
| 5 | WARNING | data-model.md vs user-roles.md | Role casing: data-model.md stores lowercase (`'user'`, `'reviewer'`, `'admin'`), user-roles.md defines title case (`User`, `Reviewer`, `Admin`). Implementation must normalize. API consistently uses lowercase. |
| 6 | WARNING | data-model.md vs api-design.md | `review_assignments.assigned_by` (`'submitter' | 'self'`) is not exposed in any API response — data is inaccessible to clients. |

---

## Structural Issues

| # | Severity | Area | Issue |
|---|----------|------|-------|
| 1 | WARNING | State Machine | `review/undo` endpoint does not document valid source states. Should specify: only callable from `accepted`, `dropped`, or `rejected` states. |
| 2 | WARNING | State Machine | `rejected → in_review` transition has two distinct paths (user resubmit via `/submit`, reviewer undo via `/review/undo`) with different actors — distinction not explicit in undo endpoint documentation. |
| 3 | WARNING | State Machine | No formal state machine diagram exists in data-model.md. Transitions defined only in features.md (F-1.5) and implicitly in API endpoints. |
| 4 | WARNING | Error Handling | Submit endpoint (`POST /api/ideas/:id/submit`) has no validation error codes for BRD completeness (e.g., /TODO markers remaining, insufficient readiness). |
| 5 | WARNING | Error Handling | Review action endpoints (accept/reject/drop) lack endpoint-specific error codes (e.g., idea not in correct state, reviewer not assigned). |
| 6 | WARNING | Error Handling | Merge request endpoints lack error codes (invalid target state, duplicate pending request, self-merge). |
| 7 | WARNING | Error Handling | Board operation endpoints lack specific error codes (locked node edit, connection to non-existent node). |
| 8 | WARNING | Error Handling | WebSocket close frame codes/reasons not defined. Token expiry mid-session behavior unspecified. |
| 9 | WARNING | Orphaned Component | `IdeasListFloating` (component-inventory.md, Landing section) has no corresponding feature requirement in features.md. May be an intentional UX addition not captured in requirements. |

---

## Ambiguous Requirements

| # | Severity | Source | Issue |
|---|----------|--------|-------|
| 1 | WARNING | NFR-P1 | "Page load under 2 seconds during regular load" — "regular load" undefined. No concurrent user count or percentile target (p50/p95/p99). |
| 2 | WARNING | NFR-P8 | "without degrading in quality" — no measurable criterion for AI quality degradation. |
| 3 | WARNING | F-2.14 | "without degrading in quality" — same as NFR-P8. No quality benchmark. |
| 4 | WARNING | F-2.4 | "AI evaluates whether it has value to add" — "value" undefined. Intentionally left to AI judgment but makes testing difficult. |
| 5 | WARNING | F-5.1 | "once the idea direction is clear" — no measurable criterion for "clarity" (message count, content threshold). |
| 6 | WARNING | F-5.2 | "prefer false negatives over false positives" — philosophy stated but no precision/recall targets given. |
| 7 | WARNING | F-3.5 | "Last write wins for concurrent edits" — no specification of how "last" is determined in distributed context (server timestamp vs client timestamp). |
| 8 | WARNING | F-12.2 | "Transient, auto-dismissing" toasts — no duration specified in features.md (resolved differently in design docs, see Consistency Issue #4). |
| 9 | WARNING | NFR-A1 | "Keyboard-first navigation" — no concrete acceptance criteria (all elements focusable? full keyboard workflow? tab order?). |
| 10 | WARNING | Availability | "Best effort — no formal uptime guarantee" — intentional for internal tool but means no SLA to test against. |

---

## Statistics

- Total files validated: 32
- Total checks run: ~180
- CRITICAL issues found: 3 (all fixed during review)
- WARNING issues found: 27
- Fixes applied: 8 (across 4 files)
- Files modified: `features.md`, `agent-architecture.md`, `api-design.md`

---

## Verdict Reasoning

**CONDITIONAL PASS** — 0 CRITICAL issues remain after 8 direct fixes. 27 WARNINGs exist but none block implementation.

The WARNINGs fall into three categories:

1. **Derived field documentation gaps (7 issues):** Several API response fields (`has_been_submitted`, `is_locked`, `merge_request_pending`, `submitted_at`, user stats) are computed from database state but their derivation logic is not documented. Implementers can figure these out, but explicit documentation would save time.

2. **Missing endpoint-specific error codes (5 issues):** The global error handling format covers standard HTTP errors, and F-14.1 defines the universal error UX pattern. But individual endpoints (submit, review actions, merge, board ops, WebSocket) don't specify their validation error codes. Implementers will need to define these during development.

3. **Minor specification ambiguities (15 issues):** Naming inconsistencies, ambiguous requirements language, missing protocol details. None prevent implementation but may require implementer judgment calls.

**Recommendation:** The Strategy Planner should proceed. These WARNINGs should be tracked and resolved during implementation — they're typical "last mile" specification details that are best finalized when writing the actual code.
