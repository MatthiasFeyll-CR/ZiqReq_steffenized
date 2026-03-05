# Milestone 10: Similarity & Merge

## Overview
- **Execution order:** 10 (runs after M9)
- **Estimated stories:** 9
- **Dependencies:** M5 (AI service), M6 (embedding pipeline), M9 (notifications)
- **MVP:** No (post-MVP)

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-5.1 | Keyword Generation | Must-have | features.md |
| F-5.2 | Background Keyword Matching | Must-have | features.md |
| F-5.3 | AI Deep Comparison | Must-have | features.md |
| F-5.4 | State-Aware Match Behavior | Must-have | features.md |
| F-5.5 | Merge Flow | Must-have | features.md |
| F-5.6 | Merge Request UI | Must-have | features.md |
| F-5.7 | Permanent Dismissal | Must-have | features.md |
| F-5.8 | Manual Merge Request | Should-have | features.md |
| F-4.12 | Similar Ideas in Review Section | Should-have | features.md |
| F-12.4 | Merge Request Banner | Must-have | features.md |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| idea_keywords | CREATE, UPDATE, READ | idea_id, keywords, last_updated_at | data-model.md |
| idea_embeddings | CREATE, UPDATE, READ | idea_id, embedding, source_text_hash | data-model.md |
| merge_requests | CREATE, READ, UPDATE | requesting_idea_id, target_idea_id, merge_type, status, consents, resulting_idea_id | data-model.md |
| ideas | CREATE (merged idea), UPDATE (closed_by_merge, closed_by_append) | all merge-related columns | data-model.md |
| idea_collaborators | CREATE (transfer collaborators to merged idea) | idea_id, user_id | data-model.md |
| chat_messages | CREATE (synthesis message in merged idea) | idea_id, sender_type='ai', content | data-model.md |
| board_nodes | CREATE (merged board) | all columns | data-model.md |
| board_connections | CREATE (merged board) | all columns | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/merge-requests | POST | Create merge request (manual or AI-triggered) | Bearer/bypass | api-design.md |
| /api/merge-requests/:id/accept | POST | Accept merge request (target owner consent) | Bearer/bypass | api-design.md |
| /api/merge-requests/:id/decline | POST | Decline merge request (permanent dismissal) | Bearer/bypass | api-design.md |
| /api/ideas/:id/similar | GET | Get similar ideas for an idea | Bearer/bypass | api-design.md |
| /api/ideas/:id/review/similar | GET | Get similar ideas for review section | Reviewer role | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| MergeRequestBanner | Component (idea page) | component-specs.md |
| SimilarIdeaCard | Component | component-specs.md |
| ManualMergeDialog | Component | component-specs.md |
| SimilarIdeasPanel (review section) | Component | component-specs.md |
| MergedIdeaReference (read-only old ideas) | Component | component-specs.md |

## AI Agent References

| Agent | Purpose | Source |
|-------|---------|--------|
| Keyword Agent | Abstract keyword extraction (runs every chat processing cycle) | agent-architecture.md §3.6 |
| Deep Comparison | Full-context similarity confirmation | agent-architecture.md §3.7 |
| Merge Synthesizer | Combine two ideas into merged context | agent-architecture.md §3.9 |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| Background keyword matching (Celery periodic task) | New | M10 |
| Idea embedding pipeline (per-idea, after keyword generation) | Activated | M10 (pipeline from M6) |
| Merge execution logic (create merged idea, close originals) | New | M10 |

## Story Outline (Suggested Order)

1. **[AI Service] Keyword Agent activation** — Wire Keyword Agent into chat processing pipeline Step 5. KeywordAgent(BaseAgent) with cheap tier. Input: chat summary + board content + current keywords. Output: JSON array of abstract keywords (max admin: max_keywords_per_idea). Persist via Core gRPC (upsert idea_keywords). Trigger idea embedding update after keyword generation.
2. **[AI Service] Idea embedding pipeline** — After Keyword Agent: concatenate chat context summary + board titles/content + keywords → embed via text-embedding-3-small → upsert idea_embeddings. source_text_hash tracks content changes (skip re-embedding if unchanged).
3. **[Backend] Background similarity detection (Celery)** — Periodic task: query idea_embeddings via pgvector for pairs with cosine similarity > threshold (admin: similarity_vector_threshold). Parallel: keyword overlap check (set intersection ≥ min_keyword_overlap). Filter: only ideas within similarity_time_limit, exclude declined pairs. Either signal → publish similarity.detected event.
4. **[AI Service] Deep Comparison agent** — DeepComparisonAgent(BaseAgent). Consumes similarity.detected event. Loads both ideas' context summaries + board content. Produces: { is_similar, confidence, explanation, overlap_areas }. If is_similar AND confidence > 0.7 → publish ai.similarity.confirmed. Core creates similarity record, Gateway notifies users.
5. **[Backend] Merge request APIs + merge execution** — POST /api/merge-requests (create). POST accept/decline. State-aware behavior: open/rejected → full merge, in_review → append, accepted/dropped → informational only. Merge execution: create new idea, set co-owners, transfer collaborators, set closed_by_merge on originals. Publish merge.request.resolved event for AI.
6. **[AI Service] Merge Synthesizer agent** — MergeSynthesizerAgent(BaseAgent). Consumes merge.request.resolved (status='accepted'). Loads full context for both ideas. Produces synthesis_message (first chat message) + board_instructions. Core creates merged idea with synthesis. Board Agent optionally executes board instructions for spatial layout.
7. **[Frontend] Similarity notification + merge request flow** — Similarity detected: both owners notified (in-app + email), granted read-only access to the other's idea. Either owner can request merge. Merge request banner on receiving idea: locked until owner accepts/rejects. Accept → merge proceeds. Decline → permanent dismissal, idea unlocks.
8. **[Frontend] Manual merge request + similar ideas in review** — Manual merge: user enters UUID/URL of target idea, or browses similar ideas list (title + keywords). Creates merge request to another active idea (recovery for accidental declines). Review section: similar ideas panel for reviewers — ideas above threshold that user rejected, ideas slightly below threshold.
9. **[Frontend] Merged idea experience** — New merged idea opens with AI synthesis message as first chat. Merged board with combined/deduplicated topics. Both owners shown as co-owners. All collaborators from both originals added. Old ideas: read-only with reference text + link to merged idea. Users can reference old idea content.

## Milestone Acceptance Criteria
- [ ] Keyword Agent generates abstract keywords during each AI processing cycle
- [ ] Idea embeddings update after keyword generation
- [ ] Background matching detects similar pairs (vector + keyword overlap)
- [ ] Deep Comparison confirms genuine similarity with confidence score
- [ ] Both owners notified with read-only cross-access on similarity detection
- [ ] Merge request: request → consent → merged idea created correctly
- [ ] Merge Synthesizer produces synthesis message + merged board content
- [ ] State-aware behavior: merge (open), append (in_review), info (accepted/dropped)
- [ ] Merge request banner: locks receiving idea, accept/decline buttons work
- [ ] Manual merge request via UUID/URL or similar ideas list works
- [ ] Permanent dismissal prevents same pair from being suggested again
- [ ] Similar ideas panel in review section displays correctly
- [ ] Old merged ideas are read-only with reference to new idea
- [ ] Recursive merge: 2-owner limit enforced (previous co-owners demoted to collaborators)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M9

## Notes
- Keyword Agent was stubbed in M5 (keywords generated but not persisted). This milestone activates persistence and the downstream pipeline.
- The append flow (open idea → in_review idea) requires consent from open owner + in_review owner + one assigned reviewer. More complex consent model than merge.
- Recursive merge handling: if a previously-merged idea (2 owners) merges again, the two users who triggered the merge become co-owners, previous co-owners demoted to collaborators (enforcing 2-owner max).
- Background matching task should run on a configurable schedule (e.g., every 5 minutes).
