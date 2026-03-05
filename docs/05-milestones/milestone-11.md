# Milestone 11: Admin Panel + Monitoring

## Overview
- **Execution order:** 11 (runs after M10)
- **Estimated stories:** 8
- **Dependencies:** M6 (RAG pipeline for context re-indexing)
- **MVP:** No (post-MVP)

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-11.1 | Admin Panel Layout | Must-have | features.md |
| F-11.2 | AI Context Tab | Must-have | features.md |
| F-11.3 | Parameters Tab | Must-have | features.md |
| F-11.4 | Monitoring Tab | Must-have | features.md |
| F-11.5 | Backend Monitoring Service | Must-have | features.md |
| F-11.6 | Users Tab | Must-have | features.md |
| F-2.16 | Company Context Management | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| facilitator_context_bucket | READ, UPDATE | content, updated_by | data-model.md |
| context_agent_bucket | READ, UPDATE | sections, free_text, updated_by | data-model.md |
| context_chunks | DELETE (bulk), CREATE (bulk) on re-index | all columns | data-model.md |
| admin_parameters | READ, UPDATE | key, value, updated_by | data-model.md |
| monitoring_alert_configs | READ, UPDATE | user_id, is_active | data-model.md |
| users | READ (search) | id, email, first_name, last_name, display_name, roles | data-model.md |
| ideas | READ (aggregate stats) | state | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/admin/ai-context/facilitator | GET | Get facilitator context | Admin role | api-design.md |
| /api/admin/ai-context/facilitator | PUT | Update facilitator context | Admin role | api-design.md |
| /api/admin/ai-context/detailed | GET | Get detailed company context | Admin role | api-design.md |
| /api/admin/ai-context/detailed | PUT | Update detailed context (triggers re-indexing) | Admin role | api-design.md |
| /api/admin/parameters | GET | List all parameters | Admin role | api-design.md |
| /api/admin/parameters/:key | PUT | Update parameter value | Admin role | api-design.md |
| /api/admin/monitoring/dashboard | GET | Get monitoring dashboard data | Admin role | api-design.md |
| /api/admin/monitoring/alerts | GET | Get alert configuration | Admin role | api-design.md |
| /api/admin/monitoring/alerts | PUT | Update alert opt-in/out | Admin role | api-design.md |
| /api/admin/users/search | GET | Search users with stats | Admin role | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| AdminPanel | Page | page-layouts.md §7 |
| AdminTabLayout | Component | component-specs.md |
| AIContextTab | Component | component-specs.md |
| FacilitatorContextEditor | Component | component-specs.md |
| DetailedContextEditor | Component | component-specs.md |
| ParametersTab | Component | component-specs.md |
| ParameterForm | Component | component-specs.md |
| MonitoringTab | Component | component-specs.md |
| MonitoringDashboard | Component | component-specs.md |
| AlertConfigPanel | Component | component-specs.md |
| UsersTab | Component | component-specs.md |
| UserSearchPanel | Component | component-specs.md |
| UserProfileCard | Component | component-specs.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| Backend monitoring service (Celery periodic task) | New | M11 |
| Admin role route guard | New | M11 |
| AI security monitoring dashboard (content filter, jailbreak, fabrication flag counts) | Consumed | M11 (events from M5, M6, M7) |

## Story Outline (Suggested Order)

1. **[Backend] Admin panel route protection + parameters API** — Admin role middleware: validates user has 'admin' in roles. Gateway REST: GET /api/admin/parameters (list all with current values, defaults, descriptions, categories), PUT /api/admin/parameters/:key (update value, validate data_type). Changes apply immediately at runtime (no restart). Grouped by category (Application, Infrastructure, AI).
2. **[Backend] AI context management APIs** — Gateway REST: GET/PUT facilitator context, GET/PUT detailed context. PUT detailed context triggers re-indexing: Gateway → AI gRPC UpdateContextAgentBucket → AI service re-chunks, re-embeds, replaces context_chunks. PUT facilitator context: Gateway → AI gRPC UpdateFacilitatorBucket → AI service updates facilitator_context_bucket (cache invalidated).
3. **[Backend] Monitoring dashboard API + backend monitoring service** — Celery periodic task (configurable interval, default 60s): health checks on all services (gateway HTTP, AI gRPC, PDF gRPC, notification heartbeat, DB, Redis, broker, DLQ depth). Results stored for dashboard. GET /api/admin/monitoring/dashboard: active connections, ideas by state, active users, AI stats (from AI service gRPC), service health, DLQ counts.
4. **[Backend] Monitoring alert configuration + alerting pipeline** — GET/PUT /api/admin/monitoring/alerts: admin opt-in/out for email alerts. On health check failure or threshold breach: publish monitoring.alert event → Notification service sends email to opted-in admins. Alert data also stored for dashboard display.
5. **[Backend] User search API** — GET /api/admin/users/search: search by name or email (not eager-loaded, search required). Response: name, first name, email, roles, idea count (aggregate), review count (aggregate from review_timeline_entries), contribution count (aggregate: ideas owned + collaborating + messages sent).
6. **[Frontend] Admin panel layout + parameters tab** — /admin route, Admin role only. 4-tab layout with icons: AI Context, Parameters, Monitoring, Users. Parameters tab: list all parameters grouped by category. Edit form per parameter with type-appropriate input (integer, float, boolean, string). Save applies immediately. Current value + default shown.
7. **[Frontend] AI Context tab** — Two clearly separated areas. Facilitator context: free text editor for table of contents. Detailed company context: structured section editor (add/remove/edit sections) + free text block. Save triggers backend update + re-indexing (detailed only). Loading indicator during re-indexing.
8. **[Frontend] Monitoring tab + Users tab** — Monitoring: dashboard cards (connection count, ideas by state pie/chart, active users, AI processing stats, per-service health indicators). Alert config: toggle list of admins with opt-in/out. Users: search input → results display (name, email, roles, stats). Not eager-loaded — search required.

## Milestone Acceptance Criteria
- [ ] Admin panel accessible at /admin with correct role guard
- [ ] 4 tabs render with correct icons and content
- [ ] AI Context tab: edit and save facilitator context works
- [ ] AI Context tab: edit and save detailed context triggers re-indexing
- [ ] Context re-indexing: old chunks deleted, new chunks embedded and stored
- [ ] Parameters tab: all parameters displayed, edit and save apply immediately
- [ ] Monitoring dashboard: shows live data (connections, ideas, AI stats, health)
- [ ] Backend monitoring service runs periodic health checks
- [ ] Alert configuration: admin opt-in/out works, alerts sent on health issues
- [ ] Users tab: search by name/email, display profile with computed stats
- [ ] No unauthorized access (admin role enforced on all endpoints)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M10

## Notes
- Until this milestone, admin parameters can be managed via direct DB updates or a dev utility script. The admin UI formalizes this.
- Context re-indexing atomicity: old chunks preserved until new chunks fully indexed. On failure, old chunks remain intact (no partial state).
- Monitoring health checks are lightweight — they check connectivity, not deep functionality.
- DLQ depth monitoring depends on message broker admin API access (RabbitMQ management plugin / Azure Service Bus SDK).
- The monitoring tab is a lightweight dashboard, not a full observability solution. Production monitoring should use Azure-native tools.
