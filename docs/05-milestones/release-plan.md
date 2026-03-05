# Release Plan

## MVP Boundary

- **MVP features:** Foundation, Landing Page, Idea Workspace, Chat, Board, AI Facilitation (Facilitator + Board Agent + Keyword + Compression), BRD Generation, PDF Generation, Collaboration & Presence, Review Workflow, Notification System, Admin Panel, Company Context AI, Error Handling, Idle State, i18n, Theme
- **MVP corresponds to:** Waves 0 through 5 (Milestones M1–M10, M12)
- **Post-MVP features:** Similarity Detection & Merge (keyword matching, vector similarity, deep comparison, merge flow, append flow, manual merge)
- **Post-MVP corresponds to:** Wave 6 (Milestone M11)

## Wave Structure

### Wave 0: Foundation
- **Purpose:** Establish the entire technical foundation — monorepo, all containers, database with all 22 tables, auth bypass, gRPC/WebSocket/broker infrastructure, frontend scaffold with design system, shared UI primitives, layout components, and cross-cutting concerns (theme, i18n, error handling).
- **Milestones:** M1
- **Parallel execution:** No (single milestone)
- **Gate criteria for Wave 1:** All containers start and pass health checks. Frontend renders Navbar + PageShell. Auth bypass works with 4 dev users. All 22 DB tables exist. gRPC, WebSocket, and broker connections established.

### Wave 1: Core Pages
- **Purpose:** Deliver the two main authenticated pages (Landing + Admin) and the Idea Workspace shell. Users can create ideas, manage them, and admins can configure the platform.
- **Milestones:** M2 (Landing Page & Idea Workspace Shell), M3 (Admin Panel)
- **Parallel execution:** Yes — M2 and M3 touch completely different pages, API namespaces, and DB tables.
  - M2 owns: `frontend/src/pages/LandingPage/`, `frontend/src/pages/IdeaWorkspace/`, `frontend/src/features/ideas/`, `services/gateway/apps/ideas/`, `services/core/apps/ideas/`
  - M3 owns: `frontend/src/pages/AdminPanel/`, `frontend/src/features/admin/`, `services/gateway/apps/admin/`, `services/core/apps/admin/`
- **Merge order:** M3 first (Admin — more isolated), then M2 (Landing — touches routing, IdeaCard shared component)
- **Gate criteria for Wave 2:** Landing page renders idea lists, creation works, workspace shell loads with panel layout. Admin panel renders all 4 tabs with functional CRUD.

### Wave 2: Chat & Board
- **Purpose:** Implement the two core workspace panels — chat (left) and board (right). Real-time sync via WebSocket for both.
- **Milestones:** M4 (Chat System), M5 (Digital Board)
- **Parallel execution:** Yes — Chat and Board are different panels, different DB tables, different API endpoints.
  - M4 owns: `frontend/src/features/chat/`, `services/gateway/apps/chat/`, `services/core/apps/chat/`
  - M5 owns: `frontend/src/features/board/`, `services/gateway/apps/board/`, `services/core/apps/board/`
- **Merge order:** M4 first (Chat — simpler, fewer shared file touches), then M5 (Board — more complex, React Flow integration)
- **Gate criteria for Wave 3:** Chat messages send/receive in real-time. Board nodes/connections CRUD with React Flow rendering. Undo/redo works. @mentions and reactions functional.

### Wave 3: AI Processing Pipeline
- **Purpose:** Bring the AI to life. Implement the core processing pipeline (Facilitator + Board Agent), keyword generation, context compression, and all pipeline orchestration (debounce, abort-and-restart).
- **Milestones:** M6
- **Parallel execution:** No (single milestone — depends on both Chat M4 and Board M5)
- **Gate criteria for Wave 4:** User sends chat message → AI responds after debounce. AI creates/modifies board nodes. Title auto-generates. Agent mode switch works. Keywords generated. Context compression triggers on long conversations. AI processing indicator shows during processing.

### Wave 4: BRD, Collaboration & Company Context
- **Purpose:** Three independent feature domains built in parallel: BRD generation + PDF + review tab editing; collaboration invitations + presence + sharing; company context RAG + context extension + AI polish.
- **Milestones:** M7 (BRD Generation & Review Tab), M8 (Collaboration & Presence), M12 (Company Context & AI Polish)
- **Parallel execution:** Yes (3-way) — clean service boundary separation.
  - M7 owns: `services/ai/agents/summarizing_ai/`, `services/pdf/`, `frontend/src/features/brd/`, `services/gateway/apps/brd/`, `services/core/apps/brd/`
  - M8 owns: `services/core/apps/collaboration/`, `services/gateway/apps/collaboration/`, `frontend/src/features/collaboration/`, `frontend/src/features/presence/`
  - M12 owns: `services/ai/agents/context_agent/`, `services/ai/agents/context_extension/`, `services/ai/embedding/`, `frontend/src/features/delegation/`
- **Merge order:** M12 first (Company Context — AI-internal, least integration surface), then M8 (Collaboration — touches workspace header area), then M7 (BRD — touches workspace right panel, adds PDF service)
- **Gate criteria for Wave 5:** BRD generates from idea state, sections editable/lockable, PDF generates, document versioning works. Collaboration invitations flow end-to-end, presence shows online/idle users, offline banner works. Company context RAG retrieves relevant chunks, delegation messages appear in chat.

### Wave 5: Review Workflow & Notifications
- **Purpose:** Complete the idea lifecycle (submit → review → decision) and implement the full notification system (bell, email, preferences).
- **Milestones:** M9 (Review Workflow), M10 (Notification System)
- **Parallel execution:** Yes — Review touches review-specific APIs/pages, Notifications touches notification service/gateway.
  - M9 owns: `services/core/apps/review/`, `services/gateway/apps/review/`, `frontend/src/features/review/`, `frontend/src/pages/ReviewPage/`
  - M10 owns: `services/notification/`, `services/gateway/apps/notifications/`, `frontend/src/features/notifications/`
- **Merge order:** M10 first (Notifications — independent infrastructure), then M9 (Review — may trigger notification events that M10 handles)
- **Gate criteria for Wave 6 (or release):** Full idea lifecycle works: create → brainstorm → generate BRD → submit → review → accept/reject/drop → resubmit. Notification bell shows unread count, email notifications dispatched per preferences, all FA-12.5 events wired.

### Wave 6: Similarity & Merge (POST-MVP)
- **Purpose:** Add similarity detection (keyword matching + vector search + AI deep comparison) and the full merge/append flow.
- **Milestones:** M11 (Similarity Detection & Merge)
- **Parallel execution:** No (single milestone)
- **Gate criteria for release:** Background matching detects similar ideas. Deep comparison confirms genuine similarity. Merge flow creates new merged idea with synthesized context. Append flow works with three-way consent. Manual merge and permanent dismissal functional.

## Milestone Summary

| Milestone | Wave | Name | Features Included | Est. Stories | Parallel With | Dependencies |
|-----------|------|------|-------------------|-------------|--------------|-------------|
| M1 | 0 | Foundation & Scaffold | FA-7 (bypass), FA-14, FA-15 (partial), FA-16, FA-17, infra | 10 | None | None |
| M2 | 1 | Landing Page & Idea Workspace Shell | FA-1, FA-9 | 8 | M3 | M1 |
| M3 | 1 | Admin Panel | FA-11 | 7 | M2 | M1 |
| M4 | 2 | Chat System | FA-2 (chat, reactions, mentions, rate limiting) | 8 | M5 | M1, M2 |
| M5 | 2 | Digital Board | FA-3 | 9 | M4 | M1, M2 |
| M6 | 3 | AI Processing Pipeline | FA-2 (AI facilitation, title gen, keywords, compression) | 10 | None | M4, M5 |
| M7 | 4 | BRD Generation & Review Tab | FA-4 (BRD, PDF, review tab) | 8 | M8, M12 | M6 |
| M8 | 4 | Collaboration & Presence | FA-6, FA-8, FA-15 | 8 | M7, M12 | M6 |
| M12 | 4 | Company Context & AI Polish | F-2.5, F-2.6, F-2.15, F-2.16 (AI side) | 7 | M7, M8 | M6 |
| M9 | 5 | Review Workflow | FA-4 (submit, review actions), FA-10 | 8 | M10 | M7 |
| M10 | 5 | Notification System | FA-12, FA-13 | 8 | M9 | M8 |
| M11 | 6 | Similarity Detection & Merge | FA-5 | 9 | None | M6 |

**Total:** 12 milestones, 7 waves, ~100 stories estimated

## Dependency Flow Diagram
```
M1 → [M2 ‖ M3] → [M4 ‖ M5] → M6 → [M7 ‖ M8 ‖ M12] → [M9 ‖ M10] → M11
                                                                          ↑
                                                              (POST-MVP) ─┘
```

## Execution Guide

### Branch Strategy
| Wave | Branch Pattern | Base Branch | Merge Target |
|------|---------------|-------------|-------------|
| 0 | ralph/m1-foundation | dev | dev |
| 1 | ralph/m2-landing, ralph/m3-admin | dev (at w0 tag) | dev |
| 2 | ralph/m4-chat, ralph/m5-board | dev (at w1 tag) | dev |
| 3 | ralph/m6-ai-pipeline | dev (at w2 tag) | dev |
| 4 | ralph/m7-brd, ralph/m8-collaboration, ralph/m12-company-context | dev (at w3 tag) | dev |
| 5 | ralph/m9-review, ralph/m10-notifications | dev (at w4 tag) | dev |
| 6 | ralph/m11-similarity-merge | dev (at w5 tag) | dev |

### Merge Order per Wave

| Wave | Order | Reasoning |
|------|-------|-----------|
| 1 | M3 → M2 | Admin is more isolated; Landing touches shared routing and IdeaCard |
| 2 | M4 → M5 | Chat is simpler; Board has more complex React Flow integration |
| 4 | M12 → M8 → M7 | Company Context is AI-internal (least conflicts); Collaboration touches workspace header; BRD touches workspace right panel and adds PDF service |
| 5 | M10 → M9 | Notification infrastructure independent; Review triggers notification events |

### Wave Acceptance Criteria

| Wave | Criteria |
|------|---------|
| 0 | All Docker containers healthy. DB migrations applied. Auth bypass with 4 dev users. Frontend renders layout with theme/i18n. gRPC/WS/broker connections verified. |
| 1 | Ideas CRUD end-to-end. Landing page functional. Workspace shell loads. Admin panel all 4 tabs operational. |
| 2 | Chat real-time send/receive. Board CRUD with React Flow. @mentions, reactions, rate limiting. Undo/redo. WebSocket sync for both. |
| 3 | AI processes chat messages and modifies board. Title generation. Keywords generated. Context compression works. Agent mode switch functional. |
| 4 | BRD generates and edits. PDF generates. Collaboration invitations flow. Presence tracking. Offline/reconnect. Company context RAG works. Delegation messages render. |
| 5 | Full submit → review → decision lifecycle. Notification bell + email. Preferences respected. All FA-12.5 events wired. |
| 6 | Similarity detection end-to-end. Merge creates new idea. Append with 3-way consent. Manual merge. Permanent dismissal. |
