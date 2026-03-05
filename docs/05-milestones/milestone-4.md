# Milestone 4: Digital Board

## Overview
- **Execution order:** 4 (runs after M3)
- **Estimated stories:** 9
- **Dependencies:** M3
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-3.1 | Node Types (Box, Group, Free Text) | Must-have | features.md |
| F-3.2 | Board Interactions | Must-have | features.md |
| F-3.3 | Board UI (MiniMap, zoom, toolbar) | Must-have | features.md |
| F-3.4 | AI Modification Indicators | Must-have | features.md |
| F-3.5 | Multi-User Board Editing | Must-have | features.md |
| F-3.6 | Board Sync (hybrid model) | Must-have | features.md |
| F-3.7 | Undo/Redo | Must-have | features.md |
| F-3.8 | Board Item Reference Action | Must-have | features.md |
| — | Board read-only on mobile | Must-have | nonfunctional.md §Compatibility |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| board_nodes | CREATE, READ, UPDATE, DELETE | id, idea_id, node_type, title, body, position_x/y, width/height, parent_id, is_locked, created_by, ai_modified_indicator | data-model.md |
| board_connections | CREATE, READ, UPDATE, DELETE | id, idea_id, source_node_id, target_node_id, label | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/board/nodes | GET | Get all board nodes for idea | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/nodes | POST | Create board node | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/nodes/:nid | PATCH | Update node (content, position, size, parent, lock) | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/nodes/:nid | DELETE | Delete board node | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/connections | GET | Get all connections for idea | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/connections | POST | Create connection | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/connections/:cid | PATCH | Update connection label | Bearer/bypass | api-design.md |
| /api/ideas/:id/board/connections/:cid | DELETE | Delete connection | Bearer/bypass | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| BoardPanel (Board tab content) | Component | page-layouts.md §4 |
| BoxNode (custom React Flow node) | Component | component-specs.md |
| GroupNode (custom React Flow node) | Component | component-specs.md |
| FreeTextNode (custom React Flow node) | Component | component-specs.md |
| BoardConnection (custom React Flow edge) | Component | component-specs.md |
| MiniMap | Component (React Flow) | component-specs.md |
| ZoomControls | Component | component-specs.md |
| BoardToolbar | Component | component-specs.md |
| UndoRedoButtons | Component | component-specs.md |
| SelectionHighlight | Component | component-specs.md |
| AIBadge | Component | component-specs.md |
| ReferenceButton | Component | component-specs.md |
| NodeLockToggle | Component | component-specs.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| Redux slice: board undo/redo history | New | M4 |
| Board state management (TanStack Query + WebSocket invalidation) | New | M4 |

## Story Outline (Suggested Order)

1. **[Backend] Board node CRUD APIs** — Gateway REST endpoints for board nodes: GET all, POST create, PATCH update (content, position, size, parent, lock), DELETE. Core gRPC servicers: CreateBoardNode, UpdateBoardNode, DeleteBoardNode, GetBoardState. Validation: node_type constraints, parent_id must be group type. Publish board.node.* events on mutations.
2. **[Backend] Board connection CRUD APIs + board WebSocket broadcast** — Gateway REST endpoints for connections: GET all, POST create, PATCH update label, DELETE. Validation: source/target must exist, no duplicate connections. WebSocket broadcast: content/position changes broadcast after REST persist. Awareness events (selections, lock state) via WebSocket only (no persistence).
3. **[Frontend] React Flow canvas setup** — React Flow integration in Board tab. Canvas with background grid. MiniMap component. Zoom controls (in/out, fit view). Canvas pan and zoom.
4. **[Frontend] Box nodes** — Custom React Flow node for Boxes. Solid background, visually distinct title + bullet-point body. Double-click to edit content. Created_by indicator (AI robot badge). AI modification indicator (fades on user selection).
5. **[Frontend] Group nodes + Free Text nodes** — Group: container with optional label, resizable, children move with group. Drag Boxes/Free Text into/out of Groups dynamically. Nesting support. Free Text: text on canvas with no card/border/background. Double-click to edit.
6. **[Frontend] Connections + toolbar** — Connection lines between any node types. Double-click connections to add/edit sticky text labels. Toolbar: Add Box, Delete Selected, Fit View, Undo, Redo. Ctrl+drag for multi-select.
7. **[Frontend] Board sync (hybrid model)** — Awareness events (selections with username highlight, lock state) via WebSocket — instant, no persistence. Content changes via REST POST/PATCH → server persist → WebSocket broadcast to other users. Position/resize via REST on release (drag end, resize end). TanStack Query cache invalidation on WebSocket board events.
8. **[Frontend] Undo/Redo** — Redux Toolkit slice for undo/redo action history stack. Tracks all board actions: node CRUD, content edits, connections, group changes, position/resize. Source tagging per action (user/ai). Context-aware button labels: "Undo AI Action" / "Redo AI Action" vs "Undo" / "Redo". Stack bounded to 100 entries. Undo pops stack → REST mutation to persist reverted state → WebSocket broadcast.
9. **[Frontend] Node lock + board item reference + mobile read-only** — Lock toggle per node (prevents editing). Lock state broadcast via WebSocket. Board item reference button (top-right corner of each node): click inserts formatted reference into chat input for explicit board references in messages. Mobile viewport detection: board renders in read-only mode on mobile devices (no create/edit/delete/drag) — all other features functional. Tablet: full functionality.

## Milestone Acceptance Criteria
- [ ] React Flow canvas renders with minimap, zoom controls, background grid
- [ ] Box nodes: create, edit title/body, delete work correctly
- [ ] Group nodes: create, label, resize, nesting, drag children in/out
- [ ] Free Text nodes: create, edit, delete on canvas
- [ ] Connections: create between any node types, edit labels, delete
- [ ] Multi-user: selection highlights show other users' selections with names
- [ ] Board sync: awareness events instant via WS, content persists via REST then broadcasts
- [ ] Undo/redo: full action history, context-aware labels, bounded stack
- [ ] Node lock toggle prevents editing, broadcasts lock state
- [ ] Board item reference button inserts reference into chat input
- [ ] AI modification indicator renders (clears on selection) — AI content tested in M5
- [ ] Toolbar (Add Box, Delete Selected, Fit View, Undo, Redo) works
- [ ] Board is read-only on mobile viewports (no editing, viewing works)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M3

## Notes
- AI-created board nodes won't appear until M5 (AI Facilitation). The `created_by: 'ai'` and `ai_modified_indicator` fields are implemented but only triggered by AI in M5.
- Board is read-only when idea state is in_review/accepted/dropped (section locking from M3). Editing works in open/rejected states.
- Last-write-wins conflict resolution: server timestamp determines ordering. Selection highlighting reduces conflicts in practice.
- Board undo/redo history is frontend-only (Redux store). Not persisted to backend. Each user has their own independent undo stack.
