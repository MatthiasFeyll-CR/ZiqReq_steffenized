# Milestone 5: Board Interactions & Undo

## Overview
- **Execution order:** 5 (runs after M4)
- **Estimated stories:** 8
- **Dependencies:** M4
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-3.2 | Board Interactions (advanced: drag, nesting, lock, multi-select) | P1 | features.md FA-3 |
| F-3.4 | AI Modification Indicators | P1 | features.md FA-3 |
| F-3.7 | Undo/Redo | P1 | features.md FA-3 |
| F-3.8 | Board Item Reference Action | P1 | features.md FA-3 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| board_nodes | UPDATE (parent_id, position, is_locked, ai_modified_indicator) | parent_id, is_locked, ai_modified_indicator, created_by | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/board/nodes/:nodeId | PATCH | Update position, parent_id, is_locked | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| AIModifiedIndicator | Feature | component-specs.md S6.1 |
| UserSelectionHighlight | Feature | component-inventory.md |
| BoardToolbar (undo/redo) | Feature | component-specs.md S6.5 |

## Story Outline (Suggested Order)
1. **[Frontend]** Drag to move nodes — position persistence via REST PATCH on drag end
2. **[Frontend]** Group nesting — drag Boxes/Free Text into/out of Groups, parent_id update
3. **[Frontend]** Node lock toggle — per-node is_locked flag, lock icon, prevents editing when locked
4. **[Frontend]** Multi-select — Ctrl+drag for selection box, batch delete
5. **[Frontend]** Undo/redo system — Redux Toolkit action history stack, bounded to 100 entries
6. **[Frontend]** Context-aware undo labels — "Undo AI Action" / "Redo AI Action" for AI-sourced entries
7. **[Frontend]** Board item reference action — Pin button on nodes, inserts [[Title]] reference into chat input
8. **[Frontend]** AI modification indicators — gold dot with pulse animation, AI badge on created_by='ai' nodes, clear on user selection

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Drag to move | ~4,000 | React Flow docs, api-design.md | 2-3 files | Low | — |
| 2 | Group nesting | ~5,000 | component-specs.md (S6.2), data-model.md (parent_id) | 3-4 files | High | Complex drag-in/out detection |
| 3 | Node lock | ~2,000 | features.md (F-3.2) | 2-3 files | Low | — |
| 4 | Multi-select | ~3,000 | features.md (F-3.2) | 2-3 files | Medium | Selection box geometry |
| 5 | Undo/redo | ~6,000 | tech-stack.md (Board Undo/Redo), component-specs.md | 4-6 files | High | Redux middleware, REST sync |
| 6 | Context-aware labels | ~2,000 | features.md (F-3.7) | 1-2 files | Low | — |
| 7 | Board item reference | ~3,000 | features.md (F-3.8), component-specs.md (S6.1) | 2-3 files | Medium | Cross-panel communication |
| 8 | AI indicators | ~4,000 | component-specs.md (S6.1), features.md (F-3.4) | 3-4 files | Medium | Animation, clear on interaction |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~29,000
- **Cumulative domain size:** Medium (board interactions + undo state)
- **Information loss risk:** Low (3)
- **Context saturation risk:** Low
- **Heavy stories:** 2 (group nesting, undo/redo)

## Milestone Acceptance Criteria
- [ ] Nodes can be dragged to new positions, positions persist
- [ ] Boxes/Free Text can be dragged into/out of Groups
- [ ] Lock toggle prevents editing of locked nodes
- [ ] Ctrl+drag creates selection box for multi-select
- [ ] Undo/redo works for all board actions (node CRUD, content, connections, position)
- [ ] Undo button shows "Undo AI Action" for AI-sourced entries
- [ ] Pin button on nodes inserts [[Title]] reference into chat input
- [ ] AI-created nodes show robot badge
- [ ] AI-modified nodes show gold pulsing dot, cleared on user selection
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M4

## Notes
- AI-sourced undo entries are prepared but no AI creates board items until M8 (Board Agent). The undo system tags entries with source='user' for now.
- User selection highlights (colored borders with names) require WebSocket presence from M6. Placeholder styling prepared here.
