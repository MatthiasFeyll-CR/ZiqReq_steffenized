# Attachment System V2 — Implementation Plan

> **For:** Fresh Claude Opus 4.6 session with clean context window
> **Date:** 2026-03-18
> **Prerequisite:** Read `CLAUDE.md` in project root — you are an orchestrator that delegates to subagents

---

## Table of Contents

1. [Overview](#1-overview)
2. [Task Groups](#2-task-groups)
3. [Task Group A: Backend — Orphan Cleanup & Storage Cascade](#3-task-group-a)
4. [Task Group B: Backend — Soft-Delete Lift, Restore & Admin APIs](#4-task-group-b)
5. [Task Group C: Backend — PDF Attachment Append](#5-task-group-c)
6. [Task Group D: Frontend — Admin Attachments Tab](#6-task-group-d)
7. [Task Group E: Frontend — Project Attachments Modal + Chat Integration](#7-task-group-e)
8. [Task Group F: Frontend — Strukturieren Tab Redesign](#8-task-group-f)
9. [Task Group G: Admin Parameters Seeding](#9-task-group-g)
10. [Task Group H: Testing & Verification](#10-task-group-h)
11. [File Reference Index](#11-file-reference-index)
12. [UI/UX Specifications](#12-uiux-specifications)

---

## 1. Overview

This plan extends the M22 attachment system with:

1. **Orphaned file cleanup** — Celery beat task deletes unlinked uploads after configurable TTL (default 96h)
2. **Storage cascade on hard delete** — MinIO files cleaned before project CASCADE delete
3. **Soft-delete lifted for message-linked attachments** — Users can now soft-delete any attachment
4. **Restore mechanism** — Soft-deleted attachments can be restored within TTL window
5. **Admin Attachments tab** — Full CRUD, search, pagination (35/page), stats, filter (active/deleted/all)
6. **Project Attachments modal** — View/delete/restore attachments per project, accessible to collaborators
7. **Chat integration** — Deleted attachments render red/crossed-out with restore prompt
8. **Strukturieren tab redesign** — Progressive disclosure layout with attachment PDF selection
9. **PDF attachment append** — Selected attachments appended to BRD PDF via PDF service
10. **Admin parameters** — All hardcoded attachment values become configurable

### Execution Order

```
A (backend cleanup) ──┐
B (backend APIs)   ───┼──> G (parameters) ──> D (admin tab)  ──┐
C (PDF service)    ───┘                   ──> E (modal+chat) ──┼──> H (testing)
                                          ──> F (strukturieren)┘
```

Groups A, B, C can run in parallel. G depends on A+B. D, E, F depend on G and their respective backend groups. H is final.

---

## 2. Task Groups

| Group | Scope | Estimated Complexity |
|-------|-------|---------------------|
| A | Backend: orphan cleanup + storage cascade | Medium |
| B | Backend: soft-delete lift, restore API, admin attachment APIs | Medium-High |
| C | Backend: PDF service attachment append | Medium |
| D | Frontend: Admin Attachments tab | Medium |
| E | Frontend: Project Attachments modal + chat changes | Medium-High |
| F | Frontend: Strukturieren tab redesign | Medium-High |
| G | Backend+Frontend: Admin parameter seeding | Low |
| H | Testing & E2E verification | Medium |

---

## 3. Task Group A: Backend — Orphan Cleanup & Storage Cascade

### Subagent Usage
- **Research:** `doc-researcher` — confirm no existing cleanup tasks beyond `soft_delete_cleanup`
- **After implementation:** `code-reviewer` + `security-review` on changed files
- **Tests:** `test-writer` for new Celery task, `infra` to run tests

### A1: Orphan Attachment Cleanup Task

**File:** `services/core/apps/projects/tasks.py`

Add a new Celery task `attachment_orphan_cleanup` that:

1. Reads `orphan_attachment_ttl_hours` parameter (default: 96) from `admin_parameters`
2. Queries attachments where:
   - `message_id IS NULL` (never linked to a message)
   - `deleted_at IS NULL` (not already soft-deleted)
   - `created_at < now() - TTL hours`
3. For each orphaned attachment:
   - Soft-delete it (`deleted_at = now()`)
   - Delete storage file from MinIO (best-effort)
4. Log count of cleaned attachments

**Important:** The core service uses an **unmanaged mirror** of the Attachment model (`services/core/apps/projects/models.py`). The attachment table is owned by gateway but shared via the same PostgreSQL database. The core task can read/write to it directly.

However, the core service does NOT have access to the MinIO storage backend (that lives in gateway). Two options:
- **Option 1 (recommended):** Move this task to the gateway service's Celery worker. Gateway already has a Celery app (`services/gateway/` — check if celery worker exists in docker-compose). If not, create a gateway celery task that the core beat scheduler dispatches.
- **Option 2:** Have the core task only soft-delete the DB records, and add a separate gateway task that periodically scans for soft-deleted attachments and cleans up their storage files.

Check `infra/docker/docker-compose.yml` for existing celery workers. The current setup has:
- `celery-worker` service (runs AI service tasks)
- `celery-beat` service (runs in core service)

**If gateway has no celery worker:** Create the cleanup as a management command in gateway that celery-beat in core dispatches via `send_task`, similar to how gateway dispatches `tasks.extract_attachment_content` to the AI service. OR add a gateway celery worker to docker-compose.

**Simpler approach:** Since the core service has direct DB access to the attachments table AND we need MinIO access, the cleanest solution is:
1. Core task soft-deletes orphaned attachment DB records (sets `deleted_at`)
2. A **second task** `attachment_storage_cleanup` runs periodically and deletes MinIO files for all attachments where `deleted_at IS NOT NULL` and `deleted_at < now() - 24h` (grace period for restores). This task lives in **gateway** and is dispatched by a gateway management command OR by extending the existing infrastructure.

Actually, looking at it more carefully: the simplest approach is to put BOTH tasks in the **gateway** service since gateway owns both the Attachment model AND the storage backend. Add a celery worker for gateway in docker-compose if one doesn't exist.

**Register in Celery Beat schedule:** Add to core's `settings/base.py` CELERY_BEAT_SCHEDULE (or wherever beat is configured):
```python
"attachment-orphan-cleanup": {
    "task": "projects.attachment_orphan_cleanup",
    "schedule": 3600,  # every hour
},
"attachment-storage-cleanup": {
    "task": "projects.attachment_storage_cleanup",
    "schedule": 3600,  # every hour
},
```

### A2: Storage Cleanup on Project Hard Delete

**File:** `services/core/apps/projects/tasks.py` (function `soft_delete_cleanup`, line 10-60)

Before the `expired_projects.delete()` call (line 54), add:

```python
# Collect attachment storage keys before CASCADE delete removes the records
from apps.projects.models import Attachment  # unmanaged mirror
attachment_keys = list(
    Attachment.objects.filter(project_id__in=project_ids).values_list("storage_key", flat=True)
)

# ... existing deletes ...
expired_projects.delete()

# Best-effort storage cleanup (after DB delete)
if attachment_keys:
    _cleanup_storage_files(attachment_keys)
```

For `_cleanup_storage_files`: Since the core service doesn't have the MinIO client, dispatch a cleanup task to gateway:
```python
def _cleanup_storage_files(storage_keys: list[str]) -> None:
    """Dispatch storage file deletion to gateway service."""
    try:
        from celery import Celery
        from django.conf import settings
        app = Celery("gateway", broker=settings.CELERY_BROKER_URL)
        app.send_task(
            "attachments.bulk_delete_storage",
            kwargs={"storage_keys": storage_keys},
            queue="gateway",
        )
    except Exception:
        logger.warning("Failed to dispatch storage cleanup for %d files", len(storage_keys))
```

And create the corresponding task in gateway that accepts a list of storage keys and deletes them from MinIO.

### A3: Permanent Deletion of Expired Soft-Deleted Attachments

Add to the `soft_delete_cleanup` task OR as a separate task:

Query attachments where:
- `deleted_at IS NOT NULL`
- `deleted_at < now() - orphan_attachment_ttl_hours`

Hard-delete these records AND their storage files.

This handles:
- User-deleted attachments past the restore window
- Orphan-cleanup-deleted attachments past the grace period

---

## 4. Task Group B: Backend — Soft-Delete Lift, Restore & Admin APIs

### Subagent Usage
- **Research:** `impl-planner` with this section's requirements
- **After implementation:** `code-reviewer` + `security-review`
- **Tests:** `test-writer`, `infra` to execute

### B1: Lift Immutability Rule on Soft Delete

**File:** `services/gateway/apps/attachments/views.py` (lines 316-321)

Remove the immutability check that blocks deletion of message-linked attachments:

```python
# REMOVE these lines (316-321):
# if attachment.message_id is not None:
#     return Response(
#         {"error": "IMMUTABLE", "message": "Cannot delete attachment already sent with message"},
#         status=status.HTTP_400_BAD_REQUEST,
#     )
```

Also **remove the immediate storage deletion** on soft-delete (lines 327-332). Storage cleanup is now handled by the periodic cleanup task (A3). This enables the restore window.

```python
# REMOVE these lines:
# try:
#     backend = _get_storage_backend()
#     backend.delete_file(attachment.storage_key)
# except Exception:
#     logger.warning(...)
```

Update access check: currently only uploader or owner can delete. Expand to include **any collaborator**:

```python
# Line 310: Change access check
if not _check_access(user, project):
    return Response(
        {"error": "ACCESS_DENIED", "message": "Only collaborators can delete attachments"},
        status=status.HTTP_403_FORBIDDEN,
    )
```

### B2: Restore Endpoint

**File:** `services/gateway/apps/attachments/views.py`

Add new endpoint: `POST /api/projects/:id/attachments/:id/restore/`

```python
@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def attachment_restore(request, project_id, attachment_id):
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    if not _check_access(user, project):
        return Response({"error": "ACCESS_DENIED"}, status=403)

    try:
        attachment = Attachment.objects.get(
            id=attachment_id, project_id=project.id, deleted_at__isnull=False
        )
    except Attachment.DoesNotExist:
        return Response({"error": "NOT_FOUND"}, status=404)

    # Check if within restore window
    from apps.admin_config.services import get_parameter
    ttl_hours = get_parameter("orphan_attachment_ttl_hours", default=96, cast=int)
    deadline = attachment.deleted_at + timedelta(hours=ttl_hours)
    if timezone.now() > deadline:
        return Response(
            {"error": "EXPIRED", "message": "Restore window has expired"},
            status=400,
        )

    # Check storage file still exists
    backend = _get_storage_backend()
    if not backend.file_exists(attachment.storage_key):
        return Response(
            {"error": "FILE_GONE", "message": "Storage file no longer exists"},
            status=410,
        )

    attachment.deleted_at = None
    attachment.save(update_fields=["deleted_at"])
    return Response(AttachmentResponseSerializer(attachment).data)
```

**File:** `services/gateway/apps/attachments/urls.py`

Add: `path("<str:attachment_id>/restore/", views.attachment_restore)`

### B3: List Attachments — Include Soft-Deleted

**File:** `services/gateway/apps/attachments/views.py` (function `_list_attachments`, line 256-276)

Modify to accept query param `include_deleted=true`:

```python
def _list_attachments(request, project_id):
    # ... auth checks ...
    include_deleted = request.query_params.get("include_deleted", "").lower() == "true"

    qs = Attachment.objects.filter(project_id=project.id)
    if not include_deleted:
        qs = qs.filter(deleted_at__isnull=True)
    attachments = qs.order_by("-created_at")

    serializer = AttachmentResponseSerializer(attachments, many=True)
    return Response(serializer.data)
```

**File:** `services/gateway/apps/attachments/serializers.py`

Add `deleted_at` field to the serializer:

```python
class AttachmentResponseSerializer(serializers.Serializer):
    # ... existing fields ...
    deleted_at = serializers.DateTimeField(allow_null=True)
```

### B4: Admin Attachments API

**File:** `services/gateway/apps/admin_config/views.py`

Add new admin endpoint: `GET /api/admin/attachments`

```python
@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def admin_attachments_list(request):
    denied = _require_admin(request)
    if denied:
        return denied

    from apps.projects.models import Attachment, Project

    filter_param = request.query_params.get("filter", "all")  # active, deleted, all
    search_param = request.query_params.get("search", "")
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(int(request.query_params.get("page_size", 35)), 100)

    qs = Attachment.objects.select_related("project").all()

    if filter_param == "active":
        qs = qs.filter(deleted_at__isnull=True)
    elif filter_param == "deleted":
        qs = qs.filter(deleted_at__isnull=False)

    if search_param:
        qs = qs.filter(Q(filename__icontains=search_param))

    qs = qs.order_by("-created_at")

    total_count = qs.count()
    offset = (page - 1) * page_size
    attachments = list(qs[offset:offset + page_size])

    # Get project names
    project_ids = {a.project_id for a in attachments}
    projects = Project.objects.filter(id__in=project_ids)
    project_map = {p.id: p for p in projects}

    # Stats (unfiltered)
    from django.db.models import Sum, Count
    stats = Attachment.objects.aggregate(
        total_size=Sum("size_bytes"),
        total_count=Count("id"),
    )

    results = []
    for att in attachments:
        proj = project_map.get(att.project_id)
        results.append({
            "id": str(att.id),
            "filename": att.filename,
            "content_type": att.content_type,
            "size_bytes": att.size_bytes,
            "extraction_status": att.extraction_status,
            "created_at": att.created_at.isoformat(),
            "deleted_at": att.deleted_at.isoformat() if att.deleted_at else None,
            "message_id": str(att.message_id) if att.message_id else None,
            "project": {
                "id": str(att.project_id),
                "title": proj.title if proj else "Unknown",
            },
        })

    return Response({
        "results": results,
        "count": total_count,
        "next": page + 1 if offset + page_size < total_count else None,
        "previous": page - 1 if page > 1 else None,
        "stats": {
            "total_size_bytes": stats["total_size"] or 0,
            "total_count": stats["total_count"] or 0,
        },
    })
```

Add admin delete/restore endpoints:
- `DELETE /api/admin/attachments/:id` — admin hard-delete (removes DB record + storage file)
- `POST /api/admin/attachments/:id/restore/` — admin restore (same as user restore but admin-only)

**File:** `services/gateway/apps/admin_config/urls.py`

Add URL patterns for the new admin attachment endpoints.

### B5: Attachment Download for Soft-Deleted (Admin)

Modify `attachment_url` and `attachment_download` views to allow access to soft-deleted attachments if the user is an admin. Currently they filter `deleted_at__isnull=True`.

---

## 5. Task Group C: Backend — PDF Attachment Append

### Subagent Usage
- **Research:** `impl-planner` + `doc-researcher` for PDF service architecture
- **After implementation:** `code-reviewer`
- **Tests:** `test-writer`, `infra` to execute

### C1: Proto Update

**File:** `proto/pdf.proto`

Add attachment data to the PDF generation request:

```protobuf
message PdfAttachment {
  string filename = 1;
  string content_type = 2;
  bytes file_data = 3;
}

message PdfGenerationRequest {
  string project_id = 1;
  string project_type = 2;
  string title = 3;
  string short_description = 4;
  string structure_json = 5;
  string generated_date = 6;
  repeated PdfAttachment attachments = 7;  // NEW
}
```

After changing the proto, regenerate Python stubs:
```bash
python -m grpc_tools.protoc -I proto --python_out=proto --grpc_python_out=proto proto/pdf.proto
```

### C2: PDF Builder — Append Attachments

**File:** `services/pdf/generator/builder.py`

Add function to create an "Attachments" appendix section in the HTML:

```python
def _render_attachments_section(attachment_names: list[str]) -> str:
    """Render an Attachments appendix listing attached file names."""
    if not attachment_names:
        return ""
    items = "\n".join(f"<li>{html.escape(name)}</li>" for name in attachment_names)
    return f"""<section class="attachments-section">
  <h2>Appendix: Attachments</h2>
  <p>The following files are appended to this document:</p>
  <ol>{items}</ol>
</section>"""
```

Add this section to `build_html()` before the closing `</main>` tag.

### C3: PDF Renderer — Merge Attachment Files

**File:** `services/pdf/generator/renderer.py`

After rendering the HTML to PDF bytes, merge attachment PDFs:

```python
import fitz  # PyMuPDF

def merge_attachments(brd_pdf_bytes: bytes, attachments: list[dict]) -> bytes:
    """Merge attachment files into the BRD PDF.

    Each attachment dict has: filename, content_type, file_data (bytes).
    PDFs are appended page-by-page. Images are inserted as full pages.
    """
    doc = fitz.open(stream=brd_pdf_bytes, filetype="pdf")

    for att in attachments:
        if att["content_type"] == "application/pdf":
            att_doc = fitz.open(stream=att["file_data"], filetype="pdf")
            doc.insert_pdf(att_doc)
            att_doc.close()
        elif att["content_type"].startswith("image/"):
            # Create a new page with the image
            img_rect = fitz.Rect(36, 36, 559, 806)  # A4 with margins
            page = doc.new_page(width=595, height=842)
            page.insert_image(img_rect, stream=att["file_data"])

    output = doc.tobytes()
    doc.close()
    return output
```

### C4: PDF Servicer — Pass Attachments Through

**File:** `services/pdf/grpc_server/servicers/pdf_servicer.py`

Update `GeneratePdf` to accept attachments and call merge:

```python
def GeneratePdf(self, request, context):
    # ... existing HTML generation ...
    pdf_bytes = render_pdf(html_string)

    # Merge attachments if any
    if request.attachments:
        attachments = [
            {
                "filename": att.filename,
                "content_type": att.content_type,
                "file_data": att.file_data,
            }
            for att in request.attachments
        ]
        pdf_bytes = merge_attachments(pdf_bytes, attachments)

    # ... return response ...
```

### C5: Gateway BRD Views — Fetch & Send Attachments

Find the gateway views that call the PDF service gRPC (search for `GeneratePdf` or `PdfGenerationRequest` in gateway). These need to:

1. Accept `attachment_ids` from the frontend (list of UUIDs to include)
2. Fetch the selected attachments' storage files from MinIO
3. Include them in the gRPC request to the PDF service

**Search for:** `services/gateway/apps/brd/` — the BRD draft/version views that trigger PDF generation.

The frontend will send `attachment_ids` when requesting PDF generation. The gateway fetches each file from MinIO and passes the bytes to the PDF service.

---

## 6. Task Group D: Frontend — Admin Attachments Tab

### Subagent Usage
- **Research:** Read existing admin tabs (ProjectsTab, MonitoringTab) for patterns
- **UI/UX:** `ui-ux` agent for component review
- **After implementation:** `code-reviewer`

### D1: Admin API Client

**File:** `frontend/src/api/admin.ts`

Add:

```typescript
export interface AdminAttachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  extraction_status: string;
  created_at: string;
  deleted_at: string | null;
  message_id: string | null;
  project: { id: string; title: string };
}

export interface AdminAttachmentsResponse {
  results: AdminAttachment[];
  count: number;
  next: number | null;
  previous: number | null;
  stats: { total_size_bytes: number; total_count: number };
}

export async function fetchAdminAttachments(params?: {
  page?: number;
  page_size?: number;
  filter?: "active" | "deleted" | "all";
  search?: string;
}): Promise<AdminAttachmentsResponse> { /* ... */ }

export async function deleteAdminAttachment(id: string): Promise<void> { /* ... */ }

export async function restoreAdminAttachment(id: string): Promise<void> { /* ... */ }
```

### D2: AttachmentsTab Component

**File:** `frontend/src/features/admin/AttachmentsTab.tsx` (new file)

Follow the exact patterns from `ProjectsTab.tsx`:

**Layout:**
```
+--Stats Bar (2 KPICards)--------------------------------------+
| [Total Storage: 2.3 GB]    [Total Files: 47]                |
+--------------------------------------------------------------+
| [Search input...]                     [Filter: All v]        |
+--------------------------------------------------------------+
| Attachment list items (35 per page)                          |
| Each item:                                                   |
|   [FileIcon] filename.pdf    PDF | 1.2 MB                   |
|   Project Alpha | Uploaded Mar 18, 2026       [Open] [Del]  |
+--------------------------------------------------------------+
| [< Back]              1 / 3                     [Next >]     |
+--------------------------------------------------------------+
```

**Key patterns to follow (copy from ProjectsTab):**
- Search: 300ms debounce with `useEffect` + `setTimeout`
- Pagination: `page` state, `PAGE_SIZE = 35`, prev/next buttons
- Filter: Radix Select with options "All", "Active", "Deleted"
- Loading state: centered "Loading..." text
- Empty state: centered icon + message

**Stats bar:** Use existing `KPICard` component from `frontend/src/components/admin/KPICard.tsx`:
```tsx
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 mb-6">
  <KPICard label={t("admin.attachments.totalStorage")} value={formatFileSize(stats.total_size_bytes)} />
  <KPICard label={t("admin.attachments.totalFiles")} value={String(stats.total_count)} />
</div>
```

**File size formatter:** Reuse from `AttachmentBox.tsx` (line 18-22):
```typescript
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}
```

**List item styling:**
- Active: normal card with border
- Deleted: `opacity-60`, filename `line-through`, red "Deleted" badge
- Project name: `<Link to={/project/${projectId}}>` with `hover:underline`
- Open icon: Lucide `ExternalLink`, opens download URL in new tab
- Delete icon: Lucide `Trash2`, shows confirmation dialog before action
- Restore button: `<Button variant="outline" size="sm">Restore</Button>` (for deleted items)

**File type icons** (Lucide):
- PDF: `FileText`
- Images (png, jpeg, webp): `Image` (from lucide-react, already imported in AttachmentBox)
- Default: `File`

### D3: Register Tab in Admin Panel

**File:** `frontend/src/pages/admin-panel.tsx`

1. Add import: `import { AttachmentsTab } from "@/features/admin/AttachmentsTab";`
2. Add `import { Paperclip } from "lucide-react";`
3. Add `"attachments"` to `VALID_TABS` array (line 14)
4. Add new `TabsTrigger` with Paperclip icon after the "projects" trigger (copy exact className pattern from existing triggers)
5. Add new `TabsContent` with `<AttachmentsTab />`

### D4: Translations

**Files:** `frontend/src/i18n/locales/en.json` and `de.json`

Add under `"admin"` key:
```json
"attachments": "Attachments",
"attachments.totalStorage": "Total Storage",
"attachments.totalFiles": "Total Files",
"attachments.searchPlaceholder": "Search by filename...",
"attachments.filterAll": "All",
"attachments.filterActive": "Active",
"attachments.filterDeleted": "Deleted",
"attachments.noResults": "No attachments found",
"attachments.deleteConfirm": "Delete this attachment permanently?",
"attachments.deleteSuccess": "Attachment deleted",
"attachments.restoreSuccess": "Attachment restored",
"attachments.uploaded": "Uploaded"
```

German translations:
```json
"attachments": "Anhaenge",
"attachments.totalStorage": "Gesamtspeicher",
"attachments.totalFiles": "Gesamtanzahl Dateien",
"attachments.searchPlaceholder": "Nach Dateinamen suchen...",
"attachments.filterAll": "Alle",
"attachments.filterActive": "Aktiv",
"attachments.filterDeleted": "Geloescht",
"attachments.noResults": "Keine Anhaenge gefunden",
"attachments.deleteConfirm": "Diesen Anhang endgueltig loeschen?",
"attachments.deleteSuccess": "Anhang geloescht",
"attachments.restoreSuccess": "Anhang wiederhergestellt",
"attachments.uploaded": "Hochgeladen"
```

---

## 7. Task Group E: Frontend — Project Attachments Modal + Chat Integration

### Subagent Usage
- **UI/UX:** `ui-ux` agent for modal design review
- **After implementation:** `code-reviewer`

### E1: Attachment API Extensions

**File:** `frontend/src/api/attachments.ts`

Add:

```typescript
export async function restoreAttachment(projectId: string, attachmentId: string): Promise<Attachment> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachmentId}/restore/`;
  const res = await authFetch(url, { method: "POST", credentials: "include" });
  if (!res.ok) { /* error handling */ }
  return res.json();
}

export async function listAttachmentsIncludeDeleted(projectId: string): Promise<Attachment[]> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/?include_deleted=true`;
  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) { /* error handling */ }
  return res.json();
}
```

Update the `Attachment` interface to include `deleted_at`:
```typescript
export interface Attachment {
  // ... existing fields ...
  deleted_at: string | null;
}
```

### E2: AttachmentsModal Component

**File:** `frontend/src/components/workspace/AttachmentsModal.tsx` (new file)

**Structure:**
```tsx
<Dialog open={open} onOpenChange={onOpenChange}>
  <DialogContent className="max-w-2xl">
    <DialogHeader>
      <DialogTitle>{t("attachments.modalTitle")}</DialogTitle>
    </DialogHeader>

    {/* Active Attachments */}
    <div>
      <h4 className="text-sm font-medium mb-3">
        {t("attachments.active")} ({activeAttachments.length})
      </h4>
      {activeAttachments.length === 0 ? (
        <EmptyState icon={Paperclip} message={t("attachments.noActive")} />
      ) : (
        <div className="space-y-2">
          {activeAttachments.map(att => (
            <AttachmentListItem
              key={att.id}
              attachment={att}
              onDelete={handleDelete}
              onOpen={handleOpen}
            />
          ))}
        </div>
      )}
    </div>

    <Separator />

    {/* Deleted Attachments */}
    <div>
      <h4 className="text-sm font-medium mb-2">
        {t("attachments.deleted")} ({deletedAttachments.length})
      </h4>
      <div className="bg-muted/30 border border-border rounded-md p-3 mb-3 flex items-start gap-2">
        <Info className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
        <p className="text-sm text-muted-foreground">
          {t("attachments.deleteNote", { hours: ttlHours })}
        </p>
      </div>
      {deletedAttachments.length === 0 ? (
        <EmptyState icon={Check} message={t("attachments.noDeleted")} />
      ) : (
        <div className="space-y-2">
          {deletedAttachments.map(att => (
            <DeletedAttachmentListItem
              key={att.id}
              attachment={att}
              ttlHours={ttlHours}
              onRestore={handleRestore}
            />
          ))}
        </div>
      )}
    </div>
  </DialogContent>
</Dialog>
```

**List item for active attachments:**
- Layout: `flex items-center justify-between`
- Left: filename + "Attached [date] [time]" (sorted newest first)
- Right: `ExternalLink` icon button + `Trash2` icon button
- Delete shows confirmation dialog

**List item for deleted attachments:**
- Same layout but `opacity-60`, filename `line-through text-muted-foreground`
- Shows countdown: "Permanently deleted in Xh Ym"
- Right: `<Button variant="outline" size="sm">Restore</Button>`
- Countdown calculation: `ttlHours - hoursSince(deleted_at)`

### E3: Attachments Button in Header

**File:** `frontend/src/components/workspace/WorkspaceHeader.tsx`

Add between the "Manage" button (line 284-294) and the "Comments" button (line 297):

```tsx
{/* Attachments button — only when project has attachments and user is not read-only */}
{!readOnly && attachmentCount > 0 && (
  <Button
    variant="outline"
    size="sm"
    onClick={() => setAttachmentsModalOpen(true)}
    data-testid="attachments-button"
  >
    <Paperclip className="mr-1 h-4 w-4" />
    {t("workspace.attachments", "Attachments")}
    <span className="ml-1 text-xs text-muted-foreground">({attachmentCount})</span>
  </Button>
)}
```

**State additions:**
- `const [attachmentsModalOpen, setAttachmentsModalOpen] = useState(false);`
- Fetch attachment count on mount (or receive as prop from parent)

**Props:** Add `attachmentCount?: number` to `WorkspaceHeaderProps`. The parent (`ProjectWorkspace/index.tsx`) should fetch this.

Add the modal at the bottom of the component (alongside CollaboratorModal and CommentsPanel):
```tsx
<AttachmentsModal
  projectId={project.id}
  open={attachmentsModalOpen}
  onOpenChange={setAttachmentsModalOpen}
/>
```

### E4: Chat AttachmentBox — Deleted State

**File:** `frontend/src/components/chat/AttachmentBox.tsx`

Add handling for soft-deleted attachments:

```tsx
const isDeleted = !!attachment.deleted_at;

// Update the container className:
className={cn(
  "relative group flex items-center gap-2 rounded-md border px-2 py-1.5 text-sm max-w-[200px]",
  isDeleted
    ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/30 cursor-pointer"
    : clickable
      ? "border-border bg-muted/50 cursor-pointer hover:bg-muted"
      : "border-border bg-muted/50 cursor-not-allowed opacity-80",
)}

// Update the filename display:
<p className={cn("truncate text-xs font-medium", isDeleted && "line-through text-red-700 dark:text-red-400")}>
  {attachment.filename}
</p>

// Update the click handler:
const handleClick = useCallback(() => {
  if (isDeleted) {
    toast.info(
      t("attachment.deletedClickPrompt", "This attachment has been deleted. Restore it in the attachment modal. Permanently deleted in {{hours}} hours.", {
        hours: hoursUntilPermanentDelete,
      })
    );
    return;
  }
  // ... existing click logic ...
}, [isDeleted, ...]);
```

The `hoursUntilPermanentDelete` calculation needs the `orphan_attachment_ttl_hours` parameter. This can be:
- Passed as a prop from a parent that fetches admin parameters, OR
- Fetched once and cached in a React context, OR
- Included in the attachment list API response as metadata

**Simplest approach:** Include it in the project attachments list response as a top-level field, or fetch it once from `GET /api/admin/parameters` (but that requires admin role). Better: add a public endpoint `GET /api/config/attachment-ttl` that returns just the TTL value, or include it in the `listAttachments` response.

### E5: WebSocket — Attachment Deleted/Restored Events

When an attachment is soft-deleted or restored, broadcast a WebSocket event so other users see the change in real-time.

**Backend:** In the delete and restore views, publish events via the existing event system:
```python
from apps.events.publisher import publish_event
publish_event("attachment.deleted", {"project_id": str(project.id), "attachment_id": str(attachment.id)})
publish_event("attachment.restored", {"project_id": str(project.id), "attachment_id": str(attachment.id)})
```

**Frontend:** Listen for `ws:attachment_deleted` and `ws:attachment_restored` events to refresh attachment lists.

---

## 8. Task Group F: Frontend — Strukturieren Tab Redesign

### Subagent Usage
- **UI/UX:** `ui-ux` agent for design validation before and after implementation
- **After implementation:** `code-reviewer`, `ui-ux` pre-delivery checklist

### F1: Progressive Disclosure Layout

**File:** `frontend/src/pages/ProjectWorkspace/StructureStepView.tsx`

Redesign to this structure:

```
+==================================================================+
| TOOLBAR (sticky): [Generate] [Allow gaps: toggle] [X/Y ready]   |
+==================================================================+
| LEFT (flex-[3])              | RIGHT (flex-[2])                  |
|   RequirementsPanel          |   PDFPreviewPanel                 |
|   (no lock controls here)    |                                   |
+------------------------------+-----------------------------------+
| COLLAPSIBLE: Advanced Options (collapsed by default)             |
|   LEFT: Item Locks (chips)   | RIGHT: Attachments for PDF       |
|                               |   [x] Select All (8 selected)   |
|                               |   [x] proposal.pdf  (2.3 MB)    |
|                               |   [x] budget.xlsx   (450 KB)    |
+==================================================================+
| COLLAPSIBLE: Submit for Review (auto-expands when content ready) |
|   [CheckCircle] Ready to submit?                                 |
|   Message textarea + reviewer assignment + submit button         |
+==================================================================+
```

**Key changes from current layout:**
1. **Move lock controls** from bottom of RequirementsPanel into the "Advanced Options" collapsible
2. **Add AttachmentSelector** in the right column of "Advanced Options"
3. **Wrap submit section** in a collapsible that auto-expands when `hasContent` is true
4. **Collapsible headers** show summary counts: "2 locked | 8 attachments selected"

### F2: New Components

**File:** `frontend/src/components/workspace/CollapsibleSection.tsx` (new)

Generic collapsible section wrapper:

```tsx
interface CollapsibleSectionProps {
  title: string;
  summary?: string;
  defaultExpanded?: boolean;
  expanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  children: React.ReactNode;
  variant?: "default" | "success";  // success = green tint for submit
}
```

Use Radix `Collapsible` or just state + conditional render with smooth height animation.

**File:** `frontend/src/components/workspace/AttachmentSelector.tsx` (new)

```tsx
interface AttachmentSelectorProps {
  projectId: string;
  selectedIds: Set<string>;
  onSelectionChange: (ids: Set<string>) => void;
}
```

- Fetches active attachments via `listAttachments(projectId)`
- Displays checkbox list with filename, type icon, size
- "Select All" / "Deselect All" toggle link
- **Default: all selected** (user answers confirm this)
- Max height 200px with `overflow-y-auto` scroll
- Empty state if no attachments

### F3: State Management Updates

In `StructureStepView`:

```tsx
// New state
const [advancedExpanded, setAdvancedExpanded] = useState(false);
const [submitExpanded, setSubmitExpanded] = useState(false);
const [selectedAttachmentIds, setSelectedAttachmentIds] = useState<Set<string>>(new Set());

// Auto-expand submit when content appears
const hasAutoExpandedSubmit = useRef(false);
useEffect(() => {
  if (hasContent && !hasAutoExpandedSubmit.current) {
    setSubmitExpanded(true);
    hasAutoExpandedSubmit.current = true;
  }
}, [hasContent]);

// Initialize all attachments as selected
useEffect(() => {
  listAttachments(projectId).then(attachments => {
    setSelectedAttachmentIds(new Set(attachments.map(a => a.id)));
  });
}, [projectId]);
```

### F4: Pass Selected Attachments to PDF Generation

When the user triggers PDF generation or preview, include `selectedAttachmentIds` in the API call. This requires:

1. Updating the frontend API call for BRD generation to include `attachment_ids`
2. The gateway BRD views to accept and forward these IDs to the PDF service (see Task Group C)

Find the relevant API functions in `frontend/src/api/projects.ts` — look for `fetchBrdPdf`, `fetchBrdPreviewPdf`, or similar.

---

## 9. Task Group G: Admin Parameters Seeding

### Subagent Usage
- **After implementation:** `code-reviewer`

### G1: New Migration for Attachment Parameters

**File:** `services/gateway/apps/admin_config/migrations/0002_attachment_parameters.py` (new)

Create a new migration that seeds these parameters:

```python
NEW_PARAMETERS = [
    ("max_attachment_size_mb", "100", "100", "Maximum file size per attachment in megabytes", "integer", "Attachments"),
    ("max_attachments_per_project", "10", "10", "Maximum active attachments per project", "integer", "Attachments"),
    ("max_attachments_per_message", "3", "3", "Maximum attachments per chat message", "integer", "Attachments"),
    ("attachment_upload_rate_limit", "10", "10", "Maximum uploads per minute per user", "integer", "Attachments"),
    ("attachment_presigned_url_ttl", "900", "900", "Presigned URL time-to-live in seconds", "integer", "Attachments"),
    ("attachment_extraction_max_chars", "16000", "16000", "Maximum characters for AI text extraction per attachment", "integer", "Attachments"),
    ("orphan_attachment_ttl_hours", "96", "96", "Hours before orphaned/deleted attachments are permanently removed", "integer", "Attachments"),
    ("allowed_attachment_types", "image/png,image/jpeg,image/webp,application/pdf", "image/png,image/jpeg,image/webp,application/pdf", "Comma-separated list of allowed MIME types for attachments", "string", "Attachments"),
]
```

Use the same `INSERT ... ON CONFLICT DO NOTHING` pattern from the existing migration.

### G2: Read Parameters in Backend Code

Replace all hardcoded values with parameter lookups:

**File:** `services/gateway/apps/attachments/views.py`

Replace:
- `MAX_FILE_SIZE = 104857600` -> read `max_attachment_size_mb` * 1024 * 1024
- `MAX_ATTACHMENTS_PER_PROJECT = 10` -> read `max_attachments_per_project`
- `RATE_LIMIT_UPLOADS_PER_MINUTE = 10` -> read `attachment_upload_rate_limit`
- `PRESIGNED_URL_TTL = 900` -> read `attachment_presigned_url_ttl`
- `ALLOWED_CONTENT_TYPES` set -> read `allowed_attachment_types` and split by comma

Use `get_parameter()` from `apps.admin_config.services`.

**File:** `services/gateway/apps/chat/views.py` or serializers

Replace max attachments per message (currently `max_length=3` in serializer) with parameter lookup.

**File:** `services/ai/tasks/extract_attachment.py`

Replace hardcoded 16000 char truncation with `attachment_extraction_max_chars` parameter.

### G3: Core Service Migration

The admin_parameters table is owned by core service. If the new migration is in gateway, it needs to match. Check if core also has a migration that creates the table. If so, also add the new parameters to core's migration OR rely on gateway's migration to INSERT.

Looking at the existing code: the table is created by gateway migration 0001 with raw SQL. Core service accesses it as an unmanaged model. So **add the new parameters in a new gateway migration** (0002) using the same `INSERT ON CONFLICT DO NOTHING` pattern.

---

## 10. Task Group H: Testing & Verification

### Subagent Usage
- **Test writing:** `test-writer` for all new code
- **Test execution:** `infra` to set up environment and run tests
- **E2E testing:** `e2e-test` for browser verification
- **Security review:** `security-review` on all backend changes

### H1: Backend Unit Tests

Tests to write:

1. **Orphan cleanup task** — mock DB, verify correct filtering and soft-delete
2. **Storage cascade** — verify storage keys collected before project delete
3. **Restore endpoint** — happy path, expired TTL, file gone, access denied
4. **Admin attachments list** — search, filter, pagination, stats
5. **Soft-delete without immutability** — verify message-linked attachments can be deleted
6. **Parameter-driven limits** — verify changed parameters affect behavior

### H2: Frontend Unit Tests

Tests to write:

1. **AttachmentsTab** — renders stats, search, filter, pagination, delete/restore actions
2. **AttachmentsModal** — renders active/deleted sections, delete/restore, countdown
3. **AttachmentBox** — deleted state renders red/crossed-out, click shows toast
4. **AttachmentSelector** — select all, deselect all, individual toggle
5. **StructureStepView** — collapsible sections expand/collapse, attachment selection state

### H3: E2E Tests

Use `e2e-test` agent with Playwright MCP:

1. **Admin Attachments tab:**
   - Navigate to /admin#attachments
   - Verify stats cards, search, filter
   - Click attachment open icon -> new tab
   - Delete and restore an attachment

2. **Project Attachments modal:**
   - Create project, upload attachment via chat
   - Click Attachments button in header
   - Verify modal shows attachment
   - Delete attachment, verify chat box turns red
   - Restore attachment, verify chat box returns to normal

3. **Strukturieren tab:**
   - Navigate to Structure tab
   - Verify Advanced Options collapsible
   - Expand and verify attachment selector
   - Toggle attachment selection
   - Verify Submit section auto-expands

### H4: Security Review

Run `security-review` agent on:
- All new/modified backend views (admin endpoints, restore, soft-delete changes)
- New frontend components (XSS in filenames, CSRF on delete/restore)
- Parameter validation (can admin set dangerous values like negative TTL?)

---

## 11. File Reference Index

### Backend Files to Modify

| File | Changes |
|------|---------|
| `services/core/apps/projects/tasks.py` | Add storage key collection before cascade delete, dispatch cleanup |
| `services/gateway/apps/attachments/views.py` | Remove immutability check, remove immediate storage delete, add restore endpoint, use parameters |
| `services/gateway/apps/attachments/urls.py` | Add restore URL |
| `services/gateway/apps/attachments/serializers.py` | Add `deleted_at` field |
| `services/gateway/apps/admin_config/views.py` | Add admin attachments list/delete/restore endpoints |
| `services/gateway/apps/admin_config/urls.py` | Add admin attachment URLs |
| `proto/pdf.proto` | Add PdfAttachment message |
| `services/pdf/generator/builder.py` | Add attachments appendix section |
| `services/pdf/generator/renderer.py` | Add merge_attachments function |
| `services/pdf/grpc_server/servicers/pdf_servicer.py` | Pass attachments to merge |

### Backend Files to Create

| File | Purpose |
|------|---------|
| `services/gateway/apps/admin_config/migrations/0002_attachment_parameters.py` | Seed new parameters |
| `services/gateway/apps/attachments/tasks.py` (or similar) | Orphan cleanup + storage cleanup tasks |

### Frontend Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/pages/admin-panel.tsx` | Add Attachments tab |
| `frontend/src/pages/ProjectWorkspace/StructureStepView.tsx` | Redesign with collapsibles |
| `frontend/src/components/workspace/WorkspaceHeader.tsx` | Add Attachments button + modal |
| `frontend/src/components/chat/AttachmentBox.tsx` | Deleted state (red, crossed-out) |
| `frontend/src/api/attachments.ts` | Add restore, listIncludeDeleted, update interface |
| `frontend/src/api/admin.ts` | Add admin attachment API functions |
| `frontend/src/i18n/locales/en.json` | New translation keys |
| `frontend/src/i18n/locales/de.json` | New German translations |

### Frontend Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/features/admin/AttachmentsTab.tsx` | Admin attachments tab |
| `frontend/src/components/workspace/AttachmentsModal.tsx` | Project attachments modal |
| `frontend/src/components/workspace/AttachmentSelector.tsx` | PDF attachment selection |
| `frontend/src/components/workspace/CollapsibleSection.tsx` | Reusable collapsible wrapper |

---

## 12. UI/UX Specifications

### Color Tokens

| Element | Light | Dark |
|---------|-------|------|
| Deleted attachment border | `border-red-300` | `border-red-800` |
| Deleted attachment bg | `bg-red-50` | `bg-red-950/30` |
| Deleted filename text | `text-red-700 line-through` | `text-red-400 line-through` |
| Deleted badge | `bg-red-100 text-red-700` | `bg-red-900/30 text-red-400` |
| Lock chip (locked) | `border-amber-300 bg-amber-50 text-amber-700` | `border-amber-700 bg-amber-950/30 text-amber-400` |
| Lock chip (unlocked) | `border-border bg-background text-muted-foreground` | same |
| Collapsible header bg | `bg-muted/30` | same |
| Submit section bg | `bg-green-500/5` | same |
| Info note bg | `bg-blue-50 border-blue-200` | `bg-blue-950/30 border-blue-800` |

### Sizing

| Element | Size |
|---------|------|
| Collapsible header height | `py-3` (~48px) |
| Attachment list item | `p-3` with `gap-3` |
| File type icon | `h-5 w-5` |
| Attachment selector max-height | `200px` with `overflow-y-auto` |
| Modal width | `max-w-2xl` (672px) |
| Admin page size | 35 items per page |

### Interaction Patterns

1. **Delete confirmation:** Always show a confirmation dialog before soft-deleting an attachment
2. **Restore:** No confirmation needed, immediate action with toast
3. **Collapsible expand:** Smooth height animation, or instant if `prefers-reduced-motion`
4. **Toast messages:** Use `react-toastify` (already in project) for all success/error notifications
5. **Loading states:** Centered "Loading..." or skeleton placeholders
6. **Empty states:** Centered icon + descriptive message

### Accessibility

1. All collapsible sections: `aria-expanded` attribute on trigger, Enter/Space to toggle
2. All icon-only buttons: `aria-label` attribute
3. Deleted attachment in chat: additional `title` attribute with countdown info
4. Focus rings: Use existing `focus:ring-2 focus:ring-primary` pattern
5. Color is never the only indicator — always paired with text/icon

---

## Execution Checklist

When starting implementation, follow this order:

- [ ] **Read CLAUDE.md** — understand orchestrator role and subagent delegation
- [ ] **Group A** — Orphan cleanup + storage cascade (backend)
- [ ] **Group B** — Soft-delete lift, restore, admin APIs (backend)
- [ ] **Group C** — PDF attachment append (backend)
- [ ] **Group G** — Admin parameter seeding (backend)
- [ ] **Group D** — Admin Attachments tab (frontend)
- [ ] **Group E** — Attachments modal + chat integration (frontend)
- [ ] **Group F** — Strukturieren tab redesign (frontend)
- [ ] **Group H** — Tests, E2E, security review
- [ ] **Final:** `infra` agent rebuilds dev environment, manual smoke test
