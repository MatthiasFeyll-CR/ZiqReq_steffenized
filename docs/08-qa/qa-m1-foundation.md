# QA Report: Milestone 1 — Foundation & Auth

**Date:** 2026-03-09
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 2 (post-escalation)
**PRD:** tasks/prd-m1.json
**Progress:** .ralph/progress.txt

---

## Summary

Bugfix cycle 2 (post-escalation) review of M1 Foundation & Auth. The single remaining defect (DEF-001: test database dropped between test classes) has been **resolved**. Ralph added a `django_db_setup` fixture override to `conftest.py` and configured `TEST.NAME` in `test.py` to reuse the Docker-provided database. All 14 Python tests now pass (previously 7 errors in cycles 0 and 1). All 10 user stories pass acceptance criteria. All required gate checks pass.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Database Schema and pgvector Setup | PASS | All 22 tables, migrations, pgvector+HNSW confirmed. |
| US-002 | Seed Data | PASS | 21 admin params, 2 singleton buckets, conditional dev users. |
| US-003 | Gateway Django Models | PASS | User (uuid PK, ArrayField, JSONField), Notification, MonitoringAlertConfig. |
| US-004 | Core Django Models | PASS | 14 core models, immutable save(), partial unique constraints. |
| US-005 | Authentication Middleware and Dev Bypass | PASS | All 14 Python tests pass. DEF-001 resolved. |
| US-006 | gRPC Service Definitions and Stubs | PASS | 5 proto files, generated code, stub servicers, gRPC clients. |
| US-007 | UI Primitive Components | PASS | All 16 shadcn/ui components with correct variants. |
| US-008 | Layout Components | PASS | Navbar, UserDropdown, PageShell, AuthenticatedLayout, ConnectionIndicator, DevUserSwitcher. |
| US-009 | Theme System and i18n Setup | PASS | CSS variables, localStorage persistence, de/en translations. |
| US-010 | Common Components | PASS | ErrorBoundary, EmptyState, ErrorToast, ErrorLogModal, LoadingSpinner, SkipLink. |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 6 found / 0 missing out of 6 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-7.1.01 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Verified — tests dev users endpoint in bypass mode |
| T-7.1.02 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Verified — tests 404 in production mode |
| T-7.1.03 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Verified — tests dev login session creation |
| T-7.2.01 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Verified — valid token validates and syncs user |
| T-7.2.02 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Verified — expired token returns 401 |
| T-7.2.03 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Verified — roles synced from AD groups |

*Test manifest (`.ralph/test-manifest.json`) has entries for all test IDs.*

---

## Defects

*No defects. DEF-001 from previous cycle has been resolved.*

### DEF-001 Resolution

- **Original issue:** Test database `test_ziqreq_test` dropped between test classes — 7 tests errored.
- **Fix applied in:** `conftest.py` (added `django_db_setup` fixture override) and `services/gateway/gateway/settings/test.py` (added `TEST.NAME` pointing to Docker DB).
- **Verification:** All 14 Python tests pass. `docker compose -f docker-compose.test.yml run --rm python-tests pytest` exits with code 0.
- **Test result timeline:** Cycle 0: FAIL, Cycle 1: FAIL, **Cycle 2: PASS** — bugfix was effective.

---

## Deviations

*No deviations found. Implementation matches specifications.*

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python Tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 14 passed in 0.63s |
| Frontend Typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | FAIL (optional) | 1 error: Duplicate module named "events" (services/core/events vs services/ai/events). Pre-existing, not a required gate. |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | PASS | Clean |

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | |
| Backend lint (Ruff) | PASSED | |
| Backend typecheck (mypy) | FAILED (optional) | Duplicate module "events" — pre-existing, not blocking |
| Frontend lint (ESLint) | PASSED | |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | Sensitive Data Exposure | Minor | `services/gateway/gateway/settings/base.py` | SECRET_KEY has insecure default. Acceptable for M1 (dev-only). | Env-inject in production. |
| SEC-002 | Security Misconfiguration | Minor | `services/gateway/gateway/settings/base.py` | `ALLOWED_HOSTS = "*"` default. Acceptable for M1. | Restrict in production. |
| SEC-003 | Injection | Info | `services/gateway/apps/authentication/azure_ad.py` | `urlopen(url)` for JWKS. URL from server config, not user input. No risk. | No action. |

**No critical or major security findings.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Caching | Info | `services/gateway/apps/authentication/azure_ad.py` | JWKS cache uses module-level dict with 24h TTL. | Consider Redis for multi-process in later milestones. |

**No critical or major performance findings.**

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| UI Primitives (16) | `docs/03-design/component-specs.md` | PASS | All 16 components present |
| Navbar | `docs/03-design/design-system.md` | PASS | 56px, role-gated, gold underline |
| UserDropdown | `docs/03-design/design-system.md` | PASS | Theme + language toggles |
| PageShell | `docs/03-design/page-layouts.md` | PASS | Sticky navbar + content |
| ConnectionIndicator | N/A | PASS | Placeholder as specified |
| DevUserSwitcher | N/A | PASS | Visible only in bypass mode |
| Theme System | `docs/03-design/design-system.md` | PASS | CSS vars, localStorage, prefers-color-scheme |
| i18n | `docs/02-architecture/tech-stack.md` | PASS | de/en, default German |
| Common Components | `docs/03-design/component-specs.md` | PASS | All 6 components correct |

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### Database & Schema
- [ ] All 22 tables exist with correct columns, types, and constraints across gateway/core/ai services
- [ ] pgvector extension enabled; `EmbeddingVector.embedding` is a 1536-dimension vector with HNSW index
- [ ] Seed data present: 21 admin parameters, 2 singleton context buckets, 4 dev users (when DEBUG=True)
- [ ] Immutable save() enforced on ChatMessage, BrdVersion, ReviewTimelineEntry
- [ ] Partial unique constraints on ReviewAssignment (state=active) and MergeRequest (state=open)

### Authentication
- [ ] `GET /api/auth/dev-users` returns 200 with 4 users when DEBUG=True and AUTH_BYPASS=True
- [ ] `GET /api/auth/dev-users` returns 404 when DEBUG=False
- [ ] `POST /api/auth/dev-login` creates session with correct user data
- [ ] `POST /api/auth/dev-switch` switches active dev user
- [ ] `POST /api/auth/validate` with valid Azure AD JWT returns 200 and syncs user
- [ ] `POST /api/auth/validate` with expired JWT returns 401
- [ ] Azure AD group-to-role mapping syncs roles on login
- [ ] Auth middleware exempts `/api/auth/*` endpoints from authentication checks

### gRPC
- [ ] 5 proto files present: common.proto, core.proto, ai.proto, gateway.proto, pdf.proto
- [ ] Generated `_pb2.py`, `_pb2_grpc.py`, `_pb2.pyi` files present in `proto/`
- [ ] Stub servicers present for core, gateway, ai (processing + context), pdf
- [ ] gRPC clients present in gateway (core, ai, pdf), ai (core), notification (gateway, core)

### Frontend Components
- [ ] All 16 shadcn/ui primitives render correctly (button, card, input, textarea, select, switch, checkbox, badge, avatar, tooltip, dropdown-menu, dialog, tabs, skeleton, toast, sheet)
- [ ] Navbar renders at 56px height with role-gated links
- [ ] UserDropdown shows theme toggle and language toggle
- [ ] DevUserSwitcher visible only when `VITE_AUTH_BYPASS` is set
- [ ] AuthenticatedLayout redirects to `/login` when not authenticated
- [ ] Theme system toggles dark/light mode via `.dark` class on `<html>` with localStorage persistence
- [ ] i18n loads de (German) as default, supports en, persists language choice to localStorage
- [ ] ErrorBoundary catches render errors and shows fallback UI
- [ ] LoadingSpinner respects `prefers-reduced-motion`
- [ ] SkipLink visible only on keyboard focus

### Test Infrastructure
- [ ] `conftest.py` contains `django_db_setup` fixture override (scope=session) that runs migrate --run-syncdb
- [ ] `docker compose -f docker-compose.test.yml run --rm python-tests pytest` exits with code 0
- [ ] All 14 Python tests pass (7 dev bypass + 6 Azure AD + 1 smoke)

### Quality Baseline
- [ ] TypeScript typecheck (`npx tsc --noEmit`) passes with zero errors
- [ ] Ruff lint (`ruff check services/`) passes with zero errors
- [ ] ESLint (`npx eslint src/`) passes with zero errors
- [ ] All existing tests pass

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (DEF-001 from previous cycle resolved)
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 2 (post-escalation) — final
- **Note:** The bugfix cycle timeline shows clear convergence: Cycle 0 FAIL (7 test errors), Cycle 1 FAIL (7 test errors), Cycle 2 PASS (14/14 tests pass). The fix in `conftest.py` (django_db_setup override) and `test.py` (TEST.NAME config) resolved the persistent test infrastructure defect.
