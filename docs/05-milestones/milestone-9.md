# Milestone 9: BRD & PDF Generation

## Overview
- **Execution order:** 9 (runs after M8)
- **Estimated stories:** 9
- **Dependencies:** M8
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-4.1 | BRD Generation | P1 | features.md FA-4 |
| F-4.2 | No Information Fabrication | P1 | features.md FA-4 |
| F-4.3 | BRD Generation Trigger | P1 | features.md FA-4 |
| F-4.4 | Per-Section Editing & Lock | P1 | features.md FA-4 |
| F-4.5 | Review Tab (right panel) | P1 | features.md FA-4 |
| F-4.7 | Document Versioning (partial — PDF gen) | P1 | features.md FA-4 |
| F-4.8 | Document Readiness Evaluation | P1 | features.md FA-4 |
| F-4.9 | Allow Information Gaps Toggle | P1 | features.md FA-4 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| brd_drafts | INSERT, SELECT, UPDATE | All section columns, section_locks, allow_information_gaps, readiness_evaluation | data-model.md |
| brd_versions | INSERT, SELECT | All section columns, pdf_file_path, version_number | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/brd | GET | Get BRD draft | Bearer | api-design.md |
| /api/ideas/:id/brd | PATCH | Update BRD sections, locks, gaps toggle | Bearer | api-design.md |
| /api/ideas/:id/brd/generate | POST | Trigger BRD generation (full/selective) | Bearer | api-design.md |
| /api/ideas/:id/brd/versions | GET | List BRD versions | Bearer | api-design.md |
| /api/ideas/:id/brd/versions/:versionId/pdf | GET | Download PDF | Bearer | api-design.md |
| TriggerBrdGeneration | gRPC | Trigger AI BRD generation | Internal | api-design.md (AI gRPC) |
| GeneratePdf | gRPC | Generate PDF from BRD content | Internal | api-design.md (PDF gRPC) |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Summarizing AI | 6-section BRD generation (3 modes) | agent-architecture.md S3.5 |

## Story Outline (Suggested Order)
1. **[Backend — AI]** Summarizing AI agent — full_generation, selective_regeneration, section_regeneration modes
2. **[Backend — AI]** BRD generation pipeline — context assembly (BRD-specific), fabrication validation (post-processing)
3. **[Backend — Core]** BRD draft REST API — GET draft, PATCH sections/locks/gaps toggle
4. **[Backend — PDF]** PDF generation service — WeasyPrint gRPC service, HTML template, PDF bytes return
5. **[Backend — Gateway]** BRD generation trigger — REST POST triggers gRPC to AI, AI publishes ai.brd.ready, gateway persists
6. **[Frontend]** Review tab UI — PDF preview (white background, scrollable), action bar (Download, Generate)
7. **[Frontend]** BRD section editor — expandable edit area, SectionField per section (label + lock icon + regenerate + textarea)
8. **[Frontend]** Readiness evaluation — progress indicator (segmented bar), per-section status, loading animation
9. **[Frontend]** Allow Information Gaps — toggle switch, /TODO markers in sections, PDF rejection if /TODO remains

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Summarizing AI | ~8,000 | agent-architecture.md (S3.5), system-prompts.md | 3-4 files | High | 3 modes, fabrication risk |
| 2 | BRD pipeline | ~6,000 | agent-architecture.md (S4.2), guardrails.md | 3-4 files | Medium | Fabrication validation |
| 3 | BRD draft API | ~5,000 | api-design.md (BRD), data-model.md (brd_drafts) | 4-5 files | Medium | Section lock logic |
| 4 | PDF service | ~5,000 | tech-stack.md (PDF Gen), api-design.md (PDF gRPC) | 4-6 files | Medium | WeasyPrint setup |
| 5 | BRD trigger | ~5,000 | api-design.md, agent-architecture.md (S4.2) | 3-4 files | Medium | Async event chain |
| 6 | Review tab UI | ~5,000 | page-layouts.md (S2, review tab), component-specs.md (S12) | 4-5 files | Medium | PDF embed, download |
| 7 | BRD editor | ~6,000 | component-specs.md (S12.2), features.md (F-4.4) | 4-5 files | Medium | Slide-in editor, lock toggle |
| 8 | Readiness evaluation | ~4,000 | component-specs.md (S12.3), features.md (F-4.8) | 2-3 files | Low | — |
| 9 | Information gaps | ~4,000 | features.md (F-4.9) | 2-3 files | Medium | /TODO marker handling |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~48,000
- **Cumulative domain size:** Large (Summarizing AI + BRD CRUD + PDF service + Review tab UI)
- **Information loss risk:** Medium (5)
- **Context saturation risk:** Low-Medium
- **Heavy stories:** 1 (Summarizing AI agent)

## Milestone Acceptance Criteria
- [ ] Summarizing AI generates 6-section BRD from idea state
- [ ] AI never fabricates information — insufficient sections show "Not enough information"
- [ ] BRD generates on first Review tab open and on manual trigger
- [ ] Sections editable with auto-lock on edit
- [ ] Locked sections excluded from AI regeneration
- [ ] Selective regeneration only regenerates unlocked sections
- [ ] PDF generated from BRD content via WeasyPrint
- [ ] PDF downloadable from Review tab
- [ ] Progress indicator shows per-section readiness
- [ ] Allow Information Gaps toggle enables /TODO markers
- [ ] PDF generation rejected if /TODO markers remain
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M8

## Notes
- BRD versioning (immutable snapshots on submit) is implemented in M10 (Review Workflow) as part of the submit flow.
- The Review tab is the right-panel tab in the workspace. The review section (below fold) comes in M10.
- PDF storage: local Docker volume in dev, Azure Blob in production. Storage path configured via env vars.
