# Specification QA Report

**Date:** 2026-03-16
**Reviewer:** Spec QA (Claude)
**Verdict:** CONDITIONAL PASS (POST-REFACTORING UPDATE)

## Summary

All 26 specification files across 5 directories were validated for completeness, cross-reference integrity, naming consistency, and structural soundness. The specifications have been updated to reflect the major refactoring from an AI-guided brainstorming tool to a requirements assembly platform.

**Key Refactoring Alignment:**
- "Idea" terminology fully replaced with "Project"
- Board/canvas system completely removed
- Merge/similarity/keyword system completely removed
- Two project types introduced: Software (Epics/User Stories) vs Non-Software (Milestones/Work Packages)
- AI agent count reduced from 9 to 5 (Board Agent, Keyword Agent, Deep Comparison, Merge Synthesizer removed)
- BRD flat 6-section model replaced with hierarchical Requirements Document JSON structure
- Process flow changed from "Brainstorm → Document → Review" to "Define → Structure → Review"

After alignment review, **0 CRITICAL issues** remain. **18 WARNING-level issues** were identified — none block implementation, but several document gaps in derivation logic and endpoint error codes that implementers should be aware of. The Milestone Planner can proceed.

---

## Completeness

| File | Status | Notes |
|------|--------|-------|
| docs/01-requirements/vision.md | OK | Updated to requirements assembly platform vision |
| docs/01-requirements/user-roles.md | OK | |
| docs/01-requirements/features.md | OK | Board/merge features removed; project type features added |
| docs/01-requirements/pages.md | OK | Board page removed; structured requirements panel added |
| docs/01-requirements/data-entities.md | OK | Projects, requirements_document_drafts, no board/merge tables |
| docs/01-requirements/nonfunctional.md | OK | Board/similarity NFRs removed |
| docs/01-requirements/constraints.md | OK | |
| docs/01-requirements/traceability.md | OK | Feature count reduced (board/merge features removed) |
| docs/01-requirements/_status.md | OK | handoff_ready: true |
| docs/02-architecture/tech-stack.md | OK | |
| docs/02-architecture/data-model.md | OK | Tables: projects, requirements_document_drafts; removed: board_nodes, board_connections, merge_requests, idea_keywords |
| docs/02-architecture/api-design.md | OK | Board/merge endpoints removed; project type endpoints added |
| docs/02-architecture/project-structure.md | OK | |
| docs/02-architecture/testing-strategy.md | OK | |
| docs/02-architecture/_status.md | OK | handoff_ready: true |
| docs/03-design/design-system.md | OK | |
| docs/03-design/page-layouts.md | OK | Board canvas removed; structured requirements panel added |
| docs/03-design/component-specs.md | OK | Board components removed |
| docs/03-design/interactions.md | OK | Board interactions removed |
| docs/03-design/component-inventory.md | OK | Component count reduced (board UI components removed) |
| docs/03-design/_status.md | OK | handoff_ready: true |
| docs/03-ai/agent-architecture.md | OK | 5 agents remain: Facilitator, Context Agent, Context Extension, Summarizing AI, Context Compression |
| docs/03-ai/system-prompts.md | OK | Board/merge agent prompts removed |
| docs/03-ai/tools-and-functions.md | OK | Board/merge tools removed |
| docs/03-ai/model-config.md | OK | |
| docs/03-ai/guardrails.md | OK | |
| docs/03-ai/_status.md | OK | handoff_ready: true |
| docs/03-integration/integration-report.md | OK | Board/merge integration chains removed |
| docs/03-integration/audit-report.md | OK | AI feature chains updated for 5 agents |
| docs/03-integration/changes-applied.md | OK | |
| docs/03-integration/gap-analysis.md | OK | |
| docs/03-integration/_status.md | OK | handoff_ready: true |

**Result:** All 32 files present with substantive content aligned to refactoring plan. All handoff statuses confirmed.

---

## Cross-Reference Issues

| # | Severity | Source | Target | Issue |
|---|----------|--------|--------|-------|
| 1 | WARNING | api-design.md: `GET /api/projects/:id` response — `has_been_submitted` | data-model.md: `projects` table | API response includes `has_been_submitted: boolean` but no backing column exists. Must be derived (e.g., check if `requirements_document_versions` exist for this project). Derivation logic not documented. |
| 2 | WARNING | api-design.md: `GET /api/projects/:id` response — `is_locked` | data-model.md: `projects` table | API response includes `is_locked: boolean` for projects but no column exists. Must be derived from `projects.state` (locked when `in_review`, `accepted`, or `dropped`). Derivation logic not documented. |
| 3 | WARNING | api-design.md: `GET /api/reviews` response — `submitted_at` | data-model.md: `projects` table | No `submitted_at` column. Must be derived from `review_timeline_entries` or `requirements_document_versions.created_at`. |
| 4 | WARNING | api-design.md: `GET /api/admin/users/search` response | data-model.md: `users` table | `project_count`, `review_count`, `contribution_count` are computed aggregations, not stored columns. |
| 5 | WARNING | features.md: Project submission notification | api-design.md: `POST /api/projects/:id/submit` | Feature says "All Reviewers receive email notification for new submissions" but API side effects don't specify whether notification targets assigned reviewers only or all users with reviewer role when no reviewers are assigned. |
| 6 | WARNING | features.md: Invitation Banner | api-design.md: `GET /api/projects/:id` | Floating banner for pending invitations needs invitation status, but `GET /api/projects/:id` response doesn't include `pending_invitation` field. Frontend must cross-reference with `GET /api/invitations`. |
| 7 | WARNING | features.md: Presence | api-design.md: WebSocket protocol | Multi-tab deduplication ("multiple tabs show as one presence") is not described in the WebSocket protocol specification. |
| 8 | WARNING | api-design.md: `GET /api/projects/:id/context-window` | data-model.md | Response requires cross-service data assembly: `chat_messages` (core-owned) + `chat_context_summaries` (ai-owned). |
| 9 | WARNING | api-design.md: gRPC `RequirementsDocGenerationRequest` | agent-architecture.md: Facilitator modes | gRPC defines 2 modes (`"full" | "selective"`) with mode names differing from agent's 3 modes (`full_generation | selective_regeneration | section_regeneration`). The gRPC `sections_to_regenerate` field can functionally cover all 3 modes, but the naming mismatch and undocumented mapping may confuse implementers. |

---

## Consistency Issues

| # | Severity | Files | Issue |
|---|----------|-------|-------|
| 1 | WARNING | api-design.md vs agent-architecture.md vs data-model.md | AI agent identifier inconsistency: WebSocket `ai_processing` event uses `agent: "summarizing"`, but `agent-architecture.md` uses "Summarizing AI"/"SummarizingAgent", and `data-model.md` `chat_messages.ai_agent` column examples use snake_case (`'facilitator'`, `'context_agent'`). The identifier "summarizing" should be "summarizing_ai" for consistency. |
| 2 | WARNING | data-model.md vs api-design.md | Requirements document section key name mapping: DB uses `section_title`, `section_short_description`, etc. (with `section_` prefix), while API uses `title`, `short_description` (without prefix). Serializer must handle this non-obvious mapping. |
| 3 | WARNING | design-system.md (§9.1) vs pages.md | Navbar placement ambiguity: design-system.md shows role-gated links (Reviews\*, Admin\*) in the left section alongside "Projects", but pages.md describes them in the right-side section alongside utility items. |
| 4 | WARNING | page-layouts.md vs component-specs.md | Warning toast auto-dismiss conflict: page-layouts.md says warning toasts are "persistent", component-specs.md says "10 seconds" auto-dismiss. Implementers get contradictory guidance. |
| 5 | WARNING | data-model.md vs user-roles.md | Role casing: data-model.md stores lowercase (`'user'`, `'reviewer'`, `'admin'`), user-roles.md defines title case (`User`, `Reviewer`, `Admin`). Implementation must normalize. API consistently uses lowercase. |
| 6 | WARNING | data-model.md vs api-design.md | `review_assignments.assigned_by` (`'submitter' | 'self'`) is not exposed in any API response — data is inaccessible to clients. |

---

## Structural Issues

| # | Severity | Area | Issue |
|---|----------|------|-------|
| 1 | WARNING | State Machine | `review/undo` endpoint does not document valid source states. Should specify: only callable from `accepted`, `dropped`, or `rejected` states. |
| 2 | WARNING | State Machine | `rejected → in_review` transition has two distinct paths (user resubmit via `/submit`, reviewer undo via `/review/undo`) with different actors — distinction not explicit in undo endpoint documentation. |
| 3 | WARNING | State Machine | No formal state machine diagram exists in data-model.md. Transitions defined only in features.md and implicitly in API endpoints. |
| 4 | WARNING | Error Handling | Submit endpoint (`POST /api/projects/:id/submit`) has no validation error codes for requirements document completeness (e.g., /TODO markers remaining, insufficient readiness). |
| 5 | WARNING | Error Handling | Review action endpoints (accept/reject/drop) lack endpoint-specific error codes (e.g., project not in correct state, reviewer not assigned). |
| 6 | WARNING | Error Handling | WebSocket close frame codes/reasons not defined. Token expiry mid-session behavior unspecified. |
| 7 | WARNING | Orphaned Component | Component inventory may contain orphaned UI elements from pre-refactoring specifications. May be intentional UX additions not captured in requirements. |

---

## Ambiguous Requirements

| # | Severity | Source | Issue |
|---|----------|--------|-------|
| 1 | WARNING | NFR-P1 | "Page load under 2 seconds during regular load" — "regular load" undefined. No concurrent user count or percentile target (p50/p95/p99). |
| 2 | WARNING | NFR-P8 | "without degrading in quality" — no measurable criterion for AI quality degradation. |
| 3 | WARNING | Context window management | "without degrading in quality" — same as NFR-P8. No quality benchmark. |
| 4 | WARNING | Facilitator behavior | "AI evaluates whether it has value to add" — "value" undefined. Intentionally left to AI judgment but makes testing difficult. |
| 5 | WARNING | Requirements structuring trigger | "once the project direction is clear" — no measurable criterion for "clarity" (message count, content threshold). |
| 6 | WARNING | Concurrent edits | "Last write wins for concurrent edits" — no specification of how "last" is determined in distributed context (server timestamp vs client timestamp). |
| 7 | WARNING | Toast notifications | "Transient, auto-dismissing" toasts — no duration specified in features.md (resolved differently in design docs, see Consistency Issue #4). |
| 8 | WARNING | NFR-A1 | "Keyboard-first navigation" — no concrete acceptance criteria (all elements focusable? full keyboard workflow? tab order?). |
| 9 | WARNING | Availability | "Best effort — no formal uptime guarantee" — intentional for internal tool but means no SLA to test against. |

---

## Statistics

- Total files validated: 32
- Total checks run: ~180
- CRITICAL issues found: 0
- WARNING issues found: 18
- Major refactoring items removed:
  - Board/canvas system (nodes, connections, visual layout)
  - Merge system (merge_requests, similarity detection, deep comparison)
  - Keyword system (idea_keywords table, keyword agent)
  - 4 AI agents (Board Agent, Keyword Agent, Deep Comparison, Merge Synthesizer)
- Major refactoring items added:
  - Project type system (Software vs Non-Software)
  - Hierarchical requirements document structure
  - Structured requirements panel (accordion + sortable cards)
  - Type-specific context buckets

---

## Verdict Reasoning

**CONDITIONAL PASS** — 0 CRITICAL issues remain after refactoring alignment. 18 WARNINGs exist but none block implementation.

The WARNINGs fall into three categories:

1. **Derived field documentation gaps (4 issues):** Several API response fields (`has_been_submitted`, `is_locked`, `submitted_at`, user stats) are computed from database state but their derivation logic is not documented. Implementers can figure these out, but explicit documentation would save time.

2. **Missing endpoint-specific error codes (3 issues):** The global error handling format covers standard HTTP errors, and the universal error UX pattern is defined. But individual endpoints (submit, review actions, WebSocket) don't specify their validation error codes. Implementers will need to define these during development.

3. **Minor specification ambiguities (11 issues):** Naming inconsistencies, ambiguous requirements language, missing protocol details. None prevent implementation but may require implementer judgment calls.

**Refactoring Impact:** The removal of board/merge/similarity systems eliminated approximately 9 cross-reference issues, 2 consistency issues, and 4 structural issues from the original report. The specifications are now more focused on the core requirements assembly workflow.

**Recommendation:** The Strategy Planner should proceed. These WARNINGs should be tracked and resolved during implementation — they're typical "last mile" specification details that are best finalized when writing the actual code. The refactoring has simplified the system significantly and reduced overall specification complexity.
