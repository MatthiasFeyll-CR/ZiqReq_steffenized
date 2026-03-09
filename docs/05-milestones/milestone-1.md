# Milestone 1: Foundation & Auth

## Overview
- **Execution order:** 1 (first milestone)
- **Estimated stories:** 10
- **Dependencies:** None
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-7.1 | Development Auth Bypass | P1 | features.md FA-7 |
| F-14.1 | Universal Error Pattern (partial — toast + modal shell) | P1 | features.md FA-14 |
| F-16.1-16.3 | i18n Scaffolding (German + English, switcher) | P1 | features.md FA-16 |
| F-17.1-17.5 | Theme System (light/dark, switcher, CSS variables) | P1 | features.md FA-17 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| users | CREATE TABLE + seed dev users | id, email, first_name, last_name, display_name, roles, email_notification_preferences | data-model.md |
| ideas | CREATE TABLE | All columns | data-model.md |
| idea_collaborators | CREATE TABLE | All columns | data-model.md |
| chat_messages | CREATE TABLE | All columns | data-model.md |
| ai_reactions | CREATE TABLE | All columns | data-model.md |
| user_reactions | CREATE TABLE | All columns | data-model.md |
| board_nodes | CREATE TABLE | All columns | data-model.md |
| board_connections | CREATE TABLE | All columns | data-model.md |
| brd_drafts | CREATE TABLE | All columns | data-model.md |
| brd_versions | CREATE TABLE | All columns | data-model.md |
| review_assignments | CREATE TABLE | All columns | data-model.md |
| review_timeline_entries | CREATE TABLE | All columns | data-model.md |
| collaboration_invitations | CREATE TABLE | All columns | data-model.md |
| notifications | CREATE TABLE | All columns | data-model.md |
| chat_context_summaries | CREATE TABLE | All columns | data-model.md |
| idea_keywords | CREATE TABLE | All columns | data-model.md |
| merge_requests | CREATE TABLE | All columns | data-model.md |
| facilitator_context_bucket | CREATE TABLE + seed empty row | All columns | data-model.md |
| context_agent_bucket | CREATE TABLE + seed empty row | All columns | data-model.md |
| admin_parameters | CREATE TABLE + seed all defaults | All columns | data-model.md |
| monitoring_alert_configs | CREATE TABLE | All columns | data-model.md |
| context_chunks | CREATE TABLE (pgvector) | All columns | data-model.md |
| idea_embeddings | CREATE TABLE (pgvector) | All columns | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/auth/validate | POST | Validate token, sync user to shadow table | Bearer JWT | api-design.md |
| /api/auth/dev-switch | POST | Switch dev user (bypass mode only) | Session | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Button (6 variants, 5 sizes) | UI Primitive | component-specs.md S1 |
| Card (base) | UI Primitive | component-specs.md S2 |
| Input, Textarea, Select | UI Primitive | component-specs.md S4 |
| Switch, Checkbox | UI Primitive | component-specs.md S4 |
| Badge (state, role) | UI Primitive | component-specs.md S3 |
| Avatar (4 sizes, initials fallback) | UI Primitive | component-specs.md S9 |
| Tooltip | UI Primitive | component-specs.md S16 |
| DropdownMenu | UI Primitive | component-specs.md S15 |
| Dialog (Modal) | UI Primitive | component-specs.md S17 |
| Tabs | UI Primitive | component-specs.md S7 |
| Skeleton | UI Primitive | component-specs.md S11.2 |
| Toast (react-toastify, 4 variants) | UI Primitive | component-specs.md S11.1 |
| Navbar | Layout | component-inventory.md |
| NavbarLink | Layout | component-inventory.md |
| UserDropdown | Layout | component-inventory.md |
| PageShell | Layout | component-inventory.md |
| AuthenticatedLayout | Layout | component-inventory.md |
| ConnectionIndicator (placeholder) | Layout | component-inventory.md |
| DevUserSwitcher | Feature (Auth) | component-inventory.md |
| ErrorBoundary | Common | component-inventory.md |
| EmptyState | Common | component-inventory.md |
| ErrorToast (shell) | Common | component-inventory.md |
| ErrorLogModal (shell) | Common | component-inventory.md |
| LoadingSpinner | Common | component-inventory.md |
| SkipLink | Common | component-inventory.md |

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives (16) | To be built | M1 |
| All Layout Components (8) | To be built | M1 |
| Common Components (6) | To be built | M1 |

## Story Outline (Suggested Order)
1. **[Schema/Migration]** All 22 table migrations + indexes + pgvector extension setup
2. **[Schema/Seed]** Seed data: admin parameters (application + infrastructure + AI), singleton buckets, dev users (conditional on DEBUG)
3. **[Backend Models — Gateway]** Django models for gateway-owned tables: users, notifications, monitoring_alert_configs
4. **[Backend Models — Core]** Django models for core-owned tables: ideas, chat_messages, board_nodes, and all related
5. **[Backend — Auth]** Auth bypass middleware, dev user session management, POST /api/auth/validate, POST /api/auth/dev-switch, user sync logic
6. **[Backend — gRPC]** Proto definitions for all gRPC services (gateway<->core, gateway<->ai, gateway<->pdf, gateway<->notification), code generation, stub implementations
7. **[Frontend — UI Primitives]** All 16 shadcn/ui components customized with design tokens (Button, Card, Input, Badge, Avatar, Tooltip, etc.)
8. **[Frontend — Layout]** Navbar (with role-gated links, user dropdown), PageShell, AuthenticatedLayout, DevUserSwitcher, ConnectionIndicator placeholder
9. **[Frontend — Theme + i18n]** CSS variable system (light/dark), theme toggle in UserDropdown, react-i18next setup with German + English translation files, language switcher
10. **[Frontend — Common]** ErrorBoundary, EmptyState, ErrorToast shell, ErrorLogModal shell, LoadingSpinner, SkipLink

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Schema migrations | ~8,000 | data-model.md (full) | 5-8 migration files | Medium | pgvector extension setup |
| 2 | Seed data | ~3,000 | data-model.md (seed tables) | 2-3 data migrations | Low | — |
| 3 | Gateway models | ~4,000 | data-model.md (3 tables) | 3-5 model files | Low | — |
| 4 | Core models | ~8,000 | data-model.md (14 tables) | 12-16 model files | Medium | Many FK relationships |
| 5 | Auth bypass | ~6,000 | api-design.md (auth), tech-stack.md (auth flow) | 5-8 files | Medium | Middleware chain correctness |
| 6 | gRPC protos | ~10,000 | api-design.md (all gRPC sections) | 8-12 proto + generated files | Medium | Cross-service contract alignment |
| 7 | UI Primitives | ~8,000 | component-specs.md, design-system.md | 16-20 component files | Medium | Many components but each is small |
| 8 | Layout | ~6,000 | component-specs.md (S8), page-layouts.md (navbar) | 8-12 files | Medium | Role-gated navigation logic |
| 9 | Theme + i18n | ~5,000 | design-system.md (colors), tech-stack.md (theming) | 6-10 files | Low | Well-documented patterns |
| 10 | Common components | ~3,000 | component-specs.md (S11, S17) | 6-8 files | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~61,000
- **Cumulative domain size:** Medium (schema + auth + UI components)
- **Information loss risk:** Low (3) — stories are independent domains
- **Context saturation risk:** Low — each story has a focused scope
- **Heavy stories:** 0 (story 6 is the heaviest but still within bounds)

## Milestone Acceptance Criteria
- [ ] All 22 tables created with correct columns, constraints, and indexes
- [ ] pgvector extension installed and vector columns functional
- [ ] Seed data present: admin parameters, singleton buckets, dev users
- [ ] Auth bypass mode works: dev user switcher, all routes protected
- [ ] POST /api/auth/validate syncs user to shadow table
- [ ] gRPC proto files compile successfully, stubs generated
- [ ] All 16 UI primitives render correctly in light and dark mode
- [ ] Navbar shows role-gated links (Reviews for Reviewers, Admin for Admins)
- [ ] Theme toggle switches between light/dark mode, persisted in localStorage
- [ ] Language switcher toggles German/English, persisted in localStorage
- [ ] ErrorBoundary catches and displays React errors gracefully
- [ ] TypeScript typecheck passes
- [ ] No regressions

## Notes
- Phase 0 handles project scaffolding (directory structure, Docker Compose, test infrastructure). M1 stories start at schema migration level.
- AI service Django models (context_summaries, buckets, chunks, embeddings) are created here but their Django `managed = True` lives in the AI service app. Cross-service model access patterns per data-model.md notes.
- The gRPC stubs are skeleton implementations that return placeholder responses. Full implementations come in later milestones.
- UI primitives follow shadcn/ui copy-paste-customize pattern. Each is a small self-contained file.
