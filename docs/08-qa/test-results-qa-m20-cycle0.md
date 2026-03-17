# Test Results: pre-QA M20 cycle 0
Date: 2026-03-17T04:09:11+0100
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
collected 712 items

services/core/apps/monitoring/tests/test_monitoring_service.py ......... [  1%]
.............                                                            [  3%]
services/core/apps/projects/tests/test_requirements_models.py .......... [  4%]
..                                                                       [  4%]
services/gateway/apps/admin_ai_context/tests/test_ai_context.py ........ [  5%]
...............                                                          [  8%]
services/gateway/apps/admin_config/tests/test_parameters.py ............ [  9%]
..                                                                       [  9%]
services/gateway/apps/authentication/tests/test_admin_users.py ......... [ 11%]
...                                                                      [ 11%]
services/gateway/apps/authentication/tests/test_azure_ad.py ......       [ 12%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [ 13%]
services/gateway/apps/authentication/tests/test_notification_prefs.py .. [ 13%]
.....                                                                    [ 14%]
services/gateway/apps/authentication/tests/test_user_search.py ......... [ 15%]
..                                                                       [ 16%]
services/gateway/apps/brd/tests/test_views.py .......................... [ 19%]
...                                                                      [ 20%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 22%]
services/gateway/apps/chat/tests/test_rate_limit.py .........            [ 23%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 25%]
services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py .... [ 25%]
........                                                                 [ 26%]
services/gateway/apps/collaboration/tests/test_invitation_api.py ....... [ 27%]
........                                                                 [ 28%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 29%]
services/gateway/apps/collaboration/tests/test_visibility.py ......      [ 30%]
services/gateway/apps/monitoring/tests/test_alert_config.py ............ [ 32%]
..                                                                       [ 32%]
services/gateway/apps/monitoring/tests/test_monitoring.py .............  [ 34%]
services/gateway/apps/monitoring/tests/test_monitoring_service.py ...... [ 35%]
................                                                         [ 37%]
services/gateway/apps/notifications/tests/test_notification_api.py ..... [ 38%]
.......                                                                  [ 39%]
services/gateway/apps/projects/tests/test_requirements_views.py ........ [ 40%]
..........                                                               [ 41%]
services/gateway/apps/projects/tests/test_share_link.py ........         [ 42%]
services/gateway/apps/projects/tests/test_views.py .................     [ 45%]
services/gateway/apps/review/tests/test_review_actions.py .............. [ 47%]
.....                                                                    [ 47%]
services/gateway/apps/review/tests/test_review_assignments.py .......... [ 49%]
..                                                                       [ 49%]
services/gateway/apps/review/tests/test_review_list.py ...........       [ 50%]
services/gateway/apps/review/tests/test_review_timeline.py ............. [ 52%]
..                                                                       [ 53%]
services/gateway/apps/review/tests/test_submit.py .............          [ 54%]
services/gateway/apps/websocket/tests/test_access.py .....               [ 55%]
services/gateway/apps/websocket/tests/test_ai_consumer.py ............   [ 57%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 58%]
services/ai/tests/test_brd_pipeline.py ...........................       [ 61%]
services/ai/tests/test_context_agent.py .............                    [ 63%]
services/ai/tests/test_context_buckets.py ........                       [ 64%]
services/ai/tests/test_context_compression.py ..................         [ 67%]
services/ai/tests/test_context_extension.py ............                 [ 68%]
services/ai/tests/test_context_retrieval.py ........                     [ 70%]
services/ai/tests/test_debouncer.py .........                            [ 71%]
services/ai/tests/test_embedding_pipeline.py .......................     [ 74%]
services/ai/tests/test_facilitator.py .................................. [ 79%]
.............................                                            [ 83%]
services/ai/tests/test_pipeline.py .........................             [ 86%]
services/ai/tests/test_summarizing_ai.py ............................... [ 91%]
......................                                                   [ 94%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 96%]
...                                                                      [ 97%]
services/pdf/tests/test_pdf_service.py ....................              [ 99%]
tests/test_smoke.py .                                                    [100%]

=============================== warnings summary ===============================
../usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371
  /usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371: PydanticDeprecatedSince211: The `__get_pydantic_core_schema__` method of the `BaseModel` class is deprecated. If you are calling `super().__get_pydantic_core_schema__` when overriding the method on a Pydantic model, consider using `handler(source)` instead. However, note that overriding this method on models can lead to unexpected side effects. Deprecated in Pydantic V2.11 to be removed in V3.0.
    schema = annotation_get_schema(source, get_inner_schema)

../usr/local/lib/python3.12/site-packages/requests/__init__.py:113
  /usr/local/lib/python3.12/site-packages/requests/__init__.py:113: RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.1.0)/charset_normalizer (3.4.6) doesn't match a supported version!
    warnings.warn(

services/core/apps/monitoring/tests/test_monitoring_service.py::TestIndividualHealthChecks::test_check_database_healthy
services/gateway/apps/monitoring/tests/test_monitoring_service.py::TestIndividualHealthChecks::test_check_database_healthy
  /usr/local/lib/python3.12/site-packages/django/test/utils.py:453: UserWarning: Overriding setting DATABASES can lead to unexpected behavior.
    with self as context:

services/core/apps/monitoring/tests/test_monitoring_service.py::TestHealthCheckTask::test_task_all_healthy_no_alerts
services/gateway/apps/monitoring/tests/test_monitoring_service.py::TestHealthCheckTask::test_task_all_healthy_no_alerts
  /usr/local/lib/python3.12/unittest/case.py:116: UserWarning: Overriding setting DATABASES can lead to unexpected behavior.
    result = enter(cm)

services/gateway/apps/websocket/tests/test_ai_consumer.py::TestAIEventConsumerChatResponse::test_chat_response_includes_full_entity_data
  /app/services/gateway/apps/websocket/tests/test_ai_consumer.py:104: DeprecationWarning: There is no current event loop
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
====================== 712 passed, 92 warnings in 29.18s =======================

```
