# API Design

## API Pattern

- **Style:** REST (Django REST Framework) for all data mutations and queries
- **Real-time:** WebSocket (Django Channels) for event broadcasting and ephemeral interactions
- **Base URL:** `/api/` (no versioning — internal single-release application)
- **WebSocket URL:** `/ws/`
- **Auth (REST):** Bearer token in `Authorization` header (Azure AD JWT). Dev bypass mode uses session-based fake auth.
- **Auth (WebSocket):** Token passed in connection handshake query parameter (`/ws/?token=<jwt>`)
- **Content-Type:** `application/json` for all requests and responses

## Communication Pattern

```
┌──────────┐     REST (mutations/queries)     ┌─────────────┐     gRPC      ┌────────────────┐
│ Frontend │ ──────────────────────────────── │ API Gateway │ ────────────── │ Internal       │
│ (React)  │                                  │ (Django)    │               │ Microservices  │
│          │ ◄── WebSocket (broadcasts) ───── │             │ ◄── Events ── │                │
└──────────┘                                  └─────────────┘               └────────────────┘
```

- **Persistent changes** (chat, reactions, requirements structure, state changes) → REST POST/PATCH → server persists → WebSocket broadcast to all connected users on the project
- **Ephemeral events** (selections, typing, presence) → WebSocket only, no persistence

---

## REST Endpoints

### Authentication

#### POST /api/auth/validate
- **Purpose:** Validate Azure AD token and sync user to shadow table. Called on app load.
- **Auth:** Bearer token (Azure AD JWT)
- **Request:** No body. Token in Authorization header.
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "display_name": "string",
    "roles": ["user", "reviewer"],
    "email_notification_preferences": {}
  }
  ```
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 401 | TOKEN_INVALID | Token expired, malformed, or not from trusted tenant |

#### GET /api/auth/dev-users
- **Purpose:** List available dev users (auth bypass mode only)
- **Auth:** None (bypass mode)
- **Guard:** Returns 404 unless `AUTH_BYPASS=True AND DEBUG=True`
- **Response (200):**
  ```json
  {
    "users": [
      { "id": "uuid", "display_name": "Dev User 1", "roles": ["user"] },
      { "id": "uuid", "display_name": "Dev User 2", "roles": ["user"] },
      { "id": "uuid", "display_name": "Dev User 3", "roles": ["user", "reviewer"] },
      { "id": "uuid", "display_name": "Dev User 4", "roles": ["user", "admin"] }
    ]
  }
  ```

#### POST /api/auth/dev-login
- **Purpose:** Login as a dev user (auth bypass mode only)
- **Auth:** None (bypass mode)
- **Guard:** Returns 404 unless `AUTH_BYPASS=True AND DEBUG=True`
- **Request:**
  ```json
  { "user_id": "uuid" }
  ```
- **Response (200):** Same shape as `/api/auth/validate`

---

### Projects

#### POST /api/projects
- **Purpose:** Create a new project
- **Auth:** Authenticated
- **Request:**
  ```json
  {
    "project_type": "software | non_software — required",
    "first_message": "string — optional initial message"
  }
  ```
- **Response (201):**
  ```json
  {
    "id": "uuid",
    "title": "",
    "state": "open",
    "visibility": "private",
    "agent_mode": "interactive",
    "project_type": "software",
    "owner": { "id": "uuid", "display_name": "string" },
    "created_at": "iso8601"
  }
  ```
- **Side effects:** If first_message provided, it is created as initial chat message and AI processing triggered after debounce.

#### GET /api/projects
- **Purpose:** List current user's projects (landing page)
- **Auth:** Authenticated
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | filter | string | `my_projects` / `collaborating` / `invitations` / `trash` (default: all) |
  | state | string | `open` / `in_review` / `accepted` / `dropped` / `rejected` (optional) |
  | search | string | Search by title (optional) |
  | page | int | Page number (default: 1) |
  | page_size | int | Items per page (default: 20) |
- **Response (200):**
  ```json
  {
    "results": [
      {
        "id": "uuid",
        "title": "string",
        "state": "open",
        "visibility": "private",
        "project_type": "software",
        "role": "owner",
        "owner": { "id": "uuid", "display_name": "string" },
        "collaborator_count": 2,
        "inviter_display_name": "string | null",
        "updated_at": "iso8601",
        "deleted_at": null
      }
    ],
    "count": 42,
    "page": 1,
    "page_size": 20
  }
  ```
  > **Note:** `inviter_display_name` is populated only when `filter=invitations`. For other filters it is `null`. Resolved by the gateway enrichment layer from the `inviter_id` field in the gRPC `ProjectListItem` message (fields 10-11 added for invitations support).

#### GET /api/projects/:id
- **Purpose:** Get full project state (workspace load)
- **Auth:** Authenticated + project access (owner, co-owner, collaborator, or read-only via share link)
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "title": "string",
    "title_manually_edited": false,
    "state": "open",
    "visibility": "collaborating",
    "agent_mode": "interactive",
    "project_type": "software",
    "owner": { "id": "uuid", "display_name": "string" },
    "collaborators": [
      { "id": "uuid", "display_name": "string" }
    ],
    "share_link_token": null,
    "review_assignments": [],
    "has_been_submitted": false,
    "created_at": "iso8601",
    "updated_at": "iso8601",
    "user_role": "owner",
    "is_locked": false
  }
  ```
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 403 | ACCESS_DENIED | User has no access to this project |
  | 404 | NOT_FOUND | Project does not exist |

#### PATCH /api/projects/:id
- **Purpose:** Update project properties (title, agent_mode)
- **Auth:** Owner or co-owner
- **Request:**
  ```json
  {
    "title": "string — optional",
    "agent_mode": "silent — optional"
  }
  ```
- **Response (200):** Updated project object
- **Side effects:** If title is changed manually, `title_manually_edited` set to true permanently. Title change broadcast via WebSocket.

#### DELETE /api/projects/:id
- **Purpose:** Soft delete a project (move to trash)
- **Auth:** Owner or co-owner
- **Response (200):**
  ```json
  { "message": "Project moved to trash", "deleted_at": "iso8601" }
  ```

#### POST /api/projects/:id/restore
- **Purpose:** Restore project from trash
- **Auth:** Owner or co-owner
- **Response (200):**
  ```json
  { "message": "Project restored" }
  ```

#### POST /api/projects/:id/share-link
- **Purpose:** Generate a read-only share link
- **Auth:** Owner or co-owner
- **Response (201):**
  ```json
  { "share_link_token": "string", "share_url": "/project/<uuid>?share=<token>" }
  ```

#### DELETE /api/projects/:id/share-link
- **Purpose:** Revoke share link
- **Auth:** Owner or co-owner
- **Response (200):**
  ```json
  { "message": "Share link revoked" }
  ```

---

### Chat

#### GET /api/projects/:id/chat
- **Purpose:** Load chat history (paginated, newest last)
- **Auth:** Project access
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | offset | int | Number of messages to skip (default: 0) |
  | limit | int | Number of messages to return (default: 50, max: 100) |
- **Response (200):**
  ```json
  {
    "messages": [
      {
        "id": "uuid",
        "sender_type": "user",
        "sender": { "id": "uuid", "display_name": "string" },
        "ai_agent": null,
        "content": "string",
        "message_type": "regular",
        "reactions": {
          "ai": null,
          "users": [
            { "user_id": "uuid", "display_name": "string", "reaction_type": "thumbs_up" }
          ]
        },
        "created_at": "iso8601"
      }
    ],
    "total": 42,
    "limit": 50,
    "offset": 0
  }
  ```

#### POST /api/projects/:id/chat
- **Purpose:** Send a chat message
- **Auth:** Owner, co-owner, or collaborator. Project state must allow editing (not locked).
- **Request:**
  ```json
  {
    "content": "string"
  }
  ```
- **Response (201):** Created message object
- **Side effects:** Message broadcast via WebSocket. AI processing triggered after debounce (unless rate limit reached).
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 403 | PROJECT_LOCKED | Project is in a locked state (in_review, accepted, dropped) |
  | 429 | RATE_LIMITED | Chat rate cap reached, waiting for AI processing (F-2.11) |

---

### Reactions

#### POST /api/projects/:id/chat/:messageId/reactions
- **Purpose:** Add a user reaction to another user's message
- **Auth:** Project access (edit permissions)
- **Request:**
  ```json
  { "reaction_type": "thumbs_up" }
  ```
- **Response (201):** Created reaction
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 400 | CANNOT_REACT_TO_AI | Target message is from AI |
  | 400 | CANNOT_REACT_TO_SELF | Target message is from the same user |
  | 409 | ALREADY_REACTED | User already reacted to this message |

#### DELETE /api/projects/:id/chat/:messageId/reactions
- **Purpose:** Remove own reaction
- **Auth:** Reaction owner
- **Response (204):** No content

---

### Requirements Document

#### GET /api/projects/:id/requirements
- **Purpose:** Get current requirements document structure
- **Auth:** Project access
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "project_type": "software",
    "structure": {
      "items": [
        {
          "id": "uuid",
          "type": "epic",
          "title": "string",
          "description": "string",
          "order": 0,
          "children": [
            {
              "id": "uuid",
              "type": "user_story",
              "title": "string",
              "description": "string",
              "order": 0
            }
          ]
        }
      ]
    },
    "last_generated_at": "iso8601 or null",
    "last_updated_at": "iso8601"
  }
  ```
- **Notes:** For software projects, items are epics containing user stories. For non_software projects, items are milestones containing work packages.

#### POST /api/projects/:id/requirements/generate
- **Purpose:** Trigger AI generation of requirements structure
- **Auth:** Owner, co-owner, or collaborator
- **Request:** No body
- **Response (202 Accepted):**
  ```json
  { "message": "Requirements generation started" }
  ```
- **Validation:**
  - Project state must be 'open'
- **Side effects:**
  - Gateway invokes AI service gRPC method
  - AI service publishes event after completion
  - Result delivered via WebSocket `requirements_ready` event
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 400 | INVALID_STATE | Project not in 'open' state |
  | 403 | FORBIDDEN | User not owner/co-owner/collaborator |
  | 503 | SERVICE_UNAVAILABLE | AI service gRPC call failed |

#### POST /api/projects/:id/requirements/items
- **Purpose:** Add a new top-level requirement item (epic or milestone)
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Request:**
  ```json
  {
    "title": "string",
    "description": "string — optional"
  }
  ```
- **Response (201):** Created item object
- **Side effects:** WebSocket broadcast

#### PATCH /api/projects/:id/requirements/items/:itemId
- **Purpose:** Update a requirement item
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Request:**
  ```json
  {
    "title": "string — optional",
    "description": "string — optional"
  }
  ```
- **Response (200):** Updated item object
- **Side effects:** WebSocket broadcast

#### DELETE /api/projects/:id/requirements/items/:itemId
- **Purpose:** Delete a requirement item and all its children
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Response (204):** No content
- **Side effects:** WebSocket broadcast

#### POST /api/projects/:id/requirements/items/:itemId/children
- **Purpose:** Add a child requirement (user story or work package)
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Request:**
  ```json
  {
    "title": "string",
    "description": "string — optional"
  }
  ```
- **Response (201):** Created child object
- **Side effects:** WebSocket broadcast

#### PATCH /api/projects/:id/requirements/items/:itemId/children/:childId
- **Purpose:** Update a child requirement
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Request:**
  ```json
  {
    "title": "string — optional",
    "description": "string — optional"
  }
  ```
- **Response (200):** Updated child object
- **Side effects:** WebSocket broadcast

#### DELETE /api/projects/:id/requirements/items/:itemId/children/:childId
- **Purpose:** Delete a child requirement
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Response (204):** No content
- **Side effects:** WebSocket broadcast

#### POST /api/projects/:id/requirements/reorder
- **Purpose:** Reorder requirements items or children
- **Auth:** Owner, co-owner, or collaborator. Project not in review.
- **Request:**
  ```json
  {
    "item_id": "uuid — optional, if reordering children",
    "ordered_ids": ["uuid1", "uuid2", "uuid3"]
  }
  ```
- **Response (200):**
  ```json
  { "message": "Reordered successfully" }
  ```
- **Side effects:** WebSocket broadcast

#### GET /api/projects/:id/requirements/versions
- **Purpose:** List all requirements versions (immutable snapshots)
- **Auth:** Project access
- **Response (200):**
  ```json
  {
    "versions": [
      { "id": "uuid", "version_number": 1, "created_at": "iso8601", "has_pdf": true },
      { "id": "uuid", "version_number": 2, "created_at": "iso8601", "has_pdf": true }
    ]
  }
  ```

#### GET /api/projects/:id/requirements/versions/:versionId/pdf
- **Purpose:** Download PDF for a specific requirements version
- **Auth:** Project access
- **Response (200):** PDF file (Content-Type: application/pdf)
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 404 | PDF_NOT_FOUND | PDF not yet generated for this version |

#### GET /api/projects/:id/requirements/pdf/preview
- **Purpose:** Generate and preview PDF from current requirements document (draft, not persisted)
- **Auth:** Owner, co-owner, or collaborator
- **Response (200):** PDF file bytes (Content-Type: application/pdf). Binary PDF data returned directly.
- **Notes:**
  - PDF generated on-demand via Gateway → PDF Service gRPC call (`GeneratePdf`)
  - Frontend uses `<object type="application/pdf" data="/api/projects/:id/requirements/pdf/preview">` for preview in PDFPreviewPanel
  - Download button creates temporary `<a>` element with blob URL from fetch response
  - PDF not persisted for drafts — only for submitted versions (via POST /submit)

---

### Review Workflow

#### POST /api/projects/:id/submit
- **Purpose:** Submit project for review
- **Auth:** Owner or co-owner. Project state must be `open` or `rejected`.
- **Request:**
  ```json
  {
    "message": "string — optional submit message (becomes first timeline comment)",
    "reviewer_ids": ["uuid — optional, specific reviewer assignments"]
  }
  ```
- **Response (200):**
  ```json
  {
    "state": "in_review",
    "version": { "id": "uuid", "version_number": 1 }
  }
  ```
- **Side effects:** Requirements document snapshotted to version. State transition to `in_review`. Requirements assembly section locks. Reviewers notified (email + in-app).

#### POST /api/projects/:id/review/accept
- **Purpose:** Accept a project
- **Auth:** Assigned reviewer (not project owner)
- **Request:** No body
- **Response (200):**
  ```json
  { "state": "accepted" }
  ```
- **Side effects:** Everything read-only. Owner notified by email.

#### POST /api/projects/:id/review/reject
- **Purpose:** Reject a project (return for rework)
- **Auth:** Assigned reviewer (not project owner)
- **Request:**
  ```json
  { "comment": "string — mandatory" }
  ```
- **Response (200):**
  ```json
  { "state": "rejected" }
  ```
- **Side effects:** Requirements assembly unlocks. Owner notified by email. Comment added to timeline.
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 400 | COMMENT_REQUIRED | Comment is empty or missing |

#### POST /api/projects/:id/review/drop
- **Purpose:** Drop a project (permanently close)
- **Auth:** Assigned reviewer (not project owner)
- **Request:**
  ```json
  { "comment": "string — mandatory" }
  ```
- **Response (200):**
  ```json
  { "state": "dropped" }
  ```
- **Side effects:** Everything read-only. Owner notified by email. Comment added to timeline.

#### POST /api/projects/:id/review/undo
- **Purpose:** Undo the last review action (returns to in_review)
- **Auth:** Any assigned reviewer
- **Request:**
  ```json
  { "comment": "string — mandatory" }
  ```
- **Response (200):**
  ```json
  { "state": "in_review" }
  ```
- **Side effects:** State returns to in_review. Comment added to timeline.

#### GET /api/projects/:id/review/timeline
- **Purpose:** Load review timeline entries
- **Auth:** Project access (review section visible)
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | page | int | Page number (default: 1) |
  | page_size | int | Items per page (default: 50) |
- **Response (200):**
  ```json
  {
    "entries": [
      {
        "id": "uuid",
        "entry_type": "comment",
        "author": { "id": "uuid", "display_name": "string" },
        "content": "string",
        "parent_entry_id": null,
        "replies": [
          {
            "id": "uuid",
            "entry_type": "comment",
            "author": { "id": "uuid", "display_name": "string" },
            "content": "reply text",
            "created_at": "iso8601"
          }
        ],
        "created_at": "iso8601"
      },
      {
        "id": "uuid",
        "entry_type": "state_change",
        "author": { "id": "uuid", "display_name": "string" },
        "content": "Project accepted",
        "old_state": "in_review",
        "new_state": "accepted",
        "created_at": "iso8601"
      },
      {
        "id": "uuid",
        "entry_type": "resubmission",
        "author": { "id": "uuid", "display_name": "string" },
        "content": "Reworked based on feedback",
        "old_version": { "id": "uuid", "version_number": 1 },
        "new_version": { "id": "uuid", "version_number": 2 },
        "created_at": "iso8601"
      }
    ],
    "pagination": {
      "count": 15,
      "page": 1,
      "page_size": 50
    }
  }
  ```

#### POST /api/projects/:id/review/timeline
- **Purpose:** Post a comment on the review timeline
- **Auth:** Owner, co-owner, collaborator, or assigned reviewer
- **Request:**
  ```json
  {
    "content": "string",
    "parent_entry_id": "uuid — optional, for nested replies"
  }
  ```
- **Response (201):** Created timeline entry

#### GET /api/projects/:id/review/reviewers
- **Purpose:** Get assigned reviewers for a project (ReviewSection header display)
- **Auth:** Project access (review section visible)
- **Response (200):**
  ```json
  {
    "reviewers": [
      { "id": "uuid", "display_name": "string" }
    ]
  }
  ```

---

### Review Page (Reviewers)

#### GET /api/reviews
- **Purpose:** List submitted projects for the review page
- **Auth:** Reviewer role
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | group | string | `assigned_to_me` / `unassigned` / `accepted` / `rejected` / `dropped` (optional, default: all) |
  | search | string | Search by title or UUID |
  | page | int | Page number |
  | page_size | int | Items per page |
- **Response (200):**
  ```json
  {
    "assigned_to_me": [
      {
        "project_id": "uuid",
        "title": "string",
        "state": "in_review",
        "owner": { "id": "uuid", "display_name": "string" },
        "owner_id": "uuid",
        "submitted_at": "iso8601",
        "reviewers": [
          { "id": "uuid", "display_name": "string" }
        ],
        "timeline_count": 5
      }
    ],
    "unassigned": [],
    "accepted": [],
    "rejected": [],
    "dropped": [],
    "counts": {
      "assigned_to_me": 3,
      "unassigned": 7,
      "accepted": 12,
      "rejected": 4,
      "dropped": 2
    }
  }
  ```
- **Note:** `owner_id` added to support frontend conflict-of-interest checks (disable assign button for own projects)

#### POST /api/reviews/:projectId/assign
- **Purpose:** Self-assign to a project for review
- **Auth:** Reviewer role. Cannot assign to own project.
- **Response (200):**
  ```json
  { "message": "Assigned", "assigned_at": "iso8601" }
  ```
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 400 | CONFLICT_OF_INTEREST | Reviewer is the project owner |

#### POST /api/reviews/:projectId/unassign
- **Purpose:** Unassign self from a review
- **Auth:** Assigned reviewer
- **Response (200):**
  ```json
  { "message": "Unassigned" }
  ```

#### GET /api/reviews/reviewers
- **Purpose:** List all users with reviewer role (for submit flow multi-select)
- **Auth:** Authenticated (owner/co-owner submitting project)
- **Response (200):**
  ```json
  {
    "reviewers": [
      { "id": "uuid", "display_name": "string" }
    ]
  }
  ```
- **Implementation:** Backend filters by `roles__contains=["reviewer"]` using PostgreSQL array containment.

---

### Collaboration

#### POST /api/projects/:id/collaborators/invite
- **Purpose:** Invite a user to collaborate
- **Auth:** Owner or co-owner
- **Request:**
  ```json
  { "user_id": "uuid" }
  ```
- **Response (201):**
  ```json
  { "invitation_id": "uuid", "status": "pending" }
  ```
- **Side effects:** Email notification + in-app notification to invitee.

#### GET /api/projects/:id/collaborators
- **Purpose:** List collaborators, roles, and pending invitations for this project
- **Auth:** Project access (owner, co-owner, collaborator, or share link)
- **Response (200):**
  ```json
  {
    "collaborators": [
      {
        "user_id": "uuid",
        "display_name": "string",
        "role": "owner | co_owner | collaborator"
      }
    ],
    "pending_invitations": [
      {
        "id": "uuid",
        "invitee_id": "uuid",
        "invitee_display_name": "string",
        "created_at": "iso8601"
      }
    ]
  }
  ```
- **Notes:** Combines data from GetProject (owner/co-owner) and ListCollaborators gRPC calls. Display names enriched via bulk UUID resolution.

#### DELETE /api/projects/:id/collaborators/:userId
- **Purpose:** Remove a collaborator from the project
- **Auth:** Owner or co-owner
- **Response (204):** No content
- **Side effects:** Removed user notified. WebSocket presence updated.

#### POST /api/projects/:id/collaborators/transfer
- **Purpose:** Transfer ownership to a collaborator
- **Auth:** Owner or co-owner
- **Request:**
  ```json
  { "new_owner_id": "uuid" }
  ```
- **Response (200):**
  ```json
  { "message": "Ownership transferred" }
  ```

#### POST /api/projects/:id/collaborators/leave
- **Purpose:** Leave a project voluntarily
- **Auth:** Co-owner (can leave freely) or collaborator. Single owner must transfer first.
- **Response (200):**
  ```json
  { "message": "Left project" }
  ```
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 400 | MUST_TRANSFER_OWNERSHIP | Single owner trying to leave without transferring |

#### GET /api/invitations
- **Purpose:** List pending invitations for current user (landing page)
- **Auth:** Authenticated
- **Response (200):**
  ```json
  {
    "invitations": [
      {
        "id": "uuid",
        "project_id": "uuid",
        "project_title": "string",
        "inviter": { "id": "uuid", "display_name": "string" },
        "created_at": "iso8601"
      }
    ]
  }
  ```
- **Notes:** Uses `ListProjects(filter="invitations")` internally, which returns `ProjectListItem`. The `created_at` field is the project's `updated_at` timestamp (closest available proxy — no invitation-specific timestamp exists in the `ProjectListItem` proto message).

#### POST /api/invitations/:id/accept
- **Purpose:** Accept a collaboration invitation
- **Auth:** Invitee
- **Response (200):**
  ```json
  { "message": "Invitation accepted", "project_id": "uuid" }
  ```
- **Side effects:** User added to project_collaborators. Visibility set to `collaborating`. Collaborator joined notification.

#### POST /api/invitations/:id/decline
- **Purpose:** Decline a collaboration invitation
- **Auth:** Invitee
- **Response (200):**
  ```json
  { "message": "Invitation declined" }
  ```

#### DELETE /api/invitations/:id
- **Purpose:** Revoke a pending invitation (owner action)
- **Auth:** Invitation inviter (project owner)
- **Response (204):** No content

#### GET /api/projects/:id/invitations
- **Purpose:** List pending invitations for a specific project (for Pending Invitations tab in CollaboratorModal)
- **Auth:** Owner only
- **Response (200):**
  ```json
  {
    "invitations": [
      {
        "id": "uuid",
        "invitee_id": "uuid",
        "invitee_display_name": "string",
        "created_at": "iso8601",
        "status": "pending"
      }
    ]
  }
  ```
- **Notes:** Complements `GET /api/invitations` which returns invitations *to* the current user. This endpoint returns invitations *from* the owner for a specific project.

---

### Notifications

#### GET /api/notifications
- **Purpose:** List persistent notifications (notification bell)
- **Auth:** Authenticated
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | unread_only | bool | Only unread notifications (default: false) |
  | page | int | Page number |
  | page_size | int | Items per page (default: 20) |
- **Response (200):**
  ```json
  {
    "notifications": [
      {
        "id": "uuid",
        "event_type": "collaboration_invitation",
        "title": "string",
        "body": "string",
        "reference_id": "uuid",
        "reference_type": "invitation | project",
        "is_read": false,
        "action_taken": false,
        "created_at": "iso8601"
      }
    ],
    "unread_count": 5,
    "count": 42,
    "page": 1,
    "page_size": 20
  }
  ```

#### GET /api/notifications/unread-count
- **Purpose:** Get unread notification count (for badge)
- **Auth:** Authenticated
- **Response (200):**
  ```json
  { "unread_count": 5 }
  ```

#### PATCH /api/notifications/:id
- **Purpose:** Mark notification as read or action taken
- **Auth:** Notification recipient
- **Request:**
  ```json
  {
    "is_read": true,
    "action_taken": true
  }
  ```
- **Response (200):** Updated notification
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 404 | NOT_FOUND | Notification belongs to another user (prevents information leakage) |

#### POST /api/notifications/mark-all-read
- **Purpose:** Mark all notifications as read
- **Auth:** Authenticated
- **Response (200):**
  ```json
  { "message": "All notifications marked as read" }
  ```

---

### User

#### GET /api/users/me
- **Purpose:** Get current user profile
- **Auth:** Authenticated
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "display_name": "string",
    "roles": ["user", "reviewer"],
    "email_notification_preferences": {}
  }
  ```

#### GET /api/users/me/notification-preferences
- **Purpose:** Get email notification preferences with category grouping
- **Auth:** Authenticated
- **Response (200):**
  ```json
  {
    "categories": {
      "Collaboration": {
        "label": "Collaboration",
        "preferences": {
          "collaboration_invitation": true,
          "collaborator_joined": true,
          "collaborator_left": true,
          "ownership_transferred": true
        }
      },
      "Review": {
        "label": "Review",
        "preferences": {
          "review_submission": true,
          "review_decision": true,
          "review_comment": true
        }
      },
      "AI": {
        "label": "AI",
        "preferences": {
          "ai_processing_failed": true
        }
      },
      "Admin": {
        "label": "Admin",
        "preferences": {
          "monitoring_alert": true
        }
      }
    }
  }
  ```
- **Notes:** Each category returns `{label, preferences}` nested structure to support frontend display and future category metadata. Missing preference keys default to true (all enabled). Admin section only visible to admin-role users. Email language defaults to `DEFAULT_APP_LANGUAGE` env var (no per-user language preference in database).

#### PATCH /api/users/me/notification-preferences
- **Purpose:** Update email notification preferences (partial merge)
- **Auth:** Authenticated
- **Request:**
  ```json
  {
    "collaboration_invitation": false,
    "review_state_changed": true,
    "chat_mention": false
  }
  ```
- **Response (200):** Updated preferences

#### GET /api/users/search
- **Purpose:** Search users for invitations, reviewer assignment, @mentions
- **Auth:** Authenticated
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | q | string | Search query (name or email) |
  | limit | int | Max results (default: 10) |
- **Response (200):**
  ```json
  {
    "users": [
      { "id": "uuid", "display_name": "string", "email": "string" }
    ]
  }
  ```

---

### Admin

All admin endpoints require the `admin` role.

#### GET /api/admin/ai-context/facilitator
- **Purpose:** Get facilitator context bucket
- **Auth:** Admin role
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "content": "string",
    "updated_by": { "id": "uuid", "display_name": "string" },
    "updated_at": "iso8601"
  }
  ```

#### PATCH /api/admin/ai-context/facilitator
- **Purpose:** Update facilitator context bucket
- **Auth:** Admin role
- **Request:**
  ```json
  { "content": "string" }
  ```
- **Response (200):** Updated bucket

#### GET /api/admin/ai-context/company
- **Purpose:** Get company context bucket
- **Auth:** Admin role
- **Response (200):**
  ```json
  {
    "id": "uuid",
    "sections": {},
    "free_text": "string",
    "updated_by": { "id": "uuid", "display_name": "string" },
    "updated_at": "iso8601"
  }
  ```

#### PATCH /api/admin/ai-context/company
- **Purpose:** Update company context bucket
- **Auth:** Admin role
- **Request:**
  ```json
  {
    "sections": {},
    "free_text": "string"
  }
  ```
- **Response (200):** Updated bucket
- **Errors:**
  | Status | Code | When |
  |--------|------|------|
  | 500 | REINDEX_FAILED | gRPC re-indexing failed (DB update persists) |
- **Side effects:** Triggers AI service re-indexing via gRPC `update_context_agent_bucket`. If re-indexing fails, returns 500 but DB update persists (fire-and-fail pattern).

#### GET /api/admin/parameters
- **Purpose:** List all runtime parameters
- **Auth:** Admin role
- **Response (200):**
  ```json
  [
    {
      "key": "debounce_timer",
      "value": "3",
      "default_value": "3",
      "description": "Seconds after last chat message before AI processes",
      "data_type": "integer",
      "category": "Application",
      "updated_by": { "id": "uuid", "display_name": "string" },
      "updated_at": "iso8601"
    }
  ]
  ```
- **Notes:** Returns bare array (not wrapped in `{"parameters": [...]}`). Includes `data_type` and `category` fields for frontend grouping and validation. `updated_by` is enriched with display name.

#### PATCH /api/admin/parameters/:key
- **Purpose:** Update a runtime parameter (applies immediately)
- **Auth:** Admin role
- **Request:**
  ```json
  { "value": "5" }
  ```
- **Response (200):** Updated parameter

#### GET /api/admin/monitoring
- **Purpose:** Get monitoring dashboard data
- **Auth:** Admin role
- **Response (200):**
  ```json
  {
    "active_connections": 42,
    "projects_by_state": {
      "open": 150,
      "in_review": 23,
      "accepted": 87,
      "dropped": 12,
      "rejected": 5
    },
    "active_users": 38,
    "ai_stats": {
      "processing_count": 1234,
      "success_rate": 0.972,
      "latency_p50_ms": 1200.0,
      "latency_p95_ms": 3500.0,
      "total_input_tokens": 500000,
      "total_output_tokens": 150000,
      "error_count": 34
    },
    "dlq_message_count": 2,
    "service_health": [
      { "service": "Gateway", "status": "healthy", "latency_ms": 12, "last_check": "iso8601" },
      { "service": "AI Service", "status": "healthy", "latency_ms": 45, "last_check": "iso8601" },
      { "service": "PDF Service", "status": "healthy", "latency_ms": 8, "last_check": "iso8601" },
      { "service": "Database", "status": "healthy", "latency_ms": 3, "last_check": "iso8601" },
      { "service": "Redis", "status": "healthy", "latency_ms": 1, "last_check": "iso8601" },
      { "service": "Broker", "status": "healthy", "latency_ms": 5, "last_check": "iso8601" }
    ]
  }
  ```
- **Notes:** `ai_stats` fields reflect the actual `GetAiMetrics` RPC response shape. `service_health` is an array of objects (not a flat map) carrying per-service latency and last check timestamps. Health check results are stored in Redis by a Celery periodic task. `projects_by_state` counts exclude soft-deleted projects (`deleted_at IS NOT NULL`).

#### GET /api/admin/monitoring/alerts
- **Purpose:** Get current user's alert configuration
- **Auth:** Admin role
- **Response (200):**
  ```json
  {
    "user_id": "uuid",
    "is_active": true
  }
  ```
- **Notes:** Returns only the current admin user's own alert opt-in status (not all recipients). Uses upsert pattern (creates config row on first access with `is_active=false`).

#### PATCH /api/admin/monitoring/alerts
- **Purpose:** Update current user's alert configuration (opt in/out)
- **Auth:** Admin role
- **Request:**
  ```json
  { "is_active": true }
  ```
- **Response (200):**
  ```json
  {
    "user_id": "uuid",
    "is_active": true
  }
  ```

#### GET /api/admin/users/search
- **Purpose:** Search users with full profile and stats
- **Auth:** Admin role
- **Query params:**
  | Param | Type | Description |
  |-------|------|-------------|
  | q | string | Search query (name, first name, or email). **Optional** — if empty or omitted, returns all users. |
- **Response (200):**
  ```json
  {
    "users": [
      {
        "id": "uuid",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "display_name": "string",
        "roles": ["user", "reviewer"],
        "project_count": 5,
        "review_count": 12
      }
    ]
  }
  ```
- **Notes:** Empty query returns all users (different from regular `/api/users/search` which requires minimum 2 chars). Stats computed via subqueries: `project_count` (owned projects), `review_count` (review timeline entries).

---

### Context Window

#### GET /api/projects/:id/context-window
- **Purpose:** Get context window utilization data (for the indicator, F-2.14)
- **Auth:** Project access
- **Response (200):**
  ```json
  {
    "usage_percentage": 45.2,
    "compression_iterations": 2,
    "total_messages": 87,
    "compressed_messages": 50,
    "recent_messages": 37
  }
  ```

---

## WebSocket Protocol

### Inline Reference Formats

Chat message `content` supports inline reference format that the frontend parses and renders as interactive elements:

| Format | Example | Purpose | Rendering |
|--------|---------|---------|-----------|
| `@user[<user_id>]` | `@user[550e8400-e29b-41d4-a716-446655440000]` | @mention a user (F-2.9) | Rendered as clickable display name (resolved client-side from user data) |

**Generation:**
- **@user references:** Inserted by the frontend when the user selects a user from the mention dropdown in chat input. The AI Facilitator can also generate @user references in its responses when addressing a specific user in a multi-user conversation.

**Resolution:**
- The frontend resolves display names client-side from the project context (users from collaborator list).

### Connection

- **URL:** `/ws/?token=<jwt>`
- **Session-level:** One connection per browser session (F-6.1), not per project
- **Auth:** Token validated on handshake. Connection rejected if invalid.
- **Reconnection:** Automatic exponential backoff, max 30 seconds (admin-configurable, F-6.1)

### Message Format

All WebSocket messages use this envelope:

```json
{
  "type": "event_type",
  "project_id": "uuid — present when event is project-scoped",
  "payload": {}
}
```

### Client → Server Events

#### subscribe_project
Subscribe to real-time events for a project (sent when user navigates to project workspace).
```json
{ "type": "subscribe_project", "project_id": "uuid" }
```

#### unsubscribe_project
Stop receiving events for a project (sent when user leaves project workspace).
```json
{ "type": "unsubscribe_project", "project_id": "uuid" }
```

#### presence_update
Update presence state.
```json
{
  "type": "presence_update",
  "payload": {
    "state": "active | idle",
    "project_id": "uuid — current project, if any"
  }
}
```

#### typing_indicator
User is typing in chat (ephemeral).
```json
{
  "type": "typing_indicator",
  "project_id": "uuid",
  "payload": {
    "user": { "id": "uuid", "display_name": "string" }
  }
}
```

### Server → Client Events

#### chat_message
New chat message (user or AI). Broadcast to all users subscribed to the project.
```json
{
  "type": "chat_message",
  "project_id": "uuid",
  "payload": {
    "id": "uuid",
    "sender_type": "user | ai",
    "sender": { "id": "uuid", "display_name": "string" },
    "ai_agent": "facilitator | null",
    "content": "string",
    "message_type": "regular | delegation",
    "created_at": "iso8601"
  }
}
```

#### ai_reaction
AI placed a reaction on a message.
```json
{
  "type": "ai_reaction",
  "project_id": "uuid",
  "payload": {
    "message_id": "uuid",
    "reaction_type": "thumbs_up | thumbs_down | heart"
  }
}
```

#### user_reaction
User placed or removed a reaction.
```json
{
  "type": "user_reaction",
  "project_id": "uuid",
  "payload": {
    "message_id": "uuid",
    "user": { "id": "uuid", "display_name": "string" },
    "reaction_type": "thumbs_up | thumbs_down | heart",
    "action": "added | removed"
  }
}
```

#### ai_processing
AI processing state changed.
```json
{
  "type": "ai_processing",
  "project_id": "uuid",
  "payload": {
    "state": "started | completed | failed",
    "agent": "facilitator | summarizing"
  }
}
```

#### requirements_updated
Requirements structure changed.
```json
{
  "type": "requirements_updated",
  "project_id": "uuid",
  "payload": {
    "structure": { "..." : "requirements structure object" },
    "source": "user | ai"
  }
}
```

#### requirements_generating
Requirements generation started.
```json
{
  "type": "requirements_generating",
  "project_id": "uuid",
  "payload": {
    "message": "AI is generating requirements..."
  }
}
```

#### requirements_ready
Requirements generation completed.
```json
{
  "type": "requirements_ready",
  "project_id": "uuid",
  "payload": {
    "structure": { "..." : "requirements structure object" }
  }
}
```

#### presence_update
User presence changed for a subscribed project.
```json
{
  "type": "presence_update",
  "project_id": "uuid",
  "payload": {
    "user": { "id": "uuid", "display_name": "string" },
    "state": "online | idle | offline"
  }
}
```

#### typing_indicator
Another user is typing.
```json
{
  "type": "typing_indicator",
  "project_id": "uuid",
  "payload": {
    "user": { "id": "uuid", "display_name": "string" }
  }
}
```

#### title_update
Project title changed (by user or AI).
```json
{
  "type": "title_update",
  "project_id": "uuid",
  "payload": {
    "title": "string",
    "source": "user | ai"
  }
}
```

#### project_state_change
Project state transitioned.
```json
{
  "type": "project_state_change",
  "project_id": "uuid",
  "payload": {
    "old_state": "open",
    "new_state": "in_review",
    "changed_by": { "id": "uuid", "display_name": "string" }
  }
}
```

#### rate_limit
Chat rate limit state changed.
```json
{
  "type": "rate_limit",
  "project_id": "uuid",
  "payload": {
    "locked": true,
    "message_count": 5,
    "cap": 5
  }
}
```

#### notification
New notification for the current user (delivered regardless of which project is open).
```json
{
  "type": "notification",
  "payload": {
    "id": "uuid",
    "event_type": "collaboration_invitation",
    "title": "string",
    "body": "string",
    "reference_id": "uuid",
    "reference_type": "invitation | project",
    "created_at": "iso8601"
  }
}
```

#### collaborator_change
Collaborator joined, left, or was removed.
```json
{
  "type": "collaborator_change",
  "project_id": "uuid",
  "payload": {
    "event": "joined | left | removed | ownership_transferred",
    "user": { "id": "uuid", "display_name": "string" },
    "new_owner": { "id": "uuid", "display_name": "string — for ownership_transferred" }
  }
}
```

#### context_window_update
Context window utilization changed (after compression or new messages).
```json
{
  "type": "context_window_update",
  "project_id": "uuid",
  "payload": {
    "usage_percentage": 62.1,
    "compression_iterations": 3
  }
}
```

#### delegation_update
AI delegation message should be de-emphasized (actual response arrived).
```json
{
  "type": "delegation_update",
  "project_id": "uuid",
  "payload": {
    "delegation_message_id": "uuid",
    "status": "completed"
  }
}
```

---

## Error Response Format

All REST API errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

Common error codes:

| Status | Code | When |
|--------|------|------|
| 400 | VALIDATION_ERROR | Request body fails validation. `details` contains field-level errors. |
| 401 | TOKEN_INVALID | Missing, expired, or malformed auth token |
| 403 | ACCESS_DENIED | User lacks permission for this action |
| 403 | PROJECT_LOCKED | Project is in a state that prevents this action |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Conflicting state (e.g., already reacted, duplicate merge request) |
| 429 | RATE_LIMITED | Chat rate cap reached |
| 500 | INTERNAL_ERROR | Unexpected server error |

---

## Rate Limiting

| Endpoint Group | Limit | Window | Notes |
|---------------|-------|--------|-------|
| Chat messages (per project) | `chat_message_cap` (default: 5) | Resets when AI completes processing | F-2.11: application-level, shared across all users on a project |
| General API | No hard limit | — | Internal tool with ~2,000 users on corporate network. Monitor and add if needed. |

---

## Pagination

Two pagination strategies:

| Strategy | Used For | Parameters |
|----------|---------|------------|
| **Page-based** | Project lists, notifications, timeline, reviews, requirements versions | `page`, `page_size` |
| **Cursor-based** | Chat messages (append-only, load older) | `before` (message UUID), `limit` |

---

## gRPC Service Definitions

> Internal service-to-service communication via gRPC. Proto files live in `proto/`. See `project-structure.md` for directory layout.

### AI Service (`proto/ai.proto`)

> **Boundary note:** The AI service gRPC contract defines the interface between the gateway/core services and the AI service. The *internal* behavior of the AI service (agent orchestration, model selection, context assembly, processing pipeline) is defined by the AI Engineer in `docs/03-ai/`. The Architect defines the external contract (request/response shapes); the AI Engineer defines what happens inside.

The AI service exposes gRPC methods for triggering AI processing and managing AI-related data.

#### TriggerChatProcessing

Trigger the main AI processing pipeline for a chat message event.

- **Called by:** Gateway (after receiving a chat message via REST), or Core service via message broker event
- **Flow:** Gateway receives chat message → persists via Core gRPC → publishes `chat.message.created` event → AI service consumes event and runs pipeline
- **Note:** In practice, this is event-driven (message broker), not a direct gRPC call. The AI service listens for `chat.message.created` events. Documented here for completeness of the contract.

```protobuf
message ChatProcessingRequest {
  string project_id = 1;       // UUID of the project
  string message_id = 2;       // UUID of the triggering chat message
}

message ChatProcessingResponse {
  string status = 1;           // "accepted" | "aborted" | "error"
  string processing_id = 2;    // UUID tracking this processing cycle
}
```

#### TriggerRequirementsGeneration

Trigger requirements structure generation.

- **Called by:** Gateway (when user triggers requirements generation)

```protobuf
service AiService {
  rpc TriggerRequirementsGeneration(RequirementsGenerationRequest) returns (RequirementsGenerationResponse);
}

message RequirementsGenerationRequest {
  string project_id = 1;
  string project_type = 2;             // "software" | "non_software"
}

message RequirementsGenerationResponse {
  string status = 1;                   // "accepted" | "error"
  string generation_id = 2;            // UUID tracking this generation
}
```

**Async result delivery:** Requirements generation is async. The AI service publishes events when done, and the gateway `AIEventConsumer` handles the event, persists requirements structure via Core gRPC, and notifies frontend via WebSocket `requirements_ready` event.

#### TriggerContextReindex

Trigger re-chunking and re-embedding of the context agent bucket content.

- **Called by:** Internally by the AI service after a bucket update via `UpdateContextAgentBucket` gRPC (see below). Not a standalone external call.

```protobuf
message ContextReindexRequest {
  string bucket_id = 1;              // UUID of the context_agent_bucket
}

message ContextReindexResponse {
  string status = 1;                  // "accepted" | "error"
  int32 chunk_count = 2;             // Number of chunks created
}
```

**Flow:**
1. Admin updates context agent bucket via REST → Gateway → AI service gRPC `UpdateContextAgentBucket`
2. AI service persists bucket update (owns the table) → triggers re-indexing internally
3. AI service publishes `ai.context_bucket.updated` event (confirms save, includes chunk count)

#### Bucket Management

CRUD for AI context buckets. The AI service owns these tables — gateway calls AI gRPC directly.

```protobuf
service AiService {
  rpc GetFacilitatorBucket(Empty) returns (FacilitatorBucketResponse);
  rpc UpdateFacilitatorBucket(UpdateFacilitatorBucketRequest) returns (FacilitatorBucketResponse);
  rpc GetContextAgentBucket(Empty) returns (ContextAgentBucketResponse);
  rpc UpdateContextAgentBucket(UpdateContextAgentBucketRequest) returns (ContextAgentBucketResponse);
}

message FacilitatorBucketResponse {
  string id = 1;
  string content = 2;
  string updated_by_id = 3;
  string updated_at = 4;            // ISO 8601
}

message UpdateFacilitatorBucketRequest {
  string content = 1;
  string updated_by_id = 2;         // Admin user ID
}

message ContextAgentBucketResponse {
  string id = 1;
  string sections_json = 2;         // JSON-encoded sections object
  string free_text = 3;
  string updated_by_id = 4;
  string updated_at = 5;
}

message UpdateContextAgentBucketRequest {
  string sections_json = 1;         // JSON-encoded sections object
  string free_text = 2;
  string updated_by_id = 3;         // Admin user ID
}
```

**Side effect:** `UpdateContextAgentBucket` triggers re-indexing (re-chunk + re-embed) after persisting the update. Publishes `ai.context_bucket.updated` event when complete.

#### GetAiMetrics

Retrieve AI processing metrics for the monitoring dashboard.

- **Called by:** Gateway (for admin monitoring dashboard F-11.4)

```protobuf
service AiService {
  rpc GetAiMetrics(AiMetricsRequest) returns (AiMetricsResponse);
}

message AiMetricsRequest {
  string time_range = 1;             // "1h" | "24h" | "7d"
}

message AiMetricsResponse {
  int64 processing_count = 1;
  double success_rate = 2;
  double latency_p50_ms = 3;
  double latency_p95_ms = 4;
  int64 total_input_tokens = 5;
  int64 total_output_tokens = 6;
  int64 delegation_count = 7;
  int64 compression_count = 8;
  int64 error_count = 9;
  int64 abort_count = 10;
  int64 extension_count = 11;         // Context Extension agent invocations
}
```

### Core Service (`proto/core.proto`) — AI-Relevant Methods

The Core service provides data access methods called by the AI service during context assembly.

#### GetProjectContext

Retrieve full project context for AI processing. Single gRPC call that bundles all data the AI service needs.

```protobuf
service CoreService {
  rpc GetProjectContext(ProjectContextRequest) returns (ProjectContextResponse);
}

message ProjectContextRequest {
  string project_id = 1;
  int32 recent_message_limit = 2;    // Number of recent messages to include (default: 20)
  bool include_requirements = 3;     // Include requirements structure (for Summarizing AI)
}

message ProjectContextResponse {
  ProjectMetadata metadata = 1;
  repeated ChatMessage recent_messages = 2;
  RequirementsState requirements = 3; // Only if requested
  repeated UserInfo active_users = 4;
}

message ProjectMetadata {
  string project_id = 1;
  string title = 2;
  bool title_manually_edited = 3;
  string state = 4;
  string agent_mode = 5;
  string project_type = 6;           // "software" | "non_software"
  string owner_display_name = 7;
}

message ChatMessage {
  string id = 1;
  string sender_type = 2;            // "user" | "ai"
  string sender_display_name = 3;
  string content = 4;
  string message_type = 5;           // "regular" | "delegation"
  string created_at = 6;             // ISO 8601
  repeated Reaction reactions = 7;
}

message RequirementsState {
  string structure_json = 1;         // JSON-encoded requirements structure
}
```

> **Note:** The AI Engineer may request additional fields in `ProjectContextResponse` for context assembly needs. The Arch+AI Integrator will reconcile.

#### GetFullChatHistory

Retrieve the complete uncompressed chat history for a project. Used by the Context Extension agent to search for specific details in long conversations where context has been compressed.

```protobuf
service CoreService {
  rpc GetFullChatHistory(FullChatHistoryRequest) returns (FullChatHistoryResponse);
}

message FullChatHistoryRequest {
  string project_id = 1;
}

message FullChatHistoryResponse {
  repeated ChatMessage messages = 1;    // All messages, oldest first. Reuses ChatMessage from GetProjectContext.
}
```

- **Called by:** AI service (Context Extension agent — rare, only when compressed context exists and user references a specific old detail)
- **Performance note:** This returns ALL messages for a project. For long sessions (100+ messages), the response can be large. The Context Extension agent has a 90s timeout, so this is acceptable. Not called during normal processing cycles.

#### PersistAiOutput

Persist AI-generated outputs (chat messages, reactions, title updates, requirements mutations).

```protobuf
service CoreService {
  rpc PersistAiChatMessage(AiChatMessageRequest) returns (AiChatMessageResponse);
  rpc PersistAiReaction(AiReactionRequest) returns (AiReactionResponse);
  rpc UpdateProjectTitle(UpdateTitleRequest) returns (UpdateTitleResponse);
  rpc UpdateRequirementsStructure(UpdateRequirementsRequest) returns (UpdateRequirementsResponse);
  rpc GetRequirementsState(GetRequirementsRequest) returns (GetRequirementsResponse);
}
```

> **Implementation Note (M20):** The proto definitions above serve as API contracts and documentation. At runtime, the AI service accesses Core data via `CoreClient` using direct PostgreSQL queries rather than gRPC server calls. This pattern is consistent across all CoreClient operations and avoids unnecessary gRPC hop overhead, as all services share the same PostgreSQL database. The Core gRPC servicer implementation exists primarily as a stub — runtime operations use direct database access through CoreClient.

#### GetProjectsByState

Retrieve project counts grouped by state. Called by gateway for admin monitoring dashboard.

```protobuf
service CoreService {
  rpc GetProjectsByState(ProjectsByStateRequest) returns (ProjectsByStateResponse);
}

message ProjectsByStateRequest {}

message ProjectsByStateResponse {
  repeated StateCount counts = 1;
}

message StateCount {
  string state = 1;
  int32 count = 2;
}
```

#### GetUserStats

Retrieve per-user statistics (project count, review count). Called by gateway for admin user search.

```protobuf
service CoreService {
  rpc GetUserStats(GetUserStatsRequest) returns (UserStatsResponse);
}

message GetUserStatsRequest {
  string user_id = 1;
}

message UserStatsResponse {
  int32 project_count = 1;
  int32 review_count = 2;
}
```

#### GetRateLimitStatus

Check if chat rate limit is reached for a project. Called by AI service before processing.

```protobuf
service CoreService {
  rpc GetRateLimitStatus(RateLimitRequest) returns (RateLimitResponse);
}

message RateLimitRequest {
  string project_id = 1;
}

message RateLimitResponse {
  int32 current_count = 1;
  int32 cap = 2;
  bool is_locked = 3;
}
```

### PDF Service (`proto/pdf.proto`)

Stateless service that generates PDF files from requirements document content.

#### GeneratePdf

Generate a PDF from requirements document structure. Returns the PDF file as bytes.

- **Called by:** Gateway (when user triggers PDF generation or on submit)

```protobuf
service PdfService {
  rpc GeneratePdf(PdfGenerationRequest) returns (PdfGenerationResponse);
}

message PdfGenerationRequest {
  string project_id = 1;
  string project_title = 2;
  string project_type = 3;           // "software" | "non_software"
  string structure_json = 4;         // JSON-encoded requirements structure
  string generated_at = 5;           // ISO 8601 timestamp for PDF header
}

message PdfGenerationResponse {
  bytes pdf_data = 1;                // Raw PDF file bytes
  string filename = 2;              // Suggested filename (e.g., "Requirements_2026-03-02_ProjectTitle.pdf")
}
```

**Notes:**
- The PDF service receives hierarchical requirements structure as JSON and renders it appropriately based on project_type (Epics/User Stories vs Milestones/Work Packages).
- The gateway stores the returned PDF bytes in the file storage backend (Azure Blob Storage in production, local volume in development) and saves the path in `requirements_versions.pdf_file_path`.

### Gateway Service (`proto/gateway.proto`)

Exposes gRPC methods for internal services to push data to the gateway (which owns the users and notifications tables).

#### CreateNotification

Create a persistent notification for a user. Called by the notification service.

```protobuf
service GatewayService {
  rpc CreateNotification(CreateNotificationRequest) returns (CreateNotificationResponse);
  rpc GetUserPreferences(UserPreferencesRequest) returns (UserPreferencesResponse);
  rpc GetAlertRecipients(AlertRecipientsRequest) returns (AlertRecipientsResponse);
  rpc GetProjectDetails(ProjectDetailsRequest) returns (ProjectDetailsResponse);
}

message CreateNotificationRequest {
  string user_id = 1;
  string event_type = 2;
  string title = 3;
  string body = 4;
  string reference_id = 5;          // UUID of related entity
  string reference_type = 6;        // "project" | "invitation"
}

message CreateNotificationResponse {
  string notification_id = 1;
}

message UserPreferencesRequest {
  string user_id = 1;
}

message UserPreferencesResponse {
  string user_id = 1;
  string email = 2;
  string display_name = 3;
  map<string, bool> email_notification_preferences = 4;
}

message ProjectDetailsRequest {
  string project_id = 1;
  bool ensure_share_link_token = 2;  // If true, generates share_link_token if not present
}

message ProjectDetailsResponse {
  string title = 1;
  string owner_id = 2;
  string share_link_token = 3;       // Empty string if not generated
}
```

```protobuf
message AlertRecipientsRequest {}

message AlertRecipientsResponse {
  repeated AlertRecipient recipients = 1;
}

message AlertRecipient {
  string user_id = 1;
  string email = 2;
  string display_name = 3;
}
```

**Notes:**
- `CreateNotification` also triggers a WebSocket `notification` event to the target user (if online).
- `GetUserPreferences` is called by the notification service before sending emails, to check if the user has opted out of specific notification types.
- `GetAlertRecipients` returns admin users who have opted in to monitoring alerts (used by notification service to send alert emails).
- `GetProjectDetails` is called by the notification service to fetch project metadata (title, owner, share link) for constructing notification emails. The `ensure_share_link_token` parameter generates a share token on-demand using `secrets.token_hex(32)` if one doesn't exist.
- The gateway runs a gRPC server on port 50054 (separate from core 50051, ai 50052, pdf 50053).

---

## Message Broker Event Contracts

> Events are published to RabbitMQ (dev) / Azure Service Bus (prod). Each event has a topic/routing key and a JSON payload. Consumers subscribe to specific topics.

### Event Naming Convention

`<domain>.<entity>.<action>` — e.g., `chat.message.created`, `ai.processing.complete`

### Events Published by Core Service

| Event | Published When | Consumers | Payload |
|-------|---------------|-----------|---------|
| `chat.message.created` | User sends a chat message | AI service (triggers processing), Gateway (WebSocket broadcast) | `{ project_id, message_id, sender_id, sender_type, created_at }` |
| `project.state.changed` | Project state transition (submit, accept, drop, reject, undo) | Gateway | `{ project_id, old_state, new_state, changed_by, timestamp }` |
| `review.accepted` | Project accepted by reviewers | Notification service | `{ project_id, reviewer_id, timestamp }` |
| `review.rejected` | Project rejected by reviewers | Notification service | `{ project_id, reviewer_id, timestamp }` |
| `review.dropped` | Project dropped by reviewers | Notification service | `{ project_id, reviewer_id, timestamp }` |
| `project.submitted` | Project submitted for review | Notification service | `{ project_id, user_id, version_id, reviewer_ids[], message }` |
| `collaboration.invitation.created` | Owner invites a collaborator | Notification service | `{ invitation_id, project_id, inviter_id, invitee_id }` |
| `collaboration.invitation.responded` | Invitee accepts/declines | Notification service, Gateway | `{ invitation_id, project_id, invitee_id, status }` |
| `monitoring.alert` | Health check detects an unhealthy service | Notification service (email alert to opted-in admins) | `{ service, status, latency_ms, timestamp }` |
| `admin.parameter.updated` | Admin changes a runtime parameter | All services (cache invalidation) | `{ key, value, updated_by, timestamp }` |
| `review.comment.created` | Reviewer or owner posts a timeline comment | Notification service | `{ entry_id, project_id, author_id, parent_entry_id }` |

### Events Published by AI Service

> **Boundary note:** The AI service's internal event flow (which agent triggers what, processing pipeline stages) is the AI Engineer's domain. The events below define the external contracts that the gateway, core, and notification services consume.

| Event | Published When | Consumers | Payload |
|-------|---------------|-----------|---------|
| `ai.processing.started` | Pipeline begins for a project | Gateway (show "AI is processing" indicator) | `{ project_id, processing_id }` |
| `ai.chat_response.ready` | Facilitator generates a chat message | Gateway (persist via Core gRPC, broadcast via WebSocket) | `{ project_id, processing_id, content, message_type, language }` |
| `ai.reaction.ready` | Facilitator places a reaction | Gateway (persist via Core gRPC, broadcast via WebSocket) | `{ project_id, message_id, reaction_type }` |
| `ai.title.updated` | Facilitator updates the title | Gateway (persist via Core gRPC, broadcast via WebSocket) | `{ project_id, new_title }` |
| `ai.delegation.started` | Facilitator triggers Context Agent delegation | Gateway (broadcast delegation message to users) | `{ project_id, delegation_id, delegation_message }` |
| `ai.delegation.complete` | Context Agent finishes and Facilitator delivers contextualized response | Gateway (broadcast response, de-emphasize delegation message) | `{ project_id, delegation_id, response_content, delegation_message_id }` |
| `ai.processing.complete` | Full pipeline cycle finishes | Core (reset rate limit counter), Gateway (hide "AI is processing") | `{ project_id, processing_id, status }` |
| `ai.processing.failed` | Pipeline fails after retries exhausted | Gateway (show error toast), Monitoring | `{ project_id, processing_id, error_code, agent }` |
| `ai.requirements.generated` | Summarizing AI finishes requirements generation | Gateway (update requirements structure via Core gRPC, notify frontend via WebSocket requirements_ready) | `{ project_id, structure_json, project_type }` |
| `ai.context_bucket.updated` | AI service persists bucket update and re-indexes | Gateway (confirm save to admin via WebSocket) | `{ bucket_id, updated_by, chunk_count, timestamp }` |

### Events Published by AI Service (Security Monitoring)

> **Boundary note:** Security event types and detection mechanisms are defined by the AI Engineer. The events below are the monitoring interface.

| Event | Published When | Consumers | Payload |
|-------|---------------|-----------|---------|
| `ai.security.content_filter_triggered` | Azure content filter blocks input/output | Monitoring | `{ project_id, user_id, filter_category, filter_action, timestamp }` |
| `ai.security.jailbreak_detected` | Azure jailbreak detection fires | Monitoring | `{ project_id, user_id, timestamp }` |
| `ai.security.injection_pattern` | Known injection pattern detected in input | Monitoring | `{ project_id, user_id, pattern_type, timestamp }` |
| `ai.security.extension_fabrication_flag` | Context Extension output contains claims not matchable to chat history | Monitoring | `{ project_id, query, flagged_quotes: [...], timestamp }` |
| `ai.security.tool_rejection` | Tool plugin rejects an invalid operation | Monitoring | `{ project_id, agent, tool_name, error_code, timestamp }` |
| `ai.security.output_validation_fail` | Agent output fails format or constraint validation | Monitoring | `{ project_id, agent, validation_type, timestamp }` |

### Events Published by Gateway

| Event | Published When | Consumers | Payload |
|-------|---------------|-----------|---------|
| `user.connected` | User WebSocket connection established | Monitoring (active connections count) | `{ user_id, project_id, timestamp }` |
| `user.disconnected` | User WebSocket connection closed | Monitoring | `{ user_id, project_id, timestamp }` |

### Notification Service

The notification service is a pure consumer — it does not publish events. It receives events and:
1. Creates persistent notifications via Gateway gRPC
2. Sends email notifications based on user preferences

### Event Delivery Guarantees

| Property | Setting | Rationale |
|----------|---------|-----------|
| Delivery | At-least-once | Consumers must be idempotent (NFR-R2) |
| Ordering | Per-project ordering (partition by project_id) | Events for the same project are processed in order |
| Dead-letter | Configured on all queues | Failed messages routed to DLQ for debugging (F-14.1) |
| TTL | 24 hours | Events older than 24h are discarded (stale by definition) |
| Retry | 3 attempts with exponential backoff (1s, 2s, 4s) | Before routing to DLQ |
