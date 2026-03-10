"""Root conftest for gateway tests.

Provides persistent test DB setup (keepdb=True) and serialized_rollback
to prevent django_content_type duplicate key IntegrityError that occurs
when async transactional tests flush and re-insert content types on PostgreSQL.
"""

import pytest
from django.test.utils import setup_databases


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Use persistent test database — skip create/destroy cycle.

    The test database is pre-created by docker compose. Using keepdb=True
    prevents unnecessary DB creation/destruction between test runs.
    """
    with django_db_blocker.unblock():
        setup_databases(
            verbosity=0,
            interactive=False,
            keepdb=True,
        )
    yield
    # Don't tear down — DB persists across runs (keepdb mode)


@pytest.fixture(autouse=True)
def django_db_serialized_rollback():
    """Enable serialized_rollback for all transactional tests.

    When pytest-django sees this fixture name in fixturenames, it sets
    serialized_rollback=True on TransactionTestCase. This causes Django
    to inhibit the post_migrate signal during fixture teardown flush,
    preventing the django_content_type duplicate key IntegrityError.
    """
