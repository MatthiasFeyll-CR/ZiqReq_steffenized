# Dependency Analysis

## Infrastructure Layer (must exist first)

| Component | Type | Why First | Source |
|-----------|------|-----------|--------|
| Docker Compose + Nginx | Container orchestration | All services run in Docker; Nginx routes frontend/API/WS under single origin | constraints.md #7, tech-stack.md |
| PostgreSQL + pgvector | Database | Every service depends on persistent storage; pgvector needed for AI tables | tech-stack.md, data-model.md |
| Redis | Channel layer | Django Channels pub/sub backend for WebSocket | tech-stack.md |
| RabbitMQ | Message broker | Event-driven communication between all services | tech-stack.md |
| Gateway service (Django + Channels) | API + WebSocket | Single entry point for frontend; all REST + WS traffic | project-structure.md |
| Core service (Django) | Domain logic | Owns 15 of 22 tables; all business logic routes through Core | project-structure.md |
| AI service (Django + SK) | AI processing | 5 owned tables; all 9 agents live here | project-structure.md, agent-architecture.md |
| Notification service | Event consumer | Email dispatch + notification creation | project-structure.md |
| PDF service (WeasyPrint) | Stateless gRPC | BRD-to-PDF generation | tech-stack.md |
| Celery worker + beat | Background tasks | Soft delete cleanup, monitoring, keyword matching | tech-stack.md |
| Auth bypass middleware | Authentication | All route protection + permission checks need auth | F-7.1 |
| Database schema + seed data | Data layer | Tables, indexes, admin parameters, dev users, singleton buckets | data-model.md |
| gRPC protobuf definitions | Service contracts | Gateway-Core, Gateway-AI, Core-AI communication | api-design.md |
| Frontend scaffold (Vite + React + providers) | UI shell | All pages depend on routing, state management, auth context | tech-stack.md |

## Feature Dependency Map

| Feature ID | Feature Name | Hard Dependencies | Soft Dependencies | Data Tables | API Endpoints | Components |
|-----------|-------------|-------------------|-------------------|-------------|---------------|------------|
| F-7.1 | Dev Auth Bypass | Infrastructure | — | users | POST /api/auth/validate, POST /api/auth/dev-login | DevUserSwitcher |
| F-7.2 | Production Auth | Infrastructure | — | users | POST /api/auth/validate | MsalProvider |
| F-17.1-5 | Theme Support | Frontend scaffold | — | — (localStorage) | — | ThemeToggle |
| F-16.1-4 | i18n | Frontend scaffold | — | — (localStorage) | — | LanguageSwitcher |
| F-9.1 | Landing Page Structure | F-7.1, Idea CRUD | — | ideas, idea_collaborators, collaboration_invitations | GET /api/ideas | LandingPage, IdeaCard |
| F-9.2 | Idea Creation | F-9.1 | — | ideas, chat_messages | POST /api/ideas | HeroSection |
| F-9.3 | Soft Delete | F-9.1 | Celery worker | ideas (deleted_at) | DELETE /api/ideas/:id, POST /api/ideas/:id/restore | TrashList |
| F-9.4 | Search & Filter | F-9.1 | — | ideas | GET /api/ideas (query params) | SearchBar, FilterControls |
| F-1.1 | Idea Page Layout | F-9.2 (idea must exist) | — | ideas | GET /api/ideas/:id | IdeaWorkspace, DraggableDivider |
| F-1.2-4 | Section Visibility/Locking | F-1.1, F-1.5 | — | ideas (state) | — | SectionManager |
| F-1.5 | Idea Lifecycle | F-1.1 | F-4.10 (submit) | ideas (state), review_timeline_entries | PATCH /api/ideas/:id | StateBadge |
| F-1.6 | Inline Title Editing | F-1.1 | F-2.3 (AI title) | ideas (title, title_manually_edited) | PATCH /api/ideas/:id | InlineTitle |
| F-1.7 | UUID-Based Routing | F-1.1 | — | ideas (id) | — | Router config |
| F-2.1 | Agent Modes | F-1.1 | F-2.4 (decision layer) | ideas (agent_mode) | PATCH /api/ideas/:id | AgentModeDropdown |
| F-2.2 | Language Detection | AI service, F-2.1 | — | chat_messages, users | — | — (AI internal) |
| F-2.3 | Title Generation | AI service, F-1.6 | — | ideas (title) | — | TitleAnimation |
| F-2.4 | Decision Layer | AI service, F-2.1 | F-2.7 (reactions) | — | — | — (AI internal) |
| F-2.5 | Multi-User Awareness | AI service, F-6.4 | — | chat_messages, users | — | — (AI internal) |
| F-2.6 | Board Item References | F-3.1 (board exists), Chat | — | chat_messages, board_nodes | — | BoardRefLink |
| F-2.7 | AI Reactions | AI service, Chat | — | ai_reactions | — | AIReaction |
| F-2.8 | User Reactions | Chat messages exist | — | user_reactions | POST/DELETE /api/.../reactions | ReactionButton |
| F-2.9 | @Mentions System | Chat, F-6.3 (presence) | F-12.1 (notifications) | chat_messages, notifications | — | MentionSuggestions |
| F-2.10 | AI Response Timing | AI service | — | admin_parameters (debounce_timer) | — | — (AI internal) |
| F-2.11 | Rate Limiting | Chat, AI service | — | admin_parameters (chat_message_cap) | — | RateLimitBanner |
| F-2.12 | AI Processing Indicator | AI service, WebSocket | — | — (UI state) | — | ProcessingIndicator |
| F-2.13 | Full State Knowledge | AI service, Chat, Board | — | chat_messages, board_nodes, chat_context_summaries | — | — (AI internal) |
| F-2.14 | Long Conversation Support | F-2.13, Context Compression agent | — | chat_context_summaries | GET /api/ideas/:id/context-window | WorkingMemoryIndicator |
| F-2.15 | Company Context Awareness | Context Agent, RAG pipeline | F-11.2 (admin context) | facilitator_context_bucket, context_agent_bucket, context_chunks | — | DelegationMessage |
| F-2.16 | Company Context Management | F-11.2 | — | facilitator_context_bucket, context_agent_bucket | PUT /api/admin/ai-context/* | — (Admin Panel) |
| F-2.17 | AI Board Content Rules | Board Agent, F-3.1 | — | board_nodes, board_connections | — | — (AI internal) |
| F-3.1 | Node Types | F-1.1 (workspace) | — | board_nodes | POST /api/ideas/:id/board/nodes | BoxNode, GroupNode, FreeTextNode |
| F-3.2 | Board Interactions | F-3.1 | — | board_nodes, board_connections | PATCH, DELETE endpoints | ReactFlow canvas |
| F-3.3 | Board UI | F-3.1 | — | — | — | MiniMap, ZoomControls, BoardToolbar |
| F-3.4 | AI Modification Indicators | F-3.1, AI service | — | board_nodes (ai_modified_indicator) | — | AIBadge |
| F-3.5 | Multi-User Board Editing | F-3.1, WebSocket | — | board_nodes | — | SelectionHighlight |
| F-3.6 | Board Sync | F-3.5, WebSocket | — | board_nodes, board_connections | REST + WS | — |
| F-3.7 | Undo/Redo | F-3.2 | — | — (frontend Redux) | — | UndoRedoButtons |
| F-3.8 | Board Item Reference Action | F-3.1, Chat | — | board_nodes, chat_messages | — | ReferenceButton |
| F-4.1 | BRD Generation | Summarizing AI, Chat, Board | F-2.15 (context) | brd_drafts | gRPC TriggerBrdGeneration | — |
| F-4.2 | No Information Fabrication | F-4.1 | — | — | — | — (AI guardrail) |
| F-4.3 | BRD Generation Trigger | F-4.1, F-4.5 (Review tab) | — | brd_drafts | POST /api/ideas/:id/brd/generate | GenerateButton |
| F-4.4 | Per-Section Editing & Lock | F-4.1 | — | brd_drafts (section_locks) | PATCH /api/ideas/:id/brd | BrdSectionEditor |
| F-4.5 | Review Tab | F-1.1, F-4.1 | F-4.7 (PDF) | brd_drafts, brd_versions | — | ReviewTabPanel |
| F-4.6 | Review Section | F-1.5 (submitted), F-4.7 | F-4.11 (reviewers) | brd_versions, review_timeline_entries, review_assignments | — | ReviewSection |
| F-4.7 | Document Versioning | F-4.1, PDF service | — | brd_versions | POST /api/ideas/:id/submit | — |
| F-4.8 | Document Readiness | Summarizing AI | — | brd_drafts (readiness_evaluation) | — | ReadinessIndicator |
| F-4.9 | Allow Info Gaps | F-4.1 | — | brd_drafts (allow_information_gaps) | — | GapsToggle |
| F-4.10 | Reviewer Assignment | F-1.5, F-10.1 | — | review_assignments, notifications | POST /api/ideas/:id/submit | ReviewerSelect |
| F-4.11 | Multiple Reviewers | F-4.10 | — | review_assignments | — | — |
| F-4.12 | Similar Ideas in Review | F-5.2, F-5.3 | — | idea_keywords, ideas | GET /api/ideas/:id/review/similar | SimilarIdeasPanel |
| F-5.1 | Keyword Generation | Keyword Agent, AI service | — | idea_keywords | — | — (AI background) |
| F-5.2 | Background Keyword Matching | F-5.1, Celery worker | — | idea_keywords, idea_embeddings | — | — (background) |
| F-5.3 | AI Deep Comparison | F-5.2, Deep Comparison agent | — | — | — | — (AI background) |
| F-5.4 | State-Aware Match Behavior | F-5.3, F-1.5 | — | ideas (state), merge_requests | — | — |
| F-5.5 | Merge Flow | F-5.4, Merge Synthesizer | — | ideas, merge_requests, chat_messages, board_nodes | POST /api/merge-requests | MergeUI |
| F-5.6 | Merge Request UI | F-5.5 | — | merge_requests, notifications | — | MergeRequestBanner |
| F-5.7 | Permanent Dismissal | F-5.5 | — | merge_requests (status=declined) | — | — |
| F-5.8 | Manual Merge Request | F-5.5 | — | merge_requests | POST /api/merge-requests | ManualMergeDialog |
| F-6.1 | Session-Level Connection | WebSocket infrastructure | — | — | /ws/?token=jwt | WebSocketProvider |
| F-6.2 | Offline Banner | F-6.1 | — | — | — | OfflineBanner |
| F-6.3 | Presence Tracking | F-6.1 | — | — (ephemeral) | — | PresenceIndicators |
| F-6.4 | Multi-User Collaboration | F-6.1, Chat, Board | — | chat_messages, board_nodes | — | — |
| F-6.5 | Offline Behavior | F-6.1 | — | — | — | — |
| F-6.6 | Connection State Indicator | F-6.1 | — | — | — | ConnectionIndicator |
| F-8.1 | Visibility Modes | F-1.1 | F-8.2 (invites) | ideas (visibility) | PATCH /api/ideas/:id | — |
| F-8.2 | Invite Flow | F-8.1, User directory | — | collaboration_invitations, notifications | POST /api/ideas/:id/collaborators/invite | InviteDialog |
| F-8.3 | Read-Only Link Sharing | F-8.1, Auth | — | ideas (share_link_token) | POST /api/ideas/:id/share-link | ShareLinkButton |
| F-8.4 | Collaborator Management | F-8.2 | — | idea_collaborators, collaboration_invitations | DELETE, POST endpoints | CollaboratorDropdown |
| F-10.1 | Review Page Access | F-7.1 (auth + roles) | — | — | — | ReviewPage |
| F-10.2 | Categorized Idea Lists | F-10.1, F-1.5 (states) | — | ideas, review_assignments | GET /api/reviews | ReviewListGroups |
| F-10.3 | Self-Assignment | F-10.2 | — | review_assignments | POST /api/reviews/:id/assign | AssignButton |
| F-10.4 | Conflict of Interest | F-10.3 | — | ideas (owner_id), review_assignments | — | — (backend validation) |
| F-11.1 | Admin Panel Layout | F-7.1 (auth + admin role) | — | — | — | AdminPanel |
| F-11.2 | AI Context Tab | F-11.1 | RAG pipeline | facilitator_context_bucket, context_agent_bucket | PUT /api/admin/ai-context/* | ContextEditor |
| F-11.3 | Parameters Tab | F-11.1 | — | admin_parameters | GET/PUT /api/admin/parameters | ParameterForm |
| F-11.4 | Monitoring Tab | F-11.1, F-11.5 | — | monitoring_alert_configs | GET /api/admin/monitoring/* | MonitoringDashboard |
| F-11.5 | Backend Monitoring Service | Celery, gRPC health checks | — | monitoring_alert_configs | — | — (background) |
| F-11.6 | Users Tab | F-11.1 | — | users | GET /api/admin/users/search | UserSearchPanel |
| F-12.1 | Notification Bell | F-7.1, WebSocket | — | notifications | GET /api/notifications | NotificationBell |
| F-12.2 | Toast Notifications | Frontend scaffold | — | — (transient) | — | ToastContainer |
| F-12.3 | Invitation Banner | F-8.2, F-1.1 | — | collaboration_invitations | — | InvitationBanner |
| F-12.4 | Merge Request Banner | F-5.5, F-1.1 | — | merge_requests | — | MergeRequestBanner |
| F-12.5 | All Notification Events | F-12.1, Notification service | — | notifications | — | — |
| F-13.1-3 | Email Notification Prefs | F-12.1 | — | users (email_notification_preferences) | PUT /api/users/me/notification-preferences | EmailPrefsModal |
| F-14.1 | Universal Error Pattern | Frontend scaffold | — | — | — | ErrorToast, ErrorLogModal |
| F-15.1-3 | Idle State | F-6.1 | — | admin_parameters | — | IdleDetector |

## Dependency Chains (Critical Paths)

### Chain 1: Core Brainstorming (Longest Critical Path)
```
Infrastructure → Auth Bypass → Landing Page → Idea Creation
  → Workspace Layout → Chat Messages → WebSocket/Real-Time
    → Digital Board → AI Service + Facilitator → Board Agent
      → AI Responses + Reactions + Title Generation
```

### Chain 2: Review & BRD
```
Chat + Board (content exists) → Summarizing AI → BRD Generation
  → Review Tab UI → PDF Service → Document Versioning
    → Submit for Review → Review Page → Review Actions
      → Review Timeline → State Transitions → Notifications
```

### Chain 3: Similarity & Merge
```
AI Facilitation (keywords generated) → Keyword Agent → Idea Embeddings
  → Background Matching (Celery) → Deep Comparison Agent
    → Similarity Notification → Merge Request UI
      → Merge Synthesizer Agent → New Merged Idea
```

### Chain 4: AI Context Pipeline
```
Admin Panel (AI Context tab) → Context Agent Bucket Update
  → Chunking + Embedding (RAG indexing) → context_chunks table
    → Facilitator delegates → Context Agent (RAG retrieval)
      → Second Facilitator pass with findings
```

### Chain 5: Notification Pipeline
```
Any triggering event (submit, review, invite, merge, etc.)
  → Core publishes event to message broker
    → Notification service consumes event
      → Creates persistent notification (via Gateway gRPC)
      → Sends email (if user preference allows)
        → Gateway broadcasts via WebSocket → Bell updates
```

## Shared Components (Cross-Cutting)

| Component | Used By Features | Must Exist Before | Source |
|-----------|-----------------|-------------------|--------|
| Global Navbar | All pages | M2 | design-system.md, page-layouts.md |
| Theme System (CSS variables, dark class) | All components | M2 | tech-stack.md, design-system.md |
| i18n (react-i18next) | All user-facing text | M2 | FA-16, nonfunctional.md |
| WebSocket Provider | Chat, Board, Presence, Notifications | M3 | FA-6, tech-stack.md |
| Toast Notification System | Error handling, all user actions | M2 | FA-12.2, FA-14.1 |
| Error Handling Pattern | All API calls, AI processing | M2 | FA-14.1 |
| Auth Context (MSAL/bypass) | All authenticated pages | M1 | FA-7, tech-stack.md |
| Redux Store (board undo/redo, WS state, UI state) | Board, WebSocket, Layout | M3 | tech-stack.md |
| TanStack Query (server state) | All data fetching | M1 | tech-stack.md |
| gRPC client utilities | All gateway-to-service calls | M1 | api-design.md |
| Message broker publisher | All event-driven flows | M1 | tech-stack.md |
| Factory-boy factories | All backend tests | M1 | testing-strategy.md |
| Frontend test helpers | All frontend tests | M1 | test-plan.md |

## AI Dependencies

| AI Feature | Infrastructure Required | Depends On Features | Source |
|-----------|----------------------|---------------------|--------|
| Facilitator Agent | AI service + SK + Azure OpenAI + Core gRPC | Chat messages, Board state, Idea metadata | agent-architecture.md §3.1 |
| Board Agent | AI service + SK | Facilitator (receives instructions), Board nodes exist | agent-architecture.md §3.2 |
| Context Agent | RAG pipeline (context_chunks + pgvector) | Admin context bucket populated, Facilitator delegates | agent-architecture.md §3.3 |
| Context Extension | Core gRPC GetFullChatHistory | Long conversation exists, Facilitator delegates | agent-architecture.md §3.4 |
| Summarizing AI | AI service, Chat + Board content | Idea has brainstorming content | agent-architecture.md §3.5 |
| Keyword Agent | AI service (cheap tier) | Chat + Board content exists | agent-architecture.md §3.6 |
| Deep Comparison | AI service, Background matching | Two ideas with keyword/vector overlap | agent-architecture.md §3.7 |
| Context Compression | AI service (cheap tier) | Long conversation (context > threshold) | agent-architecture.md §3.8 |
| Merge Synthesizer | AI service, Board Agent | Both owners accept merge request | agent-architecture.md §3.9 |
| RAG Indexing Pipeline | pgvector, text-embedding-3-small | Admin updates context_agent_bucket | agent-architecture.md §6.3 |
| Idea Embedding Pipeline | pgvector, text-embedding-3-small | Keyword Agent runs after chat processing | agent-architecture.md §6.4 |

## Circular Dependencies

No true circular dependencies exist. The closest is:

1. **Facilitator ↔ Board Agent:** Facilitator issues board instructions → Board Agent executes. This is a one-directional delegation within a single processing cycle, not circular.

2. **Facilitator ↔ Context Agent/Extension:** Facilitator delegates → specialist runs → second Facilitator pass. This is a two-pass pipeline, not circular — each pass is independent.

3. **Chat Processing → Keywords → Similarity → Merge → New Idea → Chat Processing:** This chain creates new ideas from merges, which then have their own chat processing. But each idea is independent — no circular dependency, just a lifecycle that creates new entities.

4. **Admin Parameters ↔ All Services:** Parameters are read-only by services, write-only by admins. No circular dependency.
