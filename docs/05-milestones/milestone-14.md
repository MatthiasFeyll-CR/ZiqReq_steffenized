# Milestone 14: Merge Advanced & Manual

## Overview
- **Execution order:** 14 (runs after M13)
- **Estimated stories:** 7
- **Dependencies:** M13
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-5.4 | State-Aware Match Behavior (append flow) | P1 | features.md FA-5 |
| F-5.5 | Merge Flow (recursive merge rules) | P1 | features.md FA-5 |
| F-5.8 | Manual Merge Request | P1 | features.md FA-5 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| merge_requests | INSERT, UPDATE | merge_type='append', reviewer_consent | data-model.md |
| ideas | UPDATE (closed_by_append, co_owner_id) | closed_by_append_id, co_owner_id | data-model.md |
| idea_collaborators | INSERT (demoted co-owners on recursive merge) | idea_id, user_id | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/merge-request | POST | Create manual merge request (with target UUID/URL) | Bearer | api-design.md |
| /api/merge-requests/:id/consent | POST | Accept/decline (including reviewer consent for append) | Bearer | api-design.md |

## Story Outline (Suggested Order)
1. **[Backend]** Append flow — open idea owner requests append to in_review idea, 3-way consent (open owner + in_review owner + reviewer)
2. **[Backend]** Append execution — close open idea (read-only, closed_by_append ref), add owner as collaborator on in_review idea
3. **[Backend]** Manual merge request — POST with target idea UUID or URL, validate target state, create merge request
4. **[Frontend]** Manual merge UI — insert UUID/URL input, browse similar ideas list (title + keywords), create request
5. **[Backend]** Recursive merge handling — when previously-merged idea (2 owners) re-merges, non-triggering co-owner demoted to collaborator
6. **[Backend]** Read-only old idea references — merged/appended ideas show reference to new idea, users can view old content
7. **[Backend + Frontend]** Merge notification events — wire similarity/merge events (request received, accepted, declined, idea closed by append)

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Append flow | ~6,000 | features.md (F-5.4), data-model.md (merge_requests) | 4-5 files | High | 3-way consent |
| 2 | Append execution | ~4,000 | features.md (F-5.4) | 3-4 files | Medium | State transitions |
| 3 | Manual merge request | ~4,000 | features.md (F-5.8) | 2-3 files | Medium | UUID/URL validation |
| 4 | Manual merge UI | ~4,000 | features.md (F-5.8) | 3-4 files | Medium | Two discovery methods |
| 5 | Recursive merge | ~5,000 | data-model.md (ideas notes on recursive merge) | 3-4 files | High | 2-owner model enforcement |
| 6 | Old idea references | ~3,000 | features.md (F-5.5 step 7-8) | 2-3 files | Low | — |
| 7 | Merge notification events | ~4,000 | features.md (F-12.5 similarity events) | 3-4 files | Medium | Event wiring |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~30,000
- **Cumulative domain size:** Medium (merge edge cases + append flow)
- **Information loss risk:** Low (4)
- **Context saturation risk:** Low
- **Heavy stories:** 2 (append flow, recursive merge)

## Milestone Acceptance Criteria
- [ ] Append flow: open idea owner can request append to in_review idea
- [ ] Append requires 3-way consent (open owner + in_review owner + reviewer)
- [ ] Append execution closes open idea, adds owner as collaborator
- [ ] Manual merge via UUID/URL entry works
- [ ] Manual merge via similar ideas browser works
- [ ] Recursive merge enforces 2-owner maximum (demotion to collaborator)
- [ ] Old ideas readable with reference to new/merged idea
- [ ] All merge notification events dispatched
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M13

## Notes
- This milestone has fewer stories (7) but higher per-story complexity due to edge cases in the merge/append logic.
- The recursive merge rule is critical: the 2-owner model must never be violated.
