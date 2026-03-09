# Data Model

## Schema Overview

| Table | Description | Primary Key | Key Relationships | Service Owner |
|-------|-------------|-------------|-------------------|---------------|
| users | Shadow table synced from Azure AD | uuid (AD object ID) | Owns ideas, collaborates, reviews | gateway |
| ideas | Core brainstorming workspace | uuid v4 | Owns chat, board, BRD, reviews | core |
| idea_collaborators | Join table: users collaborating on ideas | uuid v4 | FK → users, ideas | core |
| chat_messages | Immutable chat messages (user + AI) | uuid v4 | FK → ideas, users | core |
| ai_reactions | AI reactions on user messages | uuid v4 | FK → chat_messages | core |
| user_reactions | User reactions on other users' messages | uuid v4 | FK → chat_messages, users | core |
| board_nodes | Board items: box, group, free_text | uuid v4 | FK → ideas, self-referential (parent group) | core |
| board_connections | Edges between board nodes | uuid v4 | FK → board_nodes (source, target) | core |
| brd_drafts | Current working BRD state (one per idea) | uuid v4 | FK → ideas | core |
| brd_versions | Immutable BRD snapshots (one per submit) | uuid v4 | FK → ideas | core |
| review_assignments | Reviewer-to-idea assignments | uuid v4 | FK → ideas, users | core |
| review_timeline_entries | Timeline events: comments, state changes, resubmissions | uuid v4 | FK → ideas, users, self-referential (replies) | core |
| collaboration_invitations | Invitations to collaborate | uuid v4 | FK → ideas, users (inviter, invitee) | core |
| notifications | Persistent in-app notifications | uuid v4 | FK → users | gateway |
| chat_context_summaries | Compressed chat for AI context management | uuid v4 | FK → ideas, chat_messages | ai |
| idea_keywords | AI-generated abstract keywords | uuid v4 | FK → ideas | core |
| merge_requests | Merge/append requests between similar ideas | uuid v4 | FK → ideas (requesting, target, resulting) | core |
| facilitator_context_bucket | Admin-managed AI context (table of contents) | uuid v4 | FK → users (updated_by) | ai |
| context_agent_bucket | Admin-managed detailed company information | uuid v4 | FK → users (updated_by) | ai |
| admin_parameters | Runtime-configurable system parameters | varchar (key) | FK → users (updated_by) | core |
| monitoring_alert_configs | Admin opt-in to monitoring alerts | uuid v4 | FK → users | gateway |
| context_chunks | Chunked + embedded company context for RAG | uuid v4 | FK → context_agent_bucket | ai |
| idea_embeddings | Semantic embeddings per idea for similarity detection | uuid v4 | FK → ideas | ai |

> **Service ownership:** Each table is owned by one service. The owning service manages migrations and is the authority on schema. Cross-service data access happens via gRPC for business logic, but Gateway uses **mirror Django models** for REST API endpoints (see below). See `project-structure.md` for service decomposition.

> **Mirror model pattern (Gateway ↔ Core):** When Gateway exposes REST endpoints for Core-owned tables, Gateway creates a mirror Django model with an identical schema and a `db_table` attribute pointing to Core's table. Both services connect to the same PostgreSQL database. Core owns migration authority. Gateway uses its mirror for DRF serializers and ORM queries. This pattern maintains microservice code isolation while enabling efficient REST API implementation. Implemented in M2 for `ideas`, `idea_collaborators`, `chat_messages`, `collaboration_invitations`. See `project-structure.md` § Django Model Sharing for full details.

> **AI service tables:** The `ai` service owns 5 tables: `chat_context_summaries`, `facilitator_context_bucket`, `context_agent_bucket`, `context_chunks`, `idea_embeddings`. Schema is defined here for database-level completeness. The AI Engineer may refine column details or add columns for these tables in `docs/03-ai/`. If so, the Arch+AI Integrator will reconcile.

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

### ideas

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| title | varchar(500) | NO | `''` | | AI-generated initially, user can override |
| title_manually_edited | boolean | NO | false | | When true, AI title generation permanently disabled (F-2.3) |
| state | varchar(20) | NO | `'open'` | CHECK (state IN ('open', 'in_review', 'accepted', 'dropped', 'rejected')) | Idea lifecycle state (F-1.5). State transitions: open→in_review (submit), in_review→accepted/dropped/rejected (review), accepted→open (reopen for brainstorming, F-5.6) |
| visibility | varchar(20) | NO | `'private'` | CHECK (visibility IN ('private', 'collaborating')) | F-8.1 |
| agent_mode | varchar(20) | NO | `'interactive'` | CHECK (agent_mode IN ('interactive', 'silent')) | F-2.1 |
| owner_id | uuid | NO | — | FK → users(id) | Primary owner (creator) |
| co_owner_id | uuid | YES | NULL | FK → users(id) | Second owner — only set for merged ideas (F-5.5) |
| share_link_token | varchar(64) | YES | NULL | UNIQUE | Token for read-only sharing (F-8.3). NULL if not generated. |
| merged_from_idea_1_id | uuid | YES | NULL | FK → ideas(id) | First original idea (if this is a merged idea) |
| merged_from_idea_2_id | uuid | YES | NULL | FK → ideas(id) | Second original idea (if this is a merged idea) |
| closed_by_merge_id | uuid | YES | NULL | FK → ideas(id) | New merged idea that replaced this one |
| closed_by_append_id | uuid | YES | NULL | FK → ideas(id) | In-review idea this was appended to |
| deleted_at | timestamptz | YES | NULL | | Soft delete timestamp. Permanent deletion when `deleted_at + countdown` exceeded (F-9.3). |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

**Notes:**
- Owner model: single `owner_id` (always set) + optional `co_owner_id` (only for merged ideas). Max 2 owners.
- Recursive merge handling: If a previously-merged idea (which already has 2 owners) merges with another idea, the two users who triggered the merge become the co-owners of the new idea. Previous co-owners who did not trigger the merge are demoted to collaborators (added to `idea_collaborators`). This ensures the 2-owner model is never violated.
- Soft delete: `deleted_at IS NOT NULL` means idea is in trash. Celery cleanup job checks `deleted_at + admin_parameter('soft_delete_countdown')`.

---

### idea_collaborators

Join table for users collaborating on an idea (accepted collaborators only).

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| user_id | uuid | NO | — | FK → users(id) | |
| joined_at | timestamptz | NO | now() | | When collaboration was accepted |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_idea_collaborator | UNIQUE | (idea_id, user_id) |

---

### chat_messages

Immutable. Never edited or deleted.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| sender_type | varchar(10) | NO | — | CHECK (sender_type IN ('user', 'ai')) | |
| sender_id | uuid | YES | — | FK → users(id) | NULL for AI messages |
| ai_agent | varchar(30) | YES | NULL | | Identifier for which AI agent sent this (e.g., 'facilitator', 'context_agent'). NULL for user messages. Agent identifiers defined by AI Engineer. |
| content | text | NO | — | | Message text. Supports @mentions and board item references (see API design for inline reference formats). |
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

### board_nodes

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| node_type | varchar(15) | NO | — | CHECK (node_type IN ('box', 'group', 'free_text')) | F-3.1 |
| title | varchar(500) | YES | NULL | | Boxes and Groups have titles. Free Text does not. |
| body | text | YES | NULL | | Bullet-point content for Boxes, plain text for Free Text, NULL for Groups. |
| position_x | float | NO | 0 | | Canvas X coordinate |
| position_y | float | NO | 0 | | Canvas Y coordinate |
| width | float | YES | NULL | | Relevant for Groups (resizable) |
| height | float | YES | NULL | | Relevant for Groups (resizable) |
| parent_id | uuid | YES | NULL | FK → board_nodes(id) ON DELETE SET NULL | Parent Group. NULL if top-level. Enables nesting (F-3.1). |
| is_locked | boolean | NO | false | | Lock toggle per node (F-3.2) |
| created_by | varchar(10) | NO | — | CHECK (created_by IN ('user', 'ai')) | |
| ai_modified_indicator | boolean | NO | false | | Shows AI modification indicator (F-3.4). Cleared on user selection. |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

**Notes:**
- Only current state persisted. No history in backend — undo/redo is frontend-only (F-3.7, see tech-stack.md Board Undo/Redo Strategy).
- `parent_id` self-referential FK enables Group nesting. `ON DELETE SET NULL` detaches children if parent deleted.

---

### board_connections

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| source_node_id | uuid | NO | — | FK → board_nodes(id) ON DELETE CASCADE | |
| target_node_id | uuid | NO | — | FK → board_nodes(id) ON DELETE CASCADE | |
| label | varchar(500) | YES | NULL | | Optional sticky text label (F-3.2) |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_board_connection | UNIQUE | (source_node_id, target_node_id) | No duplicate connections between same pair |

---

### brd_drafts

One per idea. Current working state of the BRD.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE, UNIQUE | One draft per idea |
| section_title | text | YES | NULL | | BRD section: Title |
| section_short_description | text | YES | NULL | | BRD section: Short Description |
| section_current_workflow | text | YES | NULL | | BRD section: Current Workflow & Pain Points |
| section_affected_department | text | YES | NULL | | BRD section: Affected Department / Business Area |
| section_core_capabilities | text | YES | NULL | | BRD section: Core User Capabilities |
| section_success_criteria | text | YES | NULL | | BRD section: Success Criteria |
| section_locks | jsonb | NO | `{}` | | Per-section lock flags. `{"short_description": true, "core_capabilities": true}`. Locked sections excluded from AI regeneration (F-4.4). |
| allow_information_gaps | boolean | NO | false | | Toggle: skip readiness evaluation, AI leaves /TODO markers (F-4.9) |
| readiness_evaluation | jsonb | NO | `{}` | | Per-section readiness status. `{"current_workflow": "ready", "success_criteria": "insufficient"}` (F-4.8) |
| last_evaluated_at | timestamptz | YES | NULL | | Last readiness evaluation timestamp |
| created_at | timestamptz | NO | now() | | |
| updated_at | timestamptz | NO | now() | | Auto-update |

---

### brd_versions

Immutable snapshots created on each submit/resubmit.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| version_number | integer | NO | — | | Sequential per idea |
| section_title | text | YES | NULL | | Frozen |
| section_short_description | text | YES | NULL | | Frozen |
| section_current_workflow | text | YES | NULL | | Frozen |
| section_affected_department | text | YES | NULL | | Frozen |
| section_core_capabilities | text | YES | NULL | | Frozen |
| section_success_criteria | text | YES | NULL | | Frozen |
| pdf_file_path | varchar(500) | YES | NULL | | Path/reference to generated PDF file (see tech-stack.md PDF Generation Service Design) |
| created_at | timestamptz | NO | now() | | Submission timestamp |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_brd_version | UNIQUE | (idea_id, version_number) | Sequential versions per idea |

**Notes:**
- Immutable. No UPDATE operations.
- PDF named with date for download (F-4.7).

---

### review_assignments

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| reviewer_id | uuid | NO | — | FK → users(id) | |
| assigned_by | varchar(10) | NO | — | CHECK (assigned_by IN ('submitter', 'self')) | Who assigned: submitter on submit, or self-assignment |
| assigned_at | timestamptz | NO | now() | | |
| unassigned_at | timestamptz | YES | NULL | | NULL if still assigned |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_active_review_assignment | UNIQUE | (idea_id, reviewer_id) WHERE unassigned_at IS NULL | One active assignment per reviewer per idea |

**Notes:**
- Conflict of interest: `reviewer_id != ideas.owner_id AND reviewer_id != ideas.co_owner_id`. Enforced at application level (F-10.4).

---

### review_timeline_entries

Immutable audit trail. Never edited or deleted.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| entry_type | varchar(20) | NO | — | CHECK (entry_type IN ('comment', 'state_change', 'resubmission')) | |
| author_id | uuid | YES | — | FK → users(id) | NULL for system-generated entries |
| content | text | YES | NULL | | Comment body, state change description, or resubmission note |
| parent_entry_id | uuid | YES | NULL | FK → review_timeline_entries(id) | For nested replies. NULL if top-level. |
| old_state | varchar(20) | YES | NULL | | Previous idea state (state_change entries only) |
| new_state | varchar(20) | YES | NULL | | New idea state (state_change entries only) |
| old_version_id | uuid | YES | NULL | FK → brd_versions(id) | Previous BRD version (resubmission entries only) |
| new_version_id | uuid | YES | NULL | FK → brd_versions(id) | New BRD version (resubmission entries only) |
| created_at | timestamptz | NO | now() | | |

**Notes:**
- Append-only. No UPDATE or DELETE. This is the audit trail for all review actions.

---

### collaboration_invitations

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
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
| reference_id | uuid | YES | NULL | | ID of related entity (idea, invitation, etc.) |
| reference_type | varchar(30) | YES | NULL | | Type of referenced entity: 'idea', 'invitation', 'merge_request' |
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
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE | |
| summary_text | text | NO | — | | Compressed/summarized content |
| messages_covered_up_to_id | uuid | NO | — | FK → chat_messages(id) | Last message included in this summary |
| compression_iteration | integer | NO | 1 | | Sequential count of compression cycles |
| context_window_usage_at_compression | float | NO | — | | Context window usage % when compression was triggered |
| created_at | timestamptz | NO | now() | | |

**Notes:**
- Replaced (not appended) on each compression cycle. Incremental: new summary = previous summary + messages since then, re-summarized (F-2.14).
- Original uncompressed messages always preserved in `chat_messages`.

---

### idea_keywords

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE, UNIQUE | One keyword set per idea |
| keywords | varchar[] | NO | `{}` | | Array of single-word abstract keywords. Max length admin-configurable (default: 20). (F-5.1) |
| last_updated_at | timestamptz | NO | now() | | |

---

### merge_requests

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| requesting_idea_id | uuid | NO | — | FK → ideas(id) | |
| target_idea_id | uuid | NO | — | FK → ideas(id) | |
| merge_type | varchar(10) | NO | — | CHECK (merge_type IN ('merge', 'append')) | merge = open+open, append = open+in_review (F-5.4) |
| requested_by | uuid | NO | — | FK → users(id) | User who initiated the request |
| status | varchar(15) | NO | `'pending'` | CHECK (status IN ('pending', 'accepted', 'declined')) | |
| requesting_owner_consent | varchar(15) | NO | `'accepted'` | CHECK (requesting_owner_consent IN ('accepted', 'pending')) | Requester implicitly consents |
| target_owner_consent | varchar(15) | NO | `'pending'` | CHECK (target_owner_consent IN ('accepted', 'pending', 'declined')) | |
| reviewer_consent | varchar(20) | NO | `'not_required'` | CHECK (reviewer_consent IN ('accepted', 'pending', 'declined', 'not_required')) | Only required for append type |
| resulting_idea_id | uuid | YES | NULL | FK → ideas(id) | New merged idea (merge type only, set on completion) |
| created_at | timestamptz | NO | now() | | |
| resolved_at | timestamptz | YES | NULL | | When accepted or declined |

| Constraint | Type | Columns |
|-----------|------|---------|
| uq_active_merge_request | UNIQUE | (requesting_idea_id, target_idea_id) WHERE status = 'pending' | One active merge request per pair |

**Notes:**
- Declined merge requests are permanently dismissed — same pair never suggested again (F-5.7).

---

### facilitator_context_bucket

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Singleton table. Admin-managed table of contents for the facilitator AI.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| content | text | NO | `''` | | Free text: table of contents describing available company context (F-2.16) |
| updated_by | uuid | YES | NULL | FK → users(id) | Last admin to edit |
| updated_at | timestamptz | NO | now() | | |

**Notes:**
- Single row. Application ensures only one record exists.

---

### context_agent_bucket

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Singleton table. Admin-managed detailed company information.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| sections | jsonb | NO | `{}` | | Structured sections: existing applications, domain terminology, company structure (F-2.16) |
| free_text | text | NO | `''` | | Additional unstructured content |
| updated_by | uuid | YES | NULL | FK → users(id) | Last admin to edit |
| updated_at | timestamptz | NO | now() | | |

**Notes:**
- Single row. Application ensures only one record exists.

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
| chat_message_cap | 5 | Chat messages before AI processing lockout per idea (F-2.11) |
| idle_timeout | 300 | Seconds before user is marked idle |
| idle_disconnect | 120 | Seconds in idle before connection disconnects |
| max_reconnection_backoff | 30 | Maximum reconnection retry interval (seconds) |
| soft_delete_countdown | 30 | Days before permanent deletion from trash |
| debounce_timer | 3 | Seconds after last chat message before AI processes |
| default_app_language | de | Default language for new users |
| max_keywords_per_idea | 20 | Maximum abstract keywords per idea |
| min_keyword_overlap | 7 | Minimum keyword matches to trigger similarity |
| similarity_time_limit | 180 | Days to look back for keyword matching |

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
| ai_processing_timeout | 60 | Seconds timeout for user-facing agent invocations (Facilitator, Summarizing AI, Merge Synthesizer) |
| recent_message_count | 20 | Number of recent chat messages included in Facilitator context |
| context_compression_threshold | 60 | Context utilization percentage that triggers compression |
| context_rag_top_k | 5 | Number of chunks retrieved per RAG query |
| context_rag_min_similarity | 0.7 | Minimum cosine similarity for RAG chunk retrieval |
| similarity_vector_threshold | 0.75 | Cosine similarity threshold for idea similarity detection |

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

### idea_embeddings

> **AI service owned.** Schema defined here for database completeness. AI Engineer may refine in `docs/03-ai/`.

Semantic embeddings per idea for vector-based similarity detection. Updated after each keyword generation cycle.

| Column | Type | Nullable | Default | Constraints | Notes |
|--------|------|----------|---------|-------------|-------|
| id | uuid | NO | gen_random_uuid() | PK | |
| idea_id | uuid | NO | — | FK → ideas(id) ON DELETE CASCADE, UNIQUE | One embedding per idea |
| embedding | vector(1536) | NO | — | | Embedding of idea content (dimension per AI Engineer's model choice) |
| source_text_hash | varchar(64) | NO | — | | SHA-256 hash of the source text used to generate the embedding. Skip re-embedding if unchanged. |
| updated_at | timestamptz | NO | now() | | |

**Notes:**
- The embedding source text composition is defined by the AI Engineer (likely: title + chat summary + board content).
- `source_text_hash` enables skipping re-embedding when source text hasn't changed.
- Used by the similarity pipeline: vector cosine similarity search complements keyword matching. Either threshold triggers Deep Comparison.
- An HNSW index on the `embedding` column enables fast similarity search. See Indexes section.

---

## Relationships

```
users 1──N ideas (owner_id FK)
users 0──N ideas (co_owner_id FK, merged ideas only)
users N──M ideas (via idea_collaborators)
users 1──N review_assignments (reviewer_id FK)
users 1──N notifications (user_id FK)
users 1──N collaboration_invitations (as inviter)
users 1──N collaboration_invitations (as invitee)

ideas 1──N chat_messages
ideas 1──N board_nodes
ideas 1──N board_connections
ideas 1──1 brd_drafts
ideas 1──N brd_versions
ideas 1──N review_assignments
ideas 1──N review_timeline_entries
ideas 1──N collaboration_invitations
ideas 1──1 idea_keywords
ideas 1──N merge_requests (as requesting or target)
ideas 0──1 ideas (merged_from — original references merged)
ideas 0──1 ideas (closed_by_merge — old references new)
ideas 0──1 ideas (closed_by_append — open references in-review)

chat_messages 0──1 ai_reactions
chat_messages 0──N user_reactions

board_nodes 0──1 board_nodes (parent_id → parent Group)
board_nodes 1──N board_nodes (children, if Group)
board_nodes 1──N board_connections (as source or target)

review_timeline_entries 0──1 review_timeline_entries (parent_entry_id → nested replies)
review_timeline_entries 0──1 brd_versions (old_version_id)
review_timeline_entries 0──1 brd_versions (new_version_id)

merge_requests N──1 ideas (requesting_idea_id)
merge_requests N──1 ideas (target_idea_id)
merge_requests 0──1 ideas (resulting_idea_id)
```

---

## Indexes

| Table | Index Name | Columns | Type | Rationale |
|-------|-----------|---------|------|-----------|
| ideas | idx_ideas_owner | owner_id | btree | Landing page: "My Ideas" list |
| ideas | idx_ideas_co_owner | co_owner_id | btree | Landing page: merged ideas lookup |
| ideas | idx_ideas_state | state | btree | Filter by state on landing page, review page |
| ideas | idx_ideas_deleted_at | deleted_at | btree | Trash list, soft delete cleanup job |
| ideas | idx_ideas_state_deleted | state, deleted_at | btree | Combined filter: active ideas by state |
| idea_collaborators | idx_collab_user | user_id | btree | Landing page: "Collaborating" list |
| idea_collaborators | idx_collab_idea | idea_id | btree | Idea workspace: collaborator list |
| chat_messages | idx_chat_idea_created | idea_id, created_at | btree | Chat history loading, ordered by time |
| chat_messages | idx_chat_sender | sender_id | btree | User stats: message count |
| board_nodes | idx_board_idea | idea_id | btree | Load all board nodes for an idea |
| board_nodes | idx_board_parent | parent_id | btree | Group children lookup |
| board_connections | idx_conn_idea | idea_id | btree | Load all connections for an idea |
| board_connections | idx_conn_source | source_node_id | btree | Connection lookup by source node |
| board_connections | idx_conn_target | target_node_id | btree | Connection lookup by target node |
| brd_versions | idx_brd_ver_idea | idea_id, version_number | btree | Version history per idea |
| review_assignments | idx_review_reviewer | reviewer_id, unassigned_at | btree | Review page: "Assigned to me" |
| review_assignments | idx_review_idea | idea_id | btree | Idea review lookup |
| review_timeline_entries | idx_timeline_idea | idea_id, created_at | btree | Timeline loading, ordered by time |
| review_timeline_entries | idx_timeline_parent | parent_entry_id | btree | Nested reply loading |
| collaboration_invitations | idx_invite_invitee | invitee_id, status | btree | Landing page: pending invitations |
| collaboration_invitations | idx_invite_idea | idea_id | btree | Idea invitation list |
| notifications | idx_notif_user_unread | user_id, is_read, action_taken | btree | Notification bell: unread count + list |
| notifications | idx_notif_created | user_id, created_at DESC | btree | Notification list ordering |
| chat_context_summaries | idx_ctx_summary_idea | idea_id | btree | AI context assembly per idea |
| idea_keywords | idx_keywords_idea | idea_id | btree (UNIQUE via table constraint) | Keyword lookup per idea |
| merge_requests | idx_merge_target | target_idea_id, status | btree | Active merge requests for an idea |
| merge_requests | idx_merge_requesting | requesting_idea_id, status | btree | Outbound merge requests |
| users | idx_users_email | email | btree (UNIQUE via column constraint) | User lookup by email, search |
| users | idx_users_display_name | display_name | btree | User search by name (F-8.2, F-11.6) |
| context_chunks | idx_chunks_embedding | embedding | hnsw (vector_cosine_ops) | Fast cosine similarity search for RAG retrieval |
| context_chunks | idx_chunks_bucket | bucket_id | btree | Bulk delete + re-insert on bucket update |
| idea_embeddings | idx_idea_embed_embedding | embedding | hnsw (vector_cosine_ops) | Fast cosine similarity search for idea deduplication |
| idea_embeddings | idx_idea_embed_idea | idea_id | btree (UNIQUE via table constraint) | Embedding lookup per idea |

---

## Enums / Constants

Enums are implemented as CHECK constraints on varchar columns (not PostgreSQL native enums) for easier migration and Django ORM compatibility.

| Name | Values | Used In |
|------|--------|---------|
| idea_state | open, in_review, accepted, dropped, rejected | ideas.state. Transitions: open→in_review, in_review→accepted/dropped/rejected, accepted→open (reopen) |
| idea_visibility | private, collaborating | ideas.visibility |
| agent_mode | interactive, silent | ideas.agent_mode |
| sender_type | user, ai | chat_messages.sender_type |
| message_type | regular, delegation | chat_messages.message_type |
| reaction_type | thumbs_up, thumbs_down, heart | ai_reactions, user_reactions |
| node_type | box, group, free_text | board_nodes.node_type |
| created_by_type | user, ai | board_nodes.created_by |
| invitation_status | pending, accepted, declined, revoked | collaboration_invitations.status |
| entry_type | comment, state_change, resubmission | review_timeline_entries.entry_type |
| assignment_source | submitter, self | review_assignments.assigned_by |
| merge_type | merge, append | merge_requests.merge_type |
| merge_status | pending, accepted, declined | merge_requests.status |
| consent_status | accepted, pending, declined, not_required | merge_requests consent columns |

---

## Migration Strategy

- **Tool:** Django ORM migrations (`python manage.py makemigrations` / `migrate`)
- **Naming:** Auto-generated by Django (sequential numbered files per app)
- **Seed data:** Admin parameters table seeded with default values via a data migration
- **Singleton initialization:** Facilitator context bucket and context agent bucket created via data migration (single empty row each)
- **Schema changes:** All schema changes through Django migrations — no raw SQL unless necessary for PostgreSQL-specific features (partial unique indexes)
- **pgvector setup:** The `context_chunks` and `idea_embeddings` tables require the pgvector extension (`CREATE EXTENSION vector`). Docker PostgreSQL image should use `pgvector/pgvector:pg16` or install the extension manually. Extension creation handled in an initial migration.

## Seed Data

Data that must exist for the application to boot and function.

| Table | Data | Purpose | When Created |
|-------|------|---------|-------------|
| admin_parameters | All parameters from seed data tables above (application + infrastructure) | Runtime-configurable system parameters with defaults | Data migration |
| facilitator_context_bucket | Single empty row (content = '') | Singleton for admin AI context management | Data migration |
| context_agent_bucket | Single empty row (sections = {}, free_text = '') | Singleton for admin detailed context management | Data migration |
| users (dev only) | 4 preconfigured dev users (F-7.1) | Auth bypass mode: Dev User 1 (User), Dev User 2 (User), Dev User 3 (User+Reviewer), Dev User 4 (User+Admin) | Conditional data migration (only when DEBUG=True) |

---

## Notes

- **Immutable tables:** `chat_messages`, `brd_versions`, `review_timeline_entries` are append-only. No UPDATE or DELETE. Application layer enforces this.
- **Soft delete:** Only `ideas` uses soft delete (`deleted_at` timestamp). All other deletions are hard deletes (via CASCADE from idea deletion, or explicit removal).
- **JSONB usage:** Used sparingly for flexible schemas: `email_notification_preferences` (user), `section_locks` (BRD draft), `readiness_evaluation` (BRD draft), `sections` (context agent bucket). All other data uses typed columns.
- **Timezone-aware timestamps:** All `timestamptz` columns. Django `USE_TZ=True`.
- **Array fields:** `users.roles` (varchar[]) and `idea_keywords.keywords` (varchar[]) use PostgreSQL native array types, supported by Django's `ArrayField`.
- **Board state is current-only.** No versioning on board nodes or connections. Undo/redo handled entirely in the frontend (F-3.7).
- **Cross-service data access:** In the microservices architecture, tables are grouped by service domain (see Schema Overview "Service Owner" column). Foreign keys that cross service boundaries become application-level references (UUID stored but no DB-level FK constraint). Service boundaries defined in `project-structure.md`.
- **Cross-service raw SQL exception:** Since all tables share the same PostgreSQL instance, limited cross-service direct DB access is permitted in these cases: (1) Background Celery tasks in Core may query AI-owned tables (e.g., `idea_embeddings`) via raw SQL for performance-critical vector similarity operations. (2) Core gRPC servicers may read Gateway-owned tables (e.g., `users`) via raw SQL for display name resolution, avoiding circular gRPC dependencies. (3) Gateway may use unmanaged Django models (`managed = False`) to read/write Core-owned tables (e.g., `admin_parameters`) when both services share the same DB instance and gRPC RPCs are not defined. All cross-service access should be documented and kept minimal.
- **pgvector dependency:** The `context_chunks` and `idea_embeddings` tables require the pgvector PostgreSQL extension. Docker PostgreSQL image should use `pgvector/pgvector:pg16`.
