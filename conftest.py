"""Root pytest config: collect_ignore_glob + django_db_setup override."""

import pytest

collect_ignore_glob = [
    "services/*/apps/*/migrations/*",
    "frontend/*",
    "e2e/*",
    "node_modules/*",
]


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Use pre-existing Docker DB with migrations, skip create/destroy cycle."""
    with django_db_blocker.unblock():
        from django.core.management import call_command

        call_command("migrate", "--run-syncdb", verbosity=0)
