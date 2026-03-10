# Test Results: pre-QA M6 cycle 2
Date: 2026-03-10T06:03:16+0100
Command: docker compose -f docker-compose.test.yml run --rm python-tests pytest
Exit code: 1
Result: FAIL

## Output
```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
django: version: 5.2.12, settings: gateway.settings.test (from env)
rootdir: /app
configfile: pyproject.toml
plugins: django-4.12.0, cov-5.0.0, asyncio-0.26.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 142 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  4%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  9%]
services/gateway/apps/board/tests/test_views.py ........................ [ 26%]
.......................                                                  [ 42%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 52%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 61%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 64%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 76%]
services/gateway/apps/websocket/tests/test_consumers.py ..E.E.E.E.E.E..E [ 88%]
.E...E..E.E.E...                                                         [ 99%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
_______________ ERROR at setup of test_connection_missing_token ________________

self = <django.db.backends.utils.CursorWrapper object at 0x78c179fe9df0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179fe9df0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_connection_missing_token>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c179fe9df0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179fe9df0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at setup of test_error_on_unknown_message_type _____________

self = <django.db.backends.utils.CursorWrapper object at 0x78c17bb388c0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c17bb388c0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_error_on_unknown_message_type>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c17bb388c0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c17bb388c0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________________ ERROR at setup of test_subscribe_idea_as_owner ________________

self = <django.db.backends.utils.CursorWrapper object at 0x78c178fa6360>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178fa6360>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_subscribe_idea_as_owner>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178fa6360>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178fa6360>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____________ ERROR at setup of test_subscribe_idea_as_collaborator _____________

self = <django.db.backends.utils.CursorWrapper object at 0x78c179f6c680>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179f6c680>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_subscribe_idea_as_collaborator>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c179f6c680>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179f6c680>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at setup of test_subscribe_idea_nonexistent _______________

self = <django.db.backends.utils.CursorWrapper object at 0x78c178f8fd40>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178f8fd40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_subscribe_idea_nonexistent>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178f8fd40>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178f8fd40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at setup of test_subscribe_idea_invalid_uuid ______________

self = <django.db.backends.utils.CursorWrapper object at 0x78c179feb350>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179feb350>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_subscribe_idea_invalid_uuid>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c179feb350>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c179feb350>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at setup of test_disconnect_cleans_up_groups ______________

self = <django.db.backends.utils.CursorWrapper object at 0x78c17a3733e0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c17a3733e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_disconnect_cleans_up_groups>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c17a3733e0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c17a3733e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of test_chat_message_broadcast_not_received_by_unsubscribed __

self = <django.db.backends.utils.CursorWrapper object at 0x78c178efc650>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178efc650>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_chat_message_broadcast_not_received_by_unsubscribed>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178efc650>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178efc650>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of test_board_update_broadcast_via_view_helper _________

self = <django.db.backends.utils.CursorWrapper object at 0x78c178edc170>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178edc170>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_board_update_broadcast_via_view_helper>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178edc170>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178edc170>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of test_board_selection_broadcast_excludes_sender _______

self = <django.db.backends.utils.CursorWrapper object at 0x78c178efeb40>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178efeb40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_board_selection_broadcast_excludes_sender>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178efeb40>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178efeb40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_________ ERROR at setup of test_board_selection_not_subscribed_error __________

self = <django.db.backends.utils.CursorWrapper object at 0x78c178edddf0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178edddf0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_board_selection_not_subscribed_error>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178edddf0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178edddf0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____________ ERROR at setup of test_presence_broadcast_on_subscribe ____________

self = <django.db.backends.utils.CursorWrapper object at 0x78c178f91820>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178f91820>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_marker' for <Coroutine test_presence_broadcast_on_subscribe>>

    @pytest.fixture(autouse=True)
    def _django_db_marker(request: pytest.FixtureRequest) -> None:
        """Implement the django_db marker, internal to pytest-django."""
        marker = request.node.get_closest_marker("django_db")
        if marker:
>           request.getfixturevalue("_django_db_helper")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:566: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:289: in _django_db_helper
    PytestDjangoTestCase.setUpClass()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1123: in setUpClass
    cls._pre_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1155: in _pre_setup
    cls._fixture_setup()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1211: in _fixture_setup
    connections[db_name].creation.deserialize_db_from_string(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/creation.py:163: in deserialize_db_from_string
    obj.save()
/usr/local/lib/python3.12/site-packages/django/core/serializers/base.py:265: in save
    models.Model.save_base(self.object, using=using, raw=True, **kwargs)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1008: in save_base
    updated = self._save_table(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1169: in _save_table
    results = self._do_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:1210: in _do_insert
    return manager._insert(
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1873: in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1882: in execute_sql
    cursor.execute(sql, params)
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:79: in execute
    return self._execute_with_wrappers(
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:92: in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:100: in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <django.db.backends.utils.CursorWrapper object at 0x78c178f91820>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x78c178f91820>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_pkey"
E               DETAIL:  Key (id)=(1) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
=========================== short test summary info ============================
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_connection_missing_token
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_unknown_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_owner
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_collaborator
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_nonexistent
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_invalid_uuid
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_disconnect_cleans_up_groups
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_not_received_by_unsubscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_via_view_helper
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_broadcast_excludes_sender
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_not_subscribed_error
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_presence_broadcast_on_subscribe
======================= 130 passed, 12 errors in 27.81s ========================

```
