# Wave-Parallel Development Context

```
M1 → [M2 ‖ M3] → [M4 ‖ M5] → M6 → [M7 ‖ M8 ‖ M12] → [M9 ‖ M10] → M11
 W0       W1            W2       W3          W4                W5          W6
```

## Rules for PRDs of parallel milestones:

1. **Integration points must be explicit.** When a milestone creates something its sibling will plug into after merge, both PRDs must specify the exact interface identically.

2. **File ownership per parallel milestone.** Each PRD's Notes should list which directories/files the milestone owns.

3. **Shared file modifications.** When parallel milestones both modify a shared file, keep changes additive (appending) rather than restructuring.

4. **All DB migrations are created in M1.** No parallel milestone creates new tables or modifies schema. This eliminates migration conflicts entirely. Later milestones only write application logic against existing tables.

---

## Placeholder/Stub Pattern

- **UI placeholders:** render `<EmptyState>` with descriptive message (e.g., "BRD generation available after brainstorming")
- **API stubs:** endpoint exists, returns correct shape with empty/mock data, or returns 501 "Not Implemented"
- **AI stubs:** tool exists in plugin but returns "not yet available" string, no side effects
- **Celery task stubs:** registered with correct schedule, task body is `pass` (no-op)
- **gRPC stubs:** method exists in servicer, returns default/empty protobuf response
- **WebSocket stubs:** consumer handles message type but performs no broadcast
- **Notification stubs:** event fires toast-only on current client, no persistent notification or email

**Stub documentation rule:** Every stub MUST be documented in the milestone's Notes section with: what is stubbed, what the stub returns/renders, and which future milestone implements the real version. This allows QA to validate that stubs are correctly replaced.

---

## Wave 1: M2 (Landing + Workspace) ‖ M3 (Admin)

### File Ownership
| Directory/File | M2 | M3 |
|---------------|----|----|
| `frontend/src/pages/LandingPage/` | Owner | — |
| `frontend/src/pages/IdeaWorkspace/` | Owner | — |
| `frontend/src/features/ideas/` | Owner | — |
| `frontend/src/pages/AdminPanel/` | — | Owner |
| `frontend/src/features/admin/` | — | Owner |
| `services/gateway/apps/ideas/` | Owner | — |
| `services/gateway/apps/admin/` | — | Owner |
| `services/core/apps/ideas/` | Owner | — |
| `services/core/apps/admin/` | — | Owner |
| `frontend/src/router.tsx` | Additive (/, /idea/:id) | Additive (/admin) |
| `frontend/src/components/shared/IdeaCard/` | Owner (new) | — |
| `services/core/grpc_server/servicer.py` | Additive (GetIdeaContext) | — |
| `services/core/tasks.py` | Additive (soft_delete_cleanup) | Additive (monitoring_health_check) |

### Integration Points
- None directly — M2 and M3 are completely independent.
- Both add routes to `router.tsx` — keep additions in separate route group blocks.
- Both implement Celery task bodies in `tasks.py` — each implements their own registered task.

### Merge Order: M3 first, then M2
- M3 is more isolated. M2 introduces IdeaCard (shared component used later by Review page).

---

## Wave 2: M4 (Chat) ‖ M5 (Board)

### File Ownership
| Directory/File | M4 | M5 |
|---------------|----|----|
| `frontend/src/features/chat/` | Owner | — |
| `frontend/src/features/board/` | — | Owner |
| `services/gateway/apps/chat/` | Owner | — |
| `services/gateway/apps/board/` | — | Owner |
| `services/core/apps/chat/` | Owner | — |
| `services/core/apps/board/` | — | Owner |
| `frontend/src/pages/IdeaWorkspace/` | Additive (ChatPanel) | Additive (BoardCanvas) |
| `frontend/src/store/` | — | Additive (board undo/redo slice) |
| `services/gateway/apps/websocket/consumers.py` | Additive (chat events) | Additive (board events) |
| `proto/core.proto` | Additive (PersistChatMessage) | Additive (PersistBoardUpdate) |

### Integration Points
- Both modify `IdeaWorkspace` — M4 replaces ChatPanel placeholder (left panel), M5 replaces Board tab placeholder (right panel). These are different DOM subtrees, no conflict.
- Both add WebSocket event handlers to `consumers.py` — keep as separate handler methods, append to the event dispatch map.
- Both add gRPC implementations to Core servicer — additive, different methods.

### Merge Order: M4 first, then M5
- M4 is simpler (fewer components, no Redux slice). M5 adds React Flow + undo/redo Redux slice (more complex).

---

## Wave 4: M7 (BRD) ‖ M8 (Collaboration) ‖ M12 (Company Context)

### File Ownership
| Directory/File | M7 | M8 | M12 |
|---------------|----|----|-----|
| `services/ai/agents/summarizing_ai/` | Owner | — | — |
| `services/ai/processing/fabrication_validator.py` | Owner | — | — |
| `services/ai/processing/version_tracker.py` | Owner | — | — |
| `services/pdf/` | Owner | — | — |
| `frontend/src/features/brd/` | Owner | — | — |
| `services/gateway/apps/brd/` | Owner | — | — |
| `services/core/apps/brd/` | Owner | — | — |
| `frontend/src/features/collaboration/` | — | Owner | — |
| `frontend/src/features/presence/` | — | Owner | — |
| `services/gateway/apps/collaboration/` | — | Owner | — |
| `services/core/apps/collaboration/` | — | Owner | — |
| `services/ai/agents/context_agent/` | — | — | Owner |
| `services/ai/agents/context_extension/` | — | — | Owner |
| `services/ai/embedding/` | — | — | Owner |
| `frontend/src/features/delegation/` | — | — | Owner |
| `frontend/src/pages/IdeaWorkspace/` | Additive (Review tab) | Additive (Collaboration, Presence, Offline) | — |
| `frontend/src/features/chat/` | — | — | Additive (DelegationMessage, board refs) |
| `frontend/src/store/` | — | Additive (websocket, presence) | — |
| `services/ai/agents/facilitator/plugins.py` | — | — | Additive (replace delegation stubs) |
| `services/ai/processing/pipeline.py` | — | — | Additive (delegation steps 3a, 3b) |
| `services/ai/grpc_server/servicer.py` | Additive (TriggerBrdGeneration) | — | Additive (UpdateBuckets) |
| `services/gateway/apps/websocket/consumers.py` | — | Additive (presence) | — |
| `services/gateway/apps/admin/` | — | — | Additive (gRPC call on AI context save) |
| `proto/ai.proto` | Additive (BrdGeneration) | — | Additive (UpdateBuckets) |
| `proto/pdf.proto` | Additive (GeneratePdf) | — | — |
| `frontend/src/pages/LandingPage/` | — | Additive (invitation cards) | — |
| `frontend/src/router.tsx` | — | Additive (/shared/:token) | — |

### Integration Points
- M7 and M8 both touch `IdeaWorkspace` but in different areas: M7 = Review tab content, M8 = workspace header + offline banner + invitation banner. No overlap.
- M7 and M12 both touch AI service but in different agent directories. M12 modifies pipeline.py (add delegation steps) and facilitator plugins.py (replace stubs). M7 adds to AI gRPC servicer (BrdGeneration). Keep changes additive.
- M8 and M12 don't share any files.

### Merge Order: M12 first, then M8, then M7
1. **M12** — Purely AI-internal changes (context agents, embedding pipeline, facilitator plugin rewiring). Least integration surface with frontend.
2. **M8** — Touches workspace header, landing page, WebSocket. Moderate integration surface.
3. **M7** — Touches Review tab, PDF service, AI BRD generation. Most new service (PDF). Last to merge so BRD + Review tab are the final additions.

---

## Wave 5: M9 (Review Workflow) ‖ M10 (Notifications)

### File Ownership
| Directory/File | M9 | M10 |
|---------------|-----|-----|
| `frontend/src/features/review/` | Owner | — |
| `frontend/src/pages/ReviewPage/` | Owner | — |
| `services/gateway/apps/review/` | Owner | — |
| `services/core/apps/review/` | Owner | — |
| `services/notification/` | — | Owner |
| `frontend/src/features/notifications/` | — | Owner |
| `services/gateway/apps/notifications/` | — | Owner |
| `frontend/src/pages/IdeaWorkspace/` | Additive (submit, review section, timeline) | — |
| `frontend/src/features/brd/` | Additive (enable submit) | — |
| `frontend/src/components/layout/Navbar/` | — | Additive (NotificationBell replace) |
| `frontend/src/components/layout/UserDropdown/` | — | Additive (EmailPreferences) |
| `frontend/src/router.tsx` | Additive (/reviews) | — |
| `services/gateway/apps/websocket/consumers.py` | Additive (state change) | Additive (notification.created) |
| `services/gateway/grpc_server/servicer.py` | — | Additive (CreateNotification) |

### Integration Points
- M9 publishes idea.state.changed events. M10's notification service consumes them. After both merge, review state changes trigger notifications automatically.
- Both modify WebSocket consumers — different event types, additive.

### Merge Order: M10 first, then M9
1. **M10** — Notification infrastructure is standalone. After merge, all existing events (from M3 monitoring, M8 collaboration) immediately start producing notifications.
2. **M9** — Review workflow publishes events that M10's consumers already listen for. After M9 merges, review notifications work immediately.

---

## Cross-Wave Stub Tracking

This table tracks all stubs created in earlier milestones and when they are replaced:

| Stub | Created In | Replaced In | What Changes |
|------|-----------|-------------|-------------|
| NotificationBell (0 count, no panel) | M1 | M10 | Real unread count, floating panel |
| IdeasListFloating (empty) | M1 | M2 | Real idea lists |
| Celery soft_delete_cleanup (no-op) | M1 | M2 | Real permanent deletion logic |
| Celery monitoring_health_check (no-op) | M1 | M3 | Real health check logic |
| Celery keyword_matching_sweep (no-op) | M1 | M11 | Real keyword matching logic |
| gRPC service methods (default responses) | M1 | M2–M12 | Real implementations per milestone |
| WebSocket consumer (no domain events) | M1 | M4, M5, M8 | Chat, board, presence events |
| Invitations list on landing (empty) | M2 | M8 | Real invitation data |
| Agent mode dropdown (not connected) | M2 | M6 | AI reads agent_mode |
| Presence indicators (current user only) | M2 | M8 | Multi-user presence |
| Collaborator invite button (placeholder) | M2 | M8 | CollaboratorModal |
| Review tab (empty state) | M2 | M7 | BRD editor + preview |
| Board tab (empty state) | M2 | M5 | React Flow canvas |
| Chat panel (empty state) | M2 | M4 | Chat messages + input |
| Monitoring "active connections" (0) | M3 | M8 | Real WebSocket connection count |
| Monitoring "AI processing stats" (0) | M3 | M6 | Real AI metrics |
| AI Context save → RAG re-indexing (DB only) | M3 | M12 | Chunking + embedding pipeline |
| Email alert dispatch (log only) | M3 | M10 | Real email dispatch |
| AI message creation (no AI generates) | M4 | M6 | Facilitator generates messages |
| @ai mention → AI response (no trigger) | M4 | M6 | Pipeline checks @ai mentions |
| Rate limit auto-reset (manual only) | M4 | M6 | Auto-reset on ai.processing.complete |
| AIProcessingIndicator (never shown) | M4 | M6 | Shown during AI processing |
| ContextWindowIndicator (hidden) | M4 | M6 | Shows context utilization |
| AI-created board nodes (API only) | M5 | M6 | Board Agent creates nodes |
| UserSelectionHighlight (single user) | M5 | M8 | Multi-user selection broadcast |
| Board item reference (plain text) | M5 | M12 | Clickable links with navigation |
| Facilitator delegate_to_context_agent (unavailable) | M6 | M12 | Real RAG delegation |
| Facilitator delegate_to_context_extension (unavailable) | M6 | M12 | Real history search |
| similarity.detected event (not published) | M6 | M11 | Background matching publishes |
| Submit button (disabled) | M7 | M9 | Full submit flow |
| Reviewer assignment selector (hidden) | M7 | M9 | Reviewer multi-select |
| Review section below fold (empty) | M7 | M9 | Timeline, state, reviewers |
| Similar ideas in review section (empty) | M9 | M11 | Real similar ideas data |
| MergeRequestBanner actions (501) | M10 | M11 | Real merge request API |
| similarity.confirmed consumer (no events) | M10 | M11 | Background matching fires events |
