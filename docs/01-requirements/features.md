# Feature Catalog

## Feature Areas

---

### FA-1: Project Workspace

- **F-1.1:** Project Page Layout — The project page uses a three-step process flow: Define → Structure → Review. Each step is a separate view accessed via ProcessStepper tabs. Define step shows chat + context. Structure step shows RequirementsPanel (60%) + PDFPreviewPanel (40%) in a 60/40 split layout. Review step shows the review workflow (visible after first submit).

- **F-1.2:** Section Visibility — The review section is hidden/inaccessible until the project is submitted for review at least once. Once submitted, both sections persist on the page regardless of current state.

- **F-1.3:** Auto-Scroll on State Transition — The page auto-scrolls to the active section based on project state: Open → requirements assembly (top), In Review → review (bottom), Rejected → requirements assembly (top), Accepted → review (bottom), Dropped → review (bottom). Also triggers when submitting for review and when entering a project page.

- **F-1.4:** Section Locking — Sections lock/unlock based on project state:
  - Open: requirements assembly editable, review hidden.
  - In Review: requirements assembly locked (read-only), review active.
  - Rejected: requirements assembly editable (unlocked for rework), review visible (read-only).
  - Accepted: everything read-only.
  - Dropped: everything read-only.

- **F-1.5:** Project Lifecycle — States: `open`, `in_review`, `accepted`, `dropped`, `rejected`. Transitions:
  - Open → In Review: user submits. Requirements assembly locks, review activates.
  - In Review → Accepted: any reviewer accepts. Everything read-only, owner notified by email.
  - In Review → Dropped: any reviewer drops (mandatory comment). Everything read-only, owner notified by email.
  - In Review → Rejected: any reviewer rejects (mandatory comment). Requirements assembly unlocks for rework, owner notified by email.
  - Rejected → In Review: user resubmits.
  - Accepted → In Review: any reviewer undoes accept (mandatory comment).
  - Dropped → In Review: any reviewer undoes drop (mandatory comment).
  - Rejected → In Review: any reviewer undoes rejection (mandatory comment).
  - Multiple reviewers: any single reviewer can act independently. If conflicting actions occur, latest action wins. All actions and undos with mandatory comments are recorded in the timeline for traceability.
  - No limit on resubmissions. Abuse prevented by reviewer's power to drop.

- **F-1.6:** Inline Title Editing — The project title is editable directly in the workspace (clicking/tapping the title). Manual edits permanently disable AI title generation (see F-2.3). Title changes update the browser tab title dynamically.

- **F-1.7:** UUID-Based Routing — Each project is accessed via `/project/<uuid>`.

- **F-1.8:** Browser Tab Title — Shows the current project name. Updates dynamically on title changes including AI-generated updates.

---

### FA-2: AI Facilitation

- **F-2.1:** Agent Modes — Two modes selectable via a dropdown in the workspace header:
  - Interactive (default): AI processes all inputs and decides autonomously whether to respond.
  - Silent: AI only responds when explicitly triggered with `@ai`.

- **F-2.2:** Language Detection — AI detects the user's language from chat messages and responds in the same language. Initial language (before any messages) follows the project creator's app language setting.

- **F-2.3:** Title Generation — AI automatically generates a short, concise title from the first message. Periodically re-evaluates the title as conversation evolves and updates it when it no longer fits. Permanently disabled once a user manually edits the title. Title changes are animated.

- **F-2.4:** Decision Layer (Interactive Mode) — AI evaluates whether it has value to add before responding. Can decide "no action" — in which case it reacts instead of responding (see F-2.7).

- **F-2.5:** Multi-User Awareness — AI detects which user sent each message. Addresses users by name only when multiple users are collaborating on the same project. In single-user mode, the AI does not address by name.

- **F-2.6:** Requirements Structure Updates — AI can update the requirements structure via tool calls. AI can add, edit, or remove epics and user stories (Software projects) or milestones and work packages (Non-Software projects). Changes are reflected in the Structured Requirements Panel in real-time.

- **F-2.7:** AI Reactions — The AI can react to user messages with three reactions:
  - Thumbs up: "I've seen this, nothing to add" (acknowledges without responding).
  - Thumbs down: Disagreement / rejection.
  - Heart: "Your answer fully clarified my question" (context is now clear).
  - Users cannot react to AI messages. Users respond to AI via chat.

- **F-2.8:** User Reactions — Users can react to other users' messages (not AI messages) with the same three reactions: thumbs up, thumbs down, heart. The AI reads user-to-user reactions as sentiment signals during processing.

- **F-2.9:** @Mentions System — Typing `@` in chat opens a suggestion dropdown listing all users currently in the project and `@ai`. `@username` notifies/addresses that user. `@ai` forces an AI response in any mode.

- **F-2.10:** AI Response Timing — After the last chat message, the system waits a brief configurable period (admin-configurable) before the AI begins processing. This prevents the AI from responding to incomplete thoughts when a user sends multiple rapid messages. If a new message arrives during processing, the AI restarts with the updated state. AI-generated outputs (chat responses, requirements structure modifications, reactions) do not trigger further processing.

> DOWNSTREAM → **AI Engineer**: The old spec defined a debounce timer (default 3s), abort-and-restart processing model, and the rule that AI processes full state (all chat + all requirements structure) on each cycle. Design the processing pipeline, trigger mechanics, and state management approach. See `docs_old/01-requirements/features.md` F-2.10 for the original detailed spec.

- **F-2.11:** Rate Limiting — Admin-configurable chat message cap per project (default: 5). If the cap is reached without the AI completing a processing cycle, chat input is locked for all users on that project. Requirements Panel remains editable — only chat is locked. Counter resets when AI completes processing. Cap is per project, shared across all users.

- **F-2.12:** AI Processing Indicator — "AI is processing" indicator with gentle animation, visible only during chat-triggered processing.

- **F-2.13:** Full State Knowledge — AI has knowledge of the entire project state: all chat messages (or a summarized version of older messages plus recent messages), the complete requirements structure (all epics/stories or milestones/packages), and their current state.

- **F-2.14:** Long Conversation Support — The AI must handle long requirements assembly sessions without degrading in quality. Older chat messages may be summarized to keep the AI effective, but the original messages are always preserved and accessible. The user sees a visual indicator (filling circle) showing how much of the AI's working memory is used, with details available on hover.

> DOWNSTREAM → **AI Engineer**: The old spec defined context window management with automatic compression at a configurable threshold (default 60%), incremental summarization, and on-demand context extension with model escalation for unresolvable references. Design the context management strategy, compression approach, and any model escalation logic. See `docs_old/01-requirements/features.md` F-2.14, F-2.15, F-2.16 for the original detailed specs.

- **F-2.15:** Company Context Awareness — The AI has access to Commerz Real's business context (existing systems, domain terminology, company structure). When the AI needs to research company context during a conversation, it shows a brief placeholder message (e.g., "I'm researching this, I'll get back to you shortly"). Once the answer is ready, the placeholder is visually de-emphasized and the full response appears.

> DOWNSTREAM → **AI Engineer**: The old spec defined a two-bucket architecture (Facilitator Bucket with table of contents + Context Agent Bucket with detailed info) and a delegation flow between a facilitator AI and a specialized context agent. Design the agent architecture, context retrieval strategy, and delegation mechanics. See `docs_old/01-requirements/features.md` F-3.1 through F-3.4 for the original detailed specs.

- **F-2.16:** Company Context Management — Admins maintain the company context information through the Admin Panel (see FA-11). Three separate context areas:
  - Global context: available to all project types (high-level table of contents + detailed structured sections).
  - Software-specific context: available only to Software projects.
  - Non-Software-specific context: available only to Non-Software projects.
  - Updates to context do not retroactively affect in-progress requirements assembly sessions.

- **F-2.17:** AI Requirements Structure Guidelines — When the AI creates or modifies requirements structure, it follows type-specific guidelines:
  - **Software Projects:**
    - Epics represent high-level features or capabilities.
    - User Stories follow the format: "As a [role], I want [capability], so that [benefit]."
    - Each User Story includes acceptance criteria (specific, testable conditions).
    - Stories are prioritized (High, Medium, Low).
  - **Non-Software Projects:**
    - Milestones represent major project phases or deliverables.
    - Work Packages are specific tasks or deliverables within a milestone.
    - Each Work Package includes deliverables, dependencies, and estimated effort.

> DOWNSTREAM → **AI Engineer**: These requirements structure guidelines should be enforced via the facilitator AI's system prompt and tool schemas. Design how the AI agent interacts with the requirements structure (tool schemas, validation rules, update mechanisms). Consider the differences between Software and Non-Software project types.

---

### FA-3: Structured Requirements Panel

- **F-3.1:** Panel Location — Right panel of the project workspace, accessible via the "Requirements" tab.

- **F-3.2:** Software Project Structure — Accordion-style layout displaying Epics and User Stories:
  - Each Epic is an expandable section.
  - User Stories are nested within their parent Epic.
  - Story format: Title, "As a... I want... So that...", Acceptance Criteria (bullet points), Priority badge.
  - Drag-and-drop to reorder Epics and Stories (within their Epic).
  - Inline editing: click to edit any field.
  - Add/remove buttons per Epic and Story.

- **F-3.3:** Non-Software Project Structure — Accordion-style layout displaying Milestones and Work Packages:
  - Each Milestone is an expandable section.
  - Work Packages are nested within their parent Milestone.
  - Package format: Title, Description, Deliverables (bullet points), Dependencies, Effort estimate.
  - Drag-and-drop to reorder Milestones and Packages (within their Milestone).
  - Inline editing: click to edit any field.
  - Add/remove buttons per Milestone and Package.

- **F-3.4:** AI Modification Indicators — When AI creates or modifies requirements items, each affected item shows a visual indicator (e.g., robot badge, highlight). Indicator fades away once the user interacts with the item (acknowledged). Persists if user never interacts.

- **F-3.5:** Multi-User Editing — All users can edit simultaneously. When a user selects/edits an item, it is highlighted for all other users with the user's name displayed. Last write wins for concurrent edits on the same item.

- **F-3.6:** Requirements Sync — Selection highlights (with username) and content changes are broadcast in real-time. Position changes (drag-and-drop reordering) are broadcast on release.

> DOWNSTREAM → **Software Architect**: Design the sync protocol for the requirements structure. Consider real-time awareness (who's editing what) and conflict resolution for concurrent edits. See similar patterns in the old board sync spec (docs_old/01-requirements/features.md F-4.7).

- **F-3.7:** Undo/Redo — Full undo/redo for all requirements structure actions (user and AI). Covers: item creation/deletion, content edits, reordering. Context-aware button labels: "Undo AI Action" / "Redo AI Action" for AI-generated actions, "Undo" / "Redo" for user actions.

> DOWNSTREAM → **Software Architect**: Design the undo/redo state management for the requirements structure. Consider whether history is stored locally or persisted to backend.

- **F-3.8:** Export — Export button to download the requirements structure as JSON or structured text format.

---

### FA-4: Review & Requirements Document

- **F-4.1:** Requirements Document Generation — A dedicated AI agent (separate from the requirements assembly AI) generates the Requirements Document from the full project state (chat history, requirements structure, company context already retrieved during assembly). Document structure is type-specific:

  **Software Projects:**
  - Project Overview (title, description, objectives)
  - Epics (each Epic as a section)
    - User Stories (title, "As a... I want... So that...", acceptance criteria, priority)
  - Technical Considerations
  - Success Criteria

  **Non-Software Projects:**
  - Project Overview (title, description, objectives)
  - Milestones (each Milestone as a section)
    - Work Packages (title, description, deliverables, dependencies, effort)
  - Resource Requirements
  - Success Criteria

> DOWNSTREAM → **AI Engineer**: Design the Summarizing AI agent — its system prompt, model selection, input assembly strategy, and how it reads the full project state. The agent must handle both Software and Non-Software project types. See `docs_old/01-requirements/features.md` F-5.1 for the original BRD spec.

- **F-4.2:** No Information Fabrication — The Summarizing AI must never fill information gaps with invented content. If insufficient information exists for a section, it outputs "Not enough information."

- **F-4.3:** Document Generation Trigger — First time the user opens the Review tab (on-demand). Manual regenerate button available.

- **F-4.4:** Per-Item Editing & Lock — Each requirements item (Epic/Story or Milestone/Package) and each document section displayed as an editable text field. When a user edits an item, it is automatically locked from AI regeneration. Lock/unlock indicator icon per item, manually toggleable. Selective regeneration button for unlocked items only, with optional instruction text field. AI text regeneration automatically chains into PDF regeneration.

- **F-4.5:** Review Tab (Right Panel) —
  - Displays the generated PDF of the Requirements Document.
  - Three-dot menu (top-right) with Download function.
  - Expandable edit area (slides left, overlaps chat): all requirements items and document sections as editable text fields with lock/unlock indicators, regenerate button + instruction field, regenerate PDF button, undo/redo for AI text changes (local), "Allow Information Gaps" toggle.
  - Below PDF preview: optional message text field (becomes first review timeline comment and is included in reviewer notification email), submit button with optional reviewer assignment.
  - User can visit Review tab, edit the document, and return to requirements assembly without submitting.

- **F-4.6:** Review Section (Below Fold) — Full viewport height below requirements assembly section.
  - Top area (always visible): small preview of latest requirements document, project title, assigned reviewer(s), current state label.
  - Below: timeline — chronological feed containing comments from User and Reviewer (with nested replies), inline state changes as text, resubmission entries with linked document versions (both versions as clickable download links).

- **F-4.7:** Document Versioning — Auto-versioned on each submit/resubmit. Immutable during a review cycle. Previous versions preserved as downloadable PDFs (named with date). Preview always shows the latest version.

> DOWNSTREAM → **Software Architect**: A separate service generates the PDF. Design the PDF generation service and storage strategy. See `docs_old/01-requirements/features.md` F-5.7.

- **F-4.8:** Document Readiness Evaluation — The Summarizing AI evaluates information sufficiency using AI judgment combined with minimum information anchors:

  **Software Projects:**
  - At least one Epic with at least one User Story.
  - Each User Story has acceptance criteria.
  - At least one success criterion defined.

  **Non-Software Projects:**
  - At least one Milestone with at least one Work Package.
  - Each Work Package has deliverables.
  - At least one success criterion defined.

  - Insufficient sections display "Not enough information."
  - Progress indicator visible in Review tab. Evaluates when: user opens Review tab first time, user opens tab and state changed since last evaluation, state changes while tab is open. Does not run in background during requirements assembly. Loading animation while calculating.

- **F-4.9:** Allow Information Gaps Toggle —
  - Located in expandable edit section of Review tab.
  - Deactivated by default.
  - When activated: skips readiness evaluation, AI generates all sections regardless, AI does not invent/guess/infer, AI leaves explicit gaps (incomplete sentences, open list items), all gaps marked with `/TODO`, markers highlighted in editable fields, user can fill in gaps manually.
  - Progress indicator turns grey with "gaps allowed" text.
  - PDF generation is rejected if any `/TODO` markers remain (error message lists which sections).
  - Filling a `/TODO` gap counts as user edit and auto-locks that item.

- **F-4.10:** Reviewer Assignment on Submit — User can optionally assign one or more specific reviewers when submitting. Unassigned projects go to a shared review queue. All Reviewers receive email notification for new submissions (subject to individual notification preferences). Optional submit message included in email.

- **F-4.11:** Multiple Reviewers — A project can have multiple reviewers assigned. Any single reviewer can independently accept, reject, or drop. No consensus required. If conflicting actions occur, latest action wins. All actions are reversible (undo returns project to In Review, mandatory comment required for undo).

---

### FA-5: Real-Time Collaboration

- **F-5.1:** Session-Level Connection — One connection per session with automatic reconnection. Reconnection strategy: exponential backoff up to a maximum of 30 seconds (admin-configurable).

> DOWNSTREAM → **Software Architect**: Design the real-time transport (WebSocket, SSE, etc.), connection lifecycle, and session management. See `docs_old/01-requirements/features.md` F-7.1.

- **F-5.2:** Offline Banner — Displays "Currently offline. Retrying in X seconds" with a manual reconnect button. On reconnection: banner disappears, state syncs from server, chat and requirements panel unlock.

- **F-5.3:** Presence Tracking — Online user indicators in the tab section area (right side of workspace). Deduplicated per user (multiple tabs show as one presence). States: Online (active), Idle (grey/dimmed), Offline (not shown).

- **F-5.4:** Multi-User Collaboration — Multiple users edit simultaneously. Chat messages broadcast in real-time. Requirements structure sync per FA-3 rules. Multi-tab handled naturally (each tab = separate connection).

- **F-5.5:** Offline Behavior — When connection is lost: offline banner displayed, chat locked (no input), requirements panel locked (read-only), everything visible but non-editable. On reconnection: unlocks, syncs latest state.

- **F-5.6:** Connection State Indicator — Located in the global navbar (right side). Green indicator + "Online" when connected. Red indicator + "Offline" when disconnected.

---

### FA-6: Authentication

- **F-6.1:** Development Auth Bypass — Double-gated: requires both AUTH_BYPASS=True and DEBUG=True. Creates fake authenticated users that behave identically to real users (all route protection and permission checks work normally). 4 preconfigured dev users:
  - Dev User 1: User role
  - Dev User 2: User role
  - Dev User 3: User + Reviewer role
  - Dev User 4: User + Admin role
  - User switcher in navbar for swapping between dev users.
  - No login screen in bypass mode.

- **F-6.2:** Production Authentication — Microsoft Azure OIDC/OAuth2. Token validation at API edge and connection handshake. Silent token refresh before expiry; if refresh fails, redirect to login. All routes protected — unauthenticated users redirected to login. Auth bypass cannot activate in production (double-gate).

> DOWNSTREAM → **Software Architect**: Design the authentication flow, token management, and middleware strategy. MSAL was noted as a frontend library preference in the old spec. See `docs_old/01-requirements/technology-notes.md`.

---

### FA-7: Visibility & Sharing

- **F-7.1:** Visibility Modes —
  - Private: only the owner can see/access the project. Single-user mode.
  - Collaborating: owner + invited/accepted collaborators. Multi-user mode.

- **F-7.2:** Invite Flow — Creator searches/selects users from the user directory (or dev users in bypass mode). Invited user receives email notification. Invitation appears on invitee's landing page in "Invitations" list with inviter's name + accept/decline buttons. Owner can re-invite users who declined. Owner can revoke pending invitations.

- **F-7.3:** Read-Only Link Sharing — Creator can generate a shareable link. Users accessing via link only (not invited) see the project in read-only mode. Requires authentication — non-employees cannot access.

- **F-7.4:** Collaborator Management — Located next to presence indicators in the tab section area. "Invite" button. Dropdown/popover for management (remove, transfer ownership). All collaborators have equal edit permissions (chat + requirements structure). Owner can remove collaborators. Collaborators can leave voluntarily. Owner can transfer ownership to a collaborator at any time. Single owner must transfer ownership before leaving.

---

### FA-8: Landing Page

- **F-8.1:** Landing Page Structure — Ordered lists:
  1. My Projects — projects the user owns.
  2. Collaborating — projects the user has accepted collaboration on.
  3. Invitations — pending collaboration invitations with accept/decline buttons.
  4. Trash — soft-deleted projects.

- **F-8.2:** Project Creation — Hero section with "New Project" button. Clicking opens a modal with:
  - Project type selection: Software or Non-Software (radio buttons or cards with descriptions).
  - Optional initial title field.
  - Create button.
  - After creation, user is navigated directly to the project workspace (chat is empty, ready for the first message).

- **F-8.3:** Soft Delete — Projects move to Trash with an undo toast. Permanent deletion after a configurable countdown (default: 30 days, admin-configurable).

- **F-8.4:** Search & Filter — Search bar for projects by title. Filter by state: Open / In Review / Accepted / Dropped / Rejected. Filter by ownership: My Projects / Collaborating.

---

### FA-9: Review Page (Reviewers Only)

- **F-9.1:** Access — Separate page accessible only to Reviewer role. Accessible from the global navbar (conditionally visible to Reviewers only).

- **F-9.2:** Categorized Project Lists — Submitted projects grouped in order:
  1. Assigned to me
  2. Unassigned
  3. Accepted
  4. Rejected
  5. Dropped

- **F-9.3:** Self-Assignment — Reviewers can self-assign from the unassigned list. Reviewers can unassign themselves (project returns to unassigned).

- **F-9.4:** Conflict of Interest — A Reviewer cannot review their own project.

---

### FA-10: Admin Panel

- **F-10.1:** Layout — Separate route: `/admin`. Accessible via navbar item (conditionally visible to Admins only). 4 tabs (each with an icon): AI Context, Parameters, Monitoring, Users.

- **F-10.2:** AI Context Tab — Three isolated, clearly separated context areas:
  - **Global Context:** Available to all project types. Contains:
    - Facilitator context: table of contents describing available company context. Free text editor.
    - Detailed company context: structured sections + free text block. Section editor.
  - **Software-Specific Context:** Available only to Software projects. Same structure (facilitator context + detailed context).
  - **Non-Software-Specific Context:** Available only to Non-Software projects. Same structure (facilitator context + detailed context).
  - All maintained manually by Admins.

- **F-10.3:** Parameters Tab — All parameters apply at runtime to all active projects immediately (no restart required).

  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | Chat message cap | 5 | Chat messages before lockout per project |
  | Idle timeout | 5 minutes | Time before user is marked idle |
  | Idle disconnect | 120 seconds | Time in idle before connection disconnects |
  | Max reconnection backoff | 30 seconds | Maximum reconnection retry interval |
  | Soft delete countdown | 30 days | Days before permanent deletion from trash |
  | Debounce timer | 3 seconds | Wait time after last chat message before AI processes |
  | Default app language | German | Default language for new users |

> DOWNSTREAM → **AI Engineer**: The old spec included additional AI-specific parameters: context compression threshold (default 60%), default AI model, escalated AI model, AI processing timeout (default 60s). Define which AI parameters need to be admin-configurable and their defaults. See `docs_old/01-requirements/features.md` F-12.3.

> DOWNSTREAM → **Software Architect**: The old spec included infrastructure parameters: max retry attempts (default 3), DLQ alert threshold (default 10), health check interval (default 60s). Define which operational parameters need to be admin-configurable. See `docs_old/01-requirements/features.md` F-12.3.

- **F-10.4:** Monitoring Tab — Dashboard (lightweight): active connections count, projects by state, active/online users count, AI processing requests (count, success/failure rate), system health status per service. Alert configuration: configurable recipient list (Admins opt in/out), triggers on health issues and error conditions. Alerts delivered via email.

- **F-10.5:** Backend Monitoring Service — Periodic background task running independently. Checks system health and error rates against configured thresholds. Sends email alerts to assigned Admins. Runs continuously regardless of frontend state.

> DOWNSTREAM → **Software Architect**: Design the monitoring service — what health checks to run, what metrics to track, alerting pipeline. The old spec included DLQ monitoring, per-service health, and configurable check intervals. See `docs_old/01-requirements/features.md` F-12.4, F-12.5.

- **F-10.6:** Users Tab — Admin searches for a user (not eager-loaded). Search results display: name, first name, email address, assigned roles, project count, review count, contribution count.

---

### FA-11: Notification System

- **F-11.1:** Notification Bell — Bell icon in global navbar with unread count badge. Opens a floating window with persistent notifications. Notifications disappear after being acted on. Inline action buttons (e.g., accept/decline on invitations). Clicking navigates to relevant context.

- **F-11.2:** Toast Notifications — Transient, auto-dismissing. Types: success, info, warning, error. Used for action confirmations and real-time events.

- **F-11.3:** Floating Banner (Project Page) — Shown when a user with a pending invitation navigates to a project. Contains accept/decline buttons. Accepting: user becomes collaborator, banner disappears, project unlocks. Declining: user redirected to landing page.

- **F-11.4:** All Notification Events —

  Toast-only (transient):
  | Event | Toast Type |
  |-------|------------|
  | Project moved to trash | Info |
  | Project restored from trash | Success |
  | PDF generated successfully | Success |
  | PDF generation rejected (TODO markers) | Error |
  | Connection lost | Warning |
  | Connection restored | Success |
  | Locked out (rate cap reached) | Warning |

  Dual notifications (toast + persistent in bell):
  | Event | Toast Type |
  |-------|------------|
  | Collaboration invitation | Info |
  | Collaborator joined | Info |
  | Collaborator left | Info |
  | Collaborator removed (you were removed) | Warning |
  | Ownership transferred to you | Info |
  | AI delegation complete | Info |
  | Project submitted for review (for Reviewers) | Info |
  | Review accepted | Success |
  | Review dropped | Warning |
  | Review rejected | Info |
  | Review action undone | Info |
  | Comment on review | Info |
  | @mention in chat | Info |

---

### FA-12: User Notification Preferences

- **F-12.1:** Email Notification Settings — Accessible from user menu dropdown. Opens a floating window / modal. Controls which notification types trigger email delivery. In-app notifications (toasts + bell) are always active — only email is configurable. All email notifications enabled by default.

- **F-12.2:** Grouped Toggles — Group toggle switches all items on/off. Individual toggles per notification type. Indeterminate state when mixed.

- **F-12.3:** Role-Based Notification Groups —

  All Users:
  | Group | Notification Types |
  |-------|--------------------|
  | Collaboration | Invitation received, Collaborator joined, Collaborator left, Removed from project, Ownership transferred |
  | Review | Review state changed (accepted/dropped/rejected/undone), Comment on review |
  | Chat | @mentions |

  Reviewer-only:
  | Group | Notification Types |
  |-------|--------------------|
  | Review Management | New project submitted, Project assigned to me, Project resubmitted |

  Admin-only:
  | Group | Notification Types |
  |-------|--------------------|
  | System | Monitoring alerts (health issues, error thresholds) |

---

### FA-13: Error Handling

- **F-13.1:** Universal Error Pattern — All error scenarios follow a consistent pattern:
  1. Error toast with two buttons: "Show Logs" and "Retry".
  2. "Show Logs" opens a centered modal with: console log output, network response message, technical details for diagnosis, support contact message.
  3. "Retry" triggers the failed operation again.
  4. Maximum retry attempts: admin-configurable (default: 3).
  - Applies to: AI processing failures, PDF generation failure, API request failures.
  - Does not apply to: authentication token expiry (handled via silent refresh or login redirect).

> DOWNSTREAM → **Software Architect**: The old spec included dead-letter queues on all message queues for debugging (no automatic retry from DLQ, retry is user-triggered via error toast). Design the error handling infrastructure, DLQ strategy, and retry mechanics. See `docs_old/01-requirements/features.md` F-15.1, F-15.2.

---

### FA-14: Idle State

- **F-14.1:** Idle Detection — User considered idle after configurable period of no mouse movement (default: 5 minutes, admin-configurable). Navigating away from browser tab triggers idle immediately. Presence indicator changes to grey/dimmed. User still connected, can receive updates.

- **F-14.2:** Connection Disconnect on Prolonged Idle — After configurable idle duration (default: 120 seconds, admin-configurable), connection is closed. Offline banner appears.

- **F-14.3:** Return from Idle — User returns and moves mouse → idle ends. Reconnection triggers. On success: banner disappears, state syncs, presence returns to online.

---

### FA-15: Multi-Language Support (i18n)

- **F-15.1:** Available Languages — German (default) and English.

- **F-15.2:** Language Switcher — Inside user menu dropdown (top-right navbar). Language preference persisted per user.

- **F-15.3:** Scope — All user-facing content: UI labels, buttons, navigation, notification emails, timeline events, system-generated text.

- **F-15.4:** AI Language — Initial language follows project creator's language setting. AI then adapts to whatever language users write in chat.

---

### FA-16: Theme Support (Light/Dark Mode)

- **F-16.1:** Available Themes — Light mode (default) and Dark mode.

- **F-16.2:** Theme Switcher — Inside user menu dropdown (top-right navbar), alongside language switcher. Theme preference persisted per user.

- **F-16.3:** System Preference Detection — On first visit (no saved preference), the application respects the user's OS-level `prefers-color-scheme` setting. After the user explicitly selects a theme, their choice overrides the system preference.

- **F-16.4:** Scope — All UI components, pages, backgrounds, text, borders, shadows, and interactive elements must render correctly in both themes. Contrast ratios (4.5:1 minimum) must be met in both modes.

- **F-16.5:** Brand Assets — The Commerz Real logo must remain legible in both themes. Dark mode may use an inverted or light-on-dark variant of the logo.

---

## Third-Party Integrations

| Integration | Purpose | Direction |
|------------|---------|-----------|
| Microsoft Azure AD | Authentication, user identity, role assignment (via AD groups), user directory search | Inbound |
| AI Service (Azure OpenAI) | All AI features — requirements structuring facilitation, company context retrieval, requirements document generation | Outbound |
| Email Service | Notification emails, monitoring alerts | Outbound |

> DOWNSTREAM → **Software Architect**: The old spec specified Azure OpenAI as the AI provider. Confirm provider choice and design the integration layer. See `docs_old/01-requirements/technology-notes.md`.

## Automated Processes

| Process | Trigger | Behavior |
|---------|---------|----------|
| AI Requirements Assembly Response | Chat message (after debounce) | AI processes project state, generates chat response and/or requirements structure modifications |
| Company Context Retrieval | AI determines company context is relevant | AI researches company information and delivers contextualized response |
| Requirements Document Generation | User opens Review tab / regenerate | AI generates requirements document from full project state |
| Soft Delete Cleanup | Scheduled (daily) | Permanently deletes projects that exceeded the trash countdown |
| Backend Monitoring | Scheduled (configurable interval) | Checks system health, sends alerts to Admins |
| PDF Generation | AI text generation / user trigger | Generates PDF from requirements document content |
