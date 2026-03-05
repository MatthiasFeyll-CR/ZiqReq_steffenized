# Milestone 7: Review & BRD Generation

## Overview
- **Execution order:** 7 (runs after M6)
- **Estimated stories:** 10
- **Dependencies:** M5 (AI service), M4 (board content)
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-4.1 | BRD Generation | Must-have | features.md |
| F-4.2 | No Information Fabrication | Must-have | features.md |
| F-4.3 | BRD Generation Trigger | Must-have | features.md |
| F-4.4 | Per-Section Editing & Lock | Must-have | features.md |
| F-4.5 | Review Tab | Must-have | features.md |
| F-4.7 | Document Versioning | Must-have | features.md |
| F-4.8 | Document Readiness Evaluation | Must-have | features.md |
| F-4.9 | Allow Information Gaps Toggle | Must-have | features.md |
| F-4.10 | Reviewer Assignment on Submit | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| brd_drafts | CREATE, READ, UPDATE | idea_id, section_*, section_locks, allow_information_gaps, readiness_evaluation, last_evaluated_at | data-model.md |
| brd_versions | CREATE, READ | idea_id, version_number, section_*, pdf_file_path, created_at | data-model.md |
| ideas | UPDATE (state → in_review) | state | data-model.md |
| review_assignments | CREATE | idea_id, reviewer_id, assigned_by='submitter' | data-model.md |
| review_timeline_entries | CREATE (resubmission) | idea_id, entry_type='resubmission', old_version_id, new_version_id | data-model.md |
| users | READ (reviewer search) | id, display_name, roles | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/brd | GET | Get BRD draft | Bearer/bypass | api-design.md |
| /api/ideas/:id/brd | PATCH | Update BRD sections, toggle locks | Bearer/bypass | api-design.md |
| /api/ideas/:id/brd/generate | POST | Trigger BRD generation (full/selective) | Bearer/bypass | api-design.md |
| /api/ideas/:id/brd/versions | GET | List BRD versions | Bearer/bypass | api-design.md |
| /api/ideas/:id/brd/versions/:vid/pdf | GET | Download PDF for version | Bearer/bypass | api-design.md |
| /api/ideas/:id/submit | POST | Submit idea for review | Bearer/bypass | api-design.md |
| /api/users/search | GET | Search users (for reviewer assignment) | Bearer/bypass | api-design.md |
| AI gRPC: TriggerBrdGeneration | gRPC | Gateway triggers BRD generation | Internal | api-design.md |
| PDF gRPC: GeneratePdf | gRPC | Generate PDF from BRD sections | Internal | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| ReviewTabPanel | Component (right panel tab) | page-layouts.md §4 |
| PdfPreview | Component | component-specs.md |
| BrdSectionEditor | Component | component-specs.md |
| SectionLockIndicator | Component | component-specs.md |
| ReadinessIndicator | Component | component-specs.md |
| GapsToggle | Component | component-specs.md |
| RegenerateButton | Component | component-specs.md |
| InstructionTextField | Component | component-specs.md |
| SubmitControls | Component | component-specs.md |
| ReviewerSelect | Component | component-specs.md |

## AI Agent References

| Agent | Purpose | Source |
|-------|---------|--------|
| Summarizing AI | 6-section BRD generation (3 modes: full, selective, section) | agent-architecture.md §3.5 |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| PDF generation service (WeasyPrint) | Activated | M7 (scaffold from M1) |
| Fabrication validator (post-processing, non-AI keyword matching + source cross-ref) | New | M7 |
| ai.security.fabrication_flag event publishing | New | M7 |

## Story Outline (Suggested Order)

1. **[AI Service] Summarizing AI agent** — SummarizingAgent(BaseAgent). 3 modes: full_generation (all 6 sections), selective_regeneration (unlocked sections only), section_regeneration (single section with instruction). System prompt includes mode-specific sections. No fabrication: sections output "Not enough information" when data insufficient. Allow Information Gaps mode: leave /TODO markers instead of skipping.
2. **[AI Service] Fabrication validation (post-processing)** — Non-AI post-processing of BRD output. Keyword extraction from generated sections. Fuzzy match against chat messages + board content. Proper noun check against source material. Section length proportionality check. Flag sections with potential fabrication (warning indicators, not blocking).
3. **[AI Service] BRD readiness evaluation** — Part of Summarizing AI output. Per-section readiness check: Current Workflow (≥1 workflow + ≥1 pain point), Affected Department (≥1 area), Core Capabilities (≥1 action), Success Criteria (≥1 measurable outcome). Combined AI judgment + minimum anchors. Output: per-section ready/insufficient status.
4. **[Backend] BRD draft + versioning APIs** — Gateway REST: GET /api/ideas/:id/brd (draft), PATCH (update sections, toggle locks, toggle gaps). POST /api/ideas/:id/brd/generate (trigger AI generation, mode param). GET /api/ideas/:id/brd/versions (list). Core gRPC servicers for BRD CRUD. On generation complete: persist draft via Core, publish ai.brd.ready event.
5. **[Backend] PDF generation service** — Activate PDF service from M1 scaffold. WeasyPrint gRPC service: receives BRD section content → renders HTML template → returns PDF bytes. Gateway uploads to storage (local volume / Azure Blob). Filename: BRD_{date}_{idea_title_slug}.pdf.
6. **[Backend] Submit for review** — POST /api/ideas/:id/submit: validate BRD completeness (no /TODO if gaps not allowed, readiness check), snapshot brd_draft → brd_versions (immutable), generate PDF, transition idea state to in_review, create review_assignments if reviewers specified, create resubmission timeline entry (for resubmits), publish idea.submitted event. Optional submit message becomes first timeline comment.
7. **[Frontend] Review tab — BRD generation + PDF preview** — Review tab in right panel. First open triggers BRD generation (loading animation). PDF preview with three-dot menu (Download). Regenerate button. Generation status indicators.
8. **[Frontend] Review tab — section editing + locks** — Expandable edit area (slides left, overlaps chat). All 6 BRD sections as editable text fields. Lock/unlock indicator icon per section (auto-locks on user edit, manually toggleable). Selective regeneration button (unlocked sections only) with optional instruction text field. AI text regeneration chains into PDF regeneration. Undo/redo for AI text changes (local).
9. **[Frontend] Review tab — readiness + gaps + submit controls** — Readiness progress indicator (per-section status). Allow Information Gaps toggle: enables /TODO markers, greyed progress indicator with "gaps allowed". PDF generation rejected if /TODO markers remain (error lists which sections). Submit button with optional message text field and optional reviewer assignment (user search dropdown).
10. **[Backend + Frontend] Document version management** — GET /api/ideas/:id/brd/versions/:vid/pdf (download). Version list in review section. Resubmission entries in timeline link old and new versions (both downloadable). Preview always shows latest version.

## Milestone Acceptance Criteria
- [ ] Summarizing AI generates 6-section BRD from idea state
- [ ] "Not enough information" appears for insufficient sections
- [ ] Fabrication validation flags suspicious content (non-blocking warnings)
- [ ] BRD generation triggers on Review tab open and regenerate button
- [ ] Per-section editing works with auto-lock on edit and manual toggle
- [ ] Selective regeneration only regenerates unlocked sections
- [ ] Readiness evaluation shows per-section progress
- [ ] Allow Information Gaps: /TODO markers appear, PDF rejected if markers remain
- [ ] PDF generation produces valid downloadable PDFs
- [ ] Document versioning: immutable snapshots created on submit, previous versions downloadable
- [ ] Submit: state transitions to in_review, reviewers optionally assigned
- [ ] Resubmit: new version created, timeline entry links old and new versions
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M6

## Notes
- Review section (below fold) and review timeline come in M8. This milestone covers the Review tab (right panel) and submit flow only.
- Reviewer notification on submit is wired to publish the event, but notification delivery comes in M9.
- User search for reviewer assignment uses GET /api/users/search (searches by name).
- PDF template should match the BRD structure and Commerz Real branding.
- The expandable edit area overlaps the chat panel — z-index management needed.
