# Milestone 1: Foundation

## Overview
- **Execution order:** 1 (first milestone)
- **Estimated stories:** 10
- **Dependencies:** None
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-7.1 | Development Auth Bypass | Must-have | features.md |
| F-7.2 | Production Authentication | Must-have | features.md |
| — | Docker Compose orchestration | Must-have | constraints.md #7 |
| — | Database schema + migrations | Must-have | data-model.md |
| — | Service scaffolding (all 6 services) | Must-have | project-structure.md |
| — | gRPC protobuf definitions + stubs | Must-have | api-design.md |
| — | Message broker setup | Must-have | tech-stack.md |
| — | Seed data (admin params, dev users, singletons) | Must-have | data-model.md |
| — | Frontend scaffold (Vite + React + providers) | Must-have | tech-stack.md |
| — | Test infrastructure (factories, helpers) | Must-have | test-plan.md |
| — | CI/CD pipeline (lint, test, E2E gates) | Must-have | testing-strategy.md |
| — | Idempotent event consumer infrastructure | Must-have | nonfunctional.md NFR-R2 |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| users | CREATE TABLE + seed dev users | id, email, first_name, last_name, display_name, roles | data-model.md |
| ideas | CREATE TABLE | id, title, state, visibility, owner_id, co_owner_id, deleted_at | data-model.md |
| idea_collaborators | CREATE TABLE | idea_id, user_id | data-model.md |
| chat_messages | CREATE TABLE | id, idea_id, sender_type, sender_id, content | data-model.md |
| ai_reactions | CREATE TABLE | message_id, reaction_type | data-model.md |
| user_reactions | CREATE TABLE | message_id, user_id, reaction_type | data-model.md |
| board_nodes | CREATE TABLE | id, idea_id, node_type, title, body, position_x/y, parent_id | data-model.md |
| board_connections | CREATE TABLE | source_node_id, target_node_id, label | data-model.md |
| brd_drafts | CREATE TABLE | idea_id, section_*, section_locks, readiness_evaluation | data-model.md |
| brd_versions | CREATE TABLE | idea_id, version_number, section_*, pdf_file_path | data-model.md |
| review_assignments | CREATE TABLE | idea_id, reviewer_id, assigned_by | data-model.md |
| review_timeline_entries | CREATE TABLE | idea_id, entry_type, author_id, content | data-model.md |
| collaboration_invitations | CREATE TABLE | idea_id, inviter_id, invitee_id, status | data-model.md |
| notifications | CREATE TABLE | user_id, event_type, title, body | data-model.md |
| chat_context_summaries | CREATE TABLE | idea_id, summary_text | data-model.md |
| idea_keywords | CREATE TABLE | idea_id, keywords | data-model.md |
| merge_requests | CREATE TABLE | requesting_idea_id, target_idea_id, merge_type, status | data-model.md |
| facilitator_context_bucket | CREATE TABLE + seed singleton | content | data-model.md |
| context_agent_bucket | CREATE TABLE + seed singleton | sections, free_text | data-model.md |
| admin_parameters | CREATE TABLE + seed all params | key, value, default_value, category | data-model.md |
| monitoring_alert_configs | CREATE TABLE | user_id, is_active | data-model.md |
| context_chunks | CREATE TABLE (pgvector) | chunk_text, embedding, source_section | data-model.md |
| idea_embeddings | CREATE TABLE (pgvector) | idea_id, embedding, source_text_hash | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/auth/validate | POST | Validate token, sync user shadow table | Bearer/bypass | api-design.md |
| /api/auth/dev-login | POST | Dev bypass login (select dev user) | None (bypass only) | api-design.md |
| /api/auth/dev-users | GET | List available dev users | None (bypass only) | api-design.md |
| /login | GET | Azure AD login page (production only) | Unauthenticated | pages.md |
| /health | GET | Health check (per service) | None | tech-stack.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| App shell (React Router, providers) | Frontend scaffold | tech-stack.md |
| Route definitions (/, /idea/:id, /reviews, /admin, /login) | Routing skeleton | pages.md |
| Login page (Azure AD redirect, production only) | Page | pages.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| Auth context (MSAL provider + bypass provider) | New | M1 |
| TanStack Query client | New | M1 |
| Redux store (empty, with DevTools) | New | M1 |
| gRPC client utilities | New | M1 |
| Message broker publisher utility | New | M1 |
| Backend factory-boy factories (all 18) | New | M1 |
| Frontend test helpers (renderWithProviders, etc.) | New | M1 |
| Idempotent event consumer base (event ID tracking, dedup) | New | M1 |
| CI pipeline (lint + typecheck + unit + E2E stages) | New | M1 |
| E2E test infrastructure (docker-compose.test.yml, Playwright, seed script) | New | M1 |

## Story Outline (Suggested Order)

1. **[Infrastructure] Docker Compose setup** — PostgreSQL (pgvector image), Redis, RabbitMQ, Nginx, all service containers. Docker Compose dev profile with hot reload.
2. **[Backend] Gateway service scaffold** — Django 5 project, DRF, Channels, ASGI config, settings (dev/test/prod), health endpoint.
3. **[Backend] Core service scaffold** — Django 5 project, gRPC server, Celery worker + beat config, settings.
4. **[Backend] AI + Notification + PDF service scaffolds** — Lightweight Django (AI), Python event consumer (Notification), Python gRPC server (PDF). Health endpoints.
5. **[Database] Schema migrations + seed data** — All 22 tables via Django ORM migrations. Seed admin parameters, singleton buckets, conditional dev users. pgvector extension creation.
6. **[Contracts] gRPC protobuf definitions + message broker exchanges** — All proto files from api-design.md. RabbitMQ exchanges/queues/DLQ setup (dead-letter exchange on every queue). Idempotent event consumer base class: event ID tracking, duplicate detection, processed event ID storage (NFR-R2). Service stubs that accept calls.
7. **[Auth] Production authentication (MSAL + Azure AD)** — Frontend: @azure/msal-react provider, Azure AD OIDC/OAuth2 login flow, silent token refresh before expiry, redirect to /login on auth failure. Backend: Azure AD token validation middleware (REST: Bearer token from Authorization header, WebSocket: token from query param), JWKS key caching, user claims extraction (object ID, roles from group membership), user sync to shadow `users` table (upsert on first login). Login page (/login route, production only). All routes protected — unauthenticated users redirected to login.
8. **[Auth] Auth bypass middleware + dev user switcher API** — Double-gated bypass (AUTH_BYPASS + DEBUG). 4 dev users. POST /api/auth/dev-login, GET /api/auth/dev-users, POST /api/auth/validate (bypass mode). All permission checks work identically to production — bypass only skips Azure AD token validation. Cannot activate in production (double-gate enforced in settings). No login screen in bypass mode.
9. **[Frontend] React scaffold** — Vite + TypeScript + React 19. Tailwind CSS 4 + shadcn/ui setup. React Router with route definitions. Redux Toolkit store. TanStack Query client. MSAL provider (production) + auth bypass provider (dev). Nginx proxy config for /api and /ws.
10. **[Testing] Test infrastructure + CI/CD pipeline** — Backend: all 18 factory-boy factories, MockGrpcClient, MockBrokerPublisher, AuthenticatedAPIClient. Frontend: renderWithProviders, createTestStore, mockAuthUser, all fixture builders. pytest + Vitest configs. E2E infrastructure: docker-compose.test.yml (test DB, AI mock mode), Playwright config, scripts/seed-e2e.py seed script. CI pipeline: Stage 1 (ESLint + tsc + Ruff + mypy), Stage 2 (unit + integration tests per service), Stage 3 (E2E via Playwright), Stage 4 (coverage reports + gating). PR coverage comments.

## Milestone Acceptance Criteria
- [ ] `docker compose up` starts all services without errors
- [ ] All 22 database tables created with correct schemas and indexes
- [ ] Seed data present: 23 admin parameters, 4 dev users, 2 singleton buckets
- [ ] Production auth: MSAL login flow redirects to Azure AD, token validated on API
- [ ] Production auth: silent token refresh works, expired token redirects to login
- [ ] Production auth: user sync creates/updates shadow user on first validated request
- [ ] Auth bypass: can switch between 4 dev users via API
- [ ] Auth bypass: double-gate prevents activation without both AUTH_BYPASS=True and DEBUG=True
- [ ] Frontend loads at localhost, routes to correct page shells
- [ ] gRPC calls between gateway↔core and gateway↔ai succeed (health checks)
- [ ] Message broker accepts published events on configured exchanges
- [ ] All factory-boy factories create valid test data
- [ ] Idempotent event consumer rejects duplicate event IDs
- [ ] CI pipeline runs all 4 stages (lint, test, E2E, coverage) without errors
- [ ] E2E test infrastructure: docker-compose.test.yml starts, seed script populates test data, Playwright runs
- [ ] TypeScript typecheck passes
- [ ] Python linting (Ruff) passes
- [ ] No test failures

## Notes
- All tables created upfront (single migration set) even though most won't be populated until later milestones. This avoids migration conflicts and gives later milestones a stable schema.
- gRPC stubs return placeholder responses — full implementation in later milestones.
- Frontend renders empty shells for all routes — page content added in later milestones.
- pgvector extension must be installed in PostgreSQL container (`pgvector/pgvector:pg16` Docker image).
- Production auth (F-7.2) requires Azure AD app registration (AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID, AZURE_AD_CLIENT_SECRET env vars). In local development, auth bypass mode is used instead. Both paths share the same middleware — bypass simply skips token validation.
- The login page (/login) is only shown in production mode. In bypass mode, it is skipped entirely.
- CI pipeline also includes: nightly suite setup (axe-core accessibility audit, bundle size check via size-limit, i18n key completeness script comparing de.json vs en.json). Nightly suite runs on schedule, not per-PR.
- Idempotent event consumer base class tracks processed event IDs to prevent duplicate processing (NFR-R2). All service consumers inherit this pattern.
