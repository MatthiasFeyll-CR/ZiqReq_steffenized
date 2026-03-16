# Milestone 20: AI System Prompt Rework

## Overview
- **Execution order:** 20 (runs after M19)
- **Estimated stories:** 3
- **Dependencies:** M19
- **MVP:** Yes

## Purpose
Rewrite all AI agents to work with the new structured requirements model. The Facilitator becomes a requirements structuring assistant with type-specific behavior. The Summarizing AI generates hierarchical documents instead of flat BRDs. The AI pipeline is updated to handle requirements structure mutations.

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| R-4.1 | New Facilitator system prompt — project type aware | Critical | REFACTORING_PLAN.md Phase 4 |
| R-4.2 | New Summarizing AI — type-specific generation | Critical | REFACTORING_PLAN.md Phase 4 |
| R-4.3 | AI pipeline update — requirements mutations | Critical | REFACTORING_PLAN.md Phase 4 |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Facilitator | Rewrite as requirements structuring assistant with update_requirements_structure tool | Story 4.1 |
| Summarizing AI | Rewrite to generate structured JSON (Epics/Stories or Milestones/Packages) | Story 4.2 |
| AI Pipeline | Update context assembly, add mutation handler, remove board agent step | Story 4.3 |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| UpdateRequirementsStructure (gRPC) | RPC | Apply AI mutations to requirements draft | Internal | Story 4.3 |
| GetRequirementsState (gRPC) | RPC | Fetch current structure for context assembly | Internal | Story 4.3 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| (No new frontend components — AI changes are backend-only) | — | — |

## Story Outline (Suggested Order)
1. **[Backend] New Facilitator system prompt** — Rewrite `services/ai/agents/facilitator/prompt.py` with type-specific identity (software vs non-software). New conversation rules focused on structuring requirements (not brainstorming). Implement `update_requirements_structure` tool in plugins.py (replaces request_board_changes) — sends JSON mutations (add/update/remove epics, stories, milestones, packages, reorder). Remove board reference syntax from send_chat_message. Update build_system_prompt to accept project_type, inject current requirements structure JSON, combine global + type-specific facilitator bucket.
2. **[Backend] New Summarizing AI** — Rewrite `services/ai/agents/summarizing_ai/prompt.py` to generate structured JSON output. Software output: title, description, structure with epics containing stories (with acceptance criteria, priority). Non-software output: title, description, structure with milestones containing packages (with deliverables, dependencies). Support modes: full_generation, selective_regeneration, item_regeneration. Update readiness evaluation logic per type.
3. **[Backend] AI pipeline update** — Update `services/ai/processing/pipeline.py`: remove board agent invocation step, add requirements structure mutation handler (when Facilitator calls update_requirements_structure, apply mutations via gRPC, broadcast WebSocket event). Include current requirements JSON in context assembly (replacing board state). Include project_type in facilitator context. Add gRPC RPCs: UpdateRequirementsStructure, GetRequirementsState.

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | New Facilitator prompt | ~15,000 | AI specs, requirements model | ~5 files | High | High — core AI behavior change, new tool |
| 2 | New Summarizing AI | ~12,000 | AI specs, requirements model | ~3 files | High | Medium — output format change |
| 3 | AI pipeline update | ~10,000 | Architecture, AI specs | ~5 files | High | High — integrates all AI changes |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~37,000
- **Cumulative domain size:** Medium (focused on AI service)
- **Information loss risk:** Medium (score: 5) — all stories are cross-cutting within AI domain
- **Context saturation risk:** Low

## Milestone Acceptance Criteria
- [ ] Facilitator prompt uses type-specific identity and conversation rules
- [ ] update_requirements_structure tool works — AI can add/update/remove items in requirements structure
- [ ] Board references completely removed from all AI prompts and tools
- [ ] Summarizing AI generates correct JSON structure for software projects (Epics/Stories)
- [ ] Summarizing AI generates correct JSON structure for non-software projects (Milestones/Packages)
- [ ] All three generation modes work (full, selective, item)
- [ ] AI pipeline includes requirements structure and project_type in context
- [ ] Requirements mutations from AI broadcast via WebSocket to connected clients
- [ ] gRPC RPCs for requirements state management functional
- [ ] TypeScript typecheck passes
- [ ] No regressions on previous milestones

## Notes
- Story 1 is the most critical — the Facilitator is the primary user-facing AI agent.
- The update_requirements_structure tool mutation format must be carefully designed — it's how AI populates the requirements panel in real-time during chat.
- Story 3 depends on both Stories 1 and 2 being complete.
- The existing context_agent and context_extension delegation tools are kept — only terminology is updated (already done in M18 Story 2.4).
