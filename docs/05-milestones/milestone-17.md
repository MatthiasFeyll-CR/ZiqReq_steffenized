# Milestone 17: Remove Features (Clean Slate)

## Overview
- **Execution order:** 17 (runs after M16)
- **Estimated stories:** 4
- **Dependencies:** M16
- **MVP:** Yes

## Purpose
Completely remove deprecated features — merge/similarity/keyword system and the Board (XYFlow canvas) — from both backend and frontend. This creates a clean codebase for the subsequent rename and new feature additions.

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| R-1.1 | Remove merge/similarity/keyword — Backend | Critical | REFACTORING_PLAN.md Phase 1 |
| R-1.2 | Remove merge/similarity/keyword — Frontend | Critical | REFACTORING_PLAN.md Phase 1 |
| R-1.3 | Remove Board (XYFlow) — Backend | Critical | REFACTORING_PLAN.md Phase 1 |
| R-1.4 | Remove Board (XYFlow) — Frontend | Critical | REFACTORING_PLAN.md Phase 1 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| idea_keywords | DROP TABLE | — | Story 1.1 |
| merge_requests | DROP TABLE | — | Story 1.1 |
| idea_embeddings | DROP TABLE | — | Story 1.1 |
| ideas | DROP COLUMNS | merged_from_idea_1_id, merged_from_idea_2_id, closed_by_merge_id, closed_by_append_id, co_owner_id | Story 1.1 |
| board_nodes | DROP TABLE | — | Story 1.3 |
| board_connections | DROP TABLE | — | Story 1.3 |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/similar | GET | REMOVE | — | Story 1.1 |
| /api/ideas/:id/merge-request | POST | REMOVE | — | Story 1.1 |
| /api/merge-request/:id/consent | POST | REMOVE | — | Story 1.1 |
| /api/ideas/:id/board/* | ALL | REMOVE | — | Story 1.3 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| MergeRequestBanner | REMOVE | Story 1.2 |
| MergedIdeaBanner | REMOVE | Story 1.2 |
| AppendedIdeaBanner | REMOVE | Story 1.2 |
| ManualMergeModal | REMOVE | Story 1.2 |
| Board canvas components | REMOVE | Story 1.4 |
| Board node components | REMOVE | Story 1.4 |
| Board toolbar/controls | REMOVE | Story 1.4 |

## Story Outline (Suggested Order)
1. **[Backend] Remove merge/similarity/keyword system** — Delete directories (similarity, keyword_agent, deep_comparison, merge_synthesizer), remove merge/similarity references from models, views, serializers, URLs, settings, events, proto. Create migration to drop tables and columns. Remove `research_similar_ideas` tool from Facilitator.
2. **[Frontend] Remove merge/similarity/keyword UI** — Delete MergeRequestBanner, MergedIdeaBanner, AppendedIdeaBanner, ManualMergeModal, similarity API. Remove merge/append logic from workspace, hooks, notifications, translations.
3. **[Backend] Remove Board (XYFlow)** — Delete board app directories (core, gateway, AI agent). Remove board references from WebSocket consumers, facilitator prompt/plugins, AI pipeline, summarizing AI prompt, proto files. Create migration to drop board tables.
4. **[Frontend] Remove Board (XYFlow) UI** — Delete all board components, hooks, API files. Update WorkspaceLayout to render chat only (full width). Remove board WebSocket handlers, Redux slices, translations. Remove @xyflow/react dependency.

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Remove merge/similarity backend | ~12,000 | Architecture, data model | ~25 files (mostly deletions) | High | Medium — wide blast radius but purely deletions |
| 2 | Remove merge/similarity frontend | ~8,000 | Component specs | ~12 files | Medium | Low — isolated deletions |
| 3 | Remove board backend | ~10,000 | Architecture, AI specs | ~20 files (mostly deletions) | High | Medium — touches AI pipeline |
| 4 | Remove board frontend | ~6,000 | Component specs | ~10 files | Medium | Low — isolated deletions |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~36,000
- **Cumulative domain size:** Medium (mostly deletions, low new knowledge)
- **Information loss risk:** Low (score: 2)
- **Context saturation risk:** Low

## Milestone Acceptance Criteria
- [ ] All merge/similarity/keyword backend code removed, services start without errors
- [ ] All merge/similarity/keyword frontend code removed
- [ ] All board backend code removed, services start without errors
- [ ] All board frontend code removed, @xyflow/react dependency removed
- [ ] WorkspaceLayout renders chat-only (full width)
- [ ] Database migrations drop all deprecated tables/columns
- [ ] grep verification passes for all removed feature keywords
- [ ] TypeScript typecheck passes
- [ ] Frontend builds without errors
- [ ] No regressions on previous milestones

## Notes
- Stories 1+2 (merge removal) and 3+4 (board removal) are paired backend/frontend. Execute in order.
- Story 1 has the widest blast radius — touches core, gateway, AI, notification services and proto files.
- Story 3 touches the AI pipeline significantly — removing board state assembly and board agent invocation.
- After this milestone, the workspace will show chat only (no right panel). The structured requirements panel comes in M19.
