
● Working With Your Subagent Workflow

  The Core Principle

  You are the orchestrator. You make decisions, agents do scoped work. Don't micromanage agents — give them clear context and let them work. Don't do what an agent should do — delegate to
   keep your main context clean.

  ---
  How to Prompt Agents

  Bad vs Good Prompts

  Bad — vague, no context:
  "Debug the gateway"

  Good — specific error, service, what you already know:
  "The gateway returns 500 on POST /api/projects/. Error from docker logs:
  IntegrityError: column 'attachment_type' does not exist.
  I suspect a faked migration on gateway_projects."

  Bad — too broad:
  "Review all the code"

  Good — scoped files, what changed, why:
  "Review these files for the new attachment upload feature:
  - services/gateway/apps/projects/models.py (added Attachment model)
  - services/gateway/apps/projects/views.py (added AttachmentViewSet)
  - services/gateway/apps/projects/serializers.py (added AttachmentSerializer)
  Focus on: access control, file upload validation, and N+1 queries."

  The Prompt Template

  Every agent prompt should have 3 parts:

  1. What — the task in one sentence
  2. Context — error output, file paths, what you already know
  3. Focus — what to pay attention to (optional, narrows scope)

  ---
  Workflow by Scenario

  Scenario 1: New Feature

  Step 1 — Research (parallel). Start every feature with this:

  You: I need to implement [feature]. Let me research first.

  → Agent(impl-planner): "Plan implementation for [feature].
     Milestone scope: docs/05-milestones/mN-scope.md
     Focus on: which files to change, dependency order, migration risks."

  → Agent(doc-researcher): "What does the spec say about [feature]?
     Check requirements in docs/01-requirements/ and API design
     in docs/02-architecture/03-api-design.md."

  Both run in parallel. Read their reports before writing any code.

  Step 2 — Implement. You write the code yourself in the main context. This is where Opus earns its cost — complex implementation decisions stay with you.

  Step 3 — Review (parallel). After committing:

  → Agent(code-reviewer): "Review these files: [list changed files].
     This implements [feature]. Check conventions and performance."

  → Agent(security-review): "Security review: [list changed files].
     New endpoint accepts file uploads via Minio."

  Step 4 — Test.

  → Agent(test-writer): "Write tests for [changed files].
     [Brief description of what the code does]."

  Then after tests are written:

  → Agent(test-runner): "Run pytest services/gateway/apps/projects/ -v"

  Step 5 — E2E (if user-facing).

  → Agent(e2e-test): "Test the attachment upload flow:
     1. Log in as Dev User 4
     2. Navigate to a project workspace
     3. Upload a file via the attachment button
     4. Verify the file appears in the attachment list"

  Scenario 2: Bug Fix

  Step 1 — Diagnose. Send the debugger everything you know:

  → Agent(debugger): "Gateway crashes on project creation since last commit.
     Error: 'relation projects_attachment does not exist'
     Started after commit abc123 which added the Attachment model.
     Gateway logs show the traceback on POST /api/projects/{id}/attachments/"

  The debugger will check infra/logs/migrations/code in order and return a diagnosis.

  Step 2 — Fix. You apply the fix based on the diagnosis.

  Step 3 — Verify.

  → Agent(test-runner): "Run the tests that were failing:
     pytest services/gateway/apps/projects/tests/test_attachments.py -v"

  Scenario 3: "Something is broken but I don't know what"

  Start broad, narrow down:

  → Agent(debugger): "The app shows a blank page after login.
     No obvious error in the browser. Started sometime today."

  The debugger will check services, logs, migrations, and connectivity. Its report tells you exactly where to look.

  ---
  Best Practices

  1. Don't chain agents when one will do

  If tests fail, don't call debugger after test-runner. The test-runner already triages. Only escalate to debugger if the triage says CODE and you need deeper analysis.

  2. Use Explore for quick lookups, custom agents for real work

  # Quick: "where is this function defined?"
  → Agent(Explore): "Find the ProjectSerializer class definition"

  # Real work: "plan how to add versioning to projects"
  → Agent(impl-planner): "Plan implementation for project versioning..."

  3. Parallel when independent, sequential when dependent

  # GOOD — parallel (no dependency)
  → Agent(code-reviewer): "Review models.py"
  → Agent(security-review): "Review views.py"

  # GOOD — sequential (triage needs failure output)
  → Agent(test-runner): "Run gateway tests"
  → [read result, see failure]
  → Agent(debugger): "Diagnose this: [paste failure from test-runner]"

  4. Keep your main context for decisions

  Don't read 500 lines of logs yourself. Don't manually check migration state. Don't grep through 20 files to understand a subsystem. That's what agents are for. Your main context is
  expensive (Opus) — use it for thinking, not gathering.

  5. Pass agent output forward

  When one agent's result feeds another, paste the relevant finding:

  → Agent(test-runner): "Run gateway tests"
    Result: "FAIL — Level 0 INFRA: relation 'projects_attachment' does not exist"

  → Agent(debugger): "test-runner reports missing table 'projects_attachment'.
     Likely faked migration on gateway_projects. Verify and provide fix commands."

  6. Trust the infra-first hierarchy

  When tests fail, your instinct will be to look at the code. Resist. Let test-runner triage first. 80% of the time in this project, it's infra.

  ---
  Quick Reference

  ┌───────────────────────────────────┬────────────────────┬───────────────┐
  │           I want to...            │       Agent        │     Model     │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Plan a feature                    │ impl-planner       │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Find what the spec says           │ doc-researcher     │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Find code in the codebase         │ Explore (built-in) │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Write code                        │ You (main context) │ Opus          │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Review code quality               │ code-reviewer      │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Check for security issues         │ security-review    │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Write tests                       │ test-writer        │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Run tests                         │ test-runner        │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Test in the browser               │ e2e-test           │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Diagnose a bug                    │ debugger           │ Sonnet        │
  ├───────────────────────────────────┼────────────────────┼───────────────┤
  │ Something is really hard to debug │ debugger           │ Opus override │
  └───────────────────────────────────┴────────────────────┴───────────────┘

✻ Cogitated for 42s