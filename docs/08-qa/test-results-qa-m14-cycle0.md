# Test Results: pre-QA M14 cycle 0 (retry)
Date: 2026-03-11T14:49:20+0100
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
collected 809 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  0%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  1%]
services/gateway/apps/authentication/tests/test_notification_prefs.py .. [  1%]
.....                                                                    [  2%]
services/gateway/apps/authentication/tests/test_user_search.py ......... [  3%]
..                                                                       [  3%]
services/gateway/apps/board/tests/test_views.py ........................ [  6%]
.......................                                                  [  9%]
services/gateway/apps/brd/tests/test_views.py .......................... [ 12%]
....                                                                     [ 13%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 15%]
services/gateway/apps/chat/tests/test_rate_limit.py ........             [ 16%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 17%]
services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py .... [ 18%]
..........                                                               [ 19%]
services/gateway/apps/collaboration/tests/test_invitation_api.py ....... [ 20%]
........                                                                 [ 21%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 21%]
services/gateway/apps/collaboration/tests/test_visibility.py ......      [ 22%]
services/gateway/apps/ideas/tests/test_append_execution.py ............  [ 24%]
services/gateway/apps/ideas/tests/test_append_flow.py ..............     [ 25%]
services/gateway/apps/ideas/tests/test_manual_merge.py .............     [ 27%]
services/gateway/apps/ideas/tests/test_merge_request.py ................ [ 29%]
......                                                                   [ 30%]
services/gateway/apps/ideas/tests/test_recursive_merge.py .........      [ 31%]
services/gateway/apps/ideas/tests/test_share_link.py ........            [ 32%]
services/gateway/apps/ideas/tests/test_similar_ideas.py ................ [ 34%]
..                                                                       [ 34%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 36%]
services/gateway/apps/notifications/tests/test_notification_api.py ..... [ 37%]
.......                                                                  [ 38%]
services/gateway/apps/review/tests/test_review_actions.py .............. [ 39%]
.....                                                                    [ 40%]
services/gateway/apps/review/tests/test_review_assignments.py .......... [ 41%]
...                                                                      [ 42%]
services/gateway/apps/review/tests/test_review_list.py ...........       [ 43%]
services/gateway/apps/review/tests/test_review_timeline.py ............. [ 44%]
..                                                                       [ 45%]
services/gateway/apps/review/tests/test_submit.py .............          [ 46%]
services/gateway/apps/similarity/tests/test_keyword_matching.py ......   [ 47%]
services/gateway/apps/similarity/tests/test_merge_service.py ........... [ 48%]
........                                                                 [ 49%]
services/gateway/apps/similarity/tests/test_vector_similarity.py ......  [ 50%]
services/gateway/apps/websocket/tests/test_access.py .......             [ 51%]
services/gateway/apps/websocket/tests/test_ai_consumer.py ............   [ 53%]
services/gateway/apps/websocket/tests/test_broadcast.py .......          [ 53%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 54%]
services/ai/tests/test_board_agent.py ........................           [ 57%]
services/ai/tests/test_brd_pipeline.py ...........................       [ 60%]
services/ai/tests/test_context_agent.py .............                    [ 62%]
services/ai/tests/test_context_compression.py ..................         [ 64%]
services/ai/tests/test_context_extension.py ............                 [ 66%]
services/ai/tests/test_debouncer.py .........                            [ 67%]
services/ai/tests/test_deep_comparison.py ...........................    [ 70%]
services/ai/tests/test_embedding_pipeline.py .......................     [ 73%]
services/ai/tests/test_facilitator.py .................................. [ 77%]
....................                                                     [ 80%]
services/ai/tests/test_keyword_agent.py ............................     [ 83%]
services/ai/tests/test_merge_synthesizer.py ........................     [ 86%]
services/ai/tests/test_pipeline.py .........................             [ 89%]
services/ai/tests/test_summarizing_ai.py ............................... [ 93%]
.....                                                                    [ 94%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 96%]
...........                                                              [ 97%]
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

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================== 809 passed, 88 warnings in 41.93s =======================

```
