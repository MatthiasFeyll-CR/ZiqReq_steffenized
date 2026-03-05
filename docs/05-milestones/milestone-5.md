# Milestone 5: Digital Board

## Overview
- **Wave:** 2
- **Estimated stories:** 9
- **Must complete before starting:** M1, M2
- **Can run parallel with:** M4
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-3 | Digital Board (all: node types, interactions, sync, undo/redo) | P1 | F-3.1–F-3.8 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| board_nodes | CRUD | id, idea_id, node_type, title, body, position_x/y, width/height, parent_id, is_locked, created_by, ai_modified_indicator | data-model.md |
| board_connections | CRUD | id, idea_id, source_node_id, target_node_id, label | data-model.md |
| ideas | READ | id, state (for locking check) | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| GET /api/ideas/:id/board/nodes | GET | List all board nodes | User | api-design.md |
| POST /api/ideas/:id/board/nodes | POST | Create board node | User/AI | api-design.md |
| PATCH /api/ideas/:id/board/nodes/:nodeId | PATCH | Update node (content, position, parent, lock) | User/AI | api-design.md |
| DELETE /api/ideas/:id/board/nodes/:nodeId | DELETE | Delete node | User/AI | api-design.md |
| GET /api/ideas/:id/board/connections | GET | List all connections | User | api-design.md |
| POST /api/ideas/:id/board/connections | POST | Create connection | User/AI | api-design.md |
| PATCH /api/ideas/:id/board/connections/:connId | PATCH | Update connection label | User/AI | api-design.md |
| DELETE /api/ideas/:id/board/connections/:connId | DELETE | Delete connection | User/AI | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| BoardCanvas | Feature | component-inventory.md |
| BoxNode | Feature | component-inventory.md |
| GroupNode | Feature | component-inventory.md |
| FreeTextNode | Feature | component-inventory.md |
| ConnectionEdge | Feature | component-inventory.md |
| BoardToolbar | Feature | component-inventory.md |
| BoardMinimap | Feature | component-inventory.md |
| BoardZoomControls | Feature | component-inventory.md |
| AIModifiedIndicator | Feature | component-inventory.md |
| UserSelectionHighlight | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API] Board nodes REST API** — CRUD endpoints for board_nodes. POST: create node with type (box/group/free_text), title, body, position, parent_id. PATCH: update any field (title, body, position_x/y, width/height, parent_id, is_locked, ai_modified_indicator). DELETE: remove node (ON DELETE SET NULL for children). Permission check: idea access + idea not locked per state. Serializer includes nested children for groups.
2. **[API] Board connections REST API** — CRUD endpoints for board_connections. POST: create with source_node_id, target_node_id, optional label. PATCH: update label. DELETE: remove connection. Validation: source and target must belong to same idea. UNIQUE constraint on (source_node_id, target_node_id).
3. **[Frontend] React Flow canvas integration** — BoardCanvas component using React Flow library. Replace M2 Board tab placeholder. Dot grid background. Pan and zoom with mouse/trackpad. Load all nodes and connections from API on mount. React Flow node types registered for box, group, free_text. React Flow edge type registered for connections.
4. **[Frontend] Custom node types** — BoxNode: solid background, visually distinct title (bold) + bullet-point body, pin/lock icon (top-left), AI badge (robot icon, shown when created_by='ai'), lock icon overlay when is_locked=true. Double-click to edit content (inline editing). GroupNode: dashed border, optional label/title badge, resizable handles, children move with group. Drag nodes into/out of groups (reparenting via drop zone detection). Nested groups supported. FreeTextNode: transparent background, no border, click-to-edit.
5. **[Frontend] Connection edges** — ConnectionEdge: smooth step edge style, arrow marker on target end. Double-click on edge to add/edit sticky text label. Label rendered as floating text on edge. Support connections between any node types.
6. **[Frontend] Board toolbar + minimap + zoom** — BoardToolbar: Add Box button (creates at center of viewport), Delete Selected button, Fit View button, Undo button, Redo button. Undo/Redo buttons show context-aware labels ("Undo AI Action" / "Redo AI Action" when applicable). BoardMinimap: React Flow MiniMap component (bottom-right). BoardZoomControls: +/- buttons + Fit View (bottom-left). Ctrl+drag for multi-select.
7. **[WebSocket+API] Drag/move/resize + hybrid sync** — Awareness events (node selection) sent via WebSocket immediately (ephemeral, not persisted). Content changes (create/update/delete): REST mutation → success → WebSocket broadcast to all subscribers. Position/resize changes: REST PATCH on drag-end/resize-end → WebSocket broadcast. Last-write-wins for concurrent edits on same node (server timestamp). Optimistic update on client side.
8. **[Frontend+API] Node locking + AI modification indicators** — Lock toggle per node: click lock icon → PATCH is_locked=true/false. Locked nodes cannot be edited (UI enforces, API validates). AIModifiedIndicator: gold dot with pulse animation on nodes where ai_modified_indicator=true. Indicator cleared when user selects the node (PATCH ai_modified_indicator=false on selection). Robot badge on nodes where created_by='ai'.
9. **[Frontend] Undo/redo Redux slice** — Redux Toolkit slice for board undo/redo history. Action history stack (max 100 entries). Each entry: { action_type, node/connection data before change, node/connection data after change, source: 'user' | 'ai' }. Undo: pop stack, restore previous state locally, send REST mutation to persist reverted state, WebSocket broadcasts change. Redo: push back to stack if not branched. Context-aware button labels derived from top-of-stack source field. Cross-user: undo/redo is local to each session (not shared). Board item reference action button (top-right corner of nodes): click copies formatted reference text for pasting in chat.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Workspace page shell | Available | M2 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/features/board/`
- `services/gateway/apps/board/`
- `services/core/apps/board/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/pages/IdeaWorkspace/` (replace Board tab placeholder with real canvas)
- `frontend/src/store/` (add board undo/redo slice)
- `services/gateway/apps/websocket/consumers.py` (add board event broadcasting)
- `proto/core.proto` (add PersistBoardUpdate if not already stubbed)

## Milestone Acceptance Criteria
- [ ] Board nodes CRUD API works for all 3 types (box, group, free_text)
- [ ] Board connections CRUD API works with validation
- [ ] React Flow canvas renders nodes and connections from API data
- [ ] BoxNode, GroupNode, FreeTextNode render per design specs
- [ ] Double-click to edit content works for all node types
- [ ] Drag nodes into/out of groups (reparenting) works
- [ ] Nested groups supported
- [ ] Connection edges render with labels, double-click to edit label
- [ ] Toolbar buttons functional (Add, Delete, Fit View, Undo, Redo)
- [ ] Minimap and zoom controls work
- [ ] Hybrid sync: awareness via WebSocket, mutations via REST then broadcast
- [ ] Node locking prevents editing (UI + API validation)
- [ ] AI modification indicator renders and clears on user selection
- [ ] Undo/redo works with correct action labels
- [ ] Board item reference action copies reference text
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1, M2

## Notes
- **Stub: AI-created board nodes** — API supports `created_by='ai'` on POST. No AI agent creates nodes yet. In M6, the Board Agent calls create_node/update_node/etc. via gRPC → REST. For testing, create AI nodes via API with created_by='ai'.
- **Stub: UserSelectionHighlight for multi-user** — Component exists and renders for the current user's selection. Multi-user selection broadcasting (showing other users' selections with their name/color) is wired in M8 when presence tracking exists.
- **Stub: Board item reference in chat** — Reference action button copies a formatted text string (e.g., `[Board: Node Title]`). Pasting in chat creates a plain text reference. Clickable link behavior (navigate to Board tab + highlight node) implemented in M12.
- **Stub: Notification for board changes** — No notifications dispatched for board operations. Board changes are real-time via WebSocket only.
