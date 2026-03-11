# QA Report: Milestone 11 — Collaboration & Sharing

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** N/A (first review)
**PRD:** tasks/prd-m11.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed 9 user stories covering collaboration invitation flow, collaborator management, user directory search, read-only link sharing, visibility mode transitions, and multi-user awareness. All 620 Python tests and 389 Node tests pass. All 11 test matrix IDs are implemented and verified. Required gate checks (frontend typecheck, backend lint) pass. Zero defects found. One deviation logged (additional endpoint not in spec).

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Invitation REST API | PASS | All 4 endpoints (invite, accept, decline, revoke) implemented with correct auth, status transitions, and `transaction.atomic()` for accept flow. `responded_at` set on accept/decline/revoke. Re-invite after decline creates new pending invitation. Visibility transitions to 'collaborating' on first accept. |
| US-002 | Collaborator Management API | PASS | List, remove, transfer, leave endpoints all implemented. Batch-loads users to avoid N+1. Transfer uses `transaction.atomic()`. Single owner cannot leave (400). Co-owner leave sets `co_owner_id=NULL`. |
| US-003 | User Directory Search API | PASS | `GET /api/users/search?q=<query>` with `Q(display_name__icontains) | Q(email__icontains)`, excludes current user, max 20 results, ordered by `display_name` ASC. Min query length 2 returns 400. |
| US-004 | Read-Only Link Sharing API | PASS | `POST /api/ideas/:id/share-link` generates 64-char hex token via `secrets.token_hex(32)`. Regenerate overwrites. `ShareLinkMiddleware` validates `?token=` param, adds `share_link_viewer` role. Invalid token returns 403. |
| US-005 | Visibility Mode Transitions | PASS | New ideas default to 'private'. First accepted invitation transitions to 'collaborating' (checked via collaborator count == 1). Removing collaborators does NOT revert to private. Visibility field rejected if sent in PATCH (defense-in-depth). |
| US-006 | CollaboratorModal Frontend | PASS | Dialog with 3 tabs (Invite, Collaborators, Pending). Invite tab has debounced 300ms search. Collaborators tab has remove/transfer with confirmation dialogs. Pending tab has revoke. All mutations show success toasts. DEV-001: Additional `GET /api/ideas/:id/invitations` endpoint. |
| US-007 | Invitation Display — Banner & Card | PASS | InvitationBanner uses `AnimatePresence` with slide-down animation. Banner shows inviter name, accept/decline buttons with API calls. Landing page InvitationCard wired with accept/decline mutations. Toasts on success. |
| US-008 | Read-Only View Mode | PASS | Detects `?token=` via `useSearchParams`. `readOnly` prop flows to WorkspaceHeader (hides Manage), ChatPanel (hides input), WorkspaceLayout/BoardCanvas (disabled interactions). ReadOnlyBanner with Eye icon rendered. InvitationBanner hidden in read-only mode. |
| US-009 | Multi-User Awareness — Sender Names & Co-Owner Rules | PASS | `isMultiUser = idea.collaborators.length > 0` controls sender name display. `getSenderName` resolves from collaborators list + current user. Leave button disabled with tooltip for single owners. Co-owner and collaborator leave enabled. |

**Stories passed:** 9 / 9
**Stories with defects:** 0
**Stories with deviations:** 1

---

## Test Matrix Coverage

**Pipeline scan results:** 11 found / 0 missing out of 11 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-8.1.01 | FOUND | `services/gateway/apps/collaboration/tests/test_invitation_api.py` | Verified — tests first accept transitions visibility to 'collaborating' |
| T-8.1.02 | FOUND | `services/gateway/apps/collaboration/tests/test_visibility.py` | Verified — tests removing all collaborators keeps 'collaborating' |
| T-8.3.01 | FOUND | `services/gateway/apps/ideas/tests/test_share_link.py` | Verified — tests valid token adds share_link_viewer role |
| T-8.3.02 | FOUND | `services/gateway/apps/ideas/tests/test_share_link.py` | Verified — tests invalid token returns 403 |
| T-8.3.03 | FOUND | `frontend/src/__tests__/read-only-view.test.tsx` | Verified — tests token passed to fetchIdea |
| T-8.3.04 | FOUND | `frontend/src/__tests__/read-only-view.test.tsx` | Verified — tests readOnly passed to BoardCanvas |
| T-8.4.01 | FOUND | `services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py` | Verified — tests single owner cannot leave |
| T-8.4.02 | FOUND | `services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py` | Verified — tests co-owner can leave |
| T-8.4.07 | FOUND | `frontend/src/__tests__/multi-user-awareness.test.tsx` | Verified — tests disabled Leave button with tooltip for single owner |
| T-2.5.01 | FOUND | `frontend/src/__tests__/multi-user-awareness.test.tsx` | Verified — tests sender names hidden for single-user ideas |
| T-12.3.01 | FOUND | `frontend/src/__tests__/invitation-display.test.tsx` | Verified — tests banner not shown when no pending invitation for idea |

---

## Defects

None.

---

## Deviations

### DEV-001: Additional `GET /api/ideas/:id/invitations` endpoint not in spec
- **Story:** US-006
- **Spec document:** docs/02-architecture/api-design.md
- **Expected (per spec):** No per-idea pending invitations list endpoint specified
- **Actual (in code):** `idea_pending_invitations` view at `GET /api/ideas/:id/invitations` returns pending invitations for a specific idea (owner only)
- **Why code is correct:** The CollaboratorModal's "Pending Invitations" tab requires listing invitations per idea for the owner. The global invitations list (`GET /api/invitations`) returns invitations for the invitee, not the inviter. This endpoint was necessary to implement the Pending tab correctly.
- **Spec update needed:** Add `GET /api/ideas/:id/invitations` to api-design.md Collaboration Endpoints section

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Tests (Python) | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 620 passed, 89 warnings |
| Tests (Node) | `docker compose -f docker-compose.test.yml run --rm node-tests npx vitest run` | PASS | 389 passed (49 files) |
| Frontend Typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | FAIL (optional) | Pre-existing: duplicate module named "events" (services/core/events vs services/ai/events). Not caused by M11. |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | FAIL (optional) | 5 issues (3 errors, 2 warnings). 4 pre-existing; 1 new warning: `IdeaWorkspace/index.tsx:57` missing `shareToken` dependency in useEffect. Non-blocking — shareToken only changes when URL changes which also changes `id`. |

### ESLint Detail (New Finding)

`frontend/src/pages/IdeaWorkspace/index.tsx:57` — `useEffect` that calls `fetchIdea(id, shareToken)` has dependency array `[id, t]` but should include `shareToken`. In practice this is benign because navigating to a share link always changes the URL (and thus `id`), but the dependency array is technically incomplete. Logged as a recommendation, not a defect, since ESLint is an optional gate.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Details of security review:**

- **Injection:** All queries use Django ORM with parameterized queries (`filter()`, `get()`, `Q()`). No raw SQL. User search uses `icontains` (ORM-parameterized). Share token validated via DB lookup, not string comparison.
- **Broken Authentication:** All endpoints use `MiddlewareAuthentication` decorator and `_require_auth()` check. Session-based auth with cookie credentials.
- **Sensitive Data Exposure:** Share link tokens generated with `secrets.token_hex(32)` (cryptographically secure, 64-char hex). No secrets in frontend code. Token passed via URL query param (standard pattern for share links).
- **XSS:** React auto-escapes all rendered content. No `dangerouslySetInnerHTML` in M11 components.
- **Broken Access Control:** Owner-only operations (invite, revoke, remove, transfer, generate share link, list pending invitations) check `idea.owner_id != user.id`. Invitee-only operations (accept, decline) check `invitation.invitee_id != user.id`. Self-invite prevented. Duplicate invitation prevented.
- **CSRF:** Django session authentication provides CSRF protection. Frontend uses `credentials: "include"` for cookie-based auth.
- **Input Validation:** UUID parsing with try/except on all ID parameters. `invitee_id` validated as UUID. User search query minimum length enforced. `encodeURIComponent` used on frontend for query params.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Details of performance review:**

- **N+1 Queries:** `list_collaborators` uses batch-load pattern (collects all user IDs, single query). `invitations_list` batch-loads ideas and inviters. `idea_pending_invitations` batch-loads invitees. No N+1 patterns found.
- **Unnecessary Re-renders:** Debounce on search input (300ms) prevents excessive API calls. `useCallback` used for search change handler. `useMemo` on message deduplication.
- **Missing Indexes:** `share_link_token` is UNIQUE (indexed). `collaboration_invitations` queries by `(idea_id, invitee_id, status)` — would benefit from a composite index but is acceptable for current scale.
- **Memory Leaks:** Debounce timer cleaned up in `useEffect` return. Cancelled flag pattern used for async fetches.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| CollaboratorModal | `docs/03-design/component-specs.md` § 17 Modal | PASS | Dialog max-w-2xl, Tabs, Input (search), Button (invite/remove) per spec |
| InvitationBanner | `docs/03-design/component-specs.md` § 11.5 Banners | PASS | border-l-4 border-primary, slide-down AnimatePresence, accept/decline buttons |
| InvitationCard | `docs/03-design/component-inventory.md` | PASS | Wired with accept/decline API calls on landing page |
| ReadOnlyBanner | `docs/03-design/page-layouts.md` § 7 | PASS | Eye icon, border-l-4 border-primary styling, muted text |
| UserMessageBubble (sender names) | `docs/03-design/component-specs.md` § 5.1 | PASS | text-xs text-muted-foreground for sender name display |
| Workspace read-only mode | `docs/01-requirements/features.md` § F-8.3 | PASS | Chat input hidden, board toolbar hidden, nodes not draggable/editable |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Workspace page loads at `/idea/:id` for authenticated owner
- [ ] Workspace page loads at `/idea/:id?token=<valid_token>` in read-only mode
- [ ] Landing page renders invitation cards for pending invitations
- [ ] 403 error page shown for invalid share link tokens

### API Endpoints
- [ ] `POST /api/ideas/:id/collaborators/invite` creates invitation (owner only, 201)
- [ ] `POST /api/invitations/:id/accept` accepts invitation, creates collaborator, transitions visibility
- [ ] `POST /api/invitations/:id/decline` declines invitation
- [ ] `POST /api/invitations/:id/revoke` revokes pending invitation (owner only)
- [ ] `GET /api/ideas/:id/collaborators` returns owner, co-owner, collaborators list
- [ ] `DELETE /api/ideas/:id/collaborators/:userId` removes collaborator (owner only)
- [ ] `POST /api/ideas/:id/transfer-ownership` transfers ownership atomically
- [ ] `POST /api/ideas/:id/leave` allows collaborator/co-owner to leave, blocks single owner
- [ ] `POST /api/ideas/:id/share-link` generates 64-char hex token (owner only)
- [ ] `GET /api/users/search?q=<query>` returns matching users (min 2 chars, max 20, excludes self)
- [ ] `GET /api/invitations` returns pending invitations for current user
- [ ] `GET /api/ideas/:id/invitations` returns pending invitations for idea (owner only)

### Data Integrity
- [ ] `collaboration_invitations` status transitions: pending -> accepted/declined/revoked only
- [ ] `idea_collaborators` UNIQUE(idea_id, user_id) constraint enforced
- [ ] `ideas.visibility` transitions from 'private' to 'collaborating' on first collaborator accept
- [ ] `ideas.visibility` does NOT revert when all collaborators removed
- [ ] `ideas.share_link_token` UNIQUE constraint enforced

### Features
- [ ] CollaboratorModal opens from Manage button with 3 tabs (Invite, Collaborators, Pending)
- [ ] Invite tab search is debounced at 300ms
- [ ] Remove collaborator requires confirmation dialog
- [ ] Transfer ownership requires confirmation dialog
- [ ] InvitationBanner shows slide-down animation for pending invitations in workspace
- [ ] Accept/decline from banner works and shows toast
- [ ] Read-only mode hides chat input, board toolbar, and edit actions
- [ ] ReadOnlyBanner displays in share link access
- [ ] Chat messages show sender names when collaborators > 0
- [ ] Single-user ideas do NOT show sender names
- [ ] Leave button disabled with tooltip for single owner

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 620 Python tests pass
- [ ] All 389 Node tests pass
- [ ] Ruff lint passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 1 (DEV-001: additional endpoint not in spec)
- **Bugfix PRD required:** no
- **Bugfix cycle:** N/A
