# Test Results: pre-QA M6 cycle 0
Date: 2026-03-10T12:52:20+0100
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
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 142 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [  4%]
services/gateway/apps/authentication/tests/test_dev_bypass.py .......    [  9%]
services/gateway/apps/board/tests/test_views.py ........................ [ 26%]
.......................                                                  [ 42%]
services/gateway/apps/chat/tests/test_chat_messages.py ...............   [ 52%]
services/gateway/apps/chat/tests/test_reactions.py ............          [ 61%]
services/gateway/apps/collaboration/tests/test_views.py .....            [ 64%]
services/gateway/apps/ideas/tests/test_views.py .................        [ 76%]
services/gateway/apps/websocket/tests/test_consumers.py .....EE.E.E.E.E. [ 88%]
....E.E..E.E..E.                                                         [ 99%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
_____________ ERROR at setup of test_error_on_missing_message_type _____________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d88140>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d88140>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_error_on_missing_message_type>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d88140>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d88140>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e53daa600>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e53daa600>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e53daa600>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e53daa600>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d53200>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d53200>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d53200>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d53200>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d7da90>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d7da90>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d7da90>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d7da90>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e53d2faa0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e53d2faa0>})

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e53d2faa0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e53d2faa0>})

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
____________ ERROR at setup of test_unsubscribe_idea_not_subscribed ____________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d2b2f0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d2b2f0>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_unsubscribe_idea_not_subscribed>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d2b2f0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d2b2f0>})

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
_______ ERROR at setup of test_board_update_not_received_by_unsubscribed _______

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d29550>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d29550>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_board_update_not_received_by_unsubscribed>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d29550>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d29550>})

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
__________ ERROR at setup of test_board_update_broadcast_node_delete ___________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d20e90>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d20e90>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_board_update_broadcast_node_delete>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d20e90>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d20e90>})

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
__________ ERROR at setup of test_board_selection_deselect_null_node ___________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d23dd0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d23dd0>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_board_selection_deselect_null_node>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52d23dd0>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52d23dd0>})

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
______________ ERROR at setup of test_board_lock_change_broadcast ______________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52b04440>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52b04440>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_board_lock_change_broadcast>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52b04440>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52b04440>})

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
____________ ERROR at setup of test_presence_offline_on_unsubscribe ____________

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52b07980>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52b07980>})

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

request = <SubRequest '_django_db_marker' for <Coroutine test_presence_offline_on_unsubscribe>>

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

self = <django.db.backends.utils.CursorWrapper object at 0x7d6e52b07980>
sql = 'INSERT INTO "auth_permission" ("id", "name", "content_type_id", "codename") VALUES (%s, %s, %s, %s) RETURNING "auth_permission"."id"'
params = (1, 'Can add permission', 1, 'add_permission')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7d6e52b07980>})

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
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_missing_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_owner
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_collaborator
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_nonexistent
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_invalid_uuid
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_unsubscribe_idea_not_subscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_not_received_by_unsubscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_node_delete
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_deselect_null_node
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_lock_change_broadcast
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_presence_offline_on_unsubscribe
======================= 131 passed, 11 errors in 32.61s ========================

```
