# Integration Scenarios

> **Status:** Definitive (revised for refactoring)
> **Date:** 2026-03-16
> **Author:** Test Architect (Phase 4b - Refactored)
> **Input:** All feature areas (FA-1–FA-17), `api-design.md`, `agent-architecture.md`, `test-matrix.md`, `REFACTORING_PLAN.md`
> **Revision:** Updated for project-centric refactoring - removed board/merge/similarity systems, updated terminology (idea→project)

This document defines cross-feature integration test scenarios, end-to-end user journeys, concurrency scenarios, and error propagation scenarios. These tests catch bugs that individual feature tests miss — broken handoffs, state inconsistencies, and race conditions between subsystems.

---

## 1. Cross-Feature Scenarios

### SCN-001: Chat Message → AI Processing → Requirements Update → WebSocket Broadcast

- **Features involved:** F-2.1, F-2.10, F-2.17, F-3.5, F-3.6, F-6.4
- **Description:** User sends a chat message, AI processes it (after debounce), generates a chat response and requirements structure updates, all changes broadcast to connected clients via WebSocket.
- **Preconditions:** Project exists with owner connected via WebSocket. AI_MOCK_MODE=True.
- **Steps:**
  1. User sends chat message via REST API
  2. WebSocket broadcasts `chat.message.created` to all subscribers
  3. Debounce timer expires (3s), AI processing starts
  4. WebSocket broadcasts `ai.processing.started`
  5. AI returns chat response + requirements structure update instructions
  6. Gateway publishes chat message → WebSocket broadcasts AI message
  7. Core updates requirements structure → WebSocket broadcasts `requirements.updated` events
  8. WebSocket broadcasts `ai.processing.completed`
- **Expected result:** Both user and collaborator receive all events in order. Requirements structure reflects AI changes. Chat history includes both user and AI messages.
- **Priority:** P1
- **Layer:** E2E

---

### SCN-002: Chat Rate Limit → Lockout → AI Completes → Unlock

- **Features involved:** F-2.10, F-2.11, F-6.5
- **Description:** User hits the chat message cap, chat input locks, AI completes processing, chat unlocks.
- **Preconditions:** Project with `chat_message_cap=3` (admin parameter). AI mock mode.
- **Steps:**
  1. User sends 3 messages rapidly (before AI processes)
  2. 4th message attempt rejected with 429 / lockout toast
  3. WebSocket broadcasts `chat.rate_limited` event
  4. AI processes the batch and completes
  5. WebSocket broadcasts `ai.processing.completed`
  6. Chat input unlocks, counter resets
  7. User sends another message successfully
- **Expected result:** Rate limit enforced per project. Lockout clears on AI completion. No messages lost.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-003: Requirements Document Generation → Readiness Evaluation → Section Lock → Selective Regeneration

- **Features involved:** F-4.1, F-4.2, F-4.3, F-4.4, F-4.8
- **Description:** User opens Review tab, requirements document generates, user locks some sections, then triggers selective regeneration for unlocked sections only.
- **Preconditions:** Project with sufficient chat history. Requirements document not yet generated.
- **Steps:**
  1. User opens Review tab → triggers requirements document generation
  2. AI generates hierarchical document structure + readiness evaluation
  3. User edits "Executive Summary" section → section auto-locks
  4. User manually locks "Business Objectives"
  5. User triggers regeneration with instruction text
  6. AI regenerates only unlocked sections, locked sections preserved
  7. Readiness re-evaluates for regenerated sections
- **Expected result:** Locked sections untouched. Regenerated sections updated. Readiness reflects current state. No fabricated content (F-4.2).
- **Priority:** P1
- **Layer:** Integration

---

### SCN-004: Requirements Submit → State Transition → Review Assignment → Notification Chain

- **Features involved:** F-1.5, F-4.5, F-4.7, F-4.10, F-12.1, F-12.5
- **Description:** User submits project for review, state transitions, requirements document version created, reviewers assigned, notifications dispatched.
- **Preconditions:** Project in "open" state with completed requirements draft. Two reviewers exist.
- **Steps:**
  1. User submits with optional message and selects 2 reviewers
  2. Requirements document version (v1) created from current draft (immutable snapshot)
  3. PDF generated from requirements document version
  4. Project state transitions: `open` → `in_review`
  5. Review assignments created for both reviewers
  6. Timeline entry created (type: `state_change`)
  7. Requirements assembly section locks (read-only)
  8. Notifications dispatched: persistent (bell) + email to each reviewer
  9. WebSocket broadcasts state change to all connected users
- **Expected result:** State transition atomic. Requirements document version immutable. Both reviewers notified. Requirements assembly locked.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-005: Reviewer Action → State Change → Owner Notification → Resubmission

- **Features involved:** F-1.5, F-4.6, F-4.7, F-4.11, F-12.5
- **Description:** Reviewer rejects project, owner receives notification, reworks requirements document, resubmits.
- **Preconditions:** Project in "in_review" state with reviewer assigned.
- **Steps:**
  1. Reviewer posts timeline comment
  2. Reviewer rejects project (mandatory comment)
  3. State transitions: `in_review` → `rejected`
  4. Owner notified via persistent notification + email
  5. Requirements assembly section unlocks for rework
  6. Owner edits requirements document sections
  7. Owner resubmits → state transitions: `rejected` → `in_review`
  8. Requirements document version v2 created, new PDF generated
  9. Timeline entry created (type: `resubmission`, links v1 and v2)
  10. Reviewers re-notified
- **Expected result:** Full rejection-rework-resubmit cycle works. Both requirements document versions accessible. Timeline shows complete audit trail.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-006: Collaboration Invitation → Accept → Real-Time Join

- **Features involved:** F-8.1, F-8.2, F-6.3, F-6.4, F-12.1, F-12.3
- **Description:** Owner invites collaborator, invitee accepts, gains real-time access.
- **Preconditions:** Project in "open" state. Two users exist.
- **Steps:**
  1. Owner sends collaboration invitation
  2. Invitee notified (bell + email)
  3. Invitation appears on invitee's landing page
  4. Invitee navigates to project → sees floating banner with accept/decline
  5. Invitee accepts → collaborator record created
  6. Project visibility changes to "collaborating"
  7. Invitee's WebSocket subscribes to project's channel group
  8. Owner sees invitee appear in presence indicators
  9. AI detects multi-user mode → addresses users by name (F-2.5)
- **Expected result:** Invitation flow end-to-end. Real-time presence updates. AI behavior changes for multi-user.
- **Priority:** P1
- **Layer:** E2E

---

### SCN-007: Context Delegation (Facilitator → Context Agent → Response)

- **Features involved:** F-2.15, F-2.16
- **Description:** User asks about company context, Facilitator delegates to Context Agent, delegation message appears, full response follows.
- **Preconditions:** Company context populated in context_agent_bucket (global or type-specific). RAG chunks indexed.
- **Steps:**
  1. User sends message referencing company context ("What existing systems handle this?")
  2. Facilitator decides to delegate to Context Agent
  3. Delegation chat message created (visually de-emphasized)
  4. WebSocket broadcasts delegation message
  5. Context Agent performs RAG retrieval
  6. Context Agent returns results to Facilitator pipeline
  7. Facilitator generates response incorporating context
  8. Full response chat message created
  9. WebSocket broadcasts full response
- **Expected result:** Delegation placeholder visible before full response. Context correctly retrieved via RAG. Response incorporates company context without fabrication.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-008: Context Compression Trigger

- **Features involved:** F-2.13, F-2.14
- **Description:** Long conversation triggers context compression. Context window indicator updates. AI quality maintained.
- **Preconditions:** Project with 50+ chat messages. Context usage approaching threshold (60%).
- **Steps:**
  1. User sends message that pushes context usage above 60%
  2. Context Compression agent triggered
  3. Chat context summary created/updated
  4. WebSocket broadcasts context window usage update
  5. Frontend updates filling circle indicator
  6. Next AI processing uses compressed context + recent messages
  7. AI response quality maintained (references earlier conversation correctly)
- **Expected result:** Compression happens transparently. UI indicator reflects usage. Original messages preserved. AI doesn't "forget" critical information.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-009: Project Creation from Landing Page

- **Features involved:** F-9.2, F-2.1, F-2.3, F-2.10
- **Description:** User selects project type in modal, project created, navigates to workspace, can start requirements assembly.
- **Preconditions:** User authenticated on landing page.
- **Steps:**
  1. User clicks "New Project" button
  2. Modal opens with type selection (Software / Non-Software)
  3. User selects "Software" → project created via REST API
  4. Browser navigates to `/project/<uuid>`
  5. WebSocket connection established for new project
  6. User can start sending messages or structuring requirements
  7. AI processes first message → generates title + initial response
  8. Title displayed and animated
  9. AI response appears in chat
- **Expected result:** Modal flow complete. Type correctly set. Workspace loads. AI ready for requirements assembly.
- **Priority:** P1
- **Layer:** E2E

---

### SCN-010: Admin Parameter Change → Runtime Effect

- **Features involved:** F-11.3, F-2.10, F-2.11
- **Description:** Admin changes debounce timer parameter, effect applies immediately to active projects.
- **Preconditions:** Admin user. Active project with ongoing requirements assembly.
- **Steps:**
  1. Admin navigates to Parameters tab
  2. Admin changes `debounce_timer` from 3 to 5 seconds
  3. Parameter saved via REST API
  4. Active project's next processing cycle uses new 5s debounce
  5. No restart or reconnection required
- **Expected result:** Parameter change takes effect at runtime. No service interruption.
- **Priority:** P2
- **Layer:** Integration

---

### SCN-011: PDF Generation → /TODO Rejection → Manual Fix → Success

- **Features involved:** F-4.4, F-4.7, F-4.9
- **Description:** User enables "Allow Information Gaps", requirements document generates with /TODO markers, PDF generation rejected, user fills gaps, PDF generates successfully.
- **Preconditions:** Project with incomplete chat history. Requirements document draft exists.
- **Steps:**
  1. User enables "Allow Information Gaps" toggle
  2. Requirements document regenerates with /TODO markers in 2 sections
  3. /TODO markers highlighted in editable fields
  4. User attempts to generate PDF → rejected with error listing sections
  5. User fills in /TODO gaps in both sections
  6. Sections auto-lock on edit
  7. User generates PDF → success
  8. PDF created, requirements document version immutable
- **Expected result:** /TODO rejection enforced. Gap-filling locks sections. PDF generated after all markers resolved.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-012: Soft Delete → Trash → Undo → Permanent Delete

- **Features involved:** F-9.3, F-12.5
- **Description:** User deletes project, it appears in trash with undo toast, undo restores, re-delete and wait for permanent deletion.
- **Preconditions:** User owns a project.
- **Steps:**
  1. User deletes project → `deleted_at` set
  2. Undo toast appears (info type)
  3. Project moves to Trash list on landing page
  4. User clicks undo within toast duration → `deleted_at` cleared
  5. Project restored to original list
  6. User deletes again
  7. After `soft_delete_countdown` days, Celery cleanup job permanently deletes
  8. All related records cascade-deleted
- **Expected result:** Soft delete reversible. Permanent delete happens after countdown. CASCADE works correctly.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-013: Requirements Structure Undo/Redo Across AI and User Actions

- **Features involved:** F-3.7, F-2.17, F-3.2
- **Description:** AI modifies requirements structure, user undoes AI action, user makes their own change, redo of AI action unavailable (branched history).
- **Preconditions:** Project with existing requirements structure elements.
- **Steps:**
  1. AI creates 2 new requirements elements via `update_requirements_structure`
  2. Undo button shows "Undo AI Action"
  3. User clicks undo → AI changes reverted
  4. User creates their own requirement element
  5. Redo button disabled or shows that AI action cannot be redone (branched)
  6. User undoes their own action → "Undo" label
  7. Redo available → "Redo" label
- **Expected result:** Undo/redo stack correctly tracks AI vs user actions. Labels reflect action source. Branch history handled correctly.
- **Priority:** P1
- **Layer:** Frontend Unit (Redux slice)

---

### SCN-014: Notification Preferences → Selective Email Delivery

- **Features involved:** F-12.5, F-8.2
- **Description:** User disables email notification for collaboration invitations, receives in-app but not email notification.
- **Preconditions:** User with `email_notification_preferences: { collaboration_invitation: false }`.
- **Steps:**
  1. Another user sends collaboration invitation
  2. Notification service receives event
  3. Persistent notification created (bell) → delivered
  4. Email notification check → preferences say disabled → email NOT sent
  5. User sees notification in bell but receives no email
- **Expected result:** Email preferences respected. In-app always delivered. Email selectively suppressed.
- **Priority:** P2
- **Layer:** Integration

---

### SCN-015: Multi-Reviewer Conflict Resolution

- **Features involved:** F-4.11, F-1.5
- **Description:** Two reviewers take conflicting actions on the same project. Latest action wins.
- **Preconditions:** Project in "in_review" state with 2 reviewers assigned.
- **Steps:**
  1. Reviewer A starts writing accept comment
  2. Reviewer B rejects project (with comment) — state → `rejected`
  3. Reviewer A submits accept — state → `accepted` (latest wins)
  4. Both actions recorded in timeline
  5. Owner receives notification for latest state (accepted)
- **Expected result:** No error on conflicting actions. Latest action determines state. Full audit trail preserved.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-016: i18n Language Switch → Full Application

- **Features involved:** F-16.1 (FA-16)
- **Description:** User switches language from German to English, entire UI updates including dynamic content.
- **Preconditions:** Both `de.json` and `en.json` translation files complete.
- **Steps:**
  1. User opens language selector (navbar)
  2. Selects English
  3. Language preference saved to localStorage
  4. All static labels update immediately
  5. Date/number formatting updates to English locale
  6. AI language detection picks up preference for next processing cycle
  7. Page refresh maintains selected language
- **Expected result:** Full UI translation. Persistence across sessions. AI adapts language.
- **Priority:** P2
- **Layer:** E2E

---

### SCN-017: Read-Only Link Access → Edit Attempt → Denied

- **Features involved:** F-8.3, F-8.1
- **Description:** External user with share link can view project but all mutations are blocked.
- **Preconditions:** Project with generated share_link_token. User B is authenticated but not owner/collaborator.
- **Steps:**
  1. User B navigates to `/project/:uuid?share=<token>`
  2. Project loads in read-only mode — chat visible, requirements structure visible
  3. User B attempts to send chat message → 403
  4. User B attempts to modify requirements structure → 403
  5. User B attempts to edit requirements document → 403
  6. User B sees "View Only" indicator in workspace header
- **Expected result:** All read operations succeed. All write operations return 403. No WebSocket subscription for edits.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-018: Admin Context Update → Re-Indexing → Affects Future AI Processing

- **Features involved:** F-11.2, F-2.15, F-2.16
- **Description:** Admin updates company context (global or type-specific), re-indexing pipeline rebuilds RAG chunks, subsequent AI processing uses new context.
- **Preconditions:** Existing context_agent_bucket with old content. Project with active requirements assembly.
- **Steps:**
  1. Admin updates context agent bucket (software type) with new company information
  2. PUT /api/admin/ai-context/software succeeds
  3. Re-indexing pipeline triggers: old context_chunks deleted, new chunks created with embeddings
  4. User asks about company context in existing software project
  5. Facilitator delegates to Context Agent
  6. Context Agent retrieves chunks from the NEW content (not old)
  7. Response reflects updated company information
- **Expected result:** Re-indexing is atomic (DELETE + INSERT). New RAG queries return new content. In-progress projects see updated context on next delegation.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-019: Collaborator Removal → Notification → Access Revoked

- **Features involved:** F-8.4, F-12.5, F-6.4
- **Description:** Owner removes a collaborator, removed user loses access immediately.
- **Preconditions:** Project with owner + 2 collaborators, all connected via WebSocket.
- **Steps:**
  1. Owner removes Collaborator B via DELETE /api/projects/:id/collaborators/:userId
  2. Collaborator B receives "Removed from project" notification (bell + warning toast)
  3. Collaborator B's WebSocket receives `collaborator_removed` event
  4. Collaborator B's workspace transitions to read-only / redirect
  5. Collaborator B attempts API call → 403 ACCESS_DENIED
  6. Other collaborator (A) sees updated presence (B removed)
  7. Project visibility stays "collaborating" if A remains
- **Expected result:** Access revoked immediately. Notification sent. WebSocket cleans up removed user's subscription.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-020: Type-Specific Requirements Structure (Software vs Non-Software)

- **Features involved:** F-3.1, F-3.2, F-3.3
- **Description:** Software project uses Epics/User Stories structure, Non-Software project uses Milestones/Work Packages structure.
- **Preconditions:** Two projects created, one Software type, one Non-Software type.
- **Steps:**
  1. User creates Software project → requirements panel shows Epic/User Story accordion
  2. User creates Epic "User Management" → contains User Stories
  3. AI suggests User Story under Epic → structured correctly
  4. User creates Non-Software project → requirements panel shows Milestone/Work Package accordion
  5. User creates Milestone "Phase 1" → contains Work Packages
  6. AI suggests Work Package under Milestone → structured correctly
- **Expected result:** Type determines structure. AI tools adapt to project type. No mix of structures in single project.
- **Priority:** P1
- **Layer:** Integration

---

### SCN-021: Multi-User Requirements Editing → Conflict Resolution

- **Features involved:** F-3.5, F-3.6, F-6.4
- **Description:** Two users editing requirements structure simultaneously, changes broadcast in real-time.
- **Preconditions:** Project with 2 collaborators connected via WebSocket.
- **Steps:**
  1. User A creates new Epic "Authentication"
  2. WebSocket broadcasts `requirements.structure.created` to User B
  3. User B sees new Epic appear in their panel
  4. User A and User B simultaneously edit different User Stories
  5. Both changes persisted (no conflict, different elements)
  6. Both users see each other's changes via WebSocket
  7. User A and User B edit the same Epic title simultaneously
  8. Last write wins, both see final state
- **Expected result:** Real-time sync works. No data loss. Last write wins for conflicts.
- **Priority:** P1
- **Layer:** Integration

---

## 2. User Journey Tests

### JOURNEY-001: New User — First Project to Accepted

- **Description:** Complete lifecycle of a user's first project from creation to acceptance.
- **Features covered:** F-7.1/F-7.2, F-9.2, F-2.1, F-2.3, F-2.10, F-2.17, F-4.1, F-4.3, F-1.5, F-4.10, F-4.11
- **Steps:**
  1. User logs in (dev bypass or Azure AD) → Landing page
  2. Clicks "New Project" → Modal with type selection appears
  3. Selects "Software" → Project created, navigated to workspace
  4. User sends first message → AI responds with greeting + initial question
  5. Title auto-generated from conversation
  6. User and AI exchange 5-6 messages → Requirements structure populated with Epics/User Stories
  7. User switches to Requirements tab → Sees structured accordion with AI-created elements
  8. User edits a User Story → AI modification indicator clears
  9. User opens Review tab → Requirements document generates on first open
  10. User reviews readiness evaluation → All sections sufficient
  11. User submits with message and reviewer assignment
  12. Reviewer opens Review page → Sees project in "Assigned to me"
  13. Reviewer reads requirements document, posts comment, accepts
  14. Owner receives acceptance notification
  15. Owner visits project → Everything read-only
- **Assertions at each step:** Page navigation correct, API calls succeed, WebSocket events received, state transitions valid, notifications delivered.
- **Data cleanup:** Delete created project and related records.

---

### JOURNEY-002: Collaborative Requirements Assembly Session

- **Description:** Multi-user real-time collaboration on a single project.
- **Features covered:** F-8.1, F-8.2, F-6.3, F-6.4, F-2.5, F-3.5, F-3.6
- **Steps:**
  1. User A creates project and starts requirements assembly
  2. User A invites User B → Notification sent
  3. User B accepts invitation → Joins project
  4. Both users visible in presence indicators
  5. User B sends chat message → User A sees it in real-time
  6. AI addresses both users by name in response
  7. User A creates Epic → User B sees it appear in real-time
  8. User B creates User Story under different Epic simultaneously → No conflict
  9. Both users see each other's structure changes on commit
- **Assertions at each step:** Presence updates, message delivery, requirements structure sync, AI multi-user behavior.
- **Data cleanup:** Delete project and invitations.

---

### JOURNEY-003: Project Rejection → Rework → Resubmission → Acceptance

- **Description:** Full rejection-rework cycle demonstrating the iterative review process.
- **Features covered:** F-1.5, F-4.5, F-4.6, F-4.7, F-4.11
- **Steps:**
  1. Project submitted (version 1) → In Review
  2. Reviewer rejects with feedback → Rejected
  3. Owner reworks requirements assembly (adds more detail)
  4. Owner regenerates requirements document selectively
  5. Owner resubmits (version 2) → In Review
  6. Reviewer sees v1 and v2 linked in timeline
  7. Reviewer downloads both PDFs for comparison
  8. Reviewer accepts → Accepted
  9. Timeline shows full history: submit → reject → resubmit → accept
- **Assertions at each step:** Version numbers correct, PDFs accessible, timeline entries complete.
- **Data cleanup:** Delete project and related records.

---

### JOURNEY-004: Admin Configuration and Monitoring

- **Description:** Admin configures the platform and monitors system health.
- **Features covered:** F-11.1, F-11.2, F-11.3, F-11.4, F-11.6
- **Steps:**
  1. Admin logs in → Navbar shows Admin link
  2. Navigates to Admin Panel → 4 tabs visible
  3. AI Context tab: enters global context + software-specific context + non-software-specific context
  4. Parameters tab: adjusts debounce timer and message cap
  5. Monitoring tab: views active connections, projects by state
  6. Users tab: searches for a user → sees stats
  7. Returns to requirements assembly → New parameters take effect
- **Assertions at each step:** Role-based access works, context saved, parameters saved and effective, monitoring data displayed.
- **Data cleanup:** Reset parameters to defaults.

---

## 3. Concurrency Scenarios

### CONC-001: Simultaneous Chat Messages from Multiple Users

- **Description:** Two users send chat messages at nearly the same time on the same project.
- **Actors:** User A and User B (both collaborating)
- **Steps:**
  1. User A sends message at T+0ms
  2. User B sends message at T+50ms
  3. Both messages saved with correct `created_at` ordering
  4. Both messages broadcast via WebSocket to both users
  5. Debounce timer resets on User B's message
  6. AI processes all messages when debounce expires
- **Expected:** Both messages persisted in correct order. No lost messages. AI sees both messages.
- **Priority:** P1

---

### CONC-002: Requirements Structure Edit During AI Update

- **Description:** User edits requirements structure while AI is creating/modifying elements.
- **Actors:** User, AI (via Facilitator with update_requirements_structure tool)
- **Steps:**
  1. AI processing started → Facilitator updating requirements structure
  2. User edits an existing Epic (title change → REST PATCH)
  3. AI creates new User Story (via gRPC → REST)
  4. User's edit and AI's creation both succeed
  5. WebSocket broadcasts both changes
  6. Final structure includes user's updated Epic AND AI's new User Story
- **Expected:** No data corruption. Both changes applied. Last-write-wins for any field-level conflict on same element.
- **Priority:** P1

---

### CONC-003: Concurrent Review Actions by Multiple Reviewers

- **Description:** Two reviewers act on the same project simultaneously.
- **Actors:** Reviewer A, Reviewer B
- **Steps:**
  1. Reviewer A submits "accept" at T+0ms
  2. Reviewer B submits "reject" at T+100ms
  3. Both state change requests processed
  4. Latest action (reject) determines final state
  5. Both actions recorded in timeline with timestamps
  6. Owner notified of final state only
- **Expected:** No error. Latest action wins. Timeline shows both actions for audit.
- **Priority:** P1

---

### CONC-004: Duplicate Collaboration Invitation

- **Description:** Owner sends invitation while invitee is simultaneously accepting a previous invitation.
- **Actors:** Owner, Invitee
- **Steps:**
  1. Invitee clicks accept on existing invitation at T+0ms
  2. Owner sends new invitation to same user at T+50ms
  3. First accept succeeds → collaborator created
  4. New invitation fails (UNIQUE constraint: user already collaborating)
- **Expected:** No duplicate collaborator records. Error handled gracefully.
- **Priority:** P2

---

### CONC-005: AI Processing Restart on New Message

- **Description:** New chat message arrives while AI is mid-processing.
- **Actors:** User, AI pipeline
- **Steps:**
  1. AI processing started for messages 1-3
  2. User sends message 4 during processing
  3. AI pipeline detects new message → aborts current processing
  4. Debounce timer restarts
  5. After debounce, AI processes messages 1-4 together
  6. Only one response generated (for the restarted cycle)
- **Expected:** No duplicate AI responses. All messages included in final processing. Abort is clean (no partial state).
- **Priority:** P1

---

## 4. Error Propagation Scenarios

### ERR-001: AI Service Unavailable During Chat Processing

- **Trigger:** AI service returns gRPC UNAVAILABLE or times out during Facilitator invocation.
- **Expected behavior:**
  1. Gateway retries 3x with exponential backoff (1s, 2s, 4s)
  2. After 3 failures: error event published
  3. WebSocket broadcasts `ai.processing.failed` event
  4. Frontend shows error toast (F-14.1)
  5. Chat remains functional (user can still send messages)
  6. Requirements structure unchanged (no partial AI modifications)
  7. Rate limit counter NOT incremented (AI didn't complete)
- **Tests:** Assert retry count, error toast content, no partial state, chat remains usable.
- **Priority:** P1

---

### ERR-002: PDF Generation Service Failure

- **Trigger:** PDF service returns error during requirements document version creation.
- **Expected behavior:**
  1. Requirements document version record created (sections preserved)
  2. `pdf_file_path` remains NULL
  3. Error toast shown to user: "PDF generation failed"
  4. User can retry PDF generation manually
  5. Requirements document data intact — no data loss
- **Tests:** Assert requirements document version exists without PDF. Assert retry works. Assert no data corruption.
- **Priority:** P1

---

### ERR-003: WebSocket Disconnection During Collaborative Editing

- **Trigger:** Network interruption drops WebSocket connection for one user.
- **Expected behavior:**
  1. Disconnected user sees offline banner (F-6.2)
  2. Chat and requirements structure lock for disconnected user
  3. Other users see disconnected user leave presence
  4. Reconnection with exponential backoff
  5. On reconnect: state synced from server (latest messages + requirements structure)
  6. Any messages sent by others during offline period appear on reconnect
  7. Offline banner disappears, chat/requirements structure unlock
- **Tests:** Assert offline UI state. Assert state sync completeness. Assert no missed messages.
- **Priority:** P1

---

### ERR-004: gRPC Failure Between Gateway and Core

- **Trigger:** Core service temporarily unavailable during REST API call.
- **Expected behavior:**
  1. Gateway catches gRPC error
  2. Returns appropriate HTTP error (502 or 503) to frontend
  3. Frontend shows error toast
  4. No partial writes to gateway-owned tables
  5. Request can be retried by user
- **Tests:** Assert HTTP error code. Assert no partial state. Assert error message useful.
- **Priority:** P1

---

### ERR-005: RabbitMQ Broker Down

- **Trigger:** Message broker unavailable when event publishing attempted.
- **Expected behavior:**
  1. Publisher catches connection error
  2. Event queued in local retry buffer
  3. Primary operation (e.g., chat message creation) still succeeds
  4. Events delivered when broker recovers
  5. If retry buffer full: events logged to DLQ monitoring
  6. Admin alert triggered if DLQ threshold exceeded
- **Tests:** Assert primary operation succeeds. Assert events eventually delivered. Assert monitoring alert.
- **Priority:** P1

---

### ERR-006: Azure AD Token Expiry Mid-Session

- **Trigger:** User's MSAL access token expires during active requirements assembly.
- **Expected behavior:**
  1. Frontend detects token approaching expiry
  2. Silent token refresh attempted via MSAL
  3. If refresh succeeds: seamless, no user impact
  4. If refresh fails: redirect to login
  5. After re-login: return to previous project page
  6. WebSocket reconnects with new token
- **Tests:** Assert silent refresh works. Assert redirect on failure. Assert session restoration.
- **Priority:** P1

---

### ERR-007: AI Guardrail Violation (Fabrication Detection)

- **Trigger:** Summarizing AI generates content not grounded in chat/requirements data.
- **Expected behavior:**
  1. Output validation detects fabricated content
  2. Fabricated section replaced with "Not enough information" (F-4.2)
  3. Guardrail event logged (monitoring)
  4. User sees safe output (no fabrication)
  5. Readiness evaluation marks affected section as "insufficient"
- **Tests:** Assert fabrication caught. Assert safe fallback content. Assert monitoring log.
- **Priority:** P1

---

### ERR-008: Database Connection Pool Exhaustion

- **Trigger:** High concurrent load exhausts PostgreSQL connection pool.
- **Expected behavior:**
  1. New requests queue for available connection
  2. If queue timeout exceeded: 503 Service Unavailable
  3. Existing connections continue functioning
  4. Pool recovers as requests complete
  5. No connection leaks (all connections returned to pool)
- **Tests:** Assert graceful degradation. Assert recovery. Assert no leaks.
- **Priority:** P2

---

## 5. Scenario Statistics

| Category | Count | P1 | P2 |
|----------|-------|----|----|
| Cross-Feature Scenarios | 21 | 18 | 3 |
| User Journey Tests | 4 | 4 | 0 |
| Concurrency Scenarios | 5 | 4 | 1 |
| Error Propagation Scenarios | 8 | 7 | 1 |
| **Total** | **38** | **33** | **5** |
