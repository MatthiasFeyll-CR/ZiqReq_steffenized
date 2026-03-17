# Milestone 20 Spec Reconciliation

## Summary
- **Milestone:** M20 — AI System Prompt Rework (ai-rework)
- **Date:** 2026-03-17
- **Total deviations found:** 2
- **Auto-applied (SMALL TECHNICAL):** 0
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 1
- **Informational only:** 1

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

No SMALL TECHNICAL deviations found. All file paths, parameter names, and minor technical details matched the spec.

### FEATURE DESIGN (Flagged)

No FEATURE DESIGN deviations found. All user-visible behavior, UI changes, and feature scope matched the PRD.

### LARGE TECHNICAL (Flagged) ⚠️

| # | Deviation | Document Updated | Change | Rationale |
|---|-----------|-----------------|--------|-----------|
| 1 | **DEV-001: gRPC servicer uses CoreClient direct DB access** | `docs/02-architecture/api-design.md` | Added implementation note clarifying that proto definitions serve as API contracts/documentation, while runtime uses CoreClient direct PostgreSQL queries | All services share same PostgreSQL database. Direct DB access avoids unnecessary gRPC hop overhead, simplifies deployment, and is consistent with every other CoreClient operation in the codebase |

#### DEV-001 Detail

**Source:** QA report (`docs/08-qa/qa-m20-ai-rework.md` lines 106-112), Progress log (`.ralph/archive/m20-ai-rework/progress.txt` US-003 learnings lines 65-66)

**Stories affected:** US-003 (AI pipeline update for requirements structure mutations)

**What the spec said:**
The spec in `docs/02-architecture/api-design.md` defined `UpdateRequirementsStructure` and `GetRequirementsState` as gRPC RPCs in the CoreService, implying a traditional gRPC server implementation pattern where the AI service would make gRPC calls to the Core service to persist/retrieve requirements mutations.

**What was actually implemented:**
- Proto definitions exist in `proto/core.proto` as API contract documentation
- `CoreClient` class (`services/ai/grpc_clients/core_client.py`) implements these operations via direct PostgreSQL queries
- No actual gRPC server handles these calls at runtime
- The Core gRPC servicer exists as a stub

**Why this pattern is correct:**
1. All services (Gateway, AI, Core) share the same PostgreSQL database
2. Direct DB access eliminates unnecessary gRPC serialization/deserialization overhead
3. Simplifies deployment and reduces inter-service latency
4. Consistent with all other CoreClient operations in the codebase (per progress log: "CoreServicer is a dead stub — all services use direct DB access via CoreClient")
5. Proto files still serve their purpose as API contract documentation

**Spec update applied:**
Added an implementation note after the CoreService proto definitions (line 1772 in `api-design.md`) clarifying:
- Proto definitions are API contracts and documentation
- Runtime uses CoreClient direct PostgreSQL queries
- Pattern is consistent across all CoreClient operations
- Core gRPC servicer is primarily a stub

**Impact assessment:**
- **No functional change** — the implementation works correctly and passes all tests
- **No breaking changes** — this is an implementation detail, not a contract change
- **Architecture pattern clarification** — documents the actual microservice data access pattern used throughout ZiqReq

---

## Informational Only

| # | Deviation | Reason |
|---|-----------|--------|
| 1 | **DEV-002: Board references already absent** | Board references were already removed in earlier milestones (M17/M18). M20 PRD acceptance criteria about board removal were written before those milestones completed. Code is correct; no spec update needed. |

---

## Documents Modified

1. **docs/02-architecture/api-design.md**
   - Section: Core Service gRPC — PersistAiOutput
   - Change: Added implementation note clarifying proto definitions serve as contracts while runtime uses CoreClient direct DB access
   - Lines affected: Added note after line 1772

---

## Impact on Future Milestones

**No impact on future milestone implementations.**

**Rationale:**
- DEV-001 is an implementation pattern clarification, not a functional change
- The proto files continue to document the API contract correctly
- Future milestones that need Core service data access should continue using CoreClient direct queries (consistent with existing pattern)
- No architectural changes required in future work

**Affected milestones:** None

**Recommendations for future work:**
- When adding new Core data access operations, continue the CoreClient direct DB pattern
- Update proto files to document new operations as API contracts
- Add similar implementation notes if the pattern could be ambiguous to future implementers

---

## Deviation Analysis

### Root Cause: Architectural Pattern Not Explicitly Documented

**Why this deviation occurred:**
The spec accurately described the proto definitions and the data that needed to be accessed, but did not explicitly state the runtime implementation pattern (gRPC server vs direct DB access). Ralph made the pragmatic architectural decision to use direct database access based on the existing codebase pattern, which was correct but created a documentation gap.

**Prevention for future milestones:**
The Architecture document should include a general section on "Data Access Patterns" that explicitly states:
- When to use gRPC calls between services
- When to use direct database access
- Which services own which tables
- When proto definitions serve as documentation vs runtime contracts

This would prevent similar ambiguities in future PRDs.

**Action items:** None required. The clarification has been added to the spec.

---

## Verification

**Tests passed:** 712 Python tests, 365 Node tests (all green)

**Gate checks passed:**
- Docker build: PASSED
- Frontend typecheck: PASSED
- Backend lint (Ruff): PASSED
- Backend typecheck (mypy): PASSED

**QA verdict:** PASS (0 defects found)

**Spec alignment:** All functional behavior matches spec. One architectural implementation pattern clarified.

---

## Sign-off

- **Reconciled by:** Spec Reconciler (Claude Agent)
- **Reviewed by:** Pending human review
- **Date:** 2026-03-17
- **Milestone status:** Complete, all specs updated to match implementation
