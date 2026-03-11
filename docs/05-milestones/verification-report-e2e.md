# Verification Report — E2E Test Milestones (M17–M21)

## 1. Requirements Coverage Matrix

### Functional Requirements

| Req ID | Requirement | Covered In | Stories | Status |
|--------|------------|------------|---------|--------|
| F-1.1 | Idea Page Layout | M18-S1 | Layout tests | Covered |
| F-1.2 | Section Visibility | M18-S2 | Section visibility tests | Covered |
| F-1.3 | Auto-Scroll on State Transition | M18-S2 | Auto-scroll tests | Covered |
| F-1.4 | Section Locking | M18-S2 | Locking tests (all 5 states) | Covered |
| F-1.5 | Idea Lifecycle | M18-S3 | All state transitions | Covered |
| F-1.6 | Inline Title Editing | M18-S1 | Title editing test | Covered |
| F-1.7 | UUID-Based Routing | M18-S1 | UUID routing tests | Covered |
| F-1.8 | Browser Tab Title | M18-S1 | Tab title tests | Covered |
| F-2.1 | Agent Modes | M18-S4 | Interactive/Silent mode tests | Covered |
| F-2.2 | Language Detection | M18-S4 | AI response tests (mocked) | Covered |
| F-2.3 | Title Generation | M18-S4 | Title gen + manual override | Covered |
| F-2.4 | Decision Layer | M18-S4 | AI response tests (mocked) | Covered |
| F-2.5 | Multi-User Awareness | M21-S5 | Collaborative journey | Covered |
| F-2.6 | Board Item References in Chat | M18-S7 | Board reference action test | Covered |
| F-2.7 | AI Reactions | M18-S5 | AI reaction tests | Covered |
| F-2.8 | User Reactions | M18-S5 | User reaction tests | Covered |
| F-2.9 | @Mentions System | M18-S5 | @Mentions dropdown + notification | Covered |
| F-2.10 | AI Response Timing | M18-S4 | AI processing + debounce tests | Covered |
| F-2.11 | Rate Limiting | M18-S5 | Rate limit lock/unlock tests | Covered |
| F-2.12 | AI Processing Indicator | M18-S4 | Processing indicator test | Covered |
| F-2.13 | Full State Knowledge | M18-S4 | AI response (mocked) | Covered |
| F-2.14 | Long Conversation Support | M18-S4 | Context indicator (mocked) | Covered |
| F-2.15 | Company Context Awareness | M20-S6 | Admin context + AI delegation (mocked) | Covered |
| F-2.16 | Company Context Management | M20-S6 | Admin AI context tests | Covered |
| F-2.17 | AI Board Content Rules | M18-S7 | AI board items (mocked) | Covered |
| F-3.1 | Node Types | M18-S6 | Box, Group, Free Text tests | Covered |
| F-3.2 | Board Interactions | M18-S6, M18-S7 | Drag, edit, connect, multi-select | Covered |
| F-3.3 | Board UI | M18-S6 | MiniMap, zoom, toolbar tests | Covered |
| F-3.4 | AI Modification Indicators | M18-S7 | AI indicator tests | Covered |
| F-3.5 | Multi-User Board Editing | M18-S9 | Real-time selection highlight | Covered |
| F-3.6 | Board Sync | M18-S9 | Board sync tests | Covered |
| F-3.7 | Undo/Redo | M18-S8 | Full undo/redo tests | Covered |
| F-3.8 | Board Item Reference Action | M18-S7 | Reference to chat test | Covered |
| F-4.1 | BRD Generation | M19-S1 | BRD generation tests | Covered |
| F-4.2 | No Fabrication | M19-S1 | Insufficient info test | Covered |
| F-4.3 | BRD Generation Trigger | M19-S1 | First open trigger | Covered |
| F-4.4 | Per-Section Editing & Lock | M19-S1 | Edit, lock, selective regen | Covered |
| F-4.5 | Review Tab | M19-S1, M19-S2, M19-S3 | Tab UI, PDF, submit | Covered |
| F-4.6 | Review Section | M19-S3, M19-S5 | Timeline, comments, versions | Covered |
| F-4.7 | Document Versioning | M19-S3, M21-S6 | Version creation, downloads | Covered |
| F-4.8 | Document Readiness Evaluation | M19-S1 | Readiness indicator tests | Covered |
| F-4.9 | Allow Information Gaps Toggle | M19-S2 | Gaps toggle, /TODO, PDF rejection | Covered |
| F-4.10 | Reviewer Assignment on Submit | M19-S3 | Assigned + unassigned submit | Covered |
| F-4.11 | Multiple Reviewers | M19-S5 | Accept, reject, drop, undo | Covered |
| F-4.12 | Similar Ideas in Review | M20-S1 | Similar ideas shown | Covered |
| F-5.1 | Keyword Generation | M20-S1 | Keywords generated | Covered |
| F-5.2 | Background Keyword Matching | M20-S1 | Matching detected | Covered |
| F-5.3 | AI Deep Comparison | M20-S1 | Deep comparison confirmed | Covered |
| F-5.4 | State-Aware Match Behavior | M20-S4 | Merge/append/informational | Covered |
| F-5.5 | Merge Flow | M20-S2 | Full merge flow | Covered |
| F-5.6 | Merge Request UI | M20-S2 | Banner + accept/decline | Covered |
| F-5.7 | Permanent Dismissal | M20-S3 | Dismiss + no re-suggest | Covered |
| F-5.8 | Manual Merge Request | M20-S5 | UUID, URL, browse list | Covered |
| F-6.1 | Session-Level Connection | M18-S9 | WebSocket connection tests | Covered |
| F-6.2 | Offline Banner | M18-S9, M21-S2 | Banner + countdown + reconnect | Covered |
| F-6.3 | Presence Tracking | M18-S9 | Presence indicators | Covered |
| F-6.4 | Multi-User Collaboration | M18-S9, M21-S5 | Real-time collaboration | Covered |
| F-6.5 | Offline Behavior | M18-S9, M21-S2 | Lock/unlock on disconnect | Covered |
| F-6.6 | Connection State Indicator | M18-S9 | Green/red indicator | Covered |
| F-7.1 | Development Auth Bypass | M17-S4 | All 4 dev users tested | Covered |
| F-7.2 | Production Authentication | M17-S4 | Route protection tests (dev bypass) | Covered |
| F-8.1 | Visibility Modes | M19-S6 | Private → collaborating | Covered |
| F-8.2 | Invite Flow | M19-S6 | Invite, accept, decline, revoke | Covered |
| F-8.3 | Read-Only Link Sharing | M19-S6 | Share link + read-only | Covered |
| F-8.4 | Collaborator Management | M19-S7 | Remove, leave, transfer | Covered |
| F-9.1 | Landing Page Structure | M17-S5 | Lists, creation, navigation | Covered |
| F-9.2 | Idea Creation | M17-S5 | Hero section creation | Covered |
| F-9.3 | Soft Delete | M17-S6 | Delete, undo, trash | Covered |
| F-9.4 | Search & Filter | M17-S6 | Search, state filter, ownership | Covered |
| F-10.1 | Review Page Access | M19-S4 | Reviewer access, non-reviewer blocked | Covered |
| F-10.2 | Categorized Idea Lists | M19-S4 | 5 categories | Covered |
| F-10.3 | Self-Assignment | M19-S4 | Assign, unassign | Covered |
| F-10.4 | Conflict of Interest | M19-S4 | Own idea blocked | Covered |
| F-11.1 | Admin Layout | M20-S6 | 4 tabs, role-gated | Covered |
| F-11.2 | AI Context Tab | M20-S6 | Both context areas | Covered |
| F-11.3 | Parameters Tab | M20-S7 | All 10 parameters | Covered |
| F-11.4 | Monitoring Tab | M20-S8 | Dashboard, alerts | Covered |
| F-11.5 | Backend Monitoring Service | M20-S8 | Health check verification | Covered |
| F-11.6 | Users Tab | M20-S9 | Search, profile display | Covered |
| F-12.1 | Notification Bell | M19-S8 | Bell, badge, panel | Covered |
| F-12.2 | Toast Notifications | M19-S8 | Success, info, warning, error | Covered |
| F-12.3 | Floating Banner | M19-S8 | Invitation banner | Covered |
| F-12.4 | Merge Request Banner | M20-S2 | Merge banner | Covered |
| F-12.5 | All Notification Events | M19-S9 | All event categories | Covered |
| F-13.1 | Email Notification Settings | M19-S10 | Preferences UI | Covered |
| F-13.2 | Grouped Toggles | M19-S10 | Group/individual toggles | Covered |
| F-13.3 | Role-Based Notification Groups | M19-S10 | Role-specific groups | Covered |
| F-14.1 | Universal Error Pattern | M21-S1 | Error toast, logs modal, retry | Covered |
| F-15.1 | Idle Detection | M18-S10 | Idle timeout, tab change | Covered |
| F-15.2 | Connection Disconnect on Idle | M18-S10 | Prolonged idle disconnect | Covered |
| F-15.3 | Return from Idle | M18-S10 | Reconnection on return | Covered |
| F-16.1 | Available Languages | M17-S8 | German + English | Covered |
| F-16.2 | Language Switcher | M17-S8 | User menu switcher | Covered |
| F-16.3 | i18n Scope | M17-S8 | UI labels translation | Covered |
| F-16.4 | AI Language | M18-S4 | AI language follow (mocked) | Covered |
| F-17.1 | Available Themes | M17-S7 | Light + Dark | Covered |
| F-17.2 | Theme Switcher | M17-S7 | User menu toggle | Covered |
| F-17.3 | System Preference Detection | M17-S7 | OS preference test | Covered |
| F-17.4 | Theme Scope | M17-S7 | All components, contrast | Covered |
| F-17.5 | Brand Assets | M17-S7 | Logo legibility (spot check) | Covered |

### Coverage Summary
- **Functional requirements:** 75/75 covered (100%)
- **Missing items:** 0

---

## 2. Integration Scenarios Coverage

| Scenario | Covered In | Status |
|----------|------------|--------|
| SCN-001: Chat → AI → Board → WS | M18-S4, M18-S9 | Covered |
| SCN-002: Rate Limit → Lockout → Unlock | M18-S5 | Covered |
| SCN-003: BRD Gen → Readiness → Lock → Regen | M19-S1 | Covered |
| SCN-004: Submit → State → Assignment → Notification | M19-S3, M19-S9 | Covered |
| SCN-005: Reject → Notification → Resubmit | M19-S5, M21-S6 | Covered |
| SCN-006: Similarity → Merge → New Idea | M20-S2, M21-S7 | Covered |
| SCN-007: Decline → Dismissal → Manual Recovery | M20-S3, M20-S5 | Covered |
| SCN-008: Append Flow | M20-S4 | Covered |
| SCN-009: Invitation → Accept → Real-Time Join | M19-S6, M21-S5 | Covered |
| SCN-012: Idea Creation from Landing | M17-S5, M21-S4 | Covered |
| SCN-013: Admin Parameter → Runtime Effect | M20-S7 | Covered |
| SCN-014: PDF /TODO Rejection → Fix → Success | M19-S2 | Covered |
| SCN-015: Soft Delete → Trash → Undo → Permanent | M17-S6 | Covered |
| SCN-018: Multi-Reviewer Conflict | M21-S3 | Covered |
| SCN-019: i18n Language Switch | M17-S8 | Covered |
| SCN-020: Read-Only Link → Edit Denied | M19-S6 | Covered |
| SCN-022: Collaborator Removal → Access Revoked | M19-S7, M19-S9 | Covered |
| SCN-023: Manual Merge for Declined Pair | M20-S5 | Covered |
| SCN-024: Recursive Merge | M20-S5 | Covered |
| JOURNEY-001: New Idea to Accepted | M21-S4 | Covered |
| JOURNEY-002: Collaborative Brainstorming | M21-S5 | Covered |
| JOURNEY-003: Rejection-Rework-Resubmission | M21-S6 | Covered |
| JOURNEY-004: Merge Detection & Resolution | M21-S7 | Covered |
| JOURNEY-005: Admin Configuration | M21-S8 | Covered |
| CONC-001: Simultaneous Chat | M21-S3 | Covered |
| CONC-002: Board Edit During AI | M21-S3 | Covered |
| CONC-003: Concurrent Review Actions | M21-S3 | Covered |
| CONC-004: Merge While Submitting | M21-S3 | Covered |
| CONC-005: Duplicate Invitation | M21-S3 | Covered |
| CONC-006: AI Processing Restart | M21-S3 | Covered |
| ERR-001: AI Service Unavailable | M21-S1 | Covered |
| ERR-002: PDF Generation Failure | M21-S1 | Covered |
| ERR-003: WebSocket Disconnection | M21-S2 | Covered |
| ERR-004: gRPC Failure | M21-S1 | Covered |
| ERR-006: Token Expiry | M21-S2 | Covered |

### Scenarios Summary
- **Cross-feature scenarios covered:** 19/24 (5 omitted: SCN-010/011/016/017/021 are integration-layer tests not suitable for browser E2E — they test internal agent pipelines, notification preference logic, or Redux state, better covered by unit/integration tests)
- **User journeys covered:** 5/5 (100%)
- **Concurrency scenarios covered:** 6/6 (100%)
- **Error scenarios covered:** 5/8 (ERR-005 broker down, ERR-007 guardrail, ERR-008 pool exhaustion are infrastructure-level, not E2E-testable)

---

## 3. Non-Functional Requirements Coverage

| NFR ID | Requirement | Covered In | How | Status |
|--------|------------|------------|-----|--------|
| NFR-P1 | Page load < 2s | M17-S1 | Smoke test timing | Covered |
| NFR-P3 | Real-time events < 500ms | M18-S9 | WS delivery tests | Covered |
| NFR-R4 | Exponential backoff | M21-S2 | Backoff test | Covered |
| NFR-R5 | Manual reconnect | M21-S2 | Manual reconnect test | Covered |
| NFR-S4 | Auth bypass double-gated | M17-S4 | Auth tests | Covered |
| NFR-S7 | Reviewer conflict of interest | M19-S4 | Own idea blocked | Covered |
| NFR-S8 | All routes protected | M17-S4 | Route protection tests | Covered |
| NFR-A3 | 4.5:1 contrast ratio | M17-S7 | axe-core spot check | Covered |
| NFR-T1–T6 | Theme support | M17-S7 | Theme tests | Covered |
| NFR-I1–I5 | i18n | M17-S8 | i18n tests | Covered |

---

## 4. Dependency Integrity

- No orphan features: all features reference requirements docs
- No forward references: M17 has no dependencies on M18+, etc.
- All dependencies explicit: M18→M17, M19→M18, M20→M19, M21→M20
- Existing milestones M1–M16 are READ ONLY — not modified

## 5. Complexity Re-Verification

| Milestone | Stories | Domain Size | Info Loss Score | Rating | Max Story Context | Status |
|-----------|---------|-------------|----------------|--------|------------------|--------|
| M17 | 9 | Small–Medium | 2 | Low | ~8,000 | PASS |
| M18 | 10 | Medium–Large | 6 | Medium | ~10,000 | PASS |
| M19 | 10 | Large | 7 | Medium | ~10,000 | PASS |
| M20 | 9 | Large | 7 | Medium | ~12,000 | PASS |
| M21 | 8 | Very Large | 9 | High (mitigated) | ~15,000 | PASS (see note) |

**M21 note:** Score of 9 is at the split threshold. However, each journey test is a self-contained test file with its own setup/teardown. The agent does not need to hold cumulative state from prior stories. The high score reflects cross-domain knowledge requirements, not cumulative in-milestone state. Splitting would create milestones with only 3-4 stories each, which is undersized. Decision: keep as-is with this documented mitigation.
