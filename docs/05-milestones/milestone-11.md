# Milestone 11: Collaboration & Sharing

## Overview
- **Execution order:** 11 (runs after M6)
- **Estimated stories:** 9
- **Dependencies:** M6
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-8.1 | Visibility Modes | P1 | features.md FA-8 |
| F-8.2 | Invite Flow | P1 | features.md FA-8 |
| F-8.3 | Read-Only Link Sharing | P1 | features.md FA-8 |
| F-8.4 | Collaborator Management | P1 | features.md FA-8 |
| F-12.3 | Floating Banner (Invitation) | P1 | features.md FA-12 |
| F-2.5 | Multi-User Awareness (AI addresses by name) | P1 | features.md FA-2 |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| collaboration_invitations | INSERT, UPDATE, SELECT | idea_id, inviter_id, invitee_id, status | data-model.md |
| idea_collaborators | INSERT, DELETE, SELECT | idea_id, user_id | data-model.md |
| ideas | UPDATE (visibility, share_link_token, owner_id, co_owner_id) | visibility, share_link_token | data-model.md |
| users | SELECT (directory search) | display_name, email | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas/:id/collaborators/invite | POST | Send invitation | Bearer (Owner) | api-design.md |
| /api/invitations/:id/accept | POST | Accept invitation | Bearer | api-design.md |
| /api/invitations/:id/decline | POST | Decline invitation | Bearer | api-design.md |
| /api/invitations/:id/revoke | POST | Revoke invitation | Bearer (Owner) | api-design.md |
| /api/ideas/:id/collaborators | GET | List collaborators | Bearer | api-design.md |
| /api/ideas/:id/collaborators/:userId | DELETE | Remove collaborator | Bearer (Owner) | api-design.md |
| /api/ideas/:id/transfer-ownership | POST | Transfer ownership | Bearer (Owner) | api-design.md |
| /api/ideas/:id/share-link | POST | Generate share link | Bearer (Owner) | api-design.md |
| /api/users/search | GET | Search user directory | Bearer | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| CollaboratorModal | Feature | component-inventory.md |
| PresenceIndicators | Feature | component-specs.md S9.2 |
| InvitationBanner | Feature | component-inventory.md |
| InvitationCard (wire accept/decline) | Feature | component-inventory.md |

## Story Outline (Suggested Order)
1. **[API]** Invitation REST API — invite, accept, decline, revoke, re-invite after decline
2. **[API]** Collaborator management — list, remove, transfer ownership, leave idea
3. **[API]** User directory search — GET /api/users/search (for invite flow)
4. **[API]** Read-only link sharing — generate share_link_token, access validation
5. **[API]** Visibility mode transitions — private->collaborating on first accepted invite
6. **[Frontend]** CollaboratorModal — invite search, collaborator list with remove, pending invitations, transfer ownership
7. **[Frontend]** Invitation display — wire accept/decline on InvitationCard (landing page) and InvitationBanner (workspace)
8. **[Frontend]** Read-only view — detect share link access, render workspace in read-only mode (no edit controls)
9. **[Frontend]** Multi-user awareness — sender names below chat bubbles in multi-user mode, co-owner rules (leaving constraints)

## Per-Story Complexity Assessment
| # | Story Title | Context Tokens (est.) | Upstream Docs Needed | Files Touched (est.) | Complexity | Risk |
|---|------------|----------------------|---------------------|---------------------|------------|------|
| 1 | Invitation API | ~6,000 | api-design.md (invitations), data-model.md | 4-6 files | Medium | Status transitions |
| 2 | Collaborator mgmt | ~6,000 | api-design.md (collaborators), features.md (F-8.4) | 4-5 files | Medium | Ownership transfer rules |
| 3 | User search | ~3,000 | api-design.md (users search) | 2-3 files | Low | — |
| 4 | Share link | ~4,000 | api-design.md, features.md (F-8.3) | 3-4 files | Medium | Token generation, auth check |
| 5 | Visibility modes | ~2,000 | features.md (F-8.1) | 1-2 files | Low | — |
| 6 | CollaboratorModal | ~6,000 | page-layouts.md (collaborator management), component-specs.md | 4-5 files | Medium | Multiple subviews |
| 7 | Invitation display | ~4,000 | component-specs.md (S11.5), page-layouts.md (banners) | 3-4 files | Medium | Banner + card wiring |
| 8 | Read-only view | ~4,000 | features.md (F-8.3), page-layouts.md | 3-4 files | Medium | Conditional edit controls |
| 9 | Multi-user awareness | ~3,000 | features.md (F-2.5, F-8.4) | 2-3 files | Low | — |

## Milestone Complexity Summary
- **Total context tokens (est.):** ~38,000
- **Cumulative domain size:** Medium (invitations + collaborators + sharing)
- **Information loss risk:** Low (4)
- **Context saturation risk:** Low
- **Heavy stories:** 0

## Milestone Acceptance Criteria
- [ ] Owner can invite users by searching the directory
- [ ] Invitee sees invitation on landing page and as banner in workspace
- [ ] Accept/decline works, collaborator gains edit access
- [ ] Owner can revoke pending invitations
- [ ] Owner can remove collaborators
- [ ] Ownership transfer works
- [ ] Single owner must transfer before leaving
- [ ] Visibility transitions from private to collaborating
- [ ] Read-only link generates and grants view-only access (requires auth)
- [ ] Chat shows sender names in multi-user mode
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1-M10

## Notes
- Co-owner rules (from merged ideas) are prepared but merge flow comes in M13-M14.
- Notification events for collaboration (invite, join, leave, remove) are wired in M12.
