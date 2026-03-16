# Test Matrix

> **Status:** Definitive (revised for refactoring)
> **Date:** 2026-03-16 (originally 2026-03-04)
> **Author:** Test Architect (Phase 4b + Refactoring)
> **Input:** All validated specs from phases [1]–[4], `REFACTORING_PLAN.md`
> **Revision:** Updated for project-based terminology, removed board/merge features, added requirements panel features

This document maps every feature, API endpoint, data entity, and page to specific test cases at each testing layer. Every test case traces back to a requirement ID, endpoint, or entity.

**Priority definitions:**
- **P1 (Critical):** Must have for MVP. Blocks release if missing.
- **P2 (Important):** Should have. Addresses important edge cases and error paths.
- **P3 (Nice-to-have):** Can defer. Covers rare scenarios or polish.

---

## 1. Feature Tests

### FA-1: Project Workspace

#### F-1.1: Project Page Layout

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.1.01 | Unit | Two-panel layout renders with draggable divider | Default project state | Chat left, Requirements/Review tabs right | P1 |
| T-1.1.02 | Unit | Divider drag resizes panels proportionally | Drag event to 30%/70% | Panels resize, min width respected | P2 |
| T-1.1.03 | Unit | Requirements tab is default active in context panel | Project state = open | Requirements tab selected | P1 |

#### F-1.2: Section Visibility

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.2.01 | Unit | Review section hidden for never-submitted project | `has_been_submitted=false` | Review section not in DOM | P1 |
| T-1.2.02 | Unit | Review section visible after first submission | `has_been_submitted=true` | Review section rendered | P1 |
| T-1.2.03 | Unit | Review section persists across all states after submission | States: open, in_review, rejected, accepted, dropped | Review section always visible | P1 |

#### F-1.3: Auto-Scroll on State Transition

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.3.01 | Unit | Scroll to definition on `open` state entry | Navigate to project in `open` state | scrollIntoView called on definition section | P2 |
| T-1.3.02 | Unit | Scroll to review on `in_review` state entry | State changes to `in_review` | scrollIntoView called on review section | P2 |
| T-1.3.03 | Unit | Scroll to definition on `rejected` state | State changes to `rejected` | scrollIntoView to definition | P2 |

#### F-1.4: Section Locking

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.4.01 | Unit | Open state: definition editable, review hidden | `state=open, has_been_submitted=false` | Chat input enabled, requirements editable | P1 |
| T-1.4.02 | Unit | In Review: definition locked (read-only) | `state=in_review` | Chat input disabled, requirements read-only | P1 |
| T-1.4.03 | Unit | Rejected: definition editable, review visible read-only | `state=rejected` | Chat enabled, review section read-only | P1 |
| T-1.4.04 | Unit | Accepted: everything read-only | `state=accepted` | All inputs disabled | P1 |
| T-1.4.05 | Unit | Dropped: everything read-only | `state=dropped` | All inputs disabled | P1 |

#### F-1.5: Project Lifecycle State Transitions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.5.01 | Integration | Open → In Review via submit | POST /api/projects/:id/submit | State = in_review, document version created | P1 |
| T-1.5.02 | Integration | In Review → Accepted via reviewer accept | POST /api/projects/:id/review/accept | State = accepted | P1 |
| T-1.5.03 | Integration | In Review → Dropped via reviewer drop | POST /api/projects/:id/review/drop with comment | State = dropped | P1 |
| T-1.5.04 | Integration | In Review → Rejected via reviewer reject | POST /api/projects/:id/review/reject with comment | State = rejected | P1 |
| T-1.5.05 | Integration | Rejected → In Review via resubmit | POST /api/projects/:id/submit | State = in_review, new document version | P1 |
| T-1.5.06 | Integration | Accepted → In Review via undo | POST /api/projects/:id/review/undo with comment | State = in_review | P1 |
| T-1.5.07 | Integration | Dropped → In Review via undo | POST /api/projects/:id/review/undo with comment | State = in_review | P1 |
| T-1.5.08 | Integration | Invalid transition: open → accepted rejected | POST /api/projects/:id/review/accept on open project | 400 error | P1 |
| T-1.5.09 | Integration | Multiple reviewers: latest action wins | Two reviewers act in sequence | Last action determines state | P2 |
| T-1.5.10 | E2E | Full lifecycle: create → submit → reject → resubmit → accept | Full user flow | All transitions complete correctly | P1 |

#### F-1.6: Inline Title Editing

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.6.01 | Unit | Title is editable by clicking | Click on title element | Title becomes input field | P1 |
| T-1.6.02 | Integration | Manual edit sets title_manually_edited permanently | PATCH /api/projects/:id with title | `title_manually_edited=true` | P1 |
| T-1.6.03 | Unit | Browser tab title updates on title change | Title WebSocket event received | document.title updates | P2 |

#### F-1.7–F-1.8: UUID Routing, Browser Tab

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-1.7.01 | Unit | Route /project/:uuid renders workspace | Navigate to /project/valid-uuid | ProjectWorkspace component renders | P1 |
| T-1.7.02 | Unit | Invalid UUID shows 404 | Navigate to /project/not-a-uuid | 404 page rendered | P2 |

---

### FA-2: AI Facilitation

#### F-2.1: Agent Modes

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.1.01 | Unit | Agent mode dropdown renders with Interactive/Silent | Default state | Dropdown with two options | P1 |
| T-2.1.02 | Integration | Agent mode change persists | PATCH /api/projects/:id {agent_mode: "silent"} | Mode saved, WebSocket broadcast | P1 |
| T-2.1.03 | AI Agent | Silent mode: no AI response without @ai | `agent_mode=silent`, message without @ai | Facilitator returns no action | P1 |
| T-2.1.04 | AI Agent | Silent mode: @ai forces response | `agent_mode=silent`, message with @ai mention | Facilitator generates response | P1 |

#### F-2.2: AI Tool Calls - update_requirements_structure

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.2.01 | AI Agent | Facilitator calls update_requirements_structure for software project | User describes features | Tool call with epics/stories structure | P1 |
| T-2.2.02 | AI Agent | Facilitator calls update_requirements_structure for non-software project | User describes phases | Tool call with milestones/packages structure | P1 |
| T-2.2.03 | Integration | update_requirements_structure creates/updates requirements items | AI tool call with hierarchical structure | RequirementsItem records created with correct parent relationships | P1 |
| T-2.2.04 | Integration | update_requirements_structure respects project type | Software project receives epic structure | Rejects milestone structure with validation error | P1 |
| T-2.2.05 | AI Agent | Facilitator respects existing structure | Project has existing epics | Updates/augments without deleting unless instructed | P2 |

#### F-2.3: Title Generation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.3.01 | AI Agent | Facilitator suggests title after sufficient context | 3+ messages, no manual title edit | AI generates title suggestion | P1 |
| T-2.3.02 | Integration | Title suggestion only if not manually edited | `title_manually_edited=true` | Facilitator skips title suggestion | P1 |
| T-2.3.03 | Unit | Title suggestion appears in chat | AI suggests title | Suggestion rendered with accept/dismiss buttons | P1 |
| T-2.3.04 | Integration | Accept title suggestion updates project | User clicks accept | PATCH /api/projects/:id with title, `title_manually_edited=false` | P1 |

#### F-2.4: Context Agent Delegation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.4.01 | AI Agent | Facilitator delegates to Context Agent when relevant | User asks about existing systems | Delegation message sent | P1 |
| T-2.4.02 | AI Agent | Context Agent retrieves from correct bucket based on project type | Software project context query | RAG search in global + software bucket | P1 |
| T-2.4.03 | AI Agent | Context Agent retrieves from correct bucket for non-software | Non-software project context query | RAG search in global + non_software bucket | P1 |
| T-2.4.04 | Integration | Context Agent response includes sources | RAG query returns chunks | AI response cites source sections | P2 |
| T-2.4.05 | AI Agent | Context Agent returns "no context found" gracefully | Query with no matching chunks | Polite "no information available" response | P2 |

#### F-2.5: Requirements Structuring Prompts

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.5.01 | AI Agent | Facilitator guides software project toward epic/story structure | Initial software project conversation | AI asks about features/capabilities | P1 |
| T-2.5.02 | AI Agent | Facilitator guides non-software project toward milestone/package structure | Initial non-software project conversation | AI asks about phases/deliverables | P1 |
| T-2.5.03 | AI Agent | Facilitator adapts prompts based on project type | Software vs non-software projects | Different terminology and structure suggestions | P1 |

#### F-2.6: Message Reactions (AI)

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.6.01 | AI Agent | Facilitator adds thumbs_up reaction to supportive messages | User confirms/agrees | Reaction added via tool call | P2 |
| T-2.6.02 | Integration | AI reaction persisted in database | Facilitator reaction tool call | AiReaction record created | P2 |
| T-2.6.03 | Unit | AI reactions rendered in chat UI | Message with AI reaction | Thumbs up icon shown | P2 |

#### F-2.7: AI Processing Pipeline

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-2.7.01 | Integration | Chat message triggers AI pipeline | POST /api/projects/:id/messages | AI processing event published | P1 |
| T-2.7.02 | Integration | Pipeline debounces rapid messages | 3 messages in 1 second | Single AI invocation after 3s | P1 |
| T-2.7.03 | Integration | Pipeline loads project type context | Software project message | Context includes project_type="software" | P1 |
| T-2.7.04 | AI Agent | Pipeline invokes Facilitator with full context | Message + history + requirements state | Agent receives all relevant data | P1 |
| T-2.7.05 | Integration | Pipeline handles AI errors gracefully | AI service returns error | User sees error message, no crash | P2 |

---

### FA-4: Requirements Panel

#### F-4.1: Project Type-Specific Display

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.1.01 | Unit | Software project shows Epics/User Stories UI | `project_type="software"` | Panel displays "Epics" accordion sections | P1 |
| T-4.1.02 | Unit | Non-software project shows Milestones/Work Packages UI | `project_type="non_software"` | Panel displays "Milestones" accordion sections | P1 |
| T-4.1.03 | Unit | Software project "Add Epic" button renders | Software project | "Add Epic" button visible | P1 |
| T-4.1.04 | Unit | Non-software project "Add Milestone" button renders | Non-software project | "Add Milestone" button visible | P1 |

#### F-4.2: Add/Edit/Delete Requirements Items

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.2.01 | Unit | Add Epic button opens modal | Click "Add Epic" | Modal with title/description fields | P1 |
| T-4.2.02 | Integration | Create epic via modal | POST /api/projects/:id/requirements with item_type=epic | Epic created, WebSocket broadcast | P1 |
| T-4.2.03 | Integration | Create user story under epic | POST /api/projects/:id/requirements with parent_id=epic.id | Story created, nested under epic | P1 |
| T-4.2.04 | Integration | Edit requirement item | PATCH /api/projects/:id/requirements/:item_id | Item updated, broadcast | P1 |
| T-4.2.05 | Integration | Delete requirement item | DELETE /api/projects/:id/requirements/:item_id | Item soft-deleted, broadcast | P1 |
| T-4.2.06 | Integration | Delete epic cascades to child stories | DELETE epic with 3 stories | All 4 items soft-deleted | P2 |
| T-4.2.07 | Unit | Deleted items removed from UI immediately | WebSocket delete event received | Item disappears from panel | P1 |

#### F-4.3: Reorder Requirements Items

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.3.01 | Unit | Drag-and-drop reorders epics | Drag epic to new position | Visual reorder, onChange fired | P1 |
| T-4.3.02 | Integration | Reorder persisted to backend | PATCH /api/projects/:id/requirements/reorder | order_index values updated | P1 |
| T-4.3.03 | Unit | Drag story between epics changes parent | Drag story from Epic A to Epic B | Story's parent_id updated | P2 |
| T-4.3.04 | Integration | Reorder within epic updates order_index | Drag story within same epic | Stories re-indexed | P2 |
| T-4.3.05 | Unit | Reorder disabled in review state | `state=in_review` | Drag handles disabled | P1 |

#### F-4.4: Accordion Expand/Collapse

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.4.01 | Unit | Click epic expands to show stories | Click collapsed epic | Stories list visible | P1 |
| T-4.4.02 | Unit | Click again collapses epic | Click expanded epic | Stories hidden | P1 |
| T-4.4.03 | Unit | Expand state persists across renders | Expand epic, re-render component | Epic still expanded | P2 |
| T-4.4.04 | Unit | All epics collapsed by default | Load project with epics | All accordions collapsed | P2 |

#### F-4.5: AI-Created Indicator

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.5.01 | Unit | AI-created items show indicator badge | `created_by="ai"` | Badge with "AI" label visible | P1 |
| T-4.5.02 | Unit | User-created items have no badge | `created_by="user"` | No badge rendered | P1 |
| T-4.5.03 | Unit | AI-modified items show modified indicator | `ai_modified_indicator=true` | Faint highlight or border | P2 |

#### F-4.6: Empty State

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.6.01 | Unit | Empty software project shows prompt | No epics | "Add your first epic" message + button | P1 |
| T-4.6.02 | Unit | Empty non-software project shows prompt | No milestones | "Add your first milestone" message + button | P1 |

#### F-4.7: Real-time Collaboration

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-4.7.01 | Integration | Collaborator adds epic | User B creates epic | User A sees epic appear in panel | P1 |
| T-4.7.02 | Integration | Collaborator reorders items | User B reorders | User A sees reordered list | P2 |
| T-4.7.03 | Integration | AI updates structure | Facilitator calls update_requirements_structure | All users see updates | P1 |

---

### FA-6: Requirements Document (formerly BRD)

#### F-6.1: Draft Auto-Generation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.1.01 | Integration | Draft generates on first submit | POST /api/projects/:id/submit | Summarizing AI invoked, draft created | P1 |
| T-6.1.02 | AI Agent | Summarizing AI includes requirements_structure field | Software project with epics/stories | Draft contains hierarchical JSON structure | P1 |
| T-6.1.03 | AI Agent | Summarizing AI adapts to project type | Non-software project | Draft uses milestone/package structure | P1 |
| T-6.1.04 | AI Agent | Summarizing AI respects section locks | 2 sections locked | Locked sections unchanged, others regenerated | P1 |
| T-6.1.05 | AI Agent | Gaps mode: incomplete sections get /TODO | `allow_information_gaps=true` | Insufficient sections have "/TODO" markers | P2 |

#### F-6.2: Requirements Structure Rendering

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.2.01 | Unit | Software document renders epics/stories hierarchically | Draft with requirements_structure | Nested list with epics > stories | P1 |
| T-6.2.02 | Unit | Non-software document renders milestones/packages | Non-software draft | Nested list with milestones > packages | P1 |
| T-6.2.03 | Unit | Empty requirements_structure shows placeholder | `requirements_structure={}` | "No requirements defined yet" message | P2 |

#### F-6.3: Section Lock/Unlock

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.3.01 | Unit | Lock button appears on each section | Draft section | Lock icon button visible | P1 |
| T-6.3.02 | Integration | Lock section persists | PATCH /api/projects/:id/draft {section_locks: {title: true}} | Lock saved | P1 |
| T-6.3.03 | Integration | Locked section excluded from regeneration | Regenerate draft with title locked | Title unchanged, others updated | P1 |
| T-6.3.04 | Unit | Locked sections show lock indicator | `section_locks.title=true` | Locked icon rendered next to title | P1 |

#### F-6.4: Manual Draft Editing

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.4.01 | Unit | Draft sections editable in open state | `state=open` | All sections have text editors | P1 |
| T-6.4.02 | Integration | Manual edits persist | PATCH /api/projects/:id/draft {section_title: "New Title"} | Draft updated | P1 |
| T-6.4.03 | Unit | Draft read-only in review state | `state=in_review` | Editors disabled | P1 |

#### F-6.5: Readiness Evaluation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.5.01 | AI Agent | Summarizing AI evaluates each section | Draft generation | `readiness_evaluation` field populated | P1 |
| T-6.5.02 | Unit | Ready sections show green checkmark | `readiness_evaluation.title="ready"` | Green icon next to title | P1 |
| T-6.5.03 | Unit | Insufficient sections show warning icon | `readiness_evaluation.title="insufficient"` | Yellow/orange icon | P1 |
| T-6.5.04 | Unit | Submit blocked if critical sections insufficient | 2+ sections insufficient | Submit button disabled with tooltip | P1 |
| T-6.5.05 | Integration | Allow gaps mode bypasses blocking | `allow_information_gaps=true` | Submit button enabled despite insufficient sections | P2 |

#### F-6.6: Version History

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-6.6.01 | Integration | Submit creates frozen version | POST /api/projects/:id/submit | RequirementsDocumentVersion record created | P1 |
| T-6.6.02 | Integration | Version includes requirements_structure | Submit with requirements items | Version.requirements_structure = frozen JSON | P1 |
| T-6.6.03 | Unit | Version list shows all versions | 3 submissions | 3 versions displayed | P1 |
| T-6.6.04 | Unit | Click version loads frozen content | Select version 2 | Draft replaced with version 2 snapshot | P1 |
| T-6.6.05 | E2E | PDF download retrieves correct version | Click "Download PDF" on version 2 | PDF for version 2 downloaded | P1 |

---

### FA-7: Collaboration

#### F-7.1: Invitation Flow

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-7.1.01 | Unit | Owner sees "Invite Collaborator" button | `visibility=private` | Button rendered in project menu | P1 |
| T-7.1.02 | Integration | Send invitation | POST /api/projects/:id/invite {invitee_id} | Invitation created, notification sent | P1 |
| T-7.1.03 | Integration | Invitee accepts | PATCH /api/invitations/:id {status: "accepted"} | Collaborator added, visibility → collaborating | P1 |
| T-7.1.04 | Integration | Invitee declines | PATCH /api/invitations/:id {status: "declined"} | Invitation closed, no collaborator added | P1 |
| T-7.1.05 | Integration | Owner revokes invitation | DELETE /api/invitations/:id | Invitation status → revoked | P2 |

#### F-7.2: Real-time Presence

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-7.2.01 | Integration | WebSocket join broadcasts presence | User connects to project channel | Other users see presence indicator | P1 |
| T-7.2.02 | Integration | WebSocket leave removes presence | User disconnects | Presence indicator removed | P1 |
| T-7.2.03 | Unit | Presence indicators show avatars | 2 collaborators online | 2 avatars displayed | P1 |

#### F-7.3: Synchronized Updates

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-7.3.01 | Integration | Chat message broadcast to all | User A sends message | User B receives via WebSocket | P1 |
| T-7.3.02 | Integration | Requirements update broadcast | User A adds epic | User B sees epic appear | P1 |
| T-7.3.03 | Integration | Draft edit broadcast | User A edits section | User B sees section update | P1 |

---

### FA-8: Review

#### F-8.1: Reviewer Assignment

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-8.1.01 | Unit | Submit modal allows reviewer selection | Click submit | Modal with reviewer dropdown | P1 |
| T-8.1.02 | Integration | Submit with reviewers assigns them | POST /api/projects/:id/submit {reviewer_ids} | ReviewAssignment records created | P1 |
| T-8.1.03 | Integration | Reviewers receive notification | Submit with reviewers | Notifications sent | P1 |
| T-8.1.04 | Integration | Reviewer self-assigns | Reviewer clicks "Assign to me" | ReviewAssignment created with assigned_by="self" | P2 |
| T-8.1.05 | Integration | Unassign reviewer | DELETE /api/projects/:id/reviewers/:id | Assignment.unassigned_at set | P2 |

#### F-8.2: Review Actions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-8.2.01 | Unit | Reviewer sees accept/reject/drop buttons | `state=in_review`, user is reviewer | 3 action buttons visible | P1 |
| T-8.2.02 | Integration | Accept action | POST /api/projects/:id/review/accept | State → accepted, timeline entry created | P1 |
| T-8.2.03 | Integration | Reject action requires comment | POST /api/projects/:id/review/reject without comment | 400 validation error | P1 |
| T-8.2.04 | Integration | Drop action with reason | POST /api/projects/:id/review/drop {comment} | State → dropped, comment in timeline | P1 |
| T-8.2.05 | Integration | Undo action | POST /api/projects/:id/review/undo | State reverts to in_review | P2 |

#### F-8.3: Review Timeline

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-8.3.01 | Unit | Timeline shows all events | Project with 5 timeline entries | All 5 rendered chronologically | P1 |
| T-8.3.02 | Integration | Comment adds timeline entry | POST /api/projects/:id/review/comments {content} | Entry created, broadcast | P1 |
| T-8.3.03 | Integration | State change auto-creates timeline entry | State changes to in_review | Entry with entry_type="state_change" | P1 |
| T-8.3.04 | Integration | Resubmission links versions | Resubmit after rejection | Timeline entry references old_version_id and new_version_id | P2 |
| T-8.3.05 | Unit | Reply to comment | Click reply, submit | Nested reply with parent_entry_id | P2 |

#### F-8.4: Review Page (Reviewer View)

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-8.4.01 | Unit | Review page renders for reviewers | Navigate to /review as reviewer | ReviewPage component with assigned projects | P1 |
| T-8.4.02 | Integration | Fetch assigned reviews | GET /api/reviews/assigned | List of projects assigned to reviewer | P1 |
| T-8.4.03 | Unit | Filter by state | Select "In Review" filter | Only in_review projects shown | P2 |
| T-8.4.04 | E2E | Reviewer flow: view → comment → accept | Full reviewer journey | Project moves to accepted | P1 |

---

### FA-9: Landing Page & Project Management

#### F-9.1: Project Creation

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-9.1.01 | Unit | Create button opens modal | Click "Create Project" | Modal with type selection | P1 |
| T-9.1.02 | Unit | Modal shows two project type options | Modal opened | Software and Non-Software options visible | P1 |
| T-9.1.03 | Integration | Create software project | POST /api/projects {project_type: "software"} | Project created with type=software | P1 |
| T-9.1.04 | Integration | Create non-software project | POST /api/projects {project_type: "non_software"} | Project created with type=non_software | P1 |
| T-9.1.05 | E2E | Create project and navigate to workspace | Complete creation flow | Redirected to /project/:id | P1 |

#### F-9.2: Project List

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-9.2.01 | Integration | Fetch user's projects | GET /api/projects | List of owned + collaborated projects | P1 |
| T-9.2.02 | Unit | Project cards show type badge | Software and non-software projects | Different badges displayed | P1 |
| T-9.2.03 | Unit | Filter by project type | Select "Software" filter | Only software projects shown | P2 |
| T-9.2.04 | Unit | Filter by state | Select "In Review" filter | Only in_review projects shown | P2 |
| T-9.2.05 | Unit | Search by title | Type "automation" | Projects with matching titles shown | P2 |

#### F-9.3: Soft Delete & Trash

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-9.3.01 | Integration | Move to trash | DELETE /api/projects/:id | `deleted_at` set, project hidden from main list | P1 |
| T-9.3.02 | Integration | Trash page lists deleted projects | GET /api/projects?deleted=true | Deleted projects returned | P1 |
| T-9.3.03 | Integration | Restore from trash | POST /api/projects/:id/restore | `deleted_at` cleared | P1 |
| T-9.3.04 | Integration | Permanent delete | DELETE /api/projects/:id/permanent | Record hard-deleted | P2 |
| T-9.3.05 | Integration | Auto-purge after 30 days | Cron job runs | Projects with `deleted_at` > 30 days removed | P3 |

#### F-9.4: Share Link

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-9.4.01 | Integration | Generate share link | POST /api/projects/:id/share | `share_link_token` created | P1 |
| T-9.4.02 | Integration | Access via share link | GET /share/:token | Project loaded in read-only mode | P1 |
| T-9.4.03 | Integration | Revoke share link | DELETE /api/projects/:id/share | `share_link_token` cleared | P1 |
| T-9.4.04 | Unit | Share link UI shows token | Share link generated | URL displayed with copy button | P1 |

---

### FA-10: Admin

#### F-10.1: AI Context Management

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-10.1.01 | Unit | Context tab shows three buckets | Admin user | Global, Software, Non-Software sections | P1 |
| T-10.1.02 | Integration | Upload to global bucket | POST /api/admin/context/global with file | Chunks created with bucket_type="global" | P1 |
| T-10.1.03 | Integration | Upload to software bucket | POST /api/admin/context/software with file | Chunks created with bucket_type="software" | P1 |
| T-10.1.04 | Integration | Upload to non-software bucket | POST /api/admin/context/non_software with file | Chunks created with bucket_type="non_software" | P1 |
| T-10.1.05 | Integration | Delete context chunk | DELETE /api/admin/context/chunks/:id | Chunk removed, embeddings cleared | P2 |
| T-10.1.06 | AI Agent | RAG search respects bucket isolation | Software project queries context | Only global + software chunks searched | P1 |

#### F-10.2: Parameter Management

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-10.2.01 | Unit | Parameters tab lists all config | Admin user | All AdminParameter records displayed | P1 |
| T-10.2.02 | Integration | Update parameter | PATCH /api/admin/parameters/:key {value} | Parameter updated | P1 |
| T-10.2.03 | Integration | Reset to default | POST /api/admin/parameters/:key/reset | `value` = `default_value` | P2 |

#### F-10.3: User Management

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-10.3.01 | Integration | List all users | GET /api/admin/users | All users with roles | P1 |
| T-10.3.02 | Integration | Update user roles | PATCH /api/admin/users/:id {roles: ["user", "reviewer"]} | Roles updated | P1 |
| T-10.3.03 | Integration | Non-admin blocked from admin endpoints | Regular user calls /api/admin/users | 403 Forbidden | P1 |

---

## 2. API Endpoint Tests

### 2.1 Project Service (Core)

#### POST /api/projects

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-01 | Integration | Create software project | `{project_type: "software"}` | 201, project created | P1 |
| T-API-P-02 | Integration | Create non-software project | `{project_type: "non_software"}` | 201, project created | P1 |
| T-API-P-03 | Integration | Invalid project type rejected | `{project_type: "invalid"}` | 400 validation error | P1 |
| T-API-P-04 | Integration | Unauthenticated request blocked | No auth token | 401 Unauthorized | P1 |

#### GET /api/projects

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-05 | Integration | List user's projects | Auth user with 3 projects | 200, array of 3 projects | P1 |
| T-API-P-06 | Integration | Include collaborated projects | User collaborates on 2 projects | 200, includes collaborated projects | P1 |
| T-API-P-07 | Integration | Exclude deleted by default | User has 1 deleted project | 200, deleted project not in list | P1 |
| T-API-P-08 | Integration | Include deleted with flag | `?deleted=true` | 200, only deleted projects | P1 |

#### GET /api/projects/:id

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-09 | Integration | Fetch owned project | Valid project ID | 200, project details | P1 |
| T-API-P-10 | Integration | Fetch collaborated project | Collaborator requests project | 200, project details | P1 |
| T-API-P-11 | Integration | Block unauthorized access | User requests other's private project | 403 Forbidden | P1 |
| T-API-P-12 | Integration | 404 for non-existent project | Invalid UUID | 404 Not Found | P1 |

#### PATCH /api/projects/:id

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-13 | Integration | Update title | `{title: "New Title"}` | 200, title updated, WebSocket broadcast | P1 |
| T-API-P-14 | Integration | Manual edit sets flag | `{title: "..."}` | `title_manually_edited=true` | P1 |
| T-API-P-15 | Integration | Update agent mode | `{agent_mode: "silent"}` | 200, mode updated | P1 |
| T-API-P-16 | Integration | Block update in review state | `state=in_review`, update title | 403 or 400 error | P1 |
| T-API-P-17 | Integration | Collaborator can update | Collaborator updates title | 200, title updated | P1 |

#### DELETE /api/projects/:id

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-18 | Integration | Soft delete | DELETE request | 200, `deleted_at` set | P1 |
| T-API-P-19 | Integration | Only owner can delete | Collaborator attempts delete | 403 Forbidden | P1 |

#### POST /api/projects/:id/submit

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-P-20 | Integration | Submit for review | `{reviewer_ids: [...]}` | 200, state → in_review, version created | P1 |
| T-API-P-21 | Integration | Block if insufficient | Draft has insufficient sections, gaps=false | 400 error with details | P1 |
| T-API-P-22 | Integration | Allow with gaps flag | Insufficient sections, `allow_information_gaps=true` | 200, submission allowed | P2 |
| T-API-P-23 | Integration | Assign reviewers | Submit with 2 reviewer IDs | 2 ReviewAssignment records created | P1 |

### 2.2 Chat Service

#### POST /api/projects/:id/messages

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-C-01 | Integration | Send user message | `{content: "Hello"}` | 201, message created, AI pipeline triggered | P1 |
| T-API-C-02 | Integration | Empty message rejected | `{content: ""}` | 400 validation error | P1 |
| T-API-C-03 | Integration | Message in review state blocked | `state=in_review`, send message | 403 Forbidden | P1 |
| T-API-C-04 | Integration | Collaborator can send message | Collaborator sends message | 201, message created | P1 |

#### GET /api/projects/:id/messages

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-C-05 | Integration | Fetch message history | Valid project ID | 200, array of messages | P1 |
| T-API-C-06 | Integration | Pagination support | `?limit=20&offset=40` | 200, paginated results | P2 |
| T-API-C-07 | Integration | Include AI messages | Project with AI responses | 200, includes AI messages | P1 |

### 2.3 Requirements Service

#### POST /api/projects/:id/requirements

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-R-01 | Integration | Create epic | `{item_type: "epic", title: "...", description: "..."}` | 201, epic created | P1 |
| T-API-R-02 | Integration | Create user story under epic | `{item_type: "user_story", parent_id: epic.id, ...}` | 201, story created | P1 |
| T-API-R-03 | Integration | Create milestone | `{item_type: "milestone", ...}` | 201, milestone created | P1 |
| T-API-R-04 | Integration | Reject epic in non-software project | Non-software project, create epic | 400 validation error | P1 |
| T-API-R-05 | Integration | Reject milestone in software project | Software project, create milestone | 400 validation error | P1 |

#### PATCH /api/projects/:id/requirements/:item_id

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-R-06 | Integration | Update requirement title | `{title: "Updated"}` | 200, title updated | P1 |
| T-API-R-07 | Integration | Update blocked in review state | `state=in_review`, update requirement | 403 Forbidden | P1 |

#### DELETE /api/projects/:id/requirements/:item_id

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-R-08 | Integration | Delete requirement | DELETE request | 200, item soft-deleted | P1 |
| T-API-R-09 | Integration | Cascade delete children | Delete epic with stories | All children deleted | P2 |

#### PATCH /api/projects/:id/requirements/reorder

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-R-10 | Integration | Reorder items | `{items: [{id, order_index}, ...]}` | 200, order updated | P1 |

### 2.4 Requirements Document Service

#### GET /api/projects/:id/draft

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-D-01 | Integration | Fetch draft | Valid project ID | 200, draft with all sections | P1 |
| T-API-D-02 | Integration | 404 if no draft exists | Project never submitted | 404 Not Found | P2 |

#### PATCH /api/projects/:id/draft

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-D-03 | Integration | Update section | `{section_title: "New Title"}` | 200, section updated | P1 |
| T-API-D-04 | Integration | Lock section | `{section_locks: {title: true}}` | 200, lock saved | P1 |
| T-API-D-05 | Integration | Update blocked in review | `state=in_review`, update draft | 403 Forbidden | P1 |

#### GET /api/projects/:id/versions

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-D-06 | Integration | Fetch version list | Project with 3 submissions | 200, array of 3 versions | P1 |

#### GET /api/projects/:id/versions/:version_number

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-D-07 | Integration | Fetch specific version | Version number 2 | 200, version 2 snapshot | P1 |
| T-API-D-08 | Integration | 404 for non-existent version | Version 99 | 404 Not Found | P2 |

### 2.5 Review Service

#### POST /api/projects/:id/review/accept

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-RV-01 | Integration | Accept project | Reviewer accepts | 200, state → accepted | P1 |
| T-API-RV-02 | Integration | Non-reviewer blocked | Regular user accepts | 403 Forbidden | P1 |

#### POST /api/projects/:id/review/reject

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-RV-03 | Integration | Reject with comment | `{comment: "Needs work"}` | 200, state → rejected | P1 |
| T-API-RV-04 | Integration | Reject without comment blocked | No comment field | 400 validation error | P1 |

#### POST /api/projects/:id/review/drop

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-RV-05 | Integration | Drop with reason | `{comment: "Out of scope"}` | 200, state → dropped | P1 |

#### POST /api/projects/:id/review/comments

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-API-RV-06 | Integration | Add review comment | `{content: "Please clarify"}` | 201, timeline entry created | P1 |
| T-API-RV-07 | Integration | Reply to comment | `{content: "...", parent_entry_id: ...}` | 201, reply created | P2 |

---

## 3. Data Model Tests

### 3.1 Project Model

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-DM-P-01 | Unit | Project type enum validation | Invalid type value | ValidationError | P1 |
| T-DM-P-02 | Unit | State enum validation | Invalid state | ValidationError | P1 |
| T-DM-P-03 | Unit | Default project type is software | Create without type | `project_type="software"` | P1 |
| T-DM-P-04 | Unit | Deleted projects filtered by default manager | Query Project.objects.all() | Excludes deleted_at != NULL | P1 |

### 3.2 RequirementsItem Model

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-DM-R-01 | Unit | Item type validation | Invalid item_type | ValidationError | P1 |
| T-DM-R-02 | Unit | Parent-child relationship constraint | Story with invalid parent type | ValidationError | P1 |
| T-DM-R-03 | Unit | Order index defaults to 0 | Create without order_index | `order_index=0` | P2 |

### 3.3 RequirementsDocumentDraft Model

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-DM-D-01 | Unit | One draft per project constraint | Create second draft for same project | IntegrityError | P1 |
| T-DM-D-02 | Unit | requirements_structure defaults to empty dict | Create draft without structure | `requirements_structure={}` | P1 |
| T-DM-D-03 | Unit | section_locks defaults to empty dict | Create draft | `section_locks={}` | P1 |

### 3.4 RequirementsDocumentVersion Model

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-DM-V-01 | Unit | Version number auto-increments | Create second version | `version_number=2` | P1 |
| T-DM-V-02 | Unit | requirements_structure is immutable | Frozen version | Field is read-only | P1 |

---

## 4. Component Tests (Frontend)

### 4.1 ProjectWorkspace Component

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-FE-W-01 | Unit | Component renders for software project | `project_type="software"` | Workspace with requirements panel showing epics | P1 |
| T-FE-W-02 | Unit | Component renders for non-software project | `project_type="non_software"` | Workspace with requirements panel showing milestones | P1 |
| T-FE-W-03 | Unit | Title edit updates Redux state | Edit title | Redux action dispatched | P1 |

### 4.2 RequirementsPanel Component

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-FE-RP-01 | Unit | Renders epics for software project | Software project with 3 epics | 3 accordion sections | P1 |
| T-FE-RP-02 | Unit | Renders milestones for non-software | Non-software project with 2 milestones | 2 accordion sections | P1 |
| T-FE-RP-03 | Unit | Add button opens modal | Click "Add Epic" | Modal visible | P1 |
| T-FE-RP-04 | Unit | Drag reorder triggers optimistic update | Drag epic | UI reorders immediately | P1 |

### 4.3 RequirementsDocumentView Component

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-FE-RD-01 | Unit | Renders all 6 sections | Full draft | All sections displayed | P1 |
| T-FE-RD-02 | Unit | Renders requirements structure hierarchically | Draft with epics/stories | Nested list rendered | P1 |
| T-FE-RD-03 | Unit | Lock icon toggles lock state | Click lock on title | PATCH request sent | P1 |
| T-FE-RD-04 | Unit | Locked sections show indicator | `section_locks.title=true` | Lock icon visible | P1 |

### 4.4 ProjectCreationModal Component

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-FE-PC-01 | Unit | Modal shows two project type cards | Modal opened | Software and Non-Software cards | P1 |
| T-FE-PC-02 | Unit | Select type enables create button | Click "Software" | Create button enabled | P1 |
| T-FE-PC-03 | Unit | Create dispatches action | Click create | Redux createProject action | P1 |

### 4.5 LandingPage Component

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-FE-LP-01 | Unit | Renders project list | User with 5 projects | 5 project cards | P1 |
| T-FE-LP-02 | Unit | Project cards show type badge | Mixed project types | Different badges on cards | P1 |
| T-FE-LP-03 | Unit | Filter by type works | Select "Software" | Only software projects shown | P2 |

---

## 5. AI Agent Tests

### 5.1 Facilitator Agent

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-AI-F-01 | AI Agent | Greeting on first message | New software project, first user message | Welcoming response asking about features | P1 |
| T-AI-F-02 | AI Agent | Greeting for non-software project | New non-software project, first message | Response asking about phases/milestones | P1 |
| T-AI-F-03 | AI Agent | Call update_requirements_structure | User describes 3 features | Tool call with 3 epics | P1 |
| T-AI-F-04 | AI Agent | Adapt to project type in prompts | Software vs non-software | Different terminology used | P1 |
| T-AI-F-05 | AI Agent | Title suggestion | 3+ messages, no manual title | Suggests appropriate title | P1 |
| T-AI-F-06 | AI Agent | Delegate to Context Agent | User asks about existing systems | Delegation message sent | P1 |
| T-AI-F-07 | AI Agent | Silent mode respect | `agent_mode=silent`, no @ai | No response | P1 |
| T-AI-F-08 | AI Agent | @ai mention overrides silent | `agent_mode=silent`, @ai mention | Response generated | P1 |

### 5.2 Summarizing AI Agent

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-AI-S-01 | AI Agent | Generate complete draft | Chat + requirements for software project | All 6 sections + requirements_structure with epics | P1 |
| T-AI-S-02 | AI Agent | Generate non-software draft | Non-software project | requirements_structure with milestones | P1 |
| T-AI-S-03 | AI Agent | Respect section locks | 2 sections locked | Only 4 sections regenerated | P1 |
| T-AI-S-04 | AI Agent | Gaps mode with /TODO | Insufficient info, gaps=true | Sections have "/TODO" markers | P2 |
| T-AI-S-05 | AI Agent | Readiness evaluation | Generate draft | `readiness_evaluation` populated for all sections | P1 |
| T-AI-S-06 | AI Agent | Insufficient sections marked | Incomplete chat | Some sections marked "insufficient" | P1 |

### 5.3 Context Agent

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-AI-C-01 | AI Agent | RAG search in global bucket | Any project, context query | Searches global bucket | P1 |
| T-AI-C-02 | AI Agent | RAG search in software bucket | Software project query | Searches global + software buckets | P1 |
| T-AI-C-03 | AI Agent | RAG search in non-software bucket | Non-software project query | Searches global + non_software buckets | P1 |
| T-AI-C-04 | AI Agent | No context found response | Query with no matches | Polite "no information" message | P2 |
| T-AI-C-05 | AI Agent | Context with sources | Matching chunks found | Response includes source citations | P2 |

---

## 6. WebSocket Tests

### 6.1 Project Channel

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-WS-P-01 | Integration | Join project channel | WebSocket connect to project/:id | Connection established | P1 |
| T-WS-P-02 | Integration | Receive chat message event | User B sends message | User A receives `chat.message.created` | P1 |
| T-WS-P-03 | Integration | Receive requirements update | User B adds epic | User A receives `requirements.item.created` | P1 |
| T-WS-P-04 | Integration | Receive draft update | User B edits draft section | User A receives `draft.section.updated` | P1 |
| T-WS-P-05 | Integration | Presence broadcast | User joins | Other users receive `user.joined` | P1 |
| T-WS-P-06 | Integration | Leave broadcasts | User disconnects | Other users receive `user.left` | P1 |

---

## 7. E2E Tests

### 7.1 Project Creation Flow

| Test ID | Layer | Description | Steps | Expected Outcome | Priority |
|---------|-------|-------------|-------|------------------|----------|
| T-E2E-01 | E2E | Create software project end-to-end | 1. Click "Create Project"<br>2. Select "Software"<br>3. Confirm | Redirected to workspace, project in DB | P1 |
| T-E2E-02 | E2E | Create non-software project | Same as above, select "Non-Software" | Workspace shows milestone structure | P1 |

### 7.2 Requirements Assembly Flow

| Test ID | Layer | Description | Steps | Expected Outcome | Priority |
|---------|-------|-------------|-------|------------------|----------|
| T-E2E-03 | E2E | Add requirements via UI | 1. Create project<br>2. Click "Add Epic"<br>3. Fill form<br>4. Save | Epic appears in panel | P1 |
| T-E2E-04 | E2E | Add requirements via AI | 1. Create project<br>2. Chat "I need features X, Y, Z"<br>3. Wait for AI | AI creates epics/stories | P1 |
| T-E2E-05 | E2E | Reorder requirements | 1. Open project with epics<br>2. Drag epic to new position | Order persisted, visible to collaborators | P2 |

### 7.3 Submission & Review Flow

| Test ID | Layer | Description | Steps | Expected Outcome | Priority |
|---------|-------|-------------|-------|------------------|----------|
| T-E2E-06 | E2E | Submit for review | 1. Create project<br>2. Add requirements<br>3. Click Submit<br>4. Select reviewers | State → in_review, reviewers notified | P1 |
| T-E2E-07 | E2E | Reviewer accepts | 1. Reviewer opens project<br>2. Reviews content<br>3. Clicks Accept | State → accepted | P1 |
| T-E2E-08 | E2E | Reviewer rejects | 1. Reviewer rejects with comment<br>2. Owner sees rejection | State → rejected, comment visible | P1 |
| T-E2E-09 | E2E | Resubmit after rejection | 1. Owner edits project<br>2. Resubmits | New version created, state → in_review | P1 |

### 7.4 Collaboration Flow

| Test ID | Layer | Description | Steps | Expected Outcome | Priority |
|---------|-------|-------------|-------|------------------|----------|
| T-E2E-10 | E2E | Invite collaborator | 1. Owner invites user<br>2. Invitee accepts | Both see project, real-time sync | P1 |
| T-E2E-11 | E2E | Real-time chat sync | 1. User A sends message<br>2. User B observes | Message appears for User B instantly | P1 |
| T-E2E-12 | E2E | Real-time requirements sync | 1. User A adds epic<br>2. User B observes | Epic appears for User B | P1 |

---

## 8. Performance & Load Tests

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-PERF-01 | Load | 100 concurrent users viewing projects | JMeter/k6 script | Response time < 500ms, 0 errors | P2 |
| T-PERF-02 | Load | 50 concurrent AI requests | Simulate 50 chat messages | All responses within 10s | P2 |
| T-PERF-03 | Load | WebSocket scalability | 500 concurrent WebSocket connections | All connections stable | P2 |
| T-PERF-04 | Load | Large requirements structure | Project with 20 epics, 100 stories | Renders in < 2s | P3 |

---

## 9. Security Tests

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-SEC-01 | Integration | Unauthorized access blocked | Access other user's private project | 403 Forbidden | P1 |
| T-SEC-02 | Integration | XSS prevention | Chat message with `<script>` tag | Tag escaped, not executed | P1 |
| T-SEC-03 | Integration | SQL injection prevention | Malicious query parameter | No SQL error, query sanitized | P1 |
| T-SEC-04 | Integration | CSRF protection | POST without CSRF token | 403 Forbidden | P1 |
| T-SEC-05 | Integration | Role-based access | Regular user accesses admin endpoint | 403 Forbidden | P1 |

---

## 10. Accessibility Tests

| Test ID | Layer | Description | Input | Expected Output | Priority |
|---------|-------|-------------|-------|-----------------|----------|
| T-A11Y-01 | E2E | Keyboard navigation | Tab through workspace | All interactive elements reachable | P1 |
| T-A11Y-02 | E2E | Screen reader labels | NVDA/JAWS on requirements panel | All items properly announced | P1 |
| T-A11Y-03 | E2E | Color contrast | WCAG contrast checker | All text meets AA standard | P2 |
| T-A11Y-04 | E2E | Focus indicators | Tab through UI | Visible focus ring on all elements | P2 |

---

## Summary

**Total test cases:** 300+

**By priority:**
- P1 (Critical): ~220
- P2 (Important): ~65
- P3 (Nice-to-have): ~15

**By layer:**
- Unit: ~80
- Integration: ~110
- AI Agent: ~30
- E2E: ~25
- Performance/Security/A11y: ~25

**Coverage targets:**
- Backend code coverage: >85%
- Frontend code coverage: >80%
- E2E critical path coverage: 100%
