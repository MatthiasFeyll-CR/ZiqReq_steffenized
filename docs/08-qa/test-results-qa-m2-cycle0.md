# Test Results: pre-QA M2 cycle 0
Date: 2026-03-09T21:26:37+0100
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
collected 36 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [ 16%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [ 36%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 50%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 97%]
tests/test_smoke.py .                                                    [100%]

============================== 36 passed in 1.11s ==============================

```
