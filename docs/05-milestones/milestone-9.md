# Milestone 9: Review Workflow

## Overview
- **Wave:** 5
- **Estimated stories:** 8
- **Must complete before starting:** M7
- **Can run parallel with:** M10
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-1.5 | Idea Lifecycle (state transitions via review) | P1 | features.md |
| F-4.5 | Submit for Review | P1 | features.md |
| F-4.6 | Resubmission | P1 | features.md |
| F-4.10 | Reviewer Assignment | P1 | features.md |
| F-4.11 | Review Actions (accept/reject/drop/undo) | P1 | features.md |
| FA-10 | Review Page (reviewer dashboard) | P1 | features.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | UPDATE | state (open→in_review→accepted/rejected/dropped) | data-model.md |
| brd_versions | CREATE | version_number, sections, submitted_by, submission_message, pdf_file_path | data-model.md |
| review_assignments | CRUD | idea_id, reviewer_id, assigned_at, assigned_by | data-model.md |
| review_timeline_entries | CREATE, READ | idea_id, entry_type, user_id, content, brd_version_id, parent_entry_id | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/ideas/:id/submit | POST | Submit idea for review | Owner | api-design.md |
| POST /api/ideas/:id/review/accept | POST | Accept idea | Reviewer | api-design.md |
| POST /api/ideas/:id/review/reject | POST | Reject idea (mandatory comment) | Reviewer | api-design.md |
| POST /api/ideas/:id/review/drop | POST | Drop idea (mandatory comment) | Reviewer | api-design.md |
| POST /api/ideas/:id/review/undo | POST | Undo review action (mandatory comment) | Reviewer | api-design.md |
| POST /api/ideas/:id/review/resubmit | POST | Resubmit after rejection | Owner | api-design.md |
| GET /api/ideas/:id/review/timeline | GET | Get review timeline | User | api-design.md |
| POST /api/ideas/:id/review/timeline | POST | Add timeline comment | User | api-design.md |
| POST /api/ideas/:id/review/timeline/:entryId/reply | POST | Reply to timeline entry | User | api-design.md |
| GET /api/ideas/:id/review/assignments | GET | Get reviewers for idea | User | api-design.md |
| POST /api/ideas/:id/review/assignments | POST | Assign reviewer (self or by submitter) | Reviewer/Owner | api-design.md |
| DELETE /api/ideas/:id/review/assignments/:userId | DELETE | Unassign self | Reviewer | api-design.md |
| GET /api/reviews | GET | Reviewer dashboard — list ideas for review | Reviewer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| ReviewTimeline | Feature | component-inventory.md |
| TimelineEntry | Feature | component-inventory.md |
| CommentInput | Feature | component-inventory.md |
| ReviewCard | Feature | component-inventory.md |
| SubmitArea (complete) | Feature | component-inventory.md |
| Review Page (/reviews) | Page | pages.md |

## Story Outline (Suggested Order)
1. **[API] Submit flow** — POST /api/ideas/:id/submit: validate idea in open/rejected state, validate BRD draft has no /TODO markers (if allow_info_gaps=true, check markers resolved), create brd_versions immutable snapshot (copy all 6 sections from brd_drafts), trigger PDF generation (gRPC GeneratePdf → store PDF), transition state: open→in_review or rejected→in_review, lock brainstorming section (chat + board become read-only), create review_timeline_entry (type: state_change or resubmission). Accept optional submission_message and optional reviewer_ids array. Publish idea.state.changed event.
2. **[API+Frontend] Reviewer assignment** — On submit: if reviewer_ids provided, create review_assignments for each. Reviewers can self-assign from review page (POST assignments with own user_id). Unassign self (DELETE). Validation: reviewer cannot be owner or co-owner (conflict of interest). SubmitArea component (replace M7 stub): enable submit button, add optional message textarea, add reviewer multi-select (search users with Reviewer role). Review section in workspace: show assigned reviewers with avatars.
3. **[Frontend] Review section below fold** — Replace M7 stub. State label badge (In Review / Accepted / Rejected / Dropped). Assigned reviewer list with avatars. Small BRD preview card linking to latest brd_version. Only visible when has_been_submitted=true. Position: below brainstorming section, above fold boundary.
4. **[Frontend+API] Review timeline** — ReviewTimeline component: vertical timeline with entries. TimelineEntry variants: state_change (icon + "Status changed to [state]" + timestamp), comment (avatar + name + text + timestamp + reply button), resubmission (icon + "Resubmitted" + links to v1 and v2 + diff indicator). CommentInput: standalone textarea + send button for adding comments. Nested replies: POST reply → appears indented under parent. Timeline ordered by created_at ASC. Real-time updates via WebSocket.
5. **[API] Review actions** — POST accept: validate idea in in_review state, validate user is assigned reviewer, transition state to accepted, create timeline entry, lock all sections permanently, publish idea.state.changed event. POST reject: validate, require comment (400 if missing), transition to rejected, unlock brainstorming for rework, create timeline entry with comment. POST drop: validate, require comment, transition to dropped, lock all permanently, create timeline entry. All actions: record who acted and when.
6. **[API] Review undo actions** — POST /api/ideas/:id/review/undo: validate idea in accepted/rejected/dropped state, validate user is the reviewer who performed the last action (or any assigned reviewer), require mandatory comment explaining why undoing. Undo accepted → in_review (unlock permanent locks back to review-locked). Undo rejected → in_review (re-lock brainstorming). Undo dropped → in_review (unlock permanent locks back to review-locked). Create timeline entry (type: undo_action) with reference to original action. Publish idea.state.changed event.
7. **[Frontend+API] Review page** — /reviews page (reviewer dashboard). Categorized lists: Assigned to Me (in_review, assigned to current user), Unassigned (in_review, no reviewer assigned — reviewer can self-assign), Accepted (accepted, assigned to current user), Rejected (rejected, assigned to current user), Dropped (dropped, assigned to current user). ReviewCard component: extends IdeaCard with author info, submission date, BRD version number, action button (Open Review). Search by title or UUID. Pagination per category.
8. **[API+Frontend] Conflict of interest + multi-reviewer conflict resolution** — Conflict of interest: prevent owner/co-owner from being assigned as reviewer (API validation + frontend filter). Multi-reviewer conflict resolution: when multiple reviewers act on same idea, latest action wins (server timestamp). Both actions recorded in timeline for audit trail. Owner receives notification for final state only (not intermediate). No error on conflicting actions — the second action simply updates state.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| IdeaCard | Available | M2 |
| Workspace page shell | Available | M2 |
| BRD generation + versioning | Available | M7 |
| PDF generation | Available | M7 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/features/review/`
- `frontend/src/pages/ReviewPage/`
- `services/gateway/apps/review/`
- `services/core/apps/review/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/pages/IdeaWorkspace/` (wire SubmitArea, review section, timeline)
- `frontend/src/features/brd/` (enable submit button, wire reviewer selector)
- `frontend/src/router.tsx` (add /reviews route)
- `services/gateway/apps/websocket/consumers.py` (broadcast state change events)

## Milestone Acceptance Criteria
- [ ] Submit flow: creates BRD version, generates PDF, transitions state, locks brainstorming
- [ ] Reviewer assignment on submit and self-assignment from review page
- [ ] Review section shows state, reviewers, BRD preview when has_been_submitted=true
- [ ] Review timeline shows all entries (state changes, comments, replies, resubmissions)
- [ ] Accept/Reject/Drop actions work with correct state transitions
- [ ] Reject/Drop require mandatory comment (400 without)
- [ ] Undo actions reverse state with mandatory comment
- [ ] Resubmission creates new BRD version, re-locks brainstorming
- [ ] Review page shows categorized lists for reviewer
- [ ] Self-assign/unassign from review page works
- [ ] Conflict of interest prevents owner from being reviewer
- [ ] Multi-reviewer conflict: latest action wins, both recorded
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M8, M12

## Notes
- **Stub: Similar ideas in review section** — SimilarIdeaCard area renders with EmptyState "No similar ideas detected". Real similar ideas data wired in M11 when similarity detection exists.
- **Stub: Email notifications for review events** — State changes, review assignments, and timeline comments fire toast-only for the current user. No persistent notifications or emails dispatched to other users. Full notification wiring in M10 (parallel — M10 wires all events including review events after merge).
- **Stub: Notification for review assignment** — Assigned reviewers see the idea in their review page list, but no bell notification or email. Wired in M10.
- Resubmission reuses M7's BRD versioning and PDF generation — no new AI/PDF code needed.
- The review undo feature is complex: it must correctly reverse lock states. Test with all 3 undo paths (undo accept, undo reject, undo drop).
