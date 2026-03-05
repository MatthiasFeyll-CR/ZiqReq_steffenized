# Feature Catalog

## Feature Areas

---

### FA-1: Idea Workspace

- **F-1.1:** Idea Page Layout — The idea page is a vertically extended viewport with two sections. The top section (fills viewport) contains a two-panel layout with a draggable divider: left panel is the chat interface, right panel is a tabbed context panel with Board and Review tabs. The bottom section (below the fold) contains the review workflow, only accessible after the idea has been submitted for review at least once.

- **F-1.2:** Section Visibility — The review section is hidden/inaccessible until the idea is submitted for review at least once. Once submitted, both sections persist on the page regardless of current state.

- **F-1.3:** Auto-Scroll on State Transition — The page auto-scrolls to the active section based on idea state: Open → brainstorming (top), In Review → review (bottom), Rejected → brainstorming (top), Accepted → review (bottom), Dropped → review (bottom). Also triggers when submitting for review and when entering an idea page.

- **F-1.4:** Section Locking — Sections lock/unlock based on idea state:
  - Open: brainstorming editable, review hidden.
  - In Review: brainstorming locked (read-only), review active.
  - Rejected: brainstorming editable (unlocked for rework), review visible (read-only).
  - Accepted: everything read-only.
  - Dropped: everything read-only.

- **F-1.5:** Idea Lifecycle — States: `open`, `in_review`, `accepted`, `dropped`, `rejected`. Transitions:
  - Open → In Review: user submits. Brainstorming locks, review activates.
  - In Review → Accepted: any reviewer accepts. Everything read-only, owner notified by email.
  - In Review → Dropped: any reviewer drops (mandatory comment). Everything read-only, owner notified by email.
  - In Review → Rejected: any reviewer rejects (mandatory comment). Brainstorming unlocks for rework, owner notified by email.
  - Rejected → In Review: user resubmits.
  - Accepted → In Review: any reviewer undoes accept (mandatory comment).
  - Dropped → In Review: any reviewer undoes drop (mandatory comment).
  - Rejected → In Review: any reviewer undoes rejection (mandatory comment).
  - Multiple reviewers: any single reviewer can act independently. If conflicting actions occur, latest action wins. All actions and undos with mandatory comments are recorded in the timeline for traceability.
  - No limit on resubmissions. Abuse prevented by reviewer's power to drop.

- **F-1.6:** Inline Title Editing — The idea title is editable directly in the workspace (clicking/tapping the title). Manual edits permanently disable AI title generation (see F-2.3). Title changes update the browser tab title dynamically.

- **F-1.7:** UUID-Based Routing — Each idea is accessed via `/idea/<uuid>`.

- **F-1.8:** Browser Tab Title — Shows the current idea name. Updates dynamically on title changes including AI-generated updates.

---

### FA-2: AI Facilitation

- **F-2.1:** Agent Modes — Two modes selectable via a dropdown in the workspace header:
  - Interactive (default): AI processes all inputs and decides autonomously whether to respond.
  - Silent: AI only responds when explicitly triggered with `@ai`.

- **F-2.2:** Language Detection — AI detects the user's language from chat messages and responds in the same language. Initial language (before any messages) follows the idea creator's app language setting.

- **F-2.3:** Title Generation — AI automatically generates a short, concise title from the first message. Periodically re-evaluates the title as conversation evolves and updates it when it no longer fits. Permanently disabled once a user manually edits the title. Title changes are animated.

- **F-2.4:** Decision Layer (Interactive Mode) — AI evaluates whether it has value to add before responding. Can decide "no action" — in which case it reacts instead of responding (see F-2.7).

- **F-2.5:** Multi-User Awareness — AI detects which user sent each message. Addresses users by name only when multiple users are collaborating on the same idea. In single-user mode, the AI does not address by name.

- **F-2.6:** Board Item References in Chat — AI can reference board items by title in chat messages. References are clickable links that navigate to the Board tab and highlight the referenced item. When a user mentions a board item by name in chat, the AI resolves which item is referenced. If ambiguous, the AI asks the user to use the explicit reference action on the board item.

- **F-2.7:** AI Reactions — The AI can react to user messages with three reactions:
  - 👍 Thumbs up: "I've seen this, nothing to add" (acknowledges without responding).
  - 👎 Thumbs down: Disagreement / rejection.
  - ❤️ Heart: "Your answer fully clarified my question" (context is now clear).
  - Users cannot react to AI messages. Users respond to AI via chat.

- **F-2.8:** User Reactions — Users can react to other users' messages (not AI messages) with the same three reactions: 👍, 👎, ❤️. The AI reads user-to-user reactions as sentiment signals during processing.

- **F-2.9:** @Mentions System — Typing `@` in chat opens a suggestion dropdown listing all users currently in the idea and `@ai`. `@username` notifies/addresses that user. `@ai` forces an AI response in any mode.

- **F-2.10:** AI Response Timing — After the last chat message, the system waits a brief configurable period (admin-configurable) before the AI begins processing. This prevents the AI from responding to incomplete thoughts when a user sends multiple rapid messages. If a new message arrives during processing, the AI restarts with the updated state. AI-generated outputs (chat responses, board modifications, reactions) do not trigger further processing.

> ⚙️ DOWNSTREAM → **AI Engineer**: The old spec defined a debounce timer (default 3s), abort-and-restart processing model, and the rule that AI processes full state (all chat + all board) on each cycle. Design the processing pipeline, trigger mechanics, and state management approach. See `docs_old/01-requirements/features.md` F-2.10 for the original detailed spec.

- **F-2.11:** Rate Limiting — Admin-configurable chat message cap per idea (default: 5). If the cap is reached without the AI completing a processing cycle, chat input is locked for all users on that idea. Board remains editable — only chat is locked. Counter resets when AI completes processing. Cap is per idea, shared across all users.

- **F-2.12:** AI Processing Indicator — "AI is processing" indicator with gentle animation, visible only during chat-triggered processing.

- **F-2.13:** Full State Knowledge — AI has knowledge of the entire idea state: all chat messages (or a summarized version of older messages plus recent messages), all board items, and their current state.

- **F-2.14:** Long Conversation Support — The AI must handle long brainstorming sessions without degrading in quality. Older chat messages may be summarized to keep the AI effective, but the original messages are always preserved and accessible. The user sees a visual indicator (filling circle) showing how much of the AI's working memory is used, with details available on hover.

> ⚙️ DOWNSTREAM → **AI Engineer**: The old spec defined context window management with automatic compression at a configurable threshold (default 60%), incremental summarization, and on-demand context extension with model escalation for unresolvable references. Design the context management strategy, compression approach, and any model escalation logic. See `docs_old/01-requirements/features.md` F-2.14, F-2.15, F-2.16 for the original detailed specs.

- **F-2.15:** Company Context Awareness — The AI has access to Commerz Real's business context (existing systems, domain terminology, company structure). When the AI needs to research company context during a conversation, it shows a brief placeholder message (e.g., "I'm researching this, I'll get back to you shortly"). Once the answer is ready, the placeholder is visually de-emphasized and the full response appears.

> ⚙️ DOWNSTREAM → **AI Engineer**: The old spec defined a two-bucket architecture (Facilitator Bucket with table of contents + Context Agent Bucket with detailed info) and a delegation flow between a facilitator AI and a specialized context agent. Design the agent architecture, context retrieval strategy, and delegation mechanics. See `docs_old/01-requirements/features.md` F-3.1 through F-3.4 for the original detailed specs.

- **F-2.16:** Company Context Management — Admins maintain the company context information through the Admin Panel (see FA-12). Two separate areas: a high-level table of contents describing what context exists, and a detailed section with structured company information. Updates to context do not retroactively affect in-progress brainstorming sessions.

- **F-2.17:** AI Board Content Rules — When the AI creates or modifies board content, it follows these rules:
  1. One topic per Box.
  2. Bullet-point format for Box body content.
  3. Connections express relationships between items.
  4. AI organizes Boxes into Groups when multiple Boxes exist.
  5. AI proactively reorganizes the board structure on each processing cycle for clarity.
  6. AI updates existing Boxes rather than creating duplicates.

> ⚙️ DOWNSTREAM → **AI Engineer**: These board content rules should be enforced via the facilitator AI's system prompt and/or tool constraints. Design how the AI agent interacts with the board (tool schemas, validation rules). See `docs_old/01-requirements/features.md` F-4.4 for the original spec.

---

### FA-3: Digital Board

- **F-3.1:** Node Types —
  - Box: solid background with visually distinct title + bullet-point body. Primary content node.
  - Group: container node with optional label/title. Children (Boxes, Free Text, nested Groups) move with the Group. Supports nesting (Groups within Groups).
  - Free Text: text placed directly on the canvas with no card, border, or background.

- **F-3.2:** Board Interactions —
  - Drag to move items.
  - Drag Boxes/Free Text into/out of Groups dynamically (attach/detach by dragging over a Group).
  - Resize Groups.
  - Double-click to edit content.
  - Ctrl+drag for multi-select.
  - Connections between any node types (no restrictions). Lines/edges express relationships.
  - Double-click on connections to add/edit sticky text labels.
  - Lock toggle per node (prevents editing).
  - AI-created items show a robot badge.

- **F-3.3:** Board UI — MiniMap for overview navigation. Zoom controls (in/out, fit view). Background grid. Toolbar: Add Box, Delete Selected, Fit View, Undo, Redo.

- **F-3.4:** AI Modification Indicators — When AI creates or modifies board items, each affected item shows a visual indicator. Indicator fades away once the user selects the item (acknowledged by interaction). Persists if user never selects it.

- **F-3.5:** Multi-User Board Editing — All users can edit simultaneously. When a user selects a node, it is highlighted for all other users with the user's name displayed. Last write wins for concurrent edits on the same Box.

- **F-3.6:** Board Sync — Selection highlights (with username) and lock state changes are broadcast in real-time. Content changes are broadcast when the user commits (Enter or click-outside). Position/resize changes are broadcast on release (drag/resize end).

> ⚙️ DOWNSTREAM → **Software Architect**: The old spec called this "hybrid sync" — real-time for awareness events, commit-based for content/position. Design the sync protocol, transport mechanism, and conflict resolution strategy. See `docs_old/01-requirements/features.md` F-4.7 for the original spec.

- **F-3.7:** Undo/Redo — Full undo/redo for all board actions (user and AI). Covers: node creation/deletion, content edits, connections, group changes, position/resize. Context-aware button labels: "Undo AI Action" / "Redo AI Action" for AI-generated actions, "Undo" / "Redo" for user actions.

> ⚙️ DOWNSTREAM → **Software Architect**: The old spec specified undo/redo history stored locally in the frontend (not persisted to backend). Decide the storage and state management approach. See `docs_old/01-requirements/features.md` F-4.8.

- **F-3.8:** Board Item Reference Action — Each board item has a reference action button (top-right corner). Clicking it inserts a formatted reference into the chat input for explicit board item references in messages.

---

### FA-4: Review & Requirements Document

- **F-4.1:** BRD Generation — A dedicated AI agent (separate from the brainstorming AI) generates the Business Requirements Document from the full idea state (chat history, board state, company context already retrieved during brainstorming). BRD sections:
  1. Title
  2. Short Description (summarizes the purpose)
  3. Current Workflow & Pain Points (how things work today and what's broken)
  4. Affected Department / Business Area (who benefits)
  5. Core User Capabilities ("the user can...")
  6. Success Criteria (measurable outcomes)

> ⚙️ DOWNSTREAM → **AI Engineer**: Design the Summarizing AI agent — its system prompt, model selection, input assembly strategy, and how it reads the full idea state. See `docs_old/01-requirements/features.md` F-5.1 for the original spec.

- **F-4.2:** No Information Fabrication — The Summarizing AI must never fill information gaps with invented content. If insufficient information exists for a section, it outputs "Not enough information."

- **F-4.3:** BRD Generation Trigger — First time the user opens the Review tab (on-demand). Manual regenerate button available.

- **F-4.4:** Per-Section Editing & Lock — Each BRD section displayed as an editable text field. When a user edits a section, it is automatically locked from AI regeneration. Lock/unlock indicator icon per section, manually toggleable. Selective regeneration button for unlocked sections only, with optional instruction text field. AI text regeneration automatically chains into PDF regeneration.

- **F-4.5:** Review Tab (Right Panel) —
  - Displays the generated PDF of the BRD.
  - Three-dot menu (top-right) with Download function.
  - Expandable edit area (slides left, overlaps chat): all BRD sections as editable text fields with lock/unlock indicators, regenerate button + instruction field, regenerate PDF button, undo/redo for AI text changes (local), "Allow Information Gaps" toggle.
  - Below PDF preview: optional message text field (becomes first review timeline comment and is included in reviewer notification email), submit button with optional reviewer assignment.
  - User can visit Review tab, edit the document, and return to brainstorming without submitting.

- **F-4.6:** Review Section (Below Fold) — Full viewport height below brainstorming section.
  - Top area (always visible): small preview of latest requirements document, idea title, assigned reviewer(s), current state label.
  - Below: timeline — chronological feed containing comments from User and Reviewer (with nested replies), inline state changes as text, resubmission entries with linked document versions (both versions as clickable download links).

- **F-4.7:** Document Versioning — Auto-versioned on each submit/resubmit. Immutable during a review cycle. Previous versions preserved as downloadable PDFs (named with date). Preview always shows the latest version.

> ⚙️ DOWNSTREAM → **Software Architect**: A separate service generates the PDF. Design the PDF generation service and storage strategy. See `docs_old/01-requirements/features.md` F-5.7.

- **F-4.8:** Document Readiness Evaluation — The Summarizing AI evaluates information sufficiency per section using AI judgment combined with minimum information anchors:
  - Current Workflow & Pain Points: at least one workflow and one pain point discussed.
  - Affected Department: at least one department/area identified.
  - Core Capabilities: at least one concrete user action identified.
  - Success Criteria: at least one measurable outcome mentioned.
  - Insufficient sections display "Not enough information."
  - Progress indicator visible in Review tab. Evaluates when: user opens Review tab first time, user opens tab and state changed since last evaluation, state changes while tab is open. Does not run in background during brainstorming. Loading animation while calculating.

- **F-4.9:** Allow Information Gaps Toggle —
  - Located in expandable edit section of Review tab.
  - Deactivated by default.
  - When activated: skips readiness evaluation, AI generates all sections regardless, AI does not invent/guess/infer, AI leaves explicit gaps (incomplete sentences, open list items), all gaps marked with `/TODO`, markers highlighted in editable fields, user can fill in gaps manually.
  - Progress indicator turns grey with "gaps allowed" text.
  - PDF generation is rejected if any `/TODO` markers remain (error message lists which sections).
  - Filling a `/TODO` gap counts as user edit and auto-locks that section.

- **F-4.10:** Reviewer Assignment on Submit — User can optionally assign one or more specific reviewers when submitting. Unassigned ideas go to a shared review queue. All Reviewers receive email notification for new submissions (subject to individual notification preferences). Optional submit message included in email.

- **F-4.11:** Multiple Reviewers — An idea can have multiple reviewers assigned. Any single reviewer can independently accept, reject, or drop. No consensus required. If conflicting actions occur, latest action wins. All actions are reversible (undo returns idea to In Review, mandatory comment required for undo).

- **F-4.12:** Similar Ideas in Review Section — Displayed to reviewers in the review section. Shows:
  - Ideas that hit the similarity threshold but the user rejected the merge.
  - Ideas slightly below the similarity threshold.
  - The AI comparison also runs during the review process to help reviewers identify similarities.

---

### FA-5: Idea Similarity Detection & Resolution

- **F-5.1:** Keyword Generation — The AI generates abstract keywords (single words with highly abstract meaning) for each idea during brainstorming. Maximum 20 keywords per idea (admin-configurable). Keywords are only generated once the idea direction is clear — not during early vague brainstorming. Keywords are updated as the brainstorming evolves and the idea's scope sharpens.

> ⚙️ DOWNSTREAM → **AI Engineer**: Design how the facilitator AI generates and updates keywords — prompt strategy, when to trigger, how abstract keywords are defined. See `docs_old/01-requirements/features.md` F-6.1.

- **F-5.2:** Background Keyword Matching — A background service compares keywords across ideas. Minimum overlap threshold: 7 keywords (admin-configurable). Time limit: only matches against ideas from the last 6 months (admin-configurable). Design philosophy: prefer false negatives over false positives. Human reviewers are the safety net for missed similarities.

> ⚙️ DOWNSTREAM → **Software Architect**: Design the background matching service — scheduling, data access, threshold comparison logic. See `docs_old/01-requirements/features.md` F-6.2.

- **F-5.3:** AI Deep Comparison — When keyword overlap meets the threshold, a second-stage AI process compares the full context of both ideas to confirm genuine similarity (not a false positive from generic keyword overlap).

> ⚙️ DOWNSTREAM → **AI Engineer**: Design the deep comparison agent — input assembly, comparison prompt, confirmation/rejection output format. See `docs_old/01-requirements/features.md` F-6.3.

- **F-5.4:** State-Aware Match Behavior —
  - **Open or Rejected** (active brainstorming): Mergeable. Full merge flow applies (see F-5.5).
  - **In Review**: Not mergeable. The open idea's owner can request an append — the open idea would be closed, its context appended to the in-review idea. Requires consent from: the open idea's owner (who requests it), the in-review idea's owner, and one assigned reviewer. On acceptance: open idea closes (read-only with reference), its owner becomes a collaborator on the in-review idea.
  - **Accepted**: Informational only. AI guides the user: is this worth a new app, or should it be a change request to the existing app built from the accepted idea?
  - **Dropped**: Informational only. AI raises concerns that a similar idea was permanently closed by a reviewer. User must clarify what's different about their idea.

- **F-5.5:** Merge Flow (Open/Rejected Ideas) —
  1. AI detects similarity and notifies both users (in-app notification + email).
  2. Both users receive read-only access to the other's idea, including the other user's name.
  3. Either user can request the merge.
  4. The receiving idea is locked with a banner until its owner accepts/rejects. The requesting user continues brainstorming (no lock).
  5. Both owners must consent for merge to proceed.
  6. On merge: a new idea is created. AI synthesizes a summary of merged context as the first chat message. AI creates a merged board combining/deduplicating topics from both originals. Both original owners become co-owners. All collaborators from both ideas are added.
  7. Old ideas remain accessible in read-only mode with a reference and text information about the new merged idea.
  8. Users can reference content from the old ideas to pull things into the new context that the AI missed.

- **F-5.6:** Merge Request UI — The merge request is displayed as a banner over the receiving idea page. The owner receives an email notification and an in-app notification. The idea is locked until the owner accepts or rejects.

- **F-5.7:** Permanent Dismissal — If an owner declines a merge, the AI permanently dismisses that specific match. The same pair of ideas will not be suggested again.

- **F-5.8:** Manual Merge Request — Users can manually invoke a merge request to another active idea (recovery path for accidental declines). Two discovery methods:
  - Insert the UUID or full URL of the other idea.
  - Browse the similar ideas list (displays title and keywords on selection).

---

### FA-6: Real-Time Collaboration

- **F-6.1:** Session-Level Connection — One connection per session with automatic reconnection. Reconnection strategy: exponential backoff up to a maximum of 30 seconds (admin-configurable).

> ⚙️ DOWNSTREAM → **Software Architect**: Design the real-time transport (WebSocket, SSE, etc.), connection lifecycle, and session management. See `docs_old/01-requirements/features.md` F-7.1.

- **F-6.2:** Offline Banner — Displays "Currently offline. Retrying in X seconds" with a manual reconnect button. On reconnection: banner disappears, state syncs from server, chat and board unlock.

- **F-6.3:** Presence Tracking — Online user indicators in the tab section area (right side of workspace). Deduplicated per user (multiple tabs show as one presence). States: Online (active), Idle (grey/dimmed), Offline (not shown).

- **F-6.4:** Multi-User Collaboration — Multiple users edit simultaneously. Chat messages broadcast in real-time. Board sync per FA-3 rules. Multi-tab handled naturally (each tab = separate connection).

- **F-6.5:** Offline Behavior — When connection is lost: offline banner displayed, chat locked (no input), board locked (read-only), everything visible but non-editable. On reconnection: unlocks, syncs latest state.

- **F-6.6:** Connection State Indicator — Located in the global navbar (right side). Green indicator + "Online" when connected. Red indicator + "Offline" when disconnected.

---

### FA-7: Authentication

- **F-7.1:** Development Auth Bypass — Double-gated: requires both AUTH_BYPASS=True and DEBUG=True. Creates fake authenticated users that behave identically to real users (all route protection and permission checks work normally). 4 preconfigured dev users:
  - Dev User 1: User role
  - Dev User 2: User role
  - Dev User 3: User + Reviewer role
  - Dev User 4: User + Admin role
  - User switcher in navbar for swapping between dev users.
  - No login screen in bypass mode.

- **F-7.2:** Production Authentication — Microsoft Azure OIDC/OAuth2. Token validation at API edge and connection handshake. Silent token refresh before expiry; if refresh fails, redirect to login. All routes protected — unauthenticated users redirected to login. Auth bypass cannot activate in production (double-gate).

> ⚙️ DOWNSTREAM → **Software Architect**: Design the authentication flow, token management, and middleware strategy. MSAL was noted as a frontend library preference in the old spec. See `docs_old/01-requirements/technology-notes.md`.

---

### FA-8: Visibility & Sharing

- **F-8.1:** Visibility Modes —
  - Private: only the owner can see/access the idea. Single-user mode.
  - Collaborating: owner + invited/accepted collaborators. Multi-user mode.

- **F-8.2:** Invite Flow — Creator searches/selects users from the user directory (or dev users in bypass mode). Invited user receives email notification. Invitation appears on invitee's landing page in "Invitations" list with inviter's name + accept/decline buttons. Owner can re-invite users who declined. Owner can revoke pending invitations.

- **F-8.3:** Read-Only Link Sharing — Creator can generate a shareable link. Users accessing via link only (not invited) see the idea in read-only mode. Requires authentication — non-employees cannot access.

- **F-8.4:** Collaborator Management — Located next to presence indicators in the tab section area. "Invite" button. Dropdown/popover for management (remove, transfer ownership). All collaborators have equal edit permissions (chat + board). Owner can remove collaborators. Collaborators can leave voluntarily. Owner can transfer ownership to a collaborator at any time. Single owner must transfer ownership before leaving. Co-owners (merged ideas only) can leave without transferring.

---

### FA-9: Landing Page

- **F-9.1:** Landing Page Structure — Ordered lists:
  1. My Ideas — ideas the user owns.
  2. Collaborating — ideas the user has accepted collaboration on.
  3. Invitations — pending collaboration invitations with accept/decline buttons.
  4. Trash — soft-deleted ideas.

- **F-9.2:** Idea Creation — Hero section for creating a new idea. First message typed on the landing page becomes the first chat message in the workspace (seamless transition).

- **F-9.3:** Soft Delete — Ideas move to Trash with an undo toast. Permanent deletion after a configurable countdown (default: 30 days, admin-configurable).

- **F-9.4:** Search & Filter — Search bar for ideas by title. Filter by state: Open / In Review / Accepted / Dropped / Rejected. Filter by ownership: My Ideas / Collaborating.

---

### FA-10: Review Page (Reviewers Only)

- **F-10.1:** Access — Separate page accessible only to Reviewer role. Accessible from the global navbar (conditionally visible to Reviewers only).

- **F-10.2:** Categorized Idea Lists — Submitted ideas grouped in order:
  1. Assigned to me
  2. Unassigned
  3. Accepted
  4. Rejected
  5. Dropped

- **F-10.3:** Self-Assignment — Reviewers can self-assign from the unassigned list. Reviewers can unassign themselves (idea returns to unassigned).

- **F-10.4:** Conflict of Interest — A Reviewer cannot review their own idea.

---

### FA-11: Admin Panel

- **F-11.1:** Layout — Separate route: `/admin`. Accessible via navbar item (conditionally visible to Admins only). 4 tabs (each with an icon): AI Context, Parameters, Monitoring, Users.

- **F-11.2:** AI Context Tab — Two isolated, clearly separated areas:
  - Facilitator context: table of contents describing available company context. Free text editor.
  - Detailed company context: structured sections + free text block. Section editor.
  - Both maintained manually by Admins.

- **F-11.3:** Parameters Tab — All parameters apply at runtime to all active ideas immediately (no restart required).

  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | Chat message cap | 5 | Chat messages before lockout per idea |
  | Idle timeout | 5 minutes | Time before user is marked idle |
  | Idle disconnect | 120 seconds | Time in idle before connection disconnects |
  | Max reconnection backoff | 30 seconds | Maximum reconnection retry interval |
  | Soft delete countdown | 30 days | Days before permanent deletion from trash |
  | Debounce timer | 3 seconds | Wait time after last chat message before AI processes |
  | Default app language | German | Default language for new users |
  | Max keywords per idea | 20 | Maximum abstract keywords generated per idea |
  | Min keyword overlap | 7 | Minimum keyword matches to trigger similarity comparison |
  | Similarity time limit | 6 months | How far back to match against existing ideas |

> ⚙️ DOWNSTREAM → **AI Engineer**: The old spec included additional AI-specific parameters: context compression threshold (default 60%), default AI model, escalated AI model, AI processing timeout (default 60s). Define which AI parameters need to be admin-configurable and their defaults. See `docs_old/01-requirements/features.md` F-12.3.

> ⚙️ DOWNSTREAM → **Software Architect**: The old spec included infrastructure parameters: max retry attempts (default 3), DLQ alert threshold (default 10), health check interval (default 60s). Define which operational parameters need to be admin-configurable. See `docs_old/01-requirements/features.md` F-12.3.

- **F-11.4:** Monitoring Tab — Dashboard (lightweight): active connections count, ideas by state, active/online users count, AI processing requests (count, success/failure rate), system health status per service. Alert configuration: configurable recipient list (Admins opt in/out), triggers on health issues and error conditions. Alerts delivered via email.

- **F-11.5:** Backend Monitoring Service — Periodic background task running independently. Checks system health and error rates against configured thresholds. Sends email alerts to assigned Admins. Runs continuously regardless of frontend state.

> ⚙️ DOWNSTREAM → **Software Architect**: Design the monitoring service — what health checks to run, what metrics to track, alerting pipeline. The old spec included DLQ monitoring, per-service health, and configurable check intervals. See `docs_old/01-requirements/features.md` F-12.4, F-12.5.

- **F-11.6:** Users Tab — Admin searches for a user (not eager-loaded). Search results display: name, first name, email address, assigned roles, idea count, review count, contribution count.

---

### FA-12: Notification System

- **F-12.1:** Notification Bell — Bell icon in global navbar with unread count badge. Opens a floating window with persistent notifications. Notifications disappear after being acted on. Inline action buttons (e.g., accept/decline on invitations). Clicking navigates to relevant context.

- **F-12.2:** Toast Notifications — Transient, auto-dismissing. Types: success, info, warning, error. Used for action confirmations and real-time events.

- **F-12.3:** Floating Banner (Idea Page) — Shown when a user with a pending invitation navigates to an idea. Contains accept/decline buttons. Accepting: user becomes collaborator, banner disappears, idea unlocks. Declining: user redirected to landing page.

- **F-12.4:** Merge Request Banner (Idea Page) — Shown when a merge request is received. Idea is locked until owner accepts/rejects. Contains accept/decline buttons. Accepting: merge proceeds per F-5.5. Declining: merge permanently dismissed, idea unlocks.

- **F-12.5:** All Notification Events —

  Toast-only (transient):
  | Event | Toast Type |
  |-------|------------|
  | Idea moved to trash | Info |
  | Idea restored from trash | Success |
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
  | Idea submitted for review (for Reviewers) | Info |
  | Review accepted | Success |
  | Review dropped | Warning |
  | Review rejected | Info |
  | Review action undone | Info |
  | Comment on review | Info |
  | @mention in chat | Info |
  | Similar idea detected (merge suggestion) | Info |
  | Merge request received | Info |
  | Merge request accepted | Success |
  | Merge request declined | Info |
  | Idea closed (append to in-review idea) | Info |

---

### FA-13: User Notification Preferences

- **F-13.1:** Email Notification Settings — Accessible from user menu dropdown. Opens a floating window / modal. Controls which notification types trigger email delivery. In-app notifications (toasts + bell) are always active — only email is configurable. All email notifications enabled by default.

- **F-13.2:** Grouped Toggles — Group toggle switches all items on/off. Individual toggles per notification type. Indeterminate state when mixed.

- **F-13.3:** Role-Based Notification Groups —

  All Users:
  | Group | Notification Types |
  |-------|--------------------|
  | Collaboration | Invitation received, Collaborator joined, Collaborator left, Removed from idea, Ownership transferred |
  | Review | Review state changed (accepted/dropped/rejected/undone), Comment on review |
  | Chat | @mentions |
  | Similarity | Similar idea detected, Merge request received, Merge accepted/declined, Idea closed (append) |

  Reviewer-only:
  | Group | Notification Types |
  |-------|--------------------|
  | Review Management | New idea submitted, Idea assigned to me, Idea resubmitted, Append request received |

  Admin-only:
  | Group | Notification Types |
  |-------|--------------------|
  | System | Monitoring alerts (health issues, error thresholds) |

---

### FA-14: Error Handling

- **F-14.1:** Universal Error Pattern — All error scenarios follow a consistent pattern:
  1. Error toast with two buttons: "Show Logs" and "Retry".
  2. "Show Logs" opens a centered modal with: console log output, network response message, technical details for diagnosis, support contact message.
  3. "Retry" triggers the failed operation again.
  4. Maximum retry attempts: admin-configurable (default: 3).
  - Applies to: AI processing failures, PDF generation failure, API request failures.
  - Does not apply to: authentication token expiry (handled via silent refresh or login redirect).

> ⚙️ DOWNSTREAM → **Software Architect**: The old spec included dead-letter queues on all message queues for debugging (no automatic retry from DLQ, retry is user-triggered via error toast). Design the error handling infrastructure, DLQ strategy, and retry mechanics. See `docs_old/01-requirements/features.md` F-15.1, F-15.2.

---

### FA-15: Idle State

- **F-15.1:** Idle Detection — User considered idle after configurable period of no mouse movement (default: 5 minutes, admin-configurable). Navigating away from browser tab triggers idle immediately. Presence indicator changes to grey/dimmed. User still connected, can receive updates.

- **F-15.2:** Connection Disconnect on Prolonged Idle — After configurable idle duration (default: 120 seconds, admin-configurable), connection is closed. Offline banner appears.

- **F-15.3:** Return from Idle — User returns and moves mouse → idle ends. Reconnection triggers. On success: banner disappears, state syncs, presence returns to online.

---

### FA-16: Multi-Language Support (i18n)

- **F-16.1:** Available Languages — German (default) and English.

- **F-16.2:** Language Switcher — Inside user menu dropdown (top-right navbar). Language preference persisted per user.

- **F-16.3:** Scope — All user-facing content: UI labels, buttons, navigation, notification emails, timeline events, system-generated text.

- **F-16.4:** AI Language — Initial language follows idea creator's language setting. AI then adapts to whatever language users write in chat.

---

### FA-17: Theme Support (Light/Dark Mode)

- **F-17.1:** Available Themes — Light mode (default) and Dark mode.

- **F-17.2:** Theme Switcher — Inside user menu dropdown (top-right navbar), alongside language switcher. Theme preference persisted per user.

- **F-17.3:** System Preference Detection — On first visit (no saved preference), the application respects the user's OS-level `prefers-color-scheme` setting. After the user explicitly selects a theme, their choice overrides the system preference.

- **F-17.4:** Scope — All UI components, pages, backgrounds, text, borders, shadows, and interactive elements must render correctly in both themes. Contrast ratios (4.5:1 minimum) must be met in both modes.

- **F-17.5:** Brand Assets — The Commerz Real logo must remain legible in both themes. Dark mode may use an inverted or light-on-dark variant of the logo.

---

## Third-Party Integrations

| Integration | Purpose | Direction |
|------------|---------|-----------|
| Microsoft Azure AD | Authentication, user identity, role assignment (via AD groups), user directory search | Inbound |
| AI Service (Azure OpenAI) | All AI features — brainstorming facilitation, company context retrieval, BRD generation, keyword generation, deep comparison | Outbound |
| Email Service | Notification emails, monitoring alerts | Outbound |

> ⚙️ DOWNSTREAM → **Software Architect**: The old spec specified Azure OpenAI as the AI provider. Confirm provider choice and design the integration layer. See `docs_old/01-requirements/technology-notes.md`.

## Automated Processes

| Process | Trigger | Behavior |
|---------|---------|----------|
| AI Brainstorming Response | Chat message (after debounce) | AI processes idea state, generates chat response and/or board modifications |
| Company Context Retrieval | AI determines company context is relevant | AI researches company information and delivers contextualized response |
| BRD Generation | User opens Review tab / regenerate | AI generates BRD from full idea state |
| Keyword Generation | During AI processing | AI generates/updates abstract keywords when idea direction is clear |
| Background Keyword Matching | Continuous / periodic | Compares keywords across ideas, triggers AI deep comparison on threshold match |
| AI Deep Comparison | Keyword match threshold met | Compares full context of two ideas to confirm similarity |
| Soft Delete Cleanup | Scheduled (daily) | Permanently deletes ideas that exceeded the trash countdown |
| Backend Monitoring | Scheduled (configurable interval) | Checks system health, sends alerts to Admins |
| PDF Generation | AI text generation / user trigger | Generates PDF from BRD content |
