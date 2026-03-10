# Test Results: pre-QA M5 cycle 0
Date: 2026-03-10T03:22:23+0100
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
collected 108 items

services/gateway/apps/authentication/tests/test_azure_ad.py EEEEEE       [  5%]
services/gateway/apps/authentication/tests/test_dev_bypass.py EEEEEEE    [ 12%]
services/gateway/apps/board/tests/test_views.py EEEEEEEEEEEEEEEEEEEEEEEE [ 34%]
EEEEEEEEEEEEEEEEEEEEE                                                    [ 53%]
services/gateway/apps/chat/tests/test_chat_messages.py EEEEEEEEEEEEEEE   [ 67%]
services/gateway/apps/chat/tests/test_reactions.py EEEEEEEEEEEE          [ 78%]
services/gateway/apps/collaboration/tests/test_views.py EEEEE            [ 83%]
services/gateway/apps/ideas/tests/test_views.py EEEEEEEEEEEEEEEEE        [ 99%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
_______ ERROR at setup of TestAzureADAuth.test_expired_token_returns_401 _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______ ERROR at setup of TestAzureADAuth.test_malformed_token_returns_401 ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestAzureADAuth.test_missing_token_returns_401 _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______ ERROR at setup of TestAzureADAuth.test_roles_synced_from_ad_groups ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestAzureADAuth.test_valid_token_validates_and_syncs ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestAzureADAuth.test_validate_upserts_existing_user _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_expired_token_returns_401>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestDevBypass.test_dev_login_404_without_auth_bypass ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestDevBypass.test_dev_login_creates_session ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestDevBypass.test_dev_login_nonexistent_user_returns_404 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______ ERROR at setup of TestDevBypass.test_dev_switch_404_without_debug _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____________ ERROR at setup of TestDevBypass.test_dev_switch_works _____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestDevBypass.test_dev_users_endpoint_404_in_production ___

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestDevBypass.test_dev_users_endpoint_in_bypass_mode ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_dev_login_404_without_auth_bypass>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestBoardNodesAPI.test_collaborator_can_access_nodes ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestBoardNodesAPI.test_create_box_node_returns_201 _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestBoardNodesAPI.test_create_free_text_node ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__________ ERROR at setup of TestBoardNodesAPI.test_create_group_node __________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_body_too_long_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_invalid_type_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_missing_type_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestBoardNodesAPI.test_create_node_persists _________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_title_too_long_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestBoardNodesAPI.test_create_node_with_group_parent ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_create_node_with_non_group_parent_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestBoardNodesAPI.test_delete_node_detaches_children ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestBoardNodesAPI.test_delete_node_returns_204 _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_delete_nonexistent_node_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_delete_unauthenticated_returns_401 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__________ ERROR at setup of TestBoardNodesAPI.test_list_nodes_empty ___________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestBoardNodesAPI.test_list_nodes_no_access_returns_403 ___

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_list_nodes_nonexistent_idea_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestBoardNodesAPI.test_list_nodes_returns_200 ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_list_nodes_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___ ERROR at setup of TestBoardNodesAPI.test_update_locked_node_returns_403 ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestBoardNodesAPI.test_update_node_parent_must_be_group ___

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestBoardNodesAPI.test_update_node_returns_200 _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardNodesAPI.test_update_nonexistent_node_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_collaborator_can_access_nodes>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_cascade_delete_node_removes_connections _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_collaborator_can_access_connections _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_no_label ___

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_nonexistent_source_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_nonexistent_target_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_persists ___

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_returns_201 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_connection_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_duplicate_connection_returns_409 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_create_self_connection_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_delete_connection_returns_204 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_delete_connection_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_delete_nonexistent_connection_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestBoardConnectionsAPI.test_list_connections_empty _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_list_connections_no_access_returns_403 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_list_connections_returns_200 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_list_connections_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_update_connection_clear_label _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_update_connection_label_returns_200 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestBoardConnectionsAPI.test_update_nonexistent_connection_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_cascade_delete_node_removes_connections>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_collaborator_allowed _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_empty_content_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_missing_content_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_no_access_returns_403 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_nonexistent_idea_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______ ERROR at setup of TestChatMessagesAPI.test_create_message_persists ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestChatMessagesAPI.test_create_message_returns_201 _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_create_message_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestChatMessagesAPI.test_list_messages_empty ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_list_messages_no_access_returns_403 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_list_messages_nonexistent_idea_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_list_messages_ordered_by_created_at_asc _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestChatMessagesAPI.test_list_messages_pagination ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestChatMessagesAPI.test_list_messages_returns_200 _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestChatMessagesAPI.test_list_messages_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_message_collaborator_allowed>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestUserReactionsAPI.test_duplicate_reaction_returns_409 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__ ERROR at setup of TestUserReactionsAPI.test_react_invalid_type_returns_400 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___ ERROR at setup of TestUserReactionsAPI.test_react_no_access_returns_403 ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_react_nonexistent_message_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestUserReactionsAPI.test_react_persists_in_database ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestUserReactionsAPI.test_react_thumbs_down_valid ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_react_to_ai_message_returns_400 __

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_react_to_other_user_message_returns_201 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_react_to_own_message_returns_400 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_react_unauthenticated_returns_401 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestUserReactionsAPI.test_remove_nonexistent_reaction_returns_404 _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___ ERROR at setup of TestUserReactionsAPI.test_remove_reaction_returns_204 ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_duplicate_reaction_returns_409>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_ ERROR at setup of TestInvitationsList.test_does_not_return_other_users_invitations _

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_does_not_return_other_users_invitations>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestInvitationsList.test_empty_list_if_no_pending ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_does_not_return_other_users_invitations>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestInvitationsList.test_list_pending_invitations ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_does_not_return_other_users_invitations>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestInvitationsList.test_only_pending_returned _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_does_not_return_other_users_invitations>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestInvitationsList.test_unauthenticated_returns_401 ____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_does_not_return_other_users_invitations>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestIdeasCRUD.test_create_idea_empty_first_message _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______ ERROR at setup of TestIdeasCRUD.test_create_idea_unauthenticated _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at setup of TestIdeasCRUD.test_create_idea_with_first_message ______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at setup of TestIdeasCRUD.test_filter_by_state _____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__________ ERROR at setup of TestIdeasCRUD.test_filter_collaborating ___________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at setup of TestIdeasCRUD.test_filter_my_ideas _____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at setup of TestIdeasCRUD.test_filter_trash _______________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____________ ERROR at setup of TestIdeasCRUD.test_get_idea_as_owner ____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestIdeasCRUD.test_get_idea_non_owner_denied ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at setup of TestIdeasCRUD.test_get_idea_not_found ____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______________ ERROR at setup of TestIdeasCRUD.test_list_ideas ________________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at setup of TestIdeasCRUD.test_restore_clears_deleted_at ________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at setup of TestIdeasCRUD.test_restore_from_trash ____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at setup of TestIdeasCRUD.test_search_by_title _____________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_______________ ERROR at setup of TestIdeasCRUD.test_soft_delete _______________

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______ ERROR at setup of TestIdeasCRUD.test_soft_delete_appears_in_trash _______

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
____ ERROR at setup of TestIdeasCRUD.test_unauthenticated_list_returns_401 _____

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_setup_unittest' for <TestCaseFunction test_create_idea_empty_first_message>>
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x7cb3e33cb740>

    @pytest.fixture(autouse=True, scope="class")
    def _django_setup_unittest(
        request: pytest.FixtureRequest,
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        """Setup a django unittest, internal to pytest-django."""
        if not django_settings_is_configured() or not is_django_unittest(request):
            yield
            return
    
        # Fix/patch pytest.
        # Before pytest 5.4: https://github.com/pytest-dev/pytest/issues/5991
        # After pytest 5.4: https://github.com/pytest-dev/pytest-django/issues/824
        from _pytest.unittest import TestCaseFunction
    
        original_runtest = TestCaseFunction.runtest
    
        def non_debugging_runtest(self) -> None:  # noqa: ANN001
            self._testcase(result=self)
    
        from django.test import SimpleTestCase
    
        assert issubclass(request.cls, SimpleTestCase)  # Guarded by 'is_django_unittest'
        try:
            TestCaseFunction.runtest = non_debugging_runtest  # type: ignore[method-assign]
    
            # Don't set up the DB if the unittest does not require DB.
            # The `databases` propery seems like the best indicator for that.
            if request.cls.databases:
>               request.getfixturevalue("django_db_setup")

/usr/local/lib/python3.12/site-packages/pytest_django/plugin.py:598: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
conftest.py:19: in django_db_setup
    call_command("migrate", "--run-syncdb", verbosity=0)
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:111: in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/migrate.py:380: in handle
    emit_post_migrate_signal(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:825: in bulk_create
    returned_columns = self._batched_insert(
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:1901: in _batched_insert
    self._insert(
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

self = <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [7, 7, 7, 7], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x7cb3de648830>})

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
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "auth_permission_content_type_id_codename_01ab375a_uniq"
E               DETAIL:  Key (content_type_id, codename)=(7, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
=========================== short test summary info ============================
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_expired_token_returns_401
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_malformed_token_returns_401
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_missing_token_returns_401
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_roles_synced_from_ad_groups
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_valid_token_validates_and_syncs
ERROR services/gateway/apps/authentication/tests/test_azure_ad.py::TestAzureADAuth::test_validate_upserts_existing_user
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_404_without_auth_bypass
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_creates_session
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_nonexistent_user_returns_404
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_switch_404_without_debug
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_switch_works
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_users_endpoint_404_in_production
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_users_endpoint_in_bypass_mode
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_collaborator_can_access_nodes
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_box_node_returns_201
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_free_text_node
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_group_node
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_body_too_long_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_invalid_type_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_missing_type_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_persists
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_title_too_long_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_with_group_parent
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_create_node_with_non_group_parent_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_delete_node_detaches_children
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_delete_node_returns_204
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_delete_nonexistent_node_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_delete_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_list_nodes_empty
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_list_nodes_no_access_returns_403
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_list_nodes_nonexistent_idea_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_list_nodes_returns_200
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_list_nodes_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_update_locked_node_returns_403
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_update_node_parent_must_be_group
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_update_node_returns_200
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardNodesAPI::test_update_nonexistent_node_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_cascade_delete_node_removes_connections
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_collaborator_can_access_connections
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_no_label
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_nonexistent_source_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_nonexistent_target_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_persists
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_returns_201
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_connection_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_duplicate_connection_returns_409
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_create_self_connection_returns_400
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_delete_connection_returns_204
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_delete_connection_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_delete_nonexistent_connection_returns_404
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_list_connections_empty
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_list_connections_no_access_returns_403
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_list_connections_returns_200
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_list_connections_unauthenticated_returns_401
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_update_connection_clear_label
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_update_connection_label_returns_200
ERROR services/gateway/apps/board/tests/test_views.py::TestBoardConnectionsAPI::test_update_nonexistent_connection_returns_404
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_collaborator_allowed
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_empty_content_returns_400
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_missing_content_returns_400
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_no_access_returns_403
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_nonexistent_idea_returns_404
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_persists
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_returns_201
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_create_message_unauthenticated_returns_401
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_empty
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_no_access_returns_403
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_nonexistent_idea_returns_404
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_ordered_by_created_at_asc
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_pagination
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_returns_200
ERROR services/gateway/apps/chat/tests/test_chat_messages.py::TestChatMessagesAPI::test_list_messages_unauthenticated_returns_401
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_duplicate_reaction_returns_409
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_invalid_type_returns_400
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_no_access_returns_403
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_nonexistent_message_returns_404
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_persists_in_database
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_thumbs_down_valid
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_to_ai_message_returns_400
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_to_other_user_message_returns_201
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_to_own_message_returns_400
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_react_unauthenticated_returns_401
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_remove_nonexistent_reaction_returns_404
ERROR services/gateway/apps/chat/tests/test_reactions.py::TestUserReactionsAPI::test_remove_reaction_returns_204
ERROR services/gateway/apps/collaboration/tests/test_views.py::TestInvitationsList::test_does_not_return_other_users_invitations
ERROR services/gateway/apps/collaboration/tests/test_views.py::TestInvitationsList::test_empty_list_if_no_pending
ERROR services/gateway/apps/collaboration/tests/test_views.py::TestInvitationsList::test_list_pending_invitations
ERROR services/gateway/apps/collaboration/tests/test_views.py::TestInvitationsList::test_only_pending_returned
ERROR services/gateway/apps/collaboration/tests/test_views.py::TestInvitationsList::test_unauthenticated_returns_401
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_create_idea_empty_first_message
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_create_idea_unauthenticated
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_create_idea_with_first_message
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_filter_by_state
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_filter_collaborating
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_filter_my_ideas
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_filter_trash
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_get_idea_as_owner
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_get_idea_non_owner_denied
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_get_idea_not_found
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_list_ideas
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_restore_clears_deleted_at
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_restore_from_trash
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_search_by_title
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_soft_delete
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_soft_delete_appears_in_trash
ERROR services/gateway/apps/ideas/tests/test_views.py::TestIdeasCRUD::test_unauthenticated_list_returns_401
======================== 1 passed, 107 errors in 17.69s ========================

```
