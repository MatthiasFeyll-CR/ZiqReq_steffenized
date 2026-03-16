# Page & Route Map

## Route Overview

| Route | Page | Access | Description |
|-------|------|--------|-------------|
| `/` | Landing Page | All authenticated users | Home page with project lists, creation, and invitations |
| `/project/<uuid>` | Project Workspace | Owner, Collaborators, Read-Only viewers (via shared link) | Full requirements assembly + review workspace |
| `/reviews` | Review Page | Reviewer role only | Review queue and history for submitted projects |
| `/admin` | Admin Panel | Admin role only | System configuration, monitoring, AI context, user lookup |
| `/login` | Login Page | Unauthenticated (production only) | Azure AD OIDC login. Not shown in dev bypass mode. |

## Public Pages (No Authentication)

| Page | Purpose | Key Content | Key Actions |
|------|---------|-------------|-------------|
| Login | Authenticate via Azure AD | Azure AD login prompt | Sign in with Microsoft account |

> In development (auth bypass mode), the login page is skipped. The selected dev user is immediately active.

## Authenticated Pages

### Landing Page (`/`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Central hub for managing projects and creating new requirements documents |
| **Roles** | All authenticated users |
| **Key Content** | Ordered lists: (1) My Projects, (2) Collaborating, (3) Invitations, (4) Trash |
| **Key Actions** | Create new project (via "New Project" button with modal), accept/decline invitations, search by title, filter by state (Open / In Review / Accepted / Dropped / Rejected), filter by ownership (My Projects / Collaborating), soft-delete projects, restore from trash |

**Behaviors:**
- "New Project" button opens a modal where user selects project type (Software / Non-Software) and provides initial project description.
- Upon creation, user is transitioned to the new project workspace.
- Soft delete moves projects to Trash with an undo toast.
- Trash items permanently deleted after configurable countdown (default: 30 days).

---

### Project Workspace (`/project/<uuid>`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Full requirements assembly and review workspace for a single project |
| **Roles** | Owner, Collaborators (full edit); Read-only viewers (view only) |
| **Key Content** | Two vertical sections: Requirements Assembly (top, fills viewport) and Review (bottom, below fold) |

**Requirements Assembly Section (top):**

The workspace adapts based on the current process step:

**Define Step (Default):**
| Panel | Content | Actions |
|-------|---------|---------|
| **Left: Chat** | Chat messages (user + AI), @mention suggestions, AI processing indicator, AI reactions | Send messages, @mention users/AI, react to other users' messages |
| **Right: Structured Requirements Panel** | Requirements tab (default): Project title, description, contributors, hierarchical structure (Epics/Stories or Milestones/Packages). Expandable/collapsible cards, drag-to-reorder. Review tab: PDF preview, expandable edit area, requirements document sections, submit controls | Requirements tab: Edit title/description, add/edit/delete/reorder hierarchical items, reference items to chat. Review tab: View/download PDF, edit document sections, lock/unlock sections, regenerate AI text, regenerate PDF, toggle "Allow Information Gaps", submit for review with optional message and reviewer assignment |

- Two-panel layout with draggable divider (resize chat vs. requirements panel).
- Requirements Panel has two tabs: **Requirements** (default, shows structured project hierarchy) and **Review** (shows document preview and editing).

**Structure Step:**
- Full-width requirements editor with hierarchical structure on the left.
- PDF preview on the right.
- Focus on refining the requirements document structure.

**Review Step:**
- Review section becomes primary focus (see below).

**Header area:**
- Inline-editable project title
- Agent mode dropdown (Interactive / Silent)
- Presence indicators (online users with idle states)
- Collaborator management (invite button, remove, transfer ownership)

**Review Section (bottom, below fold):**

| Area | Content | Actions |
|------|---------|---------|
| **Top (always visible)** | Small requirements document preview (latest version), project title, assigned reviewer(s), state label | — |
| **Timeline** | Comments (with nested replies), inline state changes, resubmission entries with versioned document links | Post comments, reply to comments, download document versions |

**Section visibility and locking per project state — see F-1.2 and F-1.4.**

---

### Review Page (`/reviews`) — Reviewers Only

| Aspect | Detail |
|--------|--------|
| **Purpose** | Manage review workload and history |
| **Roles** | Reviewer role only |
| **Key Content** | Categorized project groups (see below), search field |
| **Key Actions** | Self-assign unassigned projects, unassign self, search by title or UUID, browse review history |

**Project Groups (in order):**

| Group | Visibility | Content |
|-------|-----------|---------|
| **Assigned to me** | Always visible | Projects the reviewer has self-assigned or been assigned to |
| **Unassigned** | Always visible | Projects in the shared review queue awaiting assignment |
| **Accepted** | Collapsed (history) | Previously accepted projects |
| **Rejected** | Collapsed (history) | Previously rejected projects (returned to user for rework) |
| **Dropped** | Collapsed (history) | Previously dropped projects |

- Search field searches by project title or UUID.
- Constraint: a Reviewer cannot review their own project.

---

### Admin Panel (`/admin`) — Admins Only

| Aspect | Detail |
|--------|--------|
| **Purpose** | Runtime configuration, monitoring, AI context management, user insights |
| **Roles** | Admin role only |
| **Key Content** | 4 tabs: AI Context, Parameters, Monitoring, Users |

**Tab 1: AI Context**

The AI Context tab now contains **3 sub-tabs** for managing different context types:

| Sub-tab | Content | Actions |
|---------|---------|---------|
| **Global** | Facilitator context (table of contents), detailed company context (structured sections + free text) | Edit free text and structured sections |
| **Software** | Software project-specific AI context (e.g., development standards, architectural guidelines, software-specific requirements patterns) | Edit context specific to Software projects |
| **Non-Software** | Non-Software project-specific AI context (e.g., organizational standards, milestone structures, non-software requirements patterns) | Edit context specific to Non-Software projects |

**Tab 2: Parameters**
| Content | Actions |
|---------|---------|
| All runtime-configurable parameters with current values | Edit values (apply immediately, no restart) |

**Tab 3: Monitoring**
| Content | Actions |
|---------|---------|
| Dashboard: connection count, projects by state, active users, AI stats, service health | Configure alert recipients, add/remove Admins from alert list |

**Tab 4: Users**
| Content | Actions |
|---------|---------|
| User search (not eager-loaded) | Search for user, view profile: name, first name, email, roles, project count, review count, contribution count |

---

## Floating Windows & Modals

| Element | Trigger | Content | Actions |
|---------|---------|---------|---------|
| **Projects List** | Navbar button | Quick-access tabbed list of user's projects. Tabs: Active (open + rejected, own + collaborating), In Review, Accepted, Closed (dropped + trashed). Tabs hidden when empty. | Click to navigate to project |
| **Notification Bell** | Navbar bell icon | Persistent notification list with unread count badge | Act on notifications (accept/decline invitations), click to navigate to context |
| **Email Preferences** | User menu dropdown | Grouped toggles for email notification types per role | Toggle individual or group email notifications |
| **Error Log Modal** | "Show Logs" on error toast | Console output, network response, technical details, support message | Copy/read error details |
| **Collaborator Management** | Invite button / dropdown in workspace | Collaborator list, invite search | Invite, remove, transfer ownership |
| **New Project Modal** | "New Project" button on Landing Page | Project type selection (Software / Non-Software), initial description textarea | Select type, enter description, create project |

## Banners (Contextual, Project Page)

| Banner | Trigger | Content | Actions |
|--------|---------|---------|---------|
| **Invitation Banner** | User with pending invitation navigates to project | Inviter's name, accept/decline prompt | Accept (become collaborator, unlock editing), Decline (redirect to landing page) |
| **Offline Banner** | Connection lost | "Currently offline. Retrying in X seconds" | Manual reconnect button |

---

## Navigation Structure

**Global Navbar (all pages):**
- Left:
  - Commerz Real logo + "ZiqReq" app name (brand block, left-anchored)
- Right:
  - Projects list button (floating window) — all users
  - Review Page link — Reviewers only (conditionally visible)
  - Admin Panel link — Admins only (conditionally visible)
  - Connection state indicator (green "Online" / red "Offline")
  - Notification bell with unread count badge
  - User icon → dropdown: Language switcher, Theme switcher (Light/Dark), Email notification preferences, Logout
  - Dev user switcher (auth bypass mode only)

---

## User Flows

### Flow: New Project Creation
1. User arrives at Landing Page (`/`).
2. User clicks "New Project" button.
3. Modal appears with project type selection (Software / Non-Software).
4. User selects type and enters initial project description.
5. System creates a new project, transitions to Project Workspace (`/project/<uuid>`).
6. Chat panel shows welcome message or first user message.
7. AI processes the initial description (after debounce), responds in chat, generates title, begins structuring requirements.
8. User continues defining requirements with AI assistance.

### Flow: Requirements Document Generation & Submission
1. User clicks the Review tab in the right panel (or Structure step becomes active).
2. System triggers Summarizing AI — Requirements Document generated from full project state.
3. Progress indicator shows section readiness.
4. User reviews/edits document sections, locks edited sections.
5. User optionally toggles "Allow Information Gaps" for incomplete sections.
6. User clicks regenerate PDF.
7. User writes optional message, optionally assigns reviewer(s).
8. User clicks Submit — project transitions to In Review.
9. Requirements Assembly section locks. Review section (below fold) activates.
10. Reviewers receive notification.

### Flow: Review Decision
1. Reviewer opens Review Page (`/reviews`).
2. Reviewer self-assigns an unassigned project (or sees assigned projects).
3. Reviewer reads requirements document, examines project context.
4. Reviewer accepts, rejects (with comment), or drops (with comment).
5. Owner receives notification. Project state updates.
6. If rejected: owner can rework and resubmit. If accepted: project is finalized. If dropped: project is permanently closed.
7. Any reviewer can undo an action (with mandatory comment) — returns to In Review.

### Flow: Collaboration Invitation
1. Owner clicks Invite in the workspace.
2. Owner searches/selects a user from the directory.
3. Invitee receives email + in-app notification.
4. Invitation appears on invitee's Landing Page ("Invitations" list).
5. If invitee navigates to the project directly (via notification or shared link): invitation banner appears.
6. Invitee accepts → becomes collaborator, gains edit access.
7. Invitee declines → nothing changes. Owner can re-invite.
