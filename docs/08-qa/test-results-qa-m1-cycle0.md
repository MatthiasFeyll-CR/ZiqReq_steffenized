# Test Results: QA M1 cycle 0
Date: 2026-03-05T03:45:07+01:00
Command: cd frontend && npx vitest run --reporter=verbose 2>/dev/null; FRONTEND_EXIT=$?; cd ..; pytest services/gateway/ services/core/ services/ai/ --tb=short -q 2>/dev/null; BACKEND_EXIT=$?; exit $((FRONTEND_EXIT + BACKEND_EXIT))
Exit code: 2
Result: FAIL

## Output
```

 RUN  v3.2.4 /home/feyll/hometown/ZiqReq/ZiqReq_ascended/frontend

 ✓ src/lib/ws-client.test.ts > WsClient > creates a singleton instance 85ms
 ✓ src/lib/ws-client.test.ts > WsClient > connects with token in URL 15ms
 ✓ src/lib/ws-client.test.ts > WsClient > sends subscribe and unsubscribe messages 6ms
 ✓ src/lib/ws-client.test.ts > WsClient > dispatches messages to handlers 12ms
 ✓ src/lib/ws-client.test.ts > WsClient > notifies state change handlers 10ms
 ✓ src/lib/ws-client.test.ts > WsClient > allows removing handlers 3ms
 ✓ src/lib/utils.test.ts > cn utility > merges class names 36ms
 ✓ src/lib/utils.test.ts > cn utility > handles conditional classes 1ms
 ✓ src/lib/utils.test.ts > cn utility > merges conflicting Tailwind classes (last wins) 1ms
 ✓ src/lib/utils.test.ts > cn utility > handles undefined and null 0ms
 ✓ src/hooks/use-theme.test.ts > useTheme > defaults to light theme when no stored preference and system prefers light 24ms
 ✓ src/hooks/use-theme.test.ts > useTheme > applies dark class when setTheme('dark') is called 4ms
 ✓ src/hooks/use-theme.test.ts > useTheme > persists theme choice in localStorage 4ms
 ✓ src/hooks/use-theme.test.ts > useTheme > toggleTheme switches between light and dark 5ms
 ✓ src/hooks/use-theme.test.ts > useTheme > removes dark class when switching back to light 4ms
stdout | src/components/layout/layout-components.test.tsx
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/pages/login-page.test.tsx > LoginPage > renders ZiqReq heading and CR logo 438ms
 ✓ src/pages/login-page.test.tsx > LoginPage > shows dev user list in bypass mode 78ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders with default variant and size 279ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 6 variants 34ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > renders all 5 sizes 31ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Offline when disconnected 251ms
 ✓ src/components/layout/layout-components.test.tsx > ConnectionIndicator > shows Online when connected 15ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > renders with loading aria-label 160ms
 ✓ src/components/common/common-components.test.tsx > LoadingSpinner > applies custom className 18ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders icon and message 25ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > shows loading state with spinner 76ms
 ✓ src/components/ui/ui-primitives.test.tsx > Button > is disabled when disabled prop is true 34ms
 ✓ src/components/ui/ui-primitives.test.tsx > Card > renders composable Card with Header, Content, Footer 26ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > renders input with correct type 18ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > shows error state 11ms
 ✓ src/components/ui/ui-primitives.test.tsx > Input > is disabled when disabled prop is true 8ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > renders textarea 17ms
 ✓ src/components/ui/ui-primitives.test.tsx > Textarea > shows error state 19ms
stdout | src/i18n/i18n.test.ts
🌐 i18next is maintained with support from Locize — consider powering your project with managed localization (AI, CDN, integrations): https://locize.com 💙

 ✓ src/components/ui/ui-primitives.test.tsx > Switch > renders and toggles 124ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > renders action button when provided 419ms
 ✓ src/components/common/common-components.test.tsx > EmptyState > does not render button without actionLabel 14ms
 ✓ src/components/common/common-components.test.tsx > SkipLink > renders sr-only link 7ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders children when no error 6ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders error fallback when child throws 37ms
 ✓ src/components/common/common-components.test.tsx > ErrorBoundary > renders custom fallback 9ms
 ✓ src/i18n/i18n.test.ts > i18n config > has German (de) translations loaded 16ms
 ✓ src/i18n/i18n.test.ts > i18n config > has English (en) translations loaded 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains common UI label keys in both languages 5ms
 ✓ src/i18n/i18n.test.ts > i18n config > contains auth label keys in both languages 1ms
 ✓ src/i18n/i18n.test.ts > i18n config > falls back to German (de) as default language 12ms
 ✓ src/i18n/i18n.test.ts > i18n config > can switch language and translate correctly 10ms
 ✓ src/components/ui/ui-primitives.test.tsx > Checkbox > renders and toggles 85ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders all state badge variants 12ms
 ✓ src/components/ui/ui-primitives.test.tsx > Badge > renders role badge variants 7ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders fallback initials 6ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders presence dot 6ms
 ✓ src/components/ui/ui-primitives.test.tsx > Avatar > renders idle presence dot 5ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > renders with pulse animation class 5ms
 ✓ src/components/ui/ui-primitives.test.tsx > Skeleton > respects motion-reduce 4ms
 ✓ src/components/layout/layout-components.test.tsx > NotificationBell > renders bell with 0 count 724ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > renders Show Logs and Retry buttons 56ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > calls onRetry when Retry is clicked 53ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > renders tab list and switches content 123ms
 ✓ src/components/ui/ui-primitives.test.tsx > Tabs > active tab has gold border indicator 35ms
 ✓ src/components/ui/ui-primitives.test.tsx > ToastProvider > renders toast container 10ms
 ✓ src/lib/api-client.test.ts > apiClient > makes GET requests with correct URL and headers 14ms
 ✓ src/lib/api-client.test.ts > apiClient > makes POST requests with body 2ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PUT requests with body 2ms
 ✓ src/lib/api-client.test.ts > apiClient > makes PATCH requests with body 1ms
 ✓ src/lib/api-client.test.ts > apiClient > makes DELETE requests 1ms
 ✓ src/lib/api-client.test.ts > apiClient > throws ApiClientError on non-ok response 4ms
 ✓ src/lib/api-client.test.ts > apiClient > handles non-JSON error response 1ms
 ✓ src/lib/api-client.test.ts > apiClient > includes Content-Type header 1ms
 ✓ src/components/common/common-components.test.tsx > ErrorToast > disables Retry after max retries reached 89ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > renders error details when open 116ms
 ✓ src/components/common/common-components.test.tsx > ErrorLogModal > has copy button 67ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in light mode (default) 24ms
 ✓ src/components/ui/ui-primitives.test.tsx > Theme rendering > components render in dark mode 25ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Button has accessible name 12ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > icon button requires aria-label 13ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Switch has accessible role 20ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Checkbox has accessible role 19ms
 ✓ src/components/ui/ui-primitives.test.tsx > Accessibility > Tabs have accessible structure 36ms
 ✓ src/store/store.test.ts > Redux store > has all 5 slice reducers configured 3ms
 ✓ src/store/store.test.ts > Redux store > board slice has correct initial state 2ms
 ✓ src/store/store.test.ts > Redux store > websocket slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > presence slice has correct initial state 0ms
 ✓ src/store/store.test.ts > Redux store > ui slice has correct initial state 1ms
 ✓ src/store/store.test.ts > Redux store > rateLimit slice has correct initial state 0ms
 ✓ src/store/store.test.ts > Redux store > dispatches setConnectionState action 4ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > renders logo, ZiqReq text, and banner role 479ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > includes Ideas link in desktop nav for all users 34ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > does not show Reviews link for non-reviewer 35ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Reviews link for reviewer 30ms
 ✓ src/components/layout/layout-components.test.tsx > Navbar > shows Admin link for admin 28ms
 ✓ src/config/env.test.ts > env config > exports API_BASE_URL with default /api 1ms
 ✓ src/config/env.test.ts > env config > exports WS_URL as a string 0ms
 ✓ src/config/env.test.ts > env config > exports AUTH_BYPASS as a boolean 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_CLIENT_ID as a string 0ms
 ✓ src/config/env.test.ts > env config > exports MSAL_AUTHORITY as a string 0ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows user initials and opens dropdown on click 159ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > shows theme toggle and language toggle in dropdown 79ms
 ✓ src/components/layout/layout-components.test.tsx > UserDropdown > calls onLogout when Sign Out is clicked 114ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > shows dev users in dropdown when loaded 78ms
 ✓ src/components/layout/layout-components.test.tsx > DevUserSwitcher > calls dev-login when switching user 86ms
 ✓ src/components/layout/layout-components.test.tsx > IdeasListFloating > renders empty state with message 8ms
 ✓ src/components/layout/layout-components.test.tsx > PageShell > renders navbar and main content area 26ms

 Test Files  11 passed (11)
      Tests  102 passed (102)
   Start at  03:45:02
   Duration  4.05s (transform 1.28s, setup 1.12s, collect 4.48s, tests 5.25s, environment 8.28s, prepare 1.74s)


==================================== ERRORS ====================================
___________ ERROR collecting apps/admin_config/tests/test_models.py ____________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/admin_config/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.admin_config'
_______________ ERROR collecting apps/board/tests/test_models.py _______________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/board/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.board'
________________ ERROR collecting apps/brd/tests/test_models.py ________________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/brd/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.brd'
_______________ ERROR collecting apps/chat/tests/test_models.py ________________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/chat/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.chat'
___________ ERROR collecting apps/collaboration/tests/test_models.py ___________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/collaboration/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.collaboration'
_______________ ERROR collecting apps/ideas/tests/test_models.py _______________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/ideas/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.ideas'
______________ ERROR collecting apps/review/tests/test_models.py _______________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/review/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.review'
____________ ERROR collecting apps/similarity/tests/test_models.py _____________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/apps/similarity/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.similarity'
_________________ ERROR collecting events/tests/test_broker.py _________________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/events/tests/test_broker.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'events.tests.test_broker'
_______________ ERROR collecting events/tests/test_publisher.py ________________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/events/tests/test_publisher.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'events.tests.test_publisher'
_____________ ERROR collecting grpc_server/tests/test_core_grpc.py _____________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/grpc_server/tests/test_core_grpc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'grpc_server.tests.test_core_grpc'
___________________ ERROR collecting tests/test_publisher.py ___________________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/core/tests/test_publisher.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
services/core/tests/test_publisher.py:7: in <module>
    from events.publisher import (
E   ModuleNotFoundError: No module named 'events.publisher'
______________ ERROR collecting apps/context/tests/test_models.py ______________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/ai/apps/context/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.context'
____________ ERROR collecting apps/embeddings/tests/test_models.py _____________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/ai/apps/embeddings/tests/test_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'apps.embeddings'
______________ ERROR collecting grpc_server/tests/test_ai_grpc.py ______________
ImportError while importing test module '/home/feyll/hometown/ZiqReq/ZiqReq_ascended/services/ai/grpc_server/tests/test_ai_grpc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.14/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'grpc_server.tests.test_ai_grpc'
=========================== short test summary info ============================
ERROR services/gateway/apps/admin_config/tests/test_models.py
ERROR services/gateway/apps/board/tests/test_models.py
ERROR services/gateway/apps/brd/tests/test_models.py
ERROR services/gateway/apps/chat/tests/test_models.py
ERROR services/gateway/apps/collaboration/tests/test_models.py
ERROR services/gateway/apps/ideas/tests/test_models.py
ERROR services/gateway/apps/review/tests/test_models.py
ERROR services/gateway/apps/similarity/tests/test_models.py
ERROR services/gateway/events/tests/test_broker.py
ERROR services/gateway/events/tests/test_publisher.py
ERROR services/gateway/grpc_server/tests/test_core_grpc.py
ERROR services/gateway/tests/test_publisher.py
ERROR services/gateway/apps/context/tests/test_models.py
ERROR services/gateway/apps/embeddings/tests/test_models.py
ERROR services/gateway/grpc_server/tests/test_ai_grpc.py
!!!!!!!!!!!!!!!!!!! Interrupted: 15 errors during collection !!!!!!!!!!!!!!!!!!!
15 errors in 0.32s
```
