# Test Results: pre-QA M22 cycle 0
Date: 2026-03-18T02:38:56+0100
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
collected 878 items

services/core/apps/monitoring/tests/test_monitoring_service.py ......... [  1%]
.............                                                            [  2%]
services/core/apps/projects/tests/test_requirements_models.py .......... [  3%]
..                                                                       [  3%]
services/gateway/apps/admin_ai_context/tests/test_ai_context.py ........ [  4%]
...............                                                          [  6%]
services/gateway/apps/admin_config/tests/test_parameters.py ............ [  7%]
..                                                                       [  8%]
services/gateway/apps/attachments/tests/test_validators.py ............. [  9%]
....................                                                     [ 11%]
services/gateway/apps/attachments/tests/test_views.py .................. [ 13%]
....................                                                     [ 16%]
services/gateway/apps/authentication/tests/test_admin_users.py ......... [ 17%]
...                                                                      [ 17%]
services/gateway/apps/authentication/tests/test_azure_ad.py ......       [ 18%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [ 19%]
services/gateway/apps/authentication/tests/test_notification_prefs.py .. [ 19%]
.....                                                                    [ 19%]
services/gateway/apps/authentication/tests/test_user_search.py ......... [ 20%]
..                                                                       [ 21%]
services/gateway/apps/chat/tests/test_chat_attachments.py ............   [ 22%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 24%]
services/gateway/apps/chat/tests/test_rate_limit.py .........            [ 25%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 26%]
services/gateway/apps/collaboration/tests/test_collaborator_mgmt.py .... [ 26%]
........                                                                 [ 27%]
services/gateway/apps/collaboration/tests/test_invitation_api.py ....... [ 28%]
........                                                                 [ 29%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 30%]
services/gateway/apps/collaboration/tests/test_visibility.py ......      [ 30%]
services/gateway/apps/monitoring/tests/test_alert_config.py ............ [ 32%]
..                                                                       [ 32%]
services/gateway/apps/monitoring/tests/test_monitoring.py .............  [ 33%]
services/gateway/apps/monitoring/tests/test_monitoring_service.py ...... [ 34%]
................                                                         [ 36%]
services/gateway/apps/notifications/tests/test_notification_api.py ..... [ 37%]
.......                                                                  [ 37%]
services/gateway/apps/projects/tests/test_attachment_model.py .......... [ 38%]
......                                                                   [ 39%]
services/gateway/apps/projects/tests/test_requirements_views.py ........ [ 40%]
..........                                                               [ 41%]
services/gateway/apps/projects/tests/test_share_link.py ........         [ 42%]
services/gateway/apps/projects/tests/test_views.py .................     [ 44%]
services/gateway/apps/requirements_document/tests/test_views.py ........ [ 45%]
..............                                                           [ 47%]
services/gateway/apps/review/tests/test_review_actions.py .............. [ 48%]
.....                                                                    [ 49%]
services/gateway/apps/review/tests/test_review_assignments.py .......... [ 50%]
..                                                                       [ 50%]
services/gateway/apps/review/tests/test_review_list.py ...........       [ 51%]
services/gateway/apps/review/tests/test_review_timeline.py ............. [ 53%]
..                                                                       [ 53%]
services/gateway/apps/review/tests/test_submit.py .............          [ 55%]
services/gateway/apps/websocket/tests/test_access.py .....               [ 55%]
services/gateway/apps/websocket/tests/test_ai_consumer.py ............   [ 56%]
services/gateway/apps/websocket/tests/test_middleware.py .....           [ 57%]
services/gateway/storage/tests/test_backends.py .....................    [ 59%]
services/ai/tests/test_brd_pipeline.py ...........................       [ 62%]
services/ai/tests/test_context_agent.py .............                    [ 64%]
services/ai/tests/test_context_assembly_attachments.py ................. [ 66%]
.......                                                                  [ 67%]
services/ai/tests/test_context_buckets.py ........                       [ 68%]
services/ai/tests/test_context_compression.py ..................         [ 70%]
services/ai/tests/test_context_extension.py ............                 [ 71%]
services/ai/tests/test_context_retrieval.py ........                     [ 72%]
services/ai/tests/test_debouncer.py .........                            [ 73%]
services/ai/tests/test_embedding_pipeline.py .......................     [ 76%]
services/ai/tests/test_extract_attachment.py ...................         [ 78%]
services/ai/tests/test_facilitator.py .................................. [ 82%]
...........................                                              [ 85%]
services/ai/tests/test_pipeline.py .........................             [ 88%]
services/ai/tests/test_pipeline_extraction_wait.py ......                [ 88%]
services/ai/tests/test_summarizing_ai.py ............................... [ 92%]
......................                                                   [ 94%]
services/gateway/apps/websocket/tests/test_consumers.py ................ [ 96%]
...                                                                      [ 96%]
services/pdf/tests/test_pdf_service.py ..........................        [ 99%]
tests/test_smoke.py .                                                    [100%]

=============================== warnings summary ===============================
../usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371
  /usr/local/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2371: PydanticDeprecatedSince211: The `__get_pydantic_core_schema__` method of the `BaseModel` class is deprecated. If you are calling `super().__get_pydantic_core_schema__` when overriding the method on a Pydantic model, consider using `handler(source)` instead. However, note that overriding this method on models can lead to unexpected side effects. Deprecated in Pydantic V2.11 to be removed in V3.0.
    schema = annotation_get_schema(source, get_inner_schema)

../usr/local/lib/python3.12/site-packages/requests/__init__.py:113
  /usr/local/lib/python3.12/site-packages/requests/__init__.py:113: RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.2.0)/charset_normalizer (3.4.6) doesn't match a supported version!
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

services/pdf/tests/test_pdf_service.py: 21 warnings
  /usr/local/lib/python3.12/site-packages/pydyf/__init__.py:404: DeprecationWarning: transform is deprecated, use set_matrix instead.
    warn(Stream.transform.__doc__, DeprecationWarning)

services/pdf/tests/test_pdf_service.py: 123 warnings
  /usr/local/lib/python3.12/site-packages/pydyf/__init__.py:399: DeprecationWarning: text_matrix is deprecated, use set_text_matrix instead.
    warn(Stream.text_matrix.__doc__, DeprecationWarning)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================== 878 passed, 151 warnings in 33.15s ======================

```
