# Dependency Analysis

## Infrastructure Layer (must exist first)

| Component | Type | Why First | Source |
|-----------|------|-----------|--------|
| Auth bypass middleware (F-7.1) | Security | All routes protected; dev users needed for all testing | features.md FA-7 |
| User shadow table + sync | Data | Every entity references users via FK | data-model.md users |
| Database schema (all 22 tables) | Data | Django migrations create all tables; FKs require order | data-model.md |
| gRPC proto definitions | Contract | Gateway <-> Core <-> AI communication contract | api-design.md gRPC |
| Message broker queues + exchanges | Infrastructure | Event-driven architecture requires broker | tech-stack.md |
| Redis channel layer | Infrastructure | Django Channels pub/sub backend | tech-stack.md |
| Admin parameters seed data | Data | Many features read runtime parameters | data-model.md admin_parameters |
| Shared UI primitives (16 components) | Frontend | Every page depends on buttons, cards, inputs, etc. | component-inventory.md |
| Layout components (Navbar, PageShell) | Frontend | All pages use the same shell | component-inventory.md |
| Theme system (CSS variables) | Frontend | All components reference theme tokens | design-system.md |

## Feature Dependency Map

| Feature ID | Feature Name | Hard Dependencies | Soft Dependencies | Data Tables | API Endpoints | Components |
|-----------|-------------|-------------------|-------------------|-------------|---------------|------------|
| FA-7 | Authentication | None | — | users | POST /api/auth/validate, POST /api/auth/dev-switch | LoginPage, DevUserSwitcher, AuthenticatedLayout |
| FA-9 | Landing Page | FA-7 | FA-12 (notifications) | ideas, collaboration_invitations | GET /api/ideas, POST /api/ideas, DELETE /api/ideas/:id | HeroSection, IdeaCard, FilterBar, InvitationCard |
| FA-1 | Idea Workspace | FA-7, FA-9 | FA-6 (real-time) | ideas | GET /api/ideas/:id, PATCH /api/ideas/:id | PanelDivider, ChatPanel, BoardCanvas |
| FA-2 | AI Facilitation | FA-1, FA-3, FA-6 | FA-11 (admin params) | chat_messages, ai_reactions, chat_context_summaries, idea_keywords, idea_embeddings | gRPC TriggerChatProcessing | AIMessageBubble, AIProcessingIndicator |
| FA-3 | Digital Board | FA-1 | FA-6 (sync) | board_nodes, board_connections | POST/GET/PATCH/DELETE /api/ideas/:id/board/* | BoxNode, GroupNode, FreeTextNode, ConnectionEdge, BoardToolbar |
| FA-4 | Review & BRD | FA-2, FA-3 | FA-12 (notifications) | brd_drafts, brd_versions, review_assignments, review_timeline_entries | gRPC TriggerBrdGeneration, POST /api/ideas/:id/submit | PDFPreview, BRDSectionEditor, ReviewTimeline |
| FA-5 | Similarity | FA-2 (keywords) | FA-12 (notifications) | idea_keywords, idea_embeddings, merge_requests | POST /api/ideas/:id/merge-request | SimilarIdeaCard, MergeRequestBanner |
| FA-6 | Real-Time | FA-7 | — | — | WS /ws/?token= | OfflineBanner, PresenceIndicators, ConnectionIndicator |
| FA-8 | Visibility & Sharing | FA-1 | FA-12 (notifications) | idea_collaborators, collaboration_invitations | POST /api/ideas/:id/collaborators/* | CollaboratorModal, InvitationBanner |
| FA-10 | Review Page | FA-4 | — | review_assignments | GET /api/reviews | ReviewCard |
| FA-11 | Admin Panel | FA-7 | FA-2 (AI context) | admin_parameters, facilitator_context_bucket, context_agent_bucket, monitoring_alert_configs | GET/PATCH /api/admin/* | AIContextEditor, ParametersTable, MonitoringDashboard, UserSearch |
| FA-12 | Notifications | FA-7, FA-6 | — | notifications | GET /api/notifications, PATCH /api/notifications/:id | NotificationBell, NotificationPanel, Toast |
| FA-13 | Preferences | FA-12 | — | users (email_notification_preferences) | PATCH /api/users/me/notification-preferences | EmailPreferencesPanel |
| FA-14 | Error Handling | None | — | — | — | ErrorToast, ErrorLogModal |
| FA-15 | Idle State | FA-6 | — | — | WS presence_update | — (connection state) |
| FA-16 | i18n | None | — | — | — | — (react-i18next) |
| FA-17 | Theme | None | — | — | — | — (CSS variables) |

## Dependency Chains (Critical Paths)

### Chain 1: Core Brainstorming Flow (longest)
```
Auth (M1) -> Landing (M2) -> Workspace Layout (M3) -> Board Core (M4) -> Board Advanced (M5)
                                    |                       |
                                    v                       v
                               Chat (M3) ---------> WebSocket (M6) -> AI Chat (M7) -> AI Board/Context (M8)
                                                                                            |
                                                                                            v
                                                                                    BRD Generation (M9) -> Review Workflow (M10)
```

### Chain 2: Similarity & Merge
```
AI Chat (M7) -> Keyword Agent (M8) -> Background Matching (M13) -> Deep Comparison (M13)
                     |                                                      |
                     v                                                      v
             Idea Embeddings (M8) -> Vector Similarity (M13) -------> Merge Flow (M13) -> Advanced Merge (M14)
```

### Chain 3: Admin & Monitoring
```
Auth (M1) -> Admin Layout (M15) -> AI Context Editors (M15) -> Context Re-indexing (M15)
                                         |
                                         v
                                   Parameters (M15) -> Monitoring Service (M15)
```

### Chain 4: Collaboration
```
Auth (M1) -> Workspace (M3) -> WebSocket (M6) -> Collaboration (M11) -> Multi-user Board (M11)
                                                        |
                                                        v
                                                  Notifications (M12)
```

## Shared Components (Cross-Cutting)

| Component | Used By Features | Must Exist Before | Source |
|-----------|-----------------|-------------------|--------|
| Button (6 variants) | All features | M1 | component-specs.md S1 |
| Card (base + variants) | FA-9, FA-10, FA-11 | M1 | component-specs.md S2 |
| Badge (state, role, AI) | FA-9, FA-1, FA-10, FA-11 | M1 | component-specs.md S3 |
| Avatar + Presence dot | FA-6, FA-8, FA-11 | M1 | component-specs.md S9 |
| Toast system | FA-14, FA-12, all error flows | M1 | component-specs.md S11 |
| IdeaCard | FA-9 (Landing), IdeasListFloating, FA-10 (Review) | M2 | component-inventory.md |
| ErrorBoundary | All pages | M1 | component-inventory.md |
| EmptyState | FA-9, FA-10, FA-11, FA-12 | M1 | component-inventory.md |
| Skeleton loading | All pages | M1 | component-specs.md S11.2 |
| Navbar | All authenticated pages | M1 | component-inventory.md |

## AI Dependencies

| AI Feature | Infrastructure Required | Depends On Features | Source |
|-----------|----------------------|---------------------|--------|
| Facilitator (6 tools) | SK kernel, Azure OpenAI, gRPC to Core | Chat messages, Board state, Admin params | agent-architecture.md S3.1 |
| Board Agent (8 tools) | SK kernel, Azure OpenAI, gRPC to Core | Board nodes/connections, Facilitator output | agent-architecture.md S3.2 |
| Context Agent (RAG) | pgvector, text-embedding-3-small, context_chunks | Admin context buckets, Facilitator delegation | agent-architecture.md S3.3 |
| Context Extension | Azure OpenAI (escalated), gRPC GetFullChatHistory | Chat messages, Context Compression | agent-architecture.md S3.4 |
| Summarizing AI | Azure OpenAI, gRPC to Core | Chat + Board + Company context | agent-architecture.md S3.5 |
| Keyword Agent | Azure OpenAI (cheap), gRPC to Core | Chat + Board content | agent-architecture.md S3.6 |
| Deep Comparison | Azure OpenAI, idea summaries | Keyword Agent, Idea embeddings | agent-architecture.md S3.7 |
| Context Compression | Azure OpenAI (cheap) | Chat messages, existing summary | agent-architecture.md S3.8 |
| Merge Synthesizer | Azure OpenAI, Board Agent | Two full idea contexts, merge acceptance | agent-architecture.md S3.9 |
