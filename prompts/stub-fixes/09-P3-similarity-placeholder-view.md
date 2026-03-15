# P3: Similarity Placeholder View — Wire Up Real API

## Goal

The similarity API endpoint is a single placeholder function that returns `{"status": "ok"}` regardless of input. It needs to be replaced with real endpoints that serve the similarity detection and merge flow features (FA-5).

## Files to Modify

### Primary file (the placeholder):
- `services/gateway/apps/similarity/views.py`
  ```python
  @api_view(["GET"])
  def placeholder(request):
      return Response({"status": "ok"})
  ```

### URL routing:
- `services/gateway/apps/similarity/urls.py` (or check `services/gateway/gateway/urls.py`) — find where the placeholder is routed

### Existing similarity-related code that's already implemented elsewhere:
- `services/gateway/apps/ideas/views.py` line ~558 — `get_similar_ideas()` is already implemented there with pgvector queries. It returns declined merges + near-threshold vector matches. This may belong in the similarity views instead.

### Models:
- Check `services/core/apps/similarity/models.py` or `services/gateway/apps/similarity/models.py` for:
  - `MergeRequest` model — stores merge/append requests between ideas
  - `IdeaKeywords` model — stores keywords per idea
  - `idea_embeddings` table — pgvector embeddings

### Merge/append service implementations:
- `services/gateway/apps/similarity/merge_service.py` — merge logic
- `services/gateway/apps/similarity/append_service.py` — append logic
- `services/core/apps/similarity/merge_service.py` — may also exist

### Frontend API:
- `frontend/src/api/similarity.ts` — check what endpoints the frontend expects

## What Endpoints Are Needed

Based on requirements FA-5 and the frontend API file, the similarity module likely needs:

1. **GET /api/ideas/:id/similar** — Already implemented in `ideas/views.py` as `get_similar_ideas`. Consider moving it here or keeping it there.

2. **POST /api/similarity/merge-request** — Create a merge request between two ideas
   - Body: `{ requesting_idea_id, target_idea_id }`
   - Validates both ideas exist and are in mergeable states (open/rejected)
   - Creates a `MergeRequest` record
   - Publishes notification event

3. **POST /api/similarity/merge-request/:id/accept** — Accept a merge request
4. **POST /api/similarity/merge-request/:id/decline** — Decline a merge request
5. **POST /api/similarity/append-request** — Create an append request (for in-review ideas)
6. **GET /api/similarity/merge-requests** — List pending merge requests for current user

## Related Requirements

- **F-5.4:** State-Aware Match Behavior — open/rejected = mergeable, in_review = append flow, accepted/dropped = informational
- **F-5.5:** Merge Flow — AI detects similarity, notifies both users, requires mutual consent, creates new merged idea
- **F-5.6:** Merge Request UI — banner over receiving idea page
- **F-5.7:** Permanent Dismissal — declined merge permanently dismissed
- **F-5.8:** Manual Merge Request — users can manually invoke merge by UUID or browsing similar ideas

## Frontend Reference

Read `frontend/src/api/similarity.ts` to see exactly which API endpoints the frontend calls. Also check:
- `frontend/src/components/workspace/ManualMergeModal.tsx` — manual merge UI (line 164 has UUID input)

## Important: Check What Already Exists

Before implementing new views, do a thorough search:
- `grep -r "merge_request" services/gateway/apps/` — find existing merge request handling
- `grep -r "append_request" services/gateway/apps/` — find existing append handling
- Check URL files to see if endpoints are already routed elsewhere
