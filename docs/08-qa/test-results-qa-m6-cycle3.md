# Test Results: pre-QA M6 cycle 3
Date: 2026-03-10T06:21:44+0100
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
services/gateway/apps/websocket/tests/test_consumers.py .....E.E.E..F... [ 85%]
....E.FE.E.E..FE.E.E....EFFE                                             [ 99%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
___________ ERROR at teardown of test_error_on_unknown_message_type ____________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2cff0170>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [125, 125, 125, 125], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2cff0170>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(125, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_error_on_unknown_message_type>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2cff0170>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add notification', 'Can change notification', 'Can delete notification', 'Can view notification'], [125, 125, 125, 125], ['add_notification', 'change_notification', 'delete_notification', 'view_notification'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2cff0170>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(125, add_notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
___________ ERROR at teardown of test_error_on_missing_message_type ____________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bd662a0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bd662a0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bd662a0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bd662a0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    def _commit(self):
        if self.connection is not None:
            with debug_transaction(self, "COMMIT"), self.wrap_database_errors:
>               return self.connection.commit()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
E               psycopg2.errors.ForeignKeyViolation: insert or update on table "auth_permission" violates foreign key constraint "auth_permission_content_type_id_2f476e4b_fk_django_co"
E               DETAIL:  Key (content_type_id)=(158) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: ForeignKeyViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_subscribe_idea_as_owner>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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
E               DETAIL:  Key (content_type_id)=(158) is not present in table "django_content_type".

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:303: IntegrityError
________ ERROR at teardown of test_chat_message_broadcast_to_subscriber ________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb006e0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb006e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

request = <SubRequest '_django_db_helper' for <Coroutine test_chat_message_broadcast_to_subscriber>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb006e0>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb006e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
_______ ERROR at teardown of test_chat_message_broadcast_via_view_helper _______

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb49400>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('notifications', 'notification')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb49400>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (app_label, model)=(notifications, notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_chat_message_broadcast_via_view_helper>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb49400>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('notifications', 'notification')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb49400>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (app_label, model)=(notifications, notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
________ ERROR at teardown of test_board_update_broadcast_to_subscriber ________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4bf80>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('sessions', 'session')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4bf80>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

request = <SubRequest '_django_db_helper' for <Coroutine test_board_update_broadcast_to_subscriber>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4bf80>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('sessions', 'session')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4bf80>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
_____ ERROR at teardown of test_board_update_not_received_by_unsubscribed ______

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb3a300>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb3a300>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

request = <SubRequest '_django_db_helper' for <Coroutine test_board_update_not_received_by_unsubscribed>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb3a300>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb3a300>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
__________ ERROR at teardown of test_board_update_broadcast_source_ai __________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4d370>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('notifications', 'notification')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4d370>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (app_label, model)=(notifications, notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_update_broadcast_source_ai>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4d370>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") VALUES (%s, %s) RETURNING "django_content_type"."id"'
params = ('notifications', 'notification')
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4d370>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (app_label, model)=(notifications, notification) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
_____ ERROR at teardown of test_board_selection_broadcast_excludes_sender ______

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4f770>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4f770>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb4f770>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb4f770>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb876e0>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add monitoring alert config', 'Can change monitoring alert config', 'Can delete monitoring alert config', 'Can ..._monitoringalertconfig', 'change_monitoringalertconfig', 'delete_monitoringalertconfig', 'view_monitoringalertconfig'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb876e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(596, add_monitoringalertconfig) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: UniqueViolation

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_board_selection_deselect_null_node>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb876e0>
sql = 'INSERT INTO "auth_permission" ("name", "content_type_id", "codename") SELECT * FROM UNNEST((%s)::varchar[], (%s)::integer[], (%s)::varchar[]) RETURNING "auth_permission"."id"'
params = (['Can add monitoring alert config', 'Can change monitoring alert config', 'Can delete monitoring alert config', 'Can ..._monitoringalertconfig', 'change_monitoringalertconfig', 'delete_monitoringalertconfig', 'view_monitoringalertconfig'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb876e0>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
E               DETAIL:  Key (content_type_id, codename)=(596, add_monitoringalertconfig) already exists.

/usr/local/lib/python3.12/site-packages/django/db/backends/utils.py:105: IntegrityError
______________ ERROR at teardown of test_presence_multi_tab_dedup ______________

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb48440>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb48440>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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

request = <SubRequest '_django_db_helper' for <Coroutine test_presence_multi_tab_dedup>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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

self = <django.db.backends.utils.CursorWrapper object at 0x771e2bb48440>
sql = 'INSERT INTO "django_content_type" ("app_label", "model") SELECT * FROM UNNEST((%s)::varchar[], (%s)::varchar[]) RETURNING "django_content_type"."id"'
params = (['auth', 'auth', 'auth'], ['permission', 'group', 'user'])
ignored_wrapper_args = (False, {'connection': <DatabaseWrapper vendor='postgresql' alias='default'>, 'cursor': <django.db.backends.utils.CursorWrapper object at 0x771e2bb48440>})

    def _execute(self, sql, params, *ignored_wrapper_args):
        # Raise a warning during app initialization (stored_app_configs is only
        # ever set during testing).
        if not apps.ready and not apps.stored_app_configs:
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
___________ ERROR at teardown of test_presence_update_client_message ___________

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    @async_unsafe
    def ensure_connection(self):
        """Guarantee that a connection to the database is established."""
        if self.connection is None:
            if self.in_atomic_block and self.closed_in_transaction:
                raise ProgrammingError(
                    "Cannot open a new connection in an atomic block."
                )
            with self.wrap_database_errors:
>               self.connect()

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:279: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:256: in connect
    self.connection = self.get_new_connection(conn_params)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/postgresql/base.py:332: in get_new_connection
    connection = self.Database.connect(**conn_params)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

dsn = 'dbname=test_ziqreq_test client_encoding=UTF8 user=testuser password=testpass host=postgres port=5432'
connection_factory = None, cursor_factory = <class 'psycopg2.extensions.cursor'>
kwargs = {'client_encoding': 'UTF8', 'dbname': 'test_ziqreq_test', 'host': 'postgres', 'password': 'testpass', ...}
kwasync = {}

    def connect(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
        """
        Create a new database connection.
    
        The connection parameters can be specified as a string:
    
            conn = psycopg2.connect("dbname=test user=postgres password=secret")
    
        or using a set of keyword arguments:
    
            conn = psycopg2.connect(database="test", user="postgres", password="secret")
    
        Or as a mix of both. The basic connection parameters are:
    
        - *dbname*: the database name
        - *database*: the database name (only as keyword argument)
        - *user*: user name used to authenticate
        - *password*: password used to authenticate
        - *host*: database host address (defaults to UNIX socket if not provided)
        - *port*: connection port number (defaults to 5432 if not provided)
    
        Using the *connection_factory* parameter a different class or connections
        factory can be specified. It should be a callable object taking a dsn
        argument.
    
        Using the *cursor_factory* parameter, a new default cursor factory will be
        used by cursor().
    
        Using *async*=True an asynchronous connection will be created. *async_* is
        a valid alias (for Python versions where ``async`` is a keyword).
    
        Any other keyword parameter will be passed to the underlying client
        library: the list of supported parameters depends on the library version.
    
        """
        kwasync = {}
        if 'async' in kwargs:
            kwasync['async'] = kwargs.pop('async')
        if 'async_' in kwargs:
            kwasync['async_'] = kwargs.pop('async_')
    
        dsn = _ext.make_dsn(dsn, **kwargs)
>       conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.2), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:

request = <SubRequest '_django_db_helper' for <Coroutine test_presence_update_client_message>>
django_db_setup = None
django_db_blocker = <pytest_django.plugin.DjangoDbBlocker object at 0x771e3193e900>

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
/usr/local/lib/python3.12/site-packages/django/core/management/commands/flush.py:52: in handle
    sql_list = sql_flush(
/usr/local/lib/python3.12/site-packages/django/core/management/sql.py:11: in sql_flush
    tables = connection.introspection.django_table_names(
/usr/local/lib/python3.12/site-packages/django/db/backends/base/introspection.py:110: in django_table_names
    existing_tables = set(self.table_names(include_views=include_views))
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/introspection.py:56: in table_names
    with self.connection.cursor() as cursor:
         ^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:320: in cursor
    return self._cursor()
           ^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:296: in _cursor
    self.ensure_connection()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:311: in patched_ensure_connection
    real_ensure_connection(self, *args, **kwargs)
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:278: in ensure_connection
    with self.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:279: in ensure_connection
    self.connect()
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:256: in connect
    self.connection = self.get_new_connection(conn_params)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/postgresql/base.py:332: in get_new_connection
    connection = self.Database.connect(**conn_params)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

dsn = 'dbname=test_ziqreq_test client_encoding=UTF8 user=testuser password=testpass host=postgres port=5432'
connection_factory = None, cursor_factory = <class 'psycopg2.extensions.cursor'>
kwargs = {'client_encoding': 'UTF8', 'dbname': 'test_ziqreq_test', 'host': 'postgres', 'password': 'testpass', ...}
kwasync = {}

    def connect(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
        """
        Create a new database connection.
    
        The connection parameters can be specified as a string:
    
            conn = psycopg2.connect("dbname=test user=postgres password=secret")
    
        or using a set of keyword arguments:
    
            conn = psycopg2.connect(database="test", user="postgres", password="secret")
    
        Or as a mix of both. The basic connection parameters are:
    
        - *dbname*: the database name
        - *database*: the database name (only as keyword argument)
        - *user*: user name used to authenticate
        - *password*: password used to authenticate
        - *host*: database host address (defaults to UNIX socket if not provided)
        - *port*: connection port number (defaults to 5432 if not provided)
    
        Using the *connection_factory* parameter a different class or connections
        factory can be specified. It should be a callable object taking a dsn
        argument.
    
        Using the *cursor_factory* parameter, a new default cursor factory will be
        used by cursor().
    
        Using *async*=True an asynchronous connection will be created. *async_* is
        a valid alias (for Python versions where ``async`` is a keyword).
    
        Any other keyword parameter will be passed to the underlying client
        library: the list of supported parameters depends on the library version.
    
        """
        kwasync = {}
        if 'async' in kwargs:
            kwasync['async'] = kwargs.pop('async')
        if 'async_' in kwargs:
            kwasync['async_'] = kwargs.pop('async_')
    
        dsn = _ext.make_dsn(dsn, **kwargs)
>       conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.2), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
=================================== FAILURES ===================================
______________________ test_subscribe_idea_access_denied _______________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_subscribe_idea_access_denied():
        """T-6.1.05: Non-member cannot subscribe to idea group."""
        stranger = await _create_user(display_name="Stranger")
        owner, idea = await _setup_user_and_idea(user_kwargs={"display_name": "Owner"})
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={stranger.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:271: AssertionError
_________________ test_chat_message_broadcast_via_view_helper __________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_chat_message_broadcast_via_view_helper():
        """T-6.4.02: _broadcast_chat_message sends chat_message to idea group after REST POST."""
        user, idea = await _setup_user_and_idea()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:504: AssertionError
____________________ test_board_update_broadcast_source_ai _____________________

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_board_update_broadcast_source_ai():
        """T-3.6.02: board_update payload source is 'ai' when node created by AI."""
        user, idea = await _setup_user_and_idea()
        app = _make_application()
        communicator = WebsocketCommunicator(app, f"/ws/?token={user.id}")
    
        connected, _ = await communicator.connect()
>       assert connected is True
E       assert False is True

services/gateway/apps/websocket/tests/test_consumers.py:710: AssertionError
_____________________ test_presence_offline_on_unsubscribe _____________________

self = <channels.testing.websocket.WebsocketCommunicator object at 0x771e2bab6900>
timeout = 1

    async def receive_output(self, timeout=1):
        """
        Receives a single message from the application, with optional timeout.
        """
        # Make sure there's not an exception to raise from the task
        if self.future.done():
            self.future.result()
        # Wait and receive the message
        try:
            async with async_timeout(timeout):
>               return await self.output_queue.get()
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

/usr/local/lib/python3.12/site-packages/asgiref/testing.py:110: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <Queue at 0x771e2cfaf680 maxsize=0>

    async def get(self):
        """Remove and return an item from the queue.
    
        If queue is empty, wait until an item is available.
        """
        while self.empty():
            getter = self._get_loop().create_future()
            self._getters.append(getter)
            try:
>               await getter
E               asyncio.exceptions.CancelledError

/usr/local/lib/python3.12/asyncio/queues.py:158: CancelledError

During handling of the above exception, another exception occurred:

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_offline_on_unsubscribe():
        """T-6.3.03: Unsubscribe broadcasts offline presence for user."""
        owner, other, idea = await _setup_owner_collaborator_idea(
            owner_kwargs={"display_name": "Owner"},
            collab_kwargs={"display_name": "Observer"},
        )
        app = _make_application()
    
        comm_owner = WebsocketCommunicator(app, f"/ws/?token={owner.id}")
        comm_other = WebsocketCommunicator(app, f"/ws/?token={other.id}")
    
>       connected1, _ = await comm_owner.connect()
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^

services/gateway/apps/websocket/tests/test_consumers.py:1008: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/channels/testing/websocket.py:41: in connect
    response = await self.receive_output(timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/channels/testing/application.py:17: in receive_output
    return await super().receive_output(timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/asgiref/testing.py:121: in receive_output
    raise e
/usr/local/lib/python3.12/site-packages/asgiref/testing.py:109: in receive_output
    async with async_timeout(timeout):
               ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/asgiref/timeout.py:71: in __aexit__
    self._do_exit(exc_type)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <asgiref.timeout.timeout object at 0x771e2cfafc20>
exc_type = <class 'asyncio.exceptions.CancelledError'>

    def _do_exit(self, exc_type: Type[BaseException]) -> None:
        if exc_type is asyncio.CancelledError and self._cancelled:
            self._cancel_handler = None
            self._task = None
>           raise asyncio.TimeoutError
E           TimeoutError

/usr/local/lib/python3.12/site-packages/asgiref/timeout.py:108: TimeoutError
_____________________ test_presence_update_client_message ______________________

self = <DatabaseWrapper vendor='postgresql' alias='default'>

    @async_unsafe
    def ensure_connection(self):
        """Guarantee that a connection to the database is established."""
        if self.connection is None:
            if self.in_atomic_block and self.closed_in_transaction:
                raise ProgrammingError(
                    "Cannot open a new connection in an atomic block."
                )
            with self.wrap_database_errors:
>               self.connect()

/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:279: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:256: in connect
    self.connection = self.get_new_connection(conn_params)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/postgresql/base.py:332: in get_new_connection
    connection = self.Database.connect(**conn_params)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

dsn = 'dbname=test_ziqreq_test client_encoding=UTF8 user=testuser password=testpass host=postgres port=5432'
connection_factory = None, cursor_factory = <class 'psycopg2.extensions.cursor'>
kwargs = {'client_encoding': 'UTF8', 'dbname': 'test_ziqreq_test', 'host': 'postgres', 'password': 'testpass', ...}
kwasync = {}

    def connect(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
        """
        Create a new database connection.
    
        The connection parameters can be specified as a string:
    
            conn = psycopg2.connect("dbname=test user=postgres password=secret")
    
        or using a set of keyword arguments:
    
            conn = psycopg2.connect(database="test", user="postgres", password="secret")
    
        Or as a mix of both. The basic connection parameters are:
    
        - *dbname*: the database name
        - *database*: the database name (only as keyword argument)
        - *user*: user name used to authenticate
        - *password*: password used to authenticate
        - *host*: database host address (defaults to UNIX socket if not provided)
        - *port*: connection port number (defaults to 5432 if not provided)
    
        Using the *connection_factory* parameter a different class or connections
        factory can be specified. It should be a callable object taking a dsn
        argument.
    
        Using the *cursor_factory* parameter, a new default cursor factory will be
        used by cursor().
    
        Using *async*=True an asynchronous connection will be created. *async_* is
        a valid alias (for Python versions where ``async`` is a keyword).
    
        Any other keyword parameter will be passed to the underlying client
        library: the list of supported parameters depends on the library version.
    
        """
        kwasync = {}
        if 'async' in kwargs:
            kwasync['async'] = kwargs.pop('async')
        if 'async_' in kwargs:
            kwasync['async_'] = kwargs.pop('async_')
    
        dsn = _ext.make_dsn(dsn, **kwargs)
>       conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.2), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(DEBUG=True, AUTH_BYPASS=True)
    async def test_presence_update_client_message():
        """T-6.3.04: Client presence_update message broadcasts to idea group."""
>       owner, other, idea = await _setup_owner_collaborator_idea(
            owner_kwargs={"display_name": "Owner"},
            collab_kwargs={"display_name": "Observer"},
        )

services/gateway/apps/websocket/tests/test_consumers.py:1039: 
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
services/gateway/apps/websocket/tests/test_consumers.py:82: in _setup_owner_collaborator_idea
    owner = _make_user(**(owner_kwargs or {}))
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
services/gateway/apps/websocket/tests/test_consumers.py:49: in _make_user
    return User.objects.create(**defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
/usr/local/lib/python3.12/site-packages/django/db/models/sql/compiler.py:1880: in execute_sql
    with self.connection.cursor() as cursor:
         ^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:320: in cursor
    return self._cursor()
           ^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:296: in _cursor
    self.ensure_connection()
/usr/local/lib/python3.12/site-packages/django/test/testcases.py:311: in patched_ensure_connection
    real_ensure_connection(self, *args, **kwargs)
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:278: in ensure_connection
    with self.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/utils.py:91: in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:279: in ensure_connection
    self.connect()
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:256: in connect
    self.connection = self.get_new_connection(conn_params)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/postgresql/base.py:332: in get_new_connection
    connection = self.Database.connect(**conn_params)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

dsn = 'dbname=test_ziqreq_test client_encoding=UTF8 user=testuser password=testpass host=postgres port=5432'
connection_factory = None, cursor_factory = <class 'psycopg2.extensions.cursor'>
kwargs = {'client_encoding': 'UTF8', 'dbname': 'test_ziqreq_test', 'host': 'postgres', 'password': 'testpass', ...}
kwasync = {}

    def connect(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
        """
        Create a new database connection.
    
        The connection parameters can be specified as a string:
    
            conn = psycopg2.connect("dbname=test user=postgres password=secret")
    
        or using a set of keyword arguments:
    
            conn = psycopg2.connect(database="test", user="postgres", password="secret")
    
        Or as a mix of both. The basic connection parameters are:
    
        - *dbname*: the database name
        - *database*: the database name (only as keyword argument)
        - *user*: user name used to authenticate
        - *password*: password used to authenticate
        - *host*: database host address (defaults to UNIX socket if not provided)
        - *port*: connection port number (defaults to 5432 if not provided)
    
        Using the *connection_factory* parameter a different class or connections
        factory can be specified. It should be a callable object taking a dsn
        argument.
    
        Using the *cursor_factory* parameter, a new default cursor factory will be
        used by cursor().
    
        Using *async*=True an asynchronous connection will be created. *async_* is
        a valid alias (for Python versions where ``async`` is a keyword).
    
        Any other keyword parameter will be passed to the underlying client
        library: the list of supported parameters depends on the library version.
    
        """
        kwasync = {}
        if 'async' in kwargs:
            kwasync['async'] = kwargs.pop('async')
        if 'async_' in kwargs:
            kwasync['async_'] = kwargs.pop('async_')
    
        dsn = _ext.make_dsn(dsn, **kwargs)
>       conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.2), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
=============================== warnings summary ===============================
tests/test_smoke.py::test_smoke
  /app:0: PytestWarning: Error when trying to teardown test databases: ProgrammingError('database "test_ziqreq_test" does not exist\n')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_access_denied
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_via_view_helper
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_source_ai
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_offline_on_unsubscribe
FAILED services/gateway/apps/websocket/tests/test_consumers.py::test_presence_update_client_message
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_unknown_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_error_on_missing_message_type
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_subscribe_idea_as_owner
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_to_subscriber
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_chat_message_broadcast_via_view_helper
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_to_subscriber
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_not_received_by_unsubscribed
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_update_broadcast_source_ai
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_broadcast_excludes_sender
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_board_selection_deselect_null_node
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_presence_multi_tab_dedup
ERROR services/gateway/apps/websocket/tests/test_consumers.py::test_presence_update_client_message
============= 5 failed, 137 passed, 1 warning, 12 errors in 44.56s =============

```
