# Milestone 15: Admin Panel

## Overview
- **Execution order:** 15 (runs after M8)
- **Estimated stories:** 10
- **Dependencies:** M8
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-11.1 | Admin Panel Layout | P1 | features.md FA-11 |
| F-11.2 | AI Context Tab | P1 | features.md FA-11 |
| F-11.3 | Parameters Tab | P1 | features.md FA-11 |
| F-11.4 | Monitoring Tab | P1 | features.md FA-11 |
| F-11.5 | Backend Monitoring Service | P1 | features.md FA-11 |
| F-11.6 | Users Tab | P1 | features.md FA-11 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| facilitator_context_bucket | SELECT, UPDATE | content, updated_by | data-model.md |
| context_agent_bucket | SELECT, UPDATE | sections, free_text, updated_by | data-model.md |
| admin_parameters | SELECT, UPDATE | key, value, default_value, data_type, category | data-model.md |
| monitoring_alert_configs | SELECT, UPDATE | user_id, is_active | data-model.md |
| users | SELECT (search, stats) | display_name, email, roles | data-model.md |
| ideas | SELECT (aggregate stats) | state | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/admin/ai-context/facilitator | GET/PATCH | Facilitator context bucket | Bearer (Admin) | api-design.md |
| /api/admin/ai-context/company | GET/PATCH | Company context bucket | Bearer (Admin) | api-design.md |
| /api/admin/parameters | GET | List all parameters | Bearer (Admin) | api-design.md |
| /api/admin/parameters/:key | PATCH | Update parameter value | Bearer (Admin) | api-design.md |
| /api/admin/monitoring | GET | Dashboard data | Bearer (Admin) | api-design.md |
| /api/admin/monitoring/alerts | GET/PATCH | Alert configs | Bearer (Admin) | api-design.md |
| /api/admin/users/search | GET | Search users with stats | Bearer (Admin) | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| Admin Panel (/admin) | Page | page-layouts.md S4 |
| AIContextEditor | Feature | component-inventory.md |
| ParametersTable | Feature | component-inventory.md |
| MonitoringDashboard | Feature | component-inventory.md |
| KPICard | Feature | component-specs.md S2.5 |
| ServiceHealthTable | Feature | component-inventory.md |
| AlertRecipientChips | Feature | component-inventory.md |
| UserSearch | Feature | component-inventory.md |
| UserCard | Feature | component-specs.md S2.4 |

## Story Outline (Suggested Order)
1. **[API]** Admin AI context endpoints — GET/PATCH for facilitator bucket and company context bucket
2. **[API]** Admin parameters endpoints — GET list, PATCH individual parameter, validation by data_type
3. **[API]** Admin monitoring endpoint — aggregate stats (connections, ideas by state, users, AI processing)
4. **[API]** Admin users search endpoint — search by name/email, compute idea_count/review_count/contribution_count
5. **[Backend]** Context re-indexing trigger — on company context PATCH, trigger AI gRPC UpdateContextAgentBucket -> re-chunk + re-embed
6. **[Backend]** Monitoring backend service — Celery periodic task, health checks (gateway, AI, PDF, notification, DB, Redis, broker, DLQ depth)
7. **[Backend]** Alert configuration + dispatch — admin opt-in/out, monitoring.alert event -> email to opted-in admins
8. **[Frontend]** Admin panel layout — /admin route (Admin role-gated), 4 tabs (AI Context, Parameters, Monitoring, Users) with icons
9. **[Frontend]** AI Context + Parameters tabs — facilitator editor, company context section editor, parameters table with inline editing
10. **[Frontend]** Monitoring + Users tabs — KPI cards, service health table, alert config chips, user search with UserCards

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | AI context API | ~5,000 | api-design.md (admin/ai-context), data-model.md | 3-4 files | Medium | Two bucket editors |
| 2 | Parameters API | ~4,000 | api-design.md (admin/parameters), data-model.md | 2-3 files | Low | — |
| 3 | Monitoring API | ~5,000 | api-design.md (admin/monitoring), tech-stack.md (monitoring) | 3-4 files | Medium | Cross-service aggregation |
| 4 | Users search API | ~4,000 | api-design.md (admin/users), data-model.md | 2-3 files | Medium | Computed stats |
| 5 | Context re-indexing | ~5,000 | agent-architecture.md (S6.3 RAG indexing) | 2-3 files | Medium | Pipeline trigger |
| 6 | Monitoring service | ~7,000 | tech-stack.md (Monitoring Service), features.md (F-11.5) | 4-6 files | High | Multiple health checks |
| 7 | Alert config | ~4,000 | features.md (F-11.4), data-model.md (monitoring_alert_configs) | 3-4 files | Medium | Email alert pipeline |
| 8 | Admin layout | ~4,000 | page-layouts.md (S4), component-specs.md (S7) | 3-4 files | Low | — |
| 9 | AI Context + Params | ~6,000 | page-layouts.md (S4), component-specs.md | 5-7 files | Medium | Section editor, inline table |
| 10 | Monitoring + Users | ~5,000 | page-layouts.md (S4), component-specs.md (S2.4, S2.5) | 5-7 files | Medium | Dashboard components |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~49,000
- **Cumulative domain size:** Medium-Large (admin CRUD + monitoring service + 4 tab UIs)
- **Information loss risk:** Medium (5)
- **Context saturation risk:** Low-Medium
- **Heavy stories:** 1 (monitoring service)

## Milestone Acceptance Criteria
- [ ] Admin panel accessible at /admin (Admin role only)
- [ ] AI Context tab: facilitator and company context editors save and trigger re-indexing
- [ ] Parameters tab: all parameters displayed, inline editing, changes apply at runtime
- [ ] Monitoring tab: KPI cards show live stats, service health table shows status
- [ ] Monitoring backend service runs periodically, checks all services
- [ ] Alert configuration: admins can opt in/out, alerts sent via email
- [ ] Users tab: search by name/email, user cards show stats
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M14

## Notes
- Monitoring metrics that depend on WebSocket connections and AI processing stats require those services to be running.
- The soft delete cleanup Celery job (permanent deletion) should be implemented here if not already in M2.
- Keyword matching sweep schedule is configurable via admin parameters.
