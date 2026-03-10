# Test Results: pre-QA M6 cycle 0
Date: 2026-03-10T05:08:41+0100
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
services/gateway/apps/websocket/tests/test_consumers.py ...E.E.E.EFEFEFE [ 83%]
..E...E.E..E...FE...E.EFE..F..F                                          [ 99%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
______________ ERROR at teardown of test_connection_missing_token ______________

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    def _commit(self):
        if self.connection is not None:
            with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
>               return self.connection.commit()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.ForeignKeyViolation: insert or update on table "auth_permission" violates foreign key constraint "auth_permission_content_type_id_2f476e4b_fk_django_co"
E               DETAIL:  Key (content_type_id)=(62) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: ForeignKeyViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_connection_missing_token>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:805: in bulk_create
    with transaction.atomic(using=self.db, savepoint=False):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:263: in __exit__
    connection.commit()
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:327: in commit
    self._commit()
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:302: in _commit
    with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    def _commit(self):
        if self.connection is not None:
            with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
>               return self.connection.commit()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: insert or update on table "auth_permission" violates foreign key constraint "auth_permission_content_type_id_2f476e4b_fk_django_co"
E               DETAIL:  Key (content_type_id)=(62) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: IntegrityError
_________ ERROR at teardown of test_connection_nonexistent_user_token __________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccb09c70>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccb09c70>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_connection_nonexistent_user_token>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccb09c70>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccb09c70>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at teardown of test_error_on_unknown_message_type ____________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd7dd0>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add session', 'Can change session', 'Can delete session', 'Can view session'], [105, 105, 105, 105], ['add_session', 'change_session', 'delete_session', 'view_session'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd7dd0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(105, add_session) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_error_on_unknown_message_type>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd7dd0>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add session', 'Can change session', 'Can delete session', 'Can view session'], [105, 105, 105, 105], ['add_session', 'change_session', 'delete_session', 'view_session'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd7dd0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(105, add_session) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at teardown of test_error_on_missing_message_type ____________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd53d0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd53d0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_error_on_missing_message_type>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd53d0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd53d0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at teardown of test_subscribe_idea_as_owner _______________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccce9cd0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccce9cd0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_subscribe_idea_as_owner>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccce9cd0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccce9cd0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at teardown of test_subscribe_idea_as_co_owner _____________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cca98f50>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cca98f50>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_subscribe_idea_as_co_owner>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cca98f50>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cca98f50>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at teardown of test_subscribe_idea_as_collaborator ___________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39430>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39430>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_subscribe_idea_as_collaborator>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39430>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39430>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____________ ERROR at teardown of test_subscribe_idea_nonexistent _____________

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    def _commit(self):
        if self.connection is not None:
            with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
>               return self.connection.commit()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.ForeignKeyViolation: insert or update on table "auth_permission" violates foreign key constraint "auth_permission_content_type_id_2f476e4b_fk_django_co"
E               DETAIL:  Key (content_type_id)=(225) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: ForeignKeyViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_subscribe_idea_nonexistent>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:105: in create_permissions
    Permission.objects.using(using).bulk_create(perms)
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:805: in bulk_create
    with transaction.atomic(using=self.db, savepoint=False):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:263: in __exit__
    connection.commit()
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:327: in commit
    self._commit()
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:302: in _commit
    with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    def _commit(self):
        if self.connection is not None:
            with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
>               return self.connection.commit()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: insert or update on table "auth_permission" violates foreign key constraint "auth_permission_content_type_id_2f476e4b_fk_django_co"
E               DETAIL:  Key (content_type_id)=(225) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: IntegrityError
__________________ ERROR at teardown of test_unsubscribe_idea __________________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc67830>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('admin_config', 'adminparameter')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc67830>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(admin_config, adminparameter) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_unsubscribe_idea>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc67830>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('admin_config', 'adminparameter')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc67830>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(admin_config, adminparameter) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__________ ERROR at teardown of test_unsubscribe_idea_not_subscribed ___________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cc9b6c90>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cc9b6c90>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_unsubscribe_idea_not_subscribed>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cc9b6c90>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cc9b6c90>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at teardown of test_chat_message_broadcast_to_subscriber ________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cb113a40>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add collaboration invitation', 'Can change collaboration invitation', 'Can delete collaboration invitation', 'C...rationinvitation', 'change_collaborationinvitation', 'delete_collaborationinvitation', 'view_collaborationinvitation'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cb113a40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(388, add_collaborationinvitation) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_chat_message_broadcast_to_subscriber>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cb113a40>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add collaboration invitation', 'Can change collaboration invitation', 'Can delete collaboration invitation', 'C...rationinvitation', 'change_collaborationinvitation', 'delete_collaborationinvitation', 'view_collaborationinvitation'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cb113a40>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(388, add_collaborationinvitation) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at teardown of test_board_update_not_received_by_unsubscribed ______

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cb1891c0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('authentication', 'user')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cb1891c0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(authentication, user) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_update_not_received_by_unsubscribed>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0cb1891c0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('authentication', 'user')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0cb1891c0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(authentication, user) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
__________ ERROR at teardown of test_board_update_broadcast_source_ai __________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd64e0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd64e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_update_broadcast_source_ai>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd64e0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccbd64e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at teardown of test_board_selection_broadcast_excludes_sender ______

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc00260>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc00260>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_selection_broadcast_excludes_sender>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc00260>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc00260>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(auth, permission) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_________ ERROR at teardown of test_board_selection_deselect_null_node _________

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39790>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('sessions', 'session')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39790>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(sessions, session) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_selection_deselect_null_node>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x72b0d0e05400>

    @pytest.fixture
    def _django_db_helper(
        request: pytest.FixtureRequest,
        django_db_setup: None,  # noqa: ARG001
        django_db_blocker: DjangoDbBlocker,
    ) -> Generator[None, None, None]:
        if is_django_unittest(request):
            yield
            return
    
        marker = request.node.get_closest_marker("django_db")
        if marker:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = validate_django_db(marker)
        else:
            (
                transactional,
                reset_sequences,
                databases,
                serialized_rollback,
                available_apps,
            ) = False, False, None, False, None
    
        transactional = (
            transactional
            or reset_sequences
            or ("transactional_db" in request.fixturenames or "live_server" in request.fixturenames)
        )
        reset_sequences = reset_sequences or ("django_db_reset_sequences" in request.fixturenames)
        serialized_rollback = serialized_rollback or (
            "django_db_serialized_rollback" in request.fixturenames
        )
    
        with django_db_blocker.unblock():
            import django.db
            import django.test
    
            if transactional:
                test_case_class = django.test.TransactionTestCase
            else:
                test_case_class = django.test.TestCase
    
            _reset_sequences = reset_sequences
            _serialized_rollback = serialized_rollback
            _databases = databases
            _available_apps = available_apps
    
            class PytestDjangoTestCase(test_case_class):  # type: ignore[misc,valid-type]
                reset_sequences = _reset_sequences
                serialized_rollback = _serialized_rollback
                if _databases is not None:
                    databases = _databases
                if _available_apps is not None:
                    available_apps = _available_apps
    
                # For non-transactional tests, skip executing `django.test.TestCase`'s
                # `setUpClass`/`tearDownClass`, only execute the super class ones.
                #
                # `TestCase`'s class setup manages the `setUpTestData`/class-level
                # transaction functionality. We don't use it; instead we (will) offer
                # our own alternatives. So it only adds overhead, and does some things
                # which conflict with our (planned) functionality, particularly, it
                # closes all database connections in `tearDownClass` which inhibits
                # wrapping tests in higher-scoped transactions.
                #
                # It's possible a new version of Django will add some unrelated
                # functionality to these methods, in which case skipping them completely
                # would not be desirable. Let's cross that bridge when we get there...
                if not transactional:
    
                    @classmethod
                    def setUpClass(cls) -> None:
                        super(django.test.TestCase, cls).setUpClass()
    
                    @classmethod
                    def tearDownClass(cls) -> None:
                        super(django.test.TestCase, cls).tearDownClass()
    
            PytestDjangoTestCase.setUpClass()
    
            test_case = PytestDjangoTestCase(methodName="__init__")
            test_case._pre_setup()
    
            yield
    
>           test_case._post_teardown()

/usr/local/lib/python3.12/site-packages/pytest_django/fixtures.py:296: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1231: in _post_teardown
    self._fixture_teardown()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:1266: in _fixture_teardown
    call_command(
/usr/local/lib/python3.12/site-packages/django/core/management/__init__.py:194: in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/base.py:464: in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:91: in handle
    emit_post_migrate_signal(verbosity, interactive, database)
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:52: in emit_post_migrate_signal
    models.signals.post_migrate.send(
/usr/local/lib/python3.12/site-packages/django/dispatch/dispatcher.py:189: in send
    response = receiver(signal=self, sender=sender, **named)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/contrib/auth/management/__init__.py:59: in create_permissions
    create_contenttypes(
/usr/local/lib/python3.12/site-packages/django/contrib/contenttypes/management/__init__.py:142: in create_contenttypes
    ContentType.objects.using(using).bulk_create(cts)
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

self = <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39790>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('sessions', 'session')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x72b0ccc39790>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
E               DETAIL:  Key (app_label, model)=(sessions, session) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
=================================== FAILURES ===================================
_________________________ test_subscribe_idea_as_owner _________________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_subscribe_idea_as_owner():
        """T-6.1.04: Owner can subscribe to idea group."""
        user = await _create_user()
        idea = await _create_idea(owner_id=user.id)
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:174: AssertionError
_______________________ test_subscribe_idea_as_co_owner ________________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_subscribe_idea_as_co_owner():
        """T-6.1.04b: Co-owner can subscribe to idea group."""
        owner = await _create_user(display_name="Owner")
        co_owner = await _create_user(display_name="CoOwner")
        idea = await _create_idea(owner_id=owner.id, co_owner_id=co_owner.id)
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={co_owner.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:193: AssertionError
_____________________ test_subscribe_idea_as_collaborator ______________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_subscribe_idea_as_collaborator():
        """T-6.1.04c: Collaborator can subscribe to idea group."""
        owner = await _create_user(display_name="Owner")
        collaborator = await _create_user(display_name="Collaborator")
        idea = await _create_idea(owner_id=owner.id)
        await _add_collaborator(idea_id=idea.id, user_id=collaborator.id)
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={collaborator.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:213: AssertionError
________________ test_board_update_not_received_by_unsubscribed ________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_board_update_not_received_by_unsubscribed():
        """T-6.4.03b: Unsubscribed clients do not receive board_update broadcasts."""
        user = await _create_user()
        idea = await _create_idea(owner_id=user.id)
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:575: AssertionError
___________________ test_board_selection_deselect_null_node ____________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_board_selection_deselect_null_node():
        """T-3.5.03: board_selection with node_id=null broadcasts deselection."""
        owner = await _create_user(display_name="Owner")
        other = await _create_user(display_name="Other")
        idea = await _create_idea(owner_id=owner.id)
        await _add_collaborator(idea_id=idea.id, user_id=other.id)
        app = _make_application()
    
        comm_sender = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
        comm_receiver = WebsocketCommunicator(app, f"/ws/?token={other.id}")
    
        connected1, _ = await comm_sender.connect()
        connected2, _ = await comm_receiver.connect()
>       assert connected1 and connected2
E       assert (False)

services/gateway/apps/websocket/tests/test_consumers.py:788: AssertionError
_____________________ test_presence_broadcast_on_subscribe _____________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_broadcast_on_subscribe():
        """T-6.3.01: Subscribe to idea broadcasts presence_update 'online' to all subscribers."""
        owner = await _create_user(display_name="Owner")
        other = await _create_user(display_name="Other")
        idea = await _create_idea(owner_id=owner.id)
        await _add_collaborator(idea_id=idea.id, user_id=other.id)
        app = _make_application()
    
        # First user subscribes
        comm1 = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
        connected1, _ = await comm1.connect()
>       assert connected1
E       assert False

services/gateway/apps/websocket/tests/test_consumers.py:893: AssertionError
_____________________ test_presence_update_client_message ______________________

self = <django.db.backends.postgresql.base.CursorDebugWrapper object at 0x72b0cb18b1d0>
sql = 'INSERT INTO "idea_collaborators" ("id", "idea_id", "user_id", "joined_at") VALUES (%s, %s, %s, %s)'
params = (UUID('4abb862d-2178-4d31-a0de-6730de3ea15c'), UUID('93760567-b104-4c71-a8e6-96d929e8af7a'), UUID('0ecab566-3ee0-4d58-9325-af66bf1d3178'), datetime.datetime(2026, 3, 10, 4, 8, 39, 345316, tzinfo=datetime.timezone.utc))
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.postgresql.base.CursorDebugWrapper object at 0x72b0cb18b1d0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.ForeignKeyViolation: insert or update on table "idea_collaborators" violates foreign key constraint "idea_collaborators_idea_id_87eb9cdc_fk_ideas_id"
E               DETAIL:  Key (idea_id)=(93760567-b104-4c71-a8e6-96d929e8af7a) is not present in table "ideas".

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: ForeignKeyViolation

The above exception was the direct cause of the following exception:

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_update_client_message():
        """T-6.3.04: Client presence_update message broadcasts to idea group."""
        owner = await _create_user(display_name="Owner")
        other = await _create_user(display_name="Observer")
        idea = await _create_idea(owner_id=owner.id)
>       await _add_collaborator(idea_id=idea.id, user_id=other.id)

services/gateway/apps/websocket/tests/test_consumers.py:1023: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/asgiref/sync.py:506: in __call__
    ret = await asyncio.shield(exec_coro)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/concurrent/futures/thread.py:59: in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/channels/db.py:13: in thread_handler
    return super().thread_handler(loop, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/asgiref/sync.py:561: in thread_handler
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
services/gateway/apps/websocket/tests/test_consumers.py:65: in _add_collaborator
    return IdeaCollaborator.objects.create(idea_id=idea_id, user_id=user_id)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/manager.py:87: in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/models/query.py:665: in create
    obj.save(force_insert=True, using=self.db)
/usr/local/lib/python3.12/site-packages/django/db/models/base.py:902: in save
    self.save_base(
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
/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:122: in execute
    return super().execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

self = <django.db.backends.postgresql.base.CursorDebugWrapper object at 0x72b0cb18b1d0>
sql = 'INSERT INTO "idea_collaborators" ("id", "idea_id", "user_id", "joined_at") VALUES (%s, %s, %s, %s)'
params = (UUID('4abb862d-2178-4d31-a0de-6730de3ea15c'), UUID('93760567-b104-4c71-a8e6-96d929e8af7a'), UUID('0ecab566-3ee0-4d58-9325-af66bf1d3178'), datetime.datetime(2026, 3, 10, 4, 8, 39, 345316, tzinfo=datetime.timezone.utc))
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.postgresql.base.CursorDebugWrapper object at 0x72b0cb18b1d0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
            warnings.warn(self.APPS_NOT_READY_WARNING_MSG, category=RuntimeWarning)
        self.db.validate_no_broken_transaction()
        with self.db.wrap_database_errors:
            if params is None:
                # params default might be backend specific.
                return self.cursor.execute(sql)
            else:
>               return self.cursor.execute(sql, params)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E               django.db.utils.IntegrityError: insert or update on table "idea_collaborators" violates foreign key constraint "idea_collaborators_idea_id_87eb9cdc_fk_ideas_id"
E               DETAIL:  Key (idea_id)=(93760567-b104-4c71-a8e6-96d929e8af7a) is not present in table "ideas".

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
=========================== short test summary info ============================
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_owner
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_co_owner
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_collaborator
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_not_received_by_unsubscribed
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_deselect_null_node
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_broadcast_on_subscribe
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_update_client_message
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_connection_missing_token
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_connection_nonexistent_user_token
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_unknown_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_missing_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_owner
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_co_owner
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_collaborator
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_nonexistent
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_unsubscribe_idea
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_unsubscribe_idea_not_subscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_to_subscriber
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_not_received_by_unsubscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_source_ai
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_broadcast_excludes_sender
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_deselect_null_node
================== 7 failed, 135 passed, 15 errors in 40.68s ===================

```
