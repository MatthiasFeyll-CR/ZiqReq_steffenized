# User Roles & Personas

## Roles Overview

| Role | Description | Authentication | Registration |
|------|-------------|----------------|--------------|
| **User** | Base role. Every Commerz Real employee in the Azure AD tenant. Can create projects, structure requirements with AI, collaborate, submit for review. | Required (Azure AD) | Automatic — all employees in the AD domain |
| **Reviewer** | Can evaluate submitted Requirements Documents — accept, reject, or drop projects. Accesses the Review Page. | Required (Azure AD) | Assigned via Azure AD group by IT administrators |
| **Admin** | Accesses the Admin Panel for runtime configuration, monitoring, AI context management, and user insights. | Required (Azure AD) | Assigned via Azure AD group by IT administrators |

## Role Model Rules

- Roles are **additive** — any combination is valid (e.g., User + Reviewer + Admin).
- Admin does **not** inherit Reviewer permissions. A user must be explicitly assigned both roles to have both capabilities.
- Role assignment is managed **entirely in Azure AD** — the application reads roles from AD group membership, not from an internal role management system.

## Role Details

### User (Base Role)
- **Description:** A Commerz Real employee who uses ZiqReq to structure workflow improvement requirements with AI support and submit them as Requirements Documents.
- **Key capabilities:**
  1. Create new projects (via "New Project" button with type selection modal)
  2. Select project type (Software: Epics/User Stories, or Non-Software: Milestones/Work Packages)
  3. Structure requirements with AI in the chat interface
  4. Organize requirements in the Structured Requirements Panel (accordion with sortable cards)
  5. Generate and edit the Requirements Document
  6. Submit projects for review (optionally assigning a specific reviewer)
  7. Invite collaborators to a project
  8. Manage collaborators (remove, transfer ownership)
  9. Accept or decline collaboration invitations
  10. Soft-delete own projects
  11. Search and filter own projects and collaborations
  12. Set language preference (German / English)
  13. Configure email notification preferences
  14. View read-only projects via shared links
- **Restrictions:** Cannot access the Review Page, Admin Panel, or review any project.
- **Typical workflow:** Employee has a workflow improvement idea → opens ZiqReq → clicks "New Project" → selects project type (Software/Non-Software) → structures requirements with AI in chat → AI helps organize requirements in the panel → opens Review tab → AI generates Requirements Document → user edits/refines sections → submits for review → receives notification when reviewed.

### Reviewer
- **Description:** A member of the strategic software department who evaluates submitted Requirements Documents and decides whether projects are actionable.
- **Key capabilities (in addition to User):**
  1. Access the Review Page listing all submitted projects
  2. Self-assign unassigned projects from the review queue
  3. Unassign themselves from an assigned project
  4. Accept a project (project becomes read-only, owner notified)
  5. Drop a project with mandatory comment (project permanently closed, owner notified)
  6. Reject a project with mandatory comment (project returned for rework, owner notified)
  7. Comment on projects in the review timeline
  8. View the Requirements Document and full requirements context of submitted projects
  9. Search for reviewers by name (when selecting a reviewer)
- **Restrictions:**
  - Cannot review their own project (conflict of interest prevention).
  - Accept does not require a comment; Drop and Reject require mandatory comments.
- **Typical workflow:** Reviewer opens Review Page → sees submitted projects (assigned to me / unassigned) → self-assigns an unassigned project → reads the Requirements Document and requirements context → accepts, rejects (with feedback), or drops (with reason) → owner is notified.

### Admin
- **Description:** An operations/IT team member responsible for configuring and monitoring the ZiqReq platform at runtime.
- **Key capabilities (in addition to User):**
  1. Access the Admin Panel (`/admin`)
  2. Manage AI context — edit the Global bucket (common across all projects), Software bucket (for Software projects), and Non-Software bucket (for Non-Software projects)
  3. Configure runtime parameters (debounce timers, idle timeouts, rate limits, etc.)
  4. View the monitoring dashboard (connection counts, project counts, AI stats, service health)
  5. Configure monitoring alerts and manage alert recipient list
  6. Search and view user profiles — name, email, assigned roles, project count, review count, contribution count
- **Restrictions:** Does not inherit Reviewer capabilities. Cannot accept/reject/drop projects unless also assigned the Reviewer role.
- **Typical workflow:** Admin opens Admin Panel → checks monitoring dashboard for system health → adjusts parameters if needed → updates AI context buckets when company information changes → searches user profiles for support inquiries.

## Project-Level Permissions

Beyond system-level roles, each project has an ownership and collaboration model:

| Project Role | Description | Assignment |
|-----------|-------------|------------|
| **Owner** | Full control over the project. Can invite/remove collaborators, transfer ownership, submit for review, delete. | Automatically assigned to the project creator. |
| **Collaborator** | Can edit chat and requirements structure. Cannot submit for review, invite others, or delete. | Invited by the owner, must accept invitation. |
| **Read-Only Viewer** | Can view the project but cannot edit anything. | Accesses via shared read-only link (requires Azure AD authentication). |

### Ownership Rules

- **Default:** One owner per project (the creator).
- **Single-owner leaving:** Owner must transfer ownership to a collaborator before leaving a project.
