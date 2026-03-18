# Technology Stack

## Overview

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Frontend Framework | React | 19.x | Corporate standard |
| Build Tool | Vite | 7.x | Standard modern bundler for React SPAs, fast HMR, TypeScript-native |
| Language (Frontend) | TypeScript | 5.x | Type safety across a complex collaborative UI with real-time state |
| CSS Framework | Tailwind CSS | 4.x | Corporate standard |
| Component Library | shadcn/ui (Radix primitives) | latest | Tailwind-native, accessible, no dependency lock-in — corporate library philosophy |
| State Management | Redux Toolkit | 2.x | Structured action-based model for requirements panel optimistic state, DevTools for debugging, middleware for WebSocket side effects |
| Server State | TanStack Query | 5.x | Cache management, optimistic updates, retry logic for REST API calls |
| Language (Backend) | Python | 3.12+ | Corporate standard |
| Backend Framework | Django | 5.x | Corporate standard for complex services; ORM, auth middleware, mature ecosystem |
| REST API | Django REST Framework | 3.x | Standard Django REST layer; serialization, viewsets, permission classes |
| WebSocket | Django Channels | 4.x | Real-time collaboration (FA-6); presence, chat broadcast, requirements panel sync |
| Service-to-Service | gRPC (grpcio + protobuf) | latest | Corporate standard for inter-service communication |
| Database | PostgreSQL | 16.x | Corporate standard; deeply relational data model, Django ORM first-class support |
| Vector Extension | pgvector | 0.7+ | PostgreSQL extension for vector similarity search; used by AI service for RAG. Schema defined here, usage patterns defined by AI Engineer in `docs/03-ai/` |
| ORM | Django ORM | (bundled) | Native to Django; migrations, querysets, PostgreSQL-optimized features |
| Message Broker (Dev) | RabbitMQ | 3.x | Event-driven architecture; DLQ support (NFR-R1); Docker container for local dev |
| Message Broker (Prod) | Azure Service Bus | managed | Azure SaaS equivalent of RabbitMQ; DLQ support native |
| Task Scheduling | Celery | 5.x | Periodic jobs: soft delete cleanup, monitoring health checks |
| Channel Layer (Dev) | Redis | 7.x | Django Channels pub/sub backend; Docker container for local dev |
| Channel Layer (Prod) | Azure Cache for Redis | managed | Managed Redis for Django Channels in production |
| Authentication (Frontend) | MSAL.js (@azure/msal-react) | 4.x | Azure AD OIDC/OAuth2; corporate preference (F-7.2) |
| Authentication (Backend) | Azure AD token validation | — | Token validation at API edge and WebSocket handshake (NFR-S2) |
| AI Provider | Azure OpenAI | managed | All AI features (Constraint #3). Model selection and agent architecture defined by AI Engineer in `docs/03-ai/` |
| AI Orchestration | Semantic Kernel (Python SDK) | latest | Azure-native, automatic function calling for Facilitator/Requirements Agent, unified base layer across all 5 agents (Facilitator, Context Agent, Context Extension, Summarizing AI, Context Compression). See `docs/03-ai/` |
| PDF Generation | WeasyPrint | 62.x | Python-native HTML-to-PDF; runs in container, no headless browser dependency (F-4.7). **Requires pydyf>=0.10,<0.12** (0.12.x breaks Stream.transform). System dependencies: libcairo2, libpango-1.0-0, libgdk-pixbuf-2.0-0 (Debian package names with hyphens). |
| File Storage — PDFs (Dev) | Local Docker volume | — | Mounted volume for storing generated PDF files during development |
| File Storage — PDFs (Prod) | Azure Blob Storage | managed | PDF file storage in production. `requirements_document_versions.pdf_file_path` stores the blob path. |
| File Storage — Attachments (Dev) | MinIO | 2024.x | S3-compatible object storage for development. Docker container. Bucket auto-created on Gateway startup. Supports presigned URLs. |
| File Storage — Attachments (Prod) | Azure Blob Storage | managed | Attachment file storage in production (images, PDFs). Storage abstraction layer (StorageBackend ABC) allows switching between MinIO/Azure without code changes. |
| Reverse Proxy (Dev) | Nginx | latest | Docker container; routes frontend, API, and WebSocket under single origin |
| Reverse Proxy (Prod) | Azure Container Apps ingress | managed | Ingress routing rules; same-origin for frontend + API + WebSocket |
| Hosting | Azure Container Apps | managed | Corporate standard (Constraint #6) |
| Containerization | Docker + Docker Compose | latest | Local development (Constraint #7) |

## Frontend Stack Details

### Rendering Strategy
- **SPA (Single Page Application)** — no server-side rendering
- Internal authenticated app with no SEO requirements, no public pages
- React SPA served as static assets from an Nginx container (production) or Vite dev server (development)

### Theming (Light/Dark Mode)
- **CSS variable–based theming** using shadcn/ui's built-in theme system (CSS custom properties on `:root` and `.dark` class)
- **Tailwind CSS `dark:` variant** — class-based dark mode strategy via `@custom-variant dark (&:where(.dark, .dark *))` in CSS (Tailwind CSS 4 CSS-native configuration, no `tailwind.config.ts`)
- Theme toggle switches a `dark` class on `<html>`, shadcn/ui components automatically adapt via CSS variables
- Theme preference persisted in `localStorage`, respects `prefers-color-scheme` as initial default (NFR-T2, NFR-T3)

### Brand & Typography
- **Font:** Gotham (commercial typeface, Commerz Real / Commerzbank corporate font). Self-hosted — font files served from the application's static assets. Requires corporate font license.
- **Fallback stack:** `'Gotham', ui-sans-serif, system-ui, -apple-system, sans-serif`
- **Icons:** Lucide React (`lucide-react`) — standard icon set for shadcn/ui. SVG-based, tree-shakeable.
- **Brand colors and full palette:** Defined by UI/UX Designer in `docs/03-design/`

### State Management
- **Redux Toolkit** for client-local state:
  - Requirements panel optimistic state and local drag operations
  - WebSocket connection lifecycle and reconnection state (F-6.1)
  - Presence tracking (online/idle/offline users) (F-6.3)
  - UI layout state (divider position, panel toggles, active tabs)
  - Offline/online banner state (F-6.5)
  - Rate limiting lockout state (F-2.11)
- **TanStack Query** for server state:
  - Project data, chat messages, requirements document content
  - Notification list, review queue, user directory
  - Cache invalidation on WebSocket events
  - Optimistic updates for chat send, requirements edits

### Form Handling
- **React Hook Form** for form state management (requirements document section editing, admin parameters, review comments, submit flows)
- **Zod** for schema validation — shared validation logic between frontend forms and API contracts

### Data Fetching
- **TanStack Query** wrapping `fetch` calls to REST API endpoints
- WebSocket messages trigger TanStack Query cache invalidation for real-time updates
- No direct gRPC from frontend — all communication via REST + WebSocket to API gateway

### Key Frontend Libraries
| Package | Purpose | Justification |
|---------|---------|---------------|
| @dnd-kit/core + @dnd-kit/sortable | Drag-and-drop | FA-3: sortable requirements panel items (epics/stories, milestones/packages) |
| framer-motion | Animations | Title animation (F-2.3), AI indicators (F-2.12, F-3.4); respects `prefers-reduced-motion` (NFR-A5) |
| @azure/msal-react | Azure AD auth | OIDC/OAuth2 login, silent token refresh (F-7.2, NFR-S3) |
| react-i18next | Internationalization | German + English UI (FA-16); language switcher, persisted preference |
| lucide-react | Icons | Lucide icon library; best integration with shadcn/ui, consistent SVG icon set |
| react-toastify | Toast notifications | Transient notifications, error toasts |
| @reduxjs/toolkit | State management | Requirements panel state, WebSocket state, UI state |
| @tanstack/react-query | Server state | API data caching, optimistic updates, retry logic |
| react-hook-form | Form handling | Requirements document editing, admin config, review forms |
| zod | Schema validation | Shared validation schemas, form validation, API response validation |

## Backend Stack Details

### Architecture Pattern
- **Event-driven microservices**
- **API Gateway pattern** — single Django service faces the frontend (REST + WebSocket), delegates to internal services via gRPC
- **Reverse proxy** — Nginx (dev) / Azure Container Apps ingress (prod) routes all traffic under a single origin, eliminating CORS

### API Pattern
- **REST** (Django REST Framework) for frontend-to-gateway communication
- **WebSocket** (Django Channels) for real-time events (chat, requirements panel sync, presence, notifications)
- **gRPC** (grpcio + protobuf) for gateway-to-internal-service communication
- **Message broker** (RabbitMQ / Azure Service Bus) for asynchronous event-driven communication between services

### Validation
- **Pydantic** for internal data validation, gRPC message mapping, and AI prompt/response schemas
- **DRF serializers** for REST API request/response validation
- **Zod schemas** (frontend) align with DRF serializers for consistent validation

### Error Handling Strategy
- Universal error pattern (F-14.1): all API errors return consistent error response format
- Dead-letter queues on all message queues for debugging (NFR-R1)
- Idempotent event handlers (NFR-R2)
- Retry with configurable max attempts (default: 3, admin-configurable)
- DLQ messages are captured for debugging only — no automatic retry from DLQ. Retry is user-triggered via the frontend error toast "Retry" button (F-14.1)

### Background Jobs (Celery)
| Job | Schedule | Purpose |
|-----|----------|---------|
| Soft delete cleanup | Daily | Permanently delete projects past trash countdown (F-9.3) |
| Monitoring health checks | Configurable interval (default: 60s) | Check service health, DLQ counts, send alerts (F-11.4, F-11.5) |

### Key Backend Libraries
| Package | Purpose | Justification |
|---------|---------|---------------|
| djangorestframework | REST API | Standard Django REST layer |
| channels | WebSocket support | Real-time collaboration (FA-6) |
| channels-redis | Channel layer backend | Redis-backed pub/sub for Django Channels |
| grpcio + grpcio-tools | gRPC client/server | Corporate standard: inter-service communication |
| celery | Task scheduling | Periodic background jobs |
| pydantic | Data validation | gRPC schemas, AI prompt/response contracts |
| weasyprint | PDF generation | Requirements document to PDF (F-4.7) |
| minio | Object storage client | MinIO SDK for attachment file storage (dev). Storage abstraction layer supports Azure Blob (prod). |
| Pillow | Image processing | EXIF metadata stripping, image sanitization, thumbnail generation for attachments |
| PyMuPDF (fitz) | PDF processing | PDF text extraction, JavaScript detection/stripping, page rendering for AI vision fallback |
| openai (Azure SDK) | AI integration | Azure OpenAI API calls (used by AI service — see `docs/03-ai/`) |
| pgvector | Vector search | PostgreSQL vector column type (VectorField) and HNSW indexes for RAG and similarity |
| msal | Token validation | Backend Azure AD token verification |
| factory-boy | Test fixtures | Test data generation |
| pytest + pytest-django | Testing | Standard Python/Django testing |

## Infrastructure

### Reverse Proxy Configuration
- **Development:** Nginx container in Docker Compose
  - `/` → Vite dev server (frontend hot reload)
  - `/api/*` → Django API gateway
  - `/ws/*` → Django Channels (WebSocket)
  - Alternative: Vite's built-in proxy during active frontend development
- **Production:** Azure Container Apps ingress routing
  - Same routing rules, managed by Azure
  - Single external domain, no CORS

### Container Topology (Docker Compose — Development)
```
nginx (reverse proxy)
├── frontend (Vite dev server)
├── gateway (Django + Channels)
├── [internal microservices] (Django/Python + gRPC)
├── celery-worker (background tasks)
├── celery-beat (task scheduler)
├── postgresql
├── redis
├── rabbitmq
└── minio (S3-compatible object storage for attachments)
```

### CI/CD
- Docker-based builds for all services
- Each microservice has its own Dockerfile
- Docker Compose for local development orchestration
- Azure Container Apps deployment via CI pipeline

### Monitoring
- Admin Panel dashboard (F-11.4) — lightweight, built into the application
- Backend monitoring service (F-11.5) — Celery periodic task
- Email alerts to configured Admin recipients

## Real-Time Transport Design (F-6.1, F-3.6)

> ⚙️ This section addresses the downstream delegation from requirements for real-time transport, requirements panel sync protocol, and connection lifecycle.

### Transport: WebSocket via Django Channels

**Why WebSocket over SSE:**
- SSE is server-to-client only. ZiqReq requires bidirectional communication (client sends selections, presence, typing indicators).
- WebSocket is the native transport for Django Channels — no additional runtime needed.
- Single session-level connection serves all real-time needs (NFR-P4).

### Connection Lifecycle (F-6.1)
1. **Connect:** Frontend opens WebSocket to `/ws/?token=<jwt>`. Gateway validates token on handshake.
2. **Subscribe:** Client sends `subscribe_project` when navigating to a project workspace. Server adds client to the project's channel group.
3. **Unsubscribe:** Client sends `unsubscribe_project` when leaving. Server removes client from the group.
4. **Idle:** After configurable inactivity (default: 5 minutes), client sends `presence_update` with state `idle`. After further idle (default: 120 seconds), server closes connection.
5. **Disconnect:** On connection drop, server cleans up presence. Client initiates reconnection with exponential backoff (max 30 seconds, admin-configurable).
6. **Reconnect:** On successful reconnect, client re-subscribes to active project and fetches latest state via REST to reconcile.

### Requirements Panel Sync Protocol (F-3.6)

Requirements structure changes (creating, updating, deleting, reordering epics/stories or milestones/packages) use REST mutations followed by WebSocket broadcasts:

| Event Category | Transport | Persistence | Latency Target |
|---|---|---|---|
| **Awareness events** (selections, active item focus) | WebSocket only — fire immediately | Not persisted | < 100ms |
| **Structure changes** (create/update/delete/reorder items) | REST mutation → server persists → WebSocket broadcast | Persisted | < 500ms (NFR-P3) |

**Why this approach:**
- Awareness events (who is editing what) are ephemeral — no persistence needed, but must be instant for collaborative feel.
- Structure changes must be persisted before broadcasting. REST-first ensures data integrity. Server broadcasts via WebSocket after successful write.
- This avoids the complexity of CRDT or OT — last-write-wins is sufficient for requirements item editing.

### Conflict Resolution
- **Last-write-wins** for concurrent edits to the same requirements item. Server timestamp determines ordering.
- **Selection highlighting** prevents most conflicts by showing other users which items are being edited.
- No operational transformation or CRDT — the collaborative editing pattern is item-level (entire requirement content), not character-level.

## Requirements Panel State Management

> ⚙️ This section addresses the downstream delegation for requirements panel state handling.

- **Storage:** Component-local state. RequirementsPanel component manages UI state (expanded accordions, editing mode) via React useState hooks.
- **WebSocket sync:** Window CustomEvent listeners (matching the pattern used elsewhere for WS events). Events: `requirements_updated`, `requirements_generating`, `requirements_ready`.
- **Scope:** Requirements panel item reordering, create/update/delete operations.
- **Optimistic updates:** Drag operations are applied immediately to local state. On drop, REST mutation is sent. On success, WebSocket broadcasts to other users. On failure, local state is reverted and error toast shown.
- **No undo/redo:** The requirements panel does not require undo/redo functionality. Users edit structured requirement items directly (with standard form validation and save/cancel flows).
- **Redux not used:** The requirements panel is self-contained with no cross-component state sharing needs. CustomEvents for WS sync reduced Redux boilerplate.

## PDF Generation Service Design (F-4.7)

> ⚙️ This section addresses the downstream delegation for PDF generation and storage.

### Service
- **Stateless gRPC service** using WeasyPrint (Python-native HTML-to-PDF).
- Receives requirements document content from the gateway, renders HTML template, returns PDF bytes.
- No database access. No state. Horizontally scalable.

### Storage
- **Development:** Local Docker volume mount. Path configured via `PDF_STORAGE_PATH` env var.
- **Production:** Azure Blob Storage. Path configured via `AZURE_STORAGE_CONNECTION_STRING`.
- Gateway receives PDF bytes from PDF service, uploads to storage, saves path in `requirements_document_versions.pdf_file_path`.

### Versioning
- Each submit/resubmit creates an immutable `requirements_document_versions` record with its own PDF.
- Filename convention: `REQ_{date}_{project_title_slug}.pdf`
- Previous versions preserved and downloadable from the review timeline.

## Authentication Flow Design (F-7.2)

> ⚙️ This section addresses the downstream delegation for authentication, token management, and middleware.

### Frontend (MSAL.js)
1. App loads → MSAL checks for existing session (cached token).
2. If no valid token → redirect to Azure AD login page.
3. On successful login → MSAL caches tokens (access token, refresh token, ID token).
4. Access token attached to all REST requests as `Authorization: Bearer <token>`.
5. Access token passed in WebSocket handshake as query parameter: `/ws/?token=<jwt>`.
6. MSAL handles silent token refresh before expiry. If silent refresh fails → redirect to login.

### Backend Middleware
1. **REST:** Auth middleware extracts Bearer token, validates against Azure AD JWKS endpoint (cached keys), extracts user claims (object ID, roles from group membership), attaches user to request context.
2. **WebSocket:** Auth middleware on connection handshake extracts token from query parameter, validates identically to REST middleware. Connection rejected if invalid.
3. **User sync:** On first successful validation per session, user data synced to shadow `users` table (upsert: create if new, update name/roles if changed).

### Dev Bypass Mode (F-7.1)
- Double-gated: `AUTH_BYPASS=True` AND `DEBUG=True`.
- Middleware detects bypass mode and uses session-based fake auth with preconfigured dev users.
- All permission checks work identically — bypass only skips Azure AD token validation.
- Cannot activate in production (double-gate enforced in settings).

## Monitoring Service Design (F-11.5)

> ⚙️ This section addresses the downstream delegation for monitoring health checks and alerting.

### Design
- **Celery periodic task** in the core service worker (shared codebase with keyword matching).
- Runs on configurable interval (default: 60 seconds, admin-configurable via `health_check_interval`).
- **Module location:** Core service (`services/core/apps/monitoring/`). Files are mirrored into Gateway's `apps.monitoring/` for test discoverability due to namespace conflict (both services have `apps.monitoring` packages). See `project-structure.md` Module Mirroring section.

### Health Checks
| Check | Method | Healthy Condition |
|---|---|---|
| API Gateway | HTTP GET to gateway health endpoint | 200 response within 5s |
| AI Service | gRPC health check | Serving status |
| PDF Service | gRPC health check | Serving status |
| Notification Service | Check broker consumer heartbeat | Consumer active |
| Database | Django DB connection check | Connection successful |
| Redis | Redis PING | PONG response |
| Message Broker | Broker connection check | Connected |
| DLQ Depth | Query DLQ message count per queue | Below `dlq_alert_threshold` (default: 10) |

### Metrics Tracked
- Active WebSocket connections (from gateway via gRPC)
- Projects by state (aggregate query)
- AI processing stats (from AI service via gRPC)
- DLQ message counts per queue

### Alerting Pipeline
1. Health check detects unhealthy condition or threshold breach.
2. Publishes `monitoring.alert` event to message broker.
3. Notification service consumes event, looks up opted-in admins (`monitoring_alert_configs` table), sends email alerts.
4. Alert also stored for display in the Admin Panel monitoring tab.

## Error Handling Infrastructure (F-14.1)

> ⚙️ This section addresses the downstream delegation for DLQ strategy and retry mechanics.

### Dead-Letter Queues
- **Every message queue** has a paired DLQ (RabbitMQ: `x-dead-letter-exchange` / Azure Service Bus: native DLQ).
- Failed messages are routed to DLQ after 3 retry attempts (exponential backoff: 1s, 2s, 4s).
- **No automatic retry from DLQ.** Messages sit in DLQ for debugging/manual inspection.
- DLQ message count monitored by the monitoring service. Alert triggered when count exceeds `dlq_alert_threshold`.

### Retry Strategy
- **Message broker consumers:** 3 attempts with exponential backoff before DLQ.
- **gRPC calls:** 3 attempts with exponential backoff (configurable via `max_retry_attempts`).
- **Frontend API calls:** TanStack Query retry (3 attempts), then error toast with "Retry" button for manual retry (F-14.1).

### User-Facing Error Pattern
1. Operation fails after retries exhausted.
2. Frontend shows error toast with "Show Logs" and "Retry" buttons.
3. "Show Logs" opens modal with: error code, network response, technical details, support contact.
4. "Retry" re-triggers the failed operation.
5. Maximum retry attempts configurable (default: 3, admin-configurable).

### Idempotency (NFR-R2)
- All event consumers are idempotent. Events include a unique event ID. Consumers track processed event IDs to detect duplicates.
- Database operations use upsert patterns where applicable.
- AI processing uses a version counter per project — stale processing results are discarded before persisting.

## User Preference Persistence Strategy

> ⚙️ This section addresses the downstream delegation from data-entities.md for user preference storage.

| Preference | Storage | Rationale |
|---|---|---|
| Language (German/English) | `localStorage` (frontend) | Immediate application, no round-trip needed. Respects the pattern that language is a display preference. |
| Theme (Light/Dark) | `localStorage` (frontend) | Immediate CSS class toggle, no server dependency. OS preference as initial default. |
| Email notification preferences | Database (`users.email_notification_preferences` JSONB) | Must be server-side — notification service reads this when deciding whether to send email. |

## Infrastructure Admin Parameters (F-11.3)

> ⚙️ This section addresses the downstream delegation for operational admin parameters.

In addition to the application parameters listed in F-11.3, the following infrastructure parameters are admin-configurable:

| Parameter | Default | Description |
|---|---|---|
| max_retry_attempts | 3 | Max retry attempts for failed operations (gRPC calls, message processing) |
| dlq_alert_threshold | 10 | DLQ message count that triggers a monitoring alert |
| health_check_interval | 60 | Seconds between health check runs |

> **Note:** AI-specific parameters (context compression threshold, model deployments, AI processing timeout, RAG settings) are defined by the AI Engineer in `docs/03-ai/`. The admin parameter table will include both infrastructure and AI parameters — the AI Engineer specifies which AI parameters to add.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis connection string (channel layer) |
| RABBITMQ_URL / AZURE_SERVICE_BUS_CONNECTION_STRING | Yes | Message broker connection |
| AZURE_OPENAI_ENDPOINT | Yes | Azure OpenAI service endpoint |
| AZURE_OPENAI_API_KEY | Yes | Azure OpenAI API key |
| AZURE_AD_TENANT_ID | Yes | Azure AD tenant identifier |
| AZURE_AD_CLIENT_ID | Yes | Azure AD app registration client ID |
| AZURE_AD_CLIENT_SECRET | Yes (backend) | Azure AD app registration secret |
| AZURE_STORAGE_CONNECTION_STRING | Yes (prod) | Azure Blob Storage connection string for PDF and attachment file storage |
| PDF_STORAGE_PATH | Yes (dev) | Local filesystem path for PDF storage in development (Docker volume mount) |
| MINIO_ENDPOINT | Yes (dev) | MinIO server endpoint (e.g., `minio:9000` in Docker Compose) |
| MINIO_ACCESS_KEY | Yes (dev) | MinIO access key for authentication |
| MINIO_SECRET_KEY | Yes (dev) | MinIO secret key for authentication |
| MINIO_BUCKET | Yes (dev) | MinIO bucket name for attachments (default: `attachments`) |
| STORAGE_BACKEND | No | Storage backend type: `minio` (dev) or `azure_blob` (prod). Defaults to `minio`. |
| AUTH_BYPASS | No | Enable auth bypass (must pair with DEBUG=True) |
| DEBUG | No | Enable debug mode |
| SECRET_KEY | Yes | Django secret key |
| ALLOWED_HOSTS | Yes | Django allowed hosts |
| ACS_EMAIL_ENDPOINT / ACS_EMAIL_ACCESS_KEY / EMAIL_FROM | No | Azure Communication Services Email (leave empty to disable) |

> **Note:** AI-specific environment variables (model deployment names, API versions, embedding configuration) are defined by the AI Engineer in `docs/03-ai/`. They will be added to service-specific env var tables in `project-structure.md`.

## Rejected Alternatives

| Decision | Rejected Option | Reason |
|----------|----------------|--------|
| Frontend framework | Next.js | No SSR needed for internal app; Azure Container Apps doesn't benefit from Vercel optimizations; adds complexity to Docker deployment |
| Frontend framework | Angular, Vue | Corporate standard is React |
| State management | Zustand | Insufficient structure for complex collaborative state (requirements panel, WebSocket events, presence tracking); Redux Toolkit's action-based model, middleware, and DevTools better suited for a corporate team |
| Database | MongoDB | Deeply relational data model with extensive FK references; Django ORM is relational-first |
| Message broker | Kafka | Overkill for ~2,000 users; RabbitMQ/Service Bus fits the event volume and DLQ requirements |
| WebSocket | Socket.IO | Django Channels is the native Django solution; avoids adding Node.js to a Python stack |
| Real-time transport | SSE (Server-Sent Events) | Unidirectional (server→client only); ZiqReq requires bidirectional communication for selections, presence, typing |
| PDF generation | Puppeteer / Playwright | Requires headless Chromium; heavy container footprint; WeasyPrint is Python-native and lighter |
| Component library | MUI / Ant Design | Conflicts with Tailwind styling system; shadcn/ui is Tailwind-native |
| CORS approach | django-cors-headers | Reverse proxy eliminates CORS entirely; cleaner for WebSocket; standard pattern for SPA + API deployments |
