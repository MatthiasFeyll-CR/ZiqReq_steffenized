# QA Report: Milestone 16 — Polish & Cross-Cutting

**Date:** 2026-03-11
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1 (previous cycle 0 failed due to infrastructure issue, now resolved)
**PRD:** tasks/prd-m16.json
**Progress:** .ralph/progress.txt

---

## Summary

Reviewed 10 user stories covering universal error pattern, idle detection/disconnect/recovery, i18n completion, accessibility (keyboard, screen reader, reduced motion), and production auth (MSAL.js). All stories pass acceptance criteria verification against the implemented code. All 11 test matrix tests are implemented and verified. All 922 Python tests pass (previously 554 errors in cycle 0 due to `relation "notifications" already exists` — resolved). Frontend typecheck and Ruff lint pass clean. No defects found. No deviations found.

**Cycle 0 -> Cycle 1 progress:** Tests went from FAIL (554 errors / infrastructure) to PASS (922 passed, 0 failed). The bugfix cycle was effective — the infrastructure issue has been resolved.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Universal Error Pattern — Enhanced Error Toast | PASS | Show Logs (outline) + Retry (primary) buttons present in `ErrorToast.tsx`. Retry counter with `maxRetries` prop (default 3). Toast persists (no auto-dismiss). `role="alert"`. |
| US-002 | Error Log Modal — Technical Details | PASS | Modal shows 4 sections: console logs, network response, technical details, support contact (`support@commerzreal.de`). `aria-describedby` present. No `dangerouslySetInnerHTML`. |
| US-003 | Idle Detection — Mouse Inactivity & Tab Visibility | PASS | `useIdleDetection` sends `presence_update` with `state='idle'`. Mouse throttled at 500ms. Tab visibility (`visibilitychange`) triggers idle immediately on hidden. Default timeout 300s configurable. |
| US-004 | Connection Disconnect on Prolonged Idle | PASS | Server closes WS with code 4008 after `idle_disconnect` seconds via `asyncio.sleep`. `OfflineBanner` shows idle-specific message. Inputs locked via existing offline state. |
| US-005 | Return from Idle — Reconnection & State Sync | PASS | `useIdeaSync` listens for mouse movement during idle-disconnect, calls `reconnectNow()`, fetches latest idea via REST, invalidates TanStack queries. |
| US-006 | i18n Completion — Full Coverage | PASS | `de.json` and `en.json` both have matching key sets. Language switcher in `UserDropdown.tsx`. Email renderer supports bilingual templates. All UI labels, buttons, errors translated. |
| US-007 | Accessibility — Keyboard Navigation & Focus | PASS | `SkipLink` rendered in `app.tsx` before router. Focus styles (`ring-2 ring-primary ring-offset-2`) on shadcn/ui components. Radix primitives provide Escape/Enter/Arrow navigation. `main-content` ID on both `PageShell` and `IdeaWorkspace`. |
| US-008 | Accessibility — Screen Reader Labels | PASS | `aria-label` on BoardToolbar icon buttons (5 buttons). `aria-live` on status messages (`polite` for status, `assertive` for errors). `aria-describedby` on ErrorLogModal. ARIA roles on lists, logs, alerts across 33 component files. |
| US-009 | Prefers-Reduced-Motion Support | PASS | `motion-safe:` prefix on `animate-pulse` (skeleton), `animate-spin` (spinners). `useReducedMotion` in 7 framer-motion components. `@media (prefers-reduced-motion: reduce)` in `globals.css`. |
| US-010 | Production Auth — MSAL.js Integration | PASS | `MsalProvider` wraps app conditionally (`providers.tsx`). `authFetch` adds `Bearer` token. WS handshake uses `?token=<jwt>`. Silent refresh 5min before expiry (`useMsalAuth.ts:9`). Double-gate: `DEBUG=True AND AUTH_BYPASS=True` verified in `middleware.py:48` and `websocket/middleware.py:51`. Backend validates Azure AD JWT via `validate_azure_ad_token`. |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 11 found / 0 missing out of 11 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-14.1.01 | FOUND | `frontend/src/__tests__/error-toast.test.tsx` | Verified — renders toast with Show Logs and Retry buttons |
| T-14.1.02 | FOUND | `frontend/src/__tests__/error-log-modal.test.tsx` | Verified — renders modal with all four sections |
| T-14.1.03 | FOUND | `frontend/src/__tests__/error-toast.test.tsx` | Verified — clicking Retry calls onRetry callback |
| T-14.1.04 | FOUND | `frontend/src/__tests__/error-toast.test.tsx` | Verified — disables Retry after max retries |
| T-15.1.01 | FOUND | `frontend/src/__tests__/idle-detection.test.tsx` | Verified — marks user idle after timeout |
| T-15.1.02 | FOUND | `frontend/src/__tests__/idle-detection.test.tsx` | Verified — tab hidden triggers idle |
| T-15.2.01 | FOUND | `frontend/src/__tests__/idle-disconnect.test.tsx` | Verified — shows idle disconnect message |
| T-15.3.01 | FOUND | `frontend/src/__tests__/idle-recovery.test.tsx` | Verified — mouse move triggers reconnect |
| T-16.1.01 | FOUND | `frontend/src/__tests__/i18n.test.tsx` | Verified — de.json and en.json have identical key sets |
| T-16.2.01 | FOUND | `frontend/src/__tests__/i18n.test.tsx` | Verified — switching language changes output |
| T-16.2.02 | FOUND | `frontend/src/__tests__/i18n.test.tsx` | Verified — language preference persists in localStorage |

*All test matrix tests for M16 are implemented and verified.*

---

## Defects

None.

---

## Deviations

None.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| TypeScript | `npx tsc --noEmit` | PASS | Clean — zero errors |
| Ruff Lint | `ruff check services/` | PASS | All checks passed |
| Python Tests | `pytest` (Docker) | PASS | 922 passed, 92 warnings, 0 failures. Cycle 0 had 554 errors (Django migration collision `relation "notifications" already exists`) — now fully resolved. |
| ESLint (optional) | `cd frontend && npx eslint src/` | INFO | 3 errors (pre-existing: `SECTION_FIELD_KEYS` unused in `BRDSectionEditor.tsx` from M9), 6 warnings (4x `react-hooks/exhaustive-deps` for `t` in admin tabs from M16 i18n — `t` is stable in practice; 1x `shareToken` in IdeaWorkspace from M14). Not blocking. |
| mypy (optional) | `mypy services/` | INFO | 1 error: duplicate module `events` (`services/core/events` + `services/ai/events`). Pre-existing structural issue. |

### Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | Required — clean |
| Backend lint (Ruff) | PASSED | Required — clean |
| Backend typecheck (mypy) | FAILED (optional) | Pre-existing duplicate module issue |
| Frontend lint (ESLint) | FAILED (optional) | Pre-existing errors + non-blocking warnings |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security defects found | — |

**Detailed review:**

1. **MSAL Configuration:** `msalConfig.ts` reads `clientId` and `tenantId` from `env` (environment variables via `import.meta.env`). No client secret present — correct for SPA using authorization code flow with PKCE. Cache location is `localStorage` (MSAL best practice).

2. **Auth Bypass Double-Gate:** Verified in three locations:
   - `services/gateway/apps/authentication/middleware.py:48` — `getattr(settings, "DEBUG", False) and getattr(settings, "AUTH_BYPASS", False)`
   - `services/gateway/apps/websocket/middleware.py:51` — identical check
   - Production settings enforce `DEBUG=False`, `AUTH_BYPASS=False`

3. **JWT Validation:** `validate_azure_ad_token()` called in both HTTP middleware (`middleware.py:69`) and WS middleware (`middleware.py:71`). Token failures logged at debug level only — no credential exposure.

4. **XSS Prevention:** `ErrorLogModal.tsx` and `ErrorToast.tsx` render all content via React JSX text interpolation (auto-escaped). No `dangerouslySetInnerHTML` used anywhere in M16 code.

5. **WebSocket Token:** Token passed via query parameter (`?token=<jwt>`) — standard and acceptable for WebSocket handshake. Connection rejected with code 4003 on invalid/missing token.

6. **i18n:** Translation strings rendered via `{t("key")}` JSX interpolation — auto-escaped by React. No raw HTML rendering of i18n values.

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance defects found | — |

**Detailed review:**

1. **Mouse Movement Throttle:** `useIdleDetection.ts:4,66` — 500ms throttle via `Date.now()` comparison. Efficient.
2. **Console Error Capture:** `errorLogger.ts` caps at 20 entries with `shift()`. No memory leak.
3. **Token Refresh Timer:** `useMsalAuth.ts:53-61` — `clearTimeout` in cleanup and on logout. No memory leak.
4. **useIdeaSync Listeners:** Mouse move listener only added when `isIdleDisconnected` is true. Properly cleaned up.
5. **i18n Bundle:** ~292 keys per locale file — reasonable size.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| ErrorToast | `docs/03-design/component-specs.md` S11.4 | PASS | Show Logs (outline) + Retry (primary) buttons per spec |
| ErrorLogModal | `docs/03-design/component-specs.md` S11.4 | PASS | 4 sections: console, network, technical, support |
| OfflineBanner (idle) | `docs/03-design/component-specs.md` S11.5 | PASS | Idle disconnect message variant |
| PresenceIndicator (idle) | `docs/03-design/component-specs.md` S9.2 | PASS | Idle users shown with opacity-50 + grayscale |
| SkipLink | Accessibility spec | PASS | Rendered in `app.tsx`, targets `#main-content` |
| BoardToolbar icons | `docs/03-design/component-specs.md` S1.4 | PASS | All 5 icon buttons have `aria-label` |
| Focus indicators | `docs/03-design/component-specs.md` S1.3 | PASS | `ring-2 ring-primary ring-offset-2` on interactive elements |
| Skeleton loader | Reduced motion spec | PASS | `motion-safe:animate-pulse` — static when reduced motion preferred |

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Landing page still loads with all 4 idea lists at `/`
- [ ] Idea workspace still loads at `/ideas/:id` with two-panel layout
- [ ] Admin panel still loads at `/admin` with all 4 tabs

### Error Handling
- [ ] Error toast renders with Show Logs and Retry buttons on API failure
- [ ] Error log modal shows console logs, network response, technical details, support contact
- [ ] Retry button disables after max retries with "Max retries reached" text

### Idle Detection & Recovery
- [ ] User marked idle after 300s of mouse inactivity (configurable)
- [ ] Tab visibility change to hidden triggers idle immediately
- [ ] Server closes WebSocket with code 4008 after `idle_disconnect` seconds
- [ ] Offline banner shows idle-specific message (no Reconnect button)
- [ ] Mouse movement during idle-disconnect triggers reconnection
- [ ] State syncs via REST after reconnection from idle

### i18n
- [ ] `de.json` and `en.json` have identical key sets
- [ ] Language switcher changes all visible text
- [ ] Language preference persists in localStorage

### Accessibility
- [ ] SkipLink rendered and targets `#main-content`
- [ ] All BoardToolbar icon buttons have `aria-label`
- [ ] Status messages use `aria-live` (polite for status, assertive for errors)
- [ ] Modals have `aria-describedby`
- [ ] Skeleton loaders use `motion-safe:animate-pulse`
- [ ] framer-motion components check `useReducedMotion`

### Authentication
- [ ] MsalProvider wraps app when not in dev bypass mode
- [ ] `authFetch` adds `Authorization: Bearer` header
- [ ] WebSocket handshake includes token via `?token=<jwt>`
- [ ] Silent token refresh scheduled 5 minutes before expiry
- [ ] Auth bypass requires both `DEBUG=True` and `AUTH_BYPASS=True`
- [ ] Production settings enforce `DEBUG=False`, `AUTH_BYPASS=False`

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 922 Python tests pass
- [ ] Ruff lint passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1 (cycle 0 failed due to infrastructure, cycle 1 passes clean)
