# Test Results: pre-QA M11 cycle 0
Date: 2026-03-11T08:58:33+0100
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
collected 620 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  0%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  2%]
services/gateway/apps/authentication/tests/test_user_search.py ......... [  3%]
..                                                                       [  3%]
services/gateway/apps/board/tests/test_views.py ........................ [  7%]
.......................                                                  [ 11%]
services/gateway/apps/brd/tests/test_views.py .......................... [ 15%]
....                                                                     [ 16%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 18%]
services/gateway/apps/chat/tests/test_rate_limit.py ........             [ 20%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 21%]
services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py .... [ 22%]
..........                                                               [ 24%]
services/gateway/apps/collaboration/tests/test_invitation_api.py ....... [ 25%]
........                                                                 [ 26%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 27%]
services/gateway/apps/collaboration/tests/test_visibility.py ......      [ 28%]
services/gateway/apps/ideas/tests/test_share_link.py ........            [ 29%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 32%]
services/gateway/apps/review/tests/test_review_actions.py .............. [ 34%]
.....                                                                    [ 35%]
services/gateway/apps/review/tests/test_review_assignments.py .......... [ 37%]
...                                                                      [ 37%]
services/gateway/apps/review/tests/test_review_list.py ...........       [ 39%]
services/gateway/apps/review/tests/test_review_timeline.py ............. [ 41%]
..                                                                       [ 41%]
services/gateway/apps/review/tests/test_submit.py .............          [ 43%]
services/gateway/apps/websocket/tests/test_access.py .......             [ 45%]
services/gateway/apps/websocket/tests/test_ai_consumer.py ............   [ 46%]
services/gateway/apps/websocket/tests/test_broadcast.py .......          [ 48%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 48%]
services/ai/tests/test_board_agent.py ........................           [ 52%]
services/ai/tests/test_brd_pipeline.py ...........................       [ 57%]
services/ai/tests/test_context_agent.py .............                    [ 59%]
services/ai/tests/test_context_compression.py ..................         [ 62%]
services/ai/tests/test_context_extension.py ............                 [ 64%]
services/ai/tests/test_debouncer.py .........                            [ 65%]
services/ai/tests/test_embedding_pipeline.py .......................     [ 69%]
services/ai/tests/test_facilitator.py .................................. [ 74%]
....................                                                     [ 77%]
services/ai/tests/test_keyword_agent.py ............................     [ 82%]
services/ai/tests/test_pipeline.py .........................             [ 86%]
services/ai/tests/test_summarizing_ai.py ............................... [ 91%]
.....                                                                    [ 92%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 94%]
...........                                                              [ 96%]
services/pdf/tests/test_pdf_service.py ....................              [ 99%]
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

services/pdf/tests/test_pdf_service.py::TestRenderer::test_render_pdf_returns_bytes
services/pdf/tests/test_pdf_service.py::TestRenderer::test_render_pdf_returns_bytes
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_returns_bytes
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_returns_bytes
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_all_sections_in_output
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_all_sections_in_output
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_logs_success
services/pdf/tests/test_pdf_service.py::TestPdfServicer::test_generate_pdf_logs_success
  /usr/local/lib/python3.12/site-packages/pydyf/__init__.py:404: DeprecationWarning: transform is deprecated, use set_matrix instead.
    warn(Stream.transform.__doc__, DeprecationWarning)

services/pdf/tests/test_pdf_service.py: 77 warnings
  /usr/local/lib/python3.12/site-packages/pydyf/__init__.py:399: DeprecationWarning: text_matrix is deprecated, use set_text_matrix instead.
    warn(Stream.text_matrix.__doc__, DeprecationWarning)

tests/test_smoke.py::test_smoke
  /app:0: PytestWarning: Error when trying to teardown test databases: ProgrammingError('database "ziqreq_test" does not exist\n')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================== 620 passed, 89 warnings in 28.51s =======================

```
