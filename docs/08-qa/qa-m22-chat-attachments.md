# QA Report: Milestone 22 — Chat File Attachments

**Date:** 2026-03-18
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 2 (ruff gate fixed in cycle 1)
**PRD:** tasks/prd-m22.json
**Progress:** .ralph/progress.txt

---

## Summary

Cycle 2 re-review of Milestone 22 (Chat File Attachments). All 10 original user stories were verified as PASS in cycle 0 and carried forward. Cycle 1 identified one defect (DEF-001: 5 pre-existing ruff lint errors blocking the REQUIRED gate). BF-001 fixed all 5 ruff errors. All 878 Python tests pass, all REQUIRED gates pass (Frontend typecheck, Backend lint Ruff, Backend typecheck mypy). The milestone now passes QA.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | MinIO service + storage abstraction layer | PASS | Verified in cycle 0; no regression |
| US-002 | Attachment model + migration (Gateway + Core) | PASS | Verified in cycle 0; no regression |
| US-003 | Attachment REST API | PASS | Verified in cycle 0; DEV-001 noted (read-only via access control) |
| US-004 | Chat-attachment linking + serializer/broadcast update | PASS | Verified in cycle 0; no regression |
| US-005 | File validation + security hardening | PASS | Verified in cycle 0; no regression |
| US-006 | AI content extraction — PDF processing | PASS | Verified in cycle 0; no regression |
| US-007 | AI content extraction — image + orchestration | PASS | Verified in cycle 0; no regression |
| US-008 | AI context integration | PASS | Verified in cycle 0; no regression |
| US-009 | Frontend: attachment API, upload hook, ChatInput + drag & drop | PASS | Verified in cycle 0; no regression |
| US-010 | Frontend: message attachment display, thumbnails, presigned URL access | PASS | Verified in cycle 0; no regression |
| BF-001 | Fix: ruff lint errors in 5 pre-existing files | PASS | All 4 acceptance criteria met (see below) |

**Stories passed:** 11 / 11 (10 original + 1 bugfix)
**Stories with defects:** 0
**Stories with deviations:** 1 (DEV-001, carried from cycle 0)

### BF-001 Acceptance Criteria Verification

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `ruff check services/` exits 0 with no errors | PASS | Verified locally: "All checks passed!" |
| No functional behavior changes (lint-only fixes) | PASS | Changes limited to import ordering, whitespace, line length |
| All existing tests still pass | PASS | Pipeline: 878 passed, 0 failed |
| Typecheck passes | PASS | Pipeline: frontend typecheck PASSED, mypy PASSED |

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in this milestone's PRD stories.

The test matrix (`docs/04-test-architecture/test-matrix.md`) was written before M22 was planned and does not contain M22-specific test IDs. Ralph implemented comprehensive tests regardless:

| Test Area | Test File | Test Count | Notes |
|-----------|-----------|------------|-------|
| Storage backends | `services/gateway/storage/tests/test_backends.py` | 21 | Mock minio client, ABC, factory |
| Attachment model | `services/gateway/apps/projects/tests/test_attachment_model.py` | 16 | CRUD, helpers, constraints |
| Attachment REST API | `services/gateway/apps/attachments/tests/test_views.py` | 38 | Auth, access, validation, happy path |
| File validators | `services/gateway/apps/attachments/tests/test_validators.py` | 33 | Magic bytes, EXIF, PDF JS, filename |
| Chat-attachment linking | `services/gateway/apps/chat/tests/test_chat_attachments.py` | 12 | Linking, immutability, broadcast |
| AI PDF extraction | `services/ai/tests/test_extract_attachment.py` | 19 | PDF, image, mock, errors |
| Pipeline extraction wait | `services/ai/tests/test_pipeline_extraction_wait.py` | 6 | Poll, timeout, no-op |
| AI context + attachments | `services/ai/tests/test_context_assembly_attachments.py` | 24 | Assembly, prompt, truncation |
| Frontend upload hook | `frontend/src/__tests__/use-attachment-upload.test.tsx` | 14 | Add, remove, validation |
| Frontend AttachmentBox | `frontend/src/__tests__/attachment-box.test.tsx` | 10 | Clickable, read-only, thumbnail |
| Frontend UserMessageBubble | `frontend/src/__tests__/user-message-attachments.test.tsx` | 5 | Attachments display |
| Frontend ChatInput | `frontend/src/__tests__/chat-input-attachments.test.tsx` | -- | Paperclip, file input |

*No MISSING test IDs to report since M22 predates the test matrix.*

---

## Gate Check Results

| Check | Status | Details |
|-------|--------|---------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | `cd frontend && npx tsc --noEmit` clean |
| Backend lint (Ruff) | **PASSED** | `ruff check services/` exits 0 — BF-001 resolved DEF-001 |
| Backend typecheck (mypy) | PASSED | Clean |
| Frontend lint (ESLint) | FAILED (optional) | 6 errors (3 from M22 test file unused vars, 3 pre-existing), 9 warnings (all pre-existing) |

All REQUIRED gates pass. ESLint is optional and non-blocking.

---

## Defects

No defects remain. DEF-001 (ruff lint gate failure) was resolved by BF-001 in this cycle.

### DEF-001 (RESOLVED): Ruff lint gate fails with 5 errors

- **Status:** RESOLVED in bugfix cycle 2
- **Fix applied:** BF-001 — `ruff check --fix` for I001/W293, manual line break for E501
- **Verification:** `ruff check services/` now exits 0 with "All checks passed!"

---

## Deviations

### DEV-001: Presigned URL read-only check via access control (not explicit read-only flag)

- **Story:** US-003
- **Spec document:** tasks/prd-m22.json, US-003 AC4
- **Expected (per spec):** "rejects read-only users (share link access)" — implies an explicit read-only check
- **Actual (in code):** `attachment_url` view at `services/gateway/apps/attachments/views.py` uses `_check_access(user, project)` which requires the user to be owner or collaborator. Share link (read-only) users are not collaborators and fail this check with 403.
- **Why code is correct:** The access control layer inherently blocks read-only users. An explicit `is_read_only` check would be redundant. The frontend also enforces read-only blocking with `clickable={!isReadOnly}` and a toast message.
- **Spec update needed:** Clarify in docs/02-architecture/api-design.md that read-only blocking for presigned URLs is via collaborator access control, not a separate read-only flag.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 878 passed, 0 failed |
| TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend typecheck (mypy) | mypy | PASS | Clean |
| Backend lint (Ruff) | `ruff check services/` | PASS | Clean (BF-001 resolved) |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | OPTIONAL FAIL | 6 errors (3 M22 test file, 3 pre-existing), 9 warnings (pre-existing) |

---

## Security Findings

| ID | Category | Severity | File | Finding | Status |
|----|----------|----------|------|---------|--------|
| SEC-001 | Injection (MIME spoofing) | -- | `validators.py:31-60` | Magic byte validation before upload | MITIGATED |
| SEC-002 | Sensitive Data Exposure (EXIF) | -- | `validators.py:63-89` | EXIF metadata stripped from images via Pillow | MITIGATED |
| SEC-003 | XSS (PDF JavaScript) | -- | `validators.py:92-136` | PDF scanned for /JS, /JavaScript, /Launch, /SubmitForm, /GoToR actions | MITIGATED |
| SEC-004 | Path Traversal | -- | `validators.py:139-153` | Filename sanitization strips directory paths, replaces non-alphanumeric | MITIGATED |
| SEC-005 | Prompt Injection | -- | `extract_attachment.py:21-35` | Vision prompts include "WARNING: user-uploaded content" | MITIGATED |
| SEC-006 | Prompt Injection | -- | `facilitator/prompt.py` | `<user_attachment>` XML block includes WARNING attribute for sandboxing | MITIGATED |
| SEC-007 | Broken Access Control | -- | `attachments/views.py:70-75` | Auth + collaborator check on all endpoints | MITIGATED |
| SEC-008 | Rate Limiting (DoS) | -- | `attachments/views.py:78-85` | 10 uploads/min/user via Redis cache | MITIGATED |
| SEC-009 | File Size Limit | -- | `attachments/views.py:32` | 100MB max + Django DATA_UPLOAD_MAX_MEMORY_SIZE | MITIGATED |
| SEC-010 | Forced Download | -- | `backends.py:74-75` | Presigned URLs include `response-content-disposition=attachment` | MITIGATED |
| SEC-011 | SQL Injection | -- | `extract_attachment.py:42-72` | All SQL uses parameterized queries (%s placeholders) | MITIGATED |

**No critical or major security findings. All OWASP Top 10 basics are properly addressed.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | N+1 Queries | -- | `chat/views.py` | `_list_messages` does batch prefetch of attachments per page | No issue — properly handled |
| PERF-002 | Missing Indexes | -- | `projects/models.py` | Indexes on project_id, message_id, (project_id, deleted_at) | No issue — all indexed |
| PERF-003 | Context Bloat | -- | `facilitator/prompt.py` | Extracted content truncated to ~16000 chars per attachment | No issue — properly bounded |
| PERF-004 | Pipeline Polling | Minor | `pipeline.py` | Extraction wait re-fetches full project context on each 2s poll | Acceptable — bounded by 30s timeout, max ~15 polls |
| PERF-005 | Memory Leaks | -- | `AttachmentStagingArea.tsx` | URL.createObjectURL revoked on unmount | No issue — properly handled |

**No critical or major performance findings.**

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| All M22 components | `docs/03-design/` | N/A | No design specs directory exists |

*No design specs available for this milestone. Design compliance cannot be assessed.*

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### Pages & Navigation
- [ ] ProjectWorkspace chat panel still loads correctly with attachment support
- [ ] Chat area still accepts text-only messages without attachments

### API Endpoints
- [ ] POST `/api/projects/:id/attachments/` still accepts multipart file upload and returns metadata
- [ ] GET `/api/projects/:id/attachments/` still returns active attachments for project
- [ ] DELETE `/api/projects/:id/attachments/:aid/` still soft-deletes and returns 204
- [ ] GET `/api/projects/:id/attachments/:aid/url/` still returns presigned URL; rejects read-only users
- [ ] POST `/api/projects/:id/chat/` still accepts optional `attachment_ids[]` and links attachments

### Data Integrity
- [ ] `attachments` table has correct schema (UUID PK, project_id FK, message_id, extraction_status, indexes)
- [ ] Attachment soft-delete (deleted_at) correctly frees project count
- [ ] Immutability rule: DELETE blocked for attachments with non-null message_id

### Features
- [ ] File upload validates: type (PNG/JPEG/WebP/PDF), size (100MB), magic bytes, project limit (10), per-message limit (3)
- [ ] EXIF metadata stripped from uploaded images
- [ ] PDF JavaScript/actions detected and rejected
- [ ] Celery extraction task processes PDFs (text + vision fallback) and images (vision description)
- [ ] AI pipeline waits for extraction (2s poll, 30s timeout) before processing
- [ ] Extraction completion event broadcast via WebSocket updates frontend status
- [ ] AI system prompt includes `<user_attachment>` blocks with WARNING sandboxing attribute
- [ ] AI system prompt includes `<attachment_guidance>` block
- [ ] Context extension agent searches extracted_content for compressed sessions
- [ ] Frontend: paperclip button opens file picker, drag & drop works with visual overlay
- [ ] Frontend: upload progress shown, staged attachments displayed above textarea with X remove
- [ ] Frontend: sent message attachments displayed as AttachmentBox with thumbnail for images
- [ ] Frontend: presigned URL opens in new tab for collaborators; read-only users see toast
- [ ] Frontend: extraction status (pending/processing/completed/failed) displayed on attachment boxes

### Quality Baseline
- [ ] TypeScript typecheck still passes with zero errors
- [ ] `ruff check services/` passes with zero errors
- [ ] mypy passes
- [ ] All 878+ Python tests still pass
- [ ] All frontend tests still pass
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (DEF-001 resolved by BF-001)
- **Deviations found:** 1 (DEV-001: presigned URL read-only check via access control)
- **Bugfix PRD required:** No
- **Bugfix cycle:** 2 (final)

The milestone is complete. All 10 user stories pass acceptance criteria, BF-001 resolved the sole defect (ruff lint gate), all 878 Python tests pass, and all REQUIRED gates pass. Security review found no issues — all OWASP basics are properly addressed. The milestone is ready for merge.
