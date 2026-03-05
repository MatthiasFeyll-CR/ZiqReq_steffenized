# Dependency Analysis

## Infrastructure Layer (must exist first)

| Component | Type | Why First | Source |
|-----------|------|-----------|--------|
| Monorepo scaffold + Docker Compose | Build/infra | All services, containers, networking | project-structure.md |
| PostgreSQL 16 + pgvector extension | Database | All tables depend on it | tech-stack.md, data-model.md |
| Django models + migrations (22 tables) | Database | All APIs need models | data-model.md |
| Auth bypass middleware + dev users | Auth | All routes are protected | F-7.1, tech-stack.md |
| gRPC infrastructure (proto files, stubs) | Communication | Gateway ↔ Core ↔ AI communication | project-structure.md, api-design.md |
| WebSocket (Django Channels + Redis) | Real-time | Chat, board sync, presence, notifications | tech-stack.md, F-6.1 |
| Message broker (RabbitMQ + Celery) | Async | Event-driven architecture, background jobs | tech-stack.md |
| Frontend scaffold (React + Vite + TS) | Frontend | All pages depend on it | tech-stack.md |
| Design system (Tailwind, shadcn/ui, theme, i18n) | Frontend | All components need theming + translations | design-system.md, FA-16, FA-17 |
| Shared UI primitives (16 components) | Frontend | All pages use them | component-inventory.md |
| Layout (Navbar, PageShell, UserDropdown) | Frontend | All authenticated pages | component-inventory.md |
| Redux store + TanStack Query + Router | Frontend | State management, data fetching, navigation | tech-stack.md |
| Error handling foundation (ErrorBoundary, ErrorToast, ErrorLogModal) | Cross-cutting | FA-14 required everywhere | F-14.1, component-inventory.md |

## Feature Dependency Map

| Feature ID | Feature Name | Hard Dependencies | Soft Dependencies | Data Tables | API Endpoints | Components |
|-----------|-------------|-------------------|-------------------|-------------|---------------|------------|
| FA-1 | Idea Workspace | Ideas CRUD, Auth | Board (FA-3), Chat (FA-2) | ideas | GET/POST /api/ideas, GET /api/ideas/:id | PanelDivider, Tab system |
| FA-2 (chat) | Chat & Reactions | Ideas, Users, WebSocket | AI (FA-2 AI) | chat_messages, ai_reactions, user_reactions | POST/GET /api/ideas/:id/chat, reactions endpoints | ChatPanel, ChatMessage, ReactionChips, MentionDropdown |
| FA-2 (AI) | AI Facilitation | Chat, Board, gRPC to Core | Company Context (F-2.15) | chat_context_summaries, idea_keywords, idea_embeddings | gRPC TriggerChatProcessing | AIProcessingIndicator, ContextWindowIndicator |
| FA-3 | Digital Board | Ideas, WebSocket | AI Board Agent | board_nodes, board_connections | CRUD /api/ideas/:id/board/* | BoardCanvas, BoxNode, GroupNode, FreeTextNode, BoardToolbar |
| FA-4 (BRD) | BRD Generation | AI Pipeline (Summarizing AI) | PDF service | brd_drafts, brd_versions | BRD endpoints, gRPC TriggerBrdGeneration | PDFPreview, BRDSectionEditor, SectionField, ProgressIndicator |
| FA-4 (review) | Review Workflow | BRD generation, Submit flow | Notifications | review_assignments, review_timeline_entries | Review endpoints | ReviewTimeline, TimelineEntry, CommentInput, ReviewCard |
| FA-5 | Similarity & Merge | AI Pipeline (Keywords, Embeddings), Celery | Deep Comparison, Merge Synthesizer | merge_requests, idea_keywords, idea_embeddings | Merge endpoints | MergeRequestBanner, SimilarIdeaCard |
| FA-6 | Real-Time Collab | WebSocket, Auth | Presence tracking | — (ephemeral) | WebSocket events | OfflineBanner, ConnectionIndicator |
| FA-7 | Authentication | — (foundation) | Azure AD (production) | users | POST /api/auth/validate | LoginPage, DevUserSwitcher |
| FA-8 | Visibility & Sharing | Ideas, Users, WebSocket | Notifications | collaboration_invitations, idea_collaborators | Invitation endpoints | CollaboratorModal, PresenceIndicators, InvitationBanner |
| FA-9 | Landing Page | Ideas CRUD | Collaboration (invitations list) | ideas, idea_collaborators | GET /api/ideas (list) | HeroSection, IdeaCard, FilterBar, InvitationCard |
| FA-10 | Review Page | Review workflow | — | review_assignments | GET /api/reviews | ReviewCard (extends IdeaCard) |
| FA-11 | Admin Panel | Admin parameters, Singletons | Monitoring service | admin_parameters, facilitator_context_bucket, context_agent_bucket, monitoring_alert_configs | Admin endpoints | AIContextEditor, ParametersTable, MonitoringDashboard, UserSearch |
| FA-12 | Notifications | Event-producing features | Email service | notifications | Notification endpoints | NotificationBell, NotificationPanel, Toast |
| FA-13 | Email Preferences | Users table | Notification service | users (email_notification_preferences) | PATCH /api/users/me/preferences | EmailPreferencesPanel |
| FA-14 | Error Handling | — (foundation) | — | — | — | ErrorToast, ErrorLogModal |
| FA-15 | Idle State | WebSocket | — | — | WebSocket presence events | — (behavioral) |
| FA-16 | i18n | — (foundation) | — | — | — | — (cross-cutting) |
| FA-17 | Theme | — (foundation) | — | — | — | — (cross-cutting) |
| F-2.15 | Company Context (RAG) | AI Pipeline, pgvector | Admin AI Context tab | context_chunks, facilitator_context_bucket, context_agent_bucket | gRPC UpdateBuckets | DelegationMessage |
| F-2.14 ext | Context Extension | AI Pipeline | Full chat history gRPC | chat_context_summaries | gRPC GetFullChatHistory | — |

## Dependency Chains (Critical Paths)

### Chain 1: Core Brainstorming (Longest — Critical Path)
```
Foundation (M1)
  → Ideas CRUD + Landing (M2)
    → Chat System (M4) + Board System (M5)  [parallel]
      → AI Processing Pipeline (M6)
        → BRD Generation (M7)
          → Review Workflow (M9)
```

### Chain 2: Admin (Short, Independent)
```
Foundation (M1)
  → Admin Panel (M3)  [parallel with M2]
```

### Chain 3: Collaboration (Branches from Ideas)
```
Foundation (M1)
  → Ideas CRUD (M2)
    → Chat (M4) + Board (M5)
      → AI Pipeline (M6)
        → Collaboration & Presence (M8)  [parallel with M7]
```

### Chain 4: Company Context AI (Branches from AI Pipeline)
```
AI Pipeline (M6)
  → Company Context RAG + Context Extension (M12)  [parallel with M7, M8]
```

### Chain 5: Similarity & Merge (Post-MVP, depends on AI)
```
AI Pipeline (M6, Keyword Agent + Embeddings)
  → Similarity Detection & Merge (M11)
```

### Chain 6: Notifications (Cross-cutting)
```
Foundation (M1)
  → [Any event-producing milestone]
    → Notification System (M10)  [parallel with M9]
```

## Shared Components (Cross-Cutting)

| Component | Used By Features | Must Exist Before | Source |
|-----------|-----------------|-------------------|--------|
| UI Primitives (16) | All pages | Any page-specific work | component-inventory.md |
| Layout (Navbar, PageShell, etc.) | All authenticated pages | Any page-specific work | component-inventory.md |
| IdeaCard | Landing, Review, Ideas List floating | Landing Page (M2) | component-inventory.md |
| Toast system | All features | Any user-facing feature | FA-12, FA-14 |
| ErrorBoundary + ErrorToast + ErrorLogModal | All pages | Any user-facing feature | FA-14, component-inventory.md |
| EmptyState | Landing, Review, Admin, Notifications | Any list-based page | component-inventory.md |
| NotificationBell + Panel | Navbar (all pages) | Notification milestone | component-inventory.md |
| ConnectionIndicator | Navbar | WebSocket setup | FA-6 |

## AI Dependencies

| AI Feature | Infrastructure Required | Depends On Features | Source |
|-----------|----------------------|---------------------|--------|
| Facilitator (6 tools) | Semantic Kernel, gRPC to Core, Azure OpenAI | Chat messages + Board nodes exist | agent-architecture.md §3.1 |
| Board Agent (8 tools) | Semantic Kernel, gRPC to Core | Board nodes + connections exist | agent-architecture.md §3.2 |
| Context Agent (RAG) | pgvector, embedding model, context_chunks table | Admin AI Context populated, RAG indexing | agent-architecture.md §3.3 |
| Context Extension | Escalated model tier, full chat gRPC | Long conversations with compression | agent-architecture.md §3.4 |
| Summarizing AI | AI Pipeline base | Chat + Board data, BRD draft table | agent-architecture.md §3.5 |
| Keyword Agent | Cheap model tier | Chat + Board data, idea_keywords table | agent-architecture.md §3.6 |
| Deep Comparison | Default model tier | Two ideas with keywords/embeddings | agent-architecture.md §3.7 |
| Context Compression | Cheap model tier | Chat history, context_summaries table | agent-architecture.md §3.8 |
| Merge Synthesizer | Default model tier | Two ideas' full context | agent-architecture.md §3.9 |

## Parallel Opportunities

Features with NO dependencies on each other:

- **Group A:** Landing Page (M2) ‖ Admin Panel (M3) — different pages, different DB tables, different API namespaces, zero file overlap
- **Group B:** Chat System (M4) ‖ Digital Board (M5) — different tables (chat_messages vs board_nodes), different UI panels (left vs right), different WebSocket event types
- **Group C:** BRD Generation (M7) ‖ Collaboration (M8) ‖ Company Context AI (M12) — BRD touches ai/summarizing_ai + pdf service + brd tables; Collaboration touches core/collaboration + invitations; Company Context touches ai/context_agent + embedding pipeline. Clean service boundaries.
- **Group D:** Review Workflow (M9) ‖ Notifications (M10) — Review touches core/review + review page; Notifications touches notification service + gateway notifications. M10 wires events from M9 but notification infrastructure is independent.
- **Group E (Post-MVP):** Similarity & Merge (M11) — standalone post-MVP, depends only on AI Pipeline (M6)

## Circular Dependencies

None identified. All dependency chains form a directed acyclic graph (DAG).
