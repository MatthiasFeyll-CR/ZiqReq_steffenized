# Milestone 18: E2E Workspace, Chat & Board Tests

## Overview
- **Execution order:** 18 (runs after M17)
- **Estimated stories:** 10
- **Dependencies:** M17 (test infrastructure + foundation tests)
- **Type:** E2E Testing

## Purpose

Test the core idea workspace end-to-end: workspace layout and section behavior, chat features (messages, reactions, @mentions, AI responses), digital board (nodes, connections, interactions, undo/redo), real-time collaboration via WebSocket, and idle state handling.

## Features Tested

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-1 | Idea Workspace (layout, sections, locking, lifecycle) | P1 | docs/01-requirements/features.md |
| FA-2 | AI Facilitation (modes, reactions, @mentions, rate limiting, title gen) | P1 | docs/01-requirements/features.md |
| FA-3 | Digital Board (nodes, connections, interactions, undo/redo) | P1 | docs/01-requirements/features.md |
| FA-6 | Real-Time Collaboration (WebSocket, presence, offline) | P1 | docs/01-requirements/features.md |
| FA-15 | Idle State (detection, disconnect, return) | P2 | docs/01-requirements/features.md |

## Story Outline

### S1: E2E Workspace Layout & Navigation (FA-1)
- **Test: Workspace loads correctly** — Navigate to `/idea/<uuid>`, verify two-panel layout: chat (left), tabbed panel (right) with Board and Review tabs
- **Test: Draggable divider** — Drag the panel divider left/right, verify panels resize
- **Test: Board tab default active** — Board tab is visible/active by default in right panel
- **Test: Switch between Board and Review tabs** — Click Review tab → review content shows, click Board tab → board content shows
- **Test: Inline title editing (F-1.6)** — Click idea title → becomes editable, type new title → title updates, browser tab title updates
- **Test: Browser tab title (F-1.8)** — Navigate to idea → browser tab shows idea title, change title → tab updates
- **Test: UUID-based routing (F-1.7)** — Navigate to `/idea/<valid-uuid>` → workspace loads, navigate to `/idea/<invalid-uuid>` → error/404

**Acceptance criteria:**
- [ ] Workspace layout renders correctly with two panels
- [ ] Tab switching works
- [ ] Title inline editing works and updates browser tab
- [ ] UUID routing works for valid and invalid UUIDs

### S2: E2E Workspace Section Visibility & Locking (FA-1)
- **Test: Review section hidden for new idea (F-1.2)** — New idea (open state) → review section below fold is hidden/inaccessible
- **Test: Review section visible after submit (F-1.2)** — Submit idea for review (via API setup) → review section visible below fold
- **Test: Auto-scroll on state transition (F-1.3)** — Open idea → top section visible. Set state to in_review (via API) → page scrolls to review section
- **Test: Section locking — Open state (F-1.4)** — Open idea → brainstorming editable, review hidden
- **Test: Section locking — In Review state (F-1.4)** — In-review idea → brainstorming locked (read-only), review section active
- **Test: Section locking — Rejected state (F-1.4)** — Rejected idea → brainstorming editable (unlocked for rework), review visible but read-only
- **Test: Section locking — Accepted state (F-1.4)** — Accepted idea → everything read-only
- **Test: Section locking — Dropped state (F-1.4)** — Dropped idea → everything read-only

**Acceptance criteria:**
- [ ] Review section visibility follows state rules
- [ ] Auto-scroll triggers on state transitions
- [ ] Section locking enforced for all 5 states

### S3: E2E Idea Lifecycle State Transitions (FA-1)
- **Test: Open → In Review (F-1.5)** — Owner submits idea → state changes, brainstorming locks, review activates
- **Test: In Review → Accepted (F-1.5)** — Reviewer accepts → everything read-only
- **Test: In Review → Rejected (F-1.5)** — Reviewer rejects with mandatory comment → brainstorming unlocks for rework
- **Test: In Review → Dropped (F-1.5)** — Reviewer drops with mandatory comment → everything read-only
- **Test: Rejected → In Review (F-1.5)** — Owner resubmits after rejection → back to in_review
- **Test: Accepted → In Review (undo) (F-1.5)** — Reviewer undoes accept with mandatory comment → back to in_review
- **Test: Dropped → In Review (undo) (F-1.5)** — Reviewer undoes drop with mandatory comment → back to in_review
- **Test: Mandatory comment enforcement** — Attempt to reject/drop without comment → action blocked

**Acceptance criteria:**
- [ ] All state transitions work as specified
- [ ] Mandatory comments enforced for reject/drop/undo actions
- [ ] UI updates correctly after each transition

### S4: E2E Chat — Messages & AI Response (FA-2)
- **Test: Send chat message** — Type message in chat input, submit → message appears in chat with user name and timestamp
- **Test: AI responds to message (mocked) (F-2.1, F-2.10)** — Send message → AI processing indicator appears → AI response appears in chat (mocked)
- **Test: Agent mode — Interactive (F-2.1)** — Default mode is Interactive, AI responds automatically
- **Test: Agent mode — Silent (F-2.1)** — Switch to Silent mode via dropdown → send message → AI does NOT respond. Type `@ai` → AI responds
- **Test: AI title generation (F-2.3)** — Send first message → AI generates title (visible in header + browser tab)
- **Test: Title generation disabled after manual edit (F-2.3)** — Edit title manually → send more messages → AI does not overwrite the title
- **Test: AI processing indicator (F-2.12)** — Send message → "AI is processing" indicator visible → disappears after AI responds
- **Test: Multiple messages before AI responds** — Send 3 messages rapidly → AI processes all together, responds once

**Acceptance criteria:**
- [ ] Chat messages send and display correctly
- [ ] AI responses appear (mocked) with processing indicator
- [ ] Agent mode switching works (Interactive/Silent)
- [ ] Title generation and manual override work

### S5: E2E Chat — Reactions, @Mentions, Rate Limiting (FA-2)
- **Test: AI reactions (F-2.7)** — AI reacts to user message (mocked) → reaction emoji visible on message
- **Test: User reactions to other users (F-2.8)** — In multi-user context (via API setup), User A reacts to User B's message → reaction visible
- **Test: Cannot react to AI messages (F-2.8)** — Verify reaction UI is not available on AI messages
- **Test: @Mentions dropdown (F-2.9)** — Type `@` in chat → dropdown shows users and `@ai`
- **Test: @Mention sends notification** — @mention another user → notification created (verify via API or bell)
- **Test: @ai forces response in silent mode (F-2.9)** — In Silent mode, send `@ai message` → AI responds
- **Test: Rate limiting — lockout (F-2.11)** — Send messages up to the cap → chat input locks with warning toast
- **Test: Rate limiting — unlock after AI processes (F-2.11)** — Hit rate limit → wait for AI to process → chat input unlocks
- **Test: Rate limiting — board still editable during lockout (F-2.11)** — Chat locked but board interactions still work

**Acceptance criteria:**
- [ ] AI and user reactions display correctly
- [ ] @Mentions dropdown works and triggers notifications
- [ ] Rate limiting locks/unlocks chat correctly
- [ ] Board remains editable during chat lockout

### S6: E2E Digital Board — Core (FA-3)
- **Test: Board renders with minimap (F-3.3)** — Open Board tab → canvas renders with minimap, zoom controls, background grid
- **Test: Create Box node (F-3.1)** — Click "Add Box" → new Box appears on canvas with editable title and body
- **Test: Edit Box content (F-3.2)** — Double-click Box → edit title and body (bullet points) → changes saved
- **Test: Create Free Text (F-3.1)** — Add Free Text node → text on canvas with no card/border/background
- **Test: Create Group (F-3.1)** — Add Group node → container with optional label, can contain children
- **Test: Create connection (F-3.2)** — Connect two nodes with a line/edge → connection visible
- **Test: Edit connection label (F-3.2)** — Double-click connection → add/edit sticky text label
- **Test: Delete selected nodes (F-3.3)** — Select node(s) → click Delete Selected → nodes removed
- **Test: Zoom and fit view (F-3.3)** — Use zoom controls (in/out, fit view) → canvas zooms appropriately
- **Test: Lock toggle per node (F-3.2)** — Lock a node → editing disabled on that node. Unlock → editing re-enabled

**Acceptance criteria:**
- [ ] All 3 node types (Box, Group, Free Text) can be created and edited
- [ ] Connections between nodes work with labels
- [ ] Minimap, zoom, fit view functional
- [ ] Node locking works

### S7: E2E Digital Board — Advanced Interactions (FA-3)
- **Test: Drag to move items (F-3.2)** — Drag a Box → position updates
- **Test: Drag Box into Group (F-3.2)** — Drag a Box over a Group → Box becomes child of Group, moves with Group
- **Test: Drag Box out of Group (F-3.2)** — Drag a Box out of a Group → Box becomes top-level again
- **Test: Resize Group (F-3.2)** — Resize a Group → dimensions change
- **Test: Nested Groups (F-3.1)** — Create Group inside Group → nesting works
- **Test: Multi-select with Ctrl+drag (F-3.2)** — Ctrl+drag to select multiple nodes → all selected nodes highlighted
- **Test: AI-created items show robot badge (F-3.2)** — Create idea with AI-generated board items (mocked) → robot badge visible on AI-created nodes
- **Test: AI modification indicators (F-3.4)** — AI modifies board item → indicator visible. Click/select item → indicator fades
- **Test: Board item reference action (F-3.8)** — Click reference button on a Box → formatted reference inserted into chat input

**Acceptance criteria:**
- [ ] Drag, drop, nesting, resize all work
- [ ] Multi-select works
- [ ] AI badges and indicators display and clear correctly
- [ ] Board item reference to chat works

### S8: E2E Board Undo/Redo (FA-3)
- **Test: Undo node creation (F-3.7)** — Create Box → click Undo → Box removed
- **Test: Redo node creation (F-3.7)** — Create Box → Undo → Redo → Box restored
- **Test: Undo content edit (F-3.7)** — Edit Box body → Undo → original content restored
- **Test: Undo connection creation (F-3.7)** — Create connection → Undo → connection removed
- **Test: Undo AI action with label (F-3.7)** — AI creates nodes (mocked) → Undo button shows "Undo AI Action"
- **Test: Redo AI action with label (F-3.7)** — Undo AI action → Redo button shows "Redo AI Action"
- **Test: Multiple sequential undos (F-3.7)** — Create Box, edit, create connection → Undo x3 → all reverted
- **Test: Undo after delete (F-3.7)** — Delete node → Undo → node restored

**Acceptance criteria:**
- [ ] Undo/redo works for all board operations
- [ ] AI vs user action labels display correctly
- [ ] Multiple sequential undos work
- [ ] Redo available after undo

### S9: E2E Real-Time & WebSocket (FA-6)
- **Test: Chat message real-time delivery (F-6.4)** — User A sends message → User B sees it appear in real-time (two browser contexts)
- **Test: Board sync — content commit (F-3.6)** — User A edits Box and commits → User B sees updated content
- **Test: Board sync — selection highlight (F-3.5, F-3.6)** — User A selects a node → User B sees highlight with User A's name
- **Test: Presence tracking (F-6.3)** — User A and User B on same idea → both visible in presence indicators
- **Test: Presence — user leaves** — User B closes tab → User A sees User B disappear from presence
- **Test: Connection state indicator (F-6.6)** — Connected → green "Online" indicator in navbar
- **Test: Offline banner (F-6.2)** — Simulate disconnect → "Currently offline" banner appears, chat/board lock
- **Test: Reconnection (F-6.5)** — Disconnect → reconnect → banner disappears, state syncs, chat/board unlock

**Acceptance criteria:**
- [ ] Chat and board changes broadcast in real-time between users
- [ ] Presence indicators show/update correctly
- [ ] Offline banner appears on disconnect
- [ ] Reconnection restores full state

### S10: E2E Idle State (FA-15)
- **Test: Idle detection (F-15.1)** — No mouse movement for configurable period → presence indicator changes to grey/dimmed
- **Test: Idle on tab navigation (F-15.1)** — Navigate away from browser tab → idle triggers immediately
- **Test: Return from idle (F-15.3)** — Go idle → move mouse → idle ends, presence returns to online
- **Test: Prolonged idle disconnects (F-15.2)** — Stay idle beyond disconnect threshold → offline banner appears, connection closed
- **Test: Return after prolonged idle (F-15.3)** — Disconnect due to idle → move mouse → reconnection triggers, state syncs

**Acceptance criteria:**
- [ ] Idle detection triggers correctly (inactivity + tab change)
- [ ] Presence indicator reflects idle state
- [ ] Prolonged idle disconnects the connection
- [ ] Return from idle restores connection and state

## Execution Rule

**After implementing EACH story above:**
1. Run `npx playwright test --config=e2e/playwright.config.ts`
2. ALL tests must pass (including M17 tests)
3. If any test fails → identify root cause → fix test or production code → all green before continuing

## Per-Story Complexity Assessment

| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Workspace Layout | ~6,000 | FA-1, pages.md | 1-2 | Low | — |
| 2 | Section Visibility & Locking | ~8,000 | F-1.2, F-1.3, F-1.4 | 1-2 | Medium | State setup complexity |
| 3 | Lifecycle State Transitions | ~8,000 | F-1.5 | 1-2 | Medium | Multi-role setup |
| 4 | Chat — Messages & AI | ~8,000 | F-2.1, F-2.3, F-2.10, F-2.12 | 1-2 | Medium | AI mock timing |
| 5 | Chat — Reactions, Mentions, Rate Limit | ~8,000 | F-2.7–F-2.11 | 1-2 | Medium | Multi-user setup |
| 6 | Board — Core | ~8,000 | F-3.1–F-3.3 | 1-2 | Medium | Canvas interaction |
| 7 | Board — Advanced Interactions | ~7,000 | F-3.2, F-3.4, F-3.8 | 1-2 | Medium | Drag simulation |
| 8 | Board Undo/Redo | ~6,000 | F-3.7 | 1-2 | Medium | State verification |
| 9 | Real-Time & WebSocket | ~10,000 | FA-6, F-3.5, F-3.6 | 1-2 | High | Two browser contexts |
| 10 | Idle State | ~5,000 | FA-15 | 1-2 | Medium | Timer manipulation |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~74,000
- **Cumulative domain size:** Medium–Large
- **Information loss risk:** Medium (score: 6)
- **Context saturation risk:** Medium

## Milestone Acceptance Criteria
- [ ] All workspace layout and section tests pass
- [ ] All chat feature tests pass (messages, AI, reactions, mentions, rate limiting)
- [ ] All board tests pass (CRUD, interactions, undo/redo)
- [ ] Real-time collaboration tested with two browser contexts
- [ ] Idle state detection and recovery tested
- [ ] All M17 tests still pass (no regressions)
- [ ] Any production bugs discovered are fixed and documented

## Notes
- Real-time tests (S9) require two browser contexts (Playwright supports this with `browser.newContext()`)
- Idle state tests (S10) may need to manipulate timers or use shorter admin-configured timeouts for test speed
- Board interaction tests depend on React Flow's DOM structure — use robust selectors
- AI mock responses must be deterministic; verify the AI service's `AI_MOCK_MODE` returns consistent fixtures
