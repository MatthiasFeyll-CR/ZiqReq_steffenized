"""Root conftest for gateway tests.

Fixes the async TransactionTestCase + PostgreSQL + Docker lifecycle issue:

1. The test DB ``test_ziqreq_test`` is pre-created by Docker's init script
   (infra/docker/init-test-db.sql) so we never rely on Django's fragile
   CREATE/DROP DATABASE dance that breaks under async fixture finalization.

2. ``django_db_setup`` uses ``keepdb=True`` to skip DB creation/destruction
   and disconnects ``create_contenttypes`` / ``create_permissions`` from
   ``post_migrate`` to prevent duplicate-key IntegrityErrors (DEF-002).

3. Teardown is intentionally skipped — Docker manages the DB lifecycle.

See docs/08-qa/qa-m6-websocket.md for the bugfix history.
"""

import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Create test DB with keepdb=True, silencing post_migrate handlers.

    * Disconnects ``create_contenttypes`` and ``create_permissions`` from
      the ``post_migrate`` signal **before** running migrations.  On
      PostgreSQL with Django 5.2 and ``keepdb=True``, these handlers use
      ``bulk_create`` without ``ignore_conflicts``, causing duplicate-key
      IntegrityErrors when content-type / permission rows already exist
      in the persistent test DB (DEF-002).
    * ``keepdb=True`` connects to the pre-existing ``test_ziqreq_test``
      database (created by Docker init script) and runs any outstanding
      migrations.  It never issues CREATE/DROP DATABASE.
    * The signal handlers stay disconnected for the entire test session so
      that ``TransactionTestCase._fixture_teardown`` (flush →
      ``emit_post_migrate_signal``) also doesn't trigger them.
    * We intentionally skip ``teardown_databases`` — Docker is ephemeral.
    """
    from django.contrib.auth.management import create_permissions
    from django.contrib.contenttypes.management import create_contenttypes
    from django.db.models.signals import post_migrate
    from django.test.utils import setup_databases

    post_migrate.disconnect(create_contenttypes)
    post_migrate.disconnect(
        dispatch_uid="django.contrib.auth.management.create_permissions",
    )

    with django_db_blocker.unblock():
        setup_databases(
            verbosity=0,
            interactive=False,
            keepdb=True,
        )

    yield
    # No teardown — Docker manages the DB lifecycle.
    # Reconnect handlers for completeness (session is ending anyway).
    post_migrate.connect(create_contenttypes)
    post_migrate.connect(
        create_permissions,
        dispatch_uid="django.contrib.auth.management.create_permissions",
    )


@pytest.fixture(autouse=True)
def _close_db_connections():
    """Close all DB connections before and after each test when safe to do so.

    Prevents stale thread-local connections from carrying over between
    async TransactionTestCase tests that each get their own event loop.
    Without this, @database_sync_to_async calls in the WebSocket
    middleware may use a connection that sees a different DB state
    than the test's data-creation calls (DEF-003).

    Skips closing when the default connection is inside an atomic block
    (i.e., regular TestCase tests that wrap each test in a transaction).
    """
    from django.db import connection, connections

    if not connection.in_atomic_block:
        connections.close_all()
    yield
    if not connection.in_atomic_block:
        connections.close_all()
        if connection.connection is not None:
            connection.connection.close()
            connection.connection = None
