# Component Specifications

All components use shadcn/ui (Radix primitives) customized with the design tokens from `design-system.md`. This document specifies variants, states, and visual behavior for every reusable component.

---

## 1. Buttons

### 1.1 Variants

| Variant | Light Mode | Dark Mode | Usage |
|---------|-----------|-----------|-------|
| **Primary** | `bg-secondary text-white` (#002E3C) | `bg-primary text-primary-foreground` (#FFD700 / #002E3C) | Main actions: Submit, Save, Accept, Sign In |
| **Secondary** | `bg-muted text-foreground` | `bg-muted text-foreground` | Secondary actions: Cancel, Edit, Assign |
| **Ghost** | `bg-transparent text-foreground` hover: `bg-muted` | `bg-transparent text-foreground` hover: `bg-muted` | Inline actions: toolbar buttons, close, menu items |
| **Outline** | `border border-border text-foreground` | `border border-border text-foreground` | Alternative secondary: filter toggles, options |
| **Destructive** | `bg-destructive text-white` | `bg-destructive text-white` | Dangerous actions: Delete, Drop, Remove |
| **Link** | `text-secondary underline` | `text-primary underline` | Inline text actions, navigation |

### 1.2 Sizes

| Size | Height | Padding | Font | Icon | Usage |
|------|--------|---------|------|------|-------|
| `sm` | 32px | `px-3` | 14px Medium | 16px | Compact contexts: toolbar, table actions, badges |
| `default` | 40px | `px-4` | 14px Medium | 20px | Standard buttons throughout the app |
| `lg` | 48px | `px-6` | 16px Bold | 20px | Hero actions: Submit for Review, Sign In |
| `icon` | 40px | `p-2` (square) | — | 20px | Icon-only buttons: close, menu, toolbar |
| `icon-sm` | 32px | `p-1.5` (square) | — | 16px | Small icon buttons: reactions, lock toggle |

### 1.3 States

| State | Visual Change |
|-------|--------------|
| Default | Base variant styling |
| Hover | Background shifts one step darker/lighter, `transition-colors duration-150` |
| Active/Pressed | Background shifts two steps, `scale-[0.98]` (subtle press) |
| Focus | Gold ring: `ring-2 ring-primary ring-offset-2` |
| Disabled | `opacity-50`, `cursor-not-allowed`, no hover effect |
| Loading | Spinner icon replaces left icon or text, `disabled` state, label changes to "Submitting..." etc. |

### 1.4 Icon Buttons

- Icons from Lucide React, `currentColor`
- Icon-only buttons require `aria-label`
- Tooltip on hover showing the action name (shadcn Tooltip, 300ms delay)

---

## 2. Cards

### 2.1 Base Card

| Property | Value |
|----------|-------|
| Background | `var(--card)` |
| Border | `1px solid var(--border)` |
| Radius | `rounded-md` (8px) |
| Shadow | `shadow-sm` (light), `ring-1 ring-white/[0.06]` (dark) |
| Padding | `16-20px` (context-dependent) |
| Hover | `shadow-md`, `cursor-pointer` (if clickable) |
| Transition | `transition-all duration-150` |

### 2.2 Idea Card (Landing Page, Ideas List)

```
+-------------------------------------------------------------------+
|  [State dot] Idea Title                         [State Badge] [...] |
|  Last updated 2 hours ago                                         |
+-------------------------------------------------------------------+
```

| Element | Spec |
|---------|------|
| State dot | 8px circle, idea state color, left of title |
| Title | Gotham Medium, `text-base`, `text-foreground`, single-line truncate with ellipsis |
| Timestamp | Gotham Book, `text-sm`, `text-muted-foreground` |
| State badge | See Badge component (Section 3) |
| Three-dot menu | Ghost icon button, dropdown: Delete / Restore |
| Selected state | Gold left border: `border-l-4 border-primary` |

### 2.3 Review Card (Review Page)

```
+-------------------------------------------------------------------+
|  [State dot] Idea Title                                           |
|  by Owner Name * Submitted Mar 1               [Badge]  [Action] |
+-------------------------------------------------------------------+
```

- Extends base Idea Card with author and submit date
- Action button: "Open" (outline) or "Assign" (primary) depending on context

### 2.4 User Card (Admin Panel)

```
+-------------------------------------------------------------------+
|  [Avatar] Full Name                                               |
|           email@commerzreal.de                                    |
|           [User] [Reviewer] [Admin]                               |
|           12 ideas  |  8 reviews  |  5 contributions             |
+-------------------------------------------------------------------+
```

- Avatar: 40px, `rounded-full`
- Role badges: small pills, color-coded
- Stats: `text-sm`, separated by `|`

### 2.5 KPI Card (Admin Monitoring)

```
+------------------+
|  Label           |
|  1,234           |
|  ^ 12% vs last   |
+------------------+
```

| Element | Spec |
|---------|------|
| Card | `bg-card`, `border`, `rounded-md`, `p-4` |
| Label | Gotham Book, `text-sm`, `text-muted-foreground` |
| Value | Gotham Bold, `text-2xl`, `text-foreground` |
| Trend | `text-xs`, `text-success` (up) or `text-destructive` (down), optional |

---

## 3. Badges

### 3.1 State Badges

| State | Light Mode | Dark Mode | Shape |
|-------|-----------|-----------|-------|
| Open | `bg-sky-100 text-sky-700` | `bg-sky-900/30 text-sky-400` | Pill |
| In Review | `bg-amber-100 text-amber-700` | `bg-amber-900/30 text-amber-400` | Pill |
| Accepted | `bg-green-100 text-green-700` | `bg-green-900/30 text-green-400` | Pill |
| Dropped | `bg-gray-100 text-gray-600` | `bg-gray-800 text-gray-400` | Pill |
| Rejected | `bg-orange-100 text-orange-700` | `bg-orange-900/30 text-orange-400` | Pill |

- Size: `text-xs`, `px-2 py-0.5`, Gotham Medium
- Shape: `rounded-full`
- State dot: Optional 6px circle before text (same color)

### 3.2 Role Badges

| Role | Color |
|------|-------|
| User | `bg-blue-100 text-blue-700` / `bg-blue-900/30 text-blue-400` |
| Reviewer | `bg-yellow-100 text-yellow-800` / `bg-yellow-900/30 text-yellow-400` |
| Admin | `bg-teal-100 text-teal-700` / `bg-teal-900/30 text-teal-400` |

### 3.3 Notification Count Badge

- Position: absolute, top-right of bell icon
- Size: `min-w-5 h-5`, `rounded-full`
- Color: `bg-primary text-primary-foreground` (gold/teal)
- Font: Gotham Bold, `text-xs`
- Max display: "99+" for counts over 99
- Animation: `scale-in` on new notification (100ms) — **Note:** Tailwind v4 uses `@theme` and has no `tailwind.config.js`, so custom animations must be defined in `globals.css` using `@keyframes` and `animation` property

### 3.4 AI Badge

- Small Lucide `Bot` icon overlay on AI-created board items
- Position: top-right corner of node
- Size: 16px
- Color: `text-muted-foreground`
- Tooltip: "Created by AI"

---

## 4. Form Elements

### 4.1 Text Input

| Property | Value |
|----------|-------|
| Height | `h-10` (40px) |
| Padding | `px-3` |
| Font | Gotham Book, `text-base` (16px) — minimum 16px to prevent iOS zoom |
| Border | `1px solid var(--input)` |
| Radius | `rounded` (6px) |
| Background | `var(--card)` |
| Placeholder | `text-muted-foreground` |
| Focus | `ring-2 ring-primary ring-offset-1` (gold ring) |
| Error | `border-destructive`, `ring-destructive` on focus |
| Disabled | `opacity-50`, `cursor-not-allowed`, `bg-muted` |

### 4.2 Textarea

- Same as input but with `min-h-20`, `py-2`
- Auto-grow variant: grows with content up to max height, then scrolls
- Used for: chat input, BRD section editing, review comments, admin text editors

### 4.3 Select (Dropdown)

- shadcn Select (Radix)
- Same border, radius, height as Input
- Trigger: input-style with Lucide `ChevronDown` icon
- Dropdown: `bg-popover`, `shadow-lg`, `rounded-md`, `border`
- Items: `px-3 py-2`, hover `bg-muted`, `rounded-sm`
- Selected: gold checkmark icon

### 4.4 Switch (Toggle)

- shadcn Switch (Radix)
- Size: `w-10 h-5`
- Off: `bg-muted` track
- On: `bg-primary` (gold) track with `bg-white` thumb
- Focus: gold ring
- Used for: Email preference toggles, Allow Information Gaps (F-4.9), alert opt-in

### 4.5 Checkbox

- shadcn Checkbox (Radix)
- Size: `w-5 h-5`
- Unchecked: `border-2 border-input`, `rounded-sm` (3px)
- Checked: `bg-primary`, gold checkmark
- Indeterminate: `bg-primary`, gold dash (for group toggles)
- Focus: gold ring

### 4.6 Search Input

- Extends Text Input with Lucide `Search` icon (left)
- Icon: 16px, `text-muted-foreground`
- Clear button: Lucide `X` icon appears when input has value
- Debounce: 300ms before search triggers

### 4.7 Form Layout

- shadcn Form + React Hook Form + Zod validation
- Label: Gotham Medium, `text-sm`, above input
- Description: Gotham Book, `text-sm`, `text-muted-foreground`, below label
- Error message: `text-sm`, `text-destructive`, below input, `FormMessage` component
- Spacing: `16px` between form groups

---

## 5. Chat Components

### 5.1 User Message Bubble

```
+---------------------------------------------+
|  Message content here. This is what the     |
|  user typed in chat.                        |
|                                   10:33 AM  |
+---------------------------------------------+
                                    [Name]
```

| Property | Value |
|----------|-------|
| Alignment | Right-aligned |
| Background | `var(--secondary)` (teal light / gold dark) |
| Text | `var(--secondary-foreground)` (white light / teal dark) |
| Radius | `rounded-md` with top-right corner: `rounded-tr-sm` (3px) — chat bubble shape |
| Max width | 70% of chat panel width |
| Padding | `12px` |
| Sender name | `text-xs`, `text-muted-foreground`, below bubble, only shown in multi-user mode |
| Timestamp | `text-[10px]`, `opacity-70`, inside bubble bottom-right |

### 5.2 AI Message Bubble

```
[AI]
+---------------------------------------------+
|  AI response content here. Can include      |
|  board references like [SAP FI Module]      |
|  which are clickable links.                 |
|                                   10:34 AM  |
+---------------------------------------------+
```

| Property | Value |
|----------|-------|
| Alignment | Left-aligned |
| Background | `var(--card)` |
| Border | `1px solid var(--border)` |
| Text | `var(--card-foreground)` |
| Radius | `rounded-md` with top-left corner: `rounded-tl-sm` (3px) |
| Max width | 70% of chat panel width |
| AI label | Lucide `Bot` icon + "AI", `text-xs`, above bubble |
| Board references | `text-primary` (teal/gold), underline, clickable |
| AI reactions | Small emoji chips below bubble (F-2.7) |

### 5.3 Delegation Message (De-emphasized)

- Same layout as AI message
- `opacity-60`, `text-sm`, `italic`
- No full bubble background — lighter border or no border
- Example: "I'm researching this, I'll get back to you shortly."
- When the actual response arrives, delegation message visually shrinks further

### 5.4 AI Processing Indicator

```
--- AI is processing * * * ---
```

- Centered in chat panel
- `text-sm`, `text-muted-foreground`
- Gentle pulse animation: `animate-pulse` (opacity oscillation)
- Three animated dots variant: sequential fade
- `prefers-reduced-motion`: static text "AI is processing", no animation (NFR-A5)

### 5.5 Reaction Chips

| Reaction | Emoji | Usage |
|----------|-------|-------|
| Thumbs up | thumbs up | Acknowledgment |
| Thumbs down | thumbs down | Disagreement |
| Heart | heart | Full clarity / appreciation |

- Size: `text-sm`, `px-1.5 py-0.5`
- Background: `bg-muted`, `rounded-full`
- Hover (user reactions): `bg-muted` darken, `cursor-pointer`
- AI reactions: not clickable, display-only (F-2.7)
- User reaction row: appears below other users' messages, not AI messages (F-2.8)
- User can click to toggle reaction (add/remove)

### 5.6 @Mention Dropdown

- Triggered by typing `@` in chat input
- Position: above input, `shadow-lg`, `rounded-md`, `border`
- Items: initial circle (or avatar) + display name, `px-3 py-2`
- First item: `@ai` with Lucide `Bot` icon
- Remaining: users in current idea, alphabetical
- Keyboard navigation: arrow keys + enter to select
- Filter: typing after `@` filters the list

### 5.7 Context Window Indicator

- Position: left side of chat input area
- Visual: small filling circle icon (like a pie chart / progress ring)
- Size: 20px
- Color: `text-muted-foreground`, fill `var(--primary)` (gold) proportional to usage
- Hover: tooltip with details (compression iterations, context size, percentage)
- Threshold warning: circle turns `var(--warning)` when near capacity

### 5.8 Chat Input Area

```
+---------------------------------------------------+
| [ctx] [Type a message... @                    ] [>] |
+---------------------------------------------------+
```

| Element | Spec |
|---------|------|
| Container | `border-t`, `bg-card`, `p-3`, `flex items-center gap-2` |
| Context indicator | 20px circle, left position |
| Input | `flex-1`, `h-10`, `rounded`, `border`, Gotham Book `text-base` |
| Send button | Primary icon button, Lucide `ArrowRight` icon, disabled when input is empty |
| Rate limit lockout | Overlay: `bg-card/80`, centered text "Chat locked — AI is processing", input disabled (F-2.11) |
| Brainstorming lock | `LockOverlay` wraps entire chat panel (not just input) when idea state is locked (`in_review`, `accepted`, `dropped`). Overlay with `bg-card/80`, lock icon + explanation text. Provides clearer visual indication than disabling input alone. |

---

## 6. Board Components

### 6.1 Box Node

```
+--Title Here------------------+ [pin] [ai]
|  * Bullet point one          |
|  * Bullet point two          |
|  * Bullet point three        |
+------------------------------+ [lock]
```

| Property | Value |
|----------|-------|
| Background | `var(--card)` |
| Border | `1px solid var(--border)` |
| Radius | `rounded-md` (8px) |
| Shadow | `shadow-sm` |
| Min width | 192px |
| Max width | 320px (auto-wraps beyond) |
| Title bar | `border-b`, `px-3 py-2`, Gotham Medium `text-sm` |
| Body | `px-3 py-2`, Gotham Book `text-sm`, bullet list |
| Reference button | Lucide `Pin` icon, top-right, ghost `icon-sm`, inserts ref into chat |
| AI badge | Lucide `Bot` icon, top-right (next to reference), only on AI-created nodes |
| Lock icon | Lucide `Lock`, bottom-right, `icon-sm`, toggleable (F-4.4) |
| AI modified indicator | Gold dot (8px), absolute top-left, `animate-pulse`, fades on user selection (F-3.4) |
| Selected by other user | `border-2` in user's color, small name label above node |
| Editing state | `border-2 border-primary` (gold border while editing) |

### 6.2 Group Node

| Property | Value |
|----------|-------|
| Border | `2px dashed var(--border-strong)` |
| Radius | `rounded-lg` (12px) |
| Background | `var(--muted)` at `opacity-30` (subtle tint) |
| Label | Top-left, Gotham Medium `text-xs`, `bg-muted px-2 py-0.5 rounded` badge |
| Min size | 200x150px |
| Resize | All corners and edges (React Flow handles) |
| Children | Boxes, Free Text, nested Groups move with parent |

### 6.3 Free Text Node

| Property | Value |
|----------|-------|
| Background | None (transparent) |
| Border | None (only visible border on hover/select: `1px dashed var(--border)`) |
| Font | Gotham Book `text-sm`, `text-foreground` |
| Editing | Click to edit, `textarea` overlay with auto-grow |

### 6.4 Connections (Edges)

| Property | Value |
|----------|-------|
| Type | Smooth step (React Flow `smoothstep`) |
| Stroke | React Flow default (neutral gray), 1.5px |
| Hover | Stroke widens to 2.5px, color shifts to `var(--foreground)` |
| Label | On double-click: editable sticky text, `bg-card`, `border`, `rounded-sm`, `text-xs` |
| Arrow | Small arrowhead on target end |
| Selected | `stroke: var(--primary)` (gold), 2.5px |

### 6.5 Board Toolbar

```
[+ Box] [Delete] [Fit] [Undo AI Action] [Redo]
```

| Button | Icon | Tooltip | Behavior |
|--------|------|---------|----------|
| Add Box | Lucide `Plus` | "Add Box" | Creates new Box at center of viewport |
| Delete | Lucide `Trash2` | "Delete Selected" | Deletes selected nodes/edges, disabled when nothing selected |
| Fit View | Lucide `Maximize2` | "Fit View" | Zooms to fit all content |
| Undo | Lucide `Undo2` | Context-aware: "Undo AI Action" or "Undo" | Undoes last action (F-3.4) |
| Redo | Lucide `Redo2` | Context-aware: "Redo AI Action" or "Redo" | Redoes last undone action |

- Buttons: ghost style, `icon-sm` (32px), `rounded`
- Dividers: vertical `border-l` between groups (Add | Delete | Fit | Undo/Redo)
- Disabled state: `opacity-40` when action unavailable (e.g., Undo when no history)
- Toolbar: `border-b`, `bg-card`, `h-10`, `px-2`, `flex items-center gap-1`

### 6.6 Board Canvas

| Property | Value |
|----------|-------|
| Background | `var(--background)` with dot grid pattern (`1px dots, 20px gap, opacity-20`) |
| Zoom | Scroll wheel, pinch on mobile. Range: 25%-200% |
| Pan | Middle-click drag, or scroll with shift/alt |
| Minimap | Bottom-right, `120x80px`, `border`, `rounded-sm`, `shadow-sm`, `bg-card` |
| Zoom controls | Bottom-left, vertical stack: `+`, `-`, fit. Ghost icon buttons. |

---

## 7. Tabs

### 7.1 Horizontal Tabs (Board/Review, Admin Panel)

| Property | Value |
|----------|-------|
| Container | `border-b`, full width |
| Tab item | `px-4 py-3`, Gotham Medium `text-sm`, `text-muted-foreground` |
| Active tab | `text-foreground`, gold bottom border: `border-b-2 border-primary` |
| Hover | `text-foreground`, `bg-muted/50` |
| Focus | Gold ring on keyboard focus |
| Icon | Optional, 16px, left of label. Used in Admin Panel tabs. |
| Transition | `transition-colors duration-150` |

**Admin Panel:** M3 delivers all 4 tabs (AI Context, Parameters, Monitoring, Users) in a single milestone.

### 7.2 Admin Panel Tab Icons

| Tab | Lucide Icon |
|-----|-------------|
| AI Context | `Brain` |
| Parameters | `Settings` |
| Monitoring | `BarChart3` |
| Users | `Users` |

---

## 8. Navigation Components

### 8.1 Navbar Link

| Property | Value |
|----------|-------|
| Font | Gotham Medium, `text-sm` |
| Color | `var(--navbar-text)` (white) |
| Padding | `px-3 py-2` |
| Radius | `rounded` (6px) |
| Hover | `bg-white/10` |
| Active | Gold bottom border (2px), `text-white` (no color change, just underline) |
| Focus | Gold ring, visible against dark navbar |

### 8.2 Hamburger Menu (Mobile)

- Trigger: Lucide `Menu` icon, ghost button
- Sheet: shadcn Sheet, slides from left, `w-72`
- Contains: nav links as full-width items, `py-3`, `border-b`
- Close: Lucide `X` button + click outside + swipe left

### 8.3 Breadcrumb (Idea Workspace)

- Simple: `< Back` link that navigates to Landing Page
- Not a full breadcrumb trail — just a back action
- Position: left side of workspace header
- Style: ghost button, `text-sm`, Lucide `ArrowLeft` icon

---

## 9. Avatar & Presence

### 9.1 Avatar

| Size | Dimension | Usage |
|------|-----------|-------|
| `sm` | 24px | Inline mentions, compact lists |
| `default` | 32px | Navbar user menu, chat messages, card authors |
| `lg` | 40px | User profile cards, collaborator management |
| `xl` | 64px | Login page, large profiles |

- Shape: `rounded-full`
- Content priority: Profile image (from Azure AD) > Initials fallback (first + last initial)
- Initials: `bg-secondary text-secondary-foreground` (teal/white), Gotham Bold
- Border: `2px solid var(--card)` when stacked/overlapping

### 9.2 Stacked Avatars (Presence)

```
[a1][a2][a3] +2
 ^^^overlapping by 8px
```

- Max visible: 4 avatars
- Overflow: "+N" text badge, `bg-muted`, `rounded-full`, same height as avatars
- Overlap: `-ml-2` (8px negative margin)
- Idle avatar: `opacity-50`, grayscale filter (FA-15)

### 9.3 Presence Dot

| State | Color | Position |
|-------|-------|----------|
| Online | `var(--success)` (green) | Bottom-right of avatar, `w-3 h-3`, white border ring |
| Idle | `var(--warning)` (amber) | Same position |
| Offline | Not shown (avatar removed from presence list) | — |

---

## 10. Timeline (Review Section)

### 10.1 Timeline Structure

```
|  * Event node
|  |  Content
|  |
|  * Event node
|  |  Content
|  |
```

| Property | Value |
|----------|-------|
| Line | `border-l-2 border-border`, `ml-4` |
| Node dot | 8px circle, positioned on the line |
| Spacing | `24px` between entries |
| Content | Left of line, `pl-6` (24px padding from the line, ~40px total from left edge) |

### 10.2 Entry Types

| Type | Dot Color | Content |
|------|-----------|---------|
| State change | Corresponding state color | System text: "Submitted for review", "Accepted by Anna Schmidt", etc. Italic, `text-muted-foreground` |
| Comment | `var(--info)` | User avatar + name + timestamp + text. `bg-card`, `border`, `rounded-md`, `p-4` |
| Nested reply | `var(--info)` (smaller dot) | Indented 24px from parent, reply indicator, `text-sm` |
| Resubmission | `var(--primary)` (gold) | "Resubmitted (v1 > v2)" + two download buttons for previous and new version |

### 10.3 Comment Input

- Appears at bottom of timeline
- Textarea + Send button
- Same styling as chat input but standalone (not in a panel)

---

## 11. Feedback Patterns

### 11.1 Toast Notifications

See `page-layouts.md` Section 12 for visual spec.

Configuration:

| Property | Value |
|----------|-------|
| Library | react-toastify (configured) |
| Position | Top-right |
| Max visible | 3 |
| Auto-dismiss | Success/Info: 5 seconds. Warning: 10 seconds. Error: persistent. |
| Dismiss | Click Lucide `X` button, or swipe right (mobile) |
| Entrance | Slide in from right, `200ms ease-out` |
| Exit | Fade out + slide right, `150ms ease-in` |

### 11.2 Skeleton Loading

Used for initial page loads and async content.

| Element | Skeleton Shape |
|---------|---------------|
| Idea card | Full card shape with 2 text lines |
| Chat message | Bubble shape with 3 text lines |
| Board | Full canvas area with 3 rectangle placeholders |
| KPI card | Square with large number + small text |
| User card | Circle (avatar) + 2 text lines |
| PDF preview | Rectangle matching PDF aspect ratio |

- Animation: `animate-pulse` (opacity 50%>100%>50%)
- Background: `var(--muted)`
- Radius: matches the component being loaded
- `prefers-reduced-motion`: static skeleton (no pulse), slightly lower opacity

### 11.3 Empty States

| Context | Message | Visual |
|---------|---------|--------|
| Landing: no ideas (My Ideas) | "Start your first brainstorm" | Lucide `Lightbulb` icon |
| Landing: no collaborations | Contextual empty message | Lucide `Users` icon |
| Landing: no invitations | Contextual empty message | Lucide `Mail` icon |
| Landing: empty trash | "Trash is empty" | Lucide `Trash2` icon |
| Landing: no filter results | "No ideas match your filters" | Lucide `SearchX` icon + clear filters link |
| Review Page: no assigned ideas | "No ideas assigned to you" | Muted text |
| Review Page: no unassigned ideas | "All ideas are assigned" | Muted text |
| Review Section: no timeline entries | "No review activity yet" | Muted text |
| Admin: no search results | "No users found" | Muted text |
| Ideas List (floating): empty tab | "No [state] ideas" | Muted text |
| Notifications: empty | "All caught up" | Muted text, Lucide `Check` icon |

- Empty state text: Gotham Book, `text-base`, `text-muted-foreground`, centered
- Optional: subtle Lucide icon above text (e.g., Lucide `Inbox` for empty notifications)
- No decorative illustrations — keep it clean and minimal

### 11.4 Error States

Following the universal error pattern (FA-14, F-14.1):

```
+--Error Toast-------------------------------------------+
| [X] AI processing failed                         [x]  |
|                                                        |
|   [Show Logs]   [Retry]                                |
+--------------------------------------------------------+
```

- Error toast: persistent (no auto-dismiss)
- "Show Logs": outline button, opens Error Log Modal
- "Retry": primary button, triggers failed operation again
- After max retries (default 3): Retry button disabled, text changes to "Max retries reached"

**Note (BRD generation):** For async AI operations (BRD generation), the error toast shows a text message ("BRD generation failed. Please try again.") without an inline Retry button. The Generate AI button re-enables immediately after error, serving as the retry mechanism. This avoids coupling the toast to async operation state.

### 11.5 Banners

See `page-layouts.md` Section 11. Component-level spec:

| Property | Value |
|----------|-------|
| Width | Full width of parent container |
| Padding | `p-4` |
| Radius | `rounded-md` (8px) |
| Border | `1px solid` matching semantic color |
| Background | Semantic background color (info-bg, warning-bg, error-bg) |
| Icon | Left-aligned, 20px, semantic color (Lucide icons) |
| Text | Gotham Book, `text-sm`, `text-foreground` |
| Actions | Right-aligned buttons (primary + ghost) |
| Dismiss | Some banners are persistent (offline), some dismissible |
| Animation | Slide down from top, `200ms ease-out` via framer-motion |

**Workspace-integrated banner variant:** Banners that appear below a sticky header (e.g., InvitationBanner in workspace) use `border-b bg-primary/5 px-4 py-3` — full-width strip without `rounded-md` or side borders, since rounded corners look wrong in this position. framer-motion `AnimatePresence` slide-down animation still applies.

---

## 12. PDF Preview

### 12.1 Embedded PDF View (Review Tab)

**Tab Visibility:** Review tab is visible when idea state is 'open' (M9: always visible during brainstorming). Previous spec required first submission; M9 simplified to show tab immediately for better UX — users can view/prepare BRD content before first submit.

| Property | Value |
|----------|-------|
| Container | `bg-white` (always white — document rendering), `border`, `rounded-md`, `shadow-sm` |
| Aspect ratio | A4 portrait (roughly 1:1.414) |
| Scrollable | Yes — PDF may exceed visible area |
| Zoom | Not zoomable in preview — full document rendered at readable scale |
| Action bar | Below preview. Ghost buttons: "Download PDF", "Generate". More discoverable than three-dot menu. |

### 12.2 BRD Section Editor (Expandable Edit Area)

| Property | Value |
|----------|-------|
| Container | Slides in from right, full height of right panel |
| Width | Fills the right panel (overlaps/replaces chat view temporarily) |
| Close button | Lucide `X` icon, top-right, returns to PDF preview |
| Section label | Gotham Medium, `text-sm`, with section number |
| Lock icon | Lucide `Lock` (locked) / Lucide `LockOpen` (unlocked), `icon-sm`, toggleable (F-4.4) |
| Regenerate icon | Lucide `RefreshCw`, `icon-sm`, only on unlocked sections |
| Section textarea | Auto-grow, `text-base`, `border`, `rounded`, `bg-card` |
| `/TODO` markers | Displayed as plain text in textarea. Inline highlight (`bg-warning/20 text-warning font-medium`) requires a rich text editor — deferred to future enhancement. |
| `/TODO` auto-lock | Optional enhancement. Detecting /TODO removal in textarea onChange is unreliable. Users should manually lock sections after editing /TODO content. |
| Progress bar | Horizontal, segmented per section, below header (F-4.8) |

### 12.3 Progress Indicator

```
####-- 4/6 sections ready
```

| Segment State | Color |
|---------------|-------|
| Ready | `var(--success)` (green) |
| Insufficient | `var(--muted)` (gray) |
| Gaps Allowed mode | All segments `var(--muted-foreground)`, label: "Gaps allowed" (F-4.9) |

- Size: `h-2`, `rounded-full`, segmented with 2px gaps
- Label: `text-xs`, `text-muted-foreground`, below bar in `space-y-1.5` container (avoids space competition with Edit Document button in responsive layouts)

---

## 13. Divider (Panel Splitter)

| Property | Value |
|----------|-------|
| Visual width | 4px |
| Hit area | 12px (invisible padding for easier grabbing) |
| Color (default) | `var(--border)` |
| Color (hover) | `var(--primary)` (gold) |
| Color (dragging) | `var(--primary)` (gold) with slight glow |
| Cursor | `col-resize` |
| Double-click | Resets to 40/60 default, `200ms transition` |
| Min chat width | 280px |
| Min board width | 320px |
| Persistence | Saved in `localStorage` |

---

## 14. Connection State Indicator (Navbar)

```
[*] Online     [*] Offline
```

| State | Dot | Label | Color |
|-------|-----|-------|-------|
| Online | 8px circle | "Online" | `var(--success)` / Tailwind `green-500` |
| Offline | 8px circle | "Offline" | `var(--destructive)` / Tailwind `red-500` |

- Font: Gotham Book, `text-xs`
- Dot + label side by side, `gap-1.5`
- Label hidden on small screens (dot only)
- Transition: dot color crossfade `200ms`
- **Implementation note:** Uses Tailwind semantic color tokens (`green-500`, `red-500`) which map to equivalent values as the CSS variables

---

## 15. Dropdown Menus

### 15.1 Standard Dropdown (shadcn DropdownMenu)

| Property | Value |
|----------|-------|
| Background | `var(--popover)` |
| Border | `1px solid var(--border)` |
| Radius | `rounded-md` (8px) |
| Shadow | `shadow-lg` |
| Min width | 160px |
| Item height | `py-2 px-3` |
| Item hover | `bg-muted` |
| Item focus | `bg-muted`, gold ring |
| Separator | `border-t`, `my-1` |
| Icons | Optional, 16px, left of label, `text-muted-foreground` (Lucide icons) |
| Keyboard | Arrow keys navigate, Enter selects, Escape closes |

### 15.2 Three-Dot Menu

- Trigger: Lucide `MoreVertical` or `MoreHorizontal` icon, ghost icon button
- Content: standard dropdown items
- Usage: Idea cards (Delete/Restore), workspace header. PDF preview uses action bar instead (§ 12.1).

---

## 16. Tooltip

| Property | Value |
|----------|-------|
| Background | Dark: `var(--foreground)`, Light: `var(--card)` inverted |
| Text | Small: Gotham Book `text-xs` |
| Padding | `px-2 py-1` |
| Radius | `rounded-sm` (4px) |
| Shadow | `shadow-md` |
| Delay | 300ms show, 0ms hide |
| Position | Auto (prefers top, adjusts to avoid overflow) |
| Arrow | Small 4px arrow pointing to trigger |
| Max width | 200px, text wraps |

---

## 17. Modal / Dialog

| Property | Value |
|----------|-------|
| Background | `var(--card)` |
| Border | `1px solid var(--border)` |
| Radius | `rounded-lg` (12px) |
| Shadow | `shadow-xl` |
| Backdrop | `bg-black/50`, click to close (except for critical modals) |
| Width | Context-dependent: `max-w-md` (448px), `max-w-lg` (512px), `max-w-2xl` (672px) |
| Header | Gotham Bold `text-lg`, `border-b`, `px-6 py-4` |
| Body | `px-6 py-4` |
| Footer | `border-t`, `px-6 py-4`, `flex justify-end gap-3` |
| Close | Lucide `X` icon button, top-right corner |
| Entry animation | `framer-motion`: fade in backdrop (150ms) + scale up content (200ms, `0.95>1.0`) |
| Exit animation | Reverse of entry |
| Mobile | Converts to bottom sheet (slides up from bottom, `rounded-t-lg`) |

**Confirmation dialogs:** Use nested `Dialog` with `DialogDescription` for accessibility. No `AlertDialog` component exists in `@/components/ui/`. Nested Dialog achieves the same UX pattern (e.g., transfer ownership confirmation within CollaboratorModal).
