# Test Results: pre-QA M7 cycle 0
Date: 2026-03-11T01:41:05+0100
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
plugins: anyio-4.12.1, django-4.12.0, cov-5.0.0, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 240 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  2%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  5%]
services/gateway/apps/board/tests/test_views.py ........................ [ 15%]
.......................                                                  [ 25%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 31%]
services/gateway/apps/chat/tests/test_rate_limit.py ........             [ 34%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 39%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 41%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 48%]
services/gateway/apps/websocket/tests/test_access.py .......             [ 51%]
services/gateway/apps/websocket/tests/test_ai_consumer.py ...........    [ 56%]
services/gateway/apps/websocket/tests/test_broadcast.py .......          [ 59%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 61%]
services/ai/tests/test_debouncer.py .........                            [ 65%]
services/ai/tests/test_facilitator.py .................................. [ 79%]
.........                                                                [ 82%]
services/ai/tests/test_pipeline.py .............                         [ 88%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 95%]
...........                                                              [ 99%]
tests/test_smoke.py .                                                    [100%]

=============================== warnings summary ===============================
../usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371
  /usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371: PydanticDeprecatedSince211: The `__get_pydantic_core_schema__` method of the `BaseModel` class is deprecated. If you are calling `super().__get_pydantic_core_schema__` when overriding the method on a Pydantic model, consider using `handler(source)` instead. However, note that overriding this method on models can lead to unexpected side effects. Deprecated in Pydantic V2.11 to be removed in V3.0.
    schema = annotation_get_schema(source, get_inner_schema)

../usr/local/lib/python3.12/site-packages/requests/__init__.py:113
  /usr/local/lib/python3.12/site-packages/requests/__init__.py:113: RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.0.1)/charset_normalizer (3.4.5) doesn't match a supported version!
    warnings.warn(

services/gateway/apps/websocket/tests/test_ai_consumer.py::TestAIEventConsumerChatResponse::test_chat_response_includes_full_entity_data
  /app/services/gateway/apps/websocket/tests/test_ai_consumer.py:103: DeprecationWarning: There is no current event loop
    asyncio.get_event_loop().run_until_complete(

tests/test_smoke.py::test_smoke
  /app:0: PytestWarning: Error when trying to teardown test databases: ProgrammingError('database "ziqreq_test" does not exist\n')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 240 passed, 4 warnings in 18.07s =======================

```
