# Project Structure

## Monorepo Strategy

ZiqReq uses a **monorepo** — all services, shared definitions, infrastructure configs, and documentation live in a single repository.

**Rationale:**
- Single product with tightly coupled services
- Shared protobuf definitions for gRPC contracts
- Docker Compose needs all services together for local development
- One team maintains all services
- Simplifies CI/CD pipeline management

---

## Microservice Decomposition

| Service | Framework | Database | Containers | Purpose |
|---------|-----------|----------|-----------|---------|
| **frontend** | React 19 + Vite + TypeScript | — | `frontend` | SPA served as static assets |
| **gateway** | Django 5 + DRF + Channels | Own tables in shared PG | `gateway` | REST API, WebSocket, auth, routing |
| **core** | Django 5 | Own tables in shared PG | `core`, `celery-worker`, `celery-beat` | Domain logic: projects, chat, collaboration, review, admin config |
| **ai** | Django 5 (lightweight) + AI framework (TBD by AI Engineer) | Own tables in shared PG | `ai` | All AI agents, context management, embedding pipeline |
| **notification** | Python | — (stateless consumer) | `notification` | Event consumer → email dispatch + notification creation via gateway gRPC |
| **pdf** | Python + WeasyPrint | — (stateless) | `pdf` | HTML-to-PDF generation. Type-specific rendering: `_render_epic()` (Software projects), `_render_milestone()` (Non-Software projects). |

> **AI service framework:** The AI service's internal framework (Semantic Kernel, LangChain, direct SDK, etc.) is chosen by the AI Engineer in `docs/03-ai/`. The Architect defines the service boundary, database ownership, gRPC interface, and container topology.

### Database Strategy

**Shared PostgreSQL instance, logically separated by service.**

Each Django service has its own set of tables (own Django apps with own migrations). Services primarily access their own tables via their Django models. Cross-service data access happens via gRPC, with limited exceptions documented in `data-model.md` (raw SQL for display name lookups, unmanaged models for shared-DB admin tables).

| Service | Owned Tables |
|---------|-------------|
| gateway | `users`, `notifications`, `monitoring_alert_configs`, `attachments` |
| core | `projects`, `project_collaborators`, `chat_messages`, `ai_reactions`, `user_reactions`, `requirements_document_drafts`, `requirements_document_versions`, `review_assignments`, `review_timeline_entries`, `collaboration_invitations`, `admin_parameters` |
| ai | `chat_context_summaries`, `facilitator_context_bucket`, `context_agent_bucket`, `context_chunks` |

In production (Azure Database for PostgreSQL), all tables live in the same instance. If scaling requires it, services can be split to separate databases later — the gRPC boundary already enforces the separation.

### Django Model Sharing Pattern

**Problem:** Gateway service exposes REST endpoints (via Django REST Framework) for tables owned by Core service. DRF serializers require Django model classes. Gateway and Core are separate Django projects — they cannot import each other's models (microservice code isolation).

**Solution:** Gateway creates **mirror Django models** with identical schemas pointing to Core's tables via the `db_table` Meta attribute.

**Example (M2 implementation):**

```python
# services/core/apps/projects/models.py (Core owns the table)
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=500, default="")
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="open")
    # ... full schema ...

    class Meta:
        db_table = "projects"  # Core creates migrations for this table

# services/gateway/apps/projects/models.py (Gateway mirrors the table)
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=500, default="")
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="open")
    # ... identical schema ...

    class Meta:
        db_table = "projects"  # Points to Core's table. Gateway creates migrations for test DB compatibility.
```

**Rules:**
1. **Core owns migration authority** — only Core creates/modifies migrations for the table schema
2. **Gateway creates migrations for its mirror model** — required for Django test database to create tables. Gateway's migrations define the same schema as Core but with a different app label (e.g., `gateway_projects` vs `core_projects`). Both point to the same physical table via `db_table`.
3. **Schemas must stay synchronized** — if Core changes the schema, Gateway's mirror model AND migrations must be updated manually
4. **Both models access the same physical table** — no data duplication
5. **Gateway uses its mirror for REST API only** — DRF serializers, list queries, CRUD operations
6. **Core uses its model for business logic** — gRPC servicers, Celery tasks, admin operations

**When to use this pattern:**
- Gateway needs to expose REST endpoints for Core-owned data (GET lists, POST creates, etc.)
- The endpoint requires DRF serializers (which need Django models)
- gRPC overhead would be excessive for simple CRUD (e.g., paginated list queries with filters)

**When NOT to use this pattern:**
- Complex business logic (use gRPC to Core service instead)
- Cross-service transactions (use gRPC + distributed transaction patterns)
- Gateway-owned tables (no mirroring needed — Gateway owns both model and migration)

**Tables with mirror models (as of M22):**
- `projects` (Core-owned, Gateway mirrors for `/api/projects` endpoints)
- `project_collaborators` (Core-owned, Gateway mirrors for join queries in project lists)
- `chat_messages` (Core-owned, Gateway mirrors for `/api/projects/:id/chat` endpoints)
- `collaboration_invitations` (Core-owned, Gateway mirrors for `/api/invitations` endpoints)
- `attachments` (Gateway-owned managed model, Core has unmanaged mirror for AI service gRPC access)

**Note:** `attachments` table follows the reverse pattern — Gateway owns the managed model (creates migrations), Core has an unmanaged mirror for AI service to access attachment metadata via direct SQL (same cross-service raw SQL pattern used for `users` table lookups).

**Note on `managed=False` pattern:** The `managed=False` Meta option is used for read-only mirror models where Gateway never runs tests against the table (e.g., `admin_parameters` in Gateway's admin app). For REST API mirror models where Gateway test suites query/mutate the table, migrations are required for Django test database creation.

**Module mirroring for test discoverability (as of M15):** Some Core service modules are mirrored into Gateway for test discoverability when namespace conflicts exist. For example, `apps.monitoring` exists in both Core and Gateway. Core owns the business logic (`health_checks.py`, `tasks.py`), but these files are mirrored into Gateway's `apps.monitoring/` directory so Gateway's test runner can discover and test them. This pattern is used sparingly when PYTHONPATH resolution would otherwise break test imports.

### Migration Patterns for Mirror Models

> ⚙️ Technical patterns discovered during M19 implementation for Gateway mirror models that point to tables owned by other services.

**When Gateway mirrors tables from Core or AI services:**

Gateway mirror models use `managed = False` in their Meta class to indicate that Django should not attempt to create/alter/drop these tables. However, test environments require special handling.

**Migration pattern for `managed=False` mirror models (M19+):**

```python
# services/gateway/apps/projects/migrations/0004_requirements_documents.py
from django.db import migrations

def create_requirements_tables(apps, schema_editor):
    """Create requirements tables if they don't exist (for test environments)."""
    with schema_editor.connection.cursor() as cursor:
        # Check if table exists first (Core service may have already created it)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'requirements_document_drafts'
            )
        """)
        if not cursor.fetchone()[0]:
            # Table doesn't exist — create it for test environment
            cursor.execute("""
                CREATE TABLE requirements_document_drafts (
                    id UUID PRIMARY KEY,
                    project_id UUID UNIQUE NOT NULL,
                    title TEXT,
                    structure JSONB NOT NULL DEFAULT '[]'::jsonb,
                    ...
                )
            """)

class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0003_project_type'),
    ]

    operations = [
        migrations.RunPython(
            create_requirements_tables,
            reverse_code=migrations.RunPython.noop
        ),
    ]
```

**Key rules:**

1. **Use RunPython, not RunSQL** — PostgreSQL doesn't support multi-statement strings in RunSQL for complex DDL.
2. **Check table existence via `information_schema.tables`** — Core/AI services may have already created the table in shared DB.
3. **Use `CREATE TABLE IF NOT EXISTS` where possible** — simpler than checking existence first.
4. **Avoid `ADD CONSTRAINT IF NOT EXISTS`** — PostgreSQL doesn't support this. Check table existence and skip entire DDL block if table exists.
5. **Handle ForeignKey references to Core tables** — Gateway mirror models can reference other Gateway mirror models as FKs in Django ORM, but the underlying SQL must reference the actual shared table name.

**Why this pattern is needed:**

- Gateway test container's PYTHONPATH resolves `apps.projects.models` to Gateway namespace (Gateway comes first in sys.path)
- AI service apps (`apps.context`, `apps.embedding`) are not importable from Gateway test environment
- `--reuse-db` pytest option means migrations must be idempotent (safe to run multiple times)
- Core service creates the table in production, but Gateway tests run in isolated test DB where Core migrations may not have run

**Tables using this pattern (as of M19):**
- `requirements_document_drafts` (Core-owned, Gateway mirrors)
- `requirements_document_versions` (Core-owned, Gateway mirrors)
- `facilitator_context_bucket` (AI-owned, Gateway mirrors for admin endpoints)
- `context_chunks` (AI-owned, Gateway mirrors for admin endpoints)

### Communication Patterns

```
┌──────────┐  REST + WS   ┌─────────┐  gRPC  ┌──────┐
│ Frontend │ ────────────► │ Gateway │ ──────► │ Core │
└──────────┘              │         │ ──────► │  AI  │
                          │         │ ──────► │ PDF  │
                          └────┬────┘        └──────┘
                               │
                          ┌────▼────────────┐
                          │ Message Broker   │
                          │ (RabbitMQ / ASB) │
                          └────┬───┬───┬────┘
                               │   │   │
                    ┌──────────┘   │   └──────────┐
                    ▼              ▼               ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │   AI     │  │ Notif.   │  │  Core    │
              │ Service  │  │ Service  │  │ (Worker) │
              └──────────┘  └──────────┘  └──────────┘
```

| Pattern | Used For | Direction |
|---------|----------|-----------|
| **REST** | Frontend → Gateway queries and mutations | Synchronous |
| **WebSocket** | Gateway → Frontend real-time broadcasts | Bidirectional |
| **gRPC** | Gateway → Internal services (request/response) | Synchronous |
| **Message Broker** | Service → Service async events (AI triggers, notifications, monitoring) | Asynchronous |

### Storage Backend Abstraction (M22)

> ⚙️ Attachment file storage pattern introduced in M22.

**Module location:** `services/gateway/storage/` (not inside a Django app)

Gateway service owns a storage abstraction layer for file attachments (images, PDFs). The abstraction allows switching between MinIO (dev) and Azure Blob Storage (prod) without code changes.

**Architecture:**

```python
# services/gateway/storage/backends.py
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """Abstract base class for file storage backends."""

    @abstractmethod
    def upload_file(self, file_obj, storage_key: str) -> None:
        """Upload a file to storage."""
        pass

    @abstractmethod
    def delete_file(self, storage_key: str) -> None:
        """Delete a file from storage (best-effort)."""
        pass

    @abstractmethod
    def get_presigned_url(self, storage_key: str, filename: str, ttl_seconds: int) -> str:
        """Generate a presigned download URL."""
        pass

    @abstractmethod
    def file_exists(self, storage_key: str) -> bool:
        """Check if a file exists in storage."""
        pass

class MinIOBackend(StorageBackend):
    """MinIO implementation for development."""
    # Uses minio Python SDK, singleton pattern via get_storage_backend()

class AzureBlobBackend(StorageBackend):
    """Azure Blob Storage implementation for production."""
    # Raises NotImplementedError — production deployment concern
```

**Factory pattern:**

```python
# services/gateway/storage/factory.py
_backend = None  # Singleton

def get_storage_backend() -> StorageBackend:
    """Get the configured storage backend (singleton)."""
    global _backend
    if _backend is None:
        backend_type = os.getenv("STORAGE_BACKEND", "minio")
        if backend_type == "minio":
            _backend = MinIOBackend(...)
        elif backend_type == "azure_blob":
            _backend = AzureBlobBackend(...)
    return _backend

def reset_storage_backend() -> None:
    """Reset singleton (test teardown only)."""
    global _backend
    _backend = None
```

**Bucket initialization:**

MinIO bucket auto-creation happens in `services/gateway/apps/projects/apps.py` (`ProjectsConfig.ready()`). Guarded with try/except to not break startup if MinIO is unreachable.

**AI service file download:**

AI service does NOT use Gateway's storage abstraction. It accesses MinIO directly via `minio` client for file downloads during extraction tasks. This avoids circular gRPC dependencies (AI → Gateway → back to storage).

**Key files:**

- `services/gateway/storage/__init__.py` — Package init
- `services/gateway/storage/backends.py` — ABC + MinIOBackend + AzureBlobBackend
- `services/gateway/storage/factory.py` — Singleton factory
- `services/gateway/storage/tests/test_backends.py` — Backend unit tests

**Usage in Gateway views:**

```python
from storage.factory import get_storage_backend

def upload_attachment(request, project_id):
    backend = get_storage_backend()
    backend.upload_file(file_obj, storage_key)
    # ...
```

**Test pattern:**

Mock `_get_storage_backend()` wrapper (not direct import) to return `MagicMock()` for storage operations.

**Notes:**

- Presigned URLs include `response-content-disposition=attachment` parameter for forced download (security requirement).
- Storage deletion is best-effort: logged on failure, doesn't block the DELETE endpoint.
- Storage keys use format: `attachments/{project_id}/{uuid}.{ext}`

### Event Publisher Import Pattern (CRITICAL)

**Problem:** Gateway views publish notification events via `services/gateway/events/publisher.py`. Some tests (e.g., `test_ai_consumer.py`) manipulate `sys.modules` for the `events` package at pytest collection time, causing top-level imports to fail.

**Solution:** Views that publish events MUST use **lazy imports** (import inside function body, not module-level).

**Example:**

```python
# ❌ BROKEN — top-level import breaks test collection
from events.publisher import publish_notification_event

@api_view(["POST"])
def invite_collaborator(request, project_id):
    # ... logic ...
    publish_notification_event(user_id=invitee_id, ...)
```

```python
# ✅ CORRECT — lazy import inside helper function
def _publish_notification(**kwargs):
    from events.publisher import publish_notification_event
    publish_notification_event(**kwargs)

@api_view(["POST"])
def invite_collaborator(request, project_id):
    # ... logic ...
    _publish_notification(user_id=invitee_id, ...)
```

**Affected modules:** `services/gateway/apps/collaboration/views.py`, `services/gateway/apps/review/views.py`, `services/gateway/apps/chat/views.py`, `services/gateway/events/consumers.py` (AI delegation event).

### Celery Worker Deployment

The Celery worker and beat scheduler run the **core service codebase** as separate containers:
- `celery-worker`: processes background tasks from the broker
- `celery-beat`: schedules periodic tasks (soft delete cleanup, health checks). Beat schedule is configured in `services/core/core/settings/base.py` via `CELERY_BEAT_SCHEDULE` dict.

Both import and use the core service's Django models and database directly. This is the standard Celery deployment pattern.

---

## Directory Layout

```
ziqreq/
│
├── frontend/                              # React SPA
│   ├── public/                            # Static assets (favicon, logos, fonts)
│   ├── src/
│   │   ├── app/                           # App shell, router, providers
│   │   │   ├── router.tsx                 # React Router route definitions (layout route pattern with AuthenticatedLayout)
│   │   │   ├── providers.tsx              # Context providers (Redux, Query, MSAL, i18n, ToastProvider)
│   │   │   ├── globals.css                # Tailwind CSS 4 @theme config, CSS custom properties (light/dark), @font-face
│   │   │   └── app.tsx                    # Root component
│   │   │
│   │   ├── pages/                         # Page-level components (one per route)
│   │   │   ├── landing-page.tsx          # Re-export from LandingPage/
│   │   │   ├── LandingPage/             # Landing page (co-located sub-components)
│   │   │   │   ├── index.tsx            # Main LandingPage component
│   │   │   │   ├── HeroSection.tsx
│   │   │   │   ├── ProjectList.tsx      # MyProjectsSection, CollaboratingSection, InvitationsSection, TrashSection
│   │   │   │   └── FilterBar.tsx        # Search + state/ownership filter dropdowns
│   │   │   ├── project-workspace.tsx     # Re-export from ProjectWorkspace/
│   │   │   ├── ProjectWorkspace/        # Workspace (co-located sub-components)
│   │   │   │   ├── index.tsx            # Main ProjectWorkspace component
│   │   │   │   ├── WorkspaceHeader.tsx  # Sticky header with inline title editing, agent mode
│   │   │   │   ├── PanelDivider.tsx     # Draggable divider with localStorage persistence
│   │   │   │   ├── StructureStepView.tsx  # Structure step (replaces DocumentView) — 60/40 split: RequirementsPanel + PDFPreviewPanel
│   │   │   │   └── RequirementsSection.tsx  # Two-panel layout (chat + requirements panel/review tabs)
│   │   │   ├── review-page.tsx
│   │   │   ├── admin-panel.tsx
│   │   │   └── login-page.tsx
│   │   │
│   │   ├── components/                    # UI components
│   │   │   ├── ui/                        # shadcn/ui primitives (button, dialog, dropdown, etc.)
│   │   │   ├── layout/                    # Navbar, PageShell, UserDropdown, AuthenticatedLayout, ConnectionIndicator, NotificationBell, ProjectsListFloating, HamburgerMenu
│   │   │   ├── shared/                    # Shared cross-page components
│   │   │   │   └── ProjectCard/          # ProjectCard component (used by LandingPage and others)
│   │   │   ├── chat/                      # ChatPanel, ChatMessage, ChatInput, MentionDropdown, TypingIndicator
│   │   │   ├── requirements/              # RequirementsPanel, RequirementCard, HierarchyTree, SortableList
│   │   │   ├── workspace/                 # ProcessStepper, PDFPreviewPanel, WorkspaceHeader, LockOverlay, InvitationBanner, ReadOnlyBanner
│   │   │   ├── requirements_document/     # DocumentEditor, SectionEditor, ReadinessIndicator, PdfPreview
│   │   │   ├── brd/                       # ORPHAN: ReviewTab.tsx, BRDSectionEditor.tsx — test-only imports (old BRD flow, replaced by StructureStepView)
│   │   │   ├── review/                    # ReviewTimeline, TimelineEntry, ReviewActions
│   │   │   ├── collaboration/             # InviteDialog, CollaboratorList, PresenceIndicators
│   │   │   ├── notification/              # NotificationList, NotificationItem
│   │   │   ├── admin/                     # AiContextEditor, ContextAgentBucketEditor, ParametersTable, MonitoringDashboard, KpiCard, ServiceHealthTable, UserSearch, UserCard, AlertRecipientChips
│   │   │   └── common/                    # ErrorBoundary, LoadingSpinner, OfflineBanner, EmptyState
│   │   │
│   │   ├── features/                      # Feature-level business logic (hooks, API calls, state)
│   │   │   ├── auth/                      # useAuth, MsalProvider config, DevUserSwitcher, route guards
│   │   │   ├── projects/                  # useProjects, useProject, useCreateProject, project API hooks
│   │   │   ├── chat/                      # useChat, useSendMessage, useChatScroll, chat API hooks
│   │   │   ├── requirements/              # useRequirements, useRequirementsStructure, requirements API hooks
│   │   │   ├── requirements_document/     # useDocument, useDocumentGenerate, useDocumentSections, document API hooks
│   │   │   ├── review/                    # useReview, useTimeline, useReviewActions, review API hooks
│   │   │   ├── collaboration/             # useCollaboration, useInvitations, collaboration API hooks
│   │   │   ├── notifications/             # useNotifications, useUnreadCount, notification API hooks
│   │   │   ├── admin/                     # useAdminParams, useAiContext, useMonitoring, admin API hooks
│   │   │   ├── presence/                  # usePresence, useIdleDetection, presence state
│   │   │   └── websocket/                 # useWebSocket, WebSocket client singleton, reconnection logic
│   │   │
│   │   ├── hooks/                         # App-wide React hooks (cross-cutting, not feature-specific)
│   │   │   └── use-theme.ts              # Theme switcher hook (localStorage, prefers-color-scheme)
│   │   │
│   │   ├── store/                         # Redux Toolkit store
│   │   │   ├── index.ts                   # Store configuration
│   │   │   ├── requirements-slice.ts      # Requirements panel state, selection
│   │   │   ├── websocket-slice.ts         # Connection state, reconnection
│   │   │   ├── presence-slice.ts          # Online/idle/offline users
│   │   │   ├── ui-slice.ts               # Layout state (divider, panels, tabs)
│   │   │   └── rate-limit-slice.ts        # Chat lockout state
│   │   │
│   │   ├── lib/                           # Shared utilities
│   │   │   ├── api-client.ts              # Fetch wrapper, auth header injection, error handling
│   │   │   ├── ws-client.ts               # WebSocket connection manager, message parsing
│   │   │   ├── utils.ts                   # General utilities (formatDate, debounce, etc.)
│   │   │   └── constants.ts               # App-wide constants
│   │   │
│   │   ├── types/                         # Shared TypeScript types
│   │   │   ├── api.ts                     # API request/response types
│   │   │   ├── websocket.ts               # WebSocket event types
│   │   │   ├── models.ts                  # Domain model types (Project, ChatMessage, Requirement, etc.)
│   │   │   └── index.ts                   # Re-exports
│   │   │
│   │   ├── i18n/                          # Internationalization
│   │   │   ├── config.ts                  # i18next configuration
│   │   │   └── locales/                   # Translation files
│   │   │       ├── de.json                # German translations
│   │   │       └── en.json                # English translations
│   │   │
│   │   ├── config/                        # Environment and app config
│   │   │   └── env.ts                     # Environment variable access
│   │   │
│   │   └── test-setup.ts                  # Vitest setup: matchMedia polyfill, @testing-library/jest-dom/vitest
│   │
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── .prettierrc
│   ├── package.json
│   └── Dockerfile                         # Production: build + Nginx serve
│
├── services/
│   │
│   ├── gateway/                           # API Gateway (Django + DRF + Channels)
│   │   ├── gateway/                       # Django project settings
│   │   │   ├── __init__.py
│   │   │   ├── settings/
│   │   │   │   ├── base.py               # Shared settings
│   │   │   │   ├── development.py        # Dev overrides (DEBUG, auth bypass)
│   │   │   │   ├── production.py         # Prod overrides (Azure config)
│   │   │   │   └── test.py              # Test settings (SQLite in-memory, patched ArrayField)
│   │   │   ├── urls.py                    # URL routing
│   │   │   ├── asgi.py                    # ASGI entry point (Channels)
│   │   │   └── wsgi.py                    # WSGI entry point (DRF)
│   │   ├── apps/
│   │   │   ├── authentication/            # Token validation, user sync, dev bypass
│   │   │   │   ├── models.py             # User model (shadow table)
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── urls.py
│   │   │   │   ├── middleware.py          # Auth middleware (token validation)
│   │   │   │   └── tests/
│   │   │   ├── notifications/             # Notification storage and API
│   │   │   │   ├── models.py             # Notification model
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── urls.py
│   │   │   │   └── tests/
│   │   │   ├── monitoring/                # Monitoring dashboard and alert configuration
│   │   │   │   ├── models.py             # MonitoringAlertConfig model
│   │   │   │   ├── views.py              # monitoring_dashboard, alert_config endpoints
│   │   │   │   ├── urls.py
│   │   │   │   └── tests/
│   │   │   ├── admin_config/             # Admin parameter management and user search
│   │   │   │   ├── models.py             # AdminParameter unmanaged mirror model (managed=False, reads Core's table)
│   │   │   │   ├── views.py              # parameter_list, parameter_update, user_search
│   │   │   │   ├── urls.py               # Parameter URL routing
│   │   │   │   ├── user_urls.py          # User search URL routing
│   │   │   │   └── __init__.py
│   │   │   ├── projects/                  # Projects REST endpoints (CRUD, list, restore)
│   │   │   │   ├── views.py              # REST endpoint handlers
│   │   │   │   ├── serializers.py        # CreateProjectSerializer, UpdateProjectSerializer
│   │   │   │   ├── authentication.py     # MiddlewareAuthentication (bridges Django middleware auth → DRF)
│   │   │   │   ├── urls.py               # URL routing (api/projects/)
│   │   │   │   ├── apps.py              # ProjectsConfig (label: gateway_projects)
│   │   │   │   ├── _document_check.py   # Stub for has_been_submitted (real impl in M7)
│   │   │   │   └── __init__.py
│   │   │   ├── chat/                      # Chat REST endpoints (messages, reactions)
│   │   │   │   ├── views.py              # chat_list_create, reaction_view
│   │   │   │   ├── serializers.py        # SendChatSerializer, AddReactionSerializer
│   │   │   │   ├── urls.py               # URL routing (api/projects/:id/chat/)
│   │   │   │   ├── apps.py              # ChatConfig
│   │   │   │   └── __init__.py
│   │   │   ├── collaboration/              # Collaboration REST endpoints (invite, manage, share)
│   │   │   │   ├── views.py              # Invite, list collaborators, transfer, leave, share link
│   │   │   │   ├── serializers.py        # InviteSerializer, TransferOwnershipSerializer
│   │   │   │   ├── urls.py               # URL routing (api/projects/:id/collaborators/, api/invitations/)
│   │   │   │   ├── apps.py              # CollaborationConfig
│   │   │   │   └── __init__.py
│   │   │   ├── requirements_document/     # Requirements Document REST endpoints (draft, versions, PDF, AI generation)
│   │   │   │   ├── views.py              # Draft CRUD, generate skeleton, regenerate, regenerate-section, generate-pdf, versions
│   │   │   │   ├── serializers.py        # UpdateDocumentSerializer
│   │   │   │   ├── urls.py               # URL routing (api/projects/:id/requirements-document/)
│   │   │   │   ├── apps.py              # RequirementsDocumentConfig
│   │   │   │   └── __init__.py
│   │   │   ├── admin_ai_context/          # Admin AI context bucket management
│   │   │   │   ├── views.py              # Facilitator + Context Agent bucket GET/PUT endpoints
│   │   │   │   ├── urls.py               # URL routing (api/admin/ai-context/)
│   │   │   │   └── __init__.py
│   │   │   ├── review/                    # Review REST endpoints (list, assign, actions, timeline)
│   │   │   │   ├── views.py              # REST endpoint handlers
│   │   │   │   ├── serializers.py        # Review serializers
│   │   │   │   ├── urls.py               # URL routing (api/reviews/, api/projects/:id/review/)
│   │   │   │   ├── action_urls.py        # Review action URL routing (accept, reject, drop, undo)
│   │   │   │   ├── apps.py              # ReviewConfig
│   │   │   │   └── __init__.py
│   │   │   └── websocket/                 # Channels consumers and routing
│   │   │       ├── consumers.py           # WebSocket consumer (subscribe, presence, events)
│   │   │       ├── routing.py             # Channels URL routing
│   │   │       ├── middleware.py           # WebSocket auth middleware
│   │   │       └── tests/
│   │   ├── grpc_clients/                  # gRPC stubs for calling internal services
│   │   │   ├── core_client.py
│   │   │   ├── ai_client.py
│   │   │   ├── pdf_client.py
│   │   │   ├── enrichment.py              # User display name enrichment (bulk UUID → name resolution)
│   │   │   └── __init__.py
│   │   ├── grpc_server/                   # gRPC server for notification service callbacks (port 50054)
│   │   │   ├── server.py                  # gRPC server entrypoint (requires django.setup())
│   │   │   └── servicers/
│   │   │       └── gateway_servicer.py    # GetAlertRecipients, CreateNotification, GetUserPreferences
│   │   ├── events/                         # RabbitMQ event integration (publish + consume)
│   │   │   ├── publisher.py               # Shared RabbitMQ publisher utility (publish_notification_event) — MUST use lazy imports in views
│   │   │   ├── consumers.py               # BaseEventConsumer, ChatEventConsumer, AiEventConsumer
│   │   │   ├── requirements_document_consumer.py  # RequirementsDocumentEventConsumer (document.*, ai.document.generation_complete, ai.processing.failed → WS)
│   │   │   └── review_consumer.py         # ReviewEventConsumer (review state changes → WS)
│   │   ├── middleware/                     # Shared middleware
│   │   │   ├── error_handling.py          # Consistent error response formatting
│   │   │   ├── share_link.py             # Share link token validation (?share=<token> → read-only access)
│   │   │   └── logging.py
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── core/                              # Core Domain Service (Django)
│   │   ├── core/                          # Django project settings
│   │   │   ├── __init__.py
│   │   │   ├── settings/
│   │   │   │   ├── base.py
│   │   │   │   ├── development.py
│   │   │   │   ├── production.py
│   │   │   │   └── test.py              # Test settings (SQLite in-memory, patched ArrayField)
│   │   │   ├── celery.py                  # Celery app configuration
│   │   │   └── urls.py                    # (minimal — gRPC is primary interface)
│   │   ├── apps/
│   │   │   ├── projects/                  # Project CRUD, state machine
│   │   │   │   ├── models.py             # Project, ProjectCollaborator
│   │   │   │   ├── services.py           # Business logic (state transitions, validation)
│   │   │   │   ├── tasks.py              # Celery tasks (soft delete cleanup)
│   │   │   │   └── tests/
│   │   │   ├── chat/                      # Chat messages, reactions
│   │   │   │   ├── models.py             # ChatMessage, AiReaction, UserReaction
│   │   │   │   ├── services.py
│   │   │   │   └── tests/
│   │   │   ├── requirements_document/     # Requirements document drafts, versions, submit flow
│   │   │   │   ├── models.py             # RequirementsDocumentDraft, RequirementsDocumentVersion
│   │   │   │   ├── services.py           # Document CRUD, versioning, submit_for_review (state transition + version creation)
│   │   │   │   └── tests/
│   │   │   ├── review/                    # Review workflow
│   │   │   │   ├── models.py             # ReviewAssignment, ReviewTimelineEntry
│   │   │   │   ├── services.py           # State transitions, timeline management
│   │   │   │   └── tests/
│   │   │   ├── collaboration/             # Invitations, collaborator management
│   │   │   │   ├── models.py             # CollaborationInvitation
│   │   │   │   ├── services.py
│   │   │   │   └── tests/
│   │   │   └── admin_config/              # Runtime parameters + monitoring
│   │   │       ├── models.py             # AdminParameter (with data_type, category)
│   │   │       ├── services.py           # Parameter access, caching
│   │   │       ├── tasks.py              # Celery tasks (health checks)
│   │   │       └── tests/
│   │   ├── grpc_server/                   # gRPC service implementation
│   │   │   ├── servicers/                 # gRPC servicer classes
│   │   │   │   └── core_servicer.py      # Single servicer with all RPC methods (projects, chat, requirements_document, review, collaboration, admin)
│   │   │   ├── tests/
│   │   │   │   └── test_core_grpc.py     # gRPC integration tests
│   │   │   └── server.py                  # gRPC server setup
│   │   ├── events/                        # Message broker event publishing
│   │   │   ├── broker.py                  # Exchange/queue/DLQ topology setup
│   │   │   ├── publisher.py               # EventPublisher with DLQ pairs, delivery confirmation, auto-reconnect
│   │   │   └── consumers.py               # Consume events from other services
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── ai/                                # AI Service
│   │   │
│   │   │  # ──────────────────────────────────────────────────────────────────
│   │   │  # BOUNDARY NOTE: The directory structure below is a scaffold.
│   │   │  # The AI Engineer defines the internal organization of the AI
│   │   │  # service in docs/03-ai/. The Architect defines the external
│   │   │  # boundary: Django settings, gRPC interface, database models,
│   │   │  # message broker integration, and container configuration.
│   │   │  # ──────────────────────────────────────────────────────────────────
│   │   │
│   │   ├── ai_service/                    # Django project settings (lightweight — no DRF, no views)
│   │   │   ├── __init__.py
│   │   │   ├── settings/
│   │   │   │   ├── base.py               # Minimal Django settings (DB, installed apps, pgvector)
│   │   │   │   ├── development.py
│   │   │   │   ├── production.py
│   │   │   │   └── test.py              # Test settings (SQLite in-memory, patched VectorField/HnswIndex)
│   │   │   └── wsgi.py                    # Not used — gRPC is the interface, but Django needs it
│   │   ├── apps/                          # Django apps for AI-owned database tables
│   │   │   ├── context/                   # Context management tables
│   │   │   │   ├── models.py             # ChatContextSummary, FacilitatorContextBucket, ContextAgentBucket
│   │   │   │   └── migrations/
│   │   │   └── embedding/                 # Embedding tables
│   │   │       ├── models.py             # ContextChunk
│   │   │       └── migrations/
│   │   ├── agents/                        # AI agent implementations
│   │   │   ├── base.py                   # BaseAgent with invoke(), mock mode, retry logic
│   │   │   ├── facilitator/              # Facilitator agent (requirements structuring tools)
│   │   │   │   ├── agent.py
│   │   │   │   ├── plugins.py
│   │   │   │   └── prompt.py
│   │   │   ├── context_compression/      # Context Compression agent (cheap tier, single-shot)
│   │   │   │   ├── agent.py
│   │   │   │   └── prompt.py
│   │   │   ├── context_agent/            # Context Agent (RAG-powered company knowledge retrieval)
│   │   │   │   ├── agent.py
│   │   │   │   └── prompt.py
│   │   │   ├── context_extension/        # Context Extension agent (escalated tier, full history search)
│   │   │   │   ├── agent.py
│   │   │   │   └── prompt.py
│   │   │   └── summarizing_ai/           # Summarizing AI agent (requirements document generation, 3 modes)
│   │   │       ├── agent.py
│   │   │       └── prompt.py
│   │   ├── kernel/                        # Semantic Kernel setup
│   │   │   ├── sk_factory.py             # SK kernel construction
│   │   │   ├── model_router.py           # Model tier routing (default/cheap/escalated)
│   │   │   └── token_tracker.py          # Token usage tracking
│   │   ├── processing/                    # Chat + Requirements Document processing pipelines
│   │   │   ├── pipeline.py               # ChatProcessingPipeline (7-step) + DocumentGenerationPipeline (4-step)
│   │   │   ├── context_assembler.py      # Context window assembly from gRPC data (chat + document contexts)
│   │   │   ├── fabrication_validator.py  # Fabrication detection (keyword traceability, proper nouns, length)
│   │   │   └── debouncer.py              # Per-project debounce with version counters
│   │   ├── embedding/                      # RAG pipeline utilities
│   │   │   ├── chunker.py                # Section-aware + free text chunking (~500 tokens, 50-token overlap)
│   │   │   ├── embedder.py               # Azure OpenAI text-embedding-3-small wrapper
│   │   │   ├── reindexer.py              # Full re-index (delete + bulk create) on bucket update
│   │   │   └── retriever.py              # pgvector cosine similarity search (sync + async)
│   │   ├── fixtures/                      # AI mock mode fixtures (AI_MOCK_MODE=true)
│   │   │   ├── facilitator_response.json
│   │   │   ├── context_compression_response.json
│   │   │   ├── context_agent_response.json
│   │   │   ├── context_extension_response.json
│   │   │   └── summarizing_ai_response.json
│   │   ├── grpc_server/                   # gRPC service implementation
│   │   │   ├── servicers/
│   │   │   │   ├── processing_servicer.py # Trigger AI processing
│   │   │   │   └── context_servicer.py    # Context bucket management
│   │   │   └── server.py
│   │   ├── grpc_clients/                  # gRPC stubs for calling core service
│   │   │   └── core_client.py
│   │   ├── events/                        # Message broker integration
│   │   │   ├── consumers.py               # Consume processing requests
│   │   │   └── publishers.py              # Publish processing results
│   │   ├── manage.py                      # Django management (migrations only — gRPC is the runtime interface)
│   │   ├── main.py                        # Service entry point (starts gRPC server + event consumers with Django ORM initialized)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── notification/                      # Notification Service (Python)
│   │   ├── consumers/                     # Message broker event consumers
│   │   │   ├── base.py                    # Shared notify_user helper with email preference checking
│   │   │   ├── review_events.py           # Review state changes → notifications (review.accepted/rejected/dropped)
│   │   │   ├── collaboration_events.py    # Invitations, joins, leaves → notifications
│   │   │   ├── ai_events.py              # AI processing failed → notifications
│   │   │   └── monitoring_events.py      # Health alerts → email
│   │   ├── email/                         # Email dispatch (Jinja2 templates, bilingual de/en)
│   │   │   ├── sender.py                 # Email sending logic with rate limiting (3/user/5min)
│   │   │   ├── templates/                # Email templates (HTML + plain text)
│   │   │   │   ├── de/                   # German email templates (7 types)
│   │   │   │   └── en/                   # English email templates (7 types)
│   │   │   └── renderer.py              # Jinja2 template rendering (autoescape=True)
│   │   ├── grpc_clients/                 # gRPC stubs
│   │   │   ├── gateway_client.py         # Create notifications + read user preferences (users table owned by gateway)
│   │   │   └── core_client.py            # Read project details, reviewer assignments
│   │   ├── main.py                       # Service entry point
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── pdf/                              # PDF Service (Python + WeasyPrint)
│       ├── generator/                    # PDF generation logic
│       │   ├── renderer.py               # HTML-to-PDF rendering
│       │   └── builder.py                # Requirements document HTML assembly from sections
│       ├── templates/                    # HTML templates for PDF layout
│       │   ├── requirements_document.html  # Requirements document PDF template
│       │   └── requirements_styles.css   # PDF styling (Gotham font, Commerz Real branding)
│       ├── grpc_server/                  # gRPC service
│       │   ├── servicers/
│       │   │   └── pdf_servicer.py
│       │   └── server.py
│       ├── main.py                       # Service entry point
│       ├── requirements.txt
│       └── Dockerfile
│
├── proto/                                # Shared protobuf definitions
│   ├── common.proto                      # Shared types (User, Pagination, Error)
│   ├── core.proto                        # Core service gRPC definitions
│   ├── ai.proto                          # AI service gRPC definitions
│   ├── gateway.proto                     # Gateway gRPC definitions (for notification service callbacks)
│   ├── pdf.proto                         # PDF service gRPC definitions
│   └── Makefile                          # Proto compilation targets
│
├── infra/                                # Infrastructure configuration
│   ├── docker/
│   │   ├── docker-compose.yml            # Full local dev environment
│   │   ├── docker-compose.override.yml   # Developer-specific overrides (optional, not in repo)
│   │   └── nginx/
│   │       └── nginx.conf                # Reverse proxy config (dev)
│   └── azure/                            # Azure deployment configs (Container Apps)
│       └── (deployment manifests)
│
├── scripts/                              # Development scripts
│   ├── seed-db.py                        # Seed database with dev data
│   ├── generate-proto.sh                 # Compile .proto files to Python/TypeScript stubs
│   ├── run-tests.sh                      # Sequential test runner for all services + frontend
│   └── dev-setup.sh                      # One-command dev environment setup
│
├── docs/                                 # Pipeline documentation
│   ├── 01-requirements/
│   ├── 02-architecture/
│   ├── 03-design/
│   ├── 03-ai/
│   ├── 03-integration/
│   └── 04-milestones/
│
├── conftest.py                           # Root pytest config: collect_ignore_glob for cross-service isolation, sys.path setup
├── pyproject.toml                        # Root pytest config: DJANGO_SETTINGS_MODULE, pythonpath for all service dirs
├── .gitignore
├── .editorconfig
└── README.md
```

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| **Files (frontend components)** | kebab-case | `chat-message.tsx`, `requirements-panel.tsx` |
| **Files (frontend features/hooks)** | kebab-case | `use-chat.ts`, `use-requirements.ts` |
| **Files (Python modules)** | snake_case | `project_servicer.py`, `facilitator_agent.py` |
| **React components** | PascalCase | `ChatMessage`, `RequirementsPanel` |
| **React hooks** | camelCase with `use` prefix | `useChat`, `useRequirements` |
| **TypeScript functions** | camelCase | `formatDate`, `parseReaction` |
| **TypeScript types/interfaces** | PascalCase | `ChatMessage`, `BoardNode`, `ApiError` |
| **TypeScript constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `WS_RECONNECT_INTERVAL` |
| **Python classes** | PascalCase | `ProjectService`, `FacilitatorAgent` |
| **Python functions/methods** | snake_case | `get_project_state`, `process_chat_message` |
| **Python constants** | UPPER_SNAKE_CASE | `MAX_KEYWORDS`, `DEFAULT_DEBOUNCE` |
| **Django models** | PascalCase (singular) | `Project`, `ChatMessage`, `Requirement` |
| **Database tables** | snake_case (plural by Django convention) | `projects`, `chat_messages`, `requirements` |
| **API routes** | kebab-case | `/api/projects/:id/requirements-document` |
| **gRPC services** | PascalCase | `CoreService`, `AiService` |
| **gRPC methods** | PascalCase | `GetIdeaState`, `ProcessChatMessage` |
| **Proto files** | snake_case | `core.proto`, `common.proto` |
| **Proto messages** | PascalCase | `ProjectState`, `ChatMessageRequest` |
| **Environment variables** | UPPER_SNAKE_CASE | `DATABASE_URL`, `AZURE_OPENAI_ENDPOINT` |
| **Docker service names** | kebab-case | `api-gateway`, `celery-worker` |
| **CSS classes** | Tailwind utilities | `flex items-center gap-2` |
| **Redux slices** | kebab-case file, camelCase slice name | `requirements-slice.ts`, `requirementsSlice` |
| **Redux actions** | camelCase | `setSelection`, `pushUndoAction` |
| **i18n keys** | dot-separated namespace, camelCase segments | `chat.sendButton`, `review.acceptAction` |
| **Test files** | `test_` prefix (Python), `.test.` infix (TypeScript) | `test_idea_service.py`, `chat-message.test.tsx` |

---

## Architectural Patterns

### Frontend

#### Component Pattern
- **Pages** (`pages/`): Route-level components. Compose feature components. Minimal logic.
- **Feature components** (`components/<feature>/`): Domain-specific UI. May use feature hooks.
- **UI primitives** (`components/ui/`): shadcn/ui components. No business logic. Reusable.
- **Common** (`components/common/`): Shared non-primitive components (error boundary, loading states).

#### Data Flow Pattern
```
Page
├── useFeatureHook (features/<domain>/)     ← business logic, API calls
│   ├── TanStack Query hook                 ← server state (REST API)
│   ├── Redux selector                      ← client state (local)
│   └── WebSocket subscription              ← real-time events
└── FeatureComponent (components/<domain>/) ← renders data
```

- **Server state** (projects, chat, requirements documents, reviews): TanStack Query. Cache invalidated by WebSocket events.
- **Client state** (undo/redo, selections, connection, UI layout): Redux Toolkit slices.
- **Ephemeral state** (form input, hover): Component-local `useState`.

#### WebSocket Pattern
- Single `WebSocketClient` class (`lib/ws-client.ts`) manages the session-level connection.
- On connect: authenticate via token in query parameter.
- On navigate to project: send `subscribe_project`. On leave: send `unsubscribe_project`.
- Incoming events dispatch to: Redux actions (client state updates) and/or TanStack Query invalidation (server state refresh).
- Reconnection with exponential backoff managed by the client.

#### Requirements Panel State Pattern
- Redux slice holds requirements panel state (expanded sections, selected items, drag state).
- State updates propagate to TanStack Query cache for optimistic UI updates.
- Server synchronization occurs via REST API (POST/PATCH/DELETE endpoints).
- WebSocket events from other collaborators trigger cache invalidation and UI refresh.

### Backend

#### Service Layer Pattern
Each Django app follows:
```
apps/<domain>/
├── models.py         # Django ORM models (data layer)
├── services.py       # Business logic (service layer)
├── serializers.py    # DRF serializers (gateway only — API layer)
├── views.py          # DRF viewsets/views (gateway only — API layer)
├── urls.py           # URL routing (gateway only)
├── tasks.py          # Celery tasks (core only, if applicable)
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_views.py    # (gateway only)
```

- **Models** define data structure. No business logic in models.
- **Services** contain all business logic. Called by gRPC servicers (core, AI) or DRF views (gateway).
- **Views/Serializers** (gateway only) handle HTTP request/response. Delegate to services or gRPC clients.
- **gRPC Servicers** (core, AI) handle gRPC requests. Delegate to services.

#### Event Publishing Pattern
Services publish events to the message broker after successful operations:
```python
# In services.py
def submit_project_for_review(project_id, user_id, message, reviewer_ids):
    # 1. Business logic (state transition, document versioning)
    project = transition_project_state(project_id, 'in_review')
    version = create_document_version(project_id)

    # 2. Publish events (async notification, WebSocket broadcast)
    publish_event('project.submitted', {
        'project_id': project_id,
        'user_id': user_id,
        'version_id': version.id,
        'reviewer_ids': reviewer_ids,
    })

    return project, version
```

Consumers in the notification service, AI service, and gateway pick up events and act.

#### gRPC Pattern
- Proto files define service contracts (`proto/`).
- `generate-proto.sh` compiles to Python stubs.
- Each service has a `grpc_server/` with servicer implementations and a `grpc_clients/` with client wrappers.
- Clients use connection pooling and retry logic.

#### Admin Parameter Access Pattern
```python
# Cached parameter access with runtime refresh
from apps.admin_config.services import get_parameter

debounce_timer = get_parameter('debounce_timer', default=3, cast=int)
```
Parameters cached in-memory with short TTL. Cache invalidated on admin update via `admin.parameter.updated` broker event.

---

## Code Quality

| Tool | Config File | Purpose |
|------|------------|---------|
| ESLint | `frontend/eslint.config.js` | TypeScript/React linting |
| Prettier | `frontend/.prettierrc` | Frontend code formatting |
| TypeScript | `frontend/tsconfig.json` | Type checking |
| Ruff | `services/*/pyproject.toml` | Python linting + formatting (replaces flake8 + black + isort) |
| mypy | `services/*/pyproject.toml` | Python type checking (advisory — see note below) |

### Linting Rules (Key)
- **Frontend**: ESLint recommended + React Hooks rules + import sorting
- **Backend**: Ruff defaults + Django-specific rules + import sorting
- **Both**: No unused variables, no unused imports, consistent quotes

> **mypy advisory status:** `ruff check` is the primary Python quality gate. `mypy` is advisory until `django-stubs` is configured project-wide — Django ORM reverse relations, gRPC stub types, and `request.user` union-attr patterns produce false positives that are not runtime bugs. Same pattern applies to all Django+gRPC services.

> **BaseAgent Liskov pattern:** All BaseAgent subclasses (FacilitatorAgent, BoardAgent, ContextCompressionAgent, ContextAgent, ContextExtensionAgent, SummarizingAgent) narrow the input type from `AgentInput` to their specific input model (e.g., `SummarizingInput`) in `_execute()` and `_load_mock_response()`. This produces mypy Liskov substitution warnings but is the established convention — each agent's invoke() receives its own typed input. Changing this would break all agents.

### Pre-commit Hooks
- Lint + format check on staged files
- Type check (frontend: `tsc --noEmit`, backend: `ruff check` — `mypy` advisory)
- Proto file compilation check (if .proto files changed)

---

## Environment Variables

### Frontend (build-time)
| Variable | Required | Description |
|----------|----------|-------------|
| VITE_API_BASE_URL | Yes | API base URL (default: `/api`) |
| VITE_WS_BASE_URL | Yes | WebSocket base URL (default: `/ws`) |
| VITE_AZURE_AD_CLIENT_ID | Yes (prod) | Azure AD client ID for MSAL |
| VITE_AZURE_AD_TENANT_ID | Yes (prod) | Azure AD tenant ID |
| VITE_AUTH_BYPASS | No | Enable dev auth bypass UI |

### Gateway Service
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis connection (channel layer) |
| SECRET_KEY | Yes | Django secret key |
| ALLOWED_HOSTS | Yes | Django allowed hosts |
| AZURE_AD_TENANT_ID | Yes (prod) | Azure AD tenant ID |
| AZURE_AD_CLIENT_ID | Yes (prod) | Azure AD client ID |
| AZURE_AD_CLIENT_SECRET | Yes (prod) | Azure AD client secret |
| AUTH_BYPASS | No | Enable auth bypass (with DEBUG) |
| DEBUG | No | Django debug mode |
| CORE_GRPC_ADDRESS | Yes | Core service gRPC address |
| AI_GRPC_ADDRESS | Yes | AI service gRPC address |
| PDF_GRPC_ADDRESS | Yes | PDF service gRPC address |
| BROKER_URL | Yes | RabbitMQ / Azure Service Bus connection |
| GATEWAY_GRPC_PORT | No | Gateway gRPC server port (default: 50054) |
| AZURE_STORAGE_CONNECTION_STRING | Yes (prod) | Azure Blob Storage for PDF files |
| PDF_STORAGE_PATH | Yes (dev) | Local path for PDF files (Docker volume) |

### Core Service
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| SECRET_KEY | Yes | Django secret key |
| BROKER_URL | Yes | Message broker connection |
| GATEWAY_GRPC_ADDRESS | Yes | Gateway gRPC address (for event callbacks) |
| GATEWAY_HTTP_URL | Yes | Gateway HTTP URL (for health checks) |
| AI_GRPC_ADDRESS | Yes | AI service gRPC address |
| PDF_GRPC_ADDRESS | Yes | PDF service gRPC address (for health checks) |
| HEALTH_REDIS_URL | No | Redis URL for health check result storage (default: CELERY_RESULT_BACKEND) |

### AI Service
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| AZURE_OPENAI_ENDPOINT | Yes | Azure OpenAI endpoint |
| AZURE_OPENAI_API_KEY | Yes | Azure OpenAI API key |
| AZURE_OPENAI_API_VERSION | Yes | Azure OpenAI API version (e.g., `2024-02-15-preview`) |
| BROKER_URL | Yes | Message broker connection |
| CORE_GRPC_ADDRESS | Yes | Core service gRPC address |
| AZURE_OPENAI_DEFAULT_DEPLOYMENT | Yes | Default tier deployment name — fallback if `default_ai_model` admin parameter is empty (e.g., GPT-4o) |
| AZURE_OPENAI_CHEAP_DEPLOYMENT | Yes | Cheap tier deployment name (GPT-4o-mini, not admin-configurable) |
| AZURE_OPENAI_ESCALATED_DEPLOYMENT | Yes | Escalated tier deployment name — fallback if `escalated_ai_model` admin parameter is empty (e.g., GPT-4o) |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT | Yes | Embedding model deployment name (text-embedding-3-small) |
| AI_MOCK_MODE | No | When `true`, agents return fixture data instead of calling Azure OpenAI (E2E testing) |

### Notification Service
| Variable | Required | Description |
|----------|----------|-------------|
| BROKER_URL | Yes | Message broker connection |
| GATEWAY_GRPC_ADDRESS | Yes | Gateway gRPC address |
| CORE_GRPC_ADDRESS | Yes | Core gRPC address |
| ACS_EMAIL_ENDPOINT | No | Azure Communication Services Email endpoint (leave empty to disable) |
| ACS_EMAIL_ACCESS_KEY | No | Azure Communication Services access key |
| EMAIL_FROM | No | Sender email address (must match ACS verified domain) |

### PDF Service
| Variable | Required | Description |
|----------|----------|-------------|
| (none required beyond gRPC port) | | Stateless service |

---

## Docker Compose Topology (Development)

```yaml
services:
  # Infrastructure
  nginx:          # Reverse proxy → frontend, gateway
  postgresql:     # Shared database (pgvector/pgvector:pg16 image)
  redis:          # Django Channels layer
  rabbitmq:       # Message broker

  # Application
  frontend:       # Vite dev server (hot reload)
  gateway:        # Django + DRF + Channels (Daphne)
  core:           # Django + gRPC server
  ai:             # Python + gRPC server
  notification:   # Python event consumer
  pdf:            # Python + gRPC server
  celery-worker:  # Core codebase, Celery worker mode
  celery-beat:    # Core codebase, Celery beat mode
```

**Total: 12 containers** for local development.

---

## File-to-Feature Mapping

| Feature Area | Primary Directory | Key Files | Features |
|-------------|------------------|-----------|----------|
| Landing Page / Projects | `frontend/src/pages/landing-page.tsx`, `components/landing/`, `features/projects/` | Page, HeroSection, ProjectCard, InvitationCard, FilterBar, hooks, API calls | FA-1, FA-9 |
| Chat | `frontend/src/components/chat/`, `features/chat/` | ChatPanel, hooks, WS events | FA-2 |
| Requirements Panel | `frontend/src/components/requirements/`, `features/requirements/`, `store/requirements-slice.ts` | RequirementsPanel, hierarchy tree, sortable list, hooks | FA-3 |
| Requirements Document | `frontend/src/components/requirements_document/`, `features/requirements_document/` | DocumentEditor, sections, PDF preview | FA-4 |
| Real-Time | `frontend/src/features/websocket/`, `features/presence/`, `store/websocket-slice.ts` | WS client, presence, reconnection | FA-6 |
| Authentication | `frontend/src/features/auth/` | MSAL config, route guards, dev bypass | FA-7 |
| Collaboration | `frontend/src/components/collaboration/`, `features/collaboration/` | InviteDialog, presence | FA-8 |
| Project Lifecycle | `services/core/apps/projects/` | State machine, soft delete | FA-9 |
| Review Workflow | `frontend/src/pages/review-page.tsx`, `services/core/apps/review/` | Timeline, actions, assignments | FA-10 |
| Admin Panel | `frontend/src/pages/admin-panel.tsx`, `frontend/src/components/admin/` | AI context, params, monitoring, users | FA-11 |
| Notifications | `frontend/src/components/notification/`, `services/notification/` | Bell, list, email dispatch | FA-12 |
| AI Features | `services/ai/` | Agent pipeline (see `docs/03-ai/`) | FA-13 |
| Error Handling | `frontend/src/components/common/`, `services/gateway/middleware/` | ErrorBoundary, error formatting | FA-14 |
| Accessibility | Cross-cutting (all frontend components) | ARIA attributes, keyboard nav, motion | FA-15 |
| i18n | `frontend/src/i18n/` | Config, translation files, language switch | FA-16 |
| Offline | `frontend/src/features/websocket/`, `store/websocket-slice.ts` | Banner, reconnection, stale state | FA-17 |
| API Gateway | `services/gateway/` | REST endpoints, WS consumers, gRPC routing | Cross-cutting |
| Core Service | `services/core/` | Domain logic, gRPC servicers, Celery tasks | Cross-cutting |
| PDF Service | `services/pdf/` | HTML template, WeasyPrint rendering | FA-4 |
| Shared Protos | `proto/` | gRPC contract definitions | Cross-cutting |
| Infrastructure | `infra/docker/` | Docker Compose, Nginx config | Cross-cutting |

---

## Key Decisions

1. **Monorepo over multi-repo** — single product, shared proto definitions, one team, simpler CI/CD.
2. **Core as one service** — projects, chat, collaboration, and review are tightly coupled to the project lifecycle. Splitting would create excessive cross-service calls.
3. **Shared PostgreSQL instance** — pragmatic for ~2,000 users. Logical separation by service (own tables, own migrations). Can split later if needed.
4. **Celery workers share core codebase** — standard pattern. Separate containers, same code and database.
5. **Feature-based frontend organization** — `features/` for business logic (hooks, API calls), `components/` for UI. Clear separation of concerns.
6. **Service layer in Django apps** — all business logic in `services.py`, not in models or views. Makes logic testable and reusable across gRPC and REST interfaces.
7. **Proto files in shared directory** — single source of truth for gRPC contracts. Compiled stubs generated into `proto/` directory (same location as .proto files, not a separate generated/ subdirectory).
8. **Ruff over Black + flake8 + isort** — single tool replaces three. Faster, simpler configuration, actively maintained.
9. **AI service internal structure deferred to AI Engineer** — the Architect defines the service boundary (gRPC interface, database ownership, container config, message broker integration). The AI Engineer defines the internal organization (agent structure, framework, processing pipeline) in `docs/03-ai/`.
