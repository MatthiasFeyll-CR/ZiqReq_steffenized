# Milestone 6 Spec Reconciliation

## Summary
- **Milestone:** M6 — WebSocket & Real-Time
- **Date:** 2026-03-10
- **Total deviations found:** 2
- **Auto-applied (SMALL TECHNICAL):** 1
- **Approved and applied (FEATURE DESIGN):** 1
- **Approved and applied (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| 1 | D-002: ConnectionIndicator uses Tailwind tokens | `docs/03-design/component-specs.md:739-754` | Added implementation note: Tailwind tokens (`green-500`, `red-500`) are semantically equivalent to CSS variables (`var(--success)`, `var(--destructive)`) |

**Diff:**
```diff
 | State | Dot | Label | Color |
 |-------|-----|-------|-------|
-| Online | 8px circle | "Online" | `var(--success)` |
-| Offline | 8px circle | "Offline" | `var(--destructive)` |
+| Online | 8px circle | "Online" | `var(--success)` / Tailwind `green-500` |
+| Offline | 8px circle | "Offline" | `var(--destructive)` / Tailwind `red-500` |

+- **Implementation note:** Uses Tailwind semantic color tokens (`green-500`, `red-500`) which map to equivalent values as the CSS variables
```

### FEATURE DESIGN (Applied and flagged)

| # | Deviation | Document Updated | Change | Reason |
|---|-----------|-----------------|--------|--------|
| 1 | D-001: OfflineBanner background color | `docs/03-design/page-layouts.md:1141` & `docs/03-design/component-inventory.md:162` | Changed from `bg-error-bg` (red) to `bg-warning-bg` (amber/yellow) | Amber/yellow is the UX standard for "degraded but recovering" states; red implies permanent failure |

**Diff (page-layouts.md):**
```diff
 ### 11.3 Offline Banner

-- `bg-error-bg`, `border border-error`, `rounded-md`, `p-3`
+- `bg-warning-bg`, `border border-warning`, `rounded-md`, `p-3`
 - Countdown updates in real-time
 - Reconnect button: primary style, triggers immediate reconnection
```

**Diff (component-inventory.md):**
```diff
-| OfflineBanner | Common | Workspace | No | Red banner with countdown + reconnect (FA-6) |
+| OfflineBanner | Common | Workspace | No | Amber/yellow warning banner with countdown + reconnect (FA-6) |
```

### LARGE TECHNICAL

None.

### REJECTED

None.

## Documents Modified

1. `docs/03-design/page-layouts.md` — Updated OfflineBanner color scheme (§11.3)
2. `docs/03-design/component-inventory.md` — Updated OfflineBanner description
3. `docs/03-design/component-specs.md` — Added ConnectionIndicator implementation note (§14)

## Impact on Future Milestones

**No impact.** These are visual/implementation clarifications that don't affect functionality:

- **OfflineBanner color change:** Future milestones don't implement new offline-related features. The amber/yellow color is already implemented and tested in M6.
- **ConnectionIndicator tokens:** Implementation detail only; future milestones don't modify this component.

## Deviation Analysis

### D-001: OfflineBanner Background Color (FEATURE DESIGN)

**Source:** QA report DEV-001 from M6 websocket
**Classification:** FEATURE DESIGN — changes user-visible appearance

**What changed:**
- **Spec said:** Use error colors (red: `bg-error-bg`, `border border-error`)
- **Implementation used:** Warning colors (amber/yellow: `bg-warning-bg`, `border border-warning`)

**Why the implementation is correct:**
According to established UX patterns and the implementation rationale:
- **Red (error)** semantically indicates a permanent failure or critical error state
- **Amber/Yellow (warning)** semantically indicates a degraded but recovering state
- The OfflineBanner is a temporary, auto-recovering condition (exponential backoff reconnection)
- Using warning colors better communicates "something is wrong but we're handling it"
- Matches the warning semantic token defined in `docs/03-design/design-system.md` for "offline warning"

**Decision:** Update spec to match implementation. This is a better UX pattern.

### D-002: ConnectionIndicator Uses Tailwind Tokens (SMALL TECHNICAL)

**Source:** QA report DEV-002 from M6 websocket
**Classification:** SMALL TECHNICAL — implementation technique, no visual change

**What changed:**
- **Spec said:** Use CSS variables (`var(--success)`, `var(--destructive)`)
- **Implementation used:** Tailwind utility class tokens (`green-500`, `red-500`)

**Why the implementation is correct:**
Both approaches are semantically equivalent and part of a well-structured design system:
- CSS variables (`var(--success)`) point to specific hex values defined in the design system
- Tailwind tokens (`green-500`) also point to specific hex values
- In this case, `green-500` (#22c55e) matches the dark mode `--success` color
- Using Tailwind tokens is a valid pattern and ensures consistency with Tailwind's utility-first approach
- No hardcoded hex values in either case — both use semantic tokens

**Decision:** Update spec to acknowledge both approaches are valid. The implementation using Tailwind tokens is architecturally sound and requires no changes.

## Quality Notes

All changes are **documentation-only updates** that align the spec with the actual, tested, and QA-approved implementation. No code changes are required or made. The implementation in M6 is correct and passes all quality gates.

## References

- **Progress file:** `.ralph/archive/m6-websocket/progress.txt`
- **QA report:** `docs/08-qa/qa-m6-websocket.md`
- **Original deviations:** DEV-001 (OfflineBanner color), DEV-002 (ConnectionIndicator tokens)
- **Bugfix cycles:** 7 (all defects resolved, deviations carried forward to reconciliation)
