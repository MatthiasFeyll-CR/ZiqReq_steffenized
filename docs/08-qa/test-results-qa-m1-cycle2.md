# Test Results: QA M1 cycle 2
Date: 2026-03-05T04:10:46+01:00
Command: cd frontend && npx vitest run --reporter=verbose 2>/dev/null; FRONTEND_EXIT=$?; cd ..; pytest services/gateway/ services/core/ services/ai/ --tb=short -q 2>/dev/null; BACKEND_EXIT=$?; exit $((FRONTEND_EXIT + BACKEND_EXIT))
Exit code: 2
Result: FAIL

## Output
```

 RUN  v3.2.4 /home/feyll/hometown/ZiqReq/ZiqReq_ascended/frontend

 ✓ src/lib/ws-client.test.ts > WsClient > creates a singleton instance 40ms
 ✓ src/lib/ws-client.test.ts > WsClient > connects with token in URL 8ms
 ✓ src/lib/ws-client.test.ts > WsClient > sends subscribe and unsubscribe messages 3ms
 ✓ src/lib/ws-client.test.ts > WsClient > dispatches messages to handlers 5ms
 ✓ src/lib/ws-client.test.ts > WsClient > notifies state change handlers 9ms
 ✓ src/lib/ws-client.test.ts > WsClient > allows removing handlers 9ms
 ✓ src/lib/utils.test.ts > cn utility > merges class names 8ms
 ✓ src/lib/utils.test.ts > cn utility > handles conditional classes 0ms
 ✓ src/lib/utils.test.ts > cn utility > merges conflicting Tailwind classes (last wins) 1ms
 ✓ src/lib/utils.test.ts > cn utility > handles undefined and null 6ms
 ✓ src/hooks/use-theme.test.ts > useTheme > defaults to light theme when no stored preference and system prefers light 24ms
 ✓ src/hooks/use-theme.test.ts > useTheme > applies dark class when setTheme('dark') is called 7ms
 ✓ src/hooks/use-theme.test.ts > useTheme > persists theme choice in localStorage 5ms
 ✓ src/hooks/use-theme.test.ts > useTheme > toggleTheme switches between light and dark 6ms
 ✓ src/hooks/use-theme.test.ts > useTheme > removes dark class when switching back to light 4ms
stdout | src/components/layout/layout-components.test.tsx
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/pages/login-page.test.tsx > LoginPage > renders ZiqReq heading and CR logo 248ms
 ✓ src/pages/login-page.test.tsx > LoginPage > shows dev user list in bypass mode 18ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Offline when disconnected 85ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Online when connected 8ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > renders with loading aria-label 52ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > applies custom className 7ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders icon and message 14ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders action button when provided 169ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > does not render button without actionLabel 6ms
 ✓ src/components/common/common-components.test.tsx > SkipLink > renders sr-only link 4ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders children when no error 4ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders with default variant and size 154ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 6 variants 12ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 5 sizes 7ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > shows loading state with spinner 13ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > is disabled when disabled prop is true 12ms
 ✓ src/components/ui/ui-primitives.test.tsx > Card > renders composable Card with Header, Content, Footer 7ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > renders input with correct type 6ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > shows error state 3ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > is disabled when disabled prop is true 4ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > renders textarea 5ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > shows error state 3ms
 ✓ src/lib/api-client.test.ts > apiClient > makes GET requests with correct URL and headers 8ms
 ✓ src/lib/api-client.test.ts > apiClient > makes POST requests with body 1ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PUT requests with body 1ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PATCH requests with body 1ms
 ✓ src/lib/api-client.test.ts > apiClient > makes DELETE requests 1ms
 ✓ src/lib/api-client.test.ts > apiClient > throws ApiClientError on non-ok response 2ms
 ✓ src/lib/api-client.test.ts > apiClient > handles non-JSON error response 1ms
 ✓ src/lib/api-client.test.ts > apiClient > includes Content-Type header 0ms
 ✓ src/components/layout/layout-components.test.tsx > NotificationBell > renders bell with 0 count 192ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders error fallback when child throws 23ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders custom fallback 4ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > renders Show Logs and Retry buttons 30ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > calls onRetry when Retry is clicked 29ms
 ✓ src/components/ui/ui-primitives.test.tsx > Switch > renders and toggles 75ms
 ✓ src/components/ui/ui-primitives.test.tsx > Checkbox > renders and toggles 38ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders all state badge variants 7ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders role badge variants 5ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders fallback initials 4ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders presence dot 4ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > renders logo, ZiqReq text, and banner role 222ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > disables Retry after max retries reached 54ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > renders error details when open 77ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders idle presence dot 5ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > renders with pulse animation class 8ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > respects motion-reduce 5ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > has copy button 66ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > includes Ideas link in desktop nav for all users 21ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > does not show Reviews link for non-reviewer 29ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Reviews link for reviewer 21ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Admin link for admin 24ms
stdout | src/i18n/i18n.test.ts
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/i18n/i18n.test.ts > i18n config > has German (de) translations loaded 2ms
 ✓ src/i18n/i18n.test.ts > i18n config > has English (en) translations loaded 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains common UI label keys in both languages 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains auth label keys in both languages 0ms
 ✓ src/i18n/i18n.test.ts > i18n config > falls back to German (de) as default language 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > can switch language and translate correctly 3ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > renders tab list and switches content 93ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > active tab has gold border indicator 25ms
 ✓ src/components/ui/ui-primitives.test.tsx > ToastProvider > renders toast container 7ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in light mode (default) 19ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in dark mode 11ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Button has accessible name 12ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > icon button requires aria-label 10ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Switch has accessible role 14ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Checkbox has accessible role 15ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Tabs have accessible structure 40ms
 ✓ src/store/store.test.ts > Redux store > has all 5 slice reducers configured 3ms
 ✓ src/store/store.test.ts > Redux store > board slice has correct initial state 2ms
 ✓ src/store/store.test.ts > Redux store > websocket slice has correct initial state 0ms
 ✓ src/store/store.test.ts > Redux store > presence slice has correct initial state 0ms
 ✓ src/store/store.test.ts > Redux store > ui slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > rateLimit slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > dispatches setConnectionState action 4ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows user initials and opens dropdown on click 179ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows theme toggle and language toggle in dropdown 164ms
 ✓ src/config/env.test.ts > env config > exports API_BASE_URL with default /api 2ms
 ✓ src/config/env.test.ts > env config > exports WS_URL as a string 0ms
 ✓ src/config/env.test.ts > env config > exports AUTH_BYPASS as a boolean 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_CLIENT_ID as a string 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_AUTHORITY as a string 0ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > calls onLogout when Sign Out is clicked 147ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > shows dev users in dropdown when loaded 95ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > calls dev-login when switching user 111ms
 ✓ src/components/layout/layout-components.test.tsx > IdeasListFloating > renders empty state with message 11ms
 ✓ src/components/layout/layout-components.test.tsx > PageShell > renders navbar and main content area 23ms

 Test Files  11 passed (11)
      Tests  102 passed (102)
   Start at  04:10:41
   Duration  2.93s (transform 784ms, setup 876ms, collect 2.92s, tests 2.97s, environment 6.37s, prepare 1.46s)


==================================== ERRORS ====================================
_ ERROR collecting services/gateway/apps/authentication/tests/test_auth_views.py _
services/gateway/apps/authentication/tests/test_auth_views.py:16: in <module>
    from apps.authentication.models import User
services/gateway/apps/authentication/models.py:9: in <module>
    class User(models.Model):
../../../.local/lib/python3.14/site-packages/django/db/models/base.py:131: in __new__
    app_config = apps.get_containing_app_config(module)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:260: in get_containing_app_config
    self.check_apps_ready()
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:138: in check_apps_ready
    raise AppRegistryNotReady("Apps aren't loaded yet.")
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
__ ERROR collecting services/gateway/apps/authentication/tests/test_models.py __
services/gateway/apps/authentication/tests/test_models.py:6: in <module>
    from apps.authentication.models import User
services/gateway/apps/authentication/models.py:9: in <module>
    class User(models.Model):
../../../.local/lib/python3.14/site-packages/django/db/models/base.py:131: in __new__
    app_config = apps.get_containing_app_config(module)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:260: in get_containing_app_config
    self.check_apps_ready()
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:138: in check_apps_ready
    raise AppRegistryNotReady("Apps aren't loaded yet.")
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
____ ERROR collecting services/gateway/apps/monitoring/tests/test_models.py ____
services/gateway/apps/monitoring/tests/test_models.py:6: in <module>
    from apps.monitoring.models import MonitoringAlertConfig
services/gateway/apps/monitoring/models.py:8: in <module>
    class MonitoringAlertConfig(models.Model):
../../../.local/lib/python3.14/site-packages/django/db/models/base.py:131: in __new__
    app_config = apps.get_containing_app_config(module)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:260: in get_containing_app_config
    self.check_apps_ready()
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:138: in check_apps_ready
    raise AppRegistryNotReady("Apps aren't loaded yet.")
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
__ ERROR collecting services/gateway/apps/notifications/tests/test_models.py ___
services/gateway/apps/notifications/tests/test_models.py:6: in <module>
    from apps.notifications.models import Notification
services/gateway/apps/notifications/models.py:8: in <module>
    class Notification(models.Model):
../../../.local/lib/python3.14/site-packages/django/db/models/base.py:131: in __new__
    app_config = apps.get_containing_app_config(module)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:260: in get_containing_app_config
    self.check_apps_ready()
../../../.local/lib/python3.14/site-packages/django/apps/registry.py:138: in check_apps_ready
    raise AppRegistryNotReady("Apps aren't loaded yet.")
E   django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
=========================== short test summary info ============================
ERROR services/gateway/apps/authentication/tests/test_auth_views.py - django....
ERROR services/gateway/apps/authentication/tests/test_models.py - django.core...
ERROR services/gateway/apps/monitoring/tests/test_models.py - django.core.exc...
ERROR services/gateway/apps/notifications/tests/test_models.py - django.core....
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
4 errors in 0.49s
```
