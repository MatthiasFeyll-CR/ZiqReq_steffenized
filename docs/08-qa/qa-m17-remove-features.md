# QA Report: Milestone 17 — Remove Features (Clean Slate)

**Date:** 2026-03-16
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1
**PRD:** tasks/prd-m17.json
**Progress:** .ralph/progress.txt

---

## Summary

Re-reviewed M17 after bugfix cycle 1 (BF-001: fix 9 ruff lint errors introduced by M17). All 4 original user stories pass acceptance criteria — merge/similarity/keyword system and Board/XYFlow are fully removed from both backend and frontend. The BF-001 bugfix successfully resolved all 9 M17-introduced ruff lint errors. The REQUIRED ruff gate check now shows only 2 pre-existing E501 errors (not introduced by M17). All gate checks pass. **Verdict: PASS.**

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | [Backend] Remove merge/similarity/keyword system | PASS | All directories deleted, migration correct, grep clean, no remaining references |
| US-002 | [Frontend] Remove merge/similarity/keyword UI | PASS | All components deleted, workspace simplified, translations cleaned, grep clean |
| US-003 | [Backend] Remove Board (XYFlow) | PASS | All directories deleted, migration correct, proto clean, AI prompts clean |
| US-004 | [Frontend] Remove Board (XYFlow) UI | PASS | Board components deleted, WorkspaceLayout chat-only, @xyflow removed, grep clean |
| BF-001 | Fix: Ruff lint errors introduced by M17 | PASS | All 9 M17-introduced ruff errors fixed; only 2 pre-existing E501 remain |

**Stories passed:** 5 / 5
**Stories with defects:** 0
**Stories with deviations:** 0

### BF-001 Acceptance Criteria Verification

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Remove unused import `Q` from comments/views.py | PASS | `Q` no longer imported |
| 2 | Fix unused variable `idea` in ideas/views.py:356 | PASS | Assignment removed; now `Idea.objects.get(id=idea_id)` directly |
| 3 | Sort imports in ai/grpc_server/server.py | PASS | ruff I001 resolved |
| 4 | Sort imports in ai/grpc_server/servicers/processing_servicer.py | PASS | ruff I001 resolved |
| 5 | Sort imports in gateway/apps/chat/views.py | PASS | ruff I001 resolved |
| 6 | Sort imports in gateway/grpc_clients/ai_client.py | PASS | ruff I001 resolved |
| 7 | Sort imports in gateway/grpc_clients/core_client.py | PASS | ruff I001 resolved |
| 8 | Fix line too long in gateway/apps/collaboration/views.py:204 | PASS | ruff E501 resolved |
| 9 | Fix line too long in gateway/grpc_clients/core_client.py:229 | PASS | ruff E501 resolved |
| 10 | ruff check services/ — no NEW errors vs pre-M17 baseline | PASS | 2 errors remain, both pre-existing (admin_config migration, notification sender) |
| 11 | Typecheck passes | PASS | `npx tsc --noEmit` clean |

---

## Test Matrix Coverage

**No test matrix IDs were specified for this milestone.** M17 is a pure removal milestone with no test-matrix entries. This is consistent with the test architecture.

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| — | — | — | No test IDs defined for M17 |

---

## Gate Check Results

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Docker build | `docker compose build` | SKIPPED | Condition not met |
| Frontend typecheck | `cd frontend && npx tsc --noEmit` | **PASS** | Clean |
| Backend lint (Ruff) | `ruff check services/` | **PASS** | 2 errors — both pre-existing (not M17-introduced) |
| Backend typecheck (mypy) | `mypy services/` | FAIL (optional) | Pre-existing duplicate module error |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | 10 problems: all pre-existing (0 M17-introduced) |

### Ruff Error Analysis

| Error | File | M17-Introduced? | Status |
|-------|------|-----------------|--------|
| E501 | `services/core/apps/ideas/migrations/0001_create_admin_parameters_table.py:66` | No (M1) | Pre-existing |
| E501 | `services/notification/mailer/sender.py:37` | No (pre-M17) | Pre-existing |

All 9 M17-introduced ruff errors from cycle 0 have been resolved by BF-001.

---

## Defects

None. DEF-001 from cycle 0 has been resolved by BF-001.

---

## Deviations

None found. All implementations match upstream specifications.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Ruff (backend lint) | `ruff check services/` | PASS | 2 pre-existing errors only |
| ESLint (frontend lint) | `cd frontend && npx eslint src/` | FAIL (pre-existing) | 4 errors, 6 warnings — all pre-existing, none from M17 |
| mypy | `mypy services/` | FAIL (pre-existing) | Duplicate module name — pre-existing |
| Build | Docker compose | SKIPPED | N/A |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

M17 is a removal milestone (10,105 deletions, 319 insertions). Reviewed for:
- **Injection:** Migrations use `DROP TABLE IF EXISTS` / `DROP COLUMN IF EXISTS` — parameterized, safe.
- **Broken Access Control:** Authorization checks correctly simplified from "owner or co_owner or collaborator" to "owner or collaborator" after co_owner removal.
- **Sensitive Data Exposure:** No secrets or API keys introduced.

No security concerns.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

M17 is purely removal — no new queries, components, or data flows introduced. The codebase is lighter after removing ~10,000 lines.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| WorkspaceLayout | `docs/03-design/page-layouts.md` | PASS | Correctly renders chat-only (full width) as specified for interim state before M19 |

No other design specs apply — M17 removes components, it does not add new UI.

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### Pages & Navigation
- [ ] IdeaWorkspace still loads correctly at `/workspace/:id`
- [ ] LandingPage still loads and displays idea list
- [ ] Admin panel still loads all tabs (AI Context, Monitoring, Parameters, Users)

### API Endpoints
- [ ] `GET /api/ideas/` still returns idea list without merge/similarity/board fields
- [ ] `POST /api/ideas/` still creates ideas successfully
- [ ] `GET /api/ideas/:id/context-window` still works (ideas/views.py:356 was modified)
- [ ] Collaboration endpoints still work with simplified "owner or collaborator" checks
- [ ] Review endpoints still work without co_owner references

### Data Integrity
- [ ] Migration 0002_remove_merge_similarity applied cleanly — merge_requests, idea_keywords, idea_embeddings tables dropped; co_owner_id, merged_from_idea_1_id, merged_from_idea_2_id, closed_by_merge_id, closed_by_append_id columns dropped
- [ ] Migration 0003_remove_board applied cleanly — board_nodes, board_connections tables dropped
- [ ] Remaining ideas table columns (title, description, owner, status, etc.) intact

### Features
- [ ] Chat-only workspace layout renders full width without board panel
- [ ] WebSocket connections still work for chat (board handlers removed)
- [ ] BRD generation still works without board state input
- [ ] AI facilitator still works without merge/similarity/board tools
- [ ] Notifications still work without merge/append types
- [ ] Email preferences panel shows correct preference groups (no Similarity group)
- [ ] Collaborator modal works without co_owner logic

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] `ruff check services/` has no more than 2 pre-existing E501 errors
- [ ] No new ESLint errors beyond the 10 pre-existing ones
- [ ] Frontend builds successfully
- [ ] @xyflow/react is NOT in frontend/package.json

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (DEF-001 from cycle 0 resolved by BF-001)
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1 (resolved)
