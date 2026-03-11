# Milestone 13 Spec Reconciliation — Similarity Detection & Merge

## Summary
- **Milestone:** M13 — Similarity Detection & Merge
- **Date:** 2026-03-11
- **Total deviations found:** 4
- **Auto-applied (SMALL TECHNICAL):** 1
- **Applied (FEATURE DESIGN):** 2
- **Recommendations (Security):** 1
- **Rejected:** 0

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

| # | Deviation | Document Updated | Change |
|---|-----------|-----------------|--------|
| D-004 | Email preference key naming | `docs/02-architecture/api-design.md:1136` | Fixed preference key: `similarity_alert` → `similarity` to match implementation |

**Diff:**
```diff
- "similarity_alert": true,
+ "similarity": true,
```

**Rationale:** The implementation checks `email_prefs.get("similarity", True)` in `services/notification/consumers/similarity_events.py:268`. The spec incorrectly documented this as `similarity_alert`. Updated spec to match actual implementation behavior.

---

### FEATURE DESIGN (Applied and flagged)

| # | Deviation | Document Updated | Change | Reason |
|---|-----------|-----------------|--------|--------|
| D-001 | Consent endpoint consolidation | `docs/02-architecture/api-design.md:973-992` | Consolidated two endpoints (`/accept`, `/decline`) into single `/consent` endpoint with body parameter | Reduces code duplication; both actions share identical auth and validation logic |
| D-003 | GetIdeaDetails gRPC addition | `docs/02-architecture/api-design.md:2120-2148` | Added `GetIdeaDetails` RPC to `GatewayService` proto definition | Notification service needs to fetch idea metadata for similarity emails |

#### D-001 Detail: Consent Endpoint Consolidation

**Original spec (api-design.md lines 973-992):**
```
POST /api/merge-requests/:id/accept
POST /api/merge-requests/:id/decline
```

**Actual implementation:**
```
POST /api/merge-requests/:id/consent
Body: { "consent": "accept" | "decline" }
```

**Updated spec:**
```markdown
#### POST /api/merge-requests/:id/consent
- **Purpose:** Accept or decline a merge request (target owner consent)
- **Auth:** Target idea owner
- **Request:**
  ```json
  { "consent": "accept" | "decline" }
  ```
- **Response (200) — Accept:**
  ```json
  { "status": "accepted", "resulting_idea_id": "uuid" }
  ```
- **Response (200) — Decline:**
  ```json
  { "status": "declined" }
  ```
```

**Why this is correct:** Both actions share identical authorization logic (must be target idea owner), status validation (must be pending), and only differ in the resulting status value. Single endpoint reduces controller duplication and matches the PRD acceptance criteria (US-007 AC6-8).

#### D-003 Detail: GetIdeaDetails gRPC Addition

**Original spec:** No `GetIdeaDetails` RPC documented in `proto/gateway.proto`

**Actual implementation:** Added to gateway.proto
```protobuf
rpc GetIdeaDetails(IdeaDetailsRequest) returns (IdeaDetailsResponse);

message IdeaDetailsRequest {
  string idea_id = 1;
  bool ensure_share_link_token = 2;
}

message IdeaDetailsResponse {
  string title = 1;
  string owner_id = 2;
  string share_link_token = 3;
}
```

**Updated spec:** Added RPC definition to `docs/02-architecture/api-design.md:2120-2148` with notes documenting the on-demand share token generation using `secrets.token_hex(32)`.

**Why this was needed:** The notification service needs to fetch idea titles and owner IDs to construct similarity notification emails. Additionally, it needs share link tokens to enable cross-access between similar idea owners. The gateway owns the ideas table, so the notification service must call via gRPC.

---

### LARGE TECHNICAL (Applied and flagged)

None.

---

### REJECTED

None.

---

### SECURITY RECOMMENDATIONS (Not spec deviations)

| # | Finding | Recommendation | Risk Level |
|---|---------|---------------|------------|
| SEC-001 | Email HTML without escaping | Add `html.escape()` for idea titles in HTML email templates (`services/notification/consumers/similarity_events.py:296-310`) | Minor |

**Context:** Idea titles are interpolated directly into HTML email bodies via f-strings without `html.escape()`. While risk is low (titles are from authenticated users, email clients sanitize HTML), this is flagged as a defense-in-depth opportunity.

**Not applied to spec because:** This is a security hardening recommendation, not a spec deviation. The spec does not currently define email security patterns. If the team decides to add HTML escaping as a standard pattern, it should be documented in a new "Email Security Patterns" section in `docs/02-architecture/project-structure.md`.

---

## Documents Modified

### Modified Files
1. **docs/02-architecture/api-design.md**
   - Lines 973-992: Updated merge request consent endpoint (consolidated /accept and /decline)
   - Line 1136: Fixed email preference key from `similarity_alert` to `similarity`
   - Lines 2120-2148: Added GetIdeaDetails RPC to GatewayService proto definition
   - Notes section: Documented GetIdeaDetails usage and share token generation

### Files Not Modified (No deviations found)
- `docs/01-requirements/features.md` — Feature definitions remained accurate
- `docs/02-architecture/data-model.md` — No schema changes (MergeRequest model already existed)
- `docs/02-architecture/project-structure.md` — File paths and module structure were correct
- `docs/03-design/*.md` — UI components matched specs
- `docs/03-ai/*.md` — Agent behavior and tool schemas were correct
- `docs/05-milestones/milestone-13.md` — Scope remained accurate

---

## Impact on Future Milestones

### No Impact
All changes are localized to M13 features (similarity detection and merge flow). Future milestones are not affected.

### Clarifications for Future Work
1. **Email preference keys:** Future notification features should use the same naming pattern (`<feature>` not `<feature>_alert`) for consistency with the `similarity` key.
2. **gRPC additions:** Any future inter-service communication requiring idea metadata should use the new `GetIdeaDetails` RPC rather than duplicating this logic.
3. **Consent endpoint pattern:** The single-endpoint-with-body-param pattern established in `/consent` could be reused for other dual-action flows (e.g., invitation accept/decline).

---

## Reconciliation Metadata

**Progress file scanned:** `.ralph/archive/m13-similarity/progress.txt` (181 lines, 10 user stories)
**QA report scanned:** `docs/08-qa/qa-m13-similarity.md` (197 lines, 2 deviations flagged)
**Implementation artifacts verified:**
- services/notification/consumers/similarity_events.py (email preference check)
- services/gateway/apps/ideas/views.py (consent endpoint implementation)
- proto/gateway.proto (GetIdeaDetails RPC)
- proto/gateway_pb2.py, proto/gateway_pb2_grpc.py (generated proto bindings)

**Test coverage:** All 761 Python tests passed. All 12 test matrix IDs verified. No defects found during QA.

**Reconciliation approach:** All deviations were applied to the spec (no rejections) because:
1. **SMALL TECHNICAL changes** are factual corrections (typos, naming)
2. **FEATURE DESIGN changes** were functionally equivalent improvements that QA verified as correct
3. The philosophy is "spec follows reality when reality is correct" — the implementation passed all tests and QA review

---

## Sign-off

This reconciliation was performed by the Spec Reconciler agent as part of the M13 pipeline completion workflow.

**Reconciler:** Claude (Spec Reconciler agent)
**Pipeline phase:** Post-QA reconciliation
**Next step:** M14 PRD Writer (if scheduled)
