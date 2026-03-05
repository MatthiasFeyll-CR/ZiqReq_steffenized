# Milestone 11: Similarity Detection & Merge

## Overview
- **Wave:** 6
- **Estimated stories:** 9
- **Must complete before starting:** M6
- **Can run parallel with:** None
- **MVP:** No (Post-MVP)

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-5 | Similarity Detection & Merge (all features) | P1 | F-5.1–F-5.8 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| merge_requests | CRUD | requesting_idea_id, target_idea_id, resulting_idea_id, merge_type, status, requesting_owner_consent, target_owner_consent, reviewer_consent | data-model.md |
| idea_keywords | READ | idea_id, keywords | data-model.md |
| idea_embeddings | READ | idea_id, embedding | data-model.md |
| ideas | CREATE (merged), UPDATE (state, visibility) | all columns | data-model.md |
| idea_collaborators | CREATE (transfer to merged) | idea_id, user_id | data-model.md |
| chat_messages | CREATE (synthesis message) | idea_id, content, sender_type='ai' | data-model.md |
| board_nodes | CREATE (merged board) | idea_id, all columns | data-model.md |
| board_connections | CREATE (merged board) | idea_id, all columns | data-model.md |
| notifications | CREATE (via notification service) | user_id, type | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/ideas/:id/merge/request | POST | Request merge with another idea | Owner | api-design.md |
| POST /api/merge-requests/:id/accept | POST | Accept merge request | Target owner | api-design.md |
| POST /api/merge-requests/:id/decline | POST | Decline merge request | Target owner | api-design.md |
| POST /api/merge-requests/:id/reviewer-accept | POST | Reviewer accepts append (3-way) | Reviewer | api-design.md |
| POST /api/merge-requests/:id/reviewer-decline | POST | Reviewer declines append | Reviewer | api-design.md |
| GET /api/ideas/:id/similar | GET | Get similar ideas for an idea | User | api-design.md |
| POST /api/ideas/:id/merge/manual | POST | Manual merge request by UUID/URL | Owner | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Deep Comparison | Full-context similarity confirmation | agent-architecture.md §3.7 |
| Merge Synthesizer | Combine two ideas into merged idea | agent-architecture.md §3.9 |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| MergeRequestBanner (wire actions) | Feature | component-inventory.md |
| SimilarIdeaCard | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Backend] Background keyword matching service** — Implement Celery periodic task body for keyword_matching_sweep (registered in M1). Query ideas with keywords updated since last sweep. For each updated idea: compare keyword array against all other ideas within similarity time window (default 6 months, admin-configurable). Set intersection of keyword arrays. If overlap >= admin: min_keyword_overlap (default 7) AND pair not previously dismissed (status != declined in merge_requests): publish similarity.detected event with idea pair IDs. Track last_sweep_timestamp to avoid redundant comparisons.
2. **[Backend] Vector similarity search** — Extend background task (or run as separate periodic task). Query idea_embeddings via pgvector cosine similarity search. Find pairs with similarity > admin: similarity_vector_threshold (default 0.75). Combine results with keyword matching (either signal triggers deep comparison). Deduplicate: same pair from both signals → single similarity.detected event. Filter out already-processed pairs (existing merge_requests regardless of status).
3. **[Backend] Deep Comparison agent** — DeepComparisonAgent(BaseAgent): input = Idea A summary + board content, Idea B summary + board content. Output = JSON: { is_similar: bool, confidence: float(0-1), explanation: string, overlap_areas: string[] }. Default model tier. Retry once on failure. AI service consumes similarity.detected event → loads context for both ideas → runs Deep Comparison → if is_similar AND confidence > 0.7: publish ai.similarity.confirmed event.
4. **[Backend+Frontend] Similarity notification flow** — ai.similarity.confirmed event consumed by: Core service (persists similarity relationship), Notification service (notifies both idea owners). Both users receive persistent notification + email (per preferences). Both users gain temporary read-only access to each other's idea (visibility override). Frontend: SimilarIdeaCard in review section below fold (replace M9 stub) — shows matched idea title, keyword match count, link to view.
5. **[API] Merge request API** — POST /api/ideas/:id/merge/request: create merge_request with requesting_idea_id, target_idea_id, merge_type (merge if both open, append if target is in_review). Validation: both ideas must be in appropriate states, requesting user must be owner. Consent tracking: requesting_owner_consent = accepted (auto), target_owner_consent = pending, reviewer_consent = pending (for append only). Target idea locked with merge banner on creation. Publish merge.request.created event.
6. **[Frontend] Merge request UI** — MergeRequestBanner (wire M10 stub actions): shows on target idea when pending merge_request exists. Banner content: "User X wants to merge their idea '[title]' with yours" + View Their Idea link + Accept/Decline buttons. Accept → POST accept → if all consents met, trigger merge. Decline → POST decline → unlock idea, dismiss banner, mark pair as permanently dismissed. Idea editing locked while merge pending (gray overlay on chat/board).
7. **[Backend] Merge Synthesizer + merged idea creation** — Triggered when all consents met (merge.request.resolved event with status='accepted'). MergeSynthesizerAgent(BaseAgent): input = both ideas' full context (chat summary + board state + keywords). Output = { synthesis_message: string, board_instructions: array }. Default model tier. Retry 3x. On success: Core creates new idea (co-owners = both original owners), synthesis_message becomes first chat message, Board Agent executes board_instructions on merged idea's board. All collaborators from both ideas added to new idea. Original ideas: state set to 'merged' (read-only), reference to new idea stored. merge_request.resulting_idea_id updated.
8. **[API+Frontend] Append flow** — For append (open → in_review): three-way consent required (requesting owner + target owner + target's assigned reviewer). Requesting owner → consents on creation. Target owner notified, accepts/declines. If target accepts AND idea has assigned reviewer: reviewer notified, accepts/declines. On all three accepted: open idea closed (read-only, reference to target), owner of open idea becomes collaborator on target idea, context from open idea appended to target (synthesis message + board additions). State transitions for open idea only.
9. **[API+Frontend] Manual merge + permanent dismissal + similar ideas display** — Manual merge request: owner enters another idea's UUID or URL in a search input → creates merge_request manually (bypasses similarity detection). Permanent dismissal: declined merge_request pairs are never re-suggested by background matching. But manual merge request can still be created for declined pairs. Similar ideas in review section: SimilarIdeaCard list below fold in workspace, shows all similar ideas with confidence score, keyword overlap count, and status (pending merge / dismissed / no action).

## Shared Components Required
| Component | Status | Introduced In |
|-----------|--------|---------------|
| AI service scaffold + pipeline | Available | M6 |
| Keyword Agent + embeddings | Available | M6 |
| Notification system | Available | M10 |
| Review section below fold | Available | M9 |
| MergeRequestBanner (UI shell) | Available | M10 |

## File Ownership (for parallel milestones)
This milestone is single (Wave 6) — no parallel ownership concerns.

Exclusive directories:
- `services/ai/agents/deep_comparison/`
- `services/ai/agents/merge_synthesizer/`
- `frontend/src/features/merge/`
- `services/gateway/apps/merge/`
- `services/core/apps/merge/` (or similarity/)

Shared files (additive changes):
- `services/core/tasks.py` (implement keyword_matching_sweep task body)
- `services/ai/events/consumers.py` (add similarity.detected consumer)
- `services/ai/tasks.py` (add similarity sweep vector search)
- `frontend/src/pages/IdeaWorkspace/` (wire SimilarIdeaCard, MergeRequestBanner actions)
- `frontend/src/features/notifications/` (add similarity notification templates)
- `services/gateway/apps/websocket/consumers.py` (add merge-related event broadcasting)

## Milestone Acceptance Criteria
- [ ] Background keyword matching detects similar idea pairs above threshold
- [ ] Vector similarity search finds semantically similar ideas
- [ ] Deep Comparison agent confirms genuine similarity with confidence score
- [ ] Both owners notified on confirmed similarity
- [ ] Read-only cross-access granted for similar ideas
- [ ] Merge request creates and locks target idea
- [ ] MergeRequestBanner displays with correct actions
- [ ] Accept triggers merge: new idea created with synthesized content and combined board
- [ ] Decline permanently dismisses the pair
- [ ] Both original owners become co-owners of merged idea
- [ ] Original ideas become read-only with reference
- [ ] All collaborators transferred to merged idea
- [ ] Append flow works with three-way consent
- [ ] Manual merge request works (UUID entry)
- [ ] Similar ideas display in workspace review section
- [ ] Permanently dismissed pairs never re-suggested
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1–M10, M12

## Notes
- This is the most complex milestone — involves 2 AI agents, complex state management (consent tracking), and creates new entities. Thorough testing recommended.
- Merge Synthesizer failure: if AI fails after 3 retries, merge is halted. Both users notified. merge_request status set to 'error'. Users can retry or cancel.
- Board Agent is reused from M6 to build the merged idea's board from Merge Synthesizer's board_instructions.
- Permanent dismissal is per-pair (bidirectional): if A-B declined, neither A→B nor B→A automatic matching occurs. Manual merge still allowed.
- The 'merged' state is an addition to the idea state machine (open/in_review/accepted/rejected/dropped/merged). Ensure state machine allows this transition.
