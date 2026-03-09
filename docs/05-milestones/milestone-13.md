# Milestone 13: Similarity Detection & Merge

## Overview
- **Execution order:** 13 (runs after M8 and M12)
- **Estimated stories:** 10
- **Dependencies:** M8, M12
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-5.2 | Background Keyword Matching | P1 | features.md FA-5 |
| F-5.3 | AI Deep Comparison | P1 | features.md FA-5 |
| F-5.4 | State-Aware Match Behavior | P1 | features.md FA-5 |
| F-5.5 | Merge Flow (Open/Rejected Ideas) | P1 | features.md FA-5 |
| F-5.6 | Merge Request UI | P1 | features.md FA-5 |
| F-5.7 | Permanent Dismissal | P1 | features.md FA-5 |
| F-4.12 | Similar Ideas in Review Section | P1 | features.md FA-4 |
| F-12.4 | Merge Request Banner | P1 | features.md FA-12 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| idea_keywords | SELECT (matching) | idea_id, keywords | data-model.md |
| idea_embeddings | SELECT (vector similarity) | idea_id, embedding | data-model.md |
| merge_requests | INSERT, UPDATE, SELECT | requesting_idea_id, target_idea_id, merge_type, status, consents | data-model.md |
| ideas | INSERT (merged idea), UPDATE (closed_by_merge) | All columns for new idea | data-model.md |
| idea_collaborators | INSERT (transfer collaborators to merged idea) | idea_id, user_id | data-model.md |
| chat_messages | INSERT (synthesis message in merged idea) | content, sender_type='ai' | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/merge-request | POST | Create merge request | Bearer | api-design.md |
| /api/merge-requests/:id/consent | POST | Accept/decline merge | Bearer | api-design.md |
| /api/ideas/:id/similar | GET | Get similar ideas for review section | Bearer | api-design.md |

## AI Agent References
| Agent | Purpose | Source |
|-------|---------|--------|
| Deep Comparison | Full-context similarity confirmation | agent-architecture.md S3.7 |
| Merge Synthesizer | Combine two ideas into merged context | agent-architecture.md S3.9 |

## Story Outline (Suggested Order)
1. **[Backend — Core]** Background keyword matching sweep — Celery periodic task, keyword set intersection, time window filter
2. **[Backend — Core]** Vector similarity detection — pgvector cosine similarity query on idea_embeddings, threshold check
3. **[Backend — AI]** Deep Comparison agent — compare two idea contexts, return is_similar + confidence + explanation
4. **[Backend]** Similarity notification flow — ai.similarity.confirmed event -> notify both owners (in-app + email)
5. **[Backend]** Similar ideas display — GET /api/ideas/:id/similar (declined merges + near-threshold matches)
6. **[Backend]** State-aware match behavior — open/rejected (mergeable), in_review (append), accepted/dropped (informational)
7. **[Backend]** Merge request API — create request, consent flow (both owners), status tracking
8. **[Frontend]** Merge request banner — workspace banner with accept/decline, idea locked until resolved
9. **[Backend — AI]** Merge Synthesizer agent — synthesis message + board instructions for merged idea
10. **[Backend + Frontend]** Merged idea creation — new idea with synthesis message, merged board, co-owners, collaborators transferred, old ideas read-only

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Keyword matching | ~6,000 | tech-stack.md (Background Matching), features.md (F-5.2) | 3-5 files | Medium | Celery task scheduling |
| 2 | Vector similarity | ~5,000 | data-model.md (idea_embeddings), agent-architecture.md (S6.4) | 2-3 files | Medium | pgvector query |
| 3 | Deep Comparison | ~5,000 | agent-architecture.md (S3.7), system-prompts.md | 3-4 files | Medium | — |
| 4 | Similarity notifications | ~4,000 | features.md (F-5.4), api-design.md (events) | 3-4 files | Low | — |
| 5 | Similar ideas display | ~4,000 | features.md (F-4.12) | 2-3 files | Low | — |
| 6 | State-aware behavior | ~5,000 | features.md (F-5.4) | 3-4 files | Medium | Multiple state paths |
| 7 | Merge request API | ~7,000 | api-design.md (merge), data-model.md (merge_requests) | 5-7 files | High | Dual consent tracking |
| 8 | Merge request banner | ~4,000 | component-specs.md (S11.5), features.md (F-5.6) | 2-3 files | Medium | Lock/unlock on resolve |
| 9 | Merge Synthesizer | ~6,000 | agent-architecture.md (S3.9, S4.4), system-prompts.md | 3-4 files | High | AI synthesis quality |
| 10 | Merged idea creation | ~8,000 | features.md (F-5.5), data-model.md (ideas, collaborators) | 6-8 files | High | Atomic multi-table operation |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~54,000
- **Cumulative domain size:** Large (similarity pipeline + merge flow + 2 AI agents)
- **Information loss risk:** Medium (7) — cross-domain (Celery + AI + Core + Frontend)
- **Context saturation risk:** Medium
- **Heavy stories:** 3 (merge request API, Merge Synthesizer, merged idea creation)

## Milestone Acceptance Criteria
- [ ] Background keyword matching detects overlapping ideas
- [ ] Vector similarity detects semantically similar ideas
- [ ] Deep Comparison confirms genuine similarity (not false positive)
- [ ] Both owners notified when similarity detected
- [ ] Similar ideas displayed to reviewers in review section
- [ ] State-aware: open ideas mergeable, in_review appendable, accepted/dropped informational
- [ ] Merge request creates with dual consent tracking
- [ ] Merge request banner locks receiving idea until resolved
- [ ] Merge Synthesizer produces synthesis message + board instructions
- [ ] Merged idea created with co-owners, collaborators, synthesis message, merged board
- [ ] Old ideas become read-only with reference to merged idea
- [ ] Declined merge permanently dismissed (same pair never re-suggested)
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M12

## Notes
- Append flow (open -> in_review) and manual merge request come in M14 (Merge Advanced).
- Recursive merge handling (co-owner demotion) comes in M14.
- Read-only access to other idea during similarity detection uses the same read-only link mechanism from M11.
