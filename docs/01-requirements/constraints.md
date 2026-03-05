# Constraints & Assumptions

## Hard Constraints

1. **Internal tool** — exclusively for Commerz Real employees. No external/public access under any circumstances.
2. **Azure AD dependency** — all authentication and user identity from a single Azure AD tenant. Role assignment via AD group membership.
3. **Azure OpenAI dependency** — all AI features use Azure OpenAI.
4. **Single-tenant** — no multi-tenancy or cross-organization features.
5. **No anonymous access** — even read-only link sharing requires Azure AD authentication.
6. **Production deployment on Azure** — application runs on Azure Container Apps in production.
7. **Local development via Docker** — all services run in Docker containers for local development. Auth bypass mode exists exclusively for this purpose.
8. **Full release** — no phased feature release. The complete application is delivered as one release. Development is split into milestones for demarcation only.

## Technology Standards

Technology decisions (languages, frameworks, libraries, infrastructure) were defined in a previous architecture session and are documented in `docs_old/02-architecture/tech-stack.md`. Key corporate standards identified:

- **Frontend:** React + TypeScript + Tailwind CSS (corporate standards)
- **Backend:** Python + Django (corporate standard)
- **Service-to-service:** gRPC (corporate standard)
- **Database:** PostgreSQL (corporate standard)
- **Hosting:** Azure Container Apps (corporate standard)

> ⚙️ DOWNSTREAM → **Software Architect**: Review and carry forward or update the technology decisions from `docs_old/02-architecture/tech-stack.md`. That document contains the full stack, rejected alternatives, and justifications. Technology preferences from the original SRS (React Flow, framer-motion, RabbitMQ, MSAL) were evaluated and addressed there.

## Infrastructure

- **Production:** Azure Container Apps.
- **Local development:** Docker containers (all services).
- **Message queues / supporting services:** Docker containers locally; Azure SaaS equivalents in production.
- **Database backup/retention:** Handled by a separate infrastructure department directly in Azure. Not an application-level concern.

## Timeline

- **MVP target:** No fixed date.
- **Release strategy:** Full application delivered as one release. No phased feature rollout.
- **Milestones:** Development split into milestones for demarcation. Milestone planning done after architecture is defined (using the Milestone Planner specialist).

## Budget

- No application-level budget constraints documented. Azure resource costs managed by infrastructure team.

## Assumptions

1. All users have modern browsers — Microsoft Edge or Firefox, latest 2 versions.
2. Users are primarily on a stable office network (connections generally reliable).
3. Azure AD tenant is pre-configured with correct app registrations and group assignments.
4. Role assignment (Reviewer, Admin) is managed by IT administrators in Azure AD, not within the application.
5. Azure OpenAI models are provisioned and accessible from the application's Azure environment.
6. Email service is available for notification delivery and monitoring alerts.
7. Mobile users accept read-only board functionality; primary usage is desktop.

## Dependencies

| Dependency | Type | Risk |
|-----------|------|------|
| Azure AD (authentication, user directory, roles) | Required | Application non-functional without it. Auth bypass covers local development only. |
| Azure OpenAI (AI processing) | Required | All AI features unavailable if service is down. Error handling with retry mitigates transient failures. |
| Email Service | Required | Notification emails and monitoring alerts unavailable if down. In-app notifications still function. |
| Azure Container Apps | Required (production) | Application cannot be deployed to production without it. |
| Docker | Required (development) | Local development environment depends on Docker for all services. |
