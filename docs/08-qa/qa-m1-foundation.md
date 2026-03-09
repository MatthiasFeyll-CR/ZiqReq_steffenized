# QA Report: Milestone 1 — Foundation & Auth

**Date:** 2026-03-09
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 3 (FINAL)
**PRD:** tasks/prd-m1.json
**Progress:** .ralph/progress.txt

---

## Summary

Re-reviewed all 10 user stories in M1 after bugfix cycle 3 (FINAL). Ralph removed the `@pytest.mark.django_db` decorator from both `TestDevBypass` and `TestAzureADAuth` classes as recommended. However, **DEF-001 persists** — the pipeline test execution still shows 7 errors in `test_dev_bypass.py` with `database "test_ziqreq_test" does not exist`. The fix was correctly applied (confirmed by code inspection) but did not resolve the underlying pytest-django/TestCase database lifecycle conflict. Since this is the 3rd consecutive bugfix cycle failure on the same defect, the milestone is **ESCALATED** for human intervention.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Database Schema and pgvector Setup | PASS | All 22 tables, migrations, pgvector confirmed. |
| US-002 | Seed Data | PASS | 21 admin params, 2 singleton buckets, conditional dev users. |
| US-003 | Gateway Django Models | PASS | User (uuid PK, ArrayField, JSONField), Notification, MonitoringAlertConfig. |
| US-004 | Core Django Models | PASS | 14 core models, immutable save(), partial unique constraints. |
| US-005 | Authentication Middleware and Dev Bypass | FAIL | DEF-001: 7 test_dev_bypass.py tests still error. AC "All T-7.1.* and T-7.2.* tests pass" NOT met. |
| US-006 | gRPC Service Definitions and Stubs | PASS | 5 proto files, generated code, stub servicers, gRPC clients. |
| US-007 | UI Primitive Components | PASS | All 16 shadcn/ui components present with correct variants. |
| US-008 | Layout Components | PASS | Navbar, UserDropdown, PageShell, AuthenticatedLayout, ConnectionIndicator, DevUserSwitcher. |
| US-009 | Theme System and i18n Setup | PASS | CSS variables, localStorage persistence, de/en translations. |
| US-010 | Common Components | PASS | ErrorBoundary, EmptyState, ErrorToast, ErrorLogModal, LoadingSpinner, SkipLink. |

**Stories passed:** 9 / 10
**Stories with defects:** 1 (US-005)
**Stories with deviations:** 0

---

## Test Matrix Coverage

**Pipeline scan results:** 7 found / 0 missing out of 7 expected

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-7.1.01 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Implemented — tests dev users endpoint in bypass mode. ERRORs at runtime (DEF-001). |
| T-7.1.02 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Implemented — tests 404 in production mode. ERRORs at runtime (DEF-001). |
| T-7.1.03 | FOUND | `services/gateway/apps/authentication/tests/test_dev_bypass.py` | Implemented — tests dev login creates session. ERRORs at runtime (DEF-001). |
| T-7.1.04 | FOUND | `frontend/src/__tests__/dev-login-flow.test.tsx` | Passes. 4 test cases covering dev user selection and identity visibility. |
| T-7.2.01 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Passes — valid token validates and syncs user. |
| T-7.2.02 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Passes — expired token returns 401. |
| T-7.2.03 | FOUND | `services/gateway/apps/authentication/tests/test_azure_ad.py` | Passes — roles synced from AD groups. |

*Test manifest (.ralph/test-manifest.json) has 7 entries. All test IDs registered.*

---

## Defects

### DEF-001: Test database lifecycle — `test_ziqreq_test` dropped between test classes (7 tests error) — PERSISTS through 3 bugfix cycles

- **Severity:** Major
- **Story:** US-005
- **File(s):** `services/gateway/apps/authentication/tests/test_dev_bypass.py`, `services/gateway/apps/authentication/tests/test_azure_ad.py`, `services/gateway/gateway/settings/test.py`, `pyproject.toml`, `conftest.py`
- **Expected (per spec):** All T-7.1.* and T-7.2.* tests pass (14 Python tests: 7 dev bypass + 6 Azure AD + 1 smoke).
- **Actual (in code):** 7 passed (6 Azure AD + 1 smoke), 7 errors (all test_dev_bypass.py tests). Error: `OperationalError: database "test_ziqreq_test" does not exist — It seems to have just been dropped or renamed.`
- **Fix applied in cycle 3:** Removed `@pytest.mark.django_db` decorator from both `TestDevBypass` and `TestAzureADAuth` classes (confirmed by code inspection — decorators are absent in current files). Also removed unused `import pytest`. Fix did NOT resolve the issue.

---

## Deviations

*No deviations found. Implementation matches specifications.*

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Frontend Typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | FAIL (optional) | 1 error: Duplicate module named "events" (services/core/events vs services/ai/events). Not a required gate. |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | PASS | Clean |
| Python Tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | FAIL | 7 passed, 7 errors. See DEF-001. |

---

## Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | |
| Backend lint (Ruff) | PASSED | |
| Backend typecheck (mypy) | FAILED (optional) | Duplicate module "events" — not blocking |
| Frontend lint (ESLint) | PASSED | |

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | Sensitive Data Exposure | Minor | `services/gateway/gateway/settings/base.py` | SECRET_KEY has insecure default. Acceptable for M1 (dev-only). | Env-inject in production. |
| SEC-002 | Security Misconfiguration | Minor | `services/gateway/gateway/settings/base.py` | `ALLOWED_HOSTS = "*"` default. Acceptable for M1. | Restrict in production. |
| SEC-003 | Injection | Info | `services/gateway/apps/authentication/azure_ad.py:26` | `urlopen(url)` for JWKS. URL from server config, not user input. No risk. | No action. |

**No critical or major security findings.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Caching | Info | `services/gateway/apps/authentication/azure_ad.py:11-12` | JWKS cache uses module-level dict with 24h TTL. | Consider Redis for multi-process in later milestones. |

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

## Escalation Report

**Milestone:** 1 — Foundation & Auth
**Bugfix cycles completed:** 3
**Escalation reason:** Milestone has failed QA 3 times without resolution. A single defect (DEF-001) has persisted through all 3 bugfix cycles despite progressively deeper fixes.

### Persistent Defects

**DEF-001** — Test database `test_ziqreq_test` is dropped between test classes. All 7 `test_dev_bypass.py` tests error with `OperationalError: database "test_ziqreq_test" does not exist`.

| Cycle | Fix Applied | Result |
|-------|-------------|--------|
| 1 | Added `TEST.NAME = 'ziqreq_test'` to test settings | DB name changed from `test_ziqreq_test` to `ziqreq_test` — Django used the live DB as test DB, dropping it during teardown. Same error with different DB name. |
| 2 | Removed `TEST` block entirely from test settings | Django correctly creates `test_ziqreq_test` but it gets dropped after `TestAzureADAuth` completes, before `TestDevBypass` runs. Error message now references `test_ziqreq_test`. |
| 3 | Removed `@pytest.mark.django_db` decorator from both TestCase classes, removed unused `import pytest` | Fix confirmed applied (decorators absent in code). Same error persists — DB still dropped between test classes. |

### Root Cause Analysis

The root cause is a **pytest-django test database lifecycle issue** when multiple `django.test.TestCase` subclasses run in the same pytest session. The test infrastructure (not the application code) is broken.

**Why the bugfix cycle is not converging:**

- [x] Defect is in shared infrastructure that Ralph cannot safely modify
- [x] Fix requires architectural changes beyond Ralph's scope

**Technical details:**

1. `pyproject.toml` sets `DJANGO_SETTINGS_MODULE = "gateway.settings.test"` and `pythonpath = ["services/gateway", "services/core", "services/ai"]`
2. `test.py` parses `DATABASE_URL=postgresql://testuser:testpass@postgres:5432/ziqreq_test` and sets `NAME = "ziqreq_test"`
3. pytest-django auto-creates `test_ziqreq_test` (prefixed with `test_`) at session start
4. `TestAzureADAuth` (6 tests) runs first and passes
5. Between `TestAzureADAuth` and `TestDevBypass`, the test database is dropped
6. All 7 `TestDevBypass` tests fail with `database "test_ziqreq_test" does not exist`

The DB destruction between test classes suggests a **pytest-django database setup fixture scope mismatch**. Possible causes:
- pytest-django's `django_db_setup` fixture (session-scoped) interacts incorrectly with Django `TestCase.setUpClass()`/`tearDownClass()` which calls `cls._rollback_atomics()` and may close all DB connections, triggering pytest-django to think the DB needs teardown
- The multi-`pythonpath` configuration may confuse Django's test runner about which databases to manage
- A missing or misconfigured `conftest.py` at the `services/gateway/` level may prevent proper fixture scoping

### Recommendation

**Human intervention required.** The fix is a test infrastructure change, not an application code change. Recommended approaches (in order of preference):

1. **Add a gateway-level conftest.py** with a `django_db_setup` fixture that prevents premature DB teardown:
   ```python
   # services/gateway/conftest.py (or project-root conftest.py)
   import pytest

   @pytest.fixture(scope="session")
   def django_db_setup(django_test_environment, django_db_blocker):
       """Override default to prevent DB teardown between test classes."""
       from django.test.utils import setup_databases, teardown_databases
       with django_db_blocker.unblock():
           db_cfg = setup_databases(
               verbosity=0,
               interactive=False,
               keepdb=False,
           )
           yield
           teardown_databases(db_cfg, verbosity=0)
   ```

2. **Convert both test classes to plain pytest functions** using `@pytest.mark.django_db` instead of `django.test.TestCase`, eliminating the TestCase lifecycle entirely:
   ```python
   @pytest.mark.django_db
   def test_dev_users_endpoint_in_bypass_mode(client, settings):
       settings.DEBUG = True
       settings.AUTH_BYPASS = True
       # ... test body using pytest fixtures
   ```

3. **Merge both test classes into a single TestCase** to avoid the inter-class DB teardown issue.

4. **Use `--reuse-db` flag** in pytest configuration to prevent DB destruction between runs:
   ```toml
   [tool.pytest.ini_options]
   addopts = "--reuse-db"
   ```

---

## Verdict

- **Result:** ESCALATE
- **Defects found:** 1 (1 Major — DEF-001, persistent through 3 bugfix cycles)
- **Deviations found:** 0
- **Bugfix PRD required:** no (escalation — cycle limit reached)
- **Bugfix cycle:** 3 (FINAL)
- **Escalation:** DEF-001 requires human intervention to fix pytest-django test infrastructure
