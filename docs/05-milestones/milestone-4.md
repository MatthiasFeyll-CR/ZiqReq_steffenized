# Milestone 4: Digital Board — Core

## Overview
- **Execution order:** 4 (runs after M3)
- **Estimated stories:** 9
- **Dependencies:** M3
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-3.1 | Node Types (Box, Group, Free Text) | P1 | features.md FA-3 |
| F-3.2 | Board Interactions (partial: basic editing, connections) | P1 | features.md FA-3 |
| F-3.3 | Board UI (minimap, zoom, grid, toolbar) | P1 | features.md FA-3 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| board_nodes | INSERT, SELECT, UPDATE, DELETE | id, idea_id, node_type, title, body, position_x/y, width, height, parent_id | data-model.md |
| board_connections | INSERT, SELECT, UPDATE, DELETE | id, idea_id, source_node_id, target_node_id, label | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/board/nodes | GET | List all board nodes | Bearer | api-design.md |
| /api/ideas/:id/board/nodes | POST | Create board node | Bearer | api-design.md |
| /api/ideas/:id/board/nodes/:nodeId | PATCH | Update node (content, position) | Bearer | api-design.md |
| /api/ideas/:id/board/nodes/:nodeId | DELETE | Delete node | Bearer | api-design.md |
| /api/ideas/:id/board/connections | GET | List all connections | Bearer | api-design.md |
| /api/ideas/:id/board/connections | POST | Create connection | Bearer | api-design.md |
| /api/ideas/:id/board/connections/:connId | PATCH | Update connection label | Bearer | api-design.md |
| /api/ideas/:id/board/connections/:connId | DELETE | Delete connection | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| BoardCanvas | Feature | component-specs.md S6.6 |
| BoxNode | Feature | component-specs.md S6.1 |
| GroupNode | Feature | component-specs.md S6.2 |
| FreeTextNode | Feature | component-specs.md S6.3 |
| ConnectionEdge | Feature | component-specs.md S6.4 |
| BoardToolbar | Feature | component-specs.md S6.5 |
| BoardMinimap | Feature | component-specs.md S6.6 |
| BoardZoomControls | Feature | component-specs.md S6.6 |

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Built | M1 |
| Workspace layout | Built | M3 |

## Story Outline (Suggested Order)
1. **[API]** Board nodes REST API — CRUD with validation (node_type rules, parent_id must be group)
2. **[API]** Board connections REST API — CRUD with validation (no self-connections, no duplicates)
3. **[Frontend — Canvas]** React Flow canvas setup — background grid, zoom, pan, viewport management
4. **[Frontend — Component]** BoxNode — title bar + bullet body, min/max width, border, shadow
5. **[Frontend — Component]** GroupNode — dashed container, label badge, resizable, children move with parent
6. **[Frontend — Component]** FreeTextNode — transparent background, click-to-edit, textarea overlay
7. **[Frontend — Component]** ConnectionEdge — smooth step type, arrowhead, hover state, double-click label editing
8. **[Frontend — Component]** BoardToolbar — Add Box (creates at viewport center), Delete Selected, Fit View
9. **[Frontend — Component]** Minimap + zoom controls — bottom-right minimap, bottom-left +/-/fit buttons

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Board nodes API | ~6,000 | api-design.md (board), data-model.md (board_nodes) | 5-7 files | Medium | Self-referential parent_id |
| 2 | Board connections API | ~4,000 | api-design.md (connections), data-model.md | 3-5 files | Low | — |
| 3 | React Flow canvas | ~6,000 | component-specs.md (S6.6), react-flow docs | 3-4 files | Medium | React Flow configuration |
| 4 | BoxNode | ~5,000 | component-specs.md (S6.1) | 2-3 files | Medium | Custom React Flow node |
| 5 | GroupNode | ~6,000 | component-specs.md (S6.2) | 2-3 files | High | Resize handles, child containment |
| 6 | FreeTextNode | ~3,000 | component-specs.md (S6.3) | 1-2 files | Low | — |
| 7 | ConnectionEdge | ~4,000 | component-specs.md (S6.4) | 2-3 files | Medium | Custom edge with label editing |
| 8 | BoardToolbar | ~3,000 | component-specs.md (S6.5) | 1-2 files | Low | — |
| 9 | Minimap + zoom | ~2,000 | component-specs.md (S6.6) | 1-2 files | Low | React Flow built-in |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~39,000
- **Cumulative domain size:** Medium (board nodes + connections + React Flow)
- **Information loss risk:** Low (2)
- **Context saturation risk:** Low
- **Heavy stories:** 1 (GroupNode — resize + child containment is complex)

## Milestone Acceptance Criteria
- [ ] Board tab in workspace renders React Flow canvas with background grid
- [ ] Box nodes display with title bar and bullet-point body
- [ ] Group nodes display as dashed containers with label, resizable
- [ ] Free text nodes display as transparent click-to-edit text
- [ ] Connections render as smooth-step edges with arrowhead and optional labels
- [ ] Double-click on connection opens label editor
- [ ] Toolbar: Add Box creates new box at viewport center
- [ ] Toolbar: Delete Selected removes selected nodes/edges
- [ ] Toolbar: Fit View zooms to fit all content
- [ ] Minimap shows board overview
- [ ] Zoom controls work (+, -, fit)
- [ ] All board changes persist to backend via REST
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M3

## Notes
- Board sync (real-time broadcasting) comes in M6. For now, board changes persist via REST and display locally.
- Group nesting (drag in/out) and undo/redo come in M5.
- Node lock toggle comes in M5.
- AI-related board features (AI badge, AI modification indicators) come in M5.
