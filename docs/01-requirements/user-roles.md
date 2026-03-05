# User Roles & Personas

## Roles Overview

| Role | Description | Authentication | Registration |
|------|-------------|----------------|--------------|
| **User** | Base role. Every Commerz Real employee in the Azure AD tenant. Can create ideas, brainstorm with AI, collaborate, submit for review. | Required (Azure AD) | Automatic — all employees in the AD domain |
| **Reviewer** | Can evaluate submitted BRDs — accept, reject, or drop ideas. Accesses the Review Page. | Required (Azure AD) | Assigned via Azure AD group by IT administrators |
| **Admin** | Accesses the Admin Panel for runtime configuration, monitoring, AI context management, and user insights. | Required (Azure AD) | Assigned via Azure AD group by IT administrators |

## Role Model Rules

- Roles are **additive** — any combination is valid (e.g., User + Reviewer + Admin).
- Admin does **not** inherit Reviewer permissions. A user must be explicitly assigned both roles to have both capabilities.
- Role assignment is managed **entirely in Azure AD** — the application reads roles from AD group membership, not from an internal role management system.

## Role Details

### User (Base Role)
- **Description:** A Commerz Real employee who uses ZiqReq to brainstorm workflow improvement ideas with AI support and submit them as Business Requirements Documents.
- **Key capabilities:**
  1. Create new ideas
  2. Brainstorm with AI in the chat interface
  3. Edit the digital board
  4. Generate and edit the Business Requirements Document
  5. Submit ideas for review (optionally assigning a specific reviewer)
  6. Invite collaborators to an idea
  7. Manage collaborators (remove, transfer ownership)
  8. Accept or decline collaboration invitations
  9. Soft-delete own ideas
  10. Search and filter own ideas and collaborations
  11. Set language preference (German / English)
  12. Configure email notification preferences
  13. View read-only ideas via shared links
- **Restrictions:** Cannot access the Review Page, Admin Panel, or review any idea.
- **Typical workflow:** Employee has a workflow improvement idea → opens ZiqReq → brainstorms with AI in chat → AI helps structure the idea on the board → opens Review tab → AI generates BRD → user edits/refines sections → submits for review → receives notification when reviewed.

### Reviewer
- **Description:** A member of the strategic software department who evaluates submitted BRDs and decides whether ideas are actionable.
- **Key capabilities (in addition to User):**
  1. Access the Review Page listing all submitted ideas
  2. Self-assign unassigned ideas from the review queue
  3. Unassign themselves from an assigned idea
  4. Accept an idea (idea becomes read-only, owner notified)
  5. Drop an idea with mandatory comment (idea permanently closed, owner notified)
  6. Reject an idea with mandatory comment (idea returned for rework, owner notified)
  7. Comment on ideas in the review timeline
  8. View the BRD and full brainstorming context of submitted ideas
  9. Search for reviewers by name (when selecting a reviewer)
- **Restrictions:**
  - Cannot review their own idea (conflict of interest prevention).
  - Accept does not require a comment; Drop and Reject require mandatory comments.
- **Typical workflow:** Reviewer opens Review Page → sees submitted ideas (assigned to me / unassigned) → self-assigns an unassigned idea → reads the BRD and brainstorming context → accepts, rejects (with feedback), or drops (with reason) → owner is notified.

### Admin
- **Description:** An operations/IT team member responsible for configuring and monitoring the ZiqReq platform at runtime.
- **Key capabilities (in addition to User):**
  1. Access the Admin Panel (`/admin`)
  2. Manage AI context — edit the Facilitator bucket (table of contents) and Context Agent bucket (detailed company information)
  3. Configure runtime parameters (debounce timers, idle timeouts, rate limits, etc.)
  4. View the monitoring dashboard (connection counts, idea counts, AI stats, service health)
  5. Configure monitoring alerts and manage alert recipient list
  6. Search and view user profiles — name, email, assigned roles, idea count, review count, contribution count
- **Restrictions:** Does not inherit Reviewer capabilities. Cannot accept/reject/drop ideas unless also assigned the Reviewer role.
- **Typical workflow:** Admin opens Admin Panel → checks monitoring dashboard for system health → adjusts parameters if needed → updates AI context buckets when company information changes → searches user profiles for support inquiries.

## Idea-Level Permissions

Beyond system-level roles, each idea has an ownership and collaboration model:

| Idea Role | Description | Assignment |
|-----------|-------------|------------|
| **Owner** | Full control over the idea. Can invite/remove collaborators, transfer ownership, submit for review, delete. | Automatically assigned to the idea creator. |
| **Co-Owner** | Equal authority to Owner. Either co-owner can act independently on all owner actions. | Only created through idea merge — both original owners become co-owners. |
| **Collaborator** | Can edit chat and board. Cannot submit for review, invite others, or delete. | Invited by the owner, must accept invitation. |
| **Read-Only Viewer** | Can view the idea but cannot edit anything. | Accesses via shared read-only link (requires Azure AD authentication). |

### Ownership Rules

- **Default:** One owner per idea (the creator).
- **Merged ideas:** Two co-owners (both original idea owners). All collaborators from both original ideas are added.
- **Co-owner independence:** Either co-owner can submit for review, invite collaborators, delete the idea, or transfer their ownership share independently.
- **Co-owner leaving:** A co-owner can leave voluntarily without transferring ownership (the other co-owner remains).
- **Revert to single-owner:** If one co-owner leaves a merged idea, the remaining owner operates under normal single-owner rules (must transfer ownership before leaving).
- **Single-owner leaving:** Owner must transfer ownership to a collaborator before leaving an idea.
