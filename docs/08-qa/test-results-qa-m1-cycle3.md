# Test Results: QA M1 cycle 3
Date: 2026-03-05T04:19:52+01:00
Command: cd frontend && npx vitest run --reporter=verbose 2>/dev/null; FRONTEND_EXIT=$?; cd ..; pytest services/gateway/ services/core/ services/ai/ --tb=short -q 2>/dev/null; BACKEND_EXIT=$?; exit $((FRONTEND_EXIT + BACKEND_EXIT))
Exit code: 0
Result: PASS

## Output
```

 RUN  v3.2.4 /home/feyll/hometown/ZiqReq/ZiqReq_ascended/frontend

 ✓ src/lib/utils.test.ts > cn utility > merges class names 7ms
 ✓ src/lib/utils.test.ts > cn utility > handles conditional classes 0ms
 ✓ src/lib/utils.test.ts > cn utility > merges conflicting Tailwind classes (last wins) 1ms
 ✓ src/lib/utils.test.ts > cn utility > handles undefined and null 0ms
 ✓ src/lib/ws-client.test.ts > WsClient > creates a singleton instance 72ms
 ✓ src/lib/ws-client.test.ts > WsClient > connects with token in URL 17ms
 ✓ src/lib/ws-client.test.ts > WsClient > sends subscribe and unsubscribe messages 5ms
 ✓ src/lib/ws-client.test.ts > WsClient > dispatches messages to handlers 9ms
 ✓ src/lib/ws-client.test.ts > WsClient > notifies state change handlers 10ms
 ✓ src/lib/ws-client.test.ts > WsClient > allows removing handlers 6ms
 ✓ src/hooks/use-theme.test.ts > useTheme > defaults to light theme when no stored preference and system prefers light 56ms
 ✓ src/hooks/use-theme.test.ts > useTheme > applies dark class when setTheme('dark') is called 11ms
 ✓ src/hooks/use-theme.test.ts > useTheme > persists theme choice in localStorage 11ms
 ✓ src/hooks/use-theme.test.ts > useTheme > toggleTheme switches between light and dark 13ms
 ✓ src/hooks/use-theme.test.ts > useTheme > removes dark class when switching back to light 9ms
stdout | src/components/layout/layout-components.test.tsx
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/pages/login-page.test.tsx > LoginPage > renders ZiqReq heading and CR logo 490ms
 ✓ src/pages/login-page.test.tsx > LoginPage > shows dev user list in bypass mode 59ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Offline when disconnected 233ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Online when connected 20ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders with default variant and size 337ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 6 variants 26ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 5 sizes 54ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > renders with loading aria-label 198ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > applies custom className 14ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders icon and message 23ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > shows loading state with spinner 47ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > is disabled when disabled prop is true 49ms
 ✓ src/components/ui/ui-primitives.test.tsx > Card > renders composable Card with Header, Content, Footer 30ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > renders input with correct type 15ms
 ✓ src/components/layout/layout-components.test.tsx > NotificationBell > renders bell with 0 count 608ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders action button when provided 229ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > shows error state 9ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > is disabled when disabled prop is true 8ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > renders textarea 9ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > shows error state 10ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > does not render button without actionLabel 48ms
 ✓ src/components/common/common-components.test.tsx > SkipLink > renders sr-only link 15ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders children when no error 13ms
 ✓ src/components/ui/ui-primitives.test.tsx > Switch > renders and toggles 112ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders error fallback when child throws 49ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders custom fallback 15ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > renders Show Logs and Retry buttons 67ms
 ✓ src/lib/api-client.test.ts > apiClient > makes GET requests with correct URL and headers 16ms
 ✓ src/lib/api-client.test.ts > apiClient > makes POST requests with body 2ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PUT requests with body 2ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PATCH requests with body 1ms
 ✓ src/lib/api-client.test.ts > apiClient > makes DELETE requests 1ms
 ✓ src/lib/api-client.test.ts > apiClient > throws ApiClientError on non-ok response 4ms
 ✓ src/lib/api-client.test.ts > apiClient > handles non-JSON error response 1ms
 ✓ src/lib/api-client.test.ts > apiClient > includes Content-Type header 1ms
 ✓ src/components/ui/ui-primitives.test.tsx > Checkbox > renders and toggles 76ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders all state badge variants 14ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders role badge variants 9ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders fallback initials 10ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders presence dot 8ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders idle presence dot 4ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > renders with pulse animation class 25ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > respects motion-reduce 5ms
 ✓ src/store/store.test.ts > Redux store > has all 5 slice reducers configured 7ms
 ✓ src/store/store.test.ts > Redux store > board slice has correct initial state 2ms
 ✓ src/store/store.test.ts > Redux store > websocket slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > presence slice has correct initial state 0ms
 ✓ src/store/store.test.ts > Redux store > ui slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > rateLimit slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > dispatches setConnectionState action 6ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > calls onRetry when Retry is clicked 37ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > disables Retry after max retries reached 78ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > renders tab list and switches content 73ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > active tab has gold border indicator 38ms
 ✓ src/components/ui/ui-primitives.test.tsx > ToastProvider > renders toast container 10ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > renders error details when open 96ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > has copy button 95ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in light mode (default) 16ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in dark mode 21ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Button has accessible name 22ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > icon button requires aria-label 14ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Switch has accessible role 25ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > renders logo, ZiqReq text, and banner role 540ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > includes Ideas link in desktop nav for all users 46ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > does not show Reviews link for non-reviewer 46ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Checkbox has accessible role 27ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Tabs have accessible structure 68ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Reviews link for reviewer 37ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Admin link for admin 48ms
stdout | src/i18n/i18n.test.ts
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/i18n/i18n.test.ts > i18n config > has German (de) translations loaded 6ms
 ✓ src/i18n/i18n.test.ts > i18n config > has English (en) translations loaded 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains common UI label keys in both languages 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains auth label keys in both languages 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > falls back to German (de) as default language 2ms
 ✓ src/i18n/i18n.test.ts > i18n config > can switch language and translate correctly 6ms
 ✓ src/config/env.test.ts > env config > exports API_BASE_URL with default /api 2ms
 ✓ src/config/env.test.ts > env config > exports WS_URL as a string 0ms
 ✓ src/config/env.test.ts > env config > exports AUTH_BYPASS as a boolean 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_CLIENT_ID as a string 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_AUTHORITY as a string 0ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows user initials and opens dropdown on click 267ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows theme toggle and language toggle in dropdown 131ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > calls onLogout when Sign Out is clicked 106ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > shows dev users in dropdown when loaded 77ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > calls dev-login when switching user 83ms
 ✓ src/components/layout/layout-components.test.tsx > IdeasListFloating > renders empty state with message 9ms
 ✓ src/components/layout/layout-components.test.tsx > PageShell > renders navbar and main content area 21ms

 Test Files  11 passed (11)
      Tests  102 passed (102)
   Start at  04:19:46
   Duration  4.25s (transform 1.33s, setup 1.37s, collect 4.92s, tests 5.33s, environment 8.92s, prepare 1.88s)

......................................................                   [100%]
54 passed in 0.95s
```
