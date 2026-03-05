# Page & Route Map

## Route Overview

| Route | Page | Access | Description |
|-------|------|--------|-------------|
| `/` | Landing Page | All authenticated users | Home page with idea lists, creation, and invitations |
| `/idea/<uuid>` | Idea Workspace | Owner, Collaborators, Read-Only viewers (via shared link) | Full brainstorming + review workspace |
| `/reviews` | Review Page | Reviewer role only | Review queue and history for submitted ideas |
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
| **Purpose** | Central hub for managing ideas and starting new brainstorms |
| **Roles** | All authenticated users |
| **Key Content** | Ordered lists: (1) My Ideas, (2) Collaborating, (3) Invitations, (4) Trash |
| **Key Actions** | Create new idea (hero section with chat input), accept/decline invitations, search by title, filter by state (Open / In Review / Accepted / Dropped / Rejected), filter by ownership (My Ideas / Collaborating), soft-delete ideas, restore from trash |

**Behaviors:**
- First message typed in the hero section becomes the first chat message in the new idea workspace (seamless transition).
- Soft delete moves ideas to Trash with an undo toast.
- Trash items permanently deleted after configurable countdown (default: 30 days).

---

### Idea Workspace (`/idea/<uuid>`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Full brainstorming and review workspace for a single idea |
| **Roles** | Owner, Co-owners, Collaborators (full edit); Read-only viewers (view only) |
| **Key Content** | Two vertical sections: Brainstorming (top, fills viewport) and Review (bottom, below fold) |

**Brainstorming Section (top):**

| Panel | Content | Actions |
|-------|---------|---------|
| **Left: Chat** | Chat messages (user + AI), @mention suggestions, AI processing indicator, AI reactions | Send messages, @mention users/AI, react to other users' messages |
| **Right: Board tab** | Digital board with Boxes, Groups, Free Text, connections, minimap, toolbar | Drag, resize, connect, edit, lock/unlock nodes, reference items to chat, undo/redo |
| **Right: Review tab** | PDF preview, expandable edit area, BRD sections, submit controls | View/download PDF, edit BRD sections, lock/unlock sections, regenerate AI text, regenerate PDF, toggle "Allow Information Gaps", submit for review with optional message and reviewer assignment |

**Header area:**
- Inline-editable idea title
- Agent mode dropdown (Interactive / Silent)
- Presence indicators (online users with idle states)
- Collaborator management (invite button, remove, transfer ownership)

**Review Section (bottom, below fold):**

| Area | Content | Actions |
|------|---------|---------|
| **Top (always visible)** | Small BRD preview (latest version), idea title, assigned reviewer(s), state label | — |
| **Timeline** | Comments (with nested replies), inline state changes, resubmission entries with versioned document links, similar ideas display | Post comments, reply to comments, download document versions |

**Section visibility and locking per idea state — see F-1.2 and F-1.4.**

---

### Review Page (`/reviews`) — Reviewers Only

| Aspect | Detail |
|--------|--------|
| **Purpose** | Manage review workload and history |
| **Roles** | Reviewer role only |
| **Key Content** | Categorized idea groups (see below), search field |
| **Key Actions** | Self-assign unassigned ideas, unassign self, search by title or UUID, browse review history |

**Idea Groups (in order):**

| Group | Visibility | Content |
|-------|-----------|---------|
| **Assigned to me** | Always visible | Ideas the reviewer has self-assigned or been assigned to |
| **Unassigned** | Always visible | Ideas in the shared review queue awaiting assignment |
| **Accepted** | Collapsed (history) | Previously accepted ideas |
| **Rejected** | Collapsed (history) | Previously rejected ideas (returned to user for rework) |
| **Dropped** | Collapsed (history) | Previously dropped ideas |

- Search field searches by idea title or UUID.
- Constraint: a Reviewer cannot review their own idea.

---

### Admin Panel (`/admin`) — Admins Only

| Aspect | Detail |
|--------|--------|
| **Purpose** | Runtime configuration, monitoring, AI context management, user insights |
| **Roles** | Admin role only |
| **Key Content** | 4 tabs: AI Context, Parameters, Monitoring, Users |

**Tab 1: AI Context**
| Content | Actions |
|---------|---------|
| Facilitator context (table of contents) | Edit free text |
| Detailed company context (structured sections + free text) | Edit structured sections + free text |

**Tab 2: Parameters**
| Content | Actions |
|---------|---------|
| All runtime-configurable parameters with current values | Edit values (apply immediately, no restart) |

**Tab 3: Monitoring**
| Content | Actions |
|---------|---------|
| Dashboard: connection count, ideas by state, active users, AI stats, service health | Configure alert recipients, add/remove Admins from alert list |

**Tab 4: Users**
| Content | Actions |
|---------|---------|
| User search (not eager-loaded) | Search for user, view profile: name, first name, email, roles, idea count, review count, contribution count |

---

## Floating Windows & Modals

| Element | Trigger | Content | Actions |
|---------|---------|---------|---------|
| **Ideas List** | Navbar button | Quick-access tabbed list of user's ideas. Tabs: Active (open + rejected, own + collaborating), In Review, Accepted, Closed (dropped + trashed). Tabs hidden when empty. | Click to navigate to idea |
| **Notification Bell** | Navbar bell icon | Persistent notification list with unread count badge | Act on notifications (accept/decline invitations), click to navigate to context |
| **Email Preferences** | User menu dropdown | Grouped toggles for email notification types per role | Toggle individual or group email notifications |
| **Error Log Modal** | "Show Logs" on error toast | Console output, network response, technical details, support message | Copy/read error details |
| **Collaborator Management** | Invite button / dropdown in workspace | Collaborator list, invite search | Invite, remove, transfer ownership |

## Banners (Contextual, Idea Page)

| Banner | Trigger | Content | Actions |
|--------|---------|---------|---------|
| **Invitation Banner** | User with pending invitation navigates to idea | Inviter's name, accept/decline prompt | Accept (become collaborator, unlock editing), Decline (redirect to landing page) |
| **Merge Request Banner** | Merge request received on this idea | Merge details, other idea reference | Accept (proceed with merge), Decline (dismiss permanently, unlock idea) |
| **Offline Banner** | Connection lost | "Currently offline. Retrying in X seconds" | Manual reconnect button |

---

## Navigation Structure

**Global Navbar (all pages):**
- Left:
  - Commerz Real logo + "ZiqReq" app name (brand block, left-anchored)
- Right:
  - Ideas list button (floating window) — all users
  - Review Page link — Reviewers only (conditionally visible)
  - Admin Panel link — Admins only (conditionally visible)
  - Connection state indicator (green "Online" / red "Offline")
  - Notification bell with unread count badge
  - User icon → dropdown: Language switcher, Theme switcher (Light/Dark), Email notification preferences, Logout
  - Dev user switcher (auth bypass mode only)

---

## User Flows

### Flow: New Idea Creation
1. User arrives at Landing Page (`/`).
2. User types first message in the hero section.
3. System creates a new idea, transitions to Idea Workspace (`/idea/<uuid>`).
4. First message appears as the opening chat message.
5. AI processes the message (after debounce), responds in chat, generates title, begins populating board.
6. User continues brainstorming with AI.

### Flow: BRD Generation & Submission
1. User clicks the Review tab in the right panel.
2. System triggers Summarizing AI — BRD generated from full idea state.
3. Progress indicator shows section readiness.
4. User reviews/edits BRD sections, locks edited sections.
5. User optionally toggles "Allow Information Gaps" for incomplete sections.
6. User clicks regenerate PDF.
7. User writes optional message, optionally assigns reviewer(s).
8. User clicks Submit — idea transitions to In Review.
9. Brainstorming section locks. Review section (below fold) activates.
10. Reviewers receive notification.

### Flow: Review Decision
1. Reviewer opens Review Page (`/reviews`).
2. Reviewer self-assigns an unassigned idea (or sees assigned ideas).
3. Reviewer reads BRD, examines brainstorming context, checks similar ideas.
4. Reviewer accepts, rejects (with comment), or drops (with comment).
5. Owner receives notification. Idea state updates.
6. If rejected: owner can rework and resubmit. If accepted: idea is finalized. If dropped: idea is permanently closed.
7. Any reviewer can undo an action (with mandatory comment) — returns to In Review.

### Flow: Idea Similarity & Merge (Open + Open)
1. AI generates keywords during brainstorming (once idea direction is clear).
2. Background service detects keyword overlap >= threshold between two open/rejected ideas.
3. AI deep comparison confirms genuine similarity.
4. Both owners notified (in-app + email). Both get read-only access to the other's idea.
5. Either owner requests merge.
6. Receiving idea locked with merge request banner.
7. Receiving owner accepts or declines.
8. If both consent: new idea created with AI-synthesized context (summary chat message + merged board). Both owners become co-owners. All collaborators added. Old ideas become read-only with reference to merged idea.
9. Users refine the merged context, referencing old ideas as needed.

### Flow: Idea Similarity & Append (Open + In Review)
1. Keyword matching and AI comparison detect similarity between an open idea and an in-review idea.
2. Open idea owner is notified and gets read-only access to the in-review idea.
3. Open idea owner requests append.
4. In-review idea's owner AND one assigned reviewer must accept.
5. On acceptance: open idea closes (read-only with reference), open idea's owner becomes collaborator on in-review idea, relevant context appended.

### Flow: Collaboration Invitation
1. Owner clicks Invite in the workspace.
2. Owner searches/selects a user from the directory.
3. Invitee receives email + in-app notification.
4. Invitation appears on invitee's Landing Page ("Invitations" list).
5. If invitee navigates to the idea directly (via notification or shared link): invitation banner appears.
6. Invitee accepts → becomes collaborator, gains edit access.
7. Invitee declines → nothing changes. Owner can re-invite.
