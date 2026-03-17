# Page Layouts

All wireframes use the design tokens from `design-system.md`. Layouts are shown for desktop (xl+) first, with responsive notes per section.

---

## 1. Global Layout Shell

Every authenticated page shares this structure:

```
+=========================================================================+
|  NAVBAR (56px, sticky top, z-40)                                        |
+=========================================================================+
|                                                                         |
|                                                                         |
|                          PAGE CONTENT                                   |
|                      (varies per route)                                 |
|                                                                         |
|                                                                         |
+=========================================================================+
```

- Navbar is sticky (`position: sticky; top: 0`), always visible.
- Page content scrolls beneath the navbar.
- No sidebar in the global layout — all navigation lives in the navbar.
- Background: `var(--background)` (light: `#FAFAFA`, dark: `#0B1121`).

---

## 2. Navbar

### 2.1 Desktop (xl+)

```
+=========================================================================+
| [CR] ZiqReq   |  Projects  Reviews*  Admin*  | *Online  [bell]3  [JD v]   |
+=========================================================================+
  ^brand block     ^nav links (role-gated)    ^utility items

  Left group                  Center/Right nav           Right utility
```

Detailed layout:

```
+=========================================================================+
|                                                                         |
|  [logo][16px] ZiqReq    [24px]   Projects   Reviews   Admin               |
|                                                                         |
|                          *Online   [bell] 3   [avatar v]               |
|                                                                         |
+=========================================================================+
```

| Zone | Content | Alignment |
|------|---------|-----------|
| Left | CR ribbon logo (24px h) + "ZiqReq" (Gotham Bold 18px, white) | `flex items-center gap-4` |
| Center-Left | Nav links: Projects, Reviews*, Admin* (Gotham Medium 14px) | `flex items-center gap-2` |
| Right | Connection dot + label, Bell + badge, User avatar + dropdown caret | `flex items-center gap-3` |

- Nav links use `padding: 8px 12px`, `rounded: 6px`
- Active link: gold underline (2px bottom border `#FFD700`)
- Hover: `bg-white/10` background
- Reviews link: visible only if user has Reviewer role
- Admin link: visible only if user has Admin role
- Notification bell: icon-only placeholder in M1. Gold circle badge with white count text (absolute-positioned top-right of bell icon) added when notification counts are wired in M11.
- User avatar: 32px circle, initials fallback, dropdown on click

### 2.2 Tablet / Mobile (< lg)

```
+=========================================================================+
| [hamburger]  [CR] ZiqReq                         *  [bell] 3  [JD v]   |
+=========================================================================+
```

- Hamburger menu (left) toggles a slide-in sheet (from left)
- Sheet contains: Projects, Reviews*, Admin* as full-width links
- Brand block stays visible in center
- Right utility items remain inline (condensed)

### 2.3 User Dropdown Menu

```
                                          +-------------------------+
                                          |  John Doe               |
                                          |  john.doe@commerzreal.de|
                                          +-------------------------+
                                          |  Language      DE | EN  |
                                          |  Theme      Light|Dark  |
                                          |  Email Preferences      |
                                          +-------------------------+
                                          |  Logout                 |
                                          +-------------------------+
```

- Dropdown: `shadow-lg`, `rounded-lg` (12px), `w-64`
- Language: toggle between DE and EN (segmented control) (FA-16)
- Theme: toggle between Light and Dark (segmented control) (FA-17)
- Email Preferences: opens floating window (see Section 9.3) (FA-13)
- Dev mode only: user switcher row appears above Logout

---

## 3. Landing Page (`/`)

### 3.1 Desktop Layout

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
|                                                                         |
|                        max-w-5xl mx-auto                                |
|                                                                         |
|  +-------------------------------------------------------------------+ |
|  |                                                                   | |
|  |                    HERO SECTION                                   | |
|  |                                                                   | |
|  |         "Ready to define your next project?"                      | |
|  |                                                                   | |
|  |                    [+ New Project]                                | |
|  |                                                                   | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  +-- Search & Filters -----------------------------------------------+ |
|  |  [Search by title...        ]  [State v]  [Ownership v]          | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  My Projects                                                 (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  * Project Title                  [SW]     Open    2h ago    ... | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  * Another Project             [NON-SW] In Review   1d ago    ... | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  * Third Project                  [SW]  Accepted    3d ago    ... | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  Collaborating                                               (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  * Shared Project (by Anna M.)    [SW]     Open    5h ago    ... | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  Pending Invitations                                         (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  "Process Optimization" from Max S.       [Accept]  [Decline]     | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  Trash                                                       (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  Deleted Project                 Deletes in 28d    [Restore]      | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
+=========================================================================+
```

### 3.2 Hero Section

- Background: `var(--surface)` with subtle `shadow-sm`
- Rounded: `rounded-xl` (16px)
- Padding: `48px` vertical, `32px` horizontal
- Heading: Gotham Bold, `text-2xl` (24px), centered
- Subtext: Gotham Book, `text-base`, `text-secondary`, centered
- Button: Primary button, "+ New Project", centered
- On click: opens New Project Modal (see § 3.3)

### 3.3 New Project Modal

Triggered by clicking "+ New Project" button in Hero Section.

```
+------------- Modal (max-w-2xl, centered) ----------------+
|  Create New Project                               [x]    |
+----------------------------------------------------------+
|                                                          |
|  Select Project Type:                                    |
|                                                          |
|  +----------------------+    +----------------------+    |
|  |                      |    |                      |    |
|  |   [Software Icon]    |    | [Non-Software Icon]  |    |
|  |                      |    |                      |    |
|  |  Software Project    |    | Non-Software Project |    |
|  |                      |    |                      |    |
|  | Epics & User Stories |    | Milestones & Work    |    |
|  |                      |    | Packages             |    |
|  |                      |    |                      |    |
|  +----------------------+    +----------------------+    |
|                                                          |
|                                          [Create]        |
+----------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `max-w-2xl` (672px) |
| Backdrop | `bg-black/50`, click-outside closes |
| Cards | Large selectable cards, `bg-surface`, `border-2`, `rounded-lg`, `p-6` |
| Selected state | `border-primary`, gold border glow |
| Icons | Lucide `Code` for Software, Lucide `Briefcase` for Non-Software |
| Create button | Primary button, disabled until selection made, navigates to `/project/<uuid>` |

### 3.4 Project Card

```
+-------------------------------------------------------------------+
|                                                                   |
|  * Project Title Text Here                        [SW]            |
|     Last updated 2 hours ago                                      |
|                                                                   |
|                                          [State Badge]    [...]   |
|                                                                   |
+-------------------------------------------------------------------+
```

- Card: `bg-surface`, `rounded-md` (8px), `shadow-sm`, `border`
- Padding: `16-20px`
- Title: Gotham Medium, `text-base`, `text-primary`
- Type badge: Small pill badge, `text-xs`, "SW" (software) or "NON-SW" (non-software), positioned near title
- Timestamp: Gotham Book, `text-sm`, `text-secondary`
- State badge: pill shape (`rounded-full`), `text-xs`, uses project state colors
- Three-dot menu (`...`): opens dropdown with Delete (soft delete)
- Hover: `shadow-md`, `cursor-pointer`
- Click: navigates to `/project/<uuid>`

### 3.5 Section Headers

- Gotham Bold, `text-lg` (18px), `text-primary`
- Item count on the right: `text-sm`, `text-muted`
- Bottom border: `border-b` for visual separation
- Sections with no items: show contextual empty state with relevant icon and message (see § 3.8)

### 3.6 Invitation Card

- Same card styling but with accent left border (`border-l-4 border-primary`)
- Shows inviter name, project title
- Two action buttons: Accept (primary), Decline (ghost/outline)

### 3.7 Filters

- Search input: `w-64`, `h-10`, magnifying glass icon
- State dropdown: shadcn Select, options: All / Open / In Review / Accepted / Dropped / Rejected
- Ownership dropdown: shadcn Select, options: All / My Projects / Collaborating
- Type dropdown: shadcn Select, options: All / Software / Non-Software
- Filters row: `flex items-center gap-3`, below hero, above first list

### 3.8 Empty States

Each section shows a contextual empty state with a relevant Lucide icon and message:

- My Projects (empty): Lucide `FolderOpen` icon + "Create your first project" text
- Collaborating (empty): Lucide `Users` icon + contextual message
- Pending Invitations (empty): Lucide `Mail` icon + contextual message
- Trash (empty): Lucide `Trash2` icon + "Trash is empty" muted text
- No results (filtered): Lucide `SearchX` icon + "No projects match your filters" + clear filters link

### 3.9 Responsive

| Breakpoint | Change |
|-----------|--------|
| Tablet (md) | Cards stack single-column, hero padding reduces, modal project type cards stack vertically |
| Mobile (sm) | Filters stack vertically, search full-width, filter dropdowns full-width |

---

## 4. Project Workspace (`/project/<uuid>`)

This is the most complex page. It has two vertical zones:

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
| WORKSPACE HEADER (project title, type badge, controls, presence)        |
+---------+---------------------------------------------------------------+
|         |                                                               |
|  CHAT   |  STRUCTURED REQUIREMENTS PANEL                               |
|  PANEL  |                                                               |
|  (40%)  |  (60%)                                                        |
|         |                                                               |
|         |                                                               |
+---------+---------------------------------------------------------------+
  ^ fills viewport height (100vh - navbar - header)

======================== FOLD (scroll down) ==============================

+=========================================================================+
| REVIEW SECTION (below fold, full viewport height)                       |
|                                                                         |
|  Requirements Document Preview + State + Reviewer(s)                    |
|                                                                         |
|  TIMELINE (comments, state changes, resubmissions)                      |
|                                                                         |
+=========================================================================+
```

### 4.1 Workspace Header

```
+=========================================================================+
|  [< Back]   Project Title (editable) [SW]      [Interactive v]          |
|                                          [avatars] [+ Invite] [...]     |
+=========================================================================+
```

| Element | Detail |
|---------|--------|
| Back button | `<` icon + "Back" text, navigates to Landing Page |
| Project title | Gotham Bold, `text-xl` (20px), inline-editable (click to edit) |
| Type badge | Small pill badge, "SW" or "NON-SW", non-editable, positioned next to title |
| Agent mode dropdown | "Interactive" / "Silent", shadcn Select, `w-40` |
| Presence indicators | Avatar circles (28px), stacked with overlap (-8px margin), idle = dimmed, max 4 visible + "+N" overflow |
| Invite button | Ghost button, `+ Invite`, opens collaborator management |
| Three-dot menu | Dropdown: Share link, Delete project, (owner-only actions) |

- Header: `bg-surface`, `border-b`, `h-14`, `px-4`
- Sticky below navbar: `position: sticky; top: 56px; z-index: 30`

### 4.2 Define Section — Chat Panel (Left, 40%)

```
+----------------------------------------+
|                                        |
|  [AI] Welcome! Let's define the        |
|  requirements for your project.        |
|                         10:32 AM       |
|                                        |
|            Our invoice processing is   |
|            really slow. [You]          |
|            10:33 AM                    |
|                                        |
|  [AI] I understand. Let me structure   |
|  that...                               |   <-- delegation msg (de-emphasized)
|                         10:33 AM       |
|                                        |
|  [AI] Based on your company's         |
|  current systems, here's what I found: |
|  I've created [Epic: Invoice Process]  |   <-- requirements ref (clickable)
|  with initial user stories...          |
|                            10:34 AM    |   <-- AI reaction
|                                        |
|  --- AI is processing ---              |   <-- processing indicator
|                                        |
+----------------------------------------+
|  [ctx] Type a message... @       [>]   |
+----------------------------------------+
   ^context indicator (filling circle)
```

| Element | Styling |
|---------|---------|
| Message area | Scrollable, `overflow-y: auto`, `flex-1` |
| User messages | Aligned right, `bg-secondary` (teal), `text-white`, `rounded-md` with top-right square corner |
| AI messages | Aligned left, `bg-surface`, `border`, `rounded-md` with top-left square corner |
| Delegation messages | Same as AI but `opacity-60`, `text-sm`, `italic` (de-emphasized) |
| AI processing indicator | Centered, `text-sm`, `text-muted`, gentle pulse animation |
| Timestamps | `text-xs`, `text-muted`, below message |
| AI reactions | Small emoji below AI message, `text-xs` |
| User reactions | Clickable reaction row below other users' messages |
| Requirements references | Inline link, `text-primary` with underline, gold hover, scrolls to requirement in panel |
| @mention suggestions | Dropdown above input, `shadow-lg`, shows user list + @ai |
| Input area | `border-t`, `bg-surface`, `p-3` |
| Input field | `h-10`, full-width, `rounded-md` |
| Context indicator | Small filling circle icon (left of input), shows context window usage, tooltip on hover |
| Rate limit lockout | Input disabled, overlay message "AI is processing, please wait..." (F-2.11) |

### 4.3 Define Section — Structured Requirements Panel (Right Panel, 60%)

The right panel shows the hierarchical requirements structure based on project type.

**Process Steps:**
- **Define:** Chat + Requirements Panel side by side (current view)
- **Structure:** Full-width requirements editor with inline editing + PDF preview
- **Review:** Review section (below fold)

### 4.4 Requirements Panel — Software Project

For Software projects, shows Epics and User Stories in an accordion structure:

```
+---------------------------------------------------------------+
|  Requirements                                   [+ Add Epic]  |
+---------------------------------------------------------------+
|                                                               |
|  > Epic 1: User Authentication                         [ai]   |
|    --------------------------------------------------------   |
|    |  [::] US-1: Login with SSO                      [edit]|   |
|    |  [::] US-2: Password reset flow                 [edit]|   |
|    |  [+ Add User Story]                                  |   |
|    --------------------------------------------------------   |
|                                                               |
|  v Epic 2: Invoice Processing                          [ai]   |
|    --------------------------------------------------------   |
|    |  [::] US-3: Upload invoice document             [edit]|   |
|    |  [::] US-4: Extract data with OCR               [edit]|   |
|    |  [::] US-5: Validate against rules              [edit]|   |
|    |  [+ Add User Story]                                  |   |
|    --------------------------------------------------------   |
|                                                               |
|  > Epic 3: Reporting                                   [ai]   |
|    (collapsed)                                                |
|                                                               |
+---------------------------------------------------------------+
```

| Element | Styling |
|---------|---------|
| Header | `border-b`, `bg-surface`, `px-4 py-3`, Gotham Bold `text-base` |
| Add Epic button | Primary outline button, top-right of header |
| Epic row | `bg-surface`, `border`, `rounded-md`, `p-3`, collapsible |
| Epic title | Gotham Medium `text-sm`, inline-editable on click |
| Epic collapse icon | Lucide `ChevronRight` (collapsed) / `ChevronDown` (expanded) |
| AI badge | Small robot icon (Lucide `Bot`), top-right, for AI-created items |
| User Story row | `bg-muted/30`, `border-l-2 border-primary`, `p-2`, `mb-1` |
| Drag handle | `[::]` icon, left side, drag to reorder |
| Story title | Gotham Book `text-sm`, inline-editable |
| Edit button | Lucide `Pencil` icon, opens inline editor for full description |
| Add User Story | Text button, `text-primary`, bottom of expanded epic |
| Empty state | "No epics yet. Add your first epic to start." with icon |

### 4.5 Requirements Panel — Non-Software Project

For Non-Software projects, shows Milestones and Work Packages:

```
+---------------------------------------------------------------+
|  Requirements                              [+ Add Milestone]  |
+---------------------------------------------------------------+
|                                                               |
|  > Milestone 1: Planning Phase                         [ai]   |
|    --------------------------------------------------------   |
|    |  [::] WP-1: Stakeholder interviews              [edit]|   |
|    |  [::] WP-2: Requirements gathering              [edit]|   |
|    |  [+ Add Work Package]                                |   |
|    --------------------------------------------------------   |
|                                                               |
|  v Milestone 2: Implementation                         [ai]   |
|    --------------------------------------------------------   |
|    |  [::] WP-3: Vendor selection                    [edit]|   |
|    |  [::] WP-4: System configuration                [edit]|   |
|    |  [+ Add Work Package]                                |   |
|    --------------------------------------------------------   |
|                                                               |
+---------------------------------------------------------------+
```

- Same styling as Software panel, but with Milestones instead of Epics
- Work Packages (WP-N) instead of User Stories (US-N)

### 4.6 Requirements Panel — Shared Features

- Drag and drop: reorder epics/milestones, reorder stories/work packages within parent
- Inline editing: click title to edit in place
- AI indicators: gold glow on newly AI-modified items, fades after 3s
- Keyboard navigation: Arrow keys, Enter to expand/collapse, Tab to navigate
- Search/filter: search bar at top filters visible items (future enhancement)

### 4.7 Structure Step — Full-Width Requirements Editor

When user transitions from Define to Structure step, the layout changes:

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
| WORKSPACE HEADER (project title, type badge, controls)                  |
+=========================================================================+
|                                                                         |
|  STRUCTURED REQUIREMENTS EDITOR                                         |
|                                                                         |
|  +--Epics/Milestones------------------------+  +--PDF Preview-------+  |
|  |                                          |  |                    |  |
|  | > Epic 1: User Authentication            |  | Requirements Doc   |  |
|  |   [::] US-1: Login with SSO              |  |                    |  |
|  |   [::] US-2: Password reset              |  | [Document preview] |  |
|  |                                          |  |                    |  |
|  | v Epic 2: Invoice Processing             |  |                    |  |
|  |   [::] US-3: Upload invoice              |  |                    |  |
|  |   [::] US-4: Extract data                |  |                    |  |
|  |                                          |  |                    |  |
|  | [Inline detailed editors per item]      |  |                    |  |
|  |                                          |  |                    |  |
|  +------------------------------------------+  +--------------------+  |
|                                                                         |
|  [Regenerate Document]                         Progress: ####-- 4/6    |
|                                                                         |
|  +--Submit for Review---------------------------------------------------+|
|  |  Message (optional): [Add a note for the reviewer...            ]   ||
|  |  Assign reviewer: [Search reviewers...                      v]      ||
|  |                                                      [Submit >]      ||
|  +---------------------------------------------------------------------+|
|                                                                         |
+=========================================================================+
```

| Element | Styling |
|---------|---------|
| Layout | Side-by-side: Requirements editor (50%) + PDF preview (50%), draggable divider |
| Requirements editor | Same accordion structure as Define step, but with expanded inline editing |
| PDF preview | `bg-white` (always white for document), `border`, `rounded-md`, `shadow-sm`, scrollable |
| Regenerate button | Secondary button, triggers AI to rebuild document from requirements structure |
| Progress indicator | Horizontal bar, shows completeness of requirements |
| Submit area | `border-t`, `pt-4`, message textarea + reviewer selector + submit button |
| Submit button | Primary button, Gotham Bold |

### 4.8 Inline Requirement Editing

When editing a specific Epic/Milestone or User Story/Work Package, an inline editor expands:

```
+---------------------------------------------------------------+
|  Requirements                                   [+ Add Epic]  |
+---------------------------------------------------------------+
|                                                               |
|  v Epic 2: Invoice Processing                          [ai]   |
|    --------------------------------------------------------   |
|    |  [::] US-3: Upload invoice document             [edit]|   |
|    |                                                        |   |
|    |  +--Editing US-3--------------------------------+    |   |
|    |  | Title: Upload invoice document              |    |   |
|    |  | Description:                                 |    |   |
|    |  | [Rich text area with full details...]       |    |   |
|    |  |                                              |    |   |
|    |  | Acceptance Criteria:                         |    |   |
|    |  | [ ] User can select PDF/image files          |    |   |
|    |  | [ ] File size limit 10MB                     |    |   |
|    |  | [+ Add criterion]                            |    |   |
|    |  |                                              |    |   |
|    |  | [Regenerate] [lock]               [Save]    |    |   |
|    |  +----------------------------------------------+    |   |
|    |                                                        |   |
|    |  [::] US-4: Extract data with OCR               [edit]|   |
|    |  [::] US-5: Validate against rules              [edit]|   |
|    --------------------------------------------------------   |
|                                                               |
+---------------------------------------------------------------+
```

| Element | Detail |
|---------|--------|
| Expanded editor | Slides down within the epic/milestone accordion, full width |
| Title field | Single-line input, Gotham Medium `text-sm` |
| Description | Rich text area (markdown support), auto-growing |
| Acceptance criteria | Checkbox list, editable, add/remove items |
| Regenerate button | Lucide `RefreshCw`, AI rewrites based on chat context |
| Lock icon | Lucide `Lock` (locked, user-edited) / `LockOpen` (unlocked, AI can modify) |
| Save button | Primary button, saves and collapses editor |
| Cancel (X) | Discards changes, collapses editor |

### 4.9 Review Section (Below Fold)

Visible only after project has been submitted for review at least once.

```
+=========================================================================+
|                                                                         |
|  +---Doc Preview (small)-+  Invoice Processing     In Review   [SW]    |
|  |  [thumbnail]           |  Optimization                              |
|  |                         |  Reviewer: Anna Schmidt                    |
|  +-------------------------+                                            |
|                                                                         |
+----- TIMELINE -----------------------------------------------------------+
|                                                                         |
|  * Submitted for review                            Mar 1, 2026 10:45   |
|  |  "Please review these requirements for the finance dept."            |
|  |                                                                      |
|  * Anna Schmidt assigned herself                   Mar 1, 2026 11:02   |
|  |                                                                      |
|  * Anna Schmidt                                    Mar 1, 2026 14:30   |
|  |  "Can you clarify the expected time savings?"                        |
|  |    > John Doe: "We estimate 2 hours per invoice batch"               |
|  |    > Anna Schmidt: "Thanks, that helps."                             |
|  |                                                                      |
|  * Rejected -- rework needed                       Mar 2, 2026 09:15   |
|  |  "Please add more detail to the success criteria section."           |
|  |                                                                      |
|  * Resubmitted (v1 > v2)                          Mar 2, 2026 15:00   |
|  |  [Download v1]  [Download v2]                                        |
|  |                                                                      |
+=========================================================================+
```

| Element | Styling |
|---------|---------|
| Top area | `bg-surface`, `border-b`, `p-6`, always visible |
| Document thumbnail | Small preview image/card, `w-20 h-28`, `border`, `rounded-sm` |
| Project title | Gotham Bold `text-lg` |
| Type badge | Small pill badge, "SW" or "NON-SW" |
| State badge | Pill badge with project state color |
| Reviewer name(s) | Gotham Medium `text-sm` |
| Timeline | Vertical line (left border), entries as nodes |
| State change entries | `text-muted`, italic, system-generated |
| Comments | User avatar + name + timestamp + text, `bg-surface`, `border`, `rounded-md`, `p-4` |
| Nested replies | Indented 24px, connected to parent |
| Resubmission entries | Version links as download buttons, both old and new version |

### 4.10 Section Locking by Project State

| State | Define/Structure (top) | Review Section (bottom) |
|-------|--------------------|-----------------------|
| Open | Editable | Hidden |
| In Review | Locked (read-only, dimmed) | Active, scrolled to |
| Rejected | Editable (unlocked) | Visible (read-only) |
| Accepted | Read-only | Read-only, scrolled to |
| Dropped | Read-only | Read-only, scrolled to |

- Locked sections: `opacity-70`, no cursor changes, input fields `disabled`, overlay message "Project is in review"
- Auto-scroll: `scrollIntoView({ behavior: 'smooth' })` to the active section on state change (FA-1)

### 4.11 Responsive — Project Workspace

| Breakpoint | Layout Change |
|-----------|--------------|
| Desktop (xl+) | Side-by-side: 40% chat / 60% requirements panel, draggable divider |
| Tablet (lg) | Stacked panels OR tab-based toggle (chat <> requirements), no divider |
| Mobile (sm-md) | Tab-based toggle: Chat / Requirements / Review. Requirements panel scrollable with accordion collapsed by default. Full-width panels. |

---

## 5. Review Page (`/reviews`) — Reviewers Only

### 5.1 Desktop Layout

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
|                                                                         |
|                        max-w-5xl mx-auto                                |
|                                                                         |
|  Review Queue                                                           |
|  [Search by title or UUID...                                 ]          |
|                                                                         |
|  ASSIGNED TO ME                                                (N items)|
|  +-------------------------------------------------------------------+ |
|  |  Invoice Processing Optimization                          [SW]    | |
|  |     by John Doe * Submitted Mar 1         In Review    [Open >]   | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  HR Onboarding Digitization                            [NON-SW]   | |
|  |     by Maria K. * Submitted Feb 28        In Review    [Open >]   | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  UNASSIGNED                                                    (N items)|
|  +-------------------------------------------------------------------+ |
|  |  Facility Booking System                               [NON-SW]   | |
|  |     by Tom R. * Submitted Mar 2           In Review  [Assign v]   | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  > ACCEPTED                                                    (N items)|
|  > REJECTED                                                    (N items)|
|  > DROPPED                                                     (N items)|
|                                                                         |
+=========================================================================+
```

### 5.2 Review Card

```
+-------------------------------------------------------------------+
|                                                                   |
|  Project Title                                        [SW]        |
|     by Owner Name * Submitted [date]                              |
|                                                                   |
|                                          [State Badge]  [Action]  |
|                                                                   |
+-------------------------------------------------------------------+
```

| Element | Detail |
|---------|--------|
| Card | Same styling as landing page cards |
| Type badge | Small pill badge, "SW" or "NON-SW" |
| Author | Gotham Book `text-sm`, `text-secondary` |
| Date | Relative time |
| Action button | "Open >" for assigned projects, "Assign v" (self-assign) for unassigned |
| Click | Navigates to `/project/<uuid>` (scrolls to review section) |

### 5.3 Collapsed History Sections

- Accepted, Rejected, Dropped: collapsed by default
- Section header is clickable to expand/collapse
- Expand animation: `framer-motion` `AnimatePresence`, `height: auto`
- Collapsed: shows only section title + count badge

### 5.4 Conflict of Interest

- If a reviewer's own project appears in the queue, it shows a muted card with "Your project — cannot self-review" text, no action button

### 5.5 Responsive

| Breakpoint | Change |
|-----------|--------|
| Tablet (md) | Cards single-column, full width |
| Mobile (sm) | Same as tablet, search full-width |

---

## 6. Admin Panel (`/admin`) — Admins Only

### 6.1 Desktop Layout

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
|                                                                         |
|                        max-w-5xl mx-auto                                |
|                                                                         |
|  Admin Panel                                                            |
|                                                                         |
|  [AI Context]  [Parameters]  [Monitoring]  [Users]                      |
|  ----------------------------------------------------------------       |
|                                                                         |
|                    TAB CONTENT (below)                                   |
|                                                                         |
+=========================================================================+
```

- Tab bar: horizontal, Gotham Medium `text-sm`, icon + label per tab
- Active tab: gold underline, `text-primary`
- Tab content: padded area below tab bar
- Tab icons: AI Context = Lucide `Brain`, Parameters = Lucide `Settings`, Monitoring = Lucide `BarChart3`, Users = Lucide `Users`

### 6.2 AI Context Tab

```
+-------------------------------------------------------------------+
|                                                                   |
|  [Global]  [Software]  [Non-Software]                             |
|  ---------------------------------------------------------------  |
|                                                                   |
|  FACILITATOR CONTEXT                                              |
|  Instructions for the AI facilitator (applies to selected type)   |
|                                                                   |
|  +-------------------------------------------------------------+ |
|  |                                                             | |
|  |  [Rich text editor / textarea]                              | |
|  |                                                             | |
|  |  Facilitator instructions for this project type...          | |
|  |                                                             | |
|  +-------------------------------------------------------------+ |
|  [Save Changes]                                                   |
|                                                                   |
|  ---------------------------------------------------------------  |
|                                                                   |
|  COMPANY CONTEXT                                                  |
|  Detailed company information for context (applies to selected)   |
|                                                                   |
|  Section: Existing Applications                                   |
|  +-------------------------------------------------------------+ |
|  |  [Structured section editor]                                | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  Section: Domain Terminology                                      |
|  +-------------------------------------------------------------+ |
|  |  [Structured section editor]                                | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  Section: Company Structure                                       |
|  +-------------------------------------------------------------+ |
|  |  [Structured section editor]                                | |
|  +-------------------------------------------------------------+ |
|                                                                   |
|  Additional Context (Free Text)                                   |
|  +-------------------------------------------------------------+ |
|  |  [Textarea]                                                 | |
|  +-------------------------------------------------------------+ |
|  [Save Changes]                                                   |
|                                                                   |
+-------------------------------------------------------------------+
```

- Three sub-tabs: Global (applies to all), Software, Non-Software
- Each sub-tab shows both Facilitator and Company context for that scope
- Two clearly separated buckets with distinct headings
- Each bucket: heading + description + editor + save button
- Visual divider (`border-t` or `hr`) between buckets

### 6.3 Parameters Tab

```
+-------------------------------------------------------------------+
|                                                                   |
|  Runtime Parameters                                               |
|  Changes apply immediately to all active projects.                |
|                                                                   |
|  +------------------------------+----------+----------+---------+ |
|  | Parameter                    | Current  | Default  |  Action | |
|  +------------------------------+----------+----------+---------+ |
|  | State change cap             |    5     |    5     | [Edit]  | |
|  | Idle timeout                 |  5 min   |  5 min   | [Edit]  | |
|  | Idle disconnect              | 120 sec  | 120 sec  | [Edit]  | |
|  | Max reconnection backoff     |  30 sec  |  30 sec  | [Edit]  | |
|  | Soft delete countdown        | 30 days  | 30 days  | [Edit]  | |
|  | Debounce timer               |  3 sec   |  3 sec   | [Edit]  | |
|  | Context compression threshold|   60%    |   60%    | [Edit]  | |
|  | Default AI model             | gpt-4o   |  (dep)   | [Edit]  | |
|  | Escalated AI model           | gpt-4o   |  (dep)   | [Edit]  | |
|  | Default app language         | German   | German   | [Edit]  | |
|  | AI processing timeout        |  60 sec  |  60 sec  | [Edit]  | |
|  | Max retry attempts           |    3     |    3     | [Edit]  | |
|  | DLQ alert threshold          |   10     |   10     | [Edit]  | |
|  | Health check interval        |  60 sec  |  60 sec  | [Edit]  | |
|  +------------------------------+----------+----------+---------+ |
|                                                                   |
+-------------------------------------------------------------------+
```

- shadcn Table component
- Edit: inline edit on click (input replaces value cell) or opens small popover
- Modified values: gold left border on row to indicate changed from default
- Save: auto-save on blur / enter (no separate save button needed)

### 6.4 Monitoring Tab

```
+-------------------------------------------------------------------+
|                                                                   |
|  System Health                                      Last: 30s ago |
|                                                                   |
|  +----------+  +----------+  +----------+  +----------+          |
|  | Active   |  | Projects |  | Online   |  | AI Succ  |          |
|  | Conns    |  |          |  | Users    |  | Rate     |          |
|  |   147    |  |  1,234   |  |    89    |  | 98.2%    |          |
|  +----------+  +----------+  +----------+  +----------+          |
|                                                                   |
|  Projects by State                                                |
|  Open: ################---- 823                                   |
|  In Review: ####------------ 201                                  |
|  Accepted: ##-------------- 134                                   |
|  Dropped: #---------------- 52                                    |
|  Rejected: #--------------- 24                                    |
|                                                                   |
|  +-------------------------------------------------------------+ |
|  | Service Health                                               | |
|  +------------------------------+------+--------+--------------+ |
|  | Service                      | Status | Latency | Last Check | |
|  +------------------------------+------+--------+--------------+ |
|  | Gateway                      | OK   |  12ms  | 30s ago      | |
|  | AI Service                   | OK   |  45ms  | 30s ago      | |
|  | PDF Service                  | OK   |   8ms  | 30s ago      | |
|  | Database                     | OK   |   3ms  | 30s ago      | |
|  | Redis                        | OK   |   2ms  | 30s ago      | |
|  | Broker                       | OK   |   5ms  | 30s ago      | |
|  +------------------------------+------+--------+--------------+ |
|  DLQ Messages: 0                                                  |
|                                                                   |
|  Alert Recipients                                                 |
|  [admin@commerzreal.de] [ops@commerzreal.de] [+ Add]             |
|                                                                   |
+-------------------------------------------------------------------+
```

| Element | Styling |
|---------|---------|
| KPI cards | `bg-surface`, `border`, `rounded-md`, `p-4`, 4-column grid |
| KPI value | Gotham Bold `text-2xl` |
| KPI label | Gotham Book `text-sm`, `text-secondary` |
| State bars | Horizontal bars, colored by project state colors |
| Health table | shadcn Table, status dots use semantic colors |
| DLQ count | Highlighted `text-error` if above threshold |
| Alert recipients | Chip/badge list, toggle on/off, add button |

### 6.5 Users Tab

```
+-------------------------------------------------------------------+
|                                                                   |
|  User Lookup                                                      |
|  Search for a user to view their profile.                         |
|                                                                   |
|  [Search by name or email...                             ]        |
|                                                                   |
|  (search results appear below on query)                           |
|                                                                   |
|  +-------------------------------------------------------------+ |
|  |  John Doe                                                    | |
|  |     john.doe@commerzreal.de                                  | |
|  |     Roles: User, Reviewer                                    | |
|  |     Projects: 12  |  Reviews: 8  |  Contributions: 5        | |
|  +-------------------------------------------------------------+ |
|                                                                   |
+-------------------------------------------------------------------+
```

- Not eager-loaded — results only appear after search query
- User card: `bg-surface`, `border`, `rounded-md`, `p-4`
- Stats row: Gotham Medium `text-sm`, separated by `|` dividers
- Role badges: pill badges, color-coded (User = blue, Reviewer = gold, Admin = teal)

### 6.6 Responsive — Admin Panel

| Breakpoint | Change |
|-----------|--------|
| Tablet (md) | KPI cards 2x2 grid, tables scroll horizontally |
| Mobile (sm) | KPI cards single-column, tabs become a dropdown selector |

---

## 7. Login Page (`/login`)

```
+=========================================================================+
|                                                                         |
|                                                                         |
|                                                                         |
|                         [CR Logo - large]                               |
|                                                                         |
|                            ZiqReq                                       |
|                   Requirements Assembly Platform                        |
|                                                                         |
|                   [ Sign in with Microsoft ]                            |
|                                                                         |
|                                                                         |
|                                                                         |
+=========================================================================+
```

- Centered vertically and horizontally
- No navbar (unauthenticated)
- CR logo: large (80-120px height)
- "ZiqReq": Gotham Bold, `text-3xl` (30px)
- Subtitle: Gotham Book, `text-lg`, `text-secondary`
- Sign-in button: primary button style, Microsoft icon + label
- Background: `var(--background)`, can add subtle brand gradient or pattern
- Light/dark: respects `prefers-color-scheme` (no toggle available pre-auth) (FA-17)

---

## 8. Draggable Divider

The divider between Chat and Requirements panels in the Project Workspace:

```
        Chat (40%)      Requirements (60%)
            |               |
            |   |           |
            |   | <-- divider (draggable)
            |   |           |
            |               |
```

| Property | Value |
|----------|-------|
| Width | 4px visible, 12px hit area (for easier grabbing) |
| Color | `var(--border)` default, `var(--primary)` on hover/drag |
| Cursor | `col-resize` |
| Min panel width | Chat: 280px, Requirements Panel: 320px |
| Snap points | None — continuous drag |
| Persistence | Divider position saved in `localStorage` per user |
| Animation | None on drag (real-time), smooth `200ms` on double-click reset to 40/60 |

---

## 9. Floating Windows

### 9.1 Projects List (Navbar Button)

Triggered by clicking "Projects" in navbar. Floating panel, anchored below navbar.

```
+------- Floating Window (w-80, right-aligned) --------+
|  Projects                                     [x]    |
+------------------------------------------------------+
|  [Active]  [In Review]  [Accepted]  [Closed]         |
+------------------------------------------------------+
|                                                       |
|  Invoice Processing [SW]           Open              |
|  HR Onboarding [NON-SW]            Open              |
|  Shared Project (collab) [SW]      Open              |
|                                                       |
|  (empty tabs hidden)                                  |
|                                                       |
+------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `w-80` (320px) |
| Max height | `max-h-[70vh]`, scrollable |
| Position | Below navbar, anchored to "Projects" button |
| Shadow | `shadow-lg` |
| Radius | `rounded-lg` (12px) |
| Close | `x` button or click outside |
| Tabs | Active (open + rejected, own + collab), In Review, Accepted, Closed (dropped + trashed). Hidden when empty. |
| Items | Compact: title + type badge + state badge, click navigates to project |

### 9.2 Notification Bell Panel

```
+------- Floating Window (w-96, right-aligned) --------+
|  Notifications                                [x]    |
+------------------------------------------------------+
|                                                       |
|  Collaboration invitation from Max S.        2h ago   |
|     "Process Optimization"                            |
|     [Accept]  [Decline]                               |
|                                                       |
|  Review accepted: Invoice Processing         1d ago   |
|     Anna Schmidt accepted your project.               |
|                                                       |
|  @mention from Tom R.                        1d ago   |
|     "...can you check the budget section?"            |
|                                                       |
+------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `w-96` (384px) |
| Max height | `max-h-[70vh]`, scrollable |
| Position | Below bell icon, right-aligned |
| Badge | Gold circle, white text, count of unread |
| Items | Icon + title + time + description, action buttons where applicable |
| Acted-on | Notification dismissed after action taken |
| Click | Navigates to relevant context |

### 9.3 Email Preferences (Floating Window)

Triggered from user dropdown > "Email Preferences".

```
+------- Floating Window (w-96, centered) -------------+
|  Email Notification Preferences               [x]    |
+------------------------------------------------------+
|                                                       |
|  [ ] Collaboration                                    |
|     [x] Invitation received                           |
|     [x] Collaborator joined                           |
|     [x] Collaborator left                             |
|     [x] Removed from project                          |
|     [x] Ownership transferred                         |
|                                                       |
|  [ ] Review                                           |
|     [x] State changed (accepted/dropped/rejected)     |
|     [x] Comment on review                             |
|                                                       |
|  [ ] Chat                                             |
|     [x] @mentions                                     |
|                                                       |
|  (Reviewer-only, if applicable)                       |
|  [ ] Review Management                                |
|     [x] New project submitted                         |
|     [x] Project assigned to me                        |
|     ...                                               |
|                                                       |
|  (Admin-only, if applicable)                          |
|  [ ] System                                           |
|     [x] Monitoring alerts                             |
|                                                       |
+------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `w-96` (384px) |
| Group toggle | Switches all items on/off, indeterminate when mixed |
| Individual toggles | shadcn Switch or Checkbox per notification type |
| Auto-save | Changes save immediately (no save button) |
| Role-based | Reviewer and Admin sections only visible if user has those roles |

---

## 10. Modals

### 10.1 Error Log Modal

Triggered by "Show Logs" button on error toast (FA-14).

```
+------------- Modal (max-w-2xl, centered) ----------------+
|  Error Details                                    [x]    |
+----------------------------------------------------------+
|                                                          |
|  Operation: AI Processing (Facilitator)                  |
|  Timestamp: 2026-03-02 14:23:45 UTC                     |
|  Status: 500 Internal Server Error                       |
|                                                          |
|  Response:                                               |
|  +------------------------------------------------------+|
|  | {                                                    ||
|  |   "error": "model_overloaded",                       ||
|  |   "message": "The AI model is currently..."          ||
|  | }                                                    ||
|  +------------------------------------------------------+|
|                                                          |
|  Console Output:                                         |
|  +------------------------------------------------------+|
|  | [14:23:44] POST /api/projects/abc123/process           ||
|  | [14:23:45] Error: 500 -- model_overloaded             ||
|  +------------------------------------------------------+|
|                                                          |
|  If this persists, contact IT support at                 |
|  support@commerzreal.de                                  |
|                                                          |
|                              [Copy Details]  [Close]     |
+----------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `max-w-2xl` (672px) |
| Backdrop | `bg-black/50`, click-outside closes |
| Code blocks | Monospace font, `bg-muted`, `rounded-md`, scrollable |
| Copy button | Copies all error details to clipboard |

### 10.2 Collaborator Management

Triggered by "Invite" button in project workspace (FA-8).

```
+------------- Modal (max-w-md, centered) -----------------+
|  Collaborators                                    [x]    |
+----------------------------------------------------------+
|                                                          |
|  Invite:                                                 |
|  [Search users...                                ]       |
|                                                          |
|  Current Collaborators:                                  |
|  +------------------------------------------------------+|
|  | John Doe (Owner)                                     ||
|  | Anna Schmidt                    [Remove] [crown]     ||
|  | Tom Richter                     [Remove] [crown]     ||
|  +------------------------------------------------------+|
|                                                          |
|  Pending Invitations:                                    |
|  +------------------------------------------------------+|
|  | Maria K.                        [Revoke]             ||
|  +------------------------------------------------------+|
|                                                          |
+----------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `max-w-md` (448px) |
| Search | Autocomplete from user directory |
| Remove button | Ghost/destructive style |
| Transfer ownership icon | Lucide `Crown` icon, confirms on click |
| Owner badge | "Owner" label, non-removable |

---

## 11. Banners (Contextual, Project Workspace)

Banners appear between the workspace header and the panel content. They push content down.

### 11.1 Invitation Banner

```
+=========================================================================+
| Anna Schmidt invited you to collaborate on this project.                |
|                                               [Accept]  [Decline]      |
+=========================================================================+
```

- `bg-info-bg`, `border border-info`, `rounded-md`, `p-4`
- Full-width within workspace
- Accept: primary button. Decline: ghost button.
- Accept > become collaborator, banner disappears, project unlocks
- Decline > redirect to landing page

### 11.2 Offline Banner

```
+=========================================================================+
| Currently offline. Retrying in 12 seconds...             [Reconnect]   |
+=========================================================================+
```

- `bg-warning-bg`, `border border-warning`, `rounded-md`, `p-3`
- Countdown updates in real-time
- Reconnect button: primary style, triggers immediate reconnection
- On reconnection: banner fades out, state syncs

---

## 12. Toast Notifications

Position: top-right corner, stacked vertically, `z-60`.

```
                            +-------- Toast (w-80) --------+
                            | [check] PDF generated        |
                            |   successfully        [x]    |
                            +------------------------------+
```

| Type | Left Icon | Background | Border |
|------|-----------|-----------|--------|
| Success | Lucide `Check` | `var(--success-bg)` | `border-l-4 border-success` |
| Info | Lucide `Info` | `var(--info-bg)` | `border-l-4 border-info` |
| Warning | Lucide `AlertTriangle` | `var(--warning-bg)` | `border-l-4 border-warning` |
| Error | Lucide `X` | `var(--error-bg)` | `border-l-4 border-error` |

- Error toasts additionally show: `[Show Logs]` + `[Retry]` buttons (FA-14)
- Auto-dismiss: 5 seconds for success/info, persistent for warning/error
- Width: `w-80` (320px)
- Radius: `rounded-md` (8px)
- Shadow: `shadow-lg`
- Stacking: max 3 visible, older toasts pushed up

---

## 13. Responsive Behavior Summary

| Breakpoint | Navbar | Landing | Workspace | Review Page | Admin |
|-----------|--------|---------|-----------|-------------|-------|
| Desktop (xl+) | Full links | Card grid | Split panels 40/60 | Card grid | Tab layout |
| Tablet (lg) | Full links | 2-col grid | Tab toggle (chat/requirements) | 2-col grid | Tab layout |
| Tablet (md) | Hamburger | Single col | Tab toggle | Single col | Tabs > dropdown |
| Mobile (sm) | Hamburger | Single col | Tab toggle, requirements scrollable | Single col | Scrollable |

### 13.1 Mobile-Specific Patterns

- Hamburger menu: slide-in sheet from left, contains nav links
- Touch targets: minimum 44px on all interactive elements
- Swipe: supported on floating panels (swipe down to dismiss)
- Requirements panel: scrollable accordion on mobile, collapsed by default for better overview
- Bottom sheet: modals on mobile become bottom sheets (slide up from bottom)
