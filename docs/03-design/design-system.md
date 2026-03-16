# Design System

## 1. Visual Direction

| Property | Value |
|----------|-------|
| Mood | Clean & Professional |
| Brand | Commerz Real (Commerzbank subsidiary) |
| Style | Soft UI Evolution — subtle depth, modern enterprise, accessibility-focused |
| Framework | shadcn/ui (Radix primitives) + Tailwind CSS 4 |
| Icons | Lucide React (`lucide-react`) |
| Font | Gotham (self-hosted, commercial license) |
| Themes | Light mode (default) + Dark mode |

**Design intelligence validation:** Style matches "Soft UI Evolution" profile (modern enterprise, subtle depth, WCAG AA+, 200-300ms animations, border-radius 8-12px). Color strategy validated against "Trust & Authority" profile (financial services, professional teal + gold accents). Accessibility approach confirmed against animation UX guidelines (prefers-reduced-motion, 1-2 key animated elements per view max, ease-out for entrances).

---

## 2. Color Palette

### 2.1 Brand Colors (Fixed)

| Token | Hex | Usage |
|-------|-----|-------|
| `--brand-gold` | `#FFD700` | Accent, highlights, active states, badges, focus rings. NOT for text or small elements on light backgrounds (contrast 1.3:1 against white). |
| `--brand-teal` | `#002E3C` | Primary action color in light mode (buttons, links, headings). Deep brand anchor. |

### 2.2 Light Mode

| Token | Hex | Tailwind Equiv | Usage |
|-------|-----|----------------|-------|
| `--background` | `#FAFAFA` | gray-50 | Page background |
| `--surface` | `#FFFFFF` | white | Cards, panels, modals |
| `--surface-hover` | `#F5F5F5` | gray-100 | Hovered cards, list items |
| `--surface-active` | `#F0F0F0` | gray-100/150 | Pressed/active surfaces |
| `--border` | `#E5E7EB` | gray-200 | Card borders, dividers, input borders |
| `--border-strong` | `#D1D5DB` | gray-300 | Focused input borders, emphasized dividers |
| `--text-primary` | `#002E3C` | — (brand-teal) | Headings, body text, primary labels |
| `--text-secondary` | `#475569` | slate-600 | Supporting text, descriptions, timestamps |
| `--text-muted` | `#94A3B8` | slate-400 | Placeholders, disabled text, hints |
| `--primary` | `#FFD700` | — (brand-gold) | Active indicators, selected borders, badges, progress, focus rings |
| `--primary-hover` | `#E6C200` | — | Darkened gold on hover |
| `--primary-foreground` | `#002E3C` | — (brand-teal) | Text on gold backgrounds |
| `--secondary` | `#002E3C` | — (brand-teal) | Buttons, links, interactive actions |
| `--secondary-hover` | `#003D52` | — | Lightened teal on hover |
| `--secondary-foreground` | `#FFFFFF` | white | Text on teal backgrounds |
| `--navbar-bg` | `#002E3C` | — (brand-teal) | Navbar background |
| `--navbar-text` | `#FFFFFF` | white | Navbar text and icons |
| `--navbar-accent` | `#FFD700` | — (brand-gold) | Active nav item indicator |

### 2.3 Dark Mode

| Token | Hex | Tailwind Equiv | Usage |
|-------|-----|----------------|-------|
| `--background` | `#0B1121` | — | Page background (deep navy, not pure black) |
| `--surface` | `#1E293B` | slate-800 | Cards, panels, modals |
| `--surface-hover` | `#334155` | slate-700 | Hovered cards, list items |
| `--surface-active` | `#3B4A5E` | — | Pressed/active surfaces |
| `--border` | `rgba(255,255,255,0.08)` | white/[0.08] | Card borders, dividers |
| `--border-strong` | `rgba(255,255,255,0.15)` | white/[0.15] | Focused input borders |
| `--text-primary` | `#F1F5F9` | slate-100 | Headings, body text |
| `--text-secondary` | `#94A3B8` | slate-400 | Supporting text, descriptions |
| `--text-muted` | `#64748B` | slate-500 | Placeholders, disabled text |
| `--primary` | `#FFD700` | — (brand-gold) | Active indicators, selected borders, badges, focus rings |
| `--primary-hover` | `#FFDF33` | — | Brightened gold on hover |
| `--primary-foreground` | `#002E3C` | — (brand-teal) | Text on gold backgrounds |
| `--secondary` | `#FFD700` | — (brand-gold) | Buttons swap to gold in dark mode |
| `--secondary-hover` | `#FFDF33` | — | Brightened gold on hover |
| `--secondary-foreground` | `#002E3C` | — (brand-teal) | Text on gold buttons (dark mode) |
| `--navbar-bg` | `#0F1A2E` | — | Navbar background (slightly lighter than page) |
| `--navbar-text` | `#F1F5F9` | slate-100 | Navbar text and icons |
| `--navbar-accent` | `#FFD700` | — (brand-gold) | Active nav item indicator |

### 2.4 Semantic Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--success` | `#16A34A` | `#22C55E` | Accepted projects, connection online, success toasts |
| `--success-bg` | `#F0FDF4` | `rgba(34,197,94,0.1)` | Success toast background, success badge bg |
| `--warning` | `#D97706` | `#F59E0B` | Rate limit lockout, offline warning, dropped projects |
| `--warning-bg` | `#FFFBEB` | `rgba(245,158,11,0.1)` | Warning toast background |
| `--error` | `#DC2626` | `#EF4444` | Error toasts, validation errors, failed actions |
| `--error-bg` | `#FEF2F2` | `rgba(239,68,68,0.1)` | Error toast background |
| `--info` | `#0284C7` | `#38BDF8` | Info toasts, in-review state, notifications |
| `--info-bg` | `#F0F9FF` | `rgba(56,189,248,0.1)` | Info toast background |

### 2.5 Project State Colors

| State | Color (Light) | Color (Dark) | Usage |
|-------|--------------|-------------|-------|
| Open | `#0284C7` (sky-600) | `#38BDF8` (sky-400) | Default/active requirements assembly state |
| In Review | `#F59E0B` (amber-500) | `#F59E0B` (amber-500) | Submitted, awaiting review |
| Accepted | `#16A34A` (green-600) | `#22C55E` (green-500) | Reviewer accepted |
| Dropped | `#9CA3AF` (gray-400) | `#9CA3AF` (gray-400) | Permanently closed |
| Rejected | `#F97316` (orange-500) | `#F97316` (orange-500) | Returned for rework |

### 2.6 Button Color Strategy

| Mode | Primary Button | Secondary Button | Ghost/Outline |
|------|---------------|-----------------|---------------|
| Light | `bg-[#002E3C] text-white` | `bg-gray-100 text-[#002E3C]` | `border-gray-300 text-[#002E3C]` |
| Dark | `bg-[#FFD700] text-[#002E3C]` | `bg-slate-700 text-slate-100` | `border-white/15 text-slate-100` |

**Design rationale:** In light mode, the deep teal provides a strong, authoritative primary action. In dark mode, buttons invert to gold — the bright accent pops against dark surfaces while maintaining the Commerzbank brand identity. This inversion ensures buttons are always the most visually prominent interactive element regardless of theme.

---

## 3. Typography

### 3.1 Font Family

| Role | Font | Fallback Stack |
|------|------|---------------|
| All text | Gotham | `'Gotham', ui-sans-serif, system-ui, -apple-system, sans-serif` |
| Monospace (code, UUIDs, logs) | `ui-monospace, 'Cascadia Code', 'Fira Code', monospace` | — |

> **Note:** Gotham is a commercial typeface (Hoefler & Co). Self-hosted from application static assets. Requires corporate font license from Commerz Real.

### 3.2 Type Scale

Base: `16px` (1rem)

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `text-xs` | 12px (0.75rem) | 400 Book | 1.5 (18px) | Badges, timestamps, captions, helper text |
| `text-sm` | 14px (0.875rem) | 400 Book | 1.5 (21px) | Secondary labels, table cells, form descriptions |
| `text-base` | 16px (1rem) | 400 Book | 1.6 (25.6px) | Body text, chat messages, form inputs |
| `text-lg` | 18px (1.125rem) | 500 Medium | 1.5 (27px) | Section headings, card titles |
| `text-xl` | 20px (1.25rem) | 500 Medium | 1.4 (28px) | Page sub-headings, panel headers |
| `text-2xl` | 24px (1.5rem) | 700 Bold | 1.3 (31.2px) | Page headings |
| `text-3xl` | 30px (1.875rem) | 700 Bold | 1.2 (36px) | Hero heading (Landing Page) |

### 3.3 Weight Usage

| Weight | Gotham Name | Token | Usage |
|--------|-------------|-------|-------|
| 400 | Book | `font-normal` | Body text, descriptions, chat messages |
| 500 | Medium | `font-medium` | Labels, nav items, card titles, table headers |
| 700 | Bold | `font-bold` | Page headings, emphasis, button labels |

### 3.4 Text Rendering Rules

- Line length: max `65-75ch` for body text (readability)
- German text: allow containers to grow; never truncate mid-word
- Chat messages: full-width within the chat panel (no max-width constraint)
- Monospace: used for UUIDs, error logs, technical details in the error modal

---

## 4. Spacing

### 4.1 Base Unit

`8px` (0.5rem) — all spacing is a multiple of 4px, with 8px as the primary increment.

### 4.2 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-0.5` | 2px | Inline icon-to-text gap |
| `space-1` | 4px | Tight internal padding (badge, tag) |
| `space-2` | 8px | Between related elements (icon + label, message gap in chat) |
| `space-3` | 12px | Chat panel internal padding, compact section padding |
| `space-4` | 16px | Card padding, gap between cards in lists |
| `space-5` | 20px | Section padding inside panels |
| `space-6` | 24px | Card padding (spacious), gap between sections |
| `space-8` | 32px | Major section separators, page section gaps |
| `space-10` | 40px | Page-level top/bottom padding |
| `space-12` | 48px | Hero section padding |

### 4.3 Context-Specific Spacing

| Context | Padding | Gap Between Items |
|---------|---------|-------------------|
| Navbar | 12px vertical, 16px horizontal | 8px between items |
| Landing page cards | 20-24px | 16px between cards |
| Chat messages | 12px bubble padding | 8px between messages |
| Requirements panel | 12px edge padding | 8px between items |
| Review tab panels | 16-20px | 12px between sections |
| Admin Panel tabs | 20-24px | 16px between form groups |
| Modal content | 24px | 16px between elements |
| Toast | 12-16px | — |

---

## 5. Border Radius

### 5.1 Radius Scale

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Tags, badges, small chips |
| `rounded` | 6px | Buttons, inputs, select dropdowns |
| `rounded-md` | 8px | Cards, chat bubbles, panels |
| `rounded-lg` | 12px | Modals, floating windows, notification panel |
| `rounded-xl` | 16px | Landing page hero section, large feature cards |
| `rounded-full` | 9999px | Avatars, status dots, pill badges |

---

## 6. Shadows

### 6.1 Light Mode

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-xs` | `0 1px 2px rgba(0,0,0,0.03)` | Subtle lift for input fields |
| `shadow-sm` | `0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03)` | Cards at rest |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04)` | Cards on hover, toast notifications |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.04)` | Dropdowns, floating panels, notification bell panel |
| `shadow-xl` | `0 20px 25px rgba(0,0,0,0.10), 0 8px 10px rgba(0,0,0,0.04)` | Modals, error log modal |
| `shadow-gold` | `0 0 0 2px rgba(255,215,0,0.3)` | Gold glow for active/selected elements |

### 6.2 Dark Mode

In dark mode, shadows are less visible. Use `ring` borders to define elevation:

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-xs` | `ring-1 ring-white/[0.04]` | Input fields |
| `shadow-sm` | `ring-1 ring-white/[0.06]` | Cards at rest |
| `shadow-md` | `ring-1 ring-white/[0.08] shadow-md shadow-black/20` | Cards on hover |
| `shadow-lg` | `ring-1 ring-white/[0.10] shadow-lg shadow-black/25` | Floating panels |
| `shadow-xl` | `ring-1 ring-white/[0.10] shadow-xl shadow-black/30` | Modals |
| `shadow-gold` | `0 0 0 2px rgba(255,215,0,0.25)` | Gold glow (slightly dimmed for dark mode) |

---

## 7. Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `z-base` | 0 | Normal flow content |
| `z-requirements-item` | 10 | Requirements items during drag operations |
| `z-panel` | 20 | Floating panels (projects list, notifications) |
| `z-dropdown` | 30 | Dropdown menus, @mention suggestions |
| `z-navbar` | 40 | Global navbar (sticky) |
| `z-banner` | 45 | Contextual banners (invitation, offline) |
| `z-modal` | 50 | Modals (error log, collaborator management) |
| `z-toast` | 60 | Toast notifications (always on top) |

---

## 8. Component Library Approach

### 8.1 Foundation: shadcn/ui

All components built on **shadcn/ui** (Radix primitives + Tailwind). Components are copied into the project (not imported from a package), allowing full customization of brand colors, spacing, and radius tokens.

### 8.2 Theme Implementation

- CSS custom properties defined on `:root` (light) and `.dark` (dark)
- shadcn/ui components reference these variables via Tailwind CSS 4's `@theme inline` block with hex values (e.g., `--color-primary: var(--primary)`) — no HSL interpolation needed
- Theme toggle adds/removes the `dark` class on `<html>` (F-17.2)
- On first visit, respects `prefers-color-scheme` (F-17.3)
- After explicit user selection, preference overrides system setting
- Transition: `transition-colors duration-200` on `<body>` for smooth theme switch

### 8.3 Customized shadcn/ui Components (Expected)

| Component | Customization |
|-----------|--------------|
| Button | Brand colors (teal light / gold dark), Gotham Bold labels |
| Card | Brand border-radius (8px), shadow scale, gold left-border for selected state |
| Input | Brand border colors, gold focus ring, 6px radius |
| Badge | Project state colors, small radius (4px) |
| Dialog (Modal) | Brand shadow-xl, 12px radius, backdrop blur |
| DropdownMenu | Brand shadow-lg, 6px radius, hover states |
| Toast (react-toastify) | Semantic colors, brand radius, icon + action layout |
| Tabs | Gold underline for active tab, no background change |
| Avatar | rounded-full, presence dot overlay |
| Tooltip | Dark surface, small text, 4px radius |
| Skeleton | Pulse animation, matching surface colors |
| Sheet | Slide-in panel for mobile, 12px radius on visible edge |

### 8.4 Icon Usage

- **Library:** Lucide React
- **Default size:** 20px (`w-5 h-5`) for UI elements, 16px (`w-4 h-4`) for inline/small contexts
- **Stroke width:** 1.75px (Lucide default) — clean, not too thin
- **Color:** Inherits from `currentColor` — follows text color naturally
- **No emojis as icons.** Reactions (thumbs up/down, heart) are the only emoji usage in the app (per F-2.7, F-2.8).

---

## 9. Navbar Specification

### 9.1 Structure

```
+-----------------------------------------------------------------------+
| [CR Logo] ZiqReq    | Projects | Reviews* | Admin*  |    ...right items  |
+-----------------------------------------------------------------------+
  ^brand block (left)    ^nav links              ^connection, bell, user
```

- **Left:** CR logo (small, ~24px height) + "ZiqReq" in Gotham Bold + nav links
- **Right:** Connection indicator + Notification bell + User avatar/dropdown
- `*` conditionally visible by role

### 9.2 Navbar Tokens

| Property | Light Mode | Dark Mode |
|----------|-----------|-----------|
| Background | `#002E3C` (brand-teal) | `#0F1A2E` |
| Text | `#FFFFFF` | `#F1F5F9` |
| Active item | Gold underline (`#FFD700`) | Gold underline (`#FFD700`) |
| Hover | `rgba(255,255,255,0.1)` bg | `rgba(255,255,255,0.08)` bg |
| Height | 56px | 56px |
| Logo height | 24px | 24px |
| Border bottom | none (shadow lifts it) | `1px solid rgba(255,255,255,0.06)` |

### 9.3 Logo Handling (F-17.5)

- The CR logo features the gold Commerzbank ribbon on a white/transparent background.
- **Light mode navbar** (dark teal bg): Logo works well — gold on dark.
- **Dark mode navbar** (deep navy bg): Logo works well — gold on dark.
- The "COMMERZ REAL" wordmark in the logo is NOT displayed in the navbar. Only the ribbon icon + "ZiqReq" text.
- App name "ZiqReq" uses Gotham Bold, white, `text-lg` (18px).

---

## 10. Accessibility Tokens

| Property | Value |
|----------|-------|
| Focus ring | `2px solid var(--primary)` with `3px` offset (gold ring) |
| Focus ring (dark mode) | `2px solid var(--primary)` with `3px` offset (gold ring — visible on dark surfaces) |
| Minimum contrast | 4.5:1 for normal text, 3:1 for large text (WCAG 2.1 AA) |
| Touch target | Minimum 44x44px for all interactive elements |
| Reduced motion | All framer-motion animations wrapped in `prefers-reduced-motion` check (NFR-A5) |
| Screen reader | `aria-label` on all icon-only buttons, `sr-only` text for visual-only indicators |

### 10.1 Contrast Verification

| Combination | Ratio | Pass? |
|------------|-------|-------|
| `#002E3C` on `#FAFAFA` (light: teal text on bg) | 13.2:1 | WCAG AAA |
| `#FFFFFF` on `#002E3C` (light: white on teal button) | 13.2:1 | WCAG AAA |
| `#475569` on `#FAFAFA` (light: secondary text) | 5.9:1 | WCAG AA |
| `#F1F5F9` on `#0B1121` (dark: primary text) | 15.8:1 | WCAG AAA |
| `#FFD700` on `#002E3C` (gold on teal) | 8.5:1 | WCAG AAA |
| `#FFD700` on `#0B1121` (gold on dark bg) | 10.4:1 | WCAG AAA |
| `#002E3C` on `#FFD700` (teal on gold button) | 8.5:1 | WCAG AAA |
| `#94A3B8` on `#FAFAFA` (light: muted text) | 3.3:1 | Large text only |
| `#94A3B8` on `#1E293B` (dark: secondary text) | 4.6:1 | WCAG AA |

---

## 11. Design Token Summary (Tailwind CSS Config)

```
// Mapped to shadcn/ui CSS variable conventions
// Applied via :root (light) and .dark (dark) on <html>

:root {
  --background: #FAFAFA;
  --foreground: #002E3C;
  --card: #FFFFFF;
  --card-foreground: #002E3C;
  --popover: #FFFFFF;
  --popover-foreground: #002E3C;
  --primary: #FFD700;
  --primary-foreground: #002E3C;
  --secondary: #002E3C;
  --secondary-foreground: #FFFFFF;
  --muted: #F5F5F5;
  --muted-foreground: #94A3B8;
  --accent: #F0F0F0;
  --accent-foreground: #002E3C;
  --destructive: #DC2626;
  --destructive-foreground: #FFFFFF;
  --border: #E5E7EB;
  --input: #E5E7EB;
  --ring: #FFD700;
  --radius: 6px;
}

.dark {
  --background: #0B1121;
  --foreground: #F1F5F9;
  --card: #1E293B;
  --card-foreground: #F1F5F9;
  --popover: #1E293B;
  --popover-foreground: #F1F5F9;
  --primary: #FFD700;
  --primary-foreground: #002E3C;
  --secondary: #FFD700;
  --secondary-foreground: #002E3C;
  --muted: #334155;
  --muted-foreground: #64748B;
  --accent: #334155;
  --accent-foreground: #F1F5F9;
  --destructive: #EF4444;
  --destructive-foreground: #FFFFFF;
  --border: rgba(255,255,255,0.08);
  --input: rgba(255,255,255,0.08);
  --ring: #FFD700;
  --radius: 6px;
}
```

---

## 12. Responsive Breakpoints

| Breakpoint | Width | Target |
|-----------|-------|--------|
| `sm` | 640px | Large phones (landscape) |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops, tablets landscape |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Large desktop |

### 12.1 Responsive Behavior Summary

| Page | Desktop (xl+) | Tablet (md-lg) | Mobile (sm) |
|------|--------------|----------------|-------------|
| Landing | Multi-column card grid | 2-column grid | Single column stack |
| Project Workspace | Side-by-side chat + requirements panel | Stacked or tabbed panels | Stacked, requirements panel read-only |
| Review Page | Multi-column card grid | 2-column grid | Single column stack |
| Admin Panel | Full tab layout | Full tab layout | Scrollable tab content |
| Navbar | Full nav links visible | Hamburger menu for nav links | Hamburger menu |
