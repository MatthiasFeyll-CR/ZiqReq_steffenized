# Data Model

## Schema Overview

| Table | Description | Primary Key | Key Relationships | Service Owner |
|-------|-------------|-------------|-------------------|---------------|
| users | Shadow table synced from Azure AD | uuid (AD object ID) | Owns projects, collaborates, reviews | gateway |
| projects | Core project workspace | uuid v4 | Owns chat, requirements documents, reviews | core |
| project_collaborators | Join table: users collaborating on projects | uuid v4 | FK → users, projects | core |
| chat_messages | Immutable chat messages (user + AI) | uuid v4 | FK → projects, users | core |
| ai_reactions | AI reactions on user messages | uuid v4 | FK → chat_messages | core |
| user_reactions | User reactions on other users' messages | uuid v4 | FK → chat_messages, users | core |
| requirements_document_drafts | Current working requirements document (one per project) | uuid v4 | FK → projects | core |
| requirements_document_versions | Immutable requirements snapshots (one per submit) | uuid v4 | FK → projects | core |
| review_assignments | Reviewer-to-project assignments | uuid v4 | FK → projects, users | core |
| review_timeline_entries | Timeline events: comments, state changes, resubmissions | uuid v4 | FK → projects, users, self-referential (replies) | core |
| collaboration_invitations | Invitations to collaborate | uuid v4 | FK → projects, users (inviter, invitee) | core |
| notifications | Persistent in-app notifications | uuid v4 | FK → users | gateway |
| chat_context_summaries | Compressed chat for AI context management | uuid v4 | FK → projects, chat_messages | ai |
| facilitator_context_bucket | Admin-managed AI context (table of contents) | uuid v4 | FK → users (updated_by) | ai |
| context_agent_bucket | Admin-managed detailed company information | uuid v4 | FK → users (updated_by) | ai |
| admin_parameters | Runtime-configurable system parameters | varchar (key) | FK → users (updated_by) | core |
| monitoring_alert_configs | Admin opt-in to monitoring alerts | uuid v4 | FK → users | gateway |
| context_chunks | Chunked + embedded company context for RAG | uuid v4 | FK → context_agent_bucket | ai |

> **Service ownership:** Each table is owned by one service. The owning service manages migrations and is the authority on schema. Cross-service data access happens via gRPC for business logic, but Gateway uses **mirror Django models** for REST API endpoints (see below). See `project-structure.md` for service decomposition.

> **Mirror model pattern (Gateway ↔ Core):** When Gateway exposes REST endpoints for Core-owned tables, Gateway creates a mirror Django model with an identical schema and a `db_table` attribute pointing to Core's table. Both services connect to the same PostgreSQL database. Core owns migration authority. Gateway uses its mirror for DRF serializers and ORM queries. This pattern maintains microservice code isolation while enabling efficient REST API implementation. Implemented in M2 for `projects`, `project_collaborators`, `chat_messages`, `collaboration_invitations`. See `project-structure.md` § Django Model Sharing for full details.

> **AI service tables:** The `ai` service owns 4 tables: `chat_context_summaries`, `facilitator_context_bucket`, `context_agent_bucket`, `context_chunks`. Schema is defined here for database-level completeness. The AI Engineer may refine column details or add columns for these tables in `docs/03-ai/`. If so, the Arch+AI Integrator will reconcile.

---

## Table Definitions

### users

Shadow table synced from Azure AD on each login. Application-specific data (notification preferences) stored locally.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | — | PK | Azure AD object ID (not auto-generated) |
| email | varchar(255) | NO | — | UNIQUE | From Azure AD |
| first_name | varchar(150) | NO | — | | From Azure AD |
| last_name | varchar(150) | NO | — | | From Azure AD |
| display_name | varchar(300) | NO | — | | From Azure AD |
| roles | varchar[] | NO | `{}` | | Array of role strings: `user`, `reviewer`, `admin`. Derived from AD group membership, synced on login. |
| email_notification_preferences | jsonb | NO | `{}` | | Per-notification-type toggles. Empty = all enabled (default). Structure: `{"collaboration_invitation": false, ...}` |
| last_login_at | timestamptz | YES | NULL | | Updated on each login |
| created_at | timestamptz | NO | now() | | First sync timestamp |
| updated_at | timestamptz | NO | now() | | Auto-update on sync |

**Notes:**
- PK is the Azure AD object ID — not auto-generated. Set on first login sync.
- Roles are synced from AD group membership on each login, not managed in-app.
- Language preference persisted in frontend `localStorage`, not in the database (see tech-stack.md User Preference Persistence Strategy).
- Theme preference persisted in frontend `localStorage` (same rationale).
- Email notification preferences default to all enabled. Only disabled preferences are stored (absence = enabled).

---

### projects

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| title | varchar(500) | NO | `''` | | AI-generated initially, user can override |
| title_manually_edited | boolean | NO | false | | When true, AI title generation permanently disabled |
| project_type | varchar(20) | NO | — | CHECK (project_type IN ('software', 'non_software')) | Determines requirements structure: Software (Epics/User Stories) vs Non-Software (Milestones/Work Packages) |
| state | varchar(20) | NO | `'open'` | CHECK (state IN ('open', 'in_review', 'accepted', 'dropped', 'rejected')) | Project lifecycle state. State transitions: open→in_review (submit), in_review→accepted/dropped/rejected (review), accepted→open (reopen) |
| visibility | varchar(20) | NO | `'private'` | CHECK (visibility IN ('private', 'collaborating')) | F-8.1 |
| agent_mode | varchar(20) | NO | `'interactive'` | CHECK (agent_mode IN ('interactive', 'silent')) | F-2.1 |
| owner_id | uuid | NO | — | FK → users(id) | Primary owner (creator) |
| share_link_token | varchar(64) | YES | NULL | UNIQUE | Token for read-only sharing (F-8.3). NULL if not generated. |
| deleted_at | timestamptz | YES | NULL | | Soft delete timestamp. Permanent deletion when `deleted_at + countdown` exceeded (F-9.3). |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

**Notes:**
- `project_type` set at creation and immutable. Determines whether structured requirements follow Software or Non-Software model.
- Soft delete: `deleted_at IS NOT NULL` means project is in trash. Celery cleanup job checks `deleted_at + admin_parameter('soft_delete_countdown')`.

---

### project_collaborators

Join table for users collaborating on a project (accepted collaborators only).

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| user_id | uuid | NO | — | FK → users(id) | |
| joined_at | timestamptz | NO | now() | | When collaboration was accepted |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_project_collaborator | UNIQUE | (project_id, user_id) |

---

### chat_messages

Immutable. Never edited or deleted.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| sender_type | varchar(10) | NO | — | CHECK (sender_type IN ('user', 'ai')) | |
| sender_id | uuid | YES | — | FK → users(id) | NULL for AI messages |
| ai_agent | varchar(30) | YES | NULL | | Identifier for which AI agent sent this (e.g., 'facilitator', 'context_agent'). NULL for user messages. Agent identifiers defined by AI Engineer. |
| content | text | NO | — | | Message text. Supports @mentions. |
| message_type | varchar(20) | NO | `'regular'` | CHECK (message_type IN ('regular', 'delegation')) | Delegation messages are visually de-emphasized (F-2.15) |
| created_at | timestamptz | NO | now() | | |

**Notes:**
- Chat messages are append-only. No UPDATE or DELETE operations.
- `sender_id` is NULL for AI messages; `ai_agent` is NULL for user messages.
- Ordering is always by `created_at` ASC.

---

### ai_reactions

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| message_id | uuid | NO | — | FK → chat_messages(id) ON DELETE CASCADE | |
| reaction_type | varchar(15) | NO | — | CHECK (reaction_type IN ('thumbs_up', 'thumbs_down', 'heart')) | F-2.7 |
| created_at | timestamptz | NO | now() | | |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_ai_reaction_per_message | UNIQUE | (message_id) | One AI reaction per message max |

---

### user_reactions

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| message_id | uuid | NO | — | FK → chat_messages(id) ON DELETE CASCADE | |
| user_id | uuid | NO | — | FK → users(id) | |
| reaction_type | varchar(15) | NO | — | CHECK (reaction_type IN ('thumbs_up', 'thumbs_down', 'heart')) | F-2.8 |
| created_at | timestamptz | NO | now() | | |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_user_reaction | UNIQUE | (message_id, user_id) | One reaction per user per message |

**Notes:**
- Users can only react to OTHER users' messages, not AI messages. Enforced at application level (requires checking `chat_messages.sender_type = 'user'` and `chat_messages.sender_id != user_reactions.user_id`).
- Users can remove their reaction (DELETE).

---

### requirements_document_drafts

One per project. Current working state of the requirements document.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE, UNIQUE | One draft per project |
| title | text | YES | NULL | | Document title |
| short_description | text | YES | NULL | | Document short description |
| structure | jsonb | NO | `[]` | | Hierarchical requirements structure. Array of requirement items. For Software projects: Epics → User Stories. For Non-Software: Milestones → Work Packages. Each item has: id, type, title, description, children (nested array), metadata. |
| item_locks | jsonb | NO | `{}` | | Per-item lock flags keyed by item ID. `{"epic_123": true, "story_456": true}`. Locked items excluded from AI regeneration. |
| allow_information_gaps | boolean | NO | false | | Toggle: skip readiness evaluation, AI leaves /TODO markers (F-4.9) |
| readiness_evaluation | jsonb | NO | `{}` | | Readiness status keyed by item ID or section. Structure depends on project_type. |
| last_evaluated_at | timestamptz | YES | NULL | | Last readiness evaluation timestamp |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

**Notes:**
- **Software projects:** `structure` is an array of Epic objects, each containing nested User Story objects.
  - Epic: `{id: "epic_uuid", type: "epic", title: "...", description: "...", children: [UserStory, ...], metadata: {...}}`
  - User Story: `{id: "story_uuid", type: "user_story", title: "As a ... I want ... so that ...", description: "...", acceptance_criteria: [...], metadata: {...}}`
- **Non-Software projects:** `structure` is an array of Milestone objects, each containing nested Work Package objects.
  - Milestone: `{id: "milestone_uuid", type: "milestone", title: "...", description: "...", children: [WorkPackage, ...], metadata: {...}}`
  - Work Package: `{id: "wp_uuid", type: "work_package", title: "...", description: "...", deliverables: [...], metadata: {...}}`
- `item_locks` uses UUIDs from the structure to flag locked items. Locked items are preserved during AI regeneration.

---

### requirements_document_versions

Immutable snapshots created on each submit/resubmit.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| version_number | integer | NO | — | | Sequential per project |
| title | text | YES | NULL | | Frozen |
| short_description | text | YES | NULL | | Frozen |
| structure | jsonb | NO | `[]` | | Frozen hierarchical requirements structure (same format as draft) |
| pdf_file_path | varchar(500) | YES | NULL | | Path/reference to generated PDF file (see tech-stack.md PDF Generation Service Design) |
| created_at | timestamptz | NO | now() | | Submission timestamp |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_req_version | UNIQUE | (project_id, version_number) | Sequential versions per project |

**Notes:**
- Immutable. No UPDATE operations.
- PDF named with date for download (F-4.7).

---

### review_assignments

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| reviewer_id | uuid | NO | — | FK → users(id) | |
| assigned_by | varchar(10) | NO | — | CHECK (assigned_by IN ('submitter', 'self')) | Who assigned: submitter on submit, or self-assignment |
| assigned_at | timestamptz | NO | now() | | |
| unassigned_at | timestamptz | YES | NULL | | NULL if still assigned |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_active_review_assignment | UNIQUE | (project_id, reviewer_id) WHERE unassigned_at IS NULL | One active assignment per reviewer per project |

**Notes:**
- Conflict of interest: `reviewer_id != projects.owner_id`. Enforced at application level (F-10.4).

---

### review_timeline_entries

Immutable audit trail. Never edited or deleted.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| entry_type | varchar(20) | NO | — | CHECK (entry_type IN ('comment', 'state_change', 'resubmission')) | |
| author_id | uuid | YES | — | FK → users(id) | NULL for system-generated entries |
| content | text | YES | NULL | | Comment body, state change description, or resubmission note |
| parent_entry_id | uuid | YES | NULL | FK → review_timeline_entries(id) | For nested replies. NULL if top-level. |
| old_state | varchar(20) | YES | NULL | | Previous project state (state_change entries only) |
| new_state | varchar(20) | YES | NULL | | New project state (state_change entries only) |
| old_version_id | uuid | YES | NULL | FK → requirements_document_versions(id) | Previous version (resubmission entries only) |
| new_version_id | uuid | YES | NULL | FK → requirements_document_versions(id) | New version (resubmission entries only) |
| created_at | timestamptz | NO | now() | | |

**Notes:**
- Append-only. No UPDATE or DELETE. This is the audit trail for all review actions.

---

### collaboration_invitations

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| inviter_id | uuid | NO | — | FK → users(id) | Owner who sent the invitation |
| invitee_id | uuid | NO | — | FK → users(id) | User being invited |
| status | varchar(15) | NO | `'pending'` | CHECK (status IN ('pending', 'accepted', 'declined', 'revoked')) | F-8.2 |
| created_at | timestamptz | NO | now() | | |
| responded_at | timestamptz | YES | NULL | | When invitee accepted/declined or inviter revoked |

---

### notifications

Persistent in-app notifications (notification bell).

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| user_id | uuid | NO | — | FK → users(id) ON DELETE CASCADE | Recipient |
| event_type | varchar(50) | NO | — | | Notification event type (see FA-12 notification events) |
| title | varchar(300) | NO | — | | Display title |
| body | text | NO | — | | Display text |
| reference_id | uuid | YES | NULL | | ID of related entity (project, invitation, etc.) |
| reference_type | varchar(30) | YES | NULL | | Type of referenced entity: 'project', 'invitation' |
| is_read | boolean | NO | false | | |
| action_taken | boolean | NO | false | | Dismissed after user acts on it |
| created_at | timestamptz | NO | now() | | |

---

### chat_context_summaries

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Compressed chat for AI context window management.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| project_id | uuid | NO | — | FK → projects(id) ON DELETE CASCADE | |
| summary_text | text | NO | — | | Compressed/summarized content |
| messages_covered_up_to_id | uuid | NO | — | FK → chat_messages(id) | Last message included in this summary |
| compression_iteration | integer | NO | 1 | | Sequential count of compression cycles |
| context_window_usage_at_compression | float | NO | — | | Context window usage % when compression was triggered |
| created_at | timestamptz | NO | now() | | |

**Notes:**
- Replaced (not appended) on each compression cycle. Incremental: new summary = previous summary + messages since then, re-summarized (F-2.14).
- Original uncompressed messages always preserved in `chat_messages`.

---

### facilitator_context_bucket

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Admin-managed table of contents for the facilitator AI. Three rows: one global, one for software projects, one for non-software projects.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| context_type | varchar(20) | NO | — | CHECK (context_type IN ('global', 'software', 'non_software')), UNIQUE | Context bucket type |
| content | text | NO | `''` | | Free text: table of contents describing available company context (F-2.16) |
| updated_by | uuid | YES | NULL | FK → users(id) | Last admin to edit |
| updated_at | timestamptz | NO | now() | | |

**Notes:**
- Three rows: `global` (applies to all projects), `software` (Software projects only), `non_software` (Non-Software projects only).
- Application ensures exactly three records exist (one per context_type).

---

### context_agent_bucket

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Admin-managed detailed company information. Three rows: one global, one for software projects, one for non-software projects.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| context_type | varchar(20) | NO | — | CHECK (context_type IN ('global', 'software', 'non_software')), UNIQUE | Context bucket type |
| sections | jsonb | NO | `{}` | | Structured sections: existing applications, domain terminology, company structure (F-2.16) |
| free_text | text | NO | `''` | | Additional unstructured content |
| updated_by | uuid | YES | NULL | FK → users(id) | Last admin to edit |
| updated_at | timestamptz | NO | now() | | |

**Notes:**
- Three rows: `global` (applies to all projects), `software` (Software projects only), `non_software` (Non-Software projects only).
- Application ensures exactly three records exist (one per context_type).

---

### admin_parameters

Runtime-configurable system parameters.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| key | varchar(100) | NO | — | PK | Parameter identifier |
| value | varchar(500) | NO | — | | Current value (stored as string, parsed by application) |
| default_value | varchar(500) | NO | — | | Factory default |
| description | text | NO | — | | Human-readable parameter description |
| data_type | varchar(20) | NO | `'string'` | CHECK (data_type IN ('string', 'integer', 'float', 'boolean')) | Value type for frontend validation |
| category | varchar(50) | NO | `'Application'` | | Grouping category for admin UI (Application, Infrastructure, AI) |
| updated_by | uuid | YES | NULL | FK → users(id) | Last admin to edit |
| updated_at | timestamptz | NO | now() | | |

**Seed data — application parameters (F-11.3):**

| Key | Default Value | Description |
|-----|--------------|-------------|
| chat_message_cap | 5 | Chat messages before AI processing lockout per project (F-2.11) |
| idle_timeout | 300 | Seconds before user is marked idle |
| idle_disconnect | 120 | Seconds in idle before connection disconnects |
| max_reconnection_backoff | 30 | Maximum reconnection retry interval (seconds) |
| soft_delete_countdown | 30 | Days before permanent deletion from trash |
| debounce_timer | 3 | Seconds after last chat message before AI processes |
| default_app_language | de | Default language for new users |

**Seed data — infrastructure parameters (from tech-stack.md):**

| Key | Default Value | Description |
|-----|--------------|-------------|
| max_retry_attempts | 3 | Max retry attempts for failed operations |
| dlq_alert_threshold | 10 | DLQ message count triggering alert |
| health_check_interval | 60 | Seconds between health checks |

**Seed data — AI-specific parameters (from `docs/03-ai/agent-architecture.md`):**

| Key | Default Value | Description |
|-----|--------------|-------------|
| default_ai_model | (deployment-specific) | Azure OpenAI deployment name for default tier agents |
| escalated_ai_model | (deployment-specific) | Azure OpenAI deployment name for escalated tier (Context Extension) |
| ai_processing_timeout | 60 | Seconds timeout for user-facing agent invocations (Facilitator, Summarizing AI) |
| recent_message_count | 20 | Number of recent chat messages included in Facilitator context |
| context_compression_threshold | 60 | Context utilization percentage that triggers compression |
| context_rag_top_k | 5 | Number of chunks retrieved per RAG query |
| context_rag_min_similarity | 0.7 | Minimum cosine similarity for RAG chunk retrieval |

---

### monitoring_alert_configs

Admin opt-in to receive monitoring alerts.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| user_id | uuid | NO | — | FK → users(id) ON DELETE CASCADE, UNIQUE | One config per admin |
| is_active | boolean | NO | false | | Opted in to receive alerts |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

---

### context_chunks

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Chunked and embedded company context for RAG retrieval. Populated by the AI service when admin updates the context agent bucket.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| bucket_id | uuid | NO | — | FK → context_agent_bucket(id) ON DELETE CASCADE | Source bucket |
| chunk_index | integer | NO | — | | Sequential chunk number within the bucket |
| chunk_text | text | NO | — | | The text content of this chunk |
| token_count | integer | NO | — | | Token count of the chunk (for budget tracking) |
| embedding | vector(1536) | NO | — | | Embedding vector (dimension determined by AI Engineer's model choice — 1536 is text-embedding-3-small default) |
| source_section | varchar(100) | YES | NULL | | Which bucket section this chunk came from (NULL for free_text) |
| created_at | timestamptz | NO | now() | | |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_chunk_index | UNIQUE | (bucket_id, chunk_index) |

**Notes:**
- Entire table is rebuilt (DELETE + INSERT) when admin updates the context agent bucket. No incremental updates.
- Chunking strategy details (chunk size, overlap) defined by AI Engineer.
- The `embedding` column uses pgvector's `vector()` type. Dimension depends on embedding model chosen by AI Engineer.
- An HNSW index on the `embedding` column enables fast cosine similarity search. See Indexes section.

---

## Relationships

```
users 1──N projects (owner_id FK)
users N──M projects (via project_collaborators)
users 1──N review_assignments (reviewer_id FK)
users 1──N notifications (user_id FK)
users 1──N collaboration_invitations (as inviter)
users 1──N collaboration_invitations (as invitee)

projects 1──N chat_messages
projects 1──1 requirements_document_drafts
projects 1──N requirements_document_versions
projects 1──N review_assignments
projects 1──N review_timeline_entries
projects 1──N collaboration_invitations

chat_messages 0──1 ai_reactions
chat_messages 0──N user_reactions

review_timeline_entries 0──1 review_timeline_entries (parent_entry_id → nested replies)
review_timeline_entries 0──1 requirements_document_versions (old_version_id)
review_timeline_entries 0──1 requirements_document_versions (new_version_id)

context_agent_bucket 1──N context_chunks
```

---

## Indexes

| Table | Index Name | Columns | Type | Rationale |
|-------|-----------|---------|------|-----------|
| projects | idx_projects_owner | owner_id | btree | Landing page: "My Projects" list |
| projects | idx_projects_state | state | btree | Filter by state on landing page, review page |
| projects | idx_projects_deleted_at | deleted_at | btree | Trash list, soft delete cleanup job |
| projects | idx_projects_state_deleted | state, deleted_at | btree | Combined filter: active projects by state |
| projects | idx_projects_type | project_type | btree | Filter projects by type |
| project_collaborators | idx_collab_user | user_id | btree | Landing page: "Collaborating" list |
| project_collaborators | idx_collab_project | project_id | btree | Project workspace: collaborator list |
| chat_messages | idx_chat_project_created | project_id, created_at | btree | Chat history loading, ordered by time |
| chat_messages | idx_chat_sender | sender_id | btree | User stats: message count |
| requirements_document_versions | idx_req_ver_project | project_id, version_number | btree | Version history per project |
| review_assignments | idx_review_reviewer | reviewer_id, unassigned_at | btree | Review page: "Assigned to me" |
| review_assignments | idx_review_project | project_id | btree | Project review lookup |
| review_timeline_entries | idx_timeline_project | project_id, created_at | btree | Timeline loading, ordered by time |
| review_timeline_entries | idx_timeline_parent | parent_entry_id | btree | Nested reply loading |
| collaboration_invitations | idx_invite_invitee | invitee_id, status | btree | Landing page: pending invitations |
| collaboration_invitations | idx_invite_project | project_id | btree | Project invitation list |
| notifications | idx_notif_user_unread | user_id, is_read, action_taken | btree | Notification bell: unread count + list |
| notifications | idx_notif_created | user_id, created_at DESC | btree | Notification list ordering |
| chat_context_summaries | idx_ctx_summary_project | project_id | btree | AI context assembly per project |
| users | idx_users_email | email | btree (UNIQUE via column constraint) | User lookup by email, search |
| users | idx_users_display_name | display_name | btree | User search by name (F-8.2, F-11.6) |
| context_chunks | idx_chunks_embedding | embedding | hnsw (vector_cosine_ops) | Fast cosine similarity search for RAG retrieval |
| context_chunks | idx_chunks_bucket | bucket_id | btree | Bulk delete + re-insert on bucket update |

---

## Enums / Constants

Enums are implemented as CHECK constraints on varchar columns (not PostgreSQL native enums) for easier migration and Django ORM compatibility.

| Name | Values | Used In |
|------|--------|---------|
| project_type | software, non_software | projects.project_type. Determines requirements structure (Epics/Stories vs Milestones/Work Packages) |
| project_state | open, in_review, accepted, dropped, rejected | projects.state. Transitions: open→in_review, in_review→accepted/dropped/rejected, accepted→open (reopen) |
| project_visibility | private, collaborating | projects.visibility |
| agent_mode | interactive, silent | projects.agent_mode |
| sender_type | user, ai | chat_messages.sender_type |
| message_type | regular, delegation | chat_messages.message_type |
| reaction_type | thumbs_up, thumbs_down, heart | ai_reactions, user_reactions |
| invitation_status | pending, accepted, declined, revoked | collaboration_invitations.status |
| entry_type | comment, state_change, resubmission | review_timeline_entries.entry_type |
| assignment_source | submitter, self | review_assignments.assigned_by |
| context_type | global, software, non_software | facilitator_context_bucket.context_type, context_agent_bucket.context_type |

---

## Migration Strategy

- **Tool:** Django ORM migrations (`python manage.py makemigrations` / `migrate`)
- **Naming:** Auto-generated by Django (sequential numbered files per app)
- **Seed data:** Admin parameters table seeded with default values via a data migration
- **Context bucket initialization:** Facilitator context bucket and context agent bucket created via data migration (three empty rows each: global, software, non_software)
- **Schema changes:** All schema changes through Django migrations — no raw SQL unless necessary for PostgreSQL-specific features (partial unique indexes)
- **pgvector setup:** The `context_chunks` table requires the pgvector extension (`CREATE EXTENSION vector`). Docker PostgreSQL image should use `pgvector/pgvector:pg16` or install the extension manually. Extension creation handled in an initial migration.

## Seed Data

Data that must exist for the application to boot and function.

| Table | Data | Purpose | When Created |
|-------|------|---------|-------------|
| admin_parameters | All parameters from seed data tables above (application + infrastructure + AI) | Runtime-configurable system parameters with defaults | Data migration |
| facilitator_context_bucket | Three empty rows (global, software, non_software; each with content = '') | Admin AI context management per project type | Data migration |
| context_agent_bucket | Three empty rows (global, software, non_software; each with sections = {}, free_text = '') | Admin detailed context management per project type | Data migration |
| users (dev only) | 4 preconfigured dev users (F-7.1) | Auth bypass mode: Dev User 1 (User), Dev User 2 (User), Dev User 3 (User+Reviewer), Dev User 4 (User+Admin) | Conditional data migration (only when DEBUG=True) |

---

## Notes

- **Immutable tables:** `chat_messages`, `requirements_document_versions`, `review_timeline_entries` are append-only. No UPDATE or DELETE. Application layer enforces this.
- **Soft delete:** Only `projects` uses soft delete (`deleted_at` timestamp). All other deletions are hard deletes (via CASCADE from project deletion, or explicit removal).
- **JSONB usage:** Used for flexible/hierarchical schemas: `email_notification_preferences` (user), `structure` (requirements_document_drafts, requirements_document_versions), `item_locks` (requirements_document_drafts), `readiness_evaluation` (requirements_document_drafts), `sections` (context_agent_bucket). All other data uses typed columns.
- **Timezone-aware timestamps:** All `timestamptz` columns. Django `USE_TZ=True`.
- **Array fields:** `users.roles` (varchar[]) uses PostgreSQL native array type, supported by Django's `ArrayField`.
- **Cross-service data access:** In the microservices architecture, tables are grouped by service domain (see Schema Overview "Service Owner" column). Foreign keys that cross service boundaries become application-level references (UUID stored but no DB-level FK constraint). Service boundaries defined in `project-structure.md`.
- **Cross-service raw SQL exception:** Since all tables share the same PostgreSQL instance, limited cross-service direct DB access is permitted in these cases: (1) Core gRPC servicers may read Gateway-owned tables (e.g., `users`) via raw SQL for display name resolution, avoiding circular gRPC dependencies. (2) Gateway may use unmanaged Django models (`managed = False`) to read/write Core-owned tables (e.g., `admin_parameters`) when both services share the same DB instance and gRPC RPCs are not defined. All cross-service access should be documented and kept minimal.
- **pgvector dependency:** The `context_chunks` table requires the pgvector PostgreSQL extension. Docker PostgreSQL image should use `pgvector/pgvector:pg16`.
