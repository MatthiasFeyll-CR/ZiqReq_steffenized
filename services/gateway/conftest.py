"""Root conftest for gateway tests.

Provides serialized_rollback to prevent auth_permission / django_content_type
duplicate key IntegrityError that occurs when async transactional tests flush
and re-insert content types on PostgreSQL.

NOTE: We intentionally do NOT override django_db_setup here. The default
pytest-django fixture creates the test DB fresh (with keepdb=False), runs
migrations, and — crucially — serializes the initial DB state. This
serialization is required for serialized_rollback=True to work; with
keepdb=True the serialization step is skipped, making rollback a no-op.
"""

import pytest


@pytest.fixture(autouse=True)
def django_db_serialized_rollback():
    """Enable serialized_rollback for all transactional tests.

    When pytest-django sees this fixture name in fixturenames, it sets
    serialized_rollback=True on TransactionTestCase. This causes Django
    to restore the serialized DB state after each test instead of flushing
    and re-inserting, preventing duplicate key IntegrityError on
    auth_permission and django_content_type tables.
    """
