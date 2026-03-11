# Milestone 20: E2E Similarity, Merge & Admin Tests

## Overview
- **Execution order:** 20 (runs after M19)
- **Estimated stories:** 9
- **Dependencies:** M17 (test infra), M18 (workspace), M19 (review + notifications)
- **Type:** E2E Testing

## Purpose

Test the similarity detection and merge flows (automatic detection, merge consent, append flow, manual merge, permanent dismissal), and the complete admin panel (AI context management, parameters, monitoring dashboard, user lookup).

## Features Tested

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-5 | Idea Similarity Detection & Resolution | P1 | docs/01-requirements/features.md |
| FA-11 | Admin Panel | P1 | docs/01-requirements/features.md |

## Story Outline

### S1: E2E Similarity Detection & Notification (FA-5)
- **Test: Keywords generated during brainstorming (F-5.1)** — Create idea with enough chat context → verify keywords generated (via API or admin check)
- **Test: Background keyword matching (F-5.2)** — Create 2 ideas with overlapping context (mocked AI generates overlapping keywords) → matching service detects overlap
- **Test: AI deep comparison confirms similarity (F-5.3)** — After keyword match → deep comparison runs (mocked) → genuine similarity confirmed
- **Test: Both owners notified (F-5.4)** — Similarity detected → both owners receive in-app + email notifications
- **Test: Read-only access to other idea (F-5.5)** — After notification → each owner can view the other's idea in read-only mode
- **Test: Similar ideas shown in review section (F-4.12)** — When idea is in review → reviewer sees similar ideas listed

**Acceptance criteria:**
- [ ] Keyword generation works (mocked AI)
- [ ] Background matching detects overlaps above threshold
- [ ] Deep comparison confirms/rejects similarity
- [ ] Both owners notified and can view each other's ideas

### S2: E2E Merge Flow — Open + Open (FA-5)
- **Test: Request merge (F-5.5)** — Owner A requests merge with Owner B's idea → B's idea locked with merge banner
- **Test: Merge request banner (F-5.6)** — Owner B sees banner with accept/decline, idea locked until resolved
- **Test: Accept merge (F-5.5)** — Owner B accepts → new merged idea created
- **Test: Merged idea — co-owners (F-5.5)** — New idea has both original owners as co-owners
- **Test: Merged idea — AI synthesized context (F-5.5)** — First chat message is AI-synthesized summary of both ideas
- **Test: Merged idea — combined board (F-5.5)** — Board contains items from both original ideas (AI merged/deduplicated)
- **Test: Original ideas read-only (F-5.5)** — Original ideas accessible in read-only mode with reference to merged idea
- **Test: All collaborators transferred (F-5.5)** — Collaborators from both original ideas added to merged idea

**Acceptance criteria:**
- [ ] Merge request creates and displays correctly
- [ ] Accept produces valid merged idea with co-owners
- [ ] Original ideas become read-only with references
- [ ] All collaborators transferred

### S3: E2E Merge — Decline & Permanent Dismissal (FA-5)
- **Test: Decline merge (F-5.5, F-5.7)** — Owner B declines → merge request dismissed, idea unlocks, banner disappears
- **Test: Permanent dismissal (F-5.7)** — After decline → same pair never suggested again by automatic matching
- **Test: Can still manually merge after dismissal (F-5.8)** — Despite permanent dismissal, manual merge request still possible
- **Test: Requesting user continues brainstorming (F-5.5)** — While merge pending for B, A's idea is NOT locked — A continues working

**Acceptance criteria:**
- [ ] Decline works and unlocks target idea
- [ ] Permanent dismissal prevents re-suggestion
- [ ] Manual merge bypasses dismissal
- [ ] Non-target idea remains editable during pending merge

### S4: E2E Append Flow — Open + In Review (FA-5)
- **Test: State-aware match — in_review not mergeable (F-5.4)** — Open idea matched to in-review idea → append option (not merge)
- **Test: Request append (F-5.4)** — Open idea owner requests append to in-review idea
- **Test: Three-way consent required (F-5.4)** — Append requires: open idea owner (requester), in-review owner, and one reviewer
- **Test: All three accept → append completes (F-5.4)** — Open idea closed (read-only), owner becomes collaborator on in-review idea
- **Test: Any party declines → append cancelled** — One party declines → append request cancelled, both ideas unchanged
- **Test: Matched with accepted idea — informational only (F-5.4)** — Open idea matched to accepted idea → AI guidance shown (not actionable merge)
- **Test: Matched with dropped idea — informational only (F-5.4)** — Open idea matched to dropped idea → AI raises concerns

**Acceptance criteria:**
- [ ] Append flow works with three-way consent
- [ ] Open idea closes and owner transfers correctly
- [ ] Decline cancels the append
- [ ] Informational matches for accepted/dropped ideas

### S5: E2E Manual Merge & Edge Cases (FA-5)
- **Test: Manual merge by UUID (F-5.8)** — User enters other idea's UUID → merge request created
- **Test: Manual merge by URL (F-5.8)** — User enters full URL of other idea → resolved and merge request created
- **Test: Browse similar ideas list (F-5.8)** — Manual merge UI shows similar ideas with title and keywords for selection
- **Test: Recursive merge — merged idea merges again (SCN-024)** — Merged idea (co-owners A, B) merges with idea C → new idea with co-owners A+C, B demoted to collaborator
- **Test: Co-owner independence (user-roles)** — Either co-owner can independently submit, invite, or initiate merge

**Acceptance criteria:**
- [ ] Manual merge works via UUID and URL
- [ ] Similar ideas browsable for selection
- [ ] Recursive merge handles co-owner demotion correctly
- [ ] Co-owner independence respected

### S6: E2E Admin Panel — Layout & AI Context (FA-11)
- **Test: Admin panel access (F-11.1)** — Login as Admin (User4) → navbar shows Admin link → navigate to `/admin` → 4 tabs visible
- **Test: Non-admin cannot access (F-11.1)** — Login as User1 → navigate to `/admin` → blocked/redirected
- **Test: AI Context tab — Facilitator context (F-11.2)** — Edit facilitator context (free text table of contents) → saved
- **Test: AI Context tab — Detailed company context (F-11.2)** — Edit detailed company context (structured sections + free text) → saved
- **Test: Two areas clearly separated (F-11.2)** — Facilitator context and detailed context displayed as isolated, clearly separated areas
- **Test: Context update does not affect in-progress ideas (F-2.16)** — Update context → existing brainstorming session continues with old context until next AI processing cycle

**Acceptance criteria:**
- [ ] Admin panel accessible only to Admins
- [ ] AI context editing works for both areas
- [ ] Context areas clearly separated
- [ ] In-progress ideas not retroactively affected

### S7: E2E Admin Panel — Parameters (FA-11)
- **Test: Parameters tab displays all parameters (F-11.3)** — All 10 configurable parameters visible with current values and defaults
- **Test: Edit parameter value (F-11.3)** — Change "Chat message cap" from 5 to 3 → saved
- **Test: Parameter applies at runtime (F-11.3)** — Change chat message cap → immediately effective for active ideas (no restart)
- **Test: Runtime effect — debounce timer (SCN-013)** — Change debounce timer → next AI processing uses new value
- **Test: Reset to default** — Modified parameter → verify can reset to default value
- **Test: Each parameter listed** — Verify all parameters from spec exist: chat_message_cap, idle_timeout, idle_disconnect, max_reconnection_backoff, soft_delete_countdown, debounce_timer, default_app_language, max_keywords_per_idea, min_keyword_overlap, similarity_time_limit

**Acceptance criteria:**
- [ ] All parameters visible with correct defaults
- [ ] Parameter changes save and apply at runtime
- [ ] No service restart required for changes to take effect

### S8: E2E Admin Panel — Monitoring (FA-11)
- **Test: Monitoring tab — dashboard data (F-11.4)** — Dashboard shows: active connections count, ideas by state, active/online users count, AI processing stats, service health
- **Test: Service health status (F-11.4)** — All services show healthy status (since all are running in test)
- **Test: Alert configuration (F-11.4)** — Admin opts in to receive alerts → configuration saved
- **Test: Opt out of alerts (F-11.4)** — Admin opts out → no longer in alert recipient list
- **Test: Backend monitoring service (F-11.5)** — Verify monitoring health check runs periodically (check via API or log)

**Acceptance criteria:**
- [ ] Dashboard displays real-time monitoring data
- [ ] Service health shows correct status
- [ ] Alert configuration (opt in/out) works

### S9: E2E Admin Panel — Users (FA-11)
- **Test: Users tab — search (F-11.6)** — Search for a user by name → results display
- **Test: User not eager-loaded (F-11.6)** — Users tab initial state does not show any users (search required)
- **Test: User profile display (F-11.6)** — Search result shows: name, first name, email, assigned roles, idea count, review count, contribution count
- **Test: Search by different criteria** — Search by first name, by last name, by email → all work
- **Test: No results** — Search for non-existent user → appropriate empty state message

**Acceptance criteria:**
- [ ] User search works (not eager-loaded)
- [ ] User profile shows all required fields
- [ ] Empty state handled gracefully

## Execution Rule

**After implementing EACH story above:**
1. Run `npx playwright test --config=e2e/playwright.config.ts`
2. ALL tests must pass (including M17 + M18 + M19 tests)
3. If any test fails → identify root cause → fix test or production code → all green before continuing

## Per-Story Complexity Assessment

| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Similarity Detection | ~10,000 | F-5.1–F-5.3, F-4.12 | 1-2 | High | AI mock + background job |
| 2 | Merge Flow | ~12,000 | F-5.5, F-5.6 | 1-2 | High | Multi-user + AI synth |
| 3 | Decline & Dismissal | ~6,000 | F-5.7, F-5.8 | 1-2 | Medium | — |
| 4 | Append Flow | ~10,000 | F-5.4 | 1-2 | High | Three-way consent |
| 5 | Manual Merge & Edge Cases | ~8,000 | F-5.8, SCN-024 | 1-2 | High | Recursive merge |
| 6 | Admin — AI Context | ~6,000 | F-11.1, F-11.2, F-2.16 | 1-2 | Medium | — |
| 7 | Admin — Parameters | ~7,000 | F-11.3, SCN-013 | 1-2 | Medium | Runtime effect verify |
| 8 | Admin — Monitoring | ~6,000 | F-11.4, F-11.5 | 1-2 | Medium | Health check timing |
| 9 | Admin — Users | ~4,000 | F-11.6 | 1-2 | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~69,000
- **Cumulative domain size:** Large
- **Information loss risk:** Medium (score: 7)
- **Context saturation risk:** Medium

## Milestone Acceptance Criteria
- [ ] All similarity detection tests pass (keywords, matching, deep comparison)
- [ ] All merge flow tests pass (request, accept, decline, dismissal)
- [ ] Append flow tested with three-way consent
- [ ] Manual merge and recursive merge tested
- [ ] All admin panel tabs tested (AI context, parameters, monitoring, users)
- [ ] All M17 + M18 + M19 tests still pass (no regressions)
- [ ] Any production bugs discovered are fixed and documented

## Notes
- Similarity detection tests depend on AI mock mode generating keywords and deep comparison results
- Merge flow requires two user contexts and AI synthesis mock responses
- Append flow is the most complex — requires 3 distinct user roles (open owner, in-review owner, reviewer)
- Admin parameter runtime effect tests need to verify the parameter takes effect without service restart — use a short timeout and verify behavioral change
- Background matching job may need to be triggered manually in tests (via API or Celery task invocation)
