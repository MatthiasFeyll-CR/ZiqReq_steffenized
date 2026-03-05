# Traceability Matrix

## Feature → Role → Page → Entity Map

| Feature ID | Feature Name | Roles Involved | Pages Used | Entities Affected |
|-----------|-------------|----------------|-----------|-------------------|
| F-1.1 | Idea Page Layout | User, Reviewer (view context) | Idea Workspace | Idea |
| F-1.2 | Section Visibility | User, Reviewer | Idea Workspace | Idea (state) |
| F-1.3 | Auto-Scroll on State Transition | User, Reviewer | Idea Workspace | Idea (state) |
| F-1.4 | Section Locking | User, Reviewer | Idea Workspace | Idea (state) |
| F-1.5 | Idea Lifecycle | User, Reviewer | Idea Workspace, Review Page | Idea, Review Timeline Entry |
| F-1.6 | Inline Title Editing | User | Idea Workspace | Idea (title, title_manually_edited) |
| F-1.7 | UUID-Based Routing | User, Reviewer, Admin | Idea Workspace | Idea (id) |
| F-1.8 | Browser Tab Title | User | Idea Workspace | Idea (title) |
| F-2.1 | Agent Modes | User | Idea Workspace | Idea (agent_mode) |
| F-2.2 | Language Detection | User | Idea Workspace | Chat Message, User (language preference) |
| F-2.3 | Title Generation | User | Idea Workspace | Idea (title, title_manually_edited) |
| F-2.4 | Decision Layer | User | Idea Workspace | Chat Message, AI Reaction |
| F-2.5 | Multi-User Awareness | User | Idea Workspace | Chat Message, User |
| F-2.6 | Board Item References in Chat | User | Idea Workspace | Chat Message, Board Node |
| F-2.7 | AI Reactions | User | Idea Workspace | AI Reaction, Chat Message |
| F-2.8 | User Reactions | User | Idea Workspace | User Reaction, Chat Message |
| F-2.9 | @Mentions System | User | Idea Workspace | Chat Message, Notification |
| F-2.10 | AI Response Timing | User | Idea Workspace | Chat Message, Admin Parameter |
| F-2.11 | Rate Limiting | User, Admin | Idea Workspace, Admin Panel | Chat Message, Admin Parameter |
| F-2.12 | AI Processing Indicator | User | Idea Workspace | — (UI state only) |
| F-2.13 | Full State Knowledge | User | Idea Workspace | Chat Message, Board Node, Chat Context Summary |
| F-2.14 | Long Conversation Support | User, Admin | Idea Workspace, Admin Panel | Chat Message, Chat Context Summary |
| F-2.15 | Company Context Awareness | User | Idea Workspace | Chat Message, Facilitator Context, Detailed Company Context |
| F-2.16 | Company Context Management | Admin | Admin Panel | Facilitator Context, Detailed Company Context |
| F-2.17 | AI Board Content Rules | User | Idea Workspace | Board Node, Board Connection |
| F-3.1 | Node Types | User | Idea Workspace | Board Node |
| F-3.2 | Board Interactions | User | Idea Workspace | Board Node, Board Connection |
| F-3.3 | Board UI | User | Idea Workspace | Board Node, Board Connection |
| F-3.4 | AI Modification Indicators | User | Idea Workspace | Board Node (ai_modified_indicator) |
| F-3.5 | Multi-User Board Editing | User | Idea Workspace | Board Node |
| F-3.6 | Board Sync | User | Idea Workspace | Board Node, Board Connection |
| F-3.7 | Undo/Redo | User | Idea Workspace | Board Node, Board Connection |
| F-3.8 | Board Item Reference Action | User | Idea Workspace | Board Node, Chat Message |
| F-4.1 | BRD Generation | User | Idea Workspace (Review tab) | BRD Draft, Chat Message, Board Node |
| F-4.2 | No Information Fabrication | User | Idea Workspace (Review tab) | BRD Draft |
| F-4.3 | BRD Generation Trigger | User | Idea Workspace (Review tab) | BRD Draft |
| F-4.4 | Per-Section Editing & Lock | User | Idea Workspace (Review tab) | BRD Draft (section_locks) |
| F-4.5 | Review Tab | User | Idea Workspace (Review tab) | BRD Draft, BRD Version |
| F-4.6 | Review Section | User, Reviewer | Idea Workspace (Review section) | BRD Version, Review Timeline Entry, Review Assignment |
| F-4.7 | Document Versioning | User, Reviewer | Idea Workspace | BRD Version |
| F-4.8 | Document Readiness Evaluation | User | Idea Workspace (Review tab) | BRD Draft (readiness_evaluation) |
| F-4.9 | Allow Information Gaps Toggle | User | Idea Workspace (Review tab) | BRD Draft (allow_information_gaps) |
| F-4.10 | Reviewer Assignment on Submit | User, Reviewer | Idea Workspace, Review Page | Review Assignment, Notification |
| F-4.11 | Multiple Reviewers | User, Reviewer | Idea Workspace, Review Page | Review Assignment, Review Timeline Entry |
| F-4.12 | Similar Ideas in Review Section | Reviewer | Idea Workspace (Review section) | Idea Keywords, Idea |
| F-5.1 | Keyword Generation | User | Idea Workspace | Idea Keywords |
| F-5.2 | Background Keyword Matching | — (automated) | — | Idea Keywords |
| F-5.3 | AI Deep Comparison | — (automated) | — | Idea Keywords, Idea |
| F-5.4 | State-Aware Match Behavior | User | Idea Workspace | Idea, Merge Request |
| F-5.5 | Merge Flow | User | Idea Workspace | Idea, Merge Request, Chat Message, Board Node |
| F-5.6 | Merge Request UI | User | Idea Workspace | Merge Request, Notification |
| F-5.7 | Permanent Dismissal | User | Idea Workspace | Merge Request |
| F-5.8 | Manual Merge Request | User | Idea Workspace | Merge Request, Idea Keywords |
| F-6.1 | Session-Level Connection | User | All authenticated pages | — (infrastructure) |
| F-6.2 | Offline Banner | User | All authenticated pages | — (UI state only) |
| F-6.3 | Presence Tracking | User | Idea Workspace | User |
| F-6.4 | Multi-User Collaboration | User | Idea Workspace | Chat Message, Board Node |
| F-6.5 | Offline Behavior | User | Idea Workspace | — (UI state only) |
| F-6.6 | Connection State Indicator | User | All authenticated pages | — (UI state only) |
| F-7.1 | Development Auth Bypass | User, Reviewer, Admin | All pages | User |
| F-7.2 | Production Authentication | User, Reviewer, Admin | Login, All authenticated pages | User |
| F-8.1 | Visibility Modes | User | Idea Workspace | Idea (visibility) |
| F-8.2 | Invite Flow | User | Idea Workspace, Landing Page | Collaboration Invitation, Notification |
| F-8.3 | Read-Only Link Sharing | User | Idea Workspace | Idea (share_link) |
| F-8.4 | Collaborator Management | User | Idea Workspace | Collaboration Invitation, Idea |
| F-9.1 | Landing Page Structure | User | Landing Page | Idea, Collaboration Invitation |
| F-9.2 | Idea Creation | User | Landing Page, Idea Workspace | Idea, Chat Message |
| F-9.3 | Soft Delete | User | Landing Page | Idea (deleted_at) |
| F-9.4 | Search & Filter | User | Landing Page | Idea |
| F-10.1 | Review Page Access | Reviewer | Review Page | — (access control) |
| F-10.2 | Categorized Idea Lists | Reviewer | Review Page | Idea, Review Assignment |
| F-10.3 | Self-Assignment | Reviewer | Review Page | Review Assignment |
| F-10.4 | Conflict of Interest | Reviewer | Review Page | Idea, Review Assignment |
| F-11.1 | Admin Panel Layout | Admin | Admin Panel | — |
| F-11.2 | AI Context Tab | Admin | Admin Panel | Facilitator Context, Detailed Company Context |
| F-11.3 | Parameters Tab | Admin | Admin Panel | Admin Parameter |
| F-11.4 | Monitoring Tab | Admin | Admin Panel | Monitoring Alert Config |
| F-11.5 | Backend Monitoring Service | Admin | — (background) | Monitoring Alert Config |
| F-11.6 | Users Tab | Admin | Admin Panel | User |
| F-12.1 | Notification Bell | User, Reviewer, Admin | All authenticated pages (navbar) | Notification |
| F-12.2 | Toast Notifications | User, Reviewer, Admin | All authenticated pages | — (transient UI) |
| F-12.3 | Floating Banner (Invitation) | User | Idea Workspace | Collaboration Invitation |
| F-12.4 | Merge Request Banner | User | Idea Workspace | Merge Request |
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
| F-16.4 | AI Language | User | Idea Workspace | Chat Message, User (language preference) |
| F-17.1 | Available Themes | User, Reviewer, Admin | All pages | User (theme preference) |
| F-17.2 | Theme Switcher | User, Reviewer, Admin | All authenticated pages (navbar) | User (theme preference) |
| F-17.3 | System Preference Detection | User, Reviewer, Admin | All pages | User (theme preference) |
| F-17.4 | Theme Scope | User, Reviewer, Admin | All pages | — |
| F-17.5 | Brand Assets | User, Reviewer, Admin | All pages | — |

## Coverage Check

### Features without a page (potential gap)
- **F-5.2 (Background Keyword Matching)** — Automated background process, no user-facing page. Correct: runs invisibly.
- **F-5.3 (AI Deep Comparison)** — Automated background process. Correct: results surface via notifications (F-5.4, F-5.6).
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
| **AI Engineer** | 8 | AI processing pipeline (F-2.10), context management (F-2.14), company context retrieval architecture (F-2.15), AI board rules enforcement (F-2.17), BRD generation agent (F-4.1), keyword generation strategy (F-5.1), deep comparison agent (F-5.3), AI-specific admin parameters, Chat Context Summary internals |
| **Software Architect** | 6 | Board sync protocol (F-3.6), undo/redo storage (F-3.7), PDF generation service (F-4.7), keyword matching service (F-5.2), real-time transport (F-6.1), error handling infrastructure (F-14.1), operational admin parameters, technology stack review |
| **UI/UX Designer** | 1 | Accessibility visual specs (NFR-A2 focus rings, animation behaviors, accessible palette) |

## Notes

- All 75 features map to at least one role, page, and entity (or are correctly identified as background/infrastructure).
- The traceability matrix uses the new feature numbering from this requirements iteration (FA-1 through FA-17, renumbered from the old 18-area catalog).
- Downstream delegation notes are embedded inline in `features.md`, `data-entities.md`, `nonfunctional.md`, and `constraints.md` using the `⚙️ DOWNSTREAM →` marker pattern.
