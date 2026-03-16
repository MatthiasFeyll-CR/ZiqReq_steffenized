# Data Entities & Relationships

## Entity Overview

| Entity | Description | Owner/Creator | Lifecycle |
|--------|-------------|---------------|-----------|
| User | A Commerz Real employee authenticated via Azure AD | System (from Azure AD) | Exists as long as in Azure AD |
| Project | A requirements assembly workspace containing chat and requirements document | User (creator) | Open → In Review → Accepted / Dropped / Rejected → (Rejected can resubmit) |
| Chat Message | A single message in a project's chat conversation | User or AI | Created → persists (never deleted) |
| AI Reaction | A reaction placed by the AI on a user's chat message | AI | Created → persists |
| User Reaction | A reaction placed by a user on another user's chat message | User | Created → can be removed |
| Requirements Document Draft | The current working state of the hierarchical requirements structure | AI + User edits | Generated → edited → snapshotted on submit |
| Requirements Document Version | An immutable snapshot of the Requirements Document | System (on submit) | Created on submit → immutable |
| Review Assignment | The relationship between a reviewer and a project under review | User (on submit) or Reviewer (self-assign) | Assigned → active → completed (on final action) |
| Review Timeline Entry | An event in the review timeline (comment, state change, resubmission) | User, Reviewer, or System | Created → persists (never deleted) |
| Collaboration Invitation | A pending invitation to collaborate on a project | Owner | Pending → Accepted / Declined / Revoked |
| Notification | A persistent in-app notification for a user | System | Created (unread) → acted on (dismissed) |
| Chat Context Summary | Summarized version of older chat messages for AI context management | System | Created when needed → updated incrementally |
| Facilitator Context | Admin-managed table of contents for AI context (3 types: global, software, non_software) | Admin | Created → updated manually |
| Detailed Company Context | Admin-managed detailed company information (3 types: global, software, non_software) | Admin | Created → updated manually |
| Admin Parameter | A runtime-configurable system parameter | Admin | Set → updated at runtime |
| Monitoring Alert Config | An admin's opt-in to receive monitoring alerts | Admin | Opted in → opted out |

## Entity Details

### User
- **Description:** A Commerz Real employee. Identity and basic info sourced from Azure AD. Application-specific preferences tracked internally.
- **Key attributes:**
  - id: unique identifier (from Azure AD)
  - email: Azure AD email address
  - first name, last name, display name: from Azure AD
  - roles: set of roles (User, Reviewer, Admin) — derived from Azure AD group membership
  - language preference: German or English
  - theme preference: Light or Dark (defaults to OS preference)
  - email notification preferences: per-notification-type toggles
- **Relationships:**
  - Owns many Projects (as owner)
  - Collaborates on many Projects
  - Has many Notifications
  - Has many Review Assignments (if Reviewer)
  - Has many Collaboration Invitations (sent and received)
- **Lifecycle:** User exists in the system as long as they are in the Azure AD tenant. No in-app registration or deletion.
- **Access rules:** Users can read their own profile. Admins can search and view any user's profile with stats (project count, review count, contribution count).

> ⚙️ DOWNSTREAM → **Software Architect**: Decide where user preferences (language, theme, email notification settings) are persisted — frontend storage, backend, or hybrid. The old spec suggested frontend persistence for language and theme. See `docs_old/01-requirements/data-entities.md` User entity.

### Project
- **Description:** A requirements assembly workspace representing a single project. Contains chat and hierarchical requirements document. Two types: Software (Epics/User Stories) or Non-Software (Milestones/Work Packages).
- **Key attributes:**
  - id: UUID
  - project_type: software / non_software (required at creation, immutable)
  - title: editable text (AI-generated initially, user can override)
  - title_manually_edited: flag indicating AI title generation is permanently disabled
  - state: open / in_review / accepted / dropped / rejected
  - visibility: private / collaborating
  - agent_mode: interactive / silent
  - owner: one User (single owner)
  - created_at, updated_at: timestamps
  - deleted_at: soft-delete timestamp (null if not deleted)
  - share_link: generated read-only link (null if not generated)
- **Relationships:**
  - Belongs to one User (owner)
  - Has many Collaborators (Users)
  - Has many Chat Messages
  - Has one Requirements Document Draft (working state)
  - Has many Requirements Document Versions (immutable snapshots)
  - Has many Review Assignments
  - Has many Review Timeline Entries
  - Has many Collaboration Invitations
- **Lifecycle:** Created (open) → submitted (in_review) → accepted / dropped / rejected. Rejected can be resubmitted. All actions reversible by reviewer (returns to in_review). Can be soft-deleted (moves to trash, permanent deletion after countdown).
- **Access rules:**
  - Owner: full control (edit, submit, delete, invite, manage collaborators)
  - Collaborator: edit chat, view requirements document
  - Read-only viewer (via shared link): view only
  - Reviewer: view full project context when assigned/self-assigned for review

### Chat Message
- **Description:** A single message in a project's chat conversation, sent by a user or generated by the AI.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - sender_type: user / ai
  - sender_id: reference to User (if user) or AI agent identifier (if ai)
  - content: message text (supports @mentions)
  - message_type: regular / delegation (for AI placeholder messages that get de-emphasized)
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Project
  - Belongs to one User (if user-sent) or one AI agent
  - Has many AI Reactions
  - Has many User Reactions
- **Lifecycle:** Created → persists permanently. Never edited or deleted.
- **Access rules:** Visible to all users with access to the project.

### AI Reaction
- **Description:** A reaction placed by the AI on a user's chat message.
- **Key attributes:**
  - id: unique identifier
  - message_id: reference to Chat Message
  - reaction_type: thumbs_up / thumbs_down / heart
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Chat Message
- **Lifecycle:** Created → persists.
- **Access rules:** Visible to all users with access to the project.

### User Reaction
- **Description:** A reaction placed by a user on another user's chat message. Cannot be placed on AI messages.
- **Key attributes:**
  - id: unique identifier
  - message_id: reference to Chat Message
  - user_id: reference to User who reacted
  - reaction_type: thumbs_up / thumbs_down / heart
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Chat Message
  - Belongs to one User
- **Lifecycle:** Created → can be removed by the user who placed it.
- **Access rules:** Any user with access to the project can react to other users' messages. Cannot react to AI messages.

### Requirements Document Draft
- **Description:** The current working state of the hierarchical requirements document for a project. Structure differs based on project type.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project (unique, one per project)
  - title: text
  - short_description: text
  - structure: JSON — hierarchical structure:
    - **Software:** `[{id, title, description, stories: [{id, title, description, acceptance_criteria: [str], priority: str}]}]`
    - **Non-Software:** `[{id, title, description, packages: [{id, title, description, deliverables: [str], dependencies: [str]}]}]`
  - item_locks: JSON dict of item_id → bool (locked items excluded from AI regeneration)
  - allow_information_gaps: boolean toggle flag
  - readiness_evaluation: JSON (per-item readiness status)
  - created_at, updated_at: timestamps
- **Relationships:**
  - Belongs to one Project
- **Lifecycle:** Generated by AI on first Review tab open → edited by user and/or AI → snapshotted into Requirements Document Version on submit.
- **Access rules:** Editable by owner and collaborators. Locked during review (immutable).

### Requirements Document Version
- **Description:** An immutable snapshot of the Requirements Document created on each submit/resubmit.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - version_number: sequential version number
  - title: text (frozen)
  - short_description: text (frozen)
  - structure: JSON (frozen hierarchical structure)
  - pdf_file_path: reference to generated PDF file
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Project
  - Referenced by Review Timeline Entries (resubmission entries link two versions)
- **Lifecycle:** Created on submit → immutable. Previous versions preserved as downloadable PDFs.
- **Access rules:** Readable by anyone with access to the project. Download available from review timeline.

### Review Assignment
- **Description:** The relationship between a reviewer and a project under review.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - reviewer_id: reference to User (with Reviewer role)
  - assigned_by: user (creator on submit) / self (reviewer self-assignment)
  - assigned_at: timestamp
  - unassigned_at: timestamp (null if still assigned)
- **Relationships:**
  - Belongs to one Project
  - Belongs to one User (Reviewer)
- **Lifecycle:** Assigned → active → unassigned (if reviewer unassigns self) or completed (on final project state).
- **Access rules:** Reviewers can self-assign/unassign. Users can assign specific reviewers on submit.

### Review Timeline Entry
- **Description:** An event in the review timeline — comment, state change, or resubmission record.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - entry_type: comment / state_change / resubmission
  - author_id: reference to User (or system for automated entries)
  - content: text (comment body, state change description, or resubmission note)
  - parent_entry_id: reference to parent entry (for nested replies; null if top-level)
  - old_state / new_state: previous and new project state (for state changes)
  - old_version_id / new_version_id: references to Requirements Document Versions (for resubmissions)
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Project
  - Belongs to one User (author)
  - May reference Requirements Document Versions (resubmission entries)
  - May have child entries (nested replies)
- **Lifecycle:** Created → persists permanently. Never edited or deleted (audit trail).
- **Access rules:** Visible to all users with access to the project's review section.

### Collaboration Invitation
- **Description:** An invitation from a project owner to another user to collaborate.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - inviter_id: reference to User (owner)
  - invitee_id: reference to User (invited)
  - status: pending / accepted / declined / revoked
  - created_at: timestamp
  - responded_at: timestamp (null while pending)
- **Relationships:**
  - Belongs to one Project
  - Belongs to one User (inviter) and one User (invitee)
- **Lifecycle:** Created (pending) → accepted / declined / revoked. Owner can re-invite after decline.
- **Access rules:** Inviter can revoke. Invitee can accept or decline.

### Notification
- **Description:** A persistent in-app notification delivered to a user's notification bell.
- **Key attributes:**
  - id: unique identifier
  - user_id: reference to recipient User
  - event_type: the notification event type (see FA-12 notification events)
  - title: notification display title
  - body: notification display text
  - reference_id: reference to relevant entity (project, invitation, etc.)
  - reference_type: type of referenced entity
  - is_read: flag (unread by default)
  - action_taken: flag (notification dismissed after user acts on it)
  - created_at: timestamp
- **Relationships:**
  - Belongs to one User (recipient)
  - References one entity (Project, Invitation, etc.)
- **Lifecycle:** Created (unread) → read → acted on (dismissed from list).
- **Access rules:** Only visible to the recipient user.

### Chat Context Summary
- **Description:** A summarized version of older chat messages, used to manage AI context window size. Original uncompressed messages are always preserved in the Chat Message entity.
- **Key attributes:**
  - id: unique identifier
  - project_id: reference to the Project
  - summary_text: the summarized content
  - messages_covered_up_to: reference to the last Chat Message included in this summary
  - created_at: timestamp
- **Relationships:**
  - Belongs to one Project
  - References Chat Messages (up to a certain point)
- **Lifecycle:** Created when the AI's working memory needs relief → replaced incrementally as more summarization occurs.
- **Access rules:** Read by the AI processing pipeline. Not directly visible to users (context utilization indicator shows derived stats).

> ⚙️ DOWNSTREAM → **AI Engineer**: The old spec included additional attributes (compression_iteration, context_window_usage_at_compression) and detailed mechanics for incremental compression. Design the summarization strategy, what metadata to track, and trigger conditions. See `docs_old/01-requirements/data-entities.md` Chat Context Summary entity.

### Facilitator Context
- **Description:** Admin-managed content describing what company context information exists. Provided to the AI during requirements assembly. Three context types: global (common to all projects), software (for software projects), and non_software (for non-software projects).
- **Key attributes:**
  - id: unique identifier
  - context_type: global / software / non_software
  - content: free text (table of contents)
  - updated_by: reference to Admin User
  - updated_at: timestamp
- **Relationships:**
  - Managed by Admin users
- **Lifecycle:** Created → updated manually by Admins as needed.
- **Access rules:** Editable by Admins only (AI Context tab). Read by the AI based on project type.

### Detailed Company Context
- **Description:** Admin-managed detailed company information used by the AI for company-specific answers. Three context types: global (common to all projects), software (for software projects), and non_software (for non-software projects).
- **Key attributes:**
  - id: unique identifier
  - context_type: global / software / non_software
  - sections: structured sections (existing applications, domain terminology, company structure)
  - free_text: additional unstructured content
  - updated_by: reference to Admin User
  - updated_at: timestamp
- **Relationships:**
  - Managed by Admin users
- **Lifecycle:** Created → updated manually by Admins as needed.
- **Access rules:** Editable by Admins only (AI Context tab). Read by the AI based on project type.

> ⚙️ DOWNSTREAM → **AI Engineer**: Design how these two context entities are consumed by the AI agents — which agent reads what, retrieval strategy, how context_type filtering works, and how context freshness is handled. The old spec used a "Facilitator Bucket" (table of contents for the main AI) and "Context Agent Bucket" (detailed info for a specialized retrieval agent). See `docs_old/01-requirements/data-entities.md` Facilitator Context Bucket and Context Agent Bucket entities.

### Admin Parameter
- **Description:** A runtime-configurable system parameter managed by Admins.
- **Key attributes:**
  - key: parameter identifier
  - value: parameter value
  - default_value: factory default
  - updated_by: reference to Admin User
  - updated_at: timestamp
- **Relationships:**
  - Managed by Admin users
- **Lifecycle:** Initialized with defaults → updated at runtime by Admins. Changes apply immediately.
- **Access rules:** Readable and writable by Admins only (Parameters tab).

### Monitoring Alert Config
- **Description:** An admin's opt-in to receive monitoring alerts via email.
- **Key attributes:**
  - admin_id: reference to Admin User
  - opted_in: flag
  - updated_at: timestamp
- **Relationships:**
  - Belongs to one User (Admin)
- **Lifecycle:** Admin opts in → receives alerts → opts out.
- **Access rules:** Each Admin manages their own alert preference.

## Relationship Diagram (Text)

```
User 1──N Project (as owner)
User N──M Project (as collaborator, via Collaboration Invitation)
User 1──N Review Assignment (as reviewer)
User 1──N Notification

Project 1──N Chat Message
Project 1──1 Requirements Document Draft
Project 1──N Requirements Document Version
Project 1──N Review Assignment
Project 1──N Review Timeline Entry
Project 1──N Collaboration Invitation
Project 1──0..N Chat Context Summary

Chat Message 1──N AI Reaction
Chat Message 1──N User Reaction

Review Timeline Entry 0──1 Review Timeline Entry (parent, for nested replies)
Review Timeline Entry 0──N Requirements Document Version (resubmission links)
```

## Notes

- **Chat messages are immutable.** Once created, messages are never edited or deleted. This ensures the AI always processes a consistent, complete history.
- **Requirements Document Versions are immutable.** Each submit creates a frozen snapshot. No edits during review cycles.
- **Review Timeline Entries are immutable.** Audit trail for all review actions, state changes, comments, and undos.
- **User data is sourced from Azure AD.** The application does not manage user creation/deletion. Notification preferences are the only user-specific settings managed within the app.
- **Soft delete uses a timestamp.** `deleted_at` is set on soft delete, permanent deletion occurs when the countdown expires.
- **Project type is immutable.** Once a project is created as "software" or "non_software", the type cannot be changed.
- **AI context buckets are type-aware.** Three rows exist for each context type (Facilitator Context and Detailed Company Context): global (used by all projects), software (used only by software projects), and non_software (used only by non-software projects).
