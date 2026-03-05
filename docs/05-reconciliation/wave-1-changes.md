# Wave 1 Spec Reconciliation

## Summary
- **Wave:** 1
- **Milestones included:** M2 (Landing Page & Idea Workspace Shell), M3 (Admin Panel)
- **Date:** 2026-03-05
- **Total deviations found:** 22
- **Auto-applied (SMALL TECHNICAL):** 15
- **Auto-applied (FEATURE DESIGN):** 3
- **Auto-applied (LARGE TECHNICAL):** 3
- **Rejected:** 0
- **Not actionable (future milestone / informational):** 1

> **Note:** Pipeline mode -- all changes auto-applied per pipeline configuration (QA-trusted).

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: Landing/workspace components co-located in page dirs, not components/ | `docs/02-architecture/project-structure.md` | Replaced flat `pages/` listing with `LandingPage/` and `IdeaWorkspace/` directory structures with sub-components. Removed `landing/` and `workspace/` from `components/`. Added `shared/IdeaCard/`. |
| 2 | D-002: Pages use directory + re-export pattern | `docs/02-architecture/project-structure.md` | Added `landing-page.tsx` and `idea-workspace.tsx` as re-exports from their respective directories. |
| 3 | D-004: Rejected state dot uses orange-500 | `docs/03-design/design-system.md` | Changed Rejected color from `#D97706 (amber-600)` / `#F59E0B (amber-400)` to `#F97316 (orange-500)` / `#F97316 (orange-500)`. |
| 4 | D-005: Gateway ideas app has authentication.py and _brd_check.py | `docs/02-architecture/project-structure.md` | Added `authentication.py` (MiddlewareAuthentication) and `_brd_check.py` (stub) to gateway ideas app listing. |
| 5 | D-007: hooks.ts renamed to hooks.tsx | N/A (PRD-specific, not upstream spec) | Noted: file extension changed when JSX was added. No upstream doc updated (PRDs are consumed, not maintained). |
| 6 | D-012: Monitoring auto-refresh at 30s | N/A | Existing wireframe shows "Last: 30s ago" which implies auto-refresh. Implementation uses 30s `refetchInterval`. No change needed. |
| 7 | D-014: Dropped state dot uses gray-400 | `docs/03-design/design-system.md` | Changed Dropped light color from `#6B7280 (gray-500)` to `#9CA3AF (gray-400)`. |
| 8 | D-M3-001: Context agent endpoint path mismatch | `docs/05-milestones/milestone-3.md` | Changed `/api/admin/ai-context/detailed` to `/api/admin/ai-context/context-agent` (2 occurrences). |
| 9 | D-M3-004: Reviewer badge uses yellow not amber | `docs/03-design/component-specs.md` | Changed Reviewer role badge from `bg-amber-100 text-amber-700` to `bg-yellow-100 text-yellow-800`. |
| 10 | D-M3-005: Admin page is flat file, not directory | `docs/05-milestones/milestone-3.md` | Changed file ownership from `frontend/src/pages/AdminPanel/` to `frontend/src/pages/admin-panel.tsx`. |
| 11 | D-M3-006: Gateway admin uses 3 separate apps | `docs/05-milestones/milestone-3.md` | Changed `services/gateway/apps/admin/` and `services/core/apps/admin/` to actual app paths: `admin_ai_context/`, `admin_config/`, `monitoring/`, `services/core/apps/admin_config/`. |
| 12 | D-M3-007: Health check task in admin_config app | `docs/05-milestones/milestone-3.md` | Changed `services/core/tasks.py` to `services/core/apps/admin_config/tasks.py`. |
| 13 | D-M3-016: UserCard stats format | `docs/03-design/component-specs.md` | Changed wireframe from `Ideas: 12 | Reviews: 8 | Contributions: 5` to `12 ideas | 8 reviews | 5 contributions`. |
| 14 | D-M3-017: Service health table services | `docs/03-design/page-layouts.md` | Replaced "API Gateway, WebSocket, PostgreSQL, RabbitMQ / Service Bus" with "Gateway, PDF Service, Database, Broker" to match api-design.md and implementation. |
| 15 | D-M3-021: KPI card label "AI Reqs" | `docs/03-design/page-layouts.md` | Changed "AI Reqs" to "AI Succ Rate" in wireframe to match implementation showing success rate percentage. |

### FEATURE DESIGN (Auto-applied -- pipeline trust)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-003: In Review state uses amber-500 not brand gold | `docs/03-design/design-system.md` | Changed In Review color from `#FFD700 (brand-gold)` to `#F59E0B (amber-500)` in both light and dark. Resolves internal conflict between design-system.md (gold) and component-specs.md (amber). |
| 2 | D-M3-003: Admin panel built in M3, not incrementally M9/M13 | `docs/03-design/component-specs.md` | Replaced "M9 delivers only the AI Context tab... Full 4-tab admin shell assembled in M13" with "M3 delivers all 4 tabs in a single milestone." |
| 3 | D-009: M2 US-008 not implemented | N/A | US-008 (review section visibility, auto-scroll, section locking, browser tab title) was not delivered in M2. These features (F-1.2, F-1.3, F-1.4, F-1.8) remain unimplemented. No spec change needed -- spec is correct; implementation is incomplete. Tracked as carry-forward. |

### LARGE TECHNICAL (Auto-applied -- pipeline trust)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-008: Core gRPC servicer reads Gateway's users table via raw SQL | `docs/02-architecture/data-model.md` | Expanded cross-service raw SQL exception to include: Core servicers reading Gateway tables (users) for display name resolution. |
| 2 | D-010: Gateway uses unmanaged model for Core's admin_parameters | `docs/02-architecture/data-model.md`, `docs/02-architecture/project-structure.md` | Expanded cross-service exception to include Gateway unmanaged models for shared-DB tables. Added `models.py` with unmanaged model note to gateway admin_config. Updated DB strategy text to reference exceptions. |
| 3 | D-M3-009: Parameter event publishing stubbed | N/A | `admin.parameter.updated` broker event is logged but not published (EventPublisher not available in Gateway). No spec change -- spec is correct; implementation is a documented stub. |

### REJECTED

None.

## Not Actionable

| # | Deviation | Reason |
|---|-----------|--------|
| 1 | D-009: M2 US-008 stuck (review section, auto-scroll, locking, browser tab) | Implementation incomplete, not a spec deviation. Spec remains correct. Features carry forward to a future bugfix or follow-up. |

## Documents Modified

| Document | Changes |
|----------|---------|
| `docs/02-architecture/project-structure.md` | Pages directory structure (LandingPage/, IdeaWorkspace/ dirs with re-exports), components reorganized (shared/IdeaCard/, admin sub-components expanded), gateway ideas app files (authentication.py, _brd_check.py), monitoring app (removed phantom serializers.py), admin_config (added unmanaged model note), cross-service communication note updated |
| `docs/02-architecture/data-model.md` | Expanded cross-service raw SQL exception to cover 3 cases: Celery tasks, Core servicer user lookups, Gateway unmanaged models |
| `docs/03-design/design-system.md` | Idea state colors: In Review (gold -> amber-500), Dropped (gray-500 -> gray-400), Rejected (amber-600 -> orange-500) |
| `docs/03-design/component-specs.md` | Admin panel build note (M9/M13 -> M3), Reviewer badge (amber -> yellow), UserCard stats format (label-first -> count-first) |
| `docs/03-design/page-layouts.md` | Monitoring service health table (updated service names), KPI card label (AI Reqs -> AI Succ Rate) |
| `docs/05-milestones/milestone-3.md` | Context agent endpoint path (detailed -> context-agent), file ownership paths (AdminPanel/ -> admin-panel.tsx, apps/admin/ -> actual app paths), health check task path |

## Impact on Future Milestones

1. **M2 US-008 carry-forward:** Features F-1.2 (review section visibility), F-1.3 (auto-scroll), F-1.4 (section locking/LockOverlay), F-1.8 (browser tab title) were not delivered. These should be addressed before M7 (BRD) which depends on the review section.

2. **Cross-service DB access pattern:** The expanded exception in data-model.md now documents 3 patterns for direct DB access. Future milestones should prefer gRPC for new cross-service communication, using direct DB only when gRPC would create circular dependencies or when the tables share the same PostgreSQL instance.

3. **MiddlewareAuthentication reuse:** The `authentication.py` pattern in gateway/apps/ideas/ should be imported by future gateway apps rather than duplicated. A shared location (e.g., `apps/authentication/drf.py`) would be better for M4+.

4. **EventPublisher in Gateway:** The `admin.parameter.updated` event is currently stubbed. When event publishing infrastructure reaches Gateway (potentially M8+), this should be wired up.
