# Milestone 7: BRD Generation & Review Tab

## Overview
- **Wave:** 4
- **Estimated stories:** 8
- **Must complete before starting:** M6
- **Can run parallel with:** M8, M12
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-4.1 | BRD Generation (6 sections) | P1 | features.md |
| F-4.2 | No Fabrication (guardrails) | P1 | features.md |
| F-4.3 | Section Locking | P1 | features.md |
| F-4.4 | Allow Information Gaps (/TODO) | P1 | features.md |
| F-4.7 | PDF Generation (WeasyPrint) | P1 | features.md |
| F-4.8 | Readiness Evaluation | P1 | features.md |
| F-4.9 | Regeneration Instruction | P1 | features.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| brd_drafts | CRUD | idea_id, section_short_description through section_success_criteria, section_locks, allow_info_gaps, readiness_evaluation | data-model.md |
| brd_versions | CREATE, READ | idea_id, version_number, sections snapshot, submitted_by, pdf_file_path | data-model.md |
| ideas | READ, UPDATE | state, has_been_submitted | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| GET /api/ideas/:id/brd | GET | Get current BRD draft | User | api-design.md |
| PATCH /api/ideas/:id/brd | PATCH | Update BRD section content | User (owner/collaborator) | api-design.md |
| POST /api/ideas/:id/brd/generate | POST | Trigger BRD generation | User | api-design.md |
| POST /api/ideas/:id/brd/regenerate | POST | Trigger selective regeneration | User | api-design.md |
| PATCH /api/ideas/:id/brd/locks | PATCH | Update section locks | User | api-design.md |
| PATCH /api/ideas/:id/brd/settings | PATCH | Toggle allow_info_gaps | User | api-design.md |
| GET /api/ideas/:id/brd/versions | GET | List BRD versions | User | api-design.md |
| GET /api/ideas/:id/brd/versions/:versionId | GET | Get specific version | User | api-design.md |
| GET /api/ideas/:id/brd/versions/:versionId/pdf | GET | Download PDF | User | api-design.md |
| gRPC TriggerBrdGeneration | gRPC | AI service: generate BRD | Internal (gateway → ai) | api-design.md |
| gRPC GeneratePdf | gRPC | PDF service: HTML → PDF | Internal (gateway → pdf) | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Summarizing AI | BRD generation (3 modes: full, selective, section) | agent-architecture.md §3.5 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| PDFPreview | Feature | component-inventory.md |
| BRDSectionEditor | Feature | component-inventory.md |
| SectionField | Feature | component-inventory.md |
| ProgressIndicator | Feature | component-inventory.md |
| SubmitArea | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend] Summarizing AI agent** — SummarizingAgent(BaseAgent): 3 modes per agent-architecture.md §3.5. full_generation: generate all 6 sections from full idea state. selective_regeneration: regenerate only unlocked sections, preserve locked. section_regeneration: regenerate one specific section. Input: chat history (summary + recent), board state (titles + content, no positions), company context findings (if any in chat), current draft (for selective/section modes), locked section list, optional instruction text (F-4.9). Output: 6-section BRD (or subset) with content or explicit "Not enough information" / `/TODO` markers. Default model tier.
2. **[Backend] Fabrication validation** — Post-processing pipeline per agent-architecture.md §4.2 Step 3. Keyword extraction from generated sections. Fuzzy match against chat messages + board content. Proper noun check: extract names/terms, verify against source material. Section length proportionality check. Flag sections with potential fabrication (warning indicators, not blocking). Results included in readiness evaluation.
3. **[API] BRD draft REST API** — GET /api/ideas/:id/brd: return current draft (all 6 sections + locks + settings + readiness). PATCH sections: update individual section content → auto-lock that section. PATCH locks: explicitly toggle section locks. PATCH settings: toggle allow_info_gaps. POST generate: trigger full BRD generation via gRPC TriggerBrdGeneration. POST regenerate: trigger selective regeneration with optional instruction text and target section. Ensure brd_drafts row created lazily on first access per idea.
4. **[Frontend] Review tab UI** — Replace M2 Review tab placeholder. PDFPreview component: white background document-style preview of BRD content, scrollable. Expandable BRDSectionEditor: slide-in from right when section clicked. SectionField per section: section label, lock toggle icon, regenerate button (per-section), Textarea for content editing. Auto-grow textareas. BRD content rendered as formatted text in preview mode, editable in editor mode.
5. **[Frontend+API] Section locks + readiness evaluation** — ProgressIndicator: segmented bar showing per-section readiness status (sufficient/insufficient/locked). Section lock behavior: manual lock via lock icon, auto-lock on user edit. Locked sections excluded from regeneration. Readiness evaluation: returned by AI as part of BRD generation (per-section sufficiency judgment), displayed as color-coded segments (green=sufficient, yellow=needs-work, gray=locked). Re-evaluate on regeneration.
6. **[Frontend+API] Allow Information Gaps + /TODO markers** — Toggle in Review tab settings. When enabled: AI may output `/TODO: [description]` markers instead of fabricating content. /TODO markers highlighted in yellow in editable fields. PDF generation rejected if any /TODO markers remain (validation check). Error toast lists sections with remaining markers. User fills gaps by editing sections (which auto-locks them). /TODO cleared when user replaces content.
7. **[Backend] PDF generation service** — Implement PDF gRPC service using WeasyPrint. Input: BRD section content (HTML-formatted). Output: PDF bytes. HTML template: professional layout with Commerz Real branding, section headers, page numbers, generation date. Storage: dev = local Docker volume (PDF_STORAGE_PATH), prod = Azure Blob Storage. Gateway receives PDF bytes, stores, saves path in brd_versions.pdf_file_path. Download endpoint streams file from storage.
8. **[API+Frontend] Document versioning** — brd_versions table: create immutable snapshot on submit (M9 calls this) or on manual "Save Version" action. Version includes: all 6 section contents, version_number (auto-increment per idea), submitted_by, submission_message, pdf_file_path. Version list endpoint: GET /api/ideas/:id/brd/versions. Version comparison: frontend shows version list, click to view any version's content. PDF download per version.

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| All UI Primitives | Available | M1 |
| Workspace page shell + Review tab | Available | M2 |
| AI service scaffold | Available | M6 |

## File Ownership (for parallel milestones)
This milestone owns these directories/files exclusively:
- `services/ai/agents/summarizing_ai/`
- `services/ai/processing/fabrication_validator.py`
- `services/ai/processing/version_tracker.py`
- `services/pdf/` (implementation of stub from M1)
- `frontend/src/features/brd/`
- `services/gateway/apps/brd/`
- `services/core/apps/brd/`

Shared files (merge-conflict-aware — keep changes additive):
- `frontend/src/pages/IdeaWorkspace/` (replace Review tab placeholder)
- `proto/ai.proto` (implement TriggerBrdGeneration)
- `proto/pdf.proto` (implement GeneratePdf)

## Milestone Acceptance Criteria
- [ ] BRD generates all 6 sections from idea state
- [ ] Three generation modes work: full, selective, section
- [ ] Fabrication validation detects and flags potential fabrications
- [ ] Section editing works with auto-lock behavior
- [ ] Manual lock/unlock toggles work
- [ ] Readiness evaluation shows per-section sufficiency
- [ ] Allow Information Gaps toggle enables /TODO markers
- [ ] /TODO markers highlighted in editor, block PDF generation
- [ ] PDF generates with correct formatting and branding
- [ ] PDF download works from version list
- [ ] Document versions are immutable snapshots
- [ ] Version history accessible and browsable
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M6

## Notes
- **Stub: Submit button** — SubmitArea component renders in Review tab but submit button is disabled with tooltip "Submit for review coming in next update". Full submit flow (state transition, reviewer assignment, brainstorming lock) implemented in M9.
- **Stub: Reviewer assignment selector** — Hidden in SubmitArea. Reviewer selection UI implemented in M9.
- **Stub: Review section below fold** — Empty state placeholder "Review timeline available after submission". Full review timeline in M9.
- **Stub: Notification for BRD/PDF events** — BRD generation and PDF completion show toast-only (success/error). No persistent notifications dispatched. Wired in M10.
- **Stub: Company context findings in BRD input** — Summarizing AI receives company context findings from chat delegation results (if any delegation messages exist in chat history). If no delegations occurred, this input is empty. Context Agent delegation itself is in M12.
