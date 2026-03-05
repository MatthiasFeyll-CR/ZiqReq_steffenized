# Component Inventory

Every unique component mentioned across all page layouts, organized by type and shared status. This inventory is critical input for the Milestone Planner when scoping which wave needs which shared components.

---

## UI Primitives (shadcn/ui — customized)

These are base-level components used across the entire application. Must be implemented first as shared foundation.

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| Button | UI primitive | All pages | Yes | 6 variants (Primary, Secondary, Ghost, Outline, Destructive, Link), 5 sizes |
| Card | UI primitive | Landing, Review, Admin, Workspace | Yes | Base card + Idea Card, Review Card, User Card, KPI Card variants |
| Input | UI primitive | All pages | Yes | Text input, Search input variants |
| Textarea | UI primitive | Workspace, Admin | Yes | Auto-grow variant for chat, BRD editor, review comments |
| Select | UI primitive | Landing, Workspace, Admin | Yes | shadcn Select with brand styling |
| Switch | UI primitive | Workspace, Admin | Yes | Used for toggles (email prefs, Allow Info Gaps, alerts) |
| Checkbox | UI primitive | Admin (email prefs) | Yes | With indeterminate state for group toggles |
| Badge | UI primitive | All pages | Yes | State badges, role badges, notification count, AI badge |
| Avatar | UI primitive | All pages | Yes | 4 sizes (sm/default/lg/xl), initials fallback, presence dot |
| Tooltip | UI primitive | All pages | Yes | 300ms delay, auto-position |
| DropdownMenu | UI primitive | All pages | Yes | Standard dropdown with brand styling |
| Dialog (Modal) | UI primitive | Workspace, Admin | Yes | 3 width variants, mobile bottom sheet conversion |
| Sheet | UI primitive | Mobile navigation | Yes | Slide-in panel for hamburger menu |
| Tabs | UI primitive | Workspace, Admin | Yes | Gold underline active state, optional icons |
| Skeleton | UI primitive | All pages | Yes | Pulse animation, component-shaped placeholders |
| Toast | UI primitive | All pages | Yes | 4 semantic variants, stacking, auto-dismiss |

---

## Layout Components

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| Navbar | Layout | All authenticated pages | Yes | Global navigation, role-gated links, utility items |
| NavbarLink | Layout | Navbar | Yes | Active gold underline, hover state |
| HamburgerMenu | Layout | Mobile navbar | Yes | Sheet slide-in from left |
| UserDropdown | Layout | Navbar | Yes | User info, language toggle, theme toggle, email prefs, logout |
| PageShell | Layout | All authenticated pages | Yes | Navbar + content area wrapper |
| AuthenticatedLayout | Layout | All authenticated routes | Yes | Layout route with auth guard + Outlet (replaces per-route AuthGuard wrappers) |
| PanelDivider | Layout | Workspace | No | Draggable, localStorage persistence, 40/60 default |
| ConnectionIndicator | Layout | Navbar | Yes | Online/offline dot + label |
| NotificationBell | Layout | Navbar | Yes | Bell icon + count badge (in layout/ since it's a navbar element) |
| IdeasListFloating | Layout | Navbar (floating) | No | Tabbed floating panel with compact idea items (in layout/ since it's a navbar-anchored panel) |

---

## Feature Components — Chat

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| ChatPanel | Feature | Workspace | No | Full chat panel: messages + input area |
| ChatMessage | Feature | Workspace | No | Base message bubble, user/AI variants |
| UserMessageBubble | Feature | Workspace | No | Right-aligned, teal/gold background |
| AIMessageBubble | Feature | Workspace | No | Left-aligned, card background, border |
| DelegationMessage | Feature | Workspace | No | De-emphasized AI message variant |
| AIProcessingIndicator | Feature | Workspace | No | Animated dots, centered in chat |
| ReactionChips | Feature | Workspace | No | Emoji reactions below messages (F-2.7, F-2.8) |
| MentionDropdown | Feature | Workspace | No | @mention user/AI selection above input |
| ContextWindowIndicator | Feature | Workspace | No | Filling circle showing context usage |
| ChatInput | Feature | Workspace | No | Input + send button + context indicator |
| RateLimitOverlay | Feature | Workspace | No | Lockout state overlay on chat input (F-2.11) |

---

## Feature Components — Board

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| BoardCanvas | Feature | Workspace | No | React Flow canvas with dot grid background |
| BoxNode | Feature | Workspace | No | Title + body + pin + AI badge + lock icons |
| GroupNode | Feature | Workspace | No | Dashed border, label badge, resizable |
| FreeTextNode | Feature | Workspace | No | Transparent, click-to-edit |
| ConnectionEdge | Feature | Workspace | No | Smooth step, label on double-click, arrow |
| BoardToolbar | Feature | Workspace | No | Add/Delete/Fit/Undo/Redo buttons |
| BoardMinimap | Feature | Workspace | No | Bottom-right overview |
| BoardZoomControls | Feature | Workspace | No | Bottom-left +/-/fit buttons |
| AIModifiedIndicator | Feature | Workspace | No | Gold dot with pulse animation (F-3.4) |
| UserSelectionHighlight | Feature | Workspace | No | Colored border + name label for other users |

---

## Feature Components — BRD / Review

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| PDFPreview | Feature | Workspace (Review tab) | No | White background document preview, scrollable |
| BRDSectionEditor | Feature | Workspace (Review tab) | No | Expandable edit area, slide-in from right |
| SectionField | Feature | Workspace (Review tab) | No | Label + lock + regenerate + textarea per section |
| ProgressIndicator | Feature | Workspace (Review tab) | No | Segmented bar showing BRD readiness (F-4.8) |
| SubmitArea | Feature | Workspace (Review tab) | No | Message + reviewer selector + submit button |
| ReviewTimeline | Feature | Workspace (below fold) | No | Vertical timeline with entries |
| TimelineEntry | Feature | Workspace (below fold) | No | State change, comment, reply, resubmission variants |
| CommentInput | Feature | Workspace (below fold) | No | Standalone textarea + send for timeline comments |
| SimilarIdeaCard | Feature | Workspace (below fold) | No | Title + keyword match count, navigable (FA-5) |
| ReviewCard | Feature | Review Page | No | Extends IdeaCard with author, date, action button |

---

## Feature Components — Collaboration

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| CollaboratorModal | Feature | Workspace | No | Invite search, collaborator list, pending invitations |
| PresenceIndicators | Feature | Workspace header | No | Stacked avatars with overflow count |
| InvitationBanner | Feature | Workspace | No | Accept/Decline inline banner (FA-8) |

---

## Feature Components — Notifications

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| NotificationPanel | Feature | Navbar (floating) | Yes | Floating window with notification list |
| NotificationItem | Feature | Notification panel | Yes | Icon + title + time + description + actions |
| EmailPreferencesPanel | Feature | User dropdown (floating) | No | Grouped toggles, role-based sections (FA-13) |

---

## Feature Components — Admin

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| AIContextEditor | Feature | Admin Panel | No | Facilitator + Context Agent bucket editors |
| ParametersTable | Feature | Admin Panel | No | Inline-editable table with gold modified indicator |
| MonitoringDashboard | Feature | Admin Panel | No | KPI cards + state bars + health table |
| UserSearch | Feature | Admin Panel | No | Search input + user cards |
| UserCard | Feature | Admin Panel | No | Avatar + name + email + roles + stats |
| KPICard | Feature | Admin Panel | No | Label + value + trend |
| ServiceHealthTable | Feature | Admin Panel | No | Service status dots + latency + last check |
| AlertRecipientChips | Feature | Admin Panel | No | Email chip list with add/remove |

---

## Feature Components — Landing

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| HeroSection | Feature | Landing | No | Heading + subtext + creation input |
| IdeaCard | Feature | Landing, Ideas List | Yes | State dot + title + timestamp + badge + menu |
| InvitationCard | Feature | Landing | No | Gold left border + accept/decline buttons |
| FilterBar | Feature | Landing | No | Search + state dropdown + ownership dropdown |

---

## Feature Components — Auth

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| LoginPage | Feature | Login | No | Logo + title + Microsoft sign-in button |
| DevUserSwitcher | Feature | Navbar (dev only) | No | Dev mode user selector |

---

## Common / Cross-Cutting

| Component | Type | Pages Used In | Shared? | Notes |
|-----------|------|--------------|---------|-------|
| ErrorBoundary | Common | All pages | Yes | React error boundary with fallback UI |
| EmptyState | Common | Landing, Review, Admin, Notifications | Yes | Icon + message + optional action |
| OfflineBanner | Common | Workspace | No | Red banner with countdown + reconnect (FA-6) |
| MergeRequestBanner | Common | Workspace | No | Warning banner with accept/decline (FA-5) |
| ErrorToast | Common | All pages | Yes | Persistent toast with Show Logs + Retry (FA-14) |
| ErrorLogModal | Common | All pages | Yes | Monospace error details + copy button |
| LoadingSpinner | Common | All pages | Yes | Small inline spinner for async operations |
| SkipLink | Common | All pages | Yes | sr-only "Skip to main content" link |

---

## Summary

| Category | Count | Shared |
|----------|-------|--------|
| UI Primitives | 16 | All shared |
| Layout | 10 | 8 shared |
| Chat | 11 | 0 shared |
| Board | 10 | 0 shared |
| BRD / Review | 10 | 0 shared |
| Collaboration | 3 | 0 shared |
| Notifications | 3 | 2 shared |
| Admin | 8 | 0 shared |
| Landing | 4 | 1 shared (IdeaCard) |
| Auth | 2 | 0 shared |
| Common / Cross-Cutting | 8 | 5 shared |
| **Total** | **85** | **32 shared** |

**Milestone planning note:** UI Primitives and Layout components form the shared foundation and should be implemented in Wave 1 before any page-specific features. Common components (ErrorBoundary, EmptyState, Toast patterns) should also be in Wave 1.
