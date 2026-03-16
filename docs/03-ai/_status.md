# AI Engineer — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-02
- **Last updated:** 2026-03-16 (Refactored for requirements assembly platform)

## Input Consumed
- docs/01-requirements/vision.md
- docs/01-requirements/user-roles.md
- docs/01-requirements/features.md
- docs/01-requirements/pages.md
- docs/01-requirements/data-entities.md
- docs/01-requirements/nonfunctional.md
- docs/01-requirements/constraints.md
- docs/01-requirements/traceability.md
- docs/02-architecture/tech-stack.md
- docs/02-architecture/data-model.md
- docs/02-architecture/api-design.md
- docs/02-architecture/project-structure.md
- docs/02-architecture/testing-strategy.md
- REFACTORING_PLAN.md

## Major Refactoring (2026-03-16)

Platform pivot: Brainstorming tool → Requirements assembly platform

### Key Changes
- **Agent count:** 9 agents → 5 agents
  - Removed: Board Agent, Keyword Agent, Deep Comparison, Merge Synthesizer
  - Retained: Facilitator, Context Agent, Context Extension, Summarizing AI, Context Compression
- **Facilitator identity:** "Brainstorming facilitator" → "Requirements assistant"
- **Facilitator tools:** 6 tools (changed)
  - Removed: `request_board_changes`
  - Added: `update_requirements_structure`
  - Retained: send_chat_message (no more board references), react_to_message, update_title, delegate_to_context_agent, delegate_to_context_extension
- **Project types:** Software (Epics/User Stories) vs Non-Software (Milestones/Work Packages)
- **Context:** Board state → Requirements structure (hierarchical JSON)
- **Document generation:** Flat 6-section BRD → Hierarchical requirements document (structure varies by project type)
- **Admin context:** Now supports context_type: global / software / non_software
- **Cost reduction:** ~$2.04/project → ~$1.56/project (23.5% savings from removing 4 agents)

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Agent Architecture | complete | 2026-03-16 (refactored) |
| 2 | System Prompts | complete | 2026-03-16 (refactored) |
| 3 | Tools & Function Definitions | complete | 2026-03-16 (refactored) |
| 4 | Model Configuration & Optimization | complete | 2026-03-16 (refactored) |
| 5 | Guardrails & Safety | pending | (requires update for refactoring) |
| 6 | Architecture Sync & Handoff | pending | (gap analysis needed after refactoring) |

## Deliverables
| File | Description |
|------|-------------|
| agent-architecture.md | 5 agents (down from 9), 2 pipelines (down from 4), Semantic Kernel orchestration, context management, RAG (no similarity), failure handling, full internal directory structure |
| system-prompts.md | Production-ready XML-structured prompts for all 5 agents with runtime variables, example interactions, project_type awareness, requirements structuring guidance |
| tools-and-functions.md | Exact JSON schemas for 6 Facilitator tools (down from 14 total tools). New: update_requirements_structure tool with mutations for epics/stories/milestones/packages. Removed: 8 Board Agent tools, request_board_changes |
| model-config.md | Model selection per agent, generation parameters, token budgets, cost projections (~$1.56/project, ~$15.6K/month at peak), prompt caching (~27% savings), model routing, timeout/retry config, monitoring metrics |
| guardrails.md | (needs update — current version still references board, similarity, merge) |

## Removed Functionality

### Agents Eliminated
1. **Board Agent** (8 tools)
   - create_node, update_node, delete_node, move_node, resize_group
   - create_connection, update_connection, delete_connection
   - Reason: Board/canvas UI removed entirely
2. **Keyword Agent**
   - Extracted abstract keywords for similarity detection
   - Reason: Similarity/merge system removed
3. **Deep Comparison Agent**
   - Confirmed similarity between project pairs
   - Reason: Similarity/merge system removed
4. **Merge Synthesizer Agent**
   - Combined two projects into merged project
   - Reason: Merge functionality removed

### Pipelines Eliminated
- **Pipeline 3:** Deep Comparison (similarity detection)
- **Pipeline 4:** Merge Synthesis

### Data Removed
- `idea_embeddings` table (similarity vectors)
- `idea_keywords` column (keyword arrays)
- Board state from context (board_nodes, board_connections)

### Admin Parameters Removed
- `max_keywords_per_idea` — Keyword system eliminated
- `similarity_vector_threshold` — Similarity system eliminated

## Architecture Sync Gaps (Refactoring)

These gaps are **new** and specific to the refactoring. They need to be reconciled with the architecture.

### Gap 1: Terminology Updates Throughout Architecture
- **Source:** All refactored AI docs
- **Issue:** AI docs now use "project" terminology (project_id, project_type, project metadata). Architecture still uses "idea" terminology (idea_id, ideas table, GetIdeaContext).
- **Resolution:** Either update architecture to use "project" terminology, or maintain "idea" internally and translate at AI service boundary.

### Gap 2: New gRPC Method — `GetProjectContext` with project_type
- **Source:** agent-architecture.md Section 4.1, Section 5.1
- **Issue:** AI service now needs `project_type` field from Core gRPC. Current `GetIdeaContext` doesn't include this field (it's a new field in the refactored schema).
- **Resolution:** Add `project_type` enum field to `GetIdeaContext` response in `proto/core.proto` and api-design.md.

### Gap 3: Requirements Structure Field in Projects Table
- **Source:** agent-architecture.md Section 9.2
- **Issue:** AI docs reference `requirements_structure` field (hierarchical JSON) in projects table. This is new — old design had board_nodes/connections tables.
- **Resolution:** Confirm data model includes `requirements_structure` JSONB field in projects table. If not, add to data-model.md.

### Gap 4: Requirements Document Drafts Table Renamed
- **Source:** agent-architecture.md Section 9.2
- **Issue:** AI docs reference `requirements_document_drafts` table (renamed from `brd_drafts`).
- **Resolution:** Confirm rename in data-model.md, or clarify that AI docs should still reference `brd_drafts`.

### Gap 5: Context Bucket context_type Field
- **Source:** agent-architecture.md Section 6.4
- **Issue:** Facilitator context bucket now needs `context_type` enum (global / software / non_software). Old design had single bucket.
- **Resolution:** Add `context_type` field to `facilitator_context_bucket` table schema in data-model.md.

### Gap 6: New Event — `ai.requirements.updated`
- **Source:** agent-architecture.md Section 4.1 Step 4
- **Issue:** New event type for requirements structure mutations (replaces `ai.board.updated`).
- **Resolution:** Add to api-design.md "Events Published by AI Service" table with payload: `{ project_id, mutation_type, item_type, item_id, timestamp }`.

### Gap 7: Removed Events
- **Source:** agent-architecture.md (removed pipelines)
- **Issue:** These events no longer published:
  - `similarity.detected` — similarity detection removed
  - `ai.similarity.confirmed` — deep comparison removed
  - `merge.request.resolved` consumption — merge removed
  - `ai.merge.synthesized` — merge synthesis removed
  - `ai.keywords.updated` — keyword agent removed
  - `ai.board.updated` — board agent removed
- **Resolution:** Remove from api-design.md event contracts.

### Gap 8: update_requirements_structure Tool Validation
- **Source:** tools-and-functions.md Section 6
- **Issue:** New tool `update_requirements_structure` has complex validation (project_type matching, item locking, hierarchical constraints). Core service gRPC needs to support these validations.
- **Resolution:** Ensure Core service validates mutation operations and returns appropriate errors. Document gRPC method contract in api-design.md.

## Key Decisions (Refactoring)
| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Remove Board Agent entirely | Board/canvas UI eliminated — no spatial reasoning needed |
| 2 | Remove similarity/merge system (3 agents) | Similarity detection and merge functionality eliminated from requirements |
| 3 | Add update_requirements_structure tool | Replaces board mutations with hierarchical requirements mutations (epics/stories or milestones/packages) |
| 4 | Project type awareness in all agents | Software vs Non-Software have different structures and terminology |
| 5 | Context bucket split by project type | Different guidance needed for software vs non-software projects |
| 6 | Hierarchical requirements document | Replaces flat 6-section BRD with structured epics/stories or milestones/packages |
| 7 | Retain 5 core agents only | Facilitator (requirements assistant), Context Agent, Context Extension, Summarizing AI, Context Compression — minimum viable set |

## Architecture Additions (Post-Refactoring)

Changes introduced by the refactoring that extend the existing design:

### New/Modified Environment Variables
(No changes — same 7 environment variables)

### New/Modified Admin Parameters
| Parameter | Change | Integrated In |
|-----------|--------|---------------|
| `max_keywords_per_idea` | REMOVED | Gap — needs removal from data-model.md |
| `similarity_vector_threshold` | REMOVED | Gap — needs removal from data-model.md |

### New gRPC Methods/Fields Needed
| Method/Field | Purpose | Integrated In |
|--------------|---------|---------------|
| `project_type` field in `GetIdeaContext` | Distinguish software vs non-software | Gap — needs integration (api-design.md, core.proto) |
| `requirements_structure` field access | Read hierarchical structure | Gap — confirm in GetIdeaContext response |
| Mutation validation in Core | Validate update_requirements_structure operations | Gap — needs Core service implementation |

### New Broker Events
| Event | Change | Integrated In |
|-------|--------|---------------|
| `ai.requirements.updated` | NEW (replaces ai.board.updated) | Gap — needs integration (api-design.md) |
| `ai.board.updated` | REMOVED | Gap — needs removal (api-design.md) |
| `ai.keywords.updated` | REMOVED | Gap — needs removal (api-design.md) |
| `similarity.detected` | REMOVED | Gap — needs removal (api-design.md) |
| `ai.similarity.confirmed` | REMOVED | Gap — needs removal (api-design.md) |
| `ai.merge.synthesized` | REMOVED | Gap — needs removal (api-design.md) |

### Database Schema Changes
| Change | Purpose | Integrated In |
|--------|---------|---------------|
| `facilitator_context_bucket.context_type` field | Support global/software/non_software context | Gap — needs integration (data-model.md) |
| `requirements_structure` field in projects | Store hierarchical JSON | Gap — confirm in data-model.md |
| `requirements_document_drafts` rename | Terminology alignment | Gap — confirm in data-model.md |
| `idea_embeddings` table | REMOVED | Gap — needs removal (data-model.md) |
| `idea_keywords` column | REMOVED | Gap — needs removal (data-model.md) |

## Cost Impact (Refactoring)

| Metric | Previous Design | Current Design | Change |
|--------|----------------|----------------|--------|
| Agents | 9 | 5 | -4 agents (-44%) |
| Tools | 14 (6 Facilitator + 8 Board) | 6 (Facilitator only) | -8 tools (-57%) |
| Per-message cost | ~$0.064 | ~$0.048 | -$0.016 (-25%) |
| Per-project cost | ~$2.04 | ~$1.56 | -$0.48 (-23.5%) |
| Monthly cost (peak) | ~$20,400 | ~$15,600 | -$4,800 (-23.5%) |
| With prompt caching | ~$14,700 | ~$11,235 | -$3,465 (-23.5%) |

**Primary savings drivers:**
1. Board Agent removal (was 50% trigger rate, $0.015/message)
2. Keyword Agent removal (was 100% trigger rate, $0.001/message)
3. Similarity/merge pipelines removal (background costs)

## Handoff
- **Ready:** Partial (4/5 files refactored)
- **Remaining work:**
  - Update guardrails.md for refactoring (remove board/similarity/merge references)
  - Gap analysis with architecture team (8 gaps identified)
- **Next specialist(s):** Arch+AI Integrator (`/arch_ai_integrator`) — 8 gaps found requiring reconciliation
- **Files produced (refactored):**
  - docs/03-ai/agent-architecture.md
  - docs/03-ai/system-prompts.md
  - docs/03-ai/tools-and-functions.md
  - docs/03-ai/model-config.md
- **Files pending:**
  - docs/03-ai/guardrails.md (needs refactoring)
- **Required input for next specialist:**
  - All files in docs/02-architecture/ and docs/03-ai/
  - Architecture Sync Gaps list (in this _status.md)
  - REFACTORING_PLAN.md
- **Briefing for next specialist:**
  - Major refactoring: 9 agents → 5 agents (removed board, similarity, merge functionality)
  - New requirements structure tool with hierarchical mutations (epics/stories, milestones/packages)
  - Project type awareness (software vs non-software) throughout AI system
  - 23.5% cost reduction (~$4,800/month at peak)
  - 8 architecture sync gaps identified (terminology, new fields, event changes, table changes)
  - guardrails.md still needs update to reflect refactoring
- **Open questions:**
  - Should architecture adopt "project" terminology or keep "idea" with translation layer?
  - Confirm requirements_structure JSONB field location (projects table or separate table)?
  - Confirm brd_drafts → requirements_document_drafts rename is desired
