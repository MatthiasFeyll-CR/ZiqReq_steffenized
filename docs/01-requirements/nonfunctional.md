# Non-Functional Requirements

## Performance

- **NFR-P1:** Page load under 2 seconds during regular load.
- **NFR-P2:** AI chat responses under 10 seconds for typical interactions. Hard timeout configurable by Admin (default: 60 seconds) before failure.
- **NFR-P3:** Real-time events (chat messages, requirements sync) delivered to other users within 500ms.
- **NFR-P4:** Session-level connection — one connection per session, not per project. Reduces connection overhead.
- **NFR-P5:** Requirements sync uses real-time broadcast for awareness events (selections, locks) and commit-based broadcast for content/position changes. Reduces message volume.
- **NFR-P6:** AI processing is debounced — prevents unnecessary processing cycles on rapid input (default: 3 seconds, admin-configurable).
- **NFR-P7:** Connections closed after prolonged user inactivity (default: 120 seconds idle, admin-configurable) to reduce server load.
- **NFR-P8:** AI must handle long requirements structuring sessions without degrading in quality. Older chat context is summarized automatically to keep processing efficient.

> ⚙️ DOWNSTREAM → **AI Engineer**: Define concrete thresholds and mechanics for context management that satisfy NFR-P8. The old spec used a configurable compression threshold (default 60% of context window). See `docs_old/01-requirements/nonfunctional.md` NFR-P8.

## Reliability

- **NFR-R1:** Failed messages in the processing pipeline are captured for debugging, not silently lost.
- **NFR-R2:** All event consumers must be idempotent.
- **NFR-R3:** AI errors show user-facing error toast with retry option, not silent failures.
- **NFR-R4:** Automatic reconnection with exponential backoff (max 30 seconds, admin-configurable) for disconnects.
- **NFR-R5:** Manual reconnect button available during offline state for immediate retry.
- **NFR-R6:** On reconnection, latest state is fetched from server to ensure consistency.

> ⚙️ DOWNSTREAM → **Software Architect**: Design the reliability infrastructure — dead-letter queues, retry mechanics, idempotency strategy. The old spec specified DLQs on all message queues for debugging only (no automatic retry from DLQ). See `docs_old/01-requirements/nonfunctional.md` NFR-R1, NFR-R2.

## Security

- **NFR-S1:** Microsoft Azure OIDC/OAuth2 for all production authentication.
- **NFR-S2:** Token validation at API edge and real-time connection handshake.
- **NFR-S3:** Silent token refresh before expiry. If refresh fails, redirect to login.
- **NFR-S4:** Auth bypass double-gated (`AUTH_BYPASS=True` + `DEBUG=True`) — impossible to activate in production.
- **NFR-S5:** No secrets in code — all configuration via environment variables.
- **NFR-S6:** Read-only link sharing requires Azure AD authentication — no anonymous access.
- **NFR-S7:** Conflict of interest prevention — Reviewers cannot review their own projects.
- **NFR-S8:** All routes protected — unauthenticated users redirected to login.

## Accessibility

- **NFR-A1:** Keyboard-first navigation.
- **NFR-A2:** Visible focus indicators on all interactive elements.
- **NFR-A3:** 4.5:1 contrast ratio minimum.
- **NFR-A4:** Screen reader labels on all interactive elements.
- **NFR-A5:** `prefers-reduced-motion` support — all animations respect user preference.

> ⚙️ DOWNSTREAM → **UI/UX Designer**: Define the specific focus ring style, animation behaviors, and accessible color palette that satisfy these requirements. The old spec used `2px solid var(--color-primary)` with `3px` offset for focus rings. See `docs_old/01-requirements/nonfunctional.md` NFR-A2.

## Theming

- **NFR-T1:** The application supports two themes: **Light mode** (default) and **Dark mode**.
- **NFR-T2:** Theme switcher accessible from the user menu dropdown (alongside language switcher).
- **NFR-T3:** Theme preference persisted per user.
- **NFR-T4:** All UI components, pages, and visual elements must be fully functional and accessible in both themes.
- **NFR-T5:** Contrast ratios (NFR-A3) must be met in both light and dark mode.
- **NFR-T6:** The Commerz Real logo must remain legible in both themes (use appropriate logo variant or background treatment).

## Compatibility

- **Browsers:**
  - Primary: Microsoft Edge (latest 2 versions)
  - Secondary: Firefox (latest 2 versions)
- **Devices:**
  - Desktop: full functionality (primary target)
  - Tablet: full functionality supported
  - Mobile: supported with limitations — requirements panel is read-only on mobile, all other features functional
- **Responsive:** Yes — layout adapts to desktop, tablet, and mobile viewports.

## Internationalization

- **NFR-I1:** Available languages: German (default) and English.
- **NFR-I2:** Language switcher in user menu dropdown.
- **NFR-I3:** Language preference persisted per user.
- **NFR-I4:** Scope: all user-facing content — UI labels, buttons, navigation, notification emails, timeline events, system-generated text.
- **NFR-I5:** AI initial language follows the project creator's app language setting, then adapts to user's chat language.

## Data & Privacy

- **Regulations:** Internal tool — no GDPR data subject access requests expected (employees on corporate system).
- **Data retention:** Managed by infrastructure team via Azure. Not an application-level concern.
- **Data export:** Not required.
- **Data backup:** Handled by a separate development department directly in Azure. Not an application-level concern.

## Availability

- **Uptime target:** Best effort — no formal uptime guarantee. Acceptable for an internal requirements assembly tool.
- **Maintenance:** Can be performed at any time. No zero-downtime deployment requirement.
- **Monitoring:** Admin Panel provides lightweight monitoring dashboard and email alerts for system health issues.
