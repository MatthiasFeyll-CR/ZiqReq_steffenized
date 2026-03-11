# Dependency Analysis — E2E Test Milestones (M17–M21)

## Context

These milestones are **test-only** — they write E2E tests against the already-implemented application (M1–M16). No production code is created; only test infrastructure, helpers, fixtures, and Playwright test specs.

## Infrastructure Layer (must exist first)

| Component | Type | Why First | Source |
|-----------|------|-----------|--------|
| Playwright config + project setup | Test infra | All E2E tests depend on Playwright being configured | docs/02-architecture/testing-strategy.md |
| docker-compose.e2e.yml | Test infra | All E2E tests need full stack running with AI mock mode | docker-compose.test.yml, infra/docker/docker-compose.yml |
| E2E seed script | Test data | Tests need baseline data (users, ideas in various states) | docs/02-architecture/testing-strategy.md |
| Auth bypass helpers | Test utility | Every test needs authenticated users | FA-7 |
| Azure OpenAI mock fixtures | Test utility | All AI features use mocked responses | FA-2, docs/04-test-architecture/test-plan.md |
| Email service mock/capture | Test utility | Notification tests need to verify emails without sending | FA-12 |
| Page Object Models (base) | Test pattern | Reusable selectors/actions reduce duplication | Best practice |

## Feature Test Dependency Map

| Milestone | Features Tested | Hard Dependencies | Soft Dependencies |
|-----------|----------------|-------------------|-------------------|
| M17 | FA-7, FA-9, FA-16, FA-17, test infra | None (foundation) | — |
| M18 | FA-1, FA-2, FA-3, FA-6, FA-15 | M17 (infra + auth + landing) | — |
| M19 | FA-4, FA-8, FA-10, FA-12, FA-13 | M17, M18 (workspace must be testable) | — |
| M20 | FA-5, FA-11 | M17, M18 (workspace), M19 (review + notifications) | — |
| M21 | FA-14, journeys, concurrency, error scenarios | M17, M18, M19, M20 (all features testable) | — |

## Dependency Chain

```
M17 (Test Infra + Foundation)
 └── M18 (Workspace + Chat + Board + Real-Time)
      └── M19 (BRD + Review + Collaboration + Notifications)
           └── M20 (Similarity + Merge + Admin)
                └── M21 (Error Handling + Journeys + Edge Cases)
```

## External Service Mocking Strategy

| External Service | Mock Approach | Setup Location |
|-----------------|---------------|----------------|
| Azure AD (authentication) | AUTH_BYPASS=True + DEBUG=True (dev users) | docker-compose.e2e.yml env vars |
| Azure OpenAI (AI processing) | AI_MOCK_MODE=True, fixture responses in services/ai/fixtures/ | docker-compose.e2e.yml env vars + existing fixtures |
| Email Service (SMTP) | MailHog container or Django console email backend capturing to file | docker-compose.e2e.yml + test helpers |

## Internal Services (All Real)

| Service | Container | Notes |
|---------|-----------|-------|
| Frontend (React) | Vite dev server or nginx-served build | Real frontend |
| Gateway (Django/Daphne) | Real gateway with WebSocket support | AUTH_BYPASS + DEBUG |
| Core (Django + gRPC) | Real core with migrations | Real DB operations |
| AI (gRPC + mock mode) | Real AI service but AI_MOCK_MODE=True | Deterministic fixture responses |
| Notification | Real notification service | Email captured, not sent |
| PDF | Real PDF generation service | Real PDF output |
| PostgreSQL | pgvector/pgvector:pg16 | Test database, seeded |
| Redis | redis:7-alpine | Real channel layer |
| RabbitMQ | rabbitmq:3-management-alpine | Real message broker |
| Celery worker | Real worker | CELERY_ALWAYS_EAGER or real async |
