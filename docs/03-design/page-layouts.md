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
| [CR] ZiqReq   |  Ideas  Reviews*  Admin*  | *Online  [bell]3  [JD v]   |
+=========================================================================+
  ^brand block     ^nav links (role-gated)    ^utility items

  Left group                  Center/Right nav           Right utility
```

Detailed layout:

```
+=========================================================================+
|                                                                         |
|  [logo][16px] ZiqReq    [24px]   Ideas   Reviews   Admin               |
|                                                                         |
|                          *Online   [bell] 3   [avatar v]               |
|                                                                         |
+=========================================================================+
```

| Zone | Content | Alignment |
|------|---------|-----------|
| Left | CR ribbon logo (24px h) + "ZiqReq" (Gotham Bold 18px, white) | `flex items-center gap-4` |
| Center-Left | Nav links: Ideas, Reviews*, Admin* (Gotham Medium 14px) | `flex items-center gap-2` |
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
- Sheet contains: Ideas, Reviews*, Admin* as full-width links
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
|  |         "What workflow could be improved?"                        | |
|  |                                                                   | |
|  |    +-------------------------------------------------------+     | |
|  |    |  Start typing your idea...                        [>] |     | |
|  |    +-------------------------------------------------------+     | |
|  |                                                                   | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  +-- Search & Filters -----------------------------------------------+ |
|  |  [Search by title...        ]  [State v]  [Ownership v]          | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  MY IDEAS                                                    (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  * Idea Title                               Open    2h ago    ... | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  * Another Idea                          In Review   1d ago    ... | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  * Third Idea                            Accepted    3d ago    ... | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  COLLABORATING                                               (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  * Shared Idea (by Anna M.)                 Open    5h ago    ... | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  INVITATIONS                                                 (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  "Process Optimization" from Max S.       [Accept]  [Decline]     | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  TRASH                                                       (N items)  |
|  +-------------------------------------------------------------------+ |
|  |  Deleted Idea                    Deletes in 28d    [Restore]      | |
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
- Input: full-width, `h-12`, `rounded-md` (8px), `text-base`
- Input has a send/arrow icon button on the right
- On type + enter/click: creates new idea, navigates to `/idea/<uuid>`

### 3.3 Idea Card

```
+-------------------------------------------------------------------+
|                                                                   |
|  * Idea Title Text Here                                           |
|     Last updated 2 hours ago                                      |
|                                                                   |
|                                          [State Badge]    [...]   |
|                                                                   |
+-------------------------------------------------------------------+
```

- Card: `bg-surface`, `rounded-md` (8px), `shadow-sm`, `border`
- Padding: `16-20px`
- Title: Gotham Medium, `text-base`, `text-primary`
- Timestamp: Gotham Book, `text-sm`, `text-secondary`
- State badge: pill shape (`rounded-full`), `text-xs`, uses idea state colors
- Three-dot menu (`...`): opens dropdown with Delete (soft delete)
- Hover: `shadow-md`, `cursor-pointer`
- Click: navigates to `/idea/<uuid>`

### 3.4 Section Headers

- Gotham Bold, `text-lg` (18px), `text-primary`
- Item count on the right: `text-sm`, `text-muted`
- Bottom border: `border-b` for visual separation
- Sections with no items: show contextual empty state with relevant icon and message (see § 3.7)

### 3.5 Invitation Card

- Same card styling but with accent left border (`border-l-4 border-primary`)
- Shows inviter name, idea title
- Two action buttons: Accept (primary), Decline (ghost/outline)

### 3.6 Filters

- Search input: `w-64`, `h-10`, magnifying glass icon
- State dropdown: shadcn Select, options: All / Open / In Review / Accepted / Dropped / Rejected
- Ownership dropdown: shadcn Select, options: All / My Ideas / Collaborating
- Filters row: `flex items-center gap-3`, below hero, above first list

### 3.7 Empty States

Each section shows a contextual empty state with a relevant Lucide icon and message:

- My Ideas (empty): Lucide `Lightbulb` icon + "Start your first brainstorm" text
- Collaborating (empty): Lucide `Users` icon + contextual message
- Invitations (empty): Lucide `Mail` icon + contextual message
- Trash (empty): Lucide `Trash2` icon + "Trash is empty" muted text
- No results (filtered): Lucide `SearchX` icon + "No ideas match your filters" + clear filters link

### 3.8 Responsive

| Breakpoint | Change |
|-----------|--------|
| Tablet (md) | Cards stack single-column, hero padding reduces |
| Mobile (sm) | Filters stack vertically, search full-width, filter dropdowns full-width |

---

## 4. Idea Workspace (`/idea/<uuid>`)

This is the most complex page. It has two vertical zones:

```
+=========================================================================+
| NAVBAR                                                                  |
+=========================================================================+
| WORKSPACE HEADER (idea title, controls, presence)                       |
+---------+---------------------------------------------------------------+
|         |                                                               |
|  CHAT   |  BOARD TAB / REVIEW TAB                                      |
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
|  BRD Preview + State + Reviewer(s)                                      |
|                                                                         |
|  TIMELINE (comments, state changes, resubmissions)                      |
|                                                                         |
+=========================================================================+
```

### 4.1 Workspace Header

```
+=========================================================================+
|  [< Back]   Idea Title (editable)              [Interactive v]          |
|                                          [avatars] [+ Invite] [...]     |
+=========================================================================+
```

| Element | Detail |
|---------|--------|
| Back button | `<` icon + "Back" text, navigates to Landing Page |
| Idea title | Gotham Bold, `text-xl` (20px), inline-editable (click to edit) |
| Agent mode dropdown | "Interactive" / "Silent", shadcn Select, `w-40` |
| Presence indicators | Avatar circles (28px), stacked with overlap (-8px margin), idle = dimmed, max 4 visible + "+N" overflow |
| Invite button | Ghost button, `+ Invite`, opens collaborator management |
| Three-dot menu | Dropdown: Share link, Delete idea, (owner-only actions) |

- Header: `bg-surface`, `border-b`, `h-14`, `px-4`
- Sticky below navbar: `position: sticky; top: 56px; z-index: 30`

### 4.2 Brainstorming Section — Chat Panel (Left, 40%)

```
+----------------------------------------+
|                                        |
|  [AI] Welcome! What workflow would     |
|  you like to improve?                  |
|                         10:32 AM       |
|                                        |
|            Our invoice processing is   |
|            really slow. [You]          |
|            10:33 AM                    |
|                                        |
|  [AI] I understand. Let me look       |
|  into that...                          |   <-- delegation msg (de-emphasized)
|                         10:33 AM       |
|                                        |
|  [AI] Based on your company's         |
|  current systems, here's what I found: |
|  The invoice workflow uses [SAP FI]    |   <-- board ref (clickable)
|  module and involves...                |
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
| Board references | Inline link, `text-primary` with underline, gold hover |
| @mention suggestions | Dropdown above input, `shadow-lg`, shows user list + @ai |
| Input area | `border-t`, `bg-surface`, `p-3` |
| Input field | `h-10`, full-width, `rounded-md` |
| Context indicator | Small filling circle icon (left of input), shows context window usage, tooltip on hover |
| Rate limit lockout | Input disabled, overlay message "AI is processing, please wait..." (F-2.11) |

### 4.3 Brainstorming Section — Right Panel Tabs

```
+---------------------------------------------------------------+
|  [Board]  [Review]                                             |
+---------------------------------------------------------------+
|                                                                |
|            TAB CONTENT                                         |
|                                                                |
+---------------------------------------------------------------+
```

- Tab bar: `border-b`, Gotham Medium `text-sm`
- Active tab: gold underline (`border-b-2 border-primary`), `text-primary`
- Inactive tab: `text-muted`, hover: `text-secondary`
- Tab content fills remaining height below tab bar

### 4.4 Board Tab (Right Panel)

```
+---------------------------------------------------------------+
|  [Board]  [Review]                                             |
+---------------------------------------------------------------+
|  [+ Box] [Delete] [Fit] [Undo] [Redo]                         |
+-------+-------------------------------------------------+-----+
|       |                                                 |     |
|       |     +--Group: User Pain Points--------+         |     |
|       |     |                                  |         |     |
|       |     |  +--Box: Slow Invoices--+ [ai]   |         |     |
|       |     |  | * 3 day processing   |        |         |     |
|       |     |  | * Manual entry       |  [pin] |         |     |
|       |     |  +----------+-----------+        |         |     |
|       |     |             |                    |         |     |
|       |     |             | "causes"           |         |     |
|       |     |             v                    |         |  M  |
|       |     |  +--Box: Bottleneck-----+ [ai]   |         |  i  |
|       |     |  | * Approval delays    |        |         |  n  |
|       |     |  | * Missing signatures |  [pin] |         |  i  |
|       |     |  +----------------------+        |         |  m  |
|       |     |                                  |         |  a  |
|       |     +----------------------------------+         |  p  |
|       |                                                 |     |
|       |              Free Text: "Important note"        |     |
|       |                                                 |     |
+-------+-------------------------------------------------+-----+
  grid    ^^^^^^^^^canvas (React Flow)^^^^^^^^^^^^^^^^^    minimap
```

| Element | Styling |
|---------|---------|
| Toolbar | `border-b`, `bg-surface`, `h-10`, `px-2`, `flex items-center gap-1` |
| Toolbar buttons | Icon buttons, `h-8 w-8`, `rounded`, hover `bg-muted` |
| Undo/Redo labels | Context-aware: "Undo AI Action" when last action was AI (F-3.4) |
| Canvas | React Flow canvas, `bg-background` with dot grid pattern |
| Box nodes | `bg-surface`, `border`, `rounded-md` (8px), `shadow-sm`, `min-w-48` |
| Box title | Gotham Medium `text-sm`, `border-b`, `px-3 py-2` |
| Box body | Gotham Book `text-sm`, `px-3 py-2`, bullet list |
| Group nodes | `border-2 border-dashed`, `rounded-lg`, label at top-left |
| Free Text | No background/border, Gotham Book `text-sm`, directly on canvas |
| AI badge | Small robot icon (Lucide `Bot`), top-right of AI-created nodes |
| AI modified indicator | Gold dot/glow, fades on user selection |
| Lock icon | Lucide `Lock` small, bottom-right of locked nodes |
| Reference button | Lucide `Pin` icon, top-right corner of each node, inserts ref into chat |
| Connections | Smooth step edges, `stroke: var(--border-strong)`, label on double-click |
| Minimap | Bottom-right, `120x80px`, `border`, `rounded-sm`, `shadow-sm` |
| Zoom controls | Bottom-left, vertical button group: +, -, fit |
| User selection highlight | Colored border matching user avatar color, name tooltip |

### 4.5 Review Tab (Right Panel)

```
+---------------------------------------------------------------+
|  [Board]  [Review]                                             |
+---------------------------------------------------------------+
|                                                                |
|  +--PDF Preview-----------------------------------------+      |
|  |                                                      | [...] |
|  |   BUSINESS REQUIREMENTS DOCUMENT                     |      |
|  |   ===================================               |      |
|  |                                                      |      |
|  |   Title: Invoice Processing Optimization             |      |
|  |                                                      |      |
|  |   1. Short Description                               |      |
|  |   The invoice processing workflow at Commerz Real...  |      |
|  |                                                      |      |
|  |   2. Current Workflow & Pain Points                   |      |
|  |   ...                                                |      |
|  |                                                      |      |
|  +------------------------------------------------------+      |
|                                                                |
|  [Edit Document]           Progress: ####-- 4/6 ready          |
|                                                                |
|  +--Submit----------------------------------------------+      |
|  |  Message (optional):                                 |      |
|  |  +------------------------------------------------+  |      |
|  |  |  Add a note for the reviewer...                |  |      |
|  |  +------------------------------------------------+  |      |
|  |  Assign reviewer: [Search reviewers...        v]     |      |
|  |                                        [Submit >]    |      |
|  +------------------------------------------------------+      |
|                                                                |
+---------------------------------------------------------------+
```

| Element | Styling |
|---------|---------|
| PDF preview | `bg-white` (always white for document), `border`, `rounded-md`, `shadow-sm`, scrollable |
| Three-dot menu | Download PDF action |
| Edit button | Opens expandable edit area (slides left, overlaps chat panel) |
| Progress indicator | Horizontal bar, segmented per BRD section, filled = ready, empty = insufficient (F-4.8) |
| Submit area | `border-t`, `pt-4`, message textarea + reviewer selector + submit button |
| Submit button | Primary button, Gotham Bold |

### 4.6 Expandable Edit Area (Review Tab)

When "Edit Document" is clicked, the edit area slides in from the right, overlapping the chat panel:

```
+---------------------------------------------------------------+
|  [Board]  [Review]                                             |
+---------------------------------------------------------------+
| Edit BRD                                            [x Close]  |
+---------------------------------------------------------------+
|                                                                |
|  [ ] Allow Information Gaps                                    |
|                                                                |
|  1. Short Description                            [lock] [regen]|
|  +----------------------------------------------------------+ |
|  |  The invoice processing workflow at Commerz Real          | |
|  |  currently requires manual data entry...                  | |
|  +----------------------------------------------------------+ |
|                                                                |
|  2. Current Workflow & Pain Points               [open] [regen]|
|  +----------------------------------------------------------+ |
|  |  Not enough information.                                  | |
|  +----------------------------------------------------------+ |
|                                                                |
|  3. Affected Department / Business Area          [open] [regen]|
|  +----------------------------------------------------------+ |
|  |  Finance department, specifically the accounts            | |
|  |  payable team.                                            | |
|  +----------------------------------------------------------+ |
|                                                                |
|  [Regenerate unlocked sections]  [Instruction: __________ ]   |
|  [Regenerate PDF]                                              |
|  [Undo AI] [Redo AI]                                           |
|                                                                |
+---------------------------------------------------------------+
```

| Element | Detail |
|---------|--------|
| Slide animation | `framer-motion` slide from right, `width: 100%` of right panel (overlaps chat) |
| Close button | `x` icon, top-right, returns to PDF preview |
| Allow Info Gaps toggle | shadcn Switch component, top of edit area (F-4.9) |
| Section fields | Label + lock icon + regenerate icon per section |
| Lock icon | Lucide `Lock` (locked, user-edited, excluded from AI regen) / Lucide `LockOpen` (unlocked) (F-4.4) |
| Regenerate per section | Lucide `RefreshCw` icon button, only on unlocked sections |
| Section textarea | Auto-growing textarea, `text-base`, `border`, `rounded-md` |
| `/TODO` markers | Highlighted with `bg-warning/20 text-warning` inline |
| Regenerate all | Button, regenerates all unlocked sections |
| Instruction field | Optional text input for regeneration guidance |
| Undo/Redo AI | Local undo/redo for AI text changes only |

### 4.7 Review Section (Below Fold)

Visible only after idea has been submitted for review at least once.

```
+=========================================================================+
|                                                                         |
|  +---BRD Preview (small)--+  Invoice Processing     In Review          |
|  |  [thumbnail]           |  Optimization                              |
|  |                         |  Reviewer: Anna Schmidt                    |
|  +-------------------------+                                            |
|                                                                         |
+----- TIMELINE -----------------------------------------------------------+
|                                                                         |
|  * Submitted for review                            Mar 1, 2026 10:45   |
|  |  "Please review this improvement idea for the finance dept."         |
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
|  SIMILAR IDEAS                                                          |
|  +---------------------------------------------------------------+     |
|  |  "Payment Automation" -- 8 keyword matches                [>] |     |
|  |  "AP Workflow Digitization" -- 6 keyword matches          [>] |     |
|  +---------------------------------------------------------------+     |
|                                                                         |
+=========================================================================+
```

| Element | Styling |
|---------|---------|
| Top area | `bg-surface`, `border-b`, `p-6`, always visible |
| BRD thumbnail | Small preview image/card, `w-20 h-28`, `border`, `rounded-sm` |
| State badge | Pill badge with idea state color |
| Reviewer name(s) | Gotham Medium `text-sm` |
| Timeline | Vertical line (left border), entries as nodes |
| State change entries | `text-muted`, italic, system-generated |
| Comments | User avatar + name + timestamp + text, `bg-surface`, `border`, `rounded-md`, `p-4` |
| Nested replies | Indented 24px, connected to parent |
| Resubmission entries | Version links as download buttons, both old and new version |
| Similar ideas | Section at bottom, cards with title + keyword match count, click to navigate (FA-5) |

### 4.8 Section Locking by Idea State

| State | Brainstorming (top) | Review Section (bottom) |
|-------|--------------------|-----------------------|
| Open | Editable | Hidden |
| In Review | Locked (read-only, dimmed) | Active, scrolled to |
| Rejected | Editable (unlocked) | Visible (read-only) |
| Accepted | Read-only | Read-only, scrolled to |
| Dropped | Read-only | Read-only, scrolled to |

- Locked sections: `opacity-70`, no cursor changes, input fields `disabled`, overlay message "Idea is in review"
- Auto-scroll: `scrollIntoView({ behavior: 'smooth' })` to the active section on state change (FA-1)

### 4.9 Responsive — Idea Workspace

| Breakpoint | Layout Change |
|-----------|--------------|
| Desktop (xl+) | Side-by-side: 40% chat / 60% board, draggable divider |
| Tablet (lg) | Stacked panels OR tab-based toggle (chat <> board), no divider |
| Mobile (sm-md) | Tab-based toggle: Chat / Board (read-only) / Review. Board is view-only on mobile. Full-width panels. |

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
|  |  Invoice Processing Optimization                                  | |
|  |     by John Doe * Submitted Mar 1         In Review    [Open >]   | |
|  +-------------------------------------------------------------------+ |
|  +-------------------------------------------------------------------+ |
|  |  HR Onboarding Digitization                                       | |
|  |     by Maria K. * Submitted Feb 28        In Review    [Open >]   | |
|  +-------------------------------------------------------------------+ |
|                                                                         |
|  UNASSIGNED                                                    (N items)|
|  +-------------------------------------------------------------------+ |
|  |  Facility Booking System                                          | |
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
|  Idea Title                                                       |
|     by Owner Name * Submitted [date]                              |
|                                                                   |
|                                          [State Badge]  [Action]  |
|                                                                   |
+-------------------------------------------------------------------+
```

| Element | Detail |
|---------|--------|
| Card | Same styling as landing page cards |
| Author | Gotham Book `text-sm`, `text-secondary` |
| Date | Relative time |
| Action button | "Open >" for assigned ideas, "Assign v" (self-assign) for unassigned |
| Click | Navigates to `/idea/<uuid>` (scrolls to review section) |

### 5.3 Collapsed History Sections

- Accepted, Rejected, Dropped: collapsed by default
- Section header is clickable to expand/collapse
- Expand animation: `framer-motion` `AnimatePresence`, `height: auto`
- Collapsed: shows only section title + count badge

### 5.4 Conflict of Interest

- If a reviewer's own idea appears in the queue, it shows a muted card with "Your idea — cannot self-review" text, no action button

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
|  FACILITATOR BUCKET                                               |
|  Table of contents describing available company context           |
|                                                                   |
|  +-------------------------------------------------------------+ |
|  |                                                             | |
|  |  [Rich text editor / textarea]                              | |
|  |                                                             | |
|  |  Contents of the facilitator bucket...                      | |
|  |                                                             | |
|  +-------------------------------------------------------------+ |
|  [Save Changes]                                                   |
|                                                                   |
|  ---------------------------------------------------------------  |
|                                                                   |
|  CONTEXT AGENT BUCKET                                             |
|  Detailed company information for the context agent               |
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

- Two clearly separated buckets with distinct headings
- Each bucket: heading + description + editor + save button
- Visual divider (`border-t` or `hr`) between buckets

### 6.3 Parameters Tab

```
+-------------------------------------------------------------------+
|                                                                   |
|  Runtime Parameters                                               |
|  Changes apply immediately to all active ideas.                   |
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
|  | Max keywords per idea        |   20     |   20     | [Edit]  | |
|  | Min keyword overlap          |    7     |    7     | [Edit]  | |
|  | Similarity time limit        | 6 months | 6 months | [Edit]  | |
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
|  | Active   |  | Ideas    |  | Online   |  | AI Succ  |          |
|  | Conns    |  |          |  | Users    |  | Rate     |          |
|  |   147    |  |  1,234   |  |    89    |  | 98.2%    |          |
|  +----------+  +----------+  +----------+  +----------+          |
|                                                                   |
|  Ideas by State                                                   |
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
| State bars | Horizontal bars, colored by idea state colors |
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
|  |     Ideas: 12  |  Reviews: 8  |  Contributions: 5            | |
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
|                   AI-Guided Brainstorming                               |
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

The divider between Chat and Board/Review panels in the Idea Workspace:

```
        Chat (40%)      Board (60%)
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
| Min panel width | Chat: 280px, Board: 320px |
| Snap points | None — continuous drag |
| Persistence | Divider position saved in `localStorage` per user |
| Animation | None on drag (real-time), smooth `200ms` on double-click reset to 40/60 |

---

## 9. Floating Windows

### 9.1 Ideas List (Navbar Button)

Triggered by clicking "Ideas" in navbar. Floating panel, anchored below navbar.

```
+------- Floating Window (w-80, right-aligned) --------+
|  Ideas                                        [x]    |
+------------------------------------------------------+
|  [Active]  [In Review]  [Accepted]  [Closed]         |
+------------------------------------------------------+
|                                                       |
|  Invoice Processing                    Open           |
|  HR Onboarding                         Open           |
|  Shared Idea (collab)                  Open           |
|                                                       |
|  (empty tabs hidden)                                  |
|                                                       |
+------------------------------------------------------+
```

| Property | Value |
|----------|-------|
| Width | `w-80` (320px) |
| Max height | `max-h-[70vh]`, scrollable |
| Position | Below navbar, anchored to "Ideas" button |
| Shadow | `shadow-lg` |
| Radius | `rounded-lg` (12px) |
| Close | `x` button or click outside |
| Tabs | Active (open + rejected, own + collab), In Review, Accepted, Closed (dropped + trashed). Hidden when empty. |
| Items | Compact: title + state badge, click navigates to idea |

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
|     Anna Schmidt accepted your idea.                  |
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
|     [x] Removed from idea                             |
|     [x] Ownership transferred                         |
|                                                       |
|  [ ] Review                                           |
|     [x] State changed (accepted/dropped/rejected)     |
|     [x] Comment on review                             |
|                                                       |
|  [ ] Chat                                             |
|     [x] @mentions                                     |
|                                                       |
|  [ ] Similarity                                       |
|     [x] Similar idea detected                         |
|     [x] Merge request                                 |
|     [x] Merge accepted/declined                       |
|                                                       |
|  (Reviewer-only, if applicable)                       |
|  [ ] Review Management                                |
|     [x] New idea submitted                            |
|     [x] Idea assigned to me                           |
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
|  | [14:23:44] POST /api/ideas/abc123/process             ||
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

Triggered by "Invite" button or collaborator dropdown in workspace (FA-8).

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

## 11. Banners (Contextual, Idea Workspace)

Banners appear between the workspace header and the panel content. They push content down.

### 11.1 Invitation Banner

```
+=========================================================================+
| Anna Schmidt invited you to collaborate on this idea.                   |
|                                               [Accept]  [Decline]      |
+=========================================================================+
```

- `bg-info-bg`, `border border-info`, `rounded-md`, `p-4`
- Full-width within workspace
- Accept: primary button. Decline: ghost button.
- Accept > become collaborator, banner disappears, idea unlocks
- Decline > redirect to landing page

### 11.2 Merge Request Banner

```
+=========================================================================+
| Merge request from "Payment Automation" (by Tom R.)                     |
|    Your idea is locked until you respond.                               |
|                                               [Accept]  [Decline]      |
+=========================================================================+
```

- `bg-warning-bg`, `border border-warning`, `rounded-md`, `p-4`
- Idea is locked while banner is shown
- Accept > merge proceeds. Decline > permanently dismissed, idea unlocks.

### 11.3 Offline Banner

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
| Tablet (lg) | Full links | 2-col grid | Tab toggle (chat/board) | 2-col grid | Tab layout |
| Tablet (md) | Hamburger | Single col | Tab toggle | Single col | Tabs > dropdown |
| Mobile (sm) | Hamburger | Single col | Tab toggle, board read-only | Single col | Scrollable |

### 13.1 Mobile-Specific Patterns

- Hamburger menu: slide-in sheet from left, contains nav links
- Touch targets: minimum 44px on all interactive elements
- Swipe: supported on floating panels (swipe down to dismiss)
- Board: read-only on mobile — zoom and pan only, no editing
- Bottom sheet: modals on mobile become bottom sheets (slide up from bottom)
