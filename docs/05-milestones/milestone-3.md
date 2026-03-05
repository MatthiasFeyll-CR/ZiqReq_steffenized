# Milestone 3: Admin Panel

## Overview
- **Wave:** 1
- **Estimated stories:** 7
- **Must complete before starting:** M1
- **Can run parallel with:** M2
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-11 | Admin Panel (all 4 tabs: AI Context, Parameters, Monitoring, Users) | P1 | F-11.1–F-11.6 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| facilitator_context_bucket | READ/UPDATE | content, updated_by, updated_at | data-model.md |
| context_agent_bucket | READ/UPDATE | sections, free_text, updated_by, updated_at | data-model.md |
| admin_parameters | READ/UPDATE | key, value, default_value, description, data_type, category | data-model.md |
| monitoring_alert_configs | CRUD | user_id, is_active | data-model.md |
| users | READ (search) | display_name, email, roles | data-model.md |
| ideas | READ (aggregate) | state | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| GET /api/admin/ai-context/facilitator | GET | Get facilitator bucket | Admin | api-design.md |
| PUT /api/admin/ai-context/facilitator | PUT | Update facilitator bucket | Admin | api-design.md |
| GET /api/admin/ai-context/context-agent | GET | Get context agent bucket | Admin | api-design.md |
| PUT /api/admin/ai-context/context-agent | PUT | Update context agent bucket | Admin | api-design.md |
| GET /api/admin/parameters | GET | List all parameters | Admin | api-design.md |
| PATCH /api/admin/parameters/:key | PATCH | Update parameter value | Admin | api-design.md |
| GET /api/admin/monitoring | GET | Get monitoring dashboard data | Admin | api-design.md |
| GET /api/admin/monitoring/alerts | GET | Get alert configuration | Admin | api-design.md |
| PATCH /api/admin/monitoring/alerts | PATCH | Update alert opt-in/out | Admin | api-design.md |
| GET /api/admin/users/search | GET | Search users | Admin | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Admin Panel (/admin) | Page | pages.md |
| AIContextEditor | Feature | component-inventory.md |
| ParametersTable | Feature | component-inventory.md |
| MonitoringDashboard | Feature | component-inventory.md |
| UserSearch | Feature | component-inventory.md |
| UserCard | Feature | component-inventory.md |
| KPICard | Feature | component-inventory.md |
| ServiceHealthTable | Feature | component-inventory.md |
| AlertRecipientChips | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Frontend+API] Admin page layout + role-based routing** — /admin route protected by Admin role. 4-tab navigation (AI Context, Parameters, Monitoring, Users) with icons per F-11.1. Role check in frontend (redirect non-admins). DRF permission class `IsAdmin` for all admin endpoints.
2. **[Frontend+API] AI Context tab** — Two isolated editor areas per F-11.2. Facilitator context: free text editor (Textarea auto-grow), GET/PUT API. Detailed company context: structured sections editor (dynamic section list with add/remove/reorder) + free text block, GET/PUT API. Both save to their respective singleton tables. Success toast on save.
3. **[Frontend+API] Parameters tab** — ParametersTable component: list all parameters from admin_parameters, grouped by category (Application, Infrastructure, AI). Inline editing: click value → edit → save. Validation per data_type (integer, float, boolean, string). PATCH on save. Changes apply immediately (F-11.3). Show default value for reference. Gold indicator on modified values.
4. **[Frontend+API] Users tab** — UserSearch component: search input (not eager-loaded per F-11.6). GET /api/admin/users/search?q=. UserCard component: avatar, name, first_name, email, roles (badges), computed stats: idea_count (COUNT ideas where owner_id=user), review_count (COUNT review_assignments where reviewer_id=user), contribution_count (COUNT chat_messages where sender_id=user). Stats computed via annotated queryset.
5. **[Frontend+API] Monitoring tab** — MonitoringDashboard component: KPICard for active connections (stub: 0), ideas by state (aggregate query), active users (stub: 0), AI processing stats (stub: 0/0). ServiceHealthTable: service name, status dot (green/yellow/red), last check timestamp. GET /api/admin/monitoring returns assembled dashboard data.
6. **[Backend] Monitoring service** — Implement Celery periodic task body for monitoring_health_check (registered in M1). Health checks per tech-stack.md: HTTP GET to gateway health endpoint, gRPC health check to AI/PDF services, broker connection check, Redis PING, DB connection check, DLQ depth query. Store results for dashboard API. Publish monitoring.alert event on unhealthy condition or threshold breach.
7. **[Frontend+API] Alert configuration** — AlertRecipientChips component: list of admins opted in to receive alerts. Toggle opt-in/out via PATCH. GET /api/admin/monitoring/alerts returns opted-in admin list. monitoring_alert_configs table CRUD.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Layout (Navbar, PageShell) | Available | M1 |
| Toast | Available | M1 |
| EmptyState | Available | M1 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `frontend/src/pages/admin-panel.tsx`
- `frontend/src/components/admin/`
- `frontend/src/features/admin/`
- `services/gateway/apps/admin_ai_context/`
- `services/gateway/apps/admin_config/`
- `services/gateway/apps/monitoring/` (views, urls, tests — model pre-exists from M1)
- `services/core/apps/admin_config/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/app/router.tsx` (add /admin route)
- `services/core/apps/admin_config/tasks.py` (implement monitoring_health_check task body)
- `services/core/grpc_server/servicers/core_servicer.py` (implement GetIdeasByState, GetUserStats)

## Milestone Acceptance Criteria
- [ ] /admin accessible to Admin role only, non-admins redirected
- [ ] AI Context tab: both editors save and load correctly
- [ ] Parameters tab: all parameters listed, inline editing works, changes persist
- [ ] Users tab: search returns results, UserCard shows correct stats
- [ ] Monitoring tab: KPI cards render, service health table shows check results
- [ ] Health check Celery task runs on schedule, detects unhealthy services
- [ ] Alert opt-in/out works, monitoring.alert events published on health issues
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1

## Notes
- **Stub: Monitoring "Active connections"** — Returns 0. Real WebSocket connection counting wired in M8 when presence tracking is implemented. Gateway tracks connection count per idea via channel groups.
- **Stub: Monitoring "AI processing stats"** — Returns 0 for count and 0% for success rate. Real AI metrics wired in M6 when AI pipeline tracks invocations.
- **Stub: AI Context save → RAG re-indexing** — Saving context agent bucket updates the DB only. Does NOT trigger chunking/embedding/re-indexing. RAG indexing pipeline implemented in M12. QA should verify that after M12, saving context triggers re-indexing.
- **Stub: Email alert dispatch** — monitoring.alert event is published to message broker. No consumer processes it yet — actual email dispatch requires the notification service (M10). For now, alerts are logged and stored for dashboard display only.
- **Stub: Monitoring "active users"** — Returns 0. Real active user count from WebSocket presence wired in M8.
