# Test Results: pre-QA M6 cycle 0
Date: 2026-03-10T23:34:56+0100
Command: docker compose -f docker-compose.test.yml run --rm python-tests pytest
Exit code: 0
Result: PASS

## Output
```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
django: version: 5.2.12, settings: gateway.settings.test (from env)
rootdir: /app
configfile: pyproject.toml
plugins: django-4.12.0, cov-5.0.0, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 156 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  3%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  8%]
services/gateway/apps/board/tests/test_views.py ........................ [ 23%]
.......................                                                  [ 38%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 48%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 55%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 58%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 69%]
services/gateway/apps/websocket/tests/test_access.py .......             [ 74%]
services/gateway/apps/websocket/tests/test_broadcast.py .......          [ 78%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 82%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 92%]
...........                                                              [ 99%]
tests/test_smoke.py .                                                    [100%]

=============================== warnings summary ===============================
tests/test_smoke.py::test_smoke
  /app:0: PytestWarning: Error when trying to teardown test databases: ProgrammingError('database "ziqreq_test" does not exist\n')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 156 passed, 1 warning in 13.70s ========================

```
