# Release Plan

## MVP Boundary

- **Release strategy:** Full application delivered as one release (Constraint #8). No phased feature rollout.
- **All 16 milestones are required for release.**
- **Core flow (M1-M12):** Brainstorm -> AI facilitation -> BRD generation -> Review workflow + Collaboration + Notifications
- **Enhancement features (M13-M16):** Similarity detection, merge flow, admin panel, polish/i18n/accessibility

## Milestone Execution Order

### M1: Foundation & Auth
- **Purpose:** Schema, models, auth bypass, shared UI, layout, theme — everything every other milestone depends on
- **Dependencies:** None (foundation)

### M2: Landing Page & Idea CRUD
- **Purpose:** App entry point, idea lifecycle management, the starting point for all user flows
- **Dependencies:** M1

### M3: Idea Workspace — Layout & Chat
- **Purpose:** Core workspace shell with chat functionality — the primary user interface
- **Dependencies:** M2

### M4: Digital Board — Core
- **Purpose:** Board rendering with React Flow — nodes, connections, toolbar, minimap
- **Dependencies:** M3

### M5: Board Interactions & Undo
- **Purpose:** Advanced board interactions — drag, nesting, undo/redo, references, AI indicators
- **Dependencies:** M4

### M6: WebSocket & Real-Time
- **Purpose:** Real-time infrastructure — chat broadcast, board sync, presence, offline handling
- **Dependencies:** M3

### M7: AI Core — Chat Processing Pipeline
- **Purpose:** Facilitator agent with chat processing — the core AI loop
- **Dependencies:** M5, M6

### M8: AI Board Agent & Context
- **Purpose:** Board Agent, Context Agent (RAG), Context Extension, Compression, Keywords
- **Dependencies:** M7

### M9: BRD & PDF Generation
- **Purpose:** Summarizing AI, BRD editing, readiness evaluation, PDF generation
- **Dependencies:** M8

### M10: Review Workflow
- **Purpose:** Submit flow, review page, reviewer actions, timeline, state machine
- **Dependencies:** M9

### M11: Collaboration & Sharing
- **Purpose:** Invitations, collaborator management, visibility, read-only sharing, multi-user
- **Dependencies:** M6

### M12: Notification System
- **Purpose:** Bell, panel, toasts, email service, all notification events, email preferences
- **Dependencies:** M6

### M13: Similarity Detection & Merge
- **Purpose:** Keyword matching, vector similarity, deep comparison, merge request + synthesis
- **Dependencies:** M8, M12

### M14: Merge Advanced & Manual
- **Purpose:** Append flow, manual merge, recursive merge, permanent dismissal, edge cases
- **Dependencies:** M13

### M15: Admin Panel
- **Purpose:** AI context editors, parameters, monitoring dashboard, health checks, users
- **Dependencies:** M8

### M16: Polish & Cross-Cutting
- **Purpose:** Error handling, idle state, i18n completion, accessibility, production auth
- **Dependencies:** M10, M11, M12

## Milestone Summary

| Milestone | Name | Features Included | Est. Stories | Dependencies | MVP |
|-----------|------|-------------------|-------------|-------------|-----|
| M1 | Foundation & Auth | FA-7 (bypass), FA-14 (partial), FA-16 (scaffold), FA-17 (scaffold) | 10 | None | Yes |
| M2 | Landing Page & Idea CRUD | FA-9 | 8 | M1 | Yes |
| M3 | Idea Workspace — Layout & Chat | FA-1, FA-2 (partial: reactions, mentions) | 10 | M2 | Yes |
| M4 | Digital Board — Core | FA-3 (core rendering + CRUD) | 9 | M3 | Yes |
| M5 | Board Interactions & Undo | FA-3 (advanced: undo, nesting, refs, AI indicators) | 8 | M4 | Yes |
| M6 | WebSocket & Real-Time | FA-6, FA-15 (partial: offline) | 10 | M3 | Yes |
| M7 | AI Core — Chat Processing | FA-2 (Facilitator, title gen, language, rate limit) | 10 | M5, M6 | Yes |
| M8 | AI Board Agent & Context | FA-2 (Board Agent, Context, Compression, Keywords) | 10 | M7 | Yes |
| M9 | BRD & PDF Generation | FA-4 (BRD gen, editing, PDF, review tab UI) | 9 | M8 | Yes |
| M10 | Review Workflow | FA-4 (submit, review actions), FA-10, FA-1 (state machine) | 10 | M9 | Yes |
| M11 | Collaboration & Sharing | FA-8 | 9 | M6 | Yes |
| M12 | Notification System | FA-12, FA-13 | 9 | M6 | Yes |
| M13 | Similarity Detection & Merge | FA-5 (detection + basic merge) | 10 | M8, M12 | Yes |
| M14 | Merge Advanced & Manual | FA-5 (append, manual, recursive, dismissal) | 7 | M13 | Yes |
| M15 | Admin Panel | FA-11 | 10 | M8 | Yes |
| M16 | Polish & Cross-Cutting | FA-14, FA-15, FA-16, FA-17, FA-7 (production) | 10 | M10, M11, M12 | Yes |

**Totals:** 16 milestones, ~149 estimated stories

## Dependency Flow Diagram

```
M1 (Foundation)
├── M2 (Landing)
│   └── M3 (Workspace & Chat)
│       ├── M4 (Board Core)
│       │   └── M5 (Board Advanced)
│       │       └── M7 (AI Chat) ─────────────────┐
│       │           └── M8 (AI Board & Context)    │
│       │               ├── M9 (BRD & PDF)         │
│       │               │   └── M10 (Review) ──────┤
│       │               ├── M13 (Similarity) ───┐  │
│       │               │   └── M14 (Merge Adv) │  │
│       │               └── M15 (Admin) ────────┤  │
│       └── M6 (WebSocket)                      │  │
│           ├── M11 (Collaboration) ────────────┤  │
│           └── M12 (Notifications) ────────────┤  │
│                                               │  │
└───────────────────────────────────────────────┘  │
                M16 (Polish) ◄─────────────────────┘
```

## Execution Guide

### Branch Strategy

| Milestone | Branch Pattern | Base Branch | Merge Target |
|-----------|---------------|-------------|-------------|
| M1 | ralph/m1-foundation | dev | dev |
| M2 | ralph/m2-landing | dev (after M1 merge) | dev |
| M3 | ralph/m3-workspace-chat | dev (after M2 merge) | dev |
| M4 | ralph/m4-board-core | dev (after M3 merge) | dev |
| M5 | ralph/m5-board-advanced | dev (after M4 merge) | dev |
| M6 | ralph/m6-websocket | dev (after M3 merge) | dev |
| M7 | ralph/m7-ai-chat | dev (after M5+M6 merge) | dev |
| M8 | ralph/m8-ai-context | dev (after M7 merge) | dev |
| M9 | ralph/m9-brd-pdf | dev (after M8 merge) | dev |
| M10 | ralph/m10-review | dev (after M9 merge) | dev |
| M11 | ralph/m11-collaboration | dev (after M6 merge) | dev |
| M12 | ralph/m12-notifications | dev (after M6 merge) | dev |
| M13 | ralph/m13-similarity | dev (after M8+M12 merge) | dev |
| M14 | ralph/m14-merge-advanced | dev (after M13 merge) | dev |
| M15 | ralph/m15-admin | dev (after M8 merge) | dev |
| M16 | ralph/m16-polish | dev (after M10+M11+M12 merge) | dev |

### Acceptance Criteria per Milestone

**Every milestone must pass:**
- All new tests pass (pytest, vitest, playwright as applicable)
- TypeScript typecheck passes (`tsc --noEmit`)
- No regressions on previous milestones (full test suite)
- Code follows project structure from `project-structure.md`
- API endpoints match contracts in `api-design.md`
- Components follow design specs from `component-specs.md` and `design-system.md`

**Additional per-milestone criteria are defined in each milestone scope file.**
