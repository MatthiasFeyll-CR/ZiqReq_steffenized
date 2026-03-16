# Interaction & Animation

All animations use **framer-motion**. Every animation respects `prefers-reduced-motion` (NFR-A5) — when enabled, animations are replaced with instant state changes (no motion, no opacity transitions longer than 100ms).

---

## 1. Animation Principles

| Principle | Rule |
|-----------|------|
| Purpose | Every animation communicates something — state change, spatial relationship, or feedback. No decorative animation. |
| Duration | Micro-interactions: 100-200ms. Panel transitions: 200-300ms. Page transitions: 300ms max. |
| Easing | Entrances: `ease-out`. Exits: `ease-in`. Continuous: `ease-in-out`. Never `linear` for UI elements. |
| Performance | Only animate `transform` and `opacity`. Never animate `width`, `height`, `top`, `left`, or `margin`. |
| Reduced motion | All animations wrapped in `useReducedMotion()` check. Fallback: instant state change. |
| Limit | Animate 1-2 key elements per view maximum. Avoid animating everything simultaneously. |

---

## 2. Micro-Interactions

### 2.1 Button Press

| Phase | Property | Value |
|-------|----------|-------|
| Hover | background-color | One step shift, `150ms ease-out` |
| Press | scale | `0.98`, `100ms ease-in` |
| Release | scale | `1.0`, `100ms ease-out` |
| Loading | content | Spinner replaces icon/text, `fade 150ms` |

framer-motion config:
```
whileHover={{ scale: 1.0 }}  // no scale on hover -- color change only
whileTap={{ scale: 0.98 }}
transition={{ duration: 0.1 }}
```

### 2.2 Card Hover

| Phase | Property | Value |
|-------|----------|-------|
| Hover | box-shadow | `shadow-sm` > `shadow-md`, `150ms ease-out` |
| Hover | translateY | `-1px` (subtle lift) |
| Leave | box-shadow + translateY | Return to rest, `150ms ease-in` |

- CSS transition (no framer-motion needed): `transition: box-shadow 150ms ease-out, transform 150ms ease-out`
- Selected card: gold left border appears, `150ms`

### 2.3 Switch/Toggle

| Phase | Property | Value |
|-------|----------|-------|
| Toggle | thumb translateX | Slides to opposite end, `150ms ease-out` |
| Toggle | track color | `var(--muted)` > `var(--primary)` crossfade, `150ms` |

### 2.4 Focus Ring

| Phase | Property | Value |
|-------|----------|-------|
| Focus-in | ring | `0 > 2px`, gold, `100ms ease-out` |
| Focus-out | ring | `2px > 0`, `100ms ease-in` |

- Uses `outline` with `outline-offset: 3px` for non-overlapping ring
- CSS only: `transition: outline 100ms ease-out`

### 2.5 Tooltip

| Phase | Property | Value |
|-------|----------|-------|
| Enter (300ms delay) | opacity + scale | `0/0.95 > 1/1.0`, `150ms ease-out` |
| Exit (instant) | opacity | `1 > 0`, `100ms ease-in` |

### 2.6 Dropdown Menu

| Phase | Property | Value |
|-------|----------|-------|
| Open | opacity + scale + translateY | `0/0.95/-4px > 1/1.0/0`, `150ms ease-out` |
| Close | opacity | `1 > 0`, `100ms ease-in` |

---

## 3. Panel & Layout Transitions

### 3.1 Theme Switch (Light <> Dark) (FA-17)

| Property | Value |
|----------|-------|
| Target | `<body>` background-color, all CSS variable-driven colors |
| Duration | `200ms` |
| Easing | `ease-in-out` |
| Method | `transition-colors duration-200` on `<body>`, CSS variables change instantly, colors crossfade |

- No flash of white/black during theme switch
- Gold (`#FFD700`) remains constant in both themes — provides visual continuity

### 3.2 Project Workspace — Panel Divider Drag

| Property | Value |
|----------|-------|
| During drag | Panels resize in real-time (no animation — follows cursor) |
| Double-click reset | `200ms ease-out` transition to 40/60 default |
| Divider hover | Color: `var(--border)` > `var(--primary)` (gold), `150ms` |

**Panel layout:** Chat panel (left) + Requirements panel (right), separated by draggable divider. Default split: 40% chat, 60% requirements.

### 3.3 Review Tab — Edit Area Slide-In

| Phase | Property | Value |
|-------|----------|-------|
| Open | translateX | `100% > 0`, `250ms ease-out` |
| Close | translateX | `0 > 100%`, `200ms ease-in` |

framer-motion config:
```
initial={{ x: '100%' }}
animate={{ x: 0 }}
exit={{ x: '100%' }}
transition={{ duration: 0.25, ease: 'easeOut' }}
```

- Chat panel underneath remains in DOM but is visually covered
- Backdrop: subtle `bg-black/10` overlay on the chat area (indicates it's behind)

### 3.4 Floating Windows (Projects List, Notifications, Email Preferences)

| Phase | Property | Value |
|-------|----------|-------|
| Open | opacity + translateY | `0/-8px > 1/0`, `200ms ease-out` |
| Close | opacity + translateY | `1/0 > 0/-8px`, `150ms ease-in` |

- AnimatePresence wrapper for mount/unmount transitions

### 3.5 Modal / Dialog

| Phase | Property | Value |
|-------|----------|-------|
| Backdrop enter | opacity | `0 > 1`, `150ms ease-out` |
| Content enter | opacity + scale | `0/0.95 > 1/1.0`, `200ms ease-out` (staggered 50ms after backdrop) |
| Content exit | opacity + scale | `1/1.0 > 0/0.95`, `150ms ease-in` |
| Backdrop exit | opacity | `1 > 0`, `100ms ease-in` (after content) |

- Mobile bottom sheet: `translateY: 100% > 0`, `300ms ease-out`

### 3.6 Banner Enter/Exit

| Phase | Property | Value |
|-------|----------|-------|
| Enter | height + opacity | `0/0 > auto/1`, `200ms ease-out` |
| Exit | height + opacity | `auto/1 > 0/0`, `150ms ease-in` |

- Uses framer-motion `layout` animation for height transitions
- Content below banner smoothly pushes down

### 3.7 Section Collapse/Expand (Review Page History)

| Phase | Property | Value |
|-------|----------|-------|
| Expand | height | `0 > auto`, `250ms ease-out` |
| Collapse | height | `auto > 0`, `200ms ease-in` |

- Chevron icon rotates: `rotate(0deg)` > `rotate(90deg)`, `200ms`
- framer-motion `AnimatePresence` with `layout` prop

### 3.8 Hamburger Menu Sheet (Mobile)

| Phase | Property | Value |
|-------|----------|-------|
| Open | translateX | `-100% > 0`, `250ms ease-out` |
| Close | translateX | `0 > -100%`, `200ms ease-in` |
| Backdrop | opacity | `0 > 1` / `1 > 0`, matching duration |

---

## 4. Content Animations

### 4.1 Project Title Animation (AI-Generated)

When AI updates the title (F-2.3):

| Phase | Property | Value |
|-------|----------|-------|
| Old title out | opacity + translateY | `1/0 > 0/-8px`, `200ms ease-in` |
| New title in | opacity + translateY | `0/8px > 1/0`, `200ms ease-out` (after old exits) |

- Total duration: ~400ms
- `prefers-reduced-motion`: instant text replacement, no animation

### 4.2 New Chat Message (Incoming)

| Phase | Property | Value |
|-------|----------|-------|
| Enter | opacity + translateY | `0/12px > 1/0`, `200ms ease-out` |

- Auto-scroll: chat panel scrolls to bottom on new message, `smooth` behavior
- Own messages: slide in from right. AI messages: slide in from left.
- `prefers-reduced-motion`: instant appear, no slide

### 4.3 AI Processing Indicator

```
--- AI is processing * * * ---
```

- Three dots with sequential opacity pulse:
  - Dot 1: `opacity 0.3 > 1.0`, 600ms, delay 0ms
  - Dot 2: `opacity 0.3 > 1.0`, 600ms, delay 200ms
  - Dot 3: `opacity 0.3 > 1.0`, 600ms, delay 400ms
  - Loop: infinite, `ease-in-out`
- `prefers-reduced-motion`: static text "AI is processing..." with no dot animation

### 4.4 Delegation Message De-emphasis

When the full AI response arrives after a delegation message:

| Phase | Property | Value |
|-------|----------|-------|
| Shrink | fontSize + opacity + padding | `text-base/1.0/12px > text-sm/0.6/8px`, `300ms ease-out` |

### 4.5 Toast Notifications

| Phase | Property | Value |
|-------|----------|-------|
| Enter | translateX + opacity | `100%/0 > 0/1`, `200ms ease-out` |
| Exit | translateX + opacity | `0/1 > 100%/0`, `150ms ease-in` |
| Stack shift | translateY | Existing toasts shift up, `200ms ease-out` |

### 4.6 Notification Count Badge

- New notification: `scale 0 > 1.2 > 1.0`, `300ms` (spring bounce)
- Count update: number crossfade, `150ms`
- `prefers-reduced-motion`: instant appear, no bounce

### 4.7 Skeleton Loading Pulse

- `opacity: 0.5 > 1.0 > 0.5`, `1.5s ease-in-out`, infinite
- `prefers-reduced-motion`: static at `opacity: 0.5`, no pulse

---

## 5. Requirements Panel Interactions

### 5.1 Accordion Expand/Collapse

| Phase | Property | Value |
|-------|----------|-------|
| Expand | height | `0 > auto`, `250ms ease-out` |
| Collapse | height | `auto > 0`, `200ms ease-in` |

- Chevron icon rotates: `rotate(0deg)` > `rotate(180deg)`, `200ms`
- Epic/Milestone cards as accordion headers

### 5.2 Drag-to-Reorder Items

| Phase | Property | Value |
|-------|----------|-------|
| Drag start | scale + shadow | `1.0/shadow-sm > 1.02/shadow-lg`, `150ms ease-out` |
| During drag | Follows cursor | No animation, real-time position |
| Drop | scale + shadow | `1.02/shadow-lg > 1.0/shadow-sm`, `150ms ease-in` |
| Other items shift | translateY | Items below move down/up, `200ms ease-out` |

- Uses `@dnd-kit` library for drag-and-drop
- Visual feedback: dragged item scales slightly and lifts with stronger shadow
- Drop zones highlight with gold border when drag is over

### 5.3 Inline Item Editing

| Phase | Property | Value |
|-------|----------|-------|
| Edit mode enter | border | `transparent > gold`, `150ms` |
| Save | border + scale | Gold border fades, subtle scale pulse `1.0 > 1.01 > 1.0`, `200ms` |
| Cancel | border | Gold > transparent, `150ms` |

- Click to edit: text input replaces display text
- Save on Enter or blur
- Cancel on Escape

### 5.4 Add Item Button

| Phase | Property | Value |
|-------|----------|-------|
| Hover | background | `transparent > bg-gray-100`, `150ms ease-out` |
| New item appears | opacity + translateY | `0/-8px > 1/0`, `200ms ease-out` |

---

## 6. Scroll Behavior

### 6.1 Auto-Scroll on State Transition

When project state changes (FA-1):

| State | Target | Behavior |
|-------|--------|----------|
| Open / Rejected | Requirements structuring section (top) | `scrollIntoView({ behavior: 'smooth', block: 'start' })` |
| In Review / Accepted / Dropped | Review section (below fold) | `scrollIntoView({ behavior: 'smooth', block: 'start' })` |

- Duration: browser-native smooth scroll (~300-500ms depending on distance)
- `prefers-reduced-motion`: `behavior: 'auto'` (instant jump)

### 6.2 Chat Auto-Scroll

- New message: scroll to bottom of chat panel
- Behavior: `smooth`
- Exception: if user has scrolled up (reading history), do NOT auto-scroll. Show a "New message v" pill badge at the bottom of chat that scrolls to bottom on click.

### 6.3 Navbar Sticky

- `position: sticky; top: 0`
- No scroll-hide behavior (navbar always visible)
- On scroll: no shadow change (shadow is always present on navbar via its dark background)

---

## 7. Keyboard & Focus Handling

### 7.1 Focus Management

| Context | Behavior |
|---------|----------|
| Modal opens | Focus trapped inside modal. First focusable element receives focus. |
| Modal closes | Focus returns to the element that triggered the modal. |
| Dropdown opens | Focus moves to first item. Arrow keys navigate. |
| Dropdown closes | Focus returns to trigger button. |
| Floating window opens | Focus moves into window. Tab cycles within. |
| Floating window closes | Focus returns to trigger. |
| Tab switch | Focus moves to the new tab's content area. |
| Banner appears | Focus moves to first action button in banner (for screen readers). |
| Toast appears | Does NOT steal focus (toasts are passive). Aria-live region announces. |

### 7.2 Keyboard Shortcuts

| Shortcut | Context | Action |
|----------|---------|--------|
| `Enter` | Chat input | Send message |
| `Shift+Enter` | Chat input | New line (no send) |
| `@` | Chat input | Open @mention dropdown |
| `Escape` | Any modal/dropdown/floating | Close the overlay |
| `Tab` | Global | Navigate to next focusable element |
| `Shift+Tab` | Global | Navigate to previous focusable element |
| `Enter` | Requirements item focused | Enter edit mode |
| `Escape` | Requirements item editing | Cancel edit |

### 7.3 Focus Visible Strategy

- Use `:focus-visible` (not `:focus`) to show focus rings only on keyboard interaction
- Mouse clicks: no visible focus ring
- Keyboard navigation: gold focus ring (`ring-2 ring-primary ring-offset-2`)
- `outline: none` with custom `box-shadow` ring replacement for consistent cross-browser rendering

### 7.4 Tab Order

- Follows visual order (left to right, top to bottom)
- Skip links: `sr-only` link at page top > "Skip to main content"
- Navbar: tab through brand > nav links > utility items
- Workspace: tab through header > chat panel > requirements panel
- Requirements items: tab through accordion headers, then nested items when expanded

---

## 8. Loading Patterns

### 8.1 Page Load

| Page | Loading Pattern |
|------|----------------|
| Landing Page | Skeleton cards (3-4 placeholder cards) while fetching projects |
| Project Workspace | Skeleton for chat messages + empty requirements panel. Header loads first. |
| Review Page | Skeleton cards while fetching review queue |
| Admin Panel | Skeleton content within the active tab |

### 8.2 Async Operations

| Operation | Indicator | Duration Expectation |
|-----------|-----------|---------------------|
| AI processing | "AI is processing" in chat with animated dots | 3-10 seconds typical |
| PDF generation | Toast: "Generating PDF..." (info) > "PDF generated" (success) | 2-5 seconds |
| Requirements document generation | Progress indicator in Review tab, section-by-section fill | 5-15 seconds |
| Search (users, projects) | Spinner inside search input (replacing search icon) | < 1 second |
| Submit for review | Button loading state > redirect/scroll to review section | < 2 seconds |
| Save (admin params, AI context) | Button loading state > success toast | < 1 second |

### 8.3 Optimistic Updates

| Action | Behavior |
|--------|----------|
| Send chat message | Message appears immediately in chat (optimistic). If API fails, message marked with error icon + retry. |
| Requirements panel edits | Changes apply locally immediately. Broadcast to other users on commit. If sync fails, revert with error toast. |
| Reaction toggle | Reaction appears/disappears immediately. Reverts on API failure. |
| Accept/Decline invitation | Card updates immediately. Reverts on failure. |

---

## 9. Transition Summary Table

Quick reference for all animation durations:

| Category | Element | Duration | Easing |
|----------|---------|----------|--------|
| Micro | Button hover | 150ms | ease-out |
| Micro | Button press | 100ms | ease-in |
| Micro | Focus ring | 100ms | ease-out |
| Micro | Tooltip show | 150ms | ease-out (300ms delay) |
| Micro | Toggle switch | 150ms | ease-out |
| Panel | Theme switch | 200ms | ease-in-out |
| Panel | Edit area slide-in | 250ms | ease-out |
| Panel | Floating window | 200ms | ease-out |
| Panel | Modal enter | 200ms | ease-out |
| Panel | Sidebar sheet | 250ms | ease-out |
| Panel | Section expand | 250ms | ease-out |
| Content | New chat message | 200ms | ease-out |
| Content | AI title change | 200ms + 200ms | ease-in + ease-out |
| Content | Toast enter | 200ms | ease-out |
| Content | Toast exit | 150ms | ease-in |
| Content | Banner enter | 200ms | ease-out |
| Content | Notification badge bounce | 300ms | spring |
| Requirements | Accordion expand | 250ms | ease-out |
| Requirements | Drag start | 150ms | ease-out |
| Requirements | Item shift | 200ms | ease-out |
| Requirements | Edit mode | 150ms | ease-out |
| Loading | Skeleton pulse | 1500ms | ease-in-out (loop) |
| Loading | AI dots | 600ms | ease-in-out (stagger) |
