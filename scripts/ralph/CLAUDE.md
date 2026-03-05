# Ralph Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the context bundle at `scripts/ralph/context.md` — this contains all upstream specs, test definitions, codebase patterns, and file snapshots relevant to this milestone. This is your primary reference.
2. Read the PRD at `scripts/ralph/prd.json`
3. Read the progress log at `scripts/ralph/progress.txt` (check Codebase Patterns section first)
4. Pick the **highest priority** user story where `passes: false`
5. **If the story has test specs** (check the story's `notes` field for `Testing:` references and the Test Specifications section in `context.md`):
   - a. Write the tests first, based on the test specifications in the context bundle
   - b. Run the tests — verify they fail (they should, since the feature doesn't exist yet). If they pass trivially, the tests are too weak — rewrite them.
   - c. Implement the feature until the tests pass
   - d. Run full quality checks (see Quality Checks section below)
6. **If the story has NO test specs** (scaffolding, config, or stories without test-matrix entries):
   - a. Implement the feature
   - b. Write tests for the implementation
   - c. Run quality checks (see Quality Checks section below)
7. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
8. Update the PRD JSON to set `passes: true` for the completed story
9. Append your progress to `scripts/ralph/progress.txt`

**Note:** The pipeline has already checked out the correct branch for you. Do NOT switch branches.

## File Ownership

You own all project files. Only modify files relevant to your current user story.

## Quality Checks

Run these checks before committing. ALL must pass:

```bash
# Default checks — the pipeline configurator replaces these with project-specific commands
# Tests run inside Docker containers to guarantee a defined environment.
# The compose file (e.g., docker-compose.test.yml) bind-mounts your code,
# so changes are visible immediately without rebuilding images.
docker compose -f docker-compose.test.yml run --rm test-app pytest   # Tests — MANDATORY
docker compose -f docker-compose.test.yml run --rm test-app npx tsc --noEmit  # Typecheck (if applicable)
```

Do NOT commit broken code. If a check fails, fix the issue before committing.

**Tests run in Docker containers.** Your quality checks execute inside dev test containers defined in the project's test compose file. This guarantees a defined environment (correct Python/Node version, all dependencies installed) regardless of the host machine state. The compose file bind-mounts project source code, so your code changes are visible immediately — you do NOT need to rebuild images after editing files. Images are only rebuilt when dependency files change (requirements.txt, package.json, etc.) — the pipeline handles this automatically.

**Do NOT run tests on the host.** Never run `pytest`, `npm test`, or similar directly. Always use the configured Docker compose commands. The host machine has undefined state and tests will fail with missing dependencies.

**Tests are critical.** The pipeline runs the full test suite after merging each milestone. If your code breaks tests from previous milestones, the pipeline will reject the merge. Write tests for every feature you implement — they verify acceptance criteria and catch integration issues.

**Test-first when specs exist.** When your current story has test specifications in the context bundle (referenced in the story's `Testing:` notes), write those tests BEFORE implementing the feature. This is not optional — test-first development catches design problems early and produces tests that verify behavior rather than mirroring implementation. The cycle is: write tests → verify they fail → implement → verify they pass.

**Test-matrix reference:** Check your context bundle (`scripts/ralph/context.md`) for test specifications assigned to your current story. You MUST implement those tests. If the context bundle doesn't include test specs, check `docs/04-test-architecture/test-matrix.md` directly. Missing tests will be flagged as defects during QA.

**Test ID naming convention:** When implementing tests from the test matrix, include the test matrix ID in the test name or a comment on the test function. This enables automated coverage verification. Examples:
- Python: `def test_login_valid_credentials_T_1_2_01():` or `def test_login_valid_credentials():  # T-1.2.01`
- JavaScript: `it('login with valid credentials [T-1.2.01]', ...)` or `// T-1.2.01`
- Go: `func TestLoginValidCredentials_T_1_2_01(t *testing.T)`

The pipeline checks for these IDs after each milestone. Any test matrix ID not found in the codebase is flagged as a missing test defect.

## Context Bundle

The file `scripts/ralph/context.md` is pre-assembled by the PRD Writer with everything you need for this milestone:
- Architecture specs (data model, API endpoints, project structure) relevant to your stories
- Design specs (component specs, wireframes) relevant to your stories
- Test specifications assigned to your stories
- Codebase patterns learned from previous milestones
- Current contents of files you'll be modifying

**Read this file first** before exploring `docs/` directly. Only read original docs if the context bundle doesn't cover what you need.

## Progress Report Format

APPEND to `scripts/ralph/progress.txt` (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the evaluation panel is in component X")
---
```

The learnings section is critical — it helps future iterations avoid repeating mistakes and understand the codebase better.

## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the TOP of `scripts/ralph/progress.txt` (create it if it doesn't exist). This section should consolidate the most important learnings:

```
## Codebase Patterns
- Example: Use `sql<number>` template for aggregations
- Example: Always use `IF NOT EXISTS` for migrations
- Example: Export types from actions.ts for UI components
```

Only add patterns that are **general and reusable**, not story-specific details.

## Update CLAUDE.md Files

Before committing, check if any edited files have learnings worth preserving in nearby CLAUDE.md files:

1. **Identify directories with edited files** — look at which directories you modified
2. **Check for existing CLAUDE.md** — look for CLAUDE.md in those directories or parent directories
3. **Add valuable learnings** — if you discovered something future developers/agents should know:
   - API patterns or conventions specific to that module
   - Gotchas or non-obvious requirements
   - Dependencies between files
   - Testing approaches for that area
   - Configuration or environment requirements

**Do NOT modify `scripts/ralph/CLAUDE.md`** — that is your own instruction file managed by the pipeline. Only create or update CLAUDE.md files in project source directories.

**Examples of good CLAUDE.md additions:**
- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"

**Do NOT add:**
- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt

## Browser Testing (If Available)

For any story that changes UI, verify it works in the browser if you have browser testing tools configured (e.g., via MCP):

1. Navigate to the relevant page
2. Verify the UI changes work as expected
3. Take a screenshot if helpful for the progress log

If no browser tools are available, note in your progress report that manual browser verification is needed.

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

If ALL stories are complete and passing, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally (another iteration will pick up the next story).

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting
- Do NOT switch branches — the pipeline manages branches for you
