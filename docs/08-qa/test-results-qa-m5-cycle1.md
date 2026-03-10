# Test Results: pre-QA M5 cycle 1
Date: 2026-03-10T03:31:11+0100
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
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 110 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  5%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [ 11%]
services/gateway/apps/board/tests/test_views.py ........................ [ 33%]
.......................                                                  [ 54%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 68%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 79%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 83%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 99%]
tests/test_smoke.py .                                                    [100%]

============================= 110 passed in 5.01s ==============================

```
