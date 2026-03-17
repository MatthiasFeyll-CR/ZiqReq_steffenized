# Release Plan — Chat File Attachments (M22)

## Context
Milestones M1-M16 implemented the original ZiqReq platform. M17-M21 refactored it into a requirements assembly platform. M22 adds a new feature: file attachments in the chat with AI processing.

## MVP Boundary
- **All stories are MVP** — file attachments are a complete feature
- **MVP features:** File upload (images + PDFs), drag & drop, presigned download URLs, AI content extraction (PDF + images), AI context integration with prompt injection sandboxing, attachment display in chat, security hardening

## Milestone Execution Order

### M22: Chat File Attachments
- **Purpose:** Add file attachment support to the chat (images + PDFs), with MinIO storage, content extraction, AI integration, and full frontend UI
- **Dependencies:** M21 (refactoring must be complete)
- **Stories:** 10

## Milestone Summary

| Milestone | Name | Stories | Dependencies | MVP |
|-----------|------|---------|-------------|-----|
| M22 | Chat File Attachments | 10 | M21 | Yes |

**Total: 1 milestone, 10 stories**

## Dependency Flow
```
M21 (refactoring complete) → M22 (Chat File Attachments)
```

## Story Execution Order & Dependencies
```
S1: MinIO + storage abstraction
 └─ S2: Attachment model + migration
     └─ S3: Attachment REST API
         ├─ S4: Chat-attachment linking + broadcast
         │   └─ S9: Frontend — API, upload hook, input + drag/drop
         │       └─ S10: Frontend — message display, thumbnails, presigned URL
         ├─ S5: File validation + security hardening
         └─ S6: AI extraction — PDF processing
             └─ S7: AI extraction — image + orchestration
                 └─ S8: AI context assembler + prompt update
```

Stories execute sequentially per pipeline constraints. The dependency graph above shows logical dependencies — Ralph processes them in order S1 → S2 → ... → S10.

## Branch Strategy
| Milestone | Branch Pattern | Base Branch | Merge Target |
|-----------|---------------|-------------|-------------|
| M22 | ralph/m22-chat-attachments | master (after M21 merge) | master |
