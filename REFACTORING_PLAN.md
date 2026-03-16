# ZiqReq Refactoring Plan: Ideas/Brainstorming -> Projects/Requirements Assembly

## Overview

This plan transforms ZiqReq from an AI-guided brainstorming platform into a structured
requirements assembly tool. Users create projects (software or non-software), chat with
an AI to structure their known requirements, and produce formal requirements documents.

### Key Changes Summary

- **Rename**: "Idea" -> "Project" everywhere (DB, API, frontend, prompts, translations)
- **Add**: Project type distinction (Software vs Non-Software) at creation time
- **Remove**: Board (XYFlow canvas), merge/similarity/keyword system entirely
- **Replace Board with**: Structured Requirements Panel (accordion + sortable cards)
- **Replace BRD with**: Hierarchical requirements document (Epics/Stories or Milestones/Packages)
- **Rework AI**: New system prompts for structuring (not brainstorming), type-specific behavior
- **Rework Admin**: Per-type context buckets + global bucket
- **Rework PDF**: Type-specific document templates
- **Clean Process Steps**: "Define -> Structure -> Review" instead of "Brainstorm -> Document -> Review"

---

## Phase 1: Remove Features (Clean Slate)

These stories remove deprecated features completely. No orphaned code should remain.
Execute in order since later stories may depend on earlier removals being clean.

---

### Story 1.1: Remove Merge/Similarity/Keyword System — Backend

**Goal**: Completely remove the merge, similarity detection, keyword extraction, and
append features from all backend services.

**Scope**:

DELETE entire directories:
- `services/core/apps/similarity/` (models, services, tasks, migrations, tests)
- `services/gateway/apps/similarity/` (models, views, serializers, urls, services, migrations, tests)
- `services/ai/agents/keyword_agent/` (agent, prompt, __init__)
- `services/ai/agents/deep_comparison/` (agent, prompt, consumer, __init__)
- `services/ai/agents/merge_synthesizer/` (agent, prompt, consumer, __init__)
- `services/ai/tests/test_keyword_agent.py`
- `services/ai/tests/test_deep_comparison.py`
- `services/ai/tests/test_merge_synthesizer.py`
- `services/ai/fixtures/keyword_agent_response.json`
- `services/ai/fixtures/merge_synthesizer_response.json`
- `services/ai/embedding/idea_embedder.py`
- `services/ai/embedding/retriever.py` (only if solely used for similarity — verify first)
- `services/ai/apps/embedding/models.py` (IdeaEmbedding model — verify not used by RAG context)
- `services/gateway/events/merge_consumer.py`
- `services/gateway/events/append_consumer.py`
- `services/notification/consumers/similarity_events.py`

DELETE test files:
- `services/gateway/apps/ideas/tests/test_merge_request.py`
- `services/gateway/apps/ideas/tests/test_append_execution.py`
- `services/gateway/apps/ideas/tests/test_append_flow.py`
- `services/gateway/apps/ideas/tests/test_manual_merge.py`
- `services/gateway/apps/ideas/tests/test_recursive_merge.py`
- `services/gateway/apps/ideas/tests/test_similar_ideas.py`
- `services/core/apps/similarity/tests/` (entire directory)

MODIFY — remove merge/similarity references from:
- `services/core/apps/ideas/models.py`:
  - Remove fields: `merged_from_idea_1_id`, `merged_from_idea_2_id`, `closed_by_merge_id`, `closed_by_append_id`, `co_owner_id`
- `services/core/apps/ideas/tasks.py`: Remove similarity/merge cleanup logic
- `services/gateway/apps/ideas/views.py`:
  - Remove functions: `get_similar_ideas`, `create_merge_request`, `consent_merge_request`, `_get_near_threshold_matches`
  - Remove merge_request_pending/merged_idea_ref/appended_idea_ref from `_get_idea` response
  - Remove imports for similarity models/serializers
- `services/gateway/apps/ideas/serializers.py`:
  - Remove: `SimilarIdeaSerializer`, `MergeRequestCreateSerializer`, `MergeRequestConsentSerializer`, `MergeRequestSerializer`
- `services/gateway/apps/ideas/urls.py`:
  - Remove: `similar` and `merge-request` URL patterns
- `services/gateway/gateway/urls.py`:
  - Remove: merge-request consent endpoint, ideas search-ref (if only used for merge)
- `services/core/core/settings/base.py`:
  - Remove `"apps.similarity"` from INSTALLED_APPS
  - Remove Celery beat schedule entries for `keyword-matching-sweep`, `vector-similarity-sweep`
- `services/gateway/gateway/settings/base.py`:
  - Remove `"apps.similarity"` from INSTALLED_APPS
- `services/gateway/apps/websocket/consumers.py`:
  - Remove methods: `merge_request`, `merge_complete`, `append_complete`
- `services/gateway/events/publisher.py`:
  - Remove similarity/merge event types
- `services/core/events/consumers.py`:
  - Remove `handle_merge_synthesizer_complete`, `handle_append_accepted`
- `services/notification/main.py`:
  - Remove similarity event handler imports, routing, and RabbitMQ binding keys
- `services/notification/mailer/renderer.py`:
  - Remove "merge_request" reference type
- `services/core/apps/admin_config/migrations/0002_seed_parameters.py`:
  - Remove parameters: `max_keywords_per_idea`, `min_keyword_overlap`, `similarity_time_limit`, `similarity_vector_threshold`
- `proto/core.proto`:
  - Remove `UpdateIdeaKeywords` RPC and related messages

IMPORTANT: Also remove the `research_similar_ideas` tool from the Facilitator agent:
- `services/ai/agents/facilitator/plugins.py`: Remove the tool function and its registration
- `services/ai/agents/facilitator/prompt.py`: Remove rule 2 in INTERACTIVE_RULES about similar ideas

**Verification**: All backend services should start without errors. No imports of deleted
modules should remain. Run `grep -r "similarity\|merge_synth\|keyword_agent\|deep_comparison\|append_service" services/` and confirm zero hits (excluding git history).

**Database**: Create a new migration that:
- Drops tables: `idea_keywords`, `merge_requests`, `idea_embeddings`
- Removes columns from `ideas`: `merged_from_idea_1_id`, `merged_from_idea_2_id`, `closed_by_merge_id`, `closed_by_append_id`, `co_owner_id`

---

### Story 1.2: Remove Merge/Similarity/Keyword System — Frontend

**Goal**: Completely remove all merge, similarity, and append UI from the frontend.

**Scope**:

DELETE files:
- `frontend/src/components/workspace/MergeRequestBanner.tsx`
- `frontend/src/components/workspace/MergedIdeaBanner.tsx`
- `frontend/src/components/workspace/AppendedIdeaBanner.tsx`
- `frontend/src/components/workspace/ManualMergeModal.tsx`
- `frontend/src/api/similarity.ts`

MODIFY:
- `frontend/src/pages/IdeaWorkspace/index.tsx`:
  - Remove imports: MergeRequestBanner, MergedIdeaBanner, AppendedIdeaBanner
  - Remove all banner rendering for merge/append
  - Remove `hasMergePending`, `isClosedByMerge`, `isClosedByAppend` logic
  - Remove `handleMergeResolved` callback
  - Remove merge-related WebSocket event listeners (`ws:merge_request`)
  - Simplify `effectiveChatLocked` and `effectiveLockReason` (remove merge/append conditions)
  - Simplify `isClosedIdea` (remove merge/append checks)
- `frontend/src/api/ideas.ts`:
  - Remove `merge_request_pending`, `merged_idea_ref`, `appended_idea_ref` from `Idea` interface
  - Remove `consentMergeRequest` and related functions/types
- `frontend/src/hooks/use-websocket.ts`:
  - Remove handlers for `merge_request`, `merge_complete`, `append_complete` events
- `frontend/src/components/notifications/NotificationItem.tsx`:
  - Remove similarity-related notification rendering
- `frontend/src/components/notifications/NotificationPanel.tsx`:
  - Remove "merge_request" navigation case
- `frontend/src/components/notifications/EmailPreferencesPanel.tsx`:
  - Remove "similarity" email preference options
- `frontend/src/i18n/locales/en.json`:
  - Remove entire "merge" section
  - Remove similarity notification type keys
  - Remove merge-related email preference keys
- `frontend/src/i18n/locales/de.json`:
  - Same removals as en.json

**Verification**: `grep -r "merge\|similarity\|append.*idea\|ManualMerge\|MergedIdea\|AppendedIdea" frontend/src/` should return zero hits (excluding git-related or unrelated uses of "merge").

---

### Story 1.3: Remove Board (XYFlow Canvas) — Backend

**Goal**: Completely remove the board/canvas feature from backend services.

**Scope**:

DELETE entire directories:
- `services/core/apps/board/` (models, views, migrations, tests)
- `services/gateway/apps/board/` (models, views, serializers, urls, migrations, tests)
- `services/ai/agents/board_agent/` (agent, plugins, prompt, __init__)
- Any board-related test files in `services/ai/tests/`

MODIFY:
- `services/gateway/gateway/urls.py`: Remove board URL includes
- `services/gateway/apps/ideas/urls.py`: Remove board-related nested URLs (if any)
- `services/core/core/settings/base.py`: Remove `"apps.board"` from INSTALLED_APPS
- `services/gateway/gateway/settings/base.py`: Remove `"apps.board"` from INSTALLED_APPS
- `services/gateway/apps/websocket/consumers.py`:
  - Remove `board_selection` handler
  - Remove `board_update`, `board_lock_change` event forwarding
- `services/ai/agents/facilitator/plugins.py`:
  - Remove `request_board_changes` tool entirely
- `services/ai/agents/facilitator/prompt.py`:
  - Remove `<board_references>` section
  - Remove `<board_instructions_guidance>` section
  - Remove `<board_state>` from the `<idea>` context block
  - Remove `board_nodes_formatted` and `board_connections_formatted` from build_system_prompt
  - Remove `[[Item Title]]` board reference syntax from `send_chat_message` tool description
- `services/ai/processing/pipeline.py`:
  - Remove board state assembly from context building
  - Remove board agent invocation step
- `services/ai/agents/summarizing_ai/prompt.py`:
  - Remove `<board_state>` from the prompt template
  - Remove `_format_board_state` function
  - Remove `board_state` from `build_system_prompt` input handling
- `proto/core.proto`:
  - Remove board-related messages from IdeaContextResponse (if present)

**Database**: Create migration to drop tables: `board_nodes`, `board_connections`

**Verification**: `grep -r "board_agent\|board_node\|board_connection\|BoardNode\|xyflow\|ReactFlow" services/` should return zero hits.

---

### Story 1.4: Remove Board (XYFlow Canvas) — Frontend

**Goal**: Completely remove the board/canvas UI and XYFlow dependency from frontend.

**Scope**:

DELETE files/directories:
- All board-related components (find with `grep -rl "xyflow\|ReactFlow\|BoardCanvas\|board" frontend/src/components/`)
  - The board canvas component
  - Board node components (BoxNode, GroupNode, FreeTextNode, etc.)
  - Board toolbar/controls
  - Board connection components
- `frontend/src/types/models.ts`: Remove `BoardNode`, `BoardConnection` interfaces
- `frontend/src/api/board.ts` (if exists)
- Any board-related hooks

MODIFY:
- `frontend/src/components/workspace/WorkspaceLayout.tsx`:
  - This currently renders chat + board side-by-side
  - For now, make it render chat only (full width) — the structured panel comes in Phase 3
  - Remove `ReactFlowProvider` import
- `frontend/src/pages/IdeaWorkspace/index.tsx`:
  - Remove board-related props passed to WorkspaceLayout
- `frontend/src/hooks/use-websocket.ts`:
  - Remove `board_update`, `board_lock_change`, `board_selection` handlers
- `frontend/src/store/`:
  - Remove any board-related Redux slices
- `frontend/src/i18n/locales/en.json` and `de.json`:
  - Remove board-related translation keys
- `frontend/package.json`:
  - Remove `@xyflow/react` dependency (and any xyflow-related packages)
  - Run install to update lockfile

**Verification**: `grep -r "xyflow\|ReactFlow\|BoardCanvas\|board_node\|board_connection\|BoardNode" frontend/src/` should return zero hits. App should build without errors.

---

## Phase 2: Rename (Idea -> Project)

This phase renames the core entity. Must be done after Phase 1 removals to minimize
the number of files that need renaming.

---

### Story 2.1: Rename Idea to Project — Database & Backend Models

**Goal**: Rename the core "Idea" entity to "Project" across all database tables,
Django models, and backend code.

**Scope**:

DATABASE MIGRATIONS (create new migrations in each service):
- Rename table `ideas` -> `projects`
- Rename table `idea_collaborators` -> `project_collaborators`
- Rename all `idea_id` columns to `project_id` across all tables:
  - `chat_messages.idea_id` -> `project_id`
  - `brd_drafts.idea_id` -> `project_id`
  - `brd_versions.idea_id` -> `project_id`
  - `review_assignments.idea_id` -> `project_id`
  - `review_timeline_entries.idea_id` -> `project_id`
  - `ai_reactions.idea_id` (if exists) -> `project_id`
  - Any other tables with `idea_id` FK
- Add new column `projects.project_type` (varchar, choices: "software", "non_software", non-null, no default — existing rows should get a migration default)
- Rename indexes accordingly

RENAME Django apps (in both core and gateway services):
- `services/core/apps/ideas/` -> `services/core/apps/projects/`
  - Rename `Idea` model class to `Project`
  - Rename `IdeaCollaborator` to `ProjectCollaborator`
  - Add `project_type` field with choices `[("software", "Software"), ("non_software", "Non-Software")]`
  - Update `db_table`, indexes, `__str__`, all internal references
  - Update `AppConfig` name
- `services/gateway/apps/ideas/` -> `services/gateway/apps/projects/`
  - Same renames as core
  - Update all view functions, serializers, URL names
  - Rename `_get_idea_or_error` -> `_get_project_or_error`, error messages "Idea not found" -> "Project not found"

UPDATE all cross-references in other apps:
- `services/core/apps/chat/`: `idea_id` -> `project_id` in models and queries
- `services/core/apps/brd/`: `idea_id` -> `project_id` in models
- `services/core/apps/review/`: `idea_id` -> `project_id` in models
- `services/core/apps/collaboration/`: references to idea -> project
- `services/gateway/apps/brd/views.py`: All "idea" references
- `services/gateway/apps/chat/views.py`: All "idea" references
- `services/gateway/apps/review/views.py`: All "idea" references
- `services/gateway/apps/collaboration/views.py`: All "idea" references
- Settings files: Update INSTALLED_APPS (`"apps.ideas"` -> `"apps.projects"`)

UPDATE gRPC:
- `proto/core.proto`: `GetIdeaContext` -> `GetProjectContext`, `IdeaContextRequest` -> `ProjectContextRequest`, etc.
- `proto/gateway.proto`: Same renames
- `proto/pdf.proto`: `idea_id` -> `project_id`, `idea_title` -> `project_title`
- Regenerate all proto stubs
- Update all gRPC client/servicer code

UPDATE WebSocket:
- `services/gateway/apps/websocket/consumers.py`:
  - Rename `IdeaConsumer` -> `ProjectConsumer`
  - Rename `subscribe_idea` -> `subscribe_project`, `unsubscribe_idea` -> `unsubscribe_project`
  - Rename channel group `idea_{id}` -> `project_{id}`

UPDATE events:
- All RabbitMQ event publishers/consumers: rename event types containing "idea"
- `services/notification/`: Update all templates/renderers that reference "idea"

**Verification**: `grep -r "idea\|Idea" services/ --include="*.py" | grep -v "\.pyc\|migration\|__pycache__\|\.git"` should only show the word in comments/strings that have been intentionally updated, not leftover references.

---

### Story 2.2: Rename Idea to Project — API Routes

**Goal**: Update all REST API endpoint paths from `/api/ideas/` to `/api/projects/`.

**Scope**:
- `services/gateway/gateway/urls.py`: `/api/ideas/` -> `/api/projects/`
- `services/gateway/apps/projects/urls.py` (renamed from ideas):
  - `/<str:idea_id>/` -> `/<str:project_id>/`
  - Update all URL pattern names
- Update all view function parameter names from `idea_id` to `project_id`
- Update the WebSocket routing if it references idea paths
- Update all error messages from "Idea" to "Project"

---

### Story 2.3: Rename Idea to Project — Frontend

**Goal**: Rename all frontend references from "idea" to "project".

**Scope**:

RENAME files:
- `frontend/src/api/ideas.ts` -> `frontend/src/api/projects.ts`
- `frontend/src/pages/IdeaWorkspace/` -> `frontend/src/pages/ProjectWorkspace/`
- `frontend/src/hooks/use-my-ideas.ts` -> `frontend/src/hooks/use-my-projects.ts`
- `frontend/src/hooks/use-collaborating-ideas.ts` -> `frontend/src/hooks/use-collaborating-projects.ts`
- `frontend/src/hooks/use-create-idea.ts` -> `frontend/src/hooks/use-create-project.ts`
- `frontend/src/hooks/use-delete-idea.ts` -> `frontend/src/hooks/use-delete-project.ts`
- `frontend/src/hooks/use-restore-idea.ts` -> `frontend/src/hooks/use-restore-project.ts`
- `frontend/src/hooks/use-ideas-filters.ts` -> `frontend/src/hooks/use-projects-filters.ts`
- `frontend/src/hooks/useIdeaSync.ts` -> `frontend/src/hooks/useProjectSync.ts`
- `frontend/src/components/landing/IdeaCard.tsx` -> `frontend/src/components/landing/ProjectCard.tsx`
- `frontend/src/components/landing/IdeaCardSkeleton.tsx` -> `frontend/src/components/landing/ProjectCardSkeleton.tsx`
- `frontend/src/components/workspace/WorkspaceHeader.tsx`: Rename internal idea refs

UPDATE types:
- `frontend/src/types/models.ts`:
  - Rename `Idea` interface to `Project`, add `projectType: "software" | "non_software"` field
  - Remove `BoardNode`, `BoardConnection` (if not already done)
- `frontend/src/types/api.ts`: Update request/response types
- `frontend/src/types/websocket.ts`: Rename event types

UPDATE routing:
- `frontend/src/app/router.tsx`: `/idea/:id` -> `/project/:id`

UPDATE all API calls:
- All `fetchIdea` -> `fetchProject`, `createIdea` -> `createProject`, `patchIdea` -> `patchProject`, etc.
- All endpoint URLs from `/api/ideas/` to `/api/projects/`

UPDATE Redux/state:
- Any Redux slices referencing "idea"
- React Query keys: `["ideas"]` -> `["projects"]`, etc.

UPDATE WebSocket:
- `subscribe_idea` -> `subscribe_project`, `unsubscribe_idea` -> `unsubscribe_project`
- Event names: `ws:idea_*` -> `ws:project_*`

UPDATE all component props, state variables, function names, CSS classes containing "idea".

---

### Story 2.4: Rename Brainstorming Terminology & Update Translations

**Goal**: Replace all brainstorming/idea language in user-facing text, translations,
and AI prompts with project/requirements assembly language.

**Scope**:

UPDATE translations (`frontend/src/i18n/locales/en.json` and `de.json`):
- `landing.hero.heading`: Change from brainstorming prompt to project creation prompt
- `landing.hero.subtext`: Update to requirements assembly messaging
- `landing.hero.placeholder`: Remove "Describe your idea"
- `landing.hero.submit`: Change to "Create Project" or similar
- `landing.lists.myIdeas` -> `landing.lists.myProjects`
- `landing.empty.myIdeas` -> `landing.empty.myProjects` (update text)
- `landing.untitled` -> "Untitled project"
- All `workspace.*` keys: Replace "idea" with "project"
- All `process.*` keys: Replace "brainstorm" with "define"
  - `process.brainstormDoneHint` -> `process.defineDoneHint` (update text)
  - `process.continueToDocument` -> `process.continueToStructure`
- `admin.ideas` -> `admin.projects`
- Remove all keys that referenced merge/similarity/brainstorming

UPDATE process step labels:
- Step 1: "Define" (was "Brainstorm")
- Step 2: "Structure" (was "Document")
- Step 3: "Review" (unchanged)

UPDATE AI prompts — remove all brainstorming language:
- Facilitator prompt: "brainstorming platform" -> "requirements assembly platform"
- Facilitator identity: "guide through brainstorming" -> "help structure requirements"
- Conversation rules: Remove brainstorming-specific guidance, add structuring guidance
- Summarizing AI prompt: Update identity and references
- Context agent prompt: Update references

---

## Phase 3: Add Project Type & New Data Models

---

### Story 3.1: Project Type Selection — Creation Flow

**Goal**: Add project type selection (Software / Non-Software) when creating a new project.

**Scope**:

FRONTEND — New creation flow:
- Remove the `HeroSection` textarea-based creation
- Create new `HeroSection` with a "New Project" button (no textarea)
- Create `NewProjectModal` component:
  - Modal with two large selectable cards:
    - "Software Project" — icon, brief description ("Epics & User Stories")
    - "Non-Software Project" — icon, brief description ("Milestones & Work Packages")
  - "Create" button (disabled until type selected)
  - On create: navigates to `/project/:id`
- Update `use-create-project` hook:
  - Accept `projectType: "software" | "non_software"` parameter
  - No longer takes a `firstMessage` — project starts empty, user types first message in workspace

BACKEND:
- Update `createProject` API endpoint:
  - Accept `project_type` field (required)
  - No longer require `first_message` (make optional or remove)
  - Return created project with `project_type`
- `services/gateway/apps/projects/views.py`: Update create view
- `services/gateway/apps/projects/serializers.py`: Update create serializer

---

### Story 3.2: Structured Requirements Data Model — Backend

**Goal**: Replace the flat 6-section BRD with a hierarchical JSON-based requirements
document that differs by project type.

**Scope**:

NEW DATABASE STRUCTURE — Replace BrdDraft/BrdVersion with new models:

```python
# Requirements Document Draft (one per project, working version)
class RequirementsDocumentDraft(models.Model):
    id = UUIDField(primary_key=True)
    project_id = UUIDField(unique=True)

    # Top-level summary (shared by both types)
    title = TextField(null=True)
    short_description = TextField(null=True)

    # Hierarchical structure stored as JSON
    # Software: [{"id": uuid, "title": str, "description": str, "stories": [{"id": uuid, "title": str, "description": str, "acceptance_criteria": [str], "priority": str}]}]
    # Non-software: [{"id": uuid, "title": str, "description": str, "packages": [{"id": uuid, "title": str, "description": str, "deliverables": [str], "dependencies": [str]}]}]
    structure = JSONField(default=list)

    # Per-item locks (dict of item_id -> bool)
    item_locks = JSONField(default=dict)
    allow_information_gaps = BooleanField(default=False)
    readiness_evaluation = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "requirements_document_drafts"


# Immutable version snapshot
class RequirementsDocumentVersion(models.Model):
    id = UUIDField(primary_key=True)
    project_id = UUIDField()
    version_number = IntegerField()
    title = TextField(null=True)
    short_description = TextField(null=True)
    structure = JSONField(default=list)
    pdf_file_path = CharField(max_length=500, null=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "requirements_document_versions"
        unique_together = [("project_id", "version_number")]
```

MIGRATION:
- Create new tables
- Migrate existing BrdDraft/BrdVersion data (map old 6 sections into the new structure
  as a single epic/milestone with the content as description — best-effort migration)
- Drop old `brd_drafts` and `brd_versions` tables

UPDATE serializers and views:
- New serializers for the requirements document structure
- CRUD endpoints for individual items within the structure (add/edit/delete/reorder epics, stories, milestones, packages)
- Validation: enforce correct structure based on project type

NEW API ENDPOINTS:
- `GET /api/projects/:id/requirements/` — get current draft
- `PATCH /api/projects/:id/requirements/` — update top-level fields (title, description)
- `POST /api/projects/:id/requirements/items` — add an epic/milestone
- `PATCH /api/projects/:id/requirements/items/:item_id` — update an epic/milestone
- `DELETE /api/projects/:id/requirements/items/:item_id` — delete an epic/milestone
- `POST /api/projects/:id/requirements/items/:item_id/children` — add a story/package
- `PATCH /api/projects/:id/requirements/items/:item_id/children/:child_id` — update
- `DELETE /api/projects/:id/requirements/items/:item_id/children/:child_id` — delete
- `POST /api/projects/:id/requirements/reorder` — reorder items (accepts ordered ID list)
- `POST /api/projects/:id/requirements/generate` — trigger AI generation

WebSocket events for real-time sync:
- `requirements_updated` — broadcast when structure changes (for multi-user)
- `requirements_generating` — AI is generating
- `requirements_ready` — AI generation complete

---

### Story 3.3: Structured Requirements Panel — Frontend

**Goal**: Build the new right-side panel that visualizes and allows editing of the
hierarchical requirements structure.

**Scope**:

NEW COMPONENTS:

`RequirementsPanel` (main container):
- Shows project title + short description at top (editable)
- Shows contributors (owner + collaborators) — read-only display
- Below: list of Epics or Milestones (depending on project type)
- "Add Epic" / "Add Milestone" button at bottom
- Listens to WebSocket for real-time updates from other users / AI

`EpicCard` / `MilestoneCard` (top-level item):
- Collapsible accordion header: title, description preview, item count badge
- Expanded: shows child items (stories/packages)
- Inline editing of title and description
- Delete button (with confirmation)
- Drag handle for reordering

`UserStoryCard` / `WorkPackageCard` (child item):
- Compact card inside parent
- Software story: title, "As a... I want... So that..." description, acceptance criteria chips, priority badge
- Non-software package: title, description, deliverables list, dependencies list
- Inline editing on click
- Delete, drag-to-reorder within parent or between parents

`RequirementsItemEditor` (shared edit modal/inline form):
- Context-aware fields based on project type and item level
- Auto-save with debounce (300ms)
- Lock indicator if item is locked

Drag-and-drop:
- Use `@dnd-kit/core` or `@dnd-kit/sortable` for reorder (already lighter than xyflow)
- Stories can be moved between epics, packages between milestones

Multi-user support:
- Optimistic updates with WebSocket reconciliation
- Show "User X is editing..." indicators on items being edited
- Conflict resolution: last-write-wins with toast notification

UPDATE `WorkspaceLayout`:
- Change from chat+board split to chat+requirements panel split
- Default: 40% chat, 60% requirements panel (same ratio as before)

---

### Story 3.4: Admin Context Buckets — Per Project Type

**Goal**: Replace the single facilitator + company context bucket with three buckets:
global, software-specific, and non-software-specific.

**Scope**:

BACKEND:
- Update `facilitator_context_bucket` model:
  - Add `context_type` field: choices `["global", "software", "non_software"]`
  - Remove unique constraint, add unique_together on `context_type`
  - Seed 3 rows (one per type)
- Update `context_agent_bucket` model:
  - Same: add `context_type`, 3 rows
- Update API endpoints:
  - `GET/PATCH /api/admin/ai-context/facilitator?type=global|software|non_software`
  - `GET/PATCH /api/admin/ai-context/company?type=global|software|non_software`
- Update embedding/chunking pipeline:
  - Tag chunks with their `context_type`
  - When retrieving for a project, combine global + type-specific chunks

FRONTEND — Admin panel:
- `AIContextTab.tsx`:
  - Add tab bar or segmented control: "Global" | "Software" | "Non-Software"
  - Show facilitator + company context fields for each type
  - Each type saves independently

AI PIPELINE:
- When assembling facilitator context, combine:
  - Global facilitator bucket + type-specific facilitator bucket
- When querying context agent:
  - Search global + type-specific chunks (not the other type's chunks)

---

## Phase 4: AI System Prompt Rework

---

### Story 4.1: New Facilitator System Prompt — Project Type Aware

**Goal**: Rewrite the Facilitator AI system prompt to be a requirements structuring
assistant instead of a brainstorming facilitator, with type-specific behavior.

**Scope**:

REWRITE `services/ai/agents/facilitator/prompt.py`:

New identity (varies by type):
- Software: "You are the Requirements Assistant for ZiqReq. You help employees
  structure their software project requirements into Epics and User Stories."
- Non-software: "You are the Requirements Assistant for ZiqReq. You help employees
  structure their project requirements into Milestones and Work Packages."

New conversation rules:
- "Help the user organize their requirements. They already know what they need — your
  job is to help them structure it clearly."
- "When a user describes a requirement, suggest which epic/milestone it belongs to and
  help formulate it as a user story/work package."
- "Proactively suggest acceptance criteria for user stories / deliverables for work packages."
- "If a requirement is too large, suggest splitting it into multiple stories/packages."
- "If you notice gaps (e.g., an epic with no stories), point them out."
- Keep: language detection, multi-user awareness, context delegation
- Remove: all brainstorming language, board references, board instructions

New tool: `update_requirements_structure`:
- Replaces `request_board_changes`
- Sends structured JSON mutations to the requirements document:
  - add_epic/add_milestone, update_epic/update_milestone, remove_epic/remove_milestone
  - add_story/add_package, update_story/update_package, remove_story/remove_package
  - reorder operations
- The AI calls this when the conversation produces content that should be captured
  in the requirements structure

Keep tools:
- `send_chat_message` (remove board reference [[]] syntax)
- `react_to_message`
- `update_title`
- `delegate_to_context_agent`
- `delegate_to_context_extension`

Remove tools:
- `request_board_changes` (replaced by update_requirements_structure)
- `research_similar_ideas` (already removed in Phase 1)

Update `build_system_prompt` function:
- Accept `project_type` in context dict
- Inject type-specific identity, rules, and facilitator bucket content
- Include current requirements structure state (JSON) instead of board state
- Combine global + type-specific facilitator bucket

---

### Story 4.2: New Summarizing AI — Type-Specific Document Generation

**Goal**: Rewrite the Summarizing AI to generate structured requirements documents
(epics/stories or milestones/packages) instead of flat BRD sections.

**Scope**:

REWRITE `services/ai/agents/summarizing_ai/prompt.py`:

New prompt structure:
- Identity: "You generate structured requirements documents from project conversations."
- Input: chat history + current requirements structure (JSON)
- Output format varies by project type:

Software output:
```json
{
  "title": "Project Title",
  "short_description": "...",
  "structure": [
    {
      "id": "uuid",
      "title": "Epic Title",
      "description": "Epic description",
      "stories": [
        {
          "id": "uuid",
          "title": "Story Title",
          "description": "As a <role>, I want <goal>, so that <benefit>",
          "acceptance_criteria": ["Given... When... Then..."],
          "priority": "high|medium|low"
        }
      ]
    }
  ],
  "readiness_evaluation": {...}
}
```

Non-software output:
```json
{
  "title": "Project Title",
  "short_description": "...",
  "structure": [
    {
      "id": "uuid",
      "title": "Milestone Title",
      "description": "Milestone description",
      "packages": [
        {
          "id": "uuid",
          "title": "Work Package Title",
          "description": "...",
          "deliverables": ["..."],
          "dependencies": ["..."]
        }
      ]
    }
  ],
  "readiness_evaluation": {...}
}
```

Support same modes as before:
- `full_generation`: Generate entire structure from scratch
- `selective_regeneration`: Regenerate only unlocked items
- `item_regeneration`: Regenerate a specific item

Update readiness evaluation:
- Software: Does each epic have at least 1 story? Does each story have acceptance criteria?
- Non-software: Does each milestone have at least 1 package? Does each package have deliverables?

---

### Story 4.3: AI Pipeline Update — Requirements Structure Mutations

**Goal**: Update the AI processing pipeline to handle the new `update_requirements_structure`
tool and apply mutations to the requirements document.

**Scope**:

UPDATE `services/ai/processing/pipeline.py`:
- Remove board agent invocation step
- Add requirements structure mutation handler:
  - When Facilitator calls `update_requirements_structure`, apply the mutations to the
    RequirementsDocumentDraft via gRPC/direct DB
  - Broadcast `requirements_updated` WebSocket event to all connected clients
- Include current requirements structure JSON in the context assembly step (replacing board state)
- Include `project_type` in the context passed to the facilitator

NEW or UPDATE gRPC:
- Add `UpdateRequirementsStructure` RPC to apply mutations from AI
- Add `GetRequirementsState` RPC to fetch current structure for context assembly

---

## Phase 5: Document View & PDF Generation

---

### Story 5.1: New Document/Structure Step — Frontend

**Goal**: Replace the "Document" step content (old BRD section editor) with the new
requirements structure view.

**Scope**:

The "Structure" step (step 2) should show:
- The RequirementsPanel (same component from Story 3.3) but in a focused editing mode
- A side panel showing the PDF preview (same concept as current DocumentView)
- "Generate" / "Regenerate" button that triggers AI to populate/update the structure
- "Allow information gaps" toggle
- Readiness indicators per item
- Lock/unlock individual items from AI regeneration
- Submit button to proceed to review

REMOVE:
- `frontend/src/components/workspace/DocumentView.tsx` (replace entirely)

The key UX insight: In the "Define" step, the user sees chat + requirements panel
side by side (chat-driven). In the "Structure" step, the user sees the requirements
panel in full-width editing mode with PDF preview — this is where they polish before
submitting.

---

### Story 5.2: PDF Generation — Type-Specific Templates

**Goal**: Update the PDF generation service to produce type-specific requirements documents.

**Scope**:

UPDATE `services/pdf/generator/builder.py`:
- Accept `project_type` and structured JSON instead of flat sections
- Software PDF template:
  - Header: "Software Requirements Document"
  - Title + Short Description + Contributors
  - For each Epic: heading, description, table of user stories with columns (ID, Title, Description, Acceptance Criteria, Priority)
- Non-software PDF template:
  - Header: "Project Requirements Document"
  - Title + Short Description + Contributors
  - For each Milestone: heading, description, table of work packages with columns (ID, Title, Description, Deliverables, Dependencies)

UPDATE `services/pdf/generator/renderer.py`:
- Update validation (remove /TODO marker check or adapt to new structure)

UPDATE CSS template for new layout.

UPDATE gRPC:
- `proto/pdf.proto`: Update `PdfGenerationRequest` to include `project_type` and `structure` JSON

UPDATE `services/gateway/apps/brd/` (rename to `requirements_document`):
- Views: Update PDF preview and version download endpoints
- Serializers: Update for new structure

---

## Phase 6: Process Steps & Final Polish

---

### Story 6.1: Update Process Stepper & Workspace Flow

**Goal**: Update the 3-step process from "Brainstorm -> Document -> Review" to
"Define -> Structure -> Review" with updated gate logic.

**Scope**:

UPDATE `ProcessStepper.tsx`:
- Step names: "Define", "Structure", "Review"
- Step descriptions: Update to match new flow
- Type: `ProcessStep = "define" | "structure" | "review"`

UPDATE `ProjectWorkspace/index.tsx` (renamed from IdeaWorkspace):
- Replace `"brainstorm"` with `"define"` throughout
- Replace `"document"` with `"structure"` throughout
- Step content:
  - `define`: Chat + Requirements Panel side by side (WorkspaceLayout)
  - `structure`: Full-width requirements editor + PDF preview sidebar
  - `review`: ReviewSection (mostly unchanged)
- Update gate logic:
  - `canAccessStructure` = has at least one item in requirements structure OR has chat messages
  - `canAccessReview` = has been submitted (unchanged)
- Update URL params: `?step=structure`, `?step=review`

UPDATE translations for new step labels and descriptions.

---

### Story 6.2: Landing Page & Project List Updates

**Goal**: Update the landing page to reflect the new project-centric design.

**Scope**:

UPDATE `LandingPage/index.tsx`:
- Section titles: "My Projects", "Collaborating", "Invitations", "Trash"
- Remove the textarea from HeroSection (now just a "New Project" button)

UPDATE `HeroSection.tsx`:
- Simple heading + subtext + "New Project" button
- Button opens `NewProjectModal`

UPDATE `ProjectCard.tsx` (renamed from IdeaCard):
- Show project type badge (Software / Non-Software)
- Update all internal references

UPDATE filters:
- `use-projects-filters.ts`: Same filters but renamed

---

### Story 6.3: Final Cleanup & Orphan Check

**Goal**: Comprehensive sweep to ensure no orphaned code, broken imports, or stale
references remain anywhere in the codebase.

**Scope**:

Run comprehensive searches:
```bash
# Should all return zero (non-comment, non-migration) hits:
grep -r "idea" services/ frontend/src/ --include="*.py" --include="*.ts" --include="*.tsx" -l
grep -r "brainstorm" services/ frontend/src/ --include="*.py" --include="*.ts" --include="*.tsx" -l
grep -r "board_agent\|BoardNode\|board_node\|xyflow\|ReactFlow" services/ frontend/src/ -l
grep -r "merge_synth\|keyword_agent\|deep_comparison\|similarity" services/ frontend/src/ -l
grep -r "brd_draft\|BrdDraft\|brd_version\|BrdVersion" services/ frontend/src/ -l
```

Verify:
- All backend services start without import errors
- Frontend builds without errors (`npm run build`)
- All existing tests pass (minus deleted test files)
- All API endpoints return correct responses
- WebSocket connections work
- Admin panel loads all three context buckets
- PDF generation works for both project types
- Multi-user real-time sync works for requirements panel
- The review workflow still functions end-to-end

Clean up:
- Remove any unused imports
- Remove any commented-out code referencing old features
- Remove any unused translation keys
- Remove any unused CSS classes
- Update any documentation files in `docs/` to reflect new terminology
- Update `docker-compose.yml` if service names changed
- Update `.env.example` if environment variables changed

---

## Execution Order & Dependencies

```
Phase 1 (Remove features — do these first, in order):
  1.1 Remove merge/similarity backend
  1.2 Remove merge/similarity frontend
  1.3 Remove board backend
  1.4 Remove board frontend

Phase 2 (Rename — after Phase 1 is complete):
  2.1 Rename DB & backend models
  2.2 Rename API routes
  2.3 Rename frontend
  2.4 Rename terminology & translations

Phase 3 (Add new features — after Phase 2 is complete):
  3.1 Project type selection (creation flow)
  3.2 Structured requirements data model (backend)
  3.3 Structured requirements panel (frontend)    [depends on 3.2]
  3.4 Admin context buckets per type

Phase 4 (AI rework — after Phase 3 is complete):
  4.1 New facilitator prompt                      [depends on 3.2]
  4.2 New summarizing AI                          [depends on 3.2]
  4.3 AI pipeline update                          [depends on 4.1, 4.2]

Phase 5 (Document & PDF — after Phase 4):
  5.1 New document/structure step frontend        [depends on 3.3, 4.2]
  5.2 PDF generation update                       [depends on 3.2]

Phase 6 (Polish — after everything else):
  6.1 Process stepper & workspace flow            [depends on 5.1]
  6.2 Landing page updates                        [depends on 3.1]
  6.3 Final cleanup & orphan check                [depends on all]
```

Total: 17 user stories across 6 phases.

---

## Notes for Implementors

1. **Migrations**: Each story that touches the database should create proper Django
   migrations. Do NOT modify existing migration files — always create new ones.

2. **Backwards compatibility**: Not required. This is a breaking refactor. There are
   no external API consumers to worry about.

3. **Testing**: Each story should verify that the app still builds and core flows work
   after the changes. Write tests for new features (requirements CRUD, type selection).

4. **Multi-user**: The requirements panel must handle concurrent edits. Use the existing
   WebSocket infrastructure to broadcast changes. Implement optimistic updates with
   server reconciliation.

5. **AI tool calls**: The `update_requirements_structure` tool is critical — it's how
   the AI populates the requirements panel in real-time during chat. Design the mutation
   format carefully (add/update/delete operations with item IDs).

6. **Translation**: Both `en.json` and `de.json` must be updated in every story that
   changes user-facing text. Do not leave English strings in the German file.
