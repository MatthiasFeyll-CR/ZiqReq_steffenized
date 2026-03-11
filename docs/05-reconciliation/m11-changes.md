# Milestone 11 Spec Reconciliation — Collaboration & Sharing

## Summary
- **Milestone:** M11 — Collaboration & Sharing
- **Date:** 2026-03-11
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 0
- **Applied (FEATURE DESIGN):** 1
- **Applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

None.

---

### FEATURE DESIGN (Applied & Flagged)

| # | Deviation | Document Updated | Change | Applied By |
|---|-----------|-----------------|--------|------------|
| 1 | DEV-001: Additional `GET /api/ideas/:id/invitations` endpoint | `docs/02-architecture/api-design.md` | Added new endpoint for listing pending invitations per idea (owner only) — required for CollaboratorModal Pending tab | Spec Reconciler |

#### ⚠️ DEV-001: Additional `GET /api/ideas/:id/invitations` endpoint

**Story:** US-006 (CollaboratorModal Frontend)

**Source:**
- QA report: `docs/08-qa/qa-m11-collaboration.md` (line 65-71)
- Progress file: `.ralph/archive/m11-collaboration/progress.txt` (line 104)

**What the spec said:**
No per-idea pending invitations list endpoint specified in `docs/02-architecture/api-design.md`

**What was actually implemented:**
```
GET /api/ideas/:id/invitations
```
Returns pending invitations for a specific idea (owner only)

**Why it changed:**
The CollaboratorModal's "Pending Invitations" tab requires listing invitations per idea for the owner. The global invitations list (`GET /api/invitations`) returns invitations *to* the invitee (for landing page display), not invitations *from* the owner. This endpoint was necessary to implement the Pending tab correctly.

**Implementation details:**
- **File:** `services/gateway/apps/collaboration/views.py`
- **View function:** `idea_pending_invitations`
- **URL pattern:** `/api/ideas/:id/invitations`
- **Auth:** Owner only (checks `idea.owner_id == user.id`)
- **Response schema:**
  ```json
  {
    "invitations": [
      {
        "id": "uuid",
        "invitee_id": "uuid",
        "invitee_display_name": "string",
        "created_at": "iso8601",
        "status": "pending"
      }
    ]
  }
  ```

**Spec update applied:**
Added endpoint to `docs/02-architecture/api-design.md` Collaboration section (after line 910, following `DELETE /api/invitations/:id`)

**Diff:**
```diff
#### DELETE /api/invitations/:id
- **Purpose:** Revoke a pending invitation (owner action)
- **Auth:** Invitation inviter (idea owner)
- **Response (204):** No content

+#### GET /api/ideas/:id/invitations
+- **Purpose:** List pending invitations for a specific idea (for Pending Invitations tab in CollaboratorModal)
+- **Auth:** Owner only
+- **Response (200):**
+  ```json
+  {
+    "invitations": [
+      {
+        "id": "uuid",
+        "invitee_id": "uuid",
+        "invitee_display_name": "string",
+        "created_at": "iso8601",
+        "status": "pending"
+      }
+    ]
+  }
+  ```
+- **Notes:** Added in M11 (US-006). Complements `GET /api/invitations` which returns invitations *to* the current user. This endpoint returns invitations *from* the owner for a specific idea.
+
---
```

---

### LARGE TECHNICAL (Applied & Flagged)

None.

---

## Changes NOT Applied

### REJECTED

None.

---

## Documents Modified

1. **`docs/02-architecture/api-design.md`** — Added `GET /api/ideas/:id/invitations` endpoint to Collaboration section

---

## Impact on Future Milestones

**No breaking impact.** The added endpoint is specific to M11's collaboration features and is already fully implemented and tested. Future milestones may use this endpoint if they need to display pending invitations per idea.

---

## Implementation Learnings (from progress.txt)

Key patterns discovered during M11 implementation:

### 1. Endpoint Organization Pattern
Collaboration endpoints are split between ideas URLs and collaboration URLs:
- **Per-idea actions** → `/api/ideas/:id/collaborators/*` (invite, list collaborators, remove, transfer, leave)
- **Per-user actions** → `/api/invitations/*` (list my invitations, accept, decline, revoke)

### 2. Transaction Patterns
- **Accept invitation flow:** Uses `transaction.atomic()` to wrap invitation status update + collaborator create + visibility transition
- **Transfer ownership:** Uses `transaction.atomic()` to ensure atomicity

### 3. Auth Patterns
- `MiddlewareAuthentication` class from `apps.ideas.authentication` used consistently
- `_require_auth()` helper pattern for auth checks
- Dev bypass mode with `override_settings(DEBUG=True, AUTH_BYPASS=True)`

### 4. Co-owner Model
- Co-owners stored in `idea.co_owner_id` field (NOT in collaborators table)
- Co-owner leave sets `co_owner_id=NULL` directly
- Transfer ownership removes new owner from collaborators before setting as owner

### 5. Test Infrastructure
- Docker node-tests container copies files at **build time** → must rebuild with `docker compose -f docker-compose.test.yml build node-tests` after frontend changes
- QueryClientProvider + collaboration API mocks required for all tests rendering WorkspaceHeader
- React 19 requires explicit initial value for `useRef<T>(undefined)`

### 6. React Patterns
- TanStack Query v5 passes context object as second arg to mutationFn
- framer-motion AnimatePresence used for slide-down animations (causes benign `window.scrollTo` jsdom errors)
- TooltipProvider required wrapper for Radix tooltips
- Debounced search input at 300ms to prevent excessive API calls

### 7. Visibility Transitions
- New ideas default to `'private'`
- First accepted invitation transitions to `'collaborating'` (checked via collaborator count == 1)
- Removing all collaborators does NOT revert to private (no-revert behavior)

### 8. Data Loading Patterns
- Batch-load users pattern: collect all IDs (owner + co_owner + collaborators), single query, build map
- Prevents N+1 query problems

---

## Quality Baseline After M11

| Metric | Status | Details |
|--------|--------|---------|
| Python tests | ✅ PASS | 620 tests passed |
| Node tests | ✅ PASS | 389 tests passed (49 files) |
| Frontend typecheck | ✅ PASS | Clean (tsc --noEmit) |
| Backend lint (Ruff) | ✅ PASS | Clean |
| Test matrix coverage | ✅ COMPLETE | 11/11 test IDs implemented and verified |
| Security review | ✅ PASS | OWASP Top 10 review — no issues found |
| Performance review | ✅ PASS | No N+1 queries, debouncing in place |
| Design compliance | ✅ PASS | All components match specs |

**Optional gate checks:**
- Backend typecheck (mypy): FAIL (pre-existing: duplicate module "events")
- Frontend lint (ESLint): FAIL (1 new warning: missing `shareToken` in useEffect deps — benign)

---

## Regression Tests (to preserve in future milestones)

### Critical Endpoints
- ✅ `POST /api/ideas/:id/collaborators/invite` — Create invitation
- ✅ `POST /api/invitations/:id/accept` — Accept invitation, create collaborator, transition visibility
- ✅ `GET /api/ideas/:id/invitations` — List pending invitations per idea (owner only) **[NEW IN M11]**
- ✅ `GET /api/invitations` — List pending invitations for current user
- ✅ `GET /api/ideas/:id/collaborators` — List collaborators with roles
- ✅ `DELETE /api/ideas/:id/collaborators/:userId` — Remove collaborator
- ✅ `POST /api/ideas/:id/transfer-ownership` — Transfer ownership atomically
- ✅ `POST /api/ideas/:id/leave` — Leave idea (blocks single owner, allows co-owner)
- ✅ `POST /api/ideas/:id/share-link` — Generate share link token
- ✅ `GET /api/users/search?q=<query>` — Search users (min 2 chars, max 20 results)

### UI Components
- ✅ CollaboratorModal with 3 tabs (Invite, Collaborators, Pending)
- ✅ InvitationBanner with slide-down animation
- ✅ ReadOnlyBanner in share link mode
- ✅ Sender names in chat when collaborators > 0
- ✅ Leave button disabled with tooltip for single owner

### Data Integrity
- ✅ Visibility transitions: `private` → `collaborating` on first accept
- ✅ Visibility does NOT revert when all collaborators removed
- ✅ Single owner cannot leave (400 MUST_TRANSFER_OWNERSHIP)
- ✅ Co-owner can leave freely
- ✅ Share link tokens are 64-char hex (cryptographically secure)

---

## Reconciliation Complete

**Result:** ✅ COMPLETE

All deviations from M11 (Collaboration & Sharing) have been reviewed and applied to upstream documentation. The spec now accurately reflects the implemented state.

**Files modified:** 1
**Deviations catalogued:** 1
**Breaking changes:** 0
