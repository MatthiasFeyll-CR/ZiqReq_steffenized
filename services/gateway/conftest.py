"""Root conftest for gateway tests.

Fixes the async TransactionTestCase + PostgreSQL + Docker lifecycle issue:

1. The test DB ``test_ziqreq_test`` is pre-created by Docker's init script
   (infra/docker/init-test-db.sql) so we never rely on Django's fragile
   CREATE/DROP DATABASE dance that breaks under async fixture finalization.

2. ``django_db_setup`` uses ``keepdb=True`` to skip DB creation/destruction,
   then **manually serializes** the DB state so ``serialized_rollback`` has
   data to restore from (``keepdb=True`` normally skips this step).

3. Teardown is intentionally skipped — Docker manages the DB lifecycle.

See docs/08-qa/qa-m6-websocket.md for the 3-cycle bugfix history.
"""

import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Create test DB with keepdb + manual serialization.

    * ``keepdb=True`` connects to the pre-existing ``test_ziqreq_test``
      database (created by Docker init script) and runs any outstanding
      migrations.  It never issues CREATE/DROP DATABASE, side-stepping
      the OperationalError that killed cycle 3.
    * After migrations, we manually call ``serialize_db_to_string()`` and
      store the result on ``connection._test_serialized_contents``.  This
      is the attribute that Django's ``TransactionTestCase._fixture_teardown``
      checks when ``serialized_rollback=True``; without it the rollback is
      a no-op (the bug in cycle 1–2).
    * We intentionally skip ``teardown_databases`` — Docker is ephemeral.
    """
    from django.db import connections
    from django.test.utils import setup_databases

    with django_db_blocker.unblock():
        setup_databases(
            verbosity=0,
            interactive=False,
            keepdb=True,
        )
        # keepdb=True skips the serialization step.  Do it ourselves so
        # serialized_rollback can flush-then-restore after each
        # TransactionTestCase.
        for alias in connections:
            conn = connections[alias]
            if conn.vendor != "dummy":
                conn._test_serialized_contents = (
                    conn.creation.serialize_db_to_string()
                )

    yield
    # No teardown — Docker manages the DB lifecycle.


@pytest.fixture(autouse=True)
def django_db_serialized_rollback():
    """Enable serialized_rollback for all transactional tests.

    When pytest-django sees this fixture name in fixturenames, it sets
    serialized_rollback=True on TransactionTestCase. This causes Django
    to restore the serialized DB state after each test instead of flushing
    and re-inserting, preventing duplicate key IntegrityError on
    auth_permission and django_content_type tables.
    """
