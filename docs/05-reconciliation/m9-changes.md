# Milestone 9 Spec Reconciliation

## Summary
- **Milestone:** M9 — BRD & PDF Generation
- **Date:** 2026-03-11
- **Total deviations found:** 7
- **Auto-applied (SMALL TECHNICAL):** 2
- **Applied (FEATURE DESIGN):** 1
- **Applied (LARGE TECHNICAL):** 4
- **Rejected:** 0

## Methodology

This reconciliation follows the **Deterministic Drift** pattern. The QA report noted "Deviations: None" against the M9 PRD, indicating the implementation matched the PRD specification. However, the M9 PRD itself contained evolved designs that differ from the original architecture docs, creating **deterministic drift** between PRD-to-implementation (aligned) and architecture-to-PRD (misaligned).

This reconciliation resolves that drift by updating architecture docs to match the M9 PRD and implementation reality.

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: pydyf version constraint | `docs/02-architecture/tech-stack.md` | Added pydyf dependency constraint: pydyf>=0.10,<0.12 (WeasyPrint 62.x compatibility — 0.12.x breaks Stream.transform) |
| 2 | D-002: libgdk-pixbuf package name | `docs/02-architecture/tech-stack.md` | Clarified Debian package naming: libgdk-pixbuf-2.0-0 (with hyphens, not underscores) for python:3.12-slim |

### FEATURE DESIGN (Applied with prominent changelog flag)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-003: Review tab visibility | `docs/03-design/component-specs.md` § 12.1<br>`docs/03-design/page-layouts.md` § 6 | **UX EVOLUTION:** Review tab visible for 'open' state (always visible during brainstorming), not just after first submission. Simplifies workflow — users can view/prepare BRD content before submitting. |

### LARGE TECHNICAL (Applied with prominent changelog flag)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-004: BRD API consolidation | `docs/02-architecture/api-design.md` § BRD endpoints | **API CONSOLIDATION:** Replaced POST /generate, /regenerate, /regenerate-section with single POST /api/ideas/:id/brd/generate {mode, section_name?} endpoint. Mode ∈ {full_generation, selective_regeneration, section_regeneration}. Reduces endpoint proliferation, matches ChatProcessing pattern. |
| 2 | D-005: PDF download implementation | `docs/02-architecture/api-design.md` § BRD endpoints | **IMPLEMENTATION CLARIFICATION:** PDF download uses `<object>` tag with blob URL from on-demand gRPC call to PDF service. No dedicated /generate-pdf REST endpoint in M9. Download button creates temporary `<a>` element with blob URL. |
| 3 | D-006: Fabrication validator details | `docs/03-ai/guardrails.md` § 5.2 Layer 4 | **IMPLEMENTATION DETAILS:** FabricationValidator uses Python stdlib difflib.SequenceMatcher for fuzzy matching, simple tokenization for keyword extraction. No AI models, no spaCy, no external NLP. Thresholds: _MATCH_THRESHOLD=0.75 (fuzzy match), _FLAG_RATIO_THRESHOLD=0.5 (section flagging). Lightweight heuristic for performance. |
| 4 | D-007: Event publishing pattern | `docs/02-architecture/api-design.md` § Event Contracts | **DUAL EVENT PATTERN:** BRD generation publishes (1) ai.brd.generated (main event: idea_id, mode, sections, readiness_evaluation, fabrication_flags) + (2) ai.security.fabrication_flag (per-section monitoring events). Decouples business logic from monitoring concerns. |

### REJECTED

None.

---

## Documents Modified

1. **docs/02-architecture/tech-stack.md**
   - Added pydyf version constraint: >=0.10,<0.12
   - Clarified libgdk-pixbuf Debian package name

2. **docs/02-architecture/api-design.md**
   - BRD API consolidation: single POST /generate endpoint with mode parameter
   - PDF download mechanism clarification
   - Event contracts: dual event pattern (ai.brd.generated + ai.security.fabrication_flag)

3. **docs/03-ai/guardrails.md**
   - Fabrication validator implementation details: difflib-based fuzzy matching, no AI

4. **docs/03-design/component-specs.md**
   - Review tab visibility rule: always visible for 'open' state

5. **docs/03-design/page-layouts.md**
   - Workspace layout Review tab visibility update

---

## Deviation Details

### D-001: pydyf Version Constraint
- **Source:** progress.txt US-004 from M9
- **What the spec said:** tech-stack.md listed WeasyPrint 62.x without specific pydyf constraint
- **What was actually implemented:** pydyf pinned to `>=0.10,<0.12`
- **Why it changed:** pydyf 0.12.x removed `transform` method from Stream class, breaking WeasyPrint 62.x
- **Autonomy level:** SMALL TECHNICAL

### D-002: libgdk-pixbuf Package Name
- **Source:** progress.txt US-004 from M9
- **What the spec said:** Not explicitly documented
- **What was actually implemented:** libgdk-pixbuf-2.0-0 (with hyphens)
- **Why it changed:** Debian package naming clarification for python:3.12-slim base image
- **Autonomy level:** SMALL TECHNICAL

### D-003: Review Tab Visibility Rule
- **Source:** progress.txt US-006 from M9
- **What the spec said:** Review tab visible after first submission (has_been_submitted flag)
- **What was actually implemented:** reviewVisible=true for 'open' state — always visible during brainstorming
- **Why it changed:** UX simplification — users can view/prepare BRD content before submit, reducing friction
- **Autonomy level:** FEATURE DESIGN

### D-004: BRD API Endpoint Consolidation
- **Source:** progress.txt US-005, tasks/prd-m9.json US-005
- **What the spec said:** Multiple POST endpoints:
  - POST /api/ideas/:id/brd/generate (skeleton)
  - POST /api/ideas/:id/brd/regenerate (selective)
  - POST /api/ideas/:id/brd/regenerate-section (single section)
- **What was actually implemented:** Single POST /api/ideas/:id/brd/generate with `{mode, section_name?}` body
- **Why it changed:** API consolidation — cleaner design, reduces endpoint proliferation
- **Autonomy level:** LARGE TECHNICAL

### D-005: PDF Download Implementation
- **Source:** progress.txt US-006 from M9
- **What the spec said:** POST /api/ideas/:id/brd/generate-pdf endpoint
- **What was actually implemented:** PDF embedded via `<object>` tag, Download via temporary `<a>` element, no dedicated endpoint
- **Why it changed:** Simpler implementation — on-demand generation via gRPC, blob URL from memory
- **Autonomy level:** LARGE TECHNICAL

### D-006: Fabrication Validator Implementation Details
- **Source:** progress.txt US-002 from M9
- **What the spec said:** guardrails.md specified "Source Cross-Reference" without implementation details
- **What was actually implemented:** Purely heuristic — Python stdlib difflib + simple tokenization
- **Why it changed:** Performance choice — no AI overhead, no token costs, synchronous validation
- **Autonomy level:** LARGE TECHNICAL

### D-007: Event Publishing Pattern for BRD Generation
- **Source:** progress.txt US-002 from M9
- **What the spec said:** ai.brd.generation_complete event
- **What was actually implemented:** Two events: ai.brd.generated (main) + ai.security.fabrication_flag (monitoring)
- **Why it changed:** Decoupling — business logic vs. monitoring concerns
- **Autonomy level:** LARGE TECHNICAL

---

## Impact on Future Milestones

### M10 (Review & Resubmission)
- **Benefit:** BRD API consolidation simplifies resubmission — single POST /generate handles both initial and resubmission regeneration

### M11 (PDF Versioning)
- **Benefit:** PDF download mechanism already in place — versioning adds GET /api/ideas/:id/brd/versions/:versionId/pdf for historical PDFs

### M12+ (Admin Monitoring)
- **Benefit:** ai.security.fabrication_flag events already published and available for admin dashboard consumption

### API Contract Changes
**Backward-compatible:** M9 consolidated redundant endpoints but did not break existing contracts (no M8 or earlier milestones used BRD endpoints).

---

## Notes

### Deterministic Drift Pattern
This reconciliation demonstrates **deterministic drift**: the gap between PRD (what was planned for M9) and architecture docs (original design). The M9 PRD already contained the evolved API design, but upstream architecture docs still showed the older multi-endpoint design. Implementation followed the PRD exactly (QA: "Deviations: None"), but architecture docs lagged behind.

### Fabrication Validator Design Philosophy
Lightweight heuristic approach chosen for:
1. **Performance:** No AI invocation overhead, synchronous validation
2. **Cost:** No additional LLM token consumption
3. **Determinism:** Fuzzy matching is deterministic given fixed thresholds
4. **Sufficiency:** Catches obvious fabrication without false positives

---

**Reconciliation Status:** COMPLETE
**All Changes Applied:** 2026-03-11

---

## Summary of Applied Changes

### 1. docs/02-architecture/tech-stack.md
**Lines modified:** 31
**Change:** Added pydyf version constraint and system dependencies to PDF Generation row
```diff
- | PDF Generation | WeasyPrint | 62.x | Python-native HTML-to-PDF |
+ | PDF Generation | WeasyPrint | 62.x | ... **Requires pydyf>=0.10,<0.12** (0.12.x breaks Stream.transform). System dependencies: libcairo2, libpango-1.0-0, libgdk-pixbuf-2.0-0 |
```

### 2. docs/02-architecture/api-design.md
**Sections modified:** BRD endpoints (§ BRD), Event contracts (§ Message Broker)
**Changes:**
- **Lines 450-490:** Replaced three POST endpoints with single mode-based endpoint
  - Removed: POST /generate, POST /regenerate, POST /regenerate-section
  - Added: Single POST /generate with {mode, section_name?}
- **Lines 529-537:** Updated PDF download (POST /generate-pdf → GET /pdf with M9 notes)
- **Lines 1739-1743:** Documented dual event pattern
- **Line 2129:** Updated ai.brd.generated event schema
- **Line 2145:** Clarified ai.security.fabrication_flag as part of dual pattern

### 3. docs/03-ai/guardrails.md
**Lines modified:** 222-224 (after "**Implementation:**" paragraph)
**Change:** Added M9 Implementation Details subsection
- Documented FabricationValidator: Python stdlib difflib, thresholds (0.75, 0.5), no AI

### 4. docs/03-design/component-specs.md
**Lines modified:** 680-688 (§ 12.1 Embedded PDF View)
**Change:** Added tab visibility rule: "Review tab visible for 'open' state (M9: always visible during brainstorming)"

### 5. docs/03-design/page-layouts.md
**Lines modified:** 334-350 (§ 4.3 Right Panel Tabs)
**Change:** Added M9 Tab Visibility Update subsection: Board always visible, Review visible for 'open' state

---

## Verification

✅ All changes applied to upstream documentation
✅ Deterministic drift between M9 PRD/implementation and architecture docs resolved
✅ Files modified: 5
✅ Deviations resolved: 7 (2 SMALL TECHNICAL, 1 FEATURE DESIGN, 4 LARGE TECHNICAL)
✅ Rejected changes: 0

**Next milestone (M10) can proceed with accurate, up-to-date specifications.**
