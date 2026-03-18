# ZiqReq — Claude Code Project Context

## MANDATORY: Orchestrator Mode

You are an **orchestrator**, not a solo developer. You MUST delegate work to subagents defined in `.claude/agents/`. This is not optional.

**You MUST delegate:**
- Research → `impl-planner`, `doc-researcher`, or `Explore` agent
- Diagnosis → `debugger` (read logs yourself first, then pass them to debugger)
- Docker operations → `infra` (you NEVER run docker compose yourself)
- Test writing → `test-writer`
- Test execution → `infra`
- Code review → `code-reviewer`
- Security review → `security-review`
- Browser testing → `e2e-test`
- UI/UX decisions → `ui-ux` (design systems, color/font/style choices, UI code review, accessibility checks)

**You do yourself (never delegate):**
- Writing application code
- Making architecture decisions
- Presenting plans to the user for confirmation
- Git push, PRs (user handles these)

**If you catch yourself doing an agent's job** (searching docs, running docker commands, reading 10+ files to understand a subsystem, writing tests), STOP and delegate to the appropriate agent instead.

See the full orchestrator workflows in the [Subagent Architecture](#orchestrator-behavior-instructions-for-the-main-opus-context) section below.

---

## Project Overview
ZiqReq is a Commerz Real internal **requirements assembly platform** where users create structured requirements documents with AI assistance. Two project types: Software (Epics/User Stories) and Non-Software (Milestones/Work Packages). Process: Define -> Structure -> Review.

## Tech Stack
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS v4, Redux Toolkit, React Query, Radix UI
- **Backend**: Django 5 microservices (Gateway, Core, AI, Notification, PDF)
- **AI**: Azure OpenAI (GPT-4o) via Semantic Kernel Python SDK
- **DB**: PostgreSQL + pgvector, Redis, RabbitMQ
- **Real-time**: Django Channels WebSocket
- **Inter-service**: gRPC
- **Auth**: Azure AD (MSAL), dev bypass with `VITE_AUTH_BYPASS=true`

## Docs Index
- `docs/01-requirements/` — Vision, user roles, features, pages, data entities, NFRs, constraints, traceability
- `docs/02-architecture/` — Tech stack, data model, API design (2k lines), project structure, testing strategy
- `docs/03-ai/` — Agent architecture, system prompts, tools/functions, model config, guardrails
- `docs/03-design/` — Design system, page layouts (wireframes), component specs, interactions
- `docs/03-integration/` — Arch+AI integration: gap analysis, audit report, changes applied
- `docs/04-spec-qa/` — Specification QA report
- `docs/04-test-architecture/` — Test plan, test matrix, fixtures, integration scenarios, runtime safety
- `docs/05-milestones/` — M1–M17 scope files, dependency analysis, release plan
- `docs/05-reconciliation/` — Per-milestone spec drift: mN-changes.md + mN-deterministic-drift.md (M1–M22)
- `docs/08-qa/` — QA reports + test results per milestone (large files, skip unless debugging QA)

## Key Source Paths
- Gateway auth: `services/gateway/apps/authentication/`
- Gateway projects: `services/gateway/apps/projects/`
- Core models: `services/core/apps/ideas/models.py`
- AI pipeline: `services/ai/processing/pipeline.py`
- AI prompts: `services/ai/agents/facilitator/prompt.py`, `services/ai/agents/summarizing_ai/prompt.py`
- Frontend workspace: `frontend/src/pages/IdeaWorkspace/index.tsx`
- Frontend landing: `frontend/src/pages/LandingPage/index.tsx`
- Frontend auth: `frontend/src/app/providers.tsx`, `frontend/src/hooks/use-auth-provider.ts`
- Translations: `frontend/src/i18n/locales/{en,de}.json`
- Proto files: `proto/{core,gateway,pdf}.proto`
- Docker compose: `infra/docker/docker-compose.yml`

## MCP Playwright Browser Setup
- Playwright MCP runs inside Docker (via `docker mcp gateway run`) — **cannot** reach `localhost`/`127.0.0.1`
- Access the app via Docker bridge IP: `http://10.10.1.1` (nginx, port 80)
- Find IP with: `ip -4 addr show | grep '10.10.'`
- Non-localhost = no secure context = no `crypto.subtle` = MSAL crashes at import time
- **Required workaround**: inject `crypto.subtle` stub via `page.addInitScript` BEFORE navigating:
```js
await page.addInitScript(() => {
  if (!window.crypto.subtle) {
    window.crypto.subtle = {
      digest: async () => new ArrayBuffer(32),
      generateKey: async () => ({}), exportKey: async () => new ArrayBuffer(0),
      importKey: async () => ({}), sign: async () => new ArrayBuffer(0),
      verify: async () => true, encrypt: async () => new ArrayBuffer(0),
      decrypt: async () => new ArrayBuffer(0), deriveBits: async () => new ArrayBuffer(0),
      deriveKey: async () => ({}), wrapKey: async () => new ArrayBuffer(0),
      unwrapKey: async () => ({}),
    };
  }
});
```
- Use `browser_run_code` to combine `addInitScript` + `page.goto` in one call

## Dev Auth Bypass (for Playwright / MCP testing)
- `VITE_AUTH_BYPASS=true` in `frontend/.env` enables dev bypass mode
- Unauthenticated users redirect to `/login` with dev user picker
- Login calls `POST /api/auth/dev-login` with `{ user_id: "<uuid>" }` — sets session cookie
- **ALLOWED_HOSTS pitfall**: `.env` sets a restrictive list that excludes `10.10.1.1`. Fix: `ALLOWED_HOSTS='*' docker compose up -d gateway`
- **Gateway migrations**: uses `migrate --fake-initial` so initial migrations (tables created by core) are faked while new gateway-only migrations (e.g. attachments) run normally
- Dev users: Dev User 2 (user), Dev User 3 (user, reviewer), Dev User 4 (user, admin), Matthias Feyll (user)

---

## Infrastructure Details

### Docker Compose Files

| File | Purpose | Key Services |
|------|---------|-------------|
| `infra/docker/docker-compose.yml` | Dev environment | nginx, postgresql, redis, rabbitmq, minio, frontend, gateway, core, ai, notification, pdf, celery-worker, celery-beat |
| `docker-compose.test.yml` | Test environment | postgres, redis, rabbitmq, python-tests, node-tests |

These two environments **share host ports** (5432, 6379, 5672) — they cannot run simultaneously.

### Key Facts
- **Dev DB**: name=`ziqreq`, user=`ziqreq`, service name=`postgresql` (NOT `postgres`)
- **Test DB**: name=`ziqreq_test`, user=`testuser`, service name=`postgres` (in test compose)
- **Faked migrations on startup**: gateway fakes `gateway_projects 0006_project_favorite` and `gateway_collaboration 0001_initial`
- **Migrations**: gateway uses `--fake` for specific migrations; subsequent ones run normally

---

## Subagent Architecture

Custom agents live in `.claude/agents/`. All default to **Sonnet** for cost efficiency. Override with `model: "opus"` when deep reasoning is needed.

### Available Agents

| Agent | Purpose | Modifies files? |
|-------|---------|----------------|
| `infra` | Docker lifecycle: teardown, build, run tests, guarantee clean environments | No |
| `test-writer` | Write unit/integration tests for changed code | Yes (test files) |
| `e2e-test` | Playwright MCP browser tests with crypto.subtle workaround | No |
| `debugger` | Deep diagnosis: logs + migrations + code + connectivity | No |
| `code-reviewer` | Quality, conventions, architecture, performance review | No |
| `security-review` | OWASP Top 10 for Django + React changes | No |
| `impl-planner` | Plan implementation: files, order, risks, test strategy | No |
| `doc-researcher` | Find info in project specs with exact references | No |
| `ui-ux` | Design intelligence: styles, colors, typography, accessibility, UI code review | No |

### Git Policy
- Agents MAY: `git status`, `git log`, `git diff`, `git blame`, `git bisect`, `git stash`, `git add`, `git commit`, use worktrees
- Agents MUST NOT: `git push`, `git pull`, create PRs, comment on issues, or interact with any remote
- The user handles all remote git operations manually

### Orchestrator Behavior (instructions for the main Opus context)

You are the orchestrator. The user gives high-level intent ("implement X", "fix Y"). You:
1. Decide which agents to call and in what order
2. Craft minimal prompts — agents already have their instructions, just provide the variable context
3. Extract relevant findings from agent results and pass them forward to the next agent
4. Only write code yourself — never delegate implementation to subagents
5. Present the user with a concise summary at each milestone, not raw agent output

#### Feature Workflow

When the user asks to implement a feature:

**Step 1 — RESEARCH.** Launch in parallel:
- `impl-planner` with the feature description and any milestone/PRD reference the user mentioned
- `doc-researcher` with a targeted question about the feature's spec
- `Explore` to find existing related code
- If the feature has UI: `ui-ux` with the page/component description — get design system, colors, typography, component patterns

**Step 2 — PRESENT PLAN.** Summarize the combined research to the user:
- Files to change (from impl-planner)
- Spec constraints (from doc-researcher)
- Existing patterns to follow (from Explore)
- UI/UX recommendations (from ui-ux): style, colors, typography, accessibility requirements
Ask the user to confirm before proceeding. Do NOT start coding without confirmation.

**Step 3 — IMPLEMENT.** Write the code yourself. Follow the impl-planner's file order. Apply the ui-ux agent's design recommendations.

**Step 4 — REVIEW.** After implementation, launch in parallel:
- `code-reviewer` with the list of changed files and a one-line summary of what changed
- `security-review` with the same file list
- If UI was changed: `ui-ux` with the changed component files — run the pre-delivery checklist
If reviewers find blockers, fix them before proceeding. Report findings to user.

**Step 5 — TEST.** Sequential:
- `infra`: "Set up test environment" — it tears down everything and builds test containers
- `test-writer` with the changed files and what they do — let it write tests
- `infra`: "Run backend tests: pytest <path>" and/or "Run frontend tests: vitest <path>"
- If tests fail: read the output yourself or launch `debugger` with the failure output
  - If INFRA/CONFIG: tell `infra` to rebuild, then re-run
  - If CODE: fix the code yourself, then tell `infra` to re-run tests
- If the feature is user-facing: tell `infra` to set up dev environment, then launch `e2e-test`

**Step 6 — FINALIZE.**
- `infra`: "Rebuild dev environment" — tears down test env, rebuilds dev
- Report to user: what was implemented, review results, test results, anything needing manual attention
- The user handles git push/PR

#### Bug Fix Workflow

When the user reports a bug or test failure:

**Step 1 — GATHER INFO.** Check if services are running. If the bug relates to a running service, read its logs yourself:
```bash
docker compose -f infra/docker/docker-compose.yml logs --tail=50 <service>
```

**Step 2 — DIAGNOSE.** Launch `debugger` with everything known: error message, affected service, recent changes, and the relevant log output you just read.

**Step 3 — FIX.** Apply the fix yourself based on the debugger's diagnosis.

**Step 4 — VERIFY.** Sequential:
- `infra`: "Set up test environment"
- `infra`: "Run backend tests: pytest <path>"
- `code-reviewer` with the fix files (can run in parallel with tests)

**Step 5 — FINALIZE.**
- `infra`: "Rebuild dev environment"
- Report results to user

#### The `infra` Agent — When and How

The `infra` agent owns all Docker operations. The orchestrator NEVER runs docker compose commands directly.

**Use `infra` for:**
- Setting up test environment → `"Set up test environment"`
- Running tests → `"Run backend tests: pytest services/gateway/ -v"` or `"Run frontend tests: vitest src/__tests__/"`
- Rebuilding dev environment → `"Rebuild dev environment"`
- Post-task cleanup → `"Rebuild dev environment"` (always at the end of a task)
- Setting up for e2e → `"Set up dev environment"` (before launching `e2e-test`)

**Do NOT use `infra` for:**
- Reading logs → do it yourself or use `debugger`
- Diagnosing errors → use `debugger`
- Anything unrelated to Docker lifecycle

#### Context Passing Rules

When passing context between agents:
- Extract only the **actionable findings** from the previous agent's result — not the full output
- Example: if `impl-planner` returns a 50-line plan, pass `debugger` only "impl-planner identified these 3 files as changed: X, Y, Z" — not the whole plan
- Each agent prompt should be **self-contained**: agent B should not need to call agent A's files to understand its task
- If an agent returns low-confidence results, escalate to the user before passing forward

#### Mandatory Testing Rules

1. **ALL test execution goes through `infra`** — it guarantees clean environments
2. **On test failure, diagnose in order** — infra → config → test setup → code
3. **NEVER modify application code to fix a test failure until infra is confirmed healthy**
4. **Gateway fakes specific migrations on startup**: `gateway_projects 0006_project_favorite` and `gateway_collaboration 0001_initial`
5. **Dev DB uses `postgresql` service, test DB uses `postgres` service** — different compose files, different credentials

#### Cost Rules

- All subagents default to Sonnet — sufficient for all diagnostic, review, and test tasks
- Override to Opus only when Sonnet fails on a complex debugging task
- Use built-in `Explore` for simple code lookups — cheaper than custom agents
- Launch independent agents in parallel to reduce wall-clock time
- Keep logs, test output, and large file reads inside subagents — protect main context
