# Milestone 1 Spec Reconciliation

## Summary
- **Milestone:** M1 — Foundation & Auth
- **Date:** 2026-03-09
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 1
- **Approved and applied (FEATURE DESIGN):** 0
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-001: i18n translation files in `locales/` subdirectory | `docs/02-architecture/project-structure.md` | Updated path from `frontend/src/i18n/*.json` to `frontend/src/i18n/locales/*.json` to match actual implementation. Added `locales/` subdirectory for better organization. |

### FEATURE DESIGN (Human-approved)

*No feature design deviations found.*

### LARGE TECHNICAL (Human-approved)

*No large technical deviations found.*

### REJECTED

*No deviations were rejected.*

---

## Documents Modified

1. `docs/02-architecture/project-structure.md` — Updated i18n directory structure (lines 165-170)

---

## Impact on Future Milestones

**None.** The i18n file path change is local to the frontend structure and does not affect any future milestone specifications or dependencies.

---

## Deviation Details

### D-001: i18n Translation Files Path

**Source:** `.ralph/archive/m1-foundation/progress.txt` (US-009, line 171)

**What the spec said:**
```
frontend/src/i18n/
├── config.ts
├── de.json
└── en.json
```

**What was actually implemented:**
```
frontend/src/i18n/
├── config.ts
└── locales/
    ├── de.json
    └── en.json
```

**Why it changed:**
The implementation added a `locales/` subdirectory to organize translation files separately from configuration code. This is a common pattern in i18n setups and improves project structure clarity.

**Impact:** None. This is purely a file organization change with no behavioral or functional impact.

---

## Implementation Notes Verified as Non-Deviations

The following items were documented in `progress.txt` as learnings but were **confirmed to match the spec** and are therefore **not deviations**:

1. **User.roles and IdeaKeywords.keywords use ArrayField** — Spec (data-model.md) already specified `varchar[]` type. ✓ Correct.
2. **PyJWT[crypto] added for Azure AD validation** — Spec said "Azure AD token validation" without naming library. PyJWT is the appropriate Python implementation. ✓ Correct.
3. **Session middleware added** — Standard Django component for authentication. Implementation detail not requiring spec-level documentation. ✓ Correct.
4. **Frontend tsconfig updated for Vite** — Build configuration detail not covered by architecture specs. ✓ Appropriate.
5. **Badge has 8 variants** — Spec (component-specs.md) specified 5 state badges + 3 role badges = 8 total. ✓ Matches exactly.
6. **Proto servicers return dicts in M1** — Placeholder implementation expected for foundation milestone. ✓ Appropriate for M1 scope.
7. **Docker compose at `infra/docker/`** — Spec (project-structure.md) already documented this path. ✓ Confirmed, not deviated.
8. **Test infrastructure updates (conftest.py, TEST config)** — Bug fix (DEF-001) for test database lifecycle. Test setup files are not spec-level artifacts. ✓ Appropriate bugfix.

---

## QA Alignment

The QA report for M1 (`docs/08-qa/qa-m1-foundation.md`) stated **"Deviations found: 0"**. This reconciliation identified **1 minor file path deviation** that QA did not flag. The deviation is categorized as SMALL TECHNICAL and has been corrected in the upstream spec to match the implementation.

**Recommendation:** Future QA reviews should compare file paths in `project-structure.md` against actual implementation to catch organizational deviations.

---

## Milestone 1 Completion Status

✅ **All 10 user stories passed acceptance criteria**
✅ **All required tests passing (14 Python + 5 Node)**
✅ **All gate checks passing**
✅ **1 minor spec deviation reconciled**
✅ **Upstream documentation now matches implementation**

**M1 Foundation is complete and ready for M2.**
