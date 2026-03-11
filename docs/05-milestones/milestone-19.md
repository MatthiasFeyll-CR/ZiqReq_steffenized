# Milestone 19: E2E BRD, Review & Collaboration Tests

## Overview
- **Execution order:** 19 (runs after M18)
- **Estimated stories:** 10
- **Dependencies:** M17 (test infra), M18 (workspace + chat + board tests)
- **Type:** E2E Testing

## Purpose

Test the BRD generation and editing workflow, PDF generation, the complete review workflow (submit, reviewer actions, timeline, versioning), collaboration and sharing features, the notification system, and user notification preferences.

## Features Tested

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-4 | Review & Requirements Document (BRD, PDF, review section) | P1 | docs/01-requirements/features.md |
| FA-8 | Visibility & Sharing | P1 | docs/01-requirements/features.md |
| FA-10 | Review Page (Reviewers Only) | P1 | docs/01-requirements/features.md |
| FA-12 | Notification System | P1 | docs/01-requirements/features.md |
| FA-13 | User Notification Preferences | P2 | docs/01-requirements/features.md |

## Story Outline

### S1: E2E BRD Generation & Editing (FA-4)
- **Test: BRD generates on first Review tab open (F-4.3)** — Open Review tab → BRD generation triggers (mocked AI) → 6 sections appear with content
- **Test: BRD sections display correctly (F-4.1)** — Verify all 6 sections: Title, Short Description, Current Workflow & Pain Points, Affected Department, Core Capabilities, Success Criteria
- **Test: No fabrication — insufficient info (F-4.2)** — Idea with minimal chat → BRD sections show "Not enough information" where applicable
- **Test: Per-section editing (F-4.4)** — Edit a BRD section → section auto-locks from AI regeneration, lock indicator visible
- **Test: Manual lock/unlock toggle (F-4.4)** — Manually lock a section → lock icon visible. Unlock → section becomes AI-regenerable
- **Test: Selective regeneration (F-4.4)** — Lock 2 sections, trigger regeneration with instruction text → only unlocked sections regenerated
- **Test: Readiness evaluation (F-4.8)** — Progress indicator shows section readiness, updates on Review tab open and after state changes
- **Test: Expandable edit area (F-4.5)** — Click to expand edit area → slides left, shows all editable BRD sections with controls

**Acceptance criteria:**
- [ ] BRD generates on first tab open with all 6 sections
- [ ] Section editing, locking, and selective regeneration work
- [ ] Readiness evaluation displays correctly
- [ ] Expandable edit area functions

### S2: E2E BRD — Information Gaps & PDF (FA-4)
- **Test: Allow Information Gaps toggle (F-4.9)** — Enable toggle → BRD regenerates with `/TODO` markers for insufficient sections
- **Test: /TODO highlighting (F-4.9)** — /TODO markers highlighted in editable fields
- **Test: PDF generation rejected with /TODO (F-4.9)** — Attempt PDF generation with remaining /TODO → error message lists affected sections
- **Test: Fill /TODO gap (F-4.9)** — Edit a /TODO section → counts as user edit, section auto-locks
- **Test: PDF generation success (F-4.5)** — After all /TODO resolved (or gaps not enabled), generate PDF → success toast, PDF preview visible
- **Test: PDF download (F-4.5)** — Three-dot menu on Review tab → Download → PDF file downloads
- **Test: Progress indicator grey with gaps allowed (F-4.9)** — Enable gaps → progress indicator turns grey with "gaps allowed" text

**Acceptance criteria:**
- [ ] Information gaps toggle works with /TODO markers
- [ ] PDF generation rejected when /TODO markers remain
- [ ] PDF generation succeeds and preview displays
- [ ] PDF download works

### S3: E2E Submit for Review & Review Tab (FA-4)
- **Test: Submit with optional message (F-4.5, F-4.10)** — Fill message field, optionally assign reviewers → click Submit → state changes to in_review
- **Test: Submit creates BRD version (F-4.7)** — After submit → immutable BRD version created (verify version number)
- **Test: Submit creates PDF from BRD (F-4.7)** — PDF generated from submitted BRD version
- **Test: Review section activates after submit (F-4.6)** — Scroll to review section → top area shows BRD preview, title, assigned reviewer(s), state label
- **Test: Timeline appears (F-4.6)** — Timeline shows: submit entry, optional message as first comment
- **Test: Reviewer assignment on submit (F-4.10)** — Assign 2 reviewers → both shown in review section
- **Test: Unassigned submit (F-4.10)** — Submit without assigning → idea goes to shared review queue
- **Test: Visit Review tab without submitting (F-4.5)** — Open Review tab, edit BRD, return to brainstorming without submitting → no state change

**Acceptance criteria:**
- [ ] Submit flow works with and without reviewer assignment
- [ ] BRD version and PDF created on submit
- [ ] Review section activates with correct information
- [ ] Timeline shows submit entry

### S4: E2E Review Page — Reviewer Access (FA-10)
- **Test: Reviewer accesses Review page (F-10.1)** — Login as Reviewer (User3) → navigate to `/reviews` → page loads with categorized lists
- **Test: Categorized lists (F-10.2)** — Verify groups in order: Assigned to me, Unassigned, Accepted, Rejected, Dropped
- **Test: Self-assignment (F-10.3)** — Click self-assign on unassigned idea → moves to "Assigned to me"
- **Test: Unassign self (F-10.3)** — Unassign from assigned idea → returns to Unassigned
- **Test: Conflict of interest (F-10.4)** — Reviewer's own idea submitted → Reviewer cannot self-assign or review it
- **Test: Non-reviewer cannot access (F-10.1)** — Login as User1 (no Reviewer role) → navigate to `/reviews` → redirected/blocked
- **Test: Navigate to idea from review page** — Click idea in review list → navigated to idea workspace in review context

**Acceptance criteria:**
- [ ] Review page accessible only to Reviewers
- [ ] Categorized lists display correctly
- [ ] Self-assignment and unassignment work
- [ ] Conflict of interest prevention works

### S5: E2E Reviewer Actions & Timeline (FA-4, FA-10)
- **Test: Accept idea (F-4.11)** — Reviewer accepts → state → accepted, everything read-only
- **Test: Reject idea with mandatory comment (F-4.11)** — Reviewer rejects with comment → state → rejected, brainstorming unlocks
- **Test: Drop idea with mandatory comment (F-4.11)** — Reviewer drops with comment → state → dropped, everything read-only
- **Test: Undo accept (F-4.11)** — Reviewer undoes accept with mandatory comment → back to in_review
- **Test: Undo reject (F-4.11)** — Reviewer undoes reject with mandatory comment → back to in_review
- **Test: Undo drop (F-4.11)** — Reviewer undoes drop with mandatory comment → back to in_review
- **Test: Timeline comment (F-4.6)** — Reviewer posts comment → appears in timeline
- **Test: Timeline nested reply (F-4.6)** — Reply to a timeline comment → nested reply visible
- **Test: Timeline state change entries (F-4.6)** — State changes appear as inline entries in timeline
- **Test: Resubmission entry with version links (F-4.6)** — After rejection + resubmit → timeline entry links both BRD versions (downloadable)

**Acceptance criteria:**
- [ ] All reviewer actions (accept, reject, drop) work with mandatory comments
- [ ] All undo actions work
- [ ] Timeline shows comments, replies, state changes, resubmission links
- [ ] Both BRD versions downloadable from timeline

### S6: E2E Collaboration & Sharing (FA-8)
- **Test: Invite collaborator (F-8.2)** — Owner searches and selects user → invitation sent
- **Test: Invitation on landing page (F-8.2)** — Invitee logs in → "Invitations" list shows invite with accept/decline buttons
- **Test: Accept invitation (F-8.2)** — Invitee accepts → becomes collaborator, idea visible in "Collaborating" list
- **Test: Decline invitation (F-8.2)** — Invitee declines → invitation disappears, no access granted
- **Test: Re-invite after decline (F-8.2)** — Owner re-invites declined user → new invitation appears
- **Test: Revoke pending invitation (F-8.2)** — Owner revokes invitation before invitee responds → invitation disappears
- **Test: Collaborator edit permissions (F-8.4)** — Collaborator can send chat messages and edit board
- **Test: Visibility mode change (F-8.1)** — Private idea → invite collaborator → visibility changes to "collaborating"
- **Test: Read-only link sharing (F-8.3)** — Generate share link → another authenticated user opens link → sees idea in read-only mode
- **Test: Read-only user cannot edit (F-8.3)** — Read-only viewer attempts chat/board actions → blocked

**Acceptance criteria:**
- [ ] Full invitation flow works (invite, accept, decline, re-invite, revoke)
- [ ] Collaborator gets edit permissions
- [ ] Read-only link sharing works with edit restrictions
- [ ] Visibility mode updates correctly

### S7: E2E Collaborator Management (FA-8)
- **Test: Remove collaborator (F-8.4)** — Owner removes a collaborator → collaborator loses access
- **Test: Collaborator leaves voluntarily (F-8.4)** — Collaborator leaves idea → no longer has access
- **Test: Transfer ownership (F-8.4)** — Owner transfers ownership to collaborator → new owner has full control
- **Test: Single owner must transfer before leaving (F-8.4)** — Owner attempts to leave without transferring → blocked
- **Test: Collaborator management UI (F-8.4)** — Invite button + dropdown showing collaborator list with remove/transfer options

**Acceptance criteria:**
- [ ] Remove, leave, and transfer ownership work correctly
- [ ] Ownership transfer constraints enforced
- [ ] Management UI displays and functions correctly

### S8: E2E Notification System — Bell & Toasts (FA-12)
- **Test: Notification bell with unread count (F-12.1)** — Trigger notification-generating action → bell icon shows unread count badge
- **Test: Open notification panel (F-12.1)** — Click bell → floating window with persistent notifications
- **Test: Notification disappears after action (F-12.1)** — Act on notification (e.g., accept invitation) → notification dismissed
- **Test: Click notification navigates to context (F-12.1)** — Click notification → navigated to relevant page/idea
- **Test: Toast — success type (F-12.2)** — Trigger success action → success toast appears, auto-dismisses
- **Test: Toast — warning type (F-12.2)** — Trigger warning → warning toast appears
- **Test: Toast — error type (F-12.2)** — Trigger error → error toast appears
- **Test: Invitation banner (F-12.3)** — User with pending invitation navigates to idea → banner with accept/decline
- **Test: Accept from banner (F-12.3)** — Accept from banner → becomes collaborator, banner disappears, editing unlocked
- **Test: Decline from banner (F-12.3)** — Decline from banner → redirected to landing page

**Acceptance criteria:**
- [ ] Bell badge increments on new notifications
- [ ] Notification panel shows and allows actions
- [ ] Toast notifications appear for different types
- [ ] Invitation banner works with accept/decline

### S9: E2E Notification Events — All Types (FA-12)
- **Test: Collaboration invitation notification** — Invite user → persistent + toast notification for invitee
- **Test: Collaborator joined notification** — Invitee accepts → owner gets "Collaborator joined" notification
- **Test: Collaborator removed notification** — Owner removes collaborator → removed user gets warning notification
- **Test: Review state change notifications** — Submit idea → reviewer notified. Accept → owner notified. Reject → owner notified
- **Test: @mention notification** — @mention a user in chat → user gets notification
- **Test: Ownership transferred notification** — Transfer ownership → new owner gets notification
- **Test: Email delivery for notifications** — Trigger notification with email → verify email captured (via email helper)
- **Test: Multiple notification types in sequence** — Trigger several actions → verify all notifications arrive in correct order

**Acceptance criteria:**
- [ ] All notification event types tested (at least one test per event category)
- [ ] Both in-app (bell) and email notifications verified
- [ ] Notifications arrive in correct order

### S10: E2E User Notification Preferences (FA-13)
- **Test: Access email preferences (F-13.1)** — Open user menu → click email preferences → floating window/modal appears
- **Test: Grouped toggles (F-13.2)** — Group toggle switches all items on/off. Indeterminate state when mixed
- **Test: Disable specific email notification (F-13.1)** — Disable "Collaboration invitation" email → invite triggers in-app notification but NOT email
- **Test: Re-enable email notification** — Re-enable → next invite triggers both in-app and email
- **Test: Role-based notification groups (F-13.3)** — Reviewer sees Reviewer-only notification groups. Admin sees Admin-only groups
- **Test: Preferences persistence** — Change preferences → reload page → preferences preserved

**Acceptance criteria:**
- [ ] Email preference UI works with grouped and individual toggles
- [ ] Disabling email notification suppresses email but not in-app
- [ ] Role-based groups visible only to appropriate roles
- [ ] Preferences persist across sessions

## Execution Rule

**After implementing EACH story above:**
1. Run `npx playwright test --config=e2e/playwright.config.ts`
2. ALL tests must pass (including M17 + M18 tests)
3. If any test fails → identify root cause → fix test or production code → all green before continuing

## Per-Story Complexity Assessment

| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | BRD Generation & Editing | ~10,000 | F-4.1–F-4.4, F-4.8 | 1-2 | High | AI mock integration |
| 2 | Information Gaps & PDF | ~8,000 | F-4.5, F-4.9 | 1-2 | Medium | PDF validation |
| 3 | Submit for Review | ~8,000 | F-4.5–F-4.7, F-4.10 | 1-2 | Medium | Multi-step flow |
| 4 | Review Page | ~6,000 | FA-10 | 1-2 | Low | — |
| 5 | Reviewer Actions & Timeline | ~10,000 | F-4.6, F-4.11 | 1-2 | High | Multi-role + state |
| 6 | Collaboration & Sharing | ~9,000 | FA-8 | 1-2 | Medium | Multi-user flows |
| 7 | Collaborator Management | ~6,000 | F-8.4 | 1-2 | Medium | Ownership logic |
| 8 | Notifications — Bell & Toasts | ~7,000 | FA-12 | 1-2 | Medium | Timing |
| 9 | Notification Events | ~8,000 | F-12.5 | 1-2 | Medium | Many event types |
| 10 | Notification Preferences | ~6,000 | FA-13 | 1-2 | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~78,000
- **Cumulative domain size:** Large
- **Information loss risk:** Medium (score: 7)
- **Context saturation risk:** Medium

## Milestone Acceptance Criteria
- [ ] All BRD generation, editing, and PDF tests pass
- [ ] All review workflow tests pass (submit, reviewer actions, timeline, versioning)
- [ ] All collaboration and sharing tests pass
- [ ] All notification tests pass (bell, toasts, banners, email, preferences)
- [ ] All M17 + M18 tests still pass (no regressions)
- [ ] Any production bugs discovered are fixed and documented

## Notes
- BRD generation tests depend on AI mock mode returning structured BRD content in all 6 sections
- PDF tests need to verify the PDF is generated (file exists or preview renders) — not the PDF content quality
- Review workflow tests require switching between user roles (owner vs reviewer) within the same test
- Notification event tests are the most complex — need to trigger actions and verify both in-app and email delivery
- Email verification uses the email capture helper from M17
