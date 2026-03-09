# Milestone 3 Spec Reconciliation

## Summary
- **Milestone:** M3 — Workspace Chat
- **Date:** 2026-03-09
- **Total deviations found:** 1
- **Auto-applied (SMALL TECHNICAL):** 0
- **Applied and flagged (FEATURE DESIGN):** 1
- **Applied and flagged (LARGE TECHNICAL):** 0
- **Rejected:** 0

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

_No small technical changes found._

### FEATURE DESIGN (Applied and Flagged)

| # | Deviation | Document Updated | Change | Impact |
|---|-----------|-----------------|--------|---------|
| 1 | D-001: Chat pagination changed from cursor to offset-based | `docs/02-architecture/api-design.md` | **API Contract Change**<br>**Query params:** `before` (uuid) + `limit` → `offset` (int) + `limit` (int, max 100)<br>**Response shape:** `{messages, has_more}` → `{messages, total, limit, offset}` | Frontend can now display total count and implement traditional pagination controls. Simpler implementation than cursor-based pagination. |

#### D-001 Detail: Chat Messages API Pagination

**Source:** `services/gateway/apps/chat/views.py:123-138`, progress.txt US-001 line 521

**Original Specification (docs/02-architecture/api-design.md:224-254):**
```
GET /api/ideas/:id/chat?before=<uuid>&limit=50

Response:
{
  "messages": [...],
  "has_more": boolean
}
```

**Actual Implementation:**
```
GET /api/ideas/:id/chat?offset=0&limit=50

Response:
{
  "messages": [...],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

**Rationale:**
Offset-based pagination is simpler to implement and provides a `total` count, which enables traditional pagination UI controls (e.g., "Page 1 of 5"). Cursor-based pagination is more efficient for real-time streams but adds complexity for this use case where chat history is relatively static between loads.

**Frontend Impact:**
The frontend (`frontend/src/api/chat.ts`) was implemented against the offset-based API from the start. No frontend changes required. Future milestones should use this offset-based pattern for consistency.

**Future Considerations:**
If chat messages grow very large (10,000+ messages per idea) and performance becomes an issue, cursor-based pagination could be reconsidered. For now, offset-based pagination is adequate.

### LARGE TECHNICAL (Applied and Flagged)

_No large technical changes found._

### REJECTED

_No changes were rejected._

---

## Documents Modified

1. **docs/02-architecture/api-design.md**
   - Section: `### Chat` → `#### GET /api/ideas/:id/chat`
   - Lines: 224-254
   - Change: Updated query parameters and response shape to match actual implementation

---

## Impact on Future Milestones

### Milestones Affected: None directly impacted

The chat messages API is now stable as implemented. Future milestones that use chat pagination (M6 WebSocket updates, M7 AI chat integration) will use the offset-based pagination as documented.

### Pattern Established:

**Pagination style for list endpoints:**
- **Ideas list** (`GET /api/ideas`): page-based pagination (`page`, `page_size`)
- **Chat messages** (`GET /api/ideas/:id/chat`): offset-based pagination (`offset`, `limit`)

This inconsistency should be noted but does not require reconciliation — the two endpoints serve different UX patterns (landing page list vs. chat history scroll).

---

## Deviation Analysis

### Why was this missed by QA?

The QA report (docs/08-qa/qa-m3-workspace-chat.md) states "No deviations found. Implementation matches specifications." This is **incorrect**.

**Root cause:** The QA Engineer verified that the API works correctly and returns chat messages, but did not compare the actual query parameters and response shape against the specification document. The deviation is in the **API contract**, not in functional behavior.

**Recommendation for future QA cycles:** Include explicit API contract verification — check query parameters and response shapes match the spec exactly, not just that the endpoint returns data.

---

## Technical Debt / Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| API contract divergence from spec | **Low** | Spec has been updated to match reality. Frontend was implemented correctly from the start. |
| Inconsistent pagination patterns | **Low** | Documented pattern: ideas list uses page/page_size, chat uses offset/limit. Both are valid REST patterns. |
| Performance with large chat histories | **Low** | Offset pagination can be slow for very high offsets (10,000+), but unlikely given idea lifecycle. Monitor in production. |

---

## Notes

- All M3 user stories (US-001 through US-010) passed QA and all tests pass.
- Only one deviation found despite thorough review of progress logs and implementation.
- The deviation is isolated to the chat messages API and has no cascading effects.
- Frontend implementation (`frontend/src/api/chat.ts`) matches the actual backend API, so no frontend changes required.
- The `progress.txt` comment "matches spec for chat" (line 521) was incorrect — this reconciliation corrects the documentation to match reality.
