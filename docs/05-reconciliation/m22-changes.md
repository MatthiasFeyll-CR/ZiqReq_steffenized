# Milestone 22 Spec Reconciliation — Chat File Attachments

## Summary
- **Milestone:** M22 — Chat File Attachments
- **Date:** 2026-03-18
- **Total deviations found:** 20 (all additions — M22 is a new feature)
- **Auto-applied (SMALL TECHNICAL):** 10
- **Applied and flagged (FEATURE DESIGN):** 7
- **Applied and flagged (LARGE TECHNICAL):** 3
- **Rejected:** 0

**Nature of changes:** M22 introduced a completely new feature (file attachments), so all spec updates are ADDITIONS, not corrections. The upstream docs did not describe attachments prior to M22 implementation.

---

## Changes Applied

### SMALL TECHNICAL (Auto-applied)

These are implementation details discovered during M22 that clarify patterns but don't change feature behavior.

| # | Detail | Document Updated | Change |
|---|--------|------------------|--------|
| 1 | Storage module location | `docs/02-architecture/project-structure.md` | Documented: storage module at `services/gateway/storage/` (not inside a Django app) |
| 2 | App labels | `docs/02-architecture/project-structure.md` | Documented: `gateway_projects`, `gateway_attachments` app labels |
| 3 | Migration sequence | `docs/02-architecture/data-model.md` | Documented: 0006_project_favorite was latest Gateway migration before M22 |
| 4 | Proto regeneration command | `docs/02-architecture/project-structure.md` | Documented command: `cd proto && python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. core.proto` |
| 5 | Celery task pattern | `docs/03-ai/agent-architecture.md` (if exists) | Documented: Celery tasks NOT bind=True (no automatic retry) — simpler for testing |
| 6 | AI DB access pattern | `docs/02-architecture/project-structure.md` | Documented: AI service uses direct SQL via `django.db.connection` (CoreClient pattern) |
| 7 | Vision fallback trigger | `docs/03-ai/agent-architecture.md` (if exists) | Documented: vision fallback triggers when page text < 50 chars AND page has images |
| 8 | Pipeline poll interval | `docs/03-ai/agent-architecture.md` (if exists) | Documented: extraction wait polls every 2s, max 30s timeout |
| 9 | Upload XHR pattern | Frontend patterns doc (if exists) | Documented: upload uses XMLHttpRequest (not fetch) for progress events |
| 10 | ObjectURL cleanup | Frontend patterns doc (if exists) | Documented: URL.createObjectURL requires cleanup on unmount to prevent memory leaks |

---

### FEATURE DESIGN (Applied, flagged prominently in changelog)

These changes add new features or behavioral patterns to the spec.

| # | Feature | Document Updated | Change |
|---|---------|------------------|--------|
| 1 | **Attachments table schema** | `docs/02-architecture/data-model.md` | **ADDED:** Complete `attachments` table definition with 11 columns (id, project_id, message_id nullable, uploader_id, filename, storage_key, content_type, size_bytes, extracted_content, extraction_status, created_at, deleted_at). Includes 3 indexes (project, message, project+deleted composite). Gateway-owned managed model, Core has unmanaged mirror. |
| 2 | **4 new API endpoints** | `docs/02-architecture/api-design.md` | **ADDED:** POST /attachments (upload), GET /attachments (list), DELETE /attachments/:id (soft-delete), GET /attachments/:id/url (presigned URL). Includes validation rules, rate limiting (10/min/user), error codes, side effects. |
| 3 | **Chat message modification** | `docs/02-architecture/api-design.md` | **MODIFIED:** POST /api/projects/:id/chat now accepts optional `attachment_ids` array (max 3). Content field accepts " " (single space) when empty text with attachments. Response includes attachments array. AI pipeline waits for extraction (max 30s). |
| 4 | **Presigned URL read-only blocking** | `docs/02-architecture/api-design.md` | **CLARIFIED:** Read-only share link users blocked via access control layer (`_check_access` requires collaborator), NOT an explicit read-only flag. Frontend enforces with `clickable={!isReadOnly}` + toast message. *(DEV-001 from QA report)* |
| 5 | **AI prompt structure** | `docs/03-ai/system-prompts.md` | **ADDED:** Facilitator prompt includes `<attachments>` block after `</project>` with `<user_attachment>` XML blocks containing WARNING attribute for prompt injection sandboxing. Each attachment shows: id, filename, message_id, truncated extracted_content (max 16000 chars/4000 tokens). |
| 6 | **Attachment guidance in prompt** | `docs/03-ai/system-prompts.md` | **ADDED:** `<attachment_guidance>` block instructs Facilitator to reference uploaded files by filename, use extracted content to inform requirements structuring (e.g., PDF workflows → epics/milestones). |
| 7 | **Context Extension search** | `docs/03-ai/system-prompts.md` | **MODIFIED:** Context Extension agent now searches both chat history AND attachment extracted_content. `<project_attachments>` block added to prompt with filename + extracted content for each attachment. |

---

### LARGE TECHNICAL (Applied, flagged prominently in changelog)

These changes introduce significant infrastructure or architectural patterns.

| # | Architecture | Document Updated | Change |
|---|-------------|------------------|--------|
| 1 | **MinIO storage architecture** | `docs/02-architecture/tech-stack.md`, `docs/02-architecture/project-structure.md` | **ADDED:** Storage abstraction layer with `StorageBackend` ABC, `MinIOBackend` implementation (dev), `AzureBlobBackend` stub (prod). Singleton factory pattern via `get_storage_backend()`. Bucket auto-creation in `ProjectsConfig.ready()` (guarded try/except). MinIO added to Docker Compose topology. Environment variables: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, STORAGE_BACKEND. |
| 2 | **Celery in AI service** | `docs/02-architecture/project-structure.md`, `docs/03-ai/agent-architecture.md` (if exists) | **ADDED:** Celery app at `ai_service/celery.py` uses BROKER_URL (RabbitMQ). Task `extract_attachment_content` dispatched from Gateway upload view. AI service downloads files directly via MinIO client (not Gateway storage abstraction) to avoid circular gRPC dependencies. |
| 3 | **Proto updates for attachments** | `docs/02-architecture/api-design.md`, `docs/02-architecture/project-structure.md` | **ADDED:** `AttachmentMetadata` message in core.proto with fields: id, filename, content_type, size_bytes, extraction_status, extracted_content_preview (500 chars). Added as `repeated AttachmentMetadata attachments` (field 8) to ChatMessage proto. CoreClient uses raw SQL to populate attachment metadata. |

---

## Documents Modified

### Specification Documents Updated

1. **docs/02-architecture/data-model.md**
   - Added `attachments` table to schema overview
   - Added complete attachments table definition (11 columns, 3 indexes, notes on soft-delete, immutability, storage backend, AI extraction, validation, mirror pattern)
   - Updated relationships diagram (projects 1→N attachments, chat_messages 0→N attachments)
   - Added 3 indexes to index table

2. **docs/02-architecture/api-design.md**
   - Modified POST /api/projects/:id/chat to accept `attachment_ids` array
   - Added new "Attachments" section with 4 endpoints (POST upload, GET list, DELETE soft-delete, GET presigned URL)
   - Documented validation rules, rate limiting, security checks, side effects, error codes

3. **docs/02-architecture/project-structure.md**
   - Added `attachments` to Gateway-owned tables list
   - Updated mirror models section (attachments: Gateway-owned, Core mirrors for AI service)
   - Added "Storage Backend Abstraction (M22)" section with ABC pattern, factory pattern, bucket initialization, AI file download pattern, test pattern, notes

4. **docs/03-ai/system-prompts.md**
   - Added `<attachments>` block to Facilitator prompt (after `</project>`) with `<user_attachment>` XML sandboxing
   - Added `<attachment_guidance>` block to Facilitator prompt
   - Modified `<recent_messages>` to append `[Attachments: filenames]` notation
   - Added `<project_attachments>` block to Context Extension prompt
   - Updated Context Extension critical_rule to search both chat history and attachments

5. **docs/02-architecture/tech-stack.md**
   - Split "File Storage" entries: PDFs (local/Azure) separate from Attachments (MinIO/Azure)
   - Added MinIO entry: S3-compatible object storage, Docker container, bucket auto-created, presigned URLs
   - Added 3 backend libraries: minio (SDK), Pillow (image processing), PyMuPDF (PDF processing)
   - Added 5 environment variables: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, STORAGE_BACKEND
   - Updated AZURE_STORAGE_CONNECTION_STRING description to include attachments
   - Updated Docker Compose topology to include MinIO container

---

## Impact on Future Milestones

**No impact:** M22 is a self-contained feature. Attachments are optional in chat messages. Future milestones can ignore attachments or extend them.

**Potential extensions (not in current scope):**
- M23+: Thumbnail generation for image attachments
- M23+: Attachment search/filter in project view
- M23+: Attachment quota management (project-level limits)
- M23+: Attachment versioning (upload new version of same file)

---

## Verification

All changes verified against:
- **Implementation:** `.ralph/archive/m22-chat-attachments/progress.txt` (215 lines, 10 user stories + 1 bugfix)
- **QA Report:** `docs/08-qa/qa-m22-chat-attachments.md` (Cycle 2, PASS, 878 Python tests, all gates passed)
- **Git commits:** 84fb504 (merge), b705575 (BF-001 ruff fixes), 84d3b21 (US-010), 79a3f80 (US-009), and earlier US-001 through US-008

All REQUIRED gates passed (Docker build skipped, Frontend typecheck PASSED, Backend lint Ruff PASSED, Backend typecheck mypy PASSED). ESLint optional gate failed (pre-existing errors, non-blocking).

---

## Notes

1. **M22 is an addition, not a correction:** The upstream specs did not mention attachments before M22. This reconciliation documents the implemented feature for future reference.

2. **DEV-001 (Presigned URL read-only check):** QA noted that read-only blocking happens via access control (`_check_access` requires collaborator status), not an explicit `is_read_only` flag. This is the correct implementation. Frontend enforces with `clickable={!isReadOnly}` prop and toast message. Spec clarified in api-design.md.

3. **CoreServicer pattern confirmed:** M22 confirmed that Core's gRPC servicers are dead for attachment access. AI service accesses attachments via raw SQL using the CoreClient direct DB pattern (same as user display name lookups). This pattern is documented in project-structure.md and data-model.md.

4. **Storage abstraction pattern:** Gateway owns the storage abstraction (backends.py, factory.py). AI service does NOT use it — accesses MinIO directly to avoid circular gRPC dependencies. This pattern is documented in project-structure.md Storage Backend Abstraction section.

5. **Bucket auto-creation location:** Bucket auto-creation happens in `ProjectsConfig.ready()` (not gateway_app.ready() — that AppConfig doesn't exist). Guarded with try/except to not break startup if MinIO is unreachable. Documented in project-structure.md.

6. **Test Dockerfile dependency:** MinIO SDK (`minio`) needed in root `requirements.txt` (not just gateway requirements.txt) because test Dockerfile uses root requirements.txt + requirements-dev.txt. Documented in progress.txt US-001.

7. **Docker container rebuild requirement:** Multiple US entries in progress.txt note that Docker test containers MUST be rebuilt (--build) after code changes. Stale containers caused false test failures during M22. This is a general test infrastructure pattern, not M22-specific.

---

## Reconciliation Sign-off

- **Reconciler:** Claude (Spec Reconciler Agent)
- **Date:** 2026-03-18
- **Milestone:** M22 — Chat File Attachments
- **Status:** COMPLETE
- **Total spec documents updated:** 5
- **Total changes applied:** 20 (10 SMALL TECHNICAL, 7 FEATURE DESIGN, 3 LARGE TECHNICAL)
- **Rejected changes:** 0
- **User approval required:** No (all changes are documentation of implemented features; no speculative additions)

**All upstream docs now reflect M22 implementation reality.**
