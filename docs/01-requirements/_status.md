# Requirements Engineering — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-02
- **Last updated:** 2026-03-02

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Vision & Scope | complete | 2026-03-02 |
| 2 | User Roles & Personas | complete | 2026-03-02 |
| 3 | Feature Catalog | complete | 2026-03-02 |
| 4 | Page & Route Map | complete | 2026-03-02 |
| 5 | Data Entities & Relationships | complete | 2026-03-02 |
| 6 | Non-Functional Requirements | complete | 2026-03-02 |
| 7 | Constraints & Assumptions | complete | 2026-03-02 |
| 8 | Summary & Handoff | complete | 2026-03-02 |

## Handoff
- **Ready:** true
- **Next specialist(s):** Software Architect (`/software_architect`)
- **Files produced:**
  - `docs/01-requirements/vision.md`
  - `docs/01-requirements/user-roles.md`
  - `docs/01-requirements/features.md`
  - `docs/01-requirements/pages.md`
  - `docs/01-requirements/data-entities.md`
  - `docs/01-requirements/nonfunctional.md`
  - `docs/01-requirements/constraints.md`
  - `docs/01-requirements/traceability.md`
- **Required input for next specialist:**
  - All files in `docs/01-requirements/`
  - Previous architecture decisions in `docs_old/02-architecture/` (especially `tech-stack.md`)
- **Briefing for next specialist:**
  - ZiqReq: AI-guided brainstorming platform for Commerz Real (~2,000 employees) producing Business Requirements Documents
  - 3 system roles (User, Reviewer, Admin) + idea-level permissions (Owner, Co-Owner, Collaborator, Read-Only)
  - 17 feature areas, 75 features — core loop: brainstorm with AI → generate BRD → submit to reviewers
  - Key complexity areas: real-time collaboration, AI facilitation with company context, idea similarity detection & merge, multi-state review workflow
  - Corporate standards: React + TypeScript + Tailwind (frontend), Python + Django (backend), gRPC (service-to-service), PostgreSQL (database), Azure Container Apps (hosting)
  - 15 downstream delegation notes marked with `⚙️ DOWNSTREAM →` across requirements files — 8 for AI Engineer, 6 for Software Architect, 1 for UI/UX Designer
- **Open questions:** None
