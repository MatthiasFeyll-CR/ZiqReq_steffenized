# Traceability Matrix

## Feature → Role → Page → Entity Map

| Feature ID | Feature Name | Roles Involved | Pages Used | Entities Affected |
|-----------|-------------|----------------|-----------|-------------------|
| F-1.1 | Project Page Layout | User, Reviewer (view context) | Project Workspace | Project |
| F-1.2 | Section Visibility | User, Reviewer | Project Workspace | Project (state) |
| F-1.3 | Auto-Scroll on State Transition | User, Reviewer | Project Workspace | Project (state) |
| F-1.4 | Section Locking | User, Reviewer | Project Workspace | Project (state) |
| F-1.5 | Project Lifecycle | User, Reviewer | Project Workspace, Review Page | Project, Review Timeline Entry |
| F-1.6 | Inline Title Editing | User | Project Workspace | Project (title, title_manually_edited) |
| F-1.7 | UUID-Based Routing | User, Reviewer, Admin | Project Workspace | Project (id) |
| F-1.8 | Browser Tab Title | User | Project Workspace | Project (title) |
| F-2.1 | Agent Modes | User | Project Workspace | Project (agent_mode) |
| F-2.2 | Language Detection | User | Project Workspace | Chat Message, User (language preference) |
| F-2.3 | Title Generation | User | Project Workspace | Project (title, title_manually_edited) |
| F-2.4 | Decision Layer | User | Project Workspace | Chat Message, AI Reaction |
| F-2.5 | Multi-User Awareness | User | Project Workspace | Chat Message, User |
| F-2.7 | AI Reactions | User | Project Workspace | AI Reaction, Chat Message |
| F-2.8 | User Reactions | User | Project Workspace | User Reaction, Chat Message |
| F-2.9 | @Mentions System | User | Project Workspace | Chat Message, Notification |
| F-2.10 | AI Response Timing | User | Project Workspace | Chat Message, Admin Parameter |
| F-2.11 | Rate Limiting | User, Admin | Project Workspace, Admin Panel | Chat Message, Admin Parameter |
| F-2.12 | AI Processing Indicator | User | Project Workspace | — (UI state only) |
| F-2.13 | Full State Knowledge | User | Project Workspace | Chat Message, Requirements Structure, Chat Context Summary |
| F-2.14 | Long Conversation Support | User, Admin | Project Workspace, Admin Panel | Chat Message, Chat Context Summary |
| F-2.15 | Company Context Awareness | User | Project Workspace | Chat Message, Facilitator Context, Detailed Company Context, Project Type Context |
| F-2.16 | Company Context Management | Admin | Admin Panel | Facilitator Context, Detailed Company Context, Software Context, Non-Software Context |
| F-4.1 | Requirements Document Generation | User | Project Workspace (Review tab) | Requirements Document Draft, Chat Message, Requirements Structure |
| F-4.2 | No Information Fabrication | User | Project Workspace (Review tab) | Requirements Document Draft |
| F-4.3 | Requirements Document Generation Trigger | User | Project Workspace (Review tab) | Requirements Document Draft |
| F-4.4 | Per-Section Editing & Lock | User | Project Workspace (Review tab) | Requirements Document Draft (section_locks) |
| F-4.5 | Review Tab | User | Project Workspace (Review tab) | Requirements Document Draft, Requirements Document Version |
| F-4.6 | Review Section | User, Reviewer | Project Workspace (Review section) | Requirements Document Version, Review Timeline Entry, Review Assignment |
| F-4.7 | Document Versioning | User, Reviewer | Project Workspace | Requirements Document Version |
| F-4.8 | Document Readiness Evaluation | User | Project Workspace (Review tab) | Requirements Document Draft (readiness_evaluation) |
| F-4.9 | Allow Information Gaps Toggle | User | Project Workspace (Review tab) | Requirements Document Draft (allow_information_gaps) |
| F-4.10 | Reviewer Assignment on Submit | User, Reviewer | Project Workspace, Review Page | Review Assignment, Notification |
| F-4.11 | Multiple Reviewers | User, Reviewer | Project Workspace, Review Page | Review Assignment, Review Timeline Entry |
| F-6.1 | Session-Level Connection | User | All authenticated pages | — (infrastructure) |
| F-6.2 | Offline Banner | User | All authenticated pages | — (UI state only) |
| F-6.3 | Presence Tracking | User | Project Workspace | User |
| F-6.4 | Multi-User Collaboration | User | Project Workspace | Chat Message, Requirements Structure |
| F-6.5 | Offline Behavior | User | Project Workspace | — (UI state only) |
| F-6.6 | Connection State Indicator | User | All authenticated pages | — (UI state only) |
| F-7.1 | Development Auth Bypass | User, Reviewer, Admin | All pages | User |
| F-7.2 | Production Authentication | User, Reviewer, Admin | Login, All authenticated pages | User |
| F-8.1 | Visibility Modes | User | Project Workspace | Project (visibility) |
| F-8.2 | Invite Flow | User | Project Workspace, Landing Page | Collaboration Invitation, Notification |
| F-8.3 | Read-Only Link Sharing | User | Project Workspace | Project (share_link) |
| F-8.4 | Collaborator Management | User | Project Workspace | Collaboration Invitation, Project |
| F-9.1 | Landing Page Structure | User | Landing Page | Project, Collaboration Invitation |
| F-9.2 | Project Creation | User | Landing Page, Project Workspace | Project, Chat Message |
| F-9.3 | Soft Delete | User | Landing Page | Project (deleted_at) |
| F-9.4 | Search & Filter | User | Landing Page | Project |
| F-10.1 | Review Page Access | Reviewer | Review Page | — (access control) |
| F-10.2 | Categorized Project Lists | Reviewer | Review Page | Project, Review Assignment |
| F-10.3 | Self-Assignment | Reviewer | Review Page | Review Assignment |
| F-10.4 | Conflict of Interest | Reviewer | Review Page | Project, Review Assignment |
| F-11.1 | Admin Panel Layout | Admin | Admin Panel | — |
| F-11.2 | AI Context Tab | Admin | Admin Panel | Facilitator Context, Detailed Company Context, Software Context, Non-Software Context |
| F-11.3 | Parameters Tab | Admin | Admin Panel | Admin Parameter |
| F-11.4 | Monitoring Tab | Admin | Admin Panel | Monitoring Alert Config |
| F-11.5 | Backend Monitoring Service | Admin | — (background) | Monitoring Alert Config |
| F-11.6 | Users Tab | Admin | Admin Panel | User |
| F-12.1 | Notification Bell | User, Reviewer, Admin | All authenticated pages (navbar) | Notification |
| F-12.2 | Toast Notifications | User, Reviewer, Admin | All authenticated pages | — (transient UI) |
| F-12.3 | Floating Banner (Invitation) | User | Project Workspace | Collaboration Invitation |
| F-12.5 | All Notification Events | User, Reviewer, Admin | Various | Notification |
| F-13.1 | Email Notification Settings | User, Reviewer, Admin | Floating window (navbar) | User (email notification preferences) |
| F-13.2 | Grouped Toggles | User, Reviewer, Admin | Floating window (navbar) | User (email notification preferences) |
| F-13.3 | Role-Based Notification Groups | User, Reviewer, Admin | Floating window (navbar) | User (email notification preferences) |
| F-14.1 | Universal Error Pattern | User, Reviewer, Admin | All authenticated pages | — (UI pattern) |
| F-15.1 | Idle Detection | User | All authenticated pages | — (connection state) |
| F-15.2 | Connection Disconnect on Idle | User | All authenticated pages | — (connection state) |
| F-15.3 | Return from Idle | User | All authenticated pages | — (connection state) |
| F-16.1 | Available Languages | User, Reviewer, Admin | All pages | User (language preference) |
| F-16.2 | Language Switcher | User, Reviewer, Admin | All authenticated pages (navbar) | User (language preference) |
| F-16.3 | i18n Scope | User, Reviewer, Admin | All pages | — |
| F-16.4 | AI Language | User | Project Workspace | Chat Message, User (language preference) |
| F-17.1 | Available Themes | User, Reviewer, Admin | All pages | User (theme preference) |
| F-17.2 | Theme Switcher | User, Reviewer, Admin | All authenticated pages (navbar) | User (theme preference) |
| F-17.3 | System Preference Detection | User, Reviewer, Admin | All pages | User (theme preference) |
| F-17.4 | Theme Scope | User, Reviewer, Admin | All pages | — |
| F-17.5 | Brand Assets | User, Reviewer, Admin | All pages | — |

## Coverage Check

### Features without a page (potential gap)
- **F-11.5 (Backend Monitoring Service)** — Background service. Correct: results surface via Admin Panel monitoring tab and email alerts.

No gaps identified — all background processes have user-facing surfaces for their outputs.

### Pages without features (potential dead page)
- **Login Page** — Serves F-7.2 (Production Authentication). Not dead.

No dead pages identified.

### Entities without features (potential orphan)
- **Monitoring Alert Config** — Serves F-11.4 (Monitoring Tab, alert recipient configuration). Not orphaned.

No orphaned entities identified.

## Downstream Delegation Summary

The following items were moved from the requirements feature catalog to downstream specialists. This table provides a quick reference for all delegated items:

| Downstream Specialist | Delegation Count | Key Areas |
|----------------------|-----------------|-----------|
| **AI Engineer** | 7 | AI processing pipeline (F-2.10), context management (F-2.14), company context retrieval architecture (F-2.15), requirements document generation agent (F-4.1), AI-specific admin parameters, Chat Context Summary internals, project type-specific context handling |
| **Software Architect** | 5 | PDF generation service (F-4.7), real-time transport (F-6.1), error handling infrastructure (F-14.1), operational admin parameters, technology stack review |
| **UI/UX Designer** | 1 | Accessibility visual specs (NFR-A2 focus rings, animation behaviors, accessible palette) |

## Notes

- All 63 features map to at least one role, page, and entity (or are correctly identified as background/infrastructure).
- The traceability matrix reflects the refactoring plan: "Idea" → "Project", "BRD" → "Requirements Document", Board features (FA-3) removed, Similarity/Merge features (FA-5) removed.
- Removed features: F-2.6 (Board Item References), F-2.17 (AI Board Content Rules), F-3.1-F-3.8 (all Board features), F-4.12 (Similar Ideas in Review), F-5.1-F-5.8 (all Similarity/Merge features), F-12.4 (Merge Request Banner).
- Updated entities: Board Node, Board Connection, Idea Keywords, and Merge Request removed. BRD Draft/Version replaced with Requirements Document Draft/Version. Project Type Context added.
- Feature count reduced from 107 to 63 after removing board and similarity/merge functionality.
- Downstream delegation notes are embedded inline in `features.md`, `data-entities.md`, `nonfunctional.md`, and `constraints.md` using the `⚙️ DOWNSTREAM →` marker pattern.
