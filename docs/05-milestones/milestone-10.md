# Milestone 10: Review Workflow

## Overview
- **Execution order:** 10 (runs after M9)
- **Estimated stories:** 10
- **Dependencies:** M9
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-1.5 | Idea Lifecycle (state transitions) | P1 | features.md FA-1 |
| F-4.6 | Review Section (below fold) | P1 | features.md FA-4 |
| F-4.7 | Document Versioning (immutable snapshots) | P1 | features.md FA-4 |
| F-4.10 | Reviewer Assignment on Submit | P1 | features.md FA-4 |
| F-4.11 | Multiple Reviewers | P1 | features.md FA-4 |
| F-10.1 | Review Page Access | P1 | features.md FA-10 |
| F-10.2 | Categorized Idea Lists | P1 | features.md FA-10 |
| F-10.3 | Self-Assignment | P1 | features.md FA-10 |
| F-10.4 | Conflict of Interest | P1 | features.md FA-10 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | UPDATE (state) | state | data-model.md |
| brd_versions | INSERT | All columns, pdf_file_path | data-model.md |
| review_assignments | INSERT, UPDATE, SELECT | idea_id, reviewer_id, assigned_by, unassigned_at | data-model.md |
| review_timeline_entries | INSERT, SELECT | All columns (comment, state_change, resubmission) | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/submit | POST | Submit idea for review | Bearer | api-design.md |
| /api/ideas/:id/review/accept | POST | Accept idea | Bearer (Reviewer) | api-design.md |
| /api/ideas/:id/review/reject | POST | Reject idea (mandatory comment) | Bearer (Reviewer) | api-design.md |
| /api/ideas/:id/review/drop | POST | Drop idea (mandatory comment) | Bearer (Reviewer) | api-design.md |
| /api/ideas/:id/review/undo | POST | Undo review action (mandatory comment) | Bearer (Reviewer) | api-design.md |
| /api/ideas/:id/review/timeline | GET | List timeline entries | Bearer | api-design.md |
| /api/ideas/:id/review/timeline | POST | Post timeline comment | Bearer | api-design.md |
| /api/reviews | GET | List ideas for review (categorized) | Bearer (Reviewer) | api-design.md |
| /api/reviews/:id/assign | POST | Self-assign | Bearer (Reviewer) | api-design.md |
| /api/reviews/:id/unassign | POST | Self-unassign | Bearer (Reviewer) | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Review Page (/reviews) | Page | page-layouts.md S3 |
| ReviewCard | Feature | component-specs.md S2.3 |
| ReviewTimeline | Feature | component-specs.md S10 |
| TimelineEntry | Feature | component-specs.md S10.2 |
| CommentInput | Feature | component-specs.md S10.3 |
| SubmitArea | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API]** Submit flow — POST /api/ideas/:id/submit: create BRD version, generate PDF, transition state open->in_review, create review assignments, create timeline entry
2. **[API]** Review assignments — self-assign, self-unassign, conflict of interest check (reviewer != owner/co-owner)
3. **[API]** Reviewer actions — accept, reject (mandatory comment), drop (mandatory comment), undo (mandatory comment, returns to in_review)
4. **[API]** Review timeline — GET entries (with nested replies), POST comments, POST nested replies
5. **[API]** Review page list — GET /api/reviews with categories (assigned, unassigned, accepted, rejected, dropped)
6. **[Frontend]** Review page layout — /reviews route (Reviewer role-gated), categorized lists with ReviewCards
7. **[Frontend]** Self-assignment UI — Assign/Unassign buttons on review cards, conflict of interest display
8. **[Frontend]** Review section below fold — BRD preview, assigned reviewers, state label, timeline
9. **[Frontend]** Review timeline UI — chronological feed (comments, state changes, resubmissions with version links), nested replies, comment input
10. **[Frontend]** Submit flow UI — submit area in Review tab (message field, reviewer selector, submit button), resubmission flow

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Submit flow | ~10,000 | api-design.md (submit), data-model.md (versions, assignments) | 6-8 files | High | Atomic multi-table transaction |
| 2 | Review assignments | ~5,000 | api-design.md (reviews), features.md (F-10.3, F-10.4) | 3-4 files | Medium | Conflict of interest |
| 3 | Reviewer actions | ~8,000 | api-design.md (review actions), features.md (F-1.5, F-4.11) | 4-6 files | High | State machine, mandatory comments |
| 4 | Review timeline | ~5,000 | api-design.md (timeline), data-model.md | 3-4 files | Medium | Nested replies |
| 5 | Review page list | ~4,000 | api-design.md (reviews list) | 2-3 files | Low | — |
| 6 | Review page layout | ~5,000 | page-layouts.md (S3) | 3-4 files | Medium | Categorized collapsible lists |
| 7 | Self-assignment UI | ~3,000 | features.md (F-10.3) | 2-3 files | Low | — |
| 8 | Review section | ~6,000 | page-layouts.md (S2, review section) | 4-5 files | Medium | Below-fold layout |
| 9 | Timeline UI | ~6,000 | component-specs.md (S10) | 4-5 files | Medium | Multiple entry types |
| 10 | Submit flow UI | ~5,000 | page-layouts.md (review tab submit area) | 3-4 files | Medium | Reviewer selector |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~57,000
- **Cumulative domain size:** Large (state machine + review workflow + timeline + 2 pages)
- **Information loss risk:** Medium (7) — many cross-cutting concerns (state transitions affect visibility, locking, notifications)
- **Context saturation risk:** Medium
- **Heavy stories:** 2 (submit flow, reviewer actions)

## Milestone Acceptance Criteria
- [ ] Submit creates immutable BRD version + PDF, transitions to in_review
- [ ] Brainstorming section locks on submit
- [ ] Reviewer can accept (no comment required), reject (mandatory comment), drop (mandatory comment)
- [ ] Undo returns idea to in_review (mandatory comment)
- [ ] Review page shows categorized lists for Reviewer role
- [ ] Self-assignment/unassignment works
- [ ] Conflict of interest: reviewer cannot review own idea
- [ ] Timeline shows comments, state changes, resubmissions with version links
- [ ] Nested replies work in timeline
- [ ] Resubmission creates new BRD version, links old and new in timeline
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M9

## Notes
- Notification dispatching on review events is wired in M12 (Notification System). State transitions work but notifications are not sent yet.
- Similar ideas in review section (F-4.12) comes in M13 (Similarity).
- Email notifications for review state changes come in M12.
