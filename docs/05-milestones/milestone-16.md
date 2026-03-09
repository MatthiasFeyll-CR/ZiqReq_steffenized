# Milestone 16: Polish & Cross-Cutting

## Overview
- **Execution order:** 16 (runs after M10, M11, M12)
- **Estimated stories:** 10
- **Dependencies:** M10, M11, M12
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-7.2 | Production Authentication (MSAL.js) | P1 | features.md FA-7 |
| F-14.1 | Universal Error Pattern (full implementation) | P1 | features.md FA-14 |
| F-15.1 | Idle Detection | P1 | features.md FA-15 |
| F-15.2 | Connection Disconnect on Prolonged Idle | P1 | features.md FA-15 |
| F-15.3 | Return from Idle | P1 | features.md FA-15 |
| F-16.3 | i18n Scope (full coverage) | P1 | features.md FA-16 |
| F-1.3 | Auto-Scroll on State Transition (full) | P2 | features.md FA-1 |
| NFR-A1-A5 | Accessibility (keyboard nav, focus, contrast, screen reader, reduced motion) | P1 | nonfunctional.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| users | SELECT (Azure AD sync in production) | All columns | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/auth/validate | POST | Production: Azure AD token validation | Bearer JWT | api-design.md |

## Story Outline (Suggested Order)
1. **[Frontend]** Universal error pattern — error toast with "Show Logs" + "Retry" buttons, retry counter (max from admin param), disabled after max
2. **[Frontend]** Error log modal — centered modal with console log, network response, technical details, support contact
3. **[Backend + Frontend]** Idle detection — configurable timeout (mouse inactivity), tab visibility change triggers idle, presence update via WebSocket
4. **[Backend + Frontend]** Connection disconnect on prolonged idle — configurable idle duration before server closes connection, offline banner on disconnect
5. **[Frontend + Backend]** Return from idle — mouse movement ends idle, reconnection triggers, state syncs, presence returns to online
6. **[Frontend]** i18n completion — all remaining untranslated strings, notification email templates, timeline event text, system-generated messages
7. **[Frontend]** Accessibility pass — keyboard navigation for all interactive elements, visible focus indicators (gold ring), screen reader labels (aria-label, aria-describedby)
8. **[Frontend]** prefers-reduced-motion — all animations respect user preference (framer-motion, CSS animations), static alternatives
9. **[Frontend]** Auto-scroll on state transition — scroll to active section based on idea state (open->top, in_review->bottom, rejected->top, accepted/dropped->bottom)
10. **[Frontend + Backend]** Production auth — MSAL.js integration (@azure/msal-react), token validation middleware (Azure AD JWKS), silent token refresh, login redirect on failure

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Error pattern | ~5,000 | features.md (F-14.1), component-specs.md (S11.4) | 3-4 files | Medium | Retry state management |
| 2 | Error log modal | ~3,000 | component-specs.md (S17) | 2-3 files | Low | — |
| 3 | Idle detection | ~4,000 | features.md (F-15.1), api-design.md (WS) | 3-4 files | Medium | Mouse tracking, tab visibility |
| 4 | Idle disconnect | ~3,000 | features.md (F-15.2) | 2-3 files | Low | — |
| 5 | Return from idle | ~3,000 | features.md (F-15.3) | 2-3 files | Low | — |
| 6 | i18n completion | ~5,000 | features.md (F-16.3), all page layouts | 10-15 files | Medium | Many strings across entire app |
| 7 | Accessibility pass | ~5,000 | nonfunctional.md (NFR-A1-A5), all components | 15-25 files | Medium | Many components to audit |
| 8 | Reduced motion | ~3,000 | nonfunctional.md (NFR-A5) | 5-8 files | Low | — |
| 9 | Auto-scroll | ~2,000 | features.md (F-1.3) | 1-2 files | Low | — |
| 10 | Production auth | ~8,000 | tech-stack.md (Auth Flow), features.md (F-7.2) | 6-10 files | High | MSAL.js, JWKS validation |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~41,000
- **Cumulative domain size:** Medium (cross-cutting concerns touching all pages)
- **Information loss risk:** Medium (5) — touches many files but each change is small
- **Context saturation risk:** Low-Medium
- **Heavy stories:** 1 (production auth)

## Milestone Acceptance Criteria
- [ ] Error toast shows "Show Logs" and "Retry" buttons on any operation failure
- [ ] Error log modal displays technical details
- [ ] Retry disabled after max attempts with "Max retries reached" text
- [ ] User marked idle after configurable inactivity period
- [ ] Connection closed after prolonged idle
- [ ] Return from idle triggers reconnection and state sync
- [ ] All user-facing text translated to German and English
- [ ] All interactive elements keyboard-accessible with visible focus indicators
- [ ] All elements have appropriate screen reader labels
- [ ] Animations respect prefers-reduced-motion
- [ ] Auto-scroll navigates to correct section based on idea state
- [ ] Production auth: MSAL.js login, token refresh, validation middleware
- [ ] Auth bypass cannot activate when DEBUG=False (double-gate enforced)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M15

## Notes
- Production auth is the final piece before deployment. All development uses auth bypass.
- i18n completion requires reviewing every page and component for untranslated strings.
- Accessibility pass may reveal issues in previously built components — fixes are expected and acceptable.
- This milestone touches many files but each change is typically small (add aria-label, add translation key, etc.).
