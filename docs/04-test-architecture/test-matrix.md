# Test Matrix

> **Status:** Definitive (revised)
> **Date:** 2026-03-05 (originally 2026-03-04)
> **Author:** Test Architect (Phase 4b)
> **Input:** All validated specs from phases [1]–[4]
> **Revision:** Added 26 missing test cases identified during improvement assessment

This document maps every feature, API endpoint, data entity, and page to specific test cases at each testing layer. Every test case traces back to a requirement ID, endpoint, or entity.

**Priority definitions:**
- **P1 (Critical):** Must have for MVP. Blocks release if missing.
- **P2 (Important):** Should have. Addresses important edge cases and error paths.
- **P3 (Nice-to-have):** Can defer. Covers rare scenarios or polish.

---

## 1. Feature Tests

### FA-1: Idea Workspace

#### F-1.1: Idea Page Layout

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.1.01 | Unit | Two-panel layout renders with draggable divider | Default idea state | Chat left, Board/Review tabs right | P1 |
| T-1.1.02 | Unit | Divider drag resizes panels proportionally | Drag event to 30%/70% | Panels resize, min width respected | P2 |
| T-1.1.03 | Unit | Board tab is default active in context panel | Idea state = open | Board tab selected | P1 |

#### F-1.2: Section Visibility

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.2.01 | Unit | Review section hidden for never-submitted idea | `has_been_submitted=false` | Review section not in DOM | P1 |
| T-1.2.02 | Unit | Review section visible after first submission | `has_been_submitted=true` | Review section rendered | P1 |
| T-1.2.03 | Unit | Review section persists across all states after submission | States: open, in_review, rejected, accepted, dropped | Review section always visible | P1 |

#### F-1.3: Auto-Scroll on State Transition

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.3.01 | Unit | Scroll to brainstorming on `open` state entry | Navigate to idea in `open` state | scrollIntoView called on brainstorming section | P2 |
| T-1.3.02 | Unit | Scroll to review on `in_review` state entry | State changes to `in_review` | scrollIntoView called on review section | P2 |
| T-1.3.03 | Unit | Scroll to brainstorming on `rejected` state | State changes to `rejected` | scrollIntoView to brainstorming | P2 |

#### F-1.4: Section Locking

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.4.01 | Unit | Open state: brainstorming editable, review hidden | `state=open, has_been_submitted=false` | Chat input enabled, board editable | P1 |
| T-1.4.02 | Unit | In Review: brainstorming locked (read-only) | `state=in_review` | Chat input disabled, board read-only | P1 |
| T-1.4.03 | Unit | Rejected: brainstorming editable, review visible read-only | `state=rejected` | Chat enabled, review section read-only | P1 |
| T-1.4.04 | Unit | Accepted: everything read-only | `state=accepted` | All inputs disabled | P1 |
| T-1.4.05 | Unit | Dropped: everything read-only | `state=dropped` | All inputs disabled | P1 |

#### F-1.5: Idea Lifecycle State Transitions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.5.01 | Integration | Open → In Review via submit | POST /api/ideas/:id/submit | State = in_review, BRD version created | P1 |
| T-1.5.02 | Integration | In Review → Accepted via reviewer accept | POST /api/ideas/:id/review/accept | State = accepted | P1 |
| T-1.5.03 | Integration | In Review → Dropped via reviewer drop | POST /api/ideas/:id/review/drop with comment | State = dropped | P1 |
| T-1.5.04 | Integration | In Review → Rejected via reviewer reject | POST /api/ideas/:id/review/reject with comment | State = rejected | P1 |
| T-1.5.05 | Integration | Rejected → In Review via resubmit | POST /api/ideas/:id/submit | State = in_review, new BRD version | P1 |
| T-1.5.06 | Integration | Accepted → In Review via undo | POST /api/ideas/:id/review/undo with comment | State = in_review | P1 |
| T-1.5.07 | Integration | Dropped → In Review via undo | POST /api/ideas/:id/review/undo with comment | State = in_review | P1 |
| T-1.5.08 | Integration | Invalid transition: open → accepted rejected | POST /api/ideas/:id/review/accept on open idea | 400 error | P1 |
| T-1.5.09 | Integration | Multiple reviewers: latest action wins | Two reviewers act in sequence | Last action determines state | P2 |
| T-1.5.10 | E2E | Full lifecycle: create → submit → reject → resubmit → accept | Full user flow | All transitions complete correctly | P1 |

#### F-1.6: Inline Title Editing

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.6.01 | Unit | Title is editable by clicking | Click on title element | Title becomes input field | P1 |
| T-1.6.02 | Integration | Manual edit sets title_manually_edited permanently | PATCH /api/ideas/:id with title | `title_manually_edited=true` | P1 |
| T-1.6.03 | Unit | Browser tab title updates on title change | Title WebSocket event received | document.title updates | P2 |

#### F-1.7–F-1.8: UUID Routing, Browser Tab

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.7.01 | Unit | Route /idea/:uuid renders workspace | Navigate to /idea/valid-uuid | IdeaWorkspace component renders | P1 |
| T-1.7.02 | Unit | Invalid UUID shows 404 | Navigate to /idea/not-a-uuid | 404 page rendered | P2 |

---

### FA-2: AI Facilitation

#### F-2.1: Agent Modes

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.1.01 | Unit | Agent mode dropdown renders with Interactive/Silent | Default state | Dropdown with two options | P1 |
| T-2.1.02 | Integration | Agent mode change persists | PATCH /api/ideas/:id {agent_mode: "silent"} | Mode saved, WebSocket broadcast | P1 |
| T-2.1.03 | AI Agent | Silent mode: no AI response without @ai | `agent_mode=silent`, message without @ai | Facilitator returns no action | P1 |
| T-2.1.04 | AI Agent | Silent mode: @ai forces response | `agent_mode=silent`, message with @ai mention | Facilitator generates response | P1 |

#### F-2.3: Title Generation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.3.01 | AI Agent | Title generated from first message | First message in new idea | `update_title` tool called | P1 |
| T-2.3.02 | AI Agent | Title not updated when manually edited | `title_manually_edited=true` | `update_title` tool NOT called | P1 |
| T-2.3.03 | Unit | Title update animates | WebSocket title_update event | Animation triggers on title element | P2 |

#### F-2.2: Language Detection

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.2.01 | AI Agent | AI detects German and responds in German | German chat messages | Response in German | P1 |
| T-2.2.02 | AI Agent | AI detects English and responds in English | English chat messages | Response in English | P1 |
| T-2.2.03 | AI Agent | Initial language follows creator's app language | New idea, creator language = de | First AI response in German | P2 |

#### F-2.4–F-2.5: Decision Layer, Multi-User Awareness

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.4.01 | AI Agent | AI can decide "no action" — reacts instead | Message that needs no response | `react_to_message` called, no `send_chat_message` | P2 |
| T-2.5.01 | AI Agent | Single user: AI does not address by name | One collaborator on idea | Response does not contain username | P2 |
| T-2.5.02 | AI Agent | Multi-user: AI addresses by name | Multiple collaborators | Response contains @user reference | P2 |

#### F-2.6: Board Item References in Chat

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.6.01 | Unit | @board[uuid] rendered as clickable link | Chat message with `@board[node-uuid]` | Link renders with node title | P1 |
| T-2.6.02 | Unit | Click board reference navigates to Board tab and highlights | Click @board link | Board tab activated, node highlighted | P1 |
| T-2.6.03 | Unit | Deleted node reference shows placeholder | @board[deleted-uuid] | "deleted item" placeholder shown | P2 |

#### F-2.7–F-2.8: AI Reactions, User Reactions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.7.01 | AI Agent | AI reacts with valid reaction type | AI decides to react | `react_to_message` with thumbs_up/thumbs_down/heart | P1 |
| T-2.7.02 | Integration | AI reaction persisted correctly | AI reaction event processed | ai_reactions row with UNIQUE per message | P1 |
| T-2.8.01 | Integration | User can react to other user's message | POST /api/.../reactions {reaction_type: "thumbs_up"} | 201, reaction created | P1 |
| T-2.8.02 | Integration | User cannot react to AI message | POST reaction on AI message | 400 CANNOT_REACT_TO_AI | P1 |
| T-2.8.03 | Integration | User cannot react to own message | POST reaction on own message | 400 CANNOT_REACT_TO_SELF | P1 |
| T-2.8.04 | Integration | User cannot react twice to same message | POST duplicate reaction | 409 ALREADY_REACTED | P1 |
| T-2.8.05 | Integration | User can remove own reaction | DELETE reaction | 204, reaction removed | P1 |

#### F-2.9: @Mentions System

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.9.01 | Unit | Typing @ opens suggestion dropdown | Type "@" in chat input | Dropdown shows collaborators + @ai | P1 |
| T-2.9.02 | Unit | Selecting user inserts @user[uuid] in message | Select user from dropdown | Reference format inserted | P1 |
| T-2.9.03 | Unit | @user[uuid] renders as display name | Message with @user reference | Display name shown | P1 |

#### F-2.10: AI Response Timing (Debounce)

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.10.01 | AI Agent | Debounce waits configurable period before processing | Message sent | Processing starts after debounce_timer seconds | P1 |
| T-2.10.02 | AI Agent | New message during debounce resets timer | Two messages in quick succession | Only one processing cycle for both | P1 |
| T-2.10.03 | AI Agent | New message during processing aborts and restarts | Message during active cycle | Abort flag set, new cycle starts | P1 |

#### F-2.11: Rate Limiting

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.11.01 | Integration | Chat locked after cap reached | Send chat_message_cap messages | 429 RATE_LIMITED on next message | P1 |
| T-2.11.02 | Integration | Rate limit resets after AI processing complete | AI publishes ai.processing.complete | Chat unlocked | P1 |
| T-2.11.03 | Unit | Rate limit warning toast shown | rate_limit WebSocket event | Warning toast displayed | P2 |

#### F-2.12: AI Processing Indicator

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.12.01 | Unit | Indicator shows during ai_processing started | ai_processing {state: "started"} event | Indicator visible with animation | P1 |
| T-2.12.02 | Unit | Indicator hides on completed/failed | ai_processing {state: "completed"} | Indicator hidden | P1 |

#### F-2.14: Long Conversation Support (Context Window)

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.14.01 | Unit | Context window indicator renders with usage percentage | GET /api/ideas/:id/context-window response | Circular progress at correct percentage | P1 |
| T-2.14.02 | Unit | Hover shows context window details | Mouse hover on indicator | Tooltip with message counts | P2 |
| T-2.14.03 | AI Agent | Compression triggers at threshold | Context utilization > 60% | Context Compression agent invoked | P1 |

#### F-2.15: Company Context Awareness

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.15.01 | AI Agent | Facilitator delegates to Context Agent | Question about company systems | `delegate_to_context_agent` tool called | P1 |
| T-2.15.02 | Unit | Delegation message shows "researching" placeholder | delegation message_type received | De-emphasized message visible | P1 |
| T-2.15.03 | AI Agent | Context Agent grounded in retrieved chunks | RAG query with matching chunks | Response cites chunk content only | P1 |

#### F-2.17: AI Board Content Rules

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.17.01 | AI Agent | Board Agent creates one topic per box | Board instructions with multiple topics | Separate boxes per topic | P1 |
| T-2.17.02 | AI Agent | Board Agent uses bullet-point format for body | Box creation instruction | Body contains bullet points | P2 |
| T-2.17.03 | AI Agent | Board Agent organizes boxes into groups | Multiple boxes exist | Group node created containing boxes | P2 |

---

### FA-3: Digital Board

#### F-3.1: Node Types

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.1.01 | Unit | Box node renders with title + body | BoardNode {node_type: "box"} | Title and body visible | P1 |
| T-3.1.02 | Unit | Group node renders as container | BoardNode {node_type: "group"} | Container with children inside | P1 |
| T-3.1.03 | Unit | Free text renders without card border | BoardNode {node_type: "free_text"} | Text only, no background | P1 |
| T-3.1.04 | Unit | Nested groups render correctly | Group inside group | Correct visual nesting | P2 |

#### F-3.2: Board Interactions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.2.01 | Unit | Drag moves node | Drag event on box | Position updates | P1 |
| T-3.2.02 | Unit | Drag box into group attaches it | Drag box over group | parent_id set to group | P1 |
| T-3.2.03 | Unit | Drag box out of group detaches it | Drag box outside group | parent_id set to null | P1 |
| T-3.2.04 | Unit | Double-click opens content editor | Double-click on box | Edit mode activated | P1 |
| T-3.2.05 | Unit | Connection between nodes renders as edge | Two connected nodes | Edge line visible | P1 |
| T-3.2.06 | Unit | Double-click connection opens label editor | Double-click on edge | Label input shown | P2 |
| T-3.2.07 | Unit | Lock toggle prevents editing | Click lock on node | Edit mode disabled for that node | P1 |
| T-3.2.08 | Unit | AI-created items show robot badge | Node with created_by="ai" | Bot icon visible | P1 |

#### F-3.3: Board UI

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.3.01 | Unit | MiniMap renders and reflects board state | Board with multiple nodes | MiniMap shows all nodes | P2 |
| T-3.3.02 | Unit | Zoom controls work | Click zoom in/out/fit | Canvas zoom level changes | P2 |
| T-3.3.03 | Unit | Toolbar buttons trigger correct actions | Click Add Box, Delete, Fit View, Undo, Redo | Corresponding action dispatched | P1 |

#### F-3.4: AI Modification Indicators

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.4.01 | Unit | AI-modified indicator visible | Node with ai_modified_indicator=true | Gold dot/glow visible | P1 |
| T-3.4.02 | Unit | Indicator clears on user selection | User clicks/selects AI-modified node | ai_modified_indicator cleared via REST | P1 |

#### F-3.5–F-3.6: Multi-User Editing, Board Sync

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.5.01 | Unit | Selection highlight shows for other users | board_selection WebSocket event | Highlight with username visible | P1 |
| T-3.6.01 | WebSocket | board_selection event broadcasts to subscribers | User selects node | Other subscribed users receive event | P1 |
| T-3.6.02 | Integration | Content change broadcasts via WebSocket after REST persist | POST board node | WebSocket board_update event sent | P1 |

#### F-3.7: Undo/Redo

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.7.01 | Unit | Undo reverses last board action | Dispatch undo() | Previous state restored in Redux | P1 |
| T-3.7.02 | Unit | Redo re-applies undone action | Dispatch redo() | Action re-applied | P1 |
| T-3.7.03 | Unit | AI action undo shows "Undo AI Action" label | Undo stack entry with source="ai" | Label is "Undo AI Action" | P1 |
| T-3.7.04 | Unit | Undo stack bounded at 100 entries | Push 101 actions | Oldest entry dropped | P2 |
| T-3.7.05 | Integration | Undo sends REST PATCH to persist reverted state | Undo dispatched | REST call made with reverted data | P1 |

#### F-3.8: Board Item Reference Action

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-3.8.01 | Unit | Reference button visible on node hover | Hover over board node | Reference button in top-right | P1 |
| T-3.8.02 | Unit | Click reference inserts @board[uuid] into chat input | Click reference button | Chat input contains @board[node-uuid] format | P1 |

---

### FA-4: Review & BRD

#### F-4.1–F-4.2: BRD Generation, No Fabrication

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.1.01 | AI Agent | Summarizing AI generates all 6 sections | Full idea context | Output contains title, short_desc, workflow, department, capabilities, criteria | P1 |
| T-4.1.02 | AI Agent | Insufficient info yields "Not enough information" | Minimal chat (2 messages) | At least one section = "Not enough information" | P1 |
| T-4.2.01 | AI Agent | Fabrication validator flags unsourced claims | BRD with proper nouns not in chat/board | Fabrication flag raised | P1 |
| T-4.2.02 | AI Agent | Fabrication validator passes valid BRD | BRD with all claims traceable | No flags | P1 |

#### F-4.3: BRD Generation Trigger

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.3.01 | Integration | First Review tab open triggers BRD generation | POST /api/ideas/:id/brd/generate | 200, skeleton generated | P1 |
| T-4.3.02 | Integration | Regenerate button triggers selective regeneration | POST /api/ideas/:id/brd/regenerate | 202, job started | P1 |

#### F-4.4: Per-Section Editing & Lock

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.4.01 | Integration | Editing section auto-locks it | PATCH /api/ideas/:id/brd {sections: {short_description: "edited"}} | section_locks includes short_description | P1 |
| T-4.4.02 | Integration | Locked section excluded from regeneration | Regenerate with section locked | Locked section content unchanged | P1 |
| T-4.4.03 | Unit | Lock/unlock icon toggle works | Click lock icon | Lock state toggles | P1 |

#### F-4.5: Review Tab

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.5.01 | Unit | PDF preview renders | BRD with generated PDF | PDF visible in review tab | P1 |
| T-4.5.02 | Unit | Download button triggers PDF download | Click download in three-dot menu | File download initiated | P2 |
| T-4.5.03 | Unit | Edit area expands/collapses | Click expand | Edit panel slides left | P1 |

#### F-4.7: Document Versioning

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.7.01 | Integration | Submit creates immutable BRD version | POST /api/ideas/:id/submit | New brd_versions row | P1 |
| T-4.7.02 | Integration | Previous versions remain downloadable | GET /api/ideas/:id/brd/versions/:versionId/pdf | 200 with PDF | P1 |
| T-4.7.03 | Integration | Version number increments on resubmit | Submit twice | version_number 1 then 2 | P1 |

#### F-4.8: Document Readiness Evaluation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.8.01 | AI Agent | Readiness evaluation per section | Idea with mixed completeness | Per-section status (ready/insufficient) | P1 |
| T-4.8.02 | Unit | Progress indicator reflects readiness | readiness_evaluation in BRD response | Visual indicator shows completion | P2 |

#### F-4.9: Allow Information Gaps

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.9.01 | AI Agent | Gaps mode produces /TODO markers | allow_information_gaps=true, insufficient info | Output contains /TODO markers | P1 |
| T-4.9.02 | Integration | PDF generation rejected with /TODO markers | POST /api/ideas/:id/brd/generate-pdf with /TODO | 400 TODO_MARKERS_REMAINING | P1 |
| T-4.9.03 | Integration | Filling /TODO gap auto-locks section | PATCH section replacing /TODO | Section auto-locked | P1 |

#### F-4.10–F-4.11: Reviewer Assignment, Multiple Reviewers

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.10.01 | Integration | Submit with reviewer IDs creates assignments | POST submit with reviewer_ids | review_assignments created | P1 |
| T-4.10.02 | Integration | Submit without reviewers goes to shared queue | POST submit without reviewer_ids | Appears in "unassigned" list | P1 |
| T-4.11.01 | Integration | Any reviewer can independently act | Two reviewers assigned, one accepts | State = accepted | P1 |

#### F-4.12: Similar Ideas in Review Section

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.12.01 | Integration | Similar ideas shown to reviewer | GET /api/ideas/:id/review/similar | 200 + similar ideas list (declined merges + near-threshold) | P2 |
| T-4.12.02 | Unit | Similar ideas panel renders in review section | Similar ideas data | Cards with title, keywords, similarity info | P2 |

---

### FA-5: Similarity & Merge

#### F-5.1: Keyword Generation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.1.01 | AI Agent | Keyword Agent extracts keywords | Chat with clear direction | JSON array of keyword strings | P1 |
| T-5.1.02 | AI Agent | Keywords capped at max_keywords_per_idea | Input with many topics | Array length ≤ 20 | P1 |
| T-5.1.03 | AI Agent | Keywords are single abstract words | Any input | Each keyword is single word | P1 |

#### F-5.2: Background Keyword Matching

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.2.01 | Integration | Keyword overlap ≥ threshold triggers similarity.detected | Two ideas with 7+ shared keywords | Event published | P1 |
| T-5.2.02 | Integration | Dismissed pairs not re-matched | Declined merge request exists for pair | No event published | P1 |
| T-5.2.03 | Integration | Time window filter applies | Idea older than similarity_time_limit | Not matched | P2 |

#### F-5.3: AI Deep Comparison

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.3.01 | AI Agent | Deep Comparison returns structured output | Two similar ideas | {is_similar: bool, confidence: float, explanation, overlap_areas} | P1 |
| T-5.3.02 | AI Agent | Pydantic validation enforces output schema | Malformed output | Retry with format instruction | P1 |

#### F-5.5: Merge Flow

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.5.01 | Integration | Merge request creates pending record | POST /api/ideas/:id/merge-request | 201, merge_request with status=pending | P1 |
| T-5.5.02 | Integration | Target idea locked with merge request | Active merge request | merge_request_pending populated in idea response | P1 |
| T-5.5.03 | Integration | Accept merge triggers synthesis | POST /api/merge-requests/:id/accept | Event published, resulting_idea created | P1 |
| T-5.5.04 | Integration | Decline permanently dismisses pair | POST /api/merge-requests/:id/decline | Status=declined, pair never suggested again | P1 |
| T-5.5.05 | AI Agent | Merge Synthesizer produces synthesis + board instructions | Two idea contexts | {synthesis_message: string, board_instructions: array} | P1 |
| T-5.5.06 | E2E | Full merge flow end-to-end | Two similar ideas → detect → request → accept → merged idea | Merged idea created with combined content | P1 |

#### F-5.7: Permanent Dismissal

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.7.01 | Integration | Declined pair permanently excluded | Check merge_requests for declined status=pair | Query filters out declined pairs | P1 |

#### F-5.8: Manual Merge Request

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-5.8.01 | Integration | Manual merge via UUID | POST /api/ideas/:id/manual-merge {target_idea_id: uuid} | 201 merge request created | P1 |
| T-5.8.02 | Integration | Manual merge with invalid UUID | POST with non-existent target | 404 TARGET_NOT_FOUND | P1 |
| T-5.8.03 | Integration | Manual merge with own idea | POST targeting same idea | 400 CANNOT_MERGE_SELF | P1 |

---

### FA-6: Real-Time Collaboration

#### F-6.1: Session-Level Connection

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.1.01 | WebSocket | Connection with valid token succeeds | /ws/?token=valid_jwt | connected=True | P1 |
| T-6.1.02 | WebSocket | Connection with invalid token rejected | /ws/?token=expired | connected=False | P1 |
| T-6.1.03 | Unit | Exponential backoff on disconnect | Connection lost | Retry intervals: 1s, 2s, 4s... max 30s | P1 |

#### F-6.6: Connection State Indicator

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.6.01 | Unit | Green "Online" indicator when connected | WebSocket connected | Green dot + "Online" in navbar | P1 |
| T-6.6.02 | Unit | Red "Offline" indicator when disconnected | WebSocket disconnected | Red dot + "Offline" in navbar | P1 |

#### F-6.2: Offline Banner

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.2.01 | Unit | Offline banner shows on disconnect | WebSocket disconnected state | Banner with "Currently offline" + countdown | P1 |
| T-6.2.02 | Unit | Banner disappears on reconnection | WebSocket reconnected | Banner hidden, state synced | P1 |

#### F-6.3: Presence Tracking

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.3.01 | WebSocket | Presence update broadcasts to idea subscribers | User connects to idea | presence_update event sent | P1 |
| T-6.3.02 | Unit | Online/Idle/Offline indicators render correctly | Presence states | Correct visual indicator per state | P1 |

---

### FA-7: Authentication

#### F-7.1: Dev Auth Bypass

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-7.1.01 | Integration | Dev users endpoint available in bypass mode | GET /api/auth/dev-users with DEBUG+AUTH_BYPASS | 200 with 4 users | P1 |
| T-7.1.02 | Integration | Dev users endpoint 404 in production mode | GET /api/auth/dev-users without bypass flags | 404 | P1 |
| T-7.1.03 | Integration | Dev login creates session | POST /api/auth/dev-login {user_id} | 200 with user data | P1 |
| T-7.1.04 | E2E | Dev login flow end-to-end | Select dev user → navigate to landing | User identity visible | P1 |

#### F-7.2: Production Authentication

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-7.2.01 | Integration | Valid Azure AD token validates and syncs user | POST /api/auth/validate with valid JWT | 200 with user data, user synced | P1 |
| T-7.2.02 | Integration | Expired token returns 401 | POST /api/auth/validate with expired token | 401 TOKEN_INVALID | P1 |
| T-7.2.03 | Integration | Roles synced from AD groups on login | Token with group claims | User roles updated in DB | P1 |

---

### FA-8: Visibility & Sharing

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-8.1.01 | Integration | Private idea accessible only to owner | GET /api/ideas/:id as non-owner | 403 ACCESS_DENIED | P1 |
| T-8.2.01 | Integration | Invite creates pending invitation | POST /api/ideas/:id/collaborators/invite | 201 invitation created | P1 |
| T-8.2.02 | Integration | Accept invitation adds collaborator | POST /api/invitations/:id/accept | User added to idea_collaborators | P1 |
| T-8.2.03 | Integration | Decline invitation updates status | POST /api/invitations/:id/decline | Status = declined | P1 |
| T-8.3.01 | Integration | Share link grants read-only access | GET /api/ideas/:id?share=token | 200, user_role=viewer | P1 |
| T-8.4.01 | Integration | Owner can remove collaborator | DELETE /api/ideas/:id/collaborators/:userId | 204, collaborator removed | P1 |
| T-8.4.02 | Integration | Single owner cannot leave without transferring | POST /api/ideas/:id/collaborators/leave as sole owner | 400 MUST_TRANSFER_OWNERSHIP | P1 |
| T-8.4.03 | Integration | Ownership transfer works | POST /api/ideas/:id/collaborators/transfer | 200, ownership transferred | P1 |

---

### FA-9: Landing Page

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-9.1.01 | Unit | Landing page renders all 4 lists | User with ideas in various states | My Ideas, Collaborating, Invitations, Trash lists | P1 |
| T-9.2.01 | E2E | Create idea from landing page | Type message in hero section, submit | New idea created, redirected to workspace | P1 |
| T-9.3.01 | Integration | Soft delete moves idea to trash | DELETE /api/ideas/:id | deleted_at set, appears in trash | P1 |
| T-9.3.02 | Integration | Restore from trash clears deleted_at | POST /api/ideas/:id/restore | deleted_at = null | P1 |
| T-9.4.01 | Integration | Search by title works | GET /api/ideas?search=keyword | Filtered results returned | P1 |
| T-9.4.02 | Integration | Filter by state works | GET /api/ideas?state=open | Only open ideas returned | P1 |

---

### FA-10: Review Page

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-10.1.01 | Integration | Review page requires reviewer role | GET /api/reviews as regular user | 403 | P1 |
| T-10.2.01 | Integration | Ideas grouped correctly | GET /api/reviews | 5 groups: assigned, unassigned, accepted, rejected, dropped | P1 |
| T-10.3.01 | Integration | Self-assignment works | POST /api/reviews/:ideaId/assign | 200, assignment created | P1 |
| T-10.3.02 | Integration | Unassign works | POST /api/reviews/:ideaId/unassign | 200, unassigned_at set | P1 |
| T-10.4.01 | Integration | Conflict of interest blocked | POST /api/reviews/:ideaId/assign on own idea | 400 CONFLICT_OF_INTEREST | P1 |

---

### FA-11: Admin Panel

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-11.1.01 | Integration | Admin endpoints require admin role | GET /api/admin/parameters as regular user | 403 | P1 |
| T-11.2.01 | Integration | Facilitator context CRUD | PUT /api/admin/ai-context/facilitator | Content updated | P1 |
| T-11.2.02 | Integration | Context agent bucket CRUD | PUT /api/admin/ai-context/context-agent | Sections + free_text updated | P1 |
| T-11.3.01 | Integration | Parameter update applies immediately | PATCH /api/admin/parameters/debounce_timer {value: "5"} | Value updated, runtime reads new value | P1 |
| T-11.4.01 | Integration | Monitoring dashboard returns data | GET /api/admin/monitoring | All fields populated | P1 |
| T-11.5.01 | Integration | Monitoring service detects unhealthy service | Health check fails for one service | Alert email sent to opted-in admins | P1 |
| T-11.5.02 | Integration | Monitoring alert config opt-in/opt-out | POST /api/admin/monitoring/alerts {is_active: true} | Alert config created/updated | P1 |
| T-11.5.03 | Integration | DLQ threshold triggers alert | DLQ count exceeds dlq_alert_threshold | Alert event generated | P2 |
| T-11.6.01 | Integration | User search returns stats | GET /api/admin/users/search?q=dev | Users with idea_count, review_count, contribution_count | P1 |

---

### FA-12: Notifications

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-12.1.01 | Unit | Bell icon shows unread count | unread_count > 0 | Badge visible with count | P1 |
| T-12.1.02 | Unit | Clicking bell opens notification panel | Click bell | Panel renders with notifications | P1 |
| T-12.2.01 | Unit | Toast notification renders with correct type | Toast event | Correct styling (success/info/warning/error) | P1 |
| T-12.2.02 | Unit | Toast auto-dismisses | Toast displayed | Disappears after timeout | P2 |
| T-12.5.01 | Integration | Notification created for collaboration invitation | POST invite | Notification row created for invitee | P1 |
| T-12.5.02 | WebSocket | Real-time notification via WebSocket | Notification created | notification event sent to user | P1 |

---

### FA-13: Notification Preferences

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-13.1.01 | Integration | Get notification preferences | GET /api/users/me/notification-preferences | Categories with toggle states | P1 |
| T-13.1.02 | Integration | Update preferences persists | PATCH preferences {collaboration_invitation: false} | Preference saved | P1 |
| T-13.2.01 | Unit | Group toggle switches all items | Toggle group switch | All child toggles change | P2 |
| T-13.3.01 | Unit | Reviewer-only section visible for reviewers | User with reviewer role | "Review Management" group visible | P1 |
| T-13.3.02 | Unit | Reviewer-only section hidden for regular users | User without reviewer role | "Review Management" group not rendered | P1 |
| T-13.3.03 | Unit | Admin-only section visible for admins | User with admin role | "System" group visible | P1 |

---

### FA-14: Error Handling

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-14.1.01 | Unit | Error toast with Show Logs + Retry buttons | API error received | Toast with both buttons | P1 |
| T-14.1.02 | Unit | Show Logs opens modal with details | Click Show Logs | Modal with error details | P1 |
| T-14.1.03 | Unit | Retry re-triggers failed operation | Click Retry | Operation re-invoked | P1 |
| T-14.1.04 | Unit | Max retries reached disables retry button | 3 retries exhausted | Retry button disabled or removed | P2 |

---

### FA-15: Idle State

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-15.1.01 | Unit | Idle detected after timeout | No mouse movement for idle_timeout | Presence state changes to idle | P1 |
| T-15.1.02 | Unit | Tab blur triggers immediate idle | User switches tab | Idle state set | P1 |
| T-15.2.01 | Unit | Disconnection after prolonged idle | Idle for idle_disconnect seconds | WebSocket closed, offline banner | P1 |
| T-15.3.01 | Unit | Mouse movement clears idle | Move mouse during idle | Idle ends, reconnection starts | P1 |

---

### FA-16: i18n

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-16.1.01 | Unit | All UI text available in German and English | Both language files | No missing keys | P1 |
| T-16.2.01 | Unit | Language switcher changes all visible text | Switch from de to en | All strings update | P1 |
| T-16.2.02 | Unit | Language preference persists in localStorage | Switch language, reload | Same language restored | P1 |

---

### FA-17: Theme Support

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-17.1.01 | Unit | Dark mode applies dark class to HTML | Toggle to dark | html.classList contains "dark" | P1 |
| T-17.2.01 | Unit | Theme persists in localStorage | Switch theme, reload | Same theme restored | P1 |
| T-17.3.01 | Unit | System preference detected on first visit | prefers-color-scheme: dark | Dark mode applied | P2 |

---

## 2. API Endpoint Tests

### Authentication

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-AUTH.01 | POST /api/auth/validate | Happy path | Valid Azure AD JWT | 200 + user object | P1 |
| API-AUTH.02 | POST /api/auth/validate | Auth | Expired token | 401 TOKEN_INVALID | P1 |
| API-AUTH.03 | POST /api/auth/validate | Auth | Malformed token | 401 TOKEN_INVALID | P1 |
| API-AUTH.04 | GET /api/auth/dev-users | Happy path | Bypass mode enabled | 200 + 4 dev users | P1 |
| API-AUTH.05 | GET /api/auth/dev-users | Guard | Bypass mode disabled | 404 | P1 |
| API-AUTH.06 | POST /api/auth/dev-login | Happy path | Valid dev user_id | 200 + session | P1 |

### Ideas

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-IDEA.01 | POST /api/ideas | Happy path | Create idea with first message | 201 + idea object | P1 |
| API-IDEA.02 | POST /api/ideas | Validation | Empty first_message | 400 | P1 |
| API-IDEA.03 | POST /api/ideas | Auth | Unauthenticated | 401 | P1 |
| API-IDEA.04 | GET /api/ideas | Happy path | List user's ideas | 200 + paginated results | P1 |
| API-IDEA.05 | GET /api/ideas | Filter | filter=trash | Only trashed ideas | P1 |
| API-IDEA.06 | GET /api/ideas/:id | Happy path | Get idea as owner | 200 + full idea state | P1 |
| API-IDEA.07 | GET /api/ideas/:id | Authz | Non-owner/non-collaborator | 403 ACCESS_DENIED | P1 |
| API-IDEA.08 | GET /api/ideas/:id | Not found | Non-existent UUID | 404 NOT_FOUND | P1 |
| API-IDEA.09 | PATCH /api/ideas/:id | Happy path | Update title | 200, title_manually_edited=true | P1 |
| API-IDEA.10 | PATCH /api/ideas/:id | Authz | Non-owner | 403 | P1 |
| API-IDEA.11 | DELETE /api/ideas/:id | Happy path | Soft delete | 200, deleted_at set | P1 |
| API-IDEA.12 | POST /api/ideas/:id/restore | Happy path | Restore from trash | 200, deleted_at null | P1 |
| API-IDEA.13 | POST /api/ideas/:id/share-link | Happy path | Generate share link | 201 + token | P1 |
| API-IDEA.14 | DELETE /api/ideas/:id/share-link | Happy path | Revoke share link | 200, token null | P1 |

### Chat

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-CHAT.01 | GET /api/ideas/:id/chat | Happy path | Load chat history | 200 + messages array | P1 |
| API-CHAT.02 | GET /api/ideas/:id/chat | Pagination | before=uuid, limit=20 | 200 + older messages | P1 |
| API-CHAT.03 | POST /api/ideas/:id/chat | Happy path | Send message | 201 + message object | P1 |
| API-CHAT.04 | POST /api/ideas/:id/chat | Locked | Idea in review state | 403 IDEA_LOCKED | P1 |
| API-CHAT.05 | POST /api/ideas/:id/chat | Rate limited | Cap reached | 429 RATE_LIMITED | P1 |
| API-CHAT.06 | POST /api/ideas/:id/chat | Validation | Empty content | 400 | P1 |
| API-CHAT.07 | POST /api/ideas/:id/chat | Validation | Content > 5000 chars | 400 CONTENT_TOO_LONG | P1 |

### Reactions

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-REACT.01 | POST .../reactions | Happy path | React to user message | 201 | P1 |
| API-REACT.02 | POST .../reactions | Validation | React to AI message | 400 CANNOT_REACT_TO_AI | P1 |
| API-REACT.03 | POST .../reactions | Validation | React to self | 400 CANNOT_REACT_TO_SELF | P1 |
| API-REACT.04 | POST .../reactions | Duplicate | Already reacted | 409 ALREADY_REACTED | P1 |
| API-REACT.05 | DELETE .../reactions | Happy path | Remove reaction | 204 | P1 |
| API-REACT.06 | POST .../reactions | Validation | Invalid reaction_type | 400 INVALID_REACTION_TYPE | P1 |

### Board

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-BOARD.01 | GET /api/ideas/:id/board | Happy path | Load board state | 200 + nodes + connections | P1 |
| API-BOARD.02 | POST .../board/nodes | Happy path | Create box node | 201 + node object | P1 |
| API-BOARD.03 | POST .../board/nodes | Happy path | Create group node | 201 | P1 |
| API-BOARD.04 | PATCH .../board/nodes/:id | Happy path | Update node content | 200 | P1 |
| API-BOARD.04b | PATCH .../board/nodes/:id | Validation | Title > 500 chars | 400 TITLE_TOO_LONG | P1 |
| API-BOARD.04c | PATCH .../board/nodes/:id | Validation | Body > 5000 chars | 400 BODY_TOO_LONG | P1 |
| API-BOARD.05 | PATCH .../board/nodes/:id | Locked | Update locked node | 403 or 400 | P1 |
| API-BOARD.06 | DELETE .../board/nodes/:id | Happy path | Delete node | 204, children detached | P1 |
| API-BOARD.07 | POST .../board/nodes/batch | Happy path | Batch operations | 200 + results per op | P1 |
| API-BOARD.08 | POST .../board/connections | Happy path | Create connection | 201 | P1 |
| API-BOARD.09 | POST .../board/connections | Duplicate | Same source-target pair | 409 or 400 | P1 |
| API-BOARD.10 | PATCH .../connections/:id | Happy path | Update label | 200 | P1 |
| API-BOARD.11 | DELETE .../connections/:id | Happy path | Delete connection | 204 | P1 |

### BRD

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-BRD.01 | GET /api/ideas/:id/brd | Happy path | Get current draft | 200 + sections + locks + readiness | P1 |
| API-BRD.02 | POST .../brd/generate | Happy path | Generate skeleton | 200 | P1 |
| API-BRD.03 | POST .../brd/regenerate | Happy path | Regenerate unlocked sections | 202 + job_id | P1 |
| API-BRD.04 | POST .../brd/regenerate-section | Happy path | Regenerate single section | 202 + job_id | P1 |
| API-BRD.05 | PATCH /api/ideas/:id/brd | Happy path | User edits sections | 200, auto-lock applied | P1 |
| API-BRD.06 | GET .../brd/versions | Happy path | List versions | 200 + version array | P1 |
| API-BRD.07 | GET .../brd/versions/:id/pdf | Happy path | Download PDF | 200 + PDF file | P1 |
| API-BRD.08 | GET .../brd/versions/:id/pdf | Not found | PDF not generated | 404 PDF_NOT_FOUND | P1 |
| API-BRD.09 | POST .../brd/generate-pdf | Happy path | Generate and return PDF | 200 + PDF bytes | P1 |
| API-BRD.10 | POST .../brd/generate-pdf | Validation | /TODO markers remain | 400 TODO_MARKERS_REMAINING | P1 |

### Review Workflow

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-REV.01 | POST .../submit | Happy path | Submit for review | 200 + state=in_review | P1 |
| API-REV.02 | POST .../submit | Validation | Wrong state (accepted) | 400 | P1 |
| API-REV.03 | POST .../review/accept | Happy path | Accept | 200 + state=accepted | P1 |
| API-REV.04 | POST .../review/reject | Happy path | Reject with comment | 200 + state=rejected | P1 |
| API-REV.05 | POST .../review/reject | Validation | Missing comment | 400 COMMENT_REQUIRED | P1 |
| API-REV.06 | POST .../review/drop | Happy path | Drop with comment | 200 + state=dropped | P1 |
| API-REV.07 | POST .../review/undo | Happy path | Undo action | 200 + state=in_review | P1 |
| API-REV.08 | POST .../review/undo | Validation | Missing comment | 400 COMMENT_REQUIRED | P1 |
| API-REV.09 | GET .../review/timeline | Happy path | Load timeline | 200 + entries with replies | P1 |
| API-REV.10 | POST .../review/timeline | Happy path | Post comment | 201 + entry | P1 |
| API-REV.11 | GET .../review/similar | Happy path | Get similar ideas for review | 200 + similar_ideas array | P2 |

### Collaboration

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-COLLAB.01 | POST .../invite | Happy path | Invite user | 201 + invitation | P1 |
| API-COLLAB.02 | GET .../collaborators | Happy path | List collaborators | 200 + collaborators + pending | P1 |
| API-COLLAB.03 | DELETE .../collaborators/:userId | Happy path | Remove collaborator | 204 | P1 |
| API-COLLAB.04 | POST .../transfer | Happy path | Transfer ownership | 200 | P1 |
| API-COLLAB.05 | POST .../leave | Happy path | Leave as co-owner | 200 | P1 |
| API-COLLAB.06 | POST .../leave | Validation | Leave as sole owner | 400 MUST_TRANSFER_OWNERSHIP | P1 |
| API-COLLAB.07 | POST /api/invitations/:id/accept | Happy path | Accept invitation | 200, collaborator added | P1 |
| API-COLLAB.08 | POST /api/invitations/:id/decline | Happy path | Decline invitation | 200 | P1 |
| API-COLLAB.09 | DELETE /api/invitations/:id | Happy path | Revoke invitation | 204 | P1 |

### Similarity & Merge

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-MERGE.01 | GET .../similar | Happy path | Get similar ideas | 200 + similar_ideas | P1 |
| API-MERGE.02 | POST .../merge-request | Happy path | Request merge | 201 + merge_request | P1 |
| API-MERGE.03 | POST /api/merge-requests/:id/accept | Happy path | Accept merge | 200 + resulting_idea_id | P1 |
| API-MERGE.04 | POST /api/merge-requests/:id/decline | Happy path | Decline merge | 200 + status=declined | P1 |
| API-MERGE.05 | POST .../manual-merge | Happy path | Manual merge request | 201 | P1 |
| API-MERGE.06 | POST .../reopen | Happy path | Reopen accepted idea | 200 + state=open | P1 |

### Notifications

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-NOTIF.01 | GET /api/notifications | Happy path | List notifications | 200 + paginated list | P1 |
| API-NOTIF.02 | GET .../unread-count | Happy path | Get unread count | 200 + count | P1 |
| API-NOTIF.03 | PATCH /api/notifications/:id | Happy path | Mark as read | 200 | P1 |
| API-NOTIF.04 | POST .../mark-all-read | Happy path | Mark all read | 200 | P1 |

### User

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-USER.01 | GET /api/users/me | Happy path | Get profile | 200 + user object | P1 |
| API-USER.02 | GET .../notification-preferences | Happy path | Get preferences | 200 + categories | P1 |
| API-USER.03 | PATCH .../notification-preferences | Happy path | Update preferences | 200 | P1 |
| API-USER.04 | GET /api/users/search | Happy path | Search users | 200 + results | P1 |

### Admin

| Test ID | Endpoint | Type | Description | Expected | Priority |
|---------|----------|------|-------------|----------|----------|
| API-ADMIN.01 | GET /api/admin/parameters | Happy path | List parameters | 200 + array | P1 |
| API-ADMIN.02 | GET /api/admin/parameters | Authz | Non-admin | 403 | P1 |
| API-ADMIN.03 | PATCH .../parameters/:key | Happy path | Update parameter | 200 | P1 |
| API-ADMIN.04 | GET /api/admin/monitoring | Happy path | Get dashboard data | 200 + full monitoring object | P1 |
| API-ADMIN.05 | PUT .../ai-context/facilitator | Happy path | Update facilitator context | 200 | P1 |
| API-ADMIN.06 | PUT .../ai-context/context-agent | Happy path | Update context agent bucket | 200, triggers re-indexing | P1 |
| API-ADMIN.07 | GET /api/admin/users/search | Happy path | Search with stats | 200 + users with counts | P1 |

---

## 3. Data Entity Tests

### ideas

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-IDEA.01 | Create | Valid idea creation | User exists | Row created with defaults | P1 |
| DB-IDEA.02 | Create | State CHECK constraint | state="invalid" | Database error | P1 |
| DB-IDEA.03 | Update | State transition | state=open | state=in_review | P1 |
| DB-IDEA.04 | Soft Delete | Set deleted_at | Row exists | deleted_at set, row not removed | P1 |
| DB-IDEA.05 | Cascade | Delete idea cascades | Idea with chat, board, BRD | All child rows deleted | P1 |
| DB-IDEA.06 | Constraint | Visibility CHECK | visibility="invalid" | Database error | P2 |

### chat_messages

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-CHAT.01 | Create | Valid user message | Idea exists | Row created, sender_type=user | P1 |
| DB-CHAT.02 | Create | Valid AI message | Idea exists | Row created, sender_id=null, ai_agent set | P1 |
| DB-CHAT.03 | Immutability | Update rejected at app level | Message exists | No update operation allowed | P1 |
| DB-CHAT.04 | Ordering | Messages ordered by created_at | Multiple messages | Chronological order | P1 |

### board_nodes

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-NODE.01 | Create | Valid box node | Idea exists | Row created with defaults | P1 |
| DB-NODE.02 | Create | Node with parent group | Group exists | parent_id set correctly | P1 |
| DB-NODE.03 | Delete | Parent deleted, children detached | Group with children | Children parent_id set to null (ON DELETE SET NULL) | P1 |
| DB-NODE.04 | Constraint | node_type CHECK | type="invalid" | Database error | P2 |

### board_connections

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-CONN.01 | Create | Valid connection | Two nodes exist | Row created | P1 |
| DB-CONN.02 | Unique | Duplicate connection | Connection exists | UNIQUE violation | P1 |
| DB-CONN.03 | Cascade | Source node deleted | Connection exists | Connection cascade deleted | P1 |

### brd_drafts

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-BRD.01 | Create | One draft per idea | Idea exists | Row created (UNIQUE on idea_id) | P1 |
| DB-BRD.02 | Create | Duplicate draft | Draft exists | UNIQUE violation | P1 |
| DB-BRD.03 | Update | Section lock persists in JSONB | Update section_locks | JSONB updated correctly | P1 |

### brd_versions

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-BRDV.01 | Create | Version snapshot on submit | Draft exists | Immutable row created | P1 |
| DB-BRDV.02 | Unique | Version number unique per idea | Existing versions | UNIQUE (idea_id, version_number) | P1 |
| DB-BRDV.03 | Immutability | No updates allowed | Version exists | App layer prevents update | P1 |

### review_assignments

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-ASGN.01 | Create | Assign reviewer | Idea in review | Row created | P1 |
| DB-ASGN.02 | Unique | One active assignment per reviewer | Active assignment exists | UNIQUE partial index violation | P1 |
| DB-ASGN.03 | Unassign | Set unassigned_at | Active assignment | unassigned_at timestamp set | P1 |

### merge_requests

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-MRG.01 | Create | Pending merge request | Two ideas exist | Row with status=pending | P1 |
| DB-MRG.02 | Unique | One active request per pair | Pending exists | UNIQUE partial index violation | P1 |
| DB-MRG.03 | Resolve | Accept sets resulting_idea_id | Pending request | status=accepted, resulting_idea_id set | P1 |

### notifications

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-NOTIF.01 | Create | Notification for event | User exists | Row created with event_type, is_read=false | P1 |
| DB-NOTIF.02 | Update | Mark as read | Notification exists | is_read=true | P1 |
| DB-NOTIF.03 | Cascade | User deleted cascades | User with notifications | Notifications deleted | P2 |

### AI-Owned Tables

| Test ID | Operation | Description | Precondition | Expected | Priority |
|---------|-----------|-------------|-------------|----------|----------|
| DB-AI.01 | Upsert | Chat context summary | Idea exists | Row upserted, compression_iteration incremented | P1 |
| DB-AI.02 | Rebuild | Context chunks on bucket update | Bucket updated | Old chunks deleted, new chunks inserted | P1 |
| DB-AI.03 | Upsert | Idea embedding | Idea with keywords | Embedding upserted, source_text_hash updated | P1 |
| DB-AI.04 | HNSW | Vector similarity search | Multiple embeddings | Correct top-K results | P1 |
| DB-AI.05 | Singleton | Facilitator bucket single row | Existing row | Only one row exists | P1 |

---

## 4. Page & Component Tests

### Landing Page (`/`)

| Test ID | Layer | Description | State | Expected | Priority |
|---------|-------|-------------|-------|----------|----------|
| UI-LAND.01 | Unit | Renders without error | Default | No crash | P1 |
| UI-LAND.02 | Unit | Shows empty state | No ideas | Empty state message | P2 |
| UI-LAND.03 | Unit | IdeaCard renders with title, state, collaborator count | Idea data | All fields visible | P1 |
| UI-LAND.04 | Unit | Trash section shows soft-deleted ideas | Ideas with deleted_at | Trash list populated | P1 |
| UI-LAND.05 | Unit | Undo toast on trash action | Delete idea | Toast with undo button | P2 |

### Idea Workspace (`/idea/:uuid`)

| Test ID | Layer | Description | State | Expected | Priority |
|---------|-------|-------------|-------|----------|----------|
| UI-WORK.01 | Unit | Workspace renders with chat + board panels | Idea loaded | Both panels visible | P1 |
| UI-WORK.02 | Unit | Chat panel shows loading state | Loading | Spinner visible | P2 |
| UI-WORK.03 | Unit | Chat panel shows error state | Error | Error message displayed | P2 |
| UI-WORK.04 | Unit | Board canvas renders with React Flow | Board data | Canvas with nodes/edges | P1 |
| UI-WORK.05 | Unit | Chat input disabled when locked | state=in_review | Input field disabled | P1 |
| UI-WORK.06 | Unit | Agent mode dropdown works | Click dropdown | Options visible, selection updates | P1 |
| UI-WORK.07 | Unit | Presence indicators render | Online users | User avatars with status | P1 |

### Review List Page (`/reviews`)

| Test ID | Layer | Description | State | Expected | Priority |
|---------|-------|-------------|-------|----------|----------|
| UI-REV.01 | Unit | Renders without error | Reviewer role | No crash | P1 |
| UI-REV.02 | Unit | Five category groups render | Mixed data | All 5 groups visible | P1 |
| UI-REV.03 | Unit | Assign button visible for unassigned ideas | Unassigned list | Assign button shown | P1 |
| UI-REV.04 | Unit | Non-reviewer sees 403 or redirect | User role only | Access denied | P1 |

### Admin Panel (`/admin`)

| Test ID | Layer | Description | State | Expected | Priority |
|---------|-------|-------------|-------|----------|----------|
| UI-ADMIN.01 | Unit | 4 tabs render: AI Context, Parameters, Monitoring, Users | Admin role | All tabs visible | P1 |
| UI-ADMIN.02 | Unit | Parameters tab shows editable fields | Parameter data | Input fields with current values | P1 |
| UI-ADMIN.03 | Unit | Monitoring dashboard renders stats | Monitoring data | Charts/numbers displayed | P1 |
| UI-ADMIN.04 | Unit | Non-admin sees 403 or redirect | User role only | Access denied | P1 |

---

## 5. Statistics

| Layer | Total Tests | P1 (Critical) | P2 (Important) | P3 (Nice-to-have) |
|-------|-------------|---------------|----------------|-------------------|
| Unit (Frontend) | 95 | 73 | 20 | 2 |
| Integration (Backend) | 99 | 92 | 6 | 1 |
| AI Agent | 26 | 22 | 4 | 0 |
| WebSocket | 5 | 5 | 0 | 0 |
| E2E | 4 | 4 | 0 | 0 |
| Data Entity | 27 | 23 | 4 | 0 |
| **Total** | **256** | **219** | **34** | **3** |

> **Note:** E2E flows from the architect's testing strategy (13 critical flows) are tracked separately in `docs/02-architecture/testing-strategy.md` § Critical Test Flows. This matrix adds the feature-specific test cases that implement those flows.
>
> **Changes from v1 (2026-03-04):** Added 26 test cases: F-2.2 language detection (3), F-3.8 board reference action (2), F-4.12 similar ideas in review (2), F-5.8 manual merge (3), F-6.6 connection indicator (2), F-11.5 monitoring service (3), F-13.3 role-based notification groups (3), input validation edge cases (6: chat length, board title/body length, reaction type, similar ideas API).
