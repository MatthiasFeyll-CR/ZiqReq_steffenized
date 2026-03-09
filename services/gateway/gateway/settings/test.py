import os
from urllib.parse import urlparse

from .base import *  # noqa: F401, F403

DEBUG = True
AUTH_BYPASS = True

_db_url = os.environ.get("DATABASE_URL", "")
if _db_url:
    _parsed = urlparse(_db_url)
    _db_name = (_parsed.path or "/ziqreq_test").lstrip("/")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": _parsed.username or "testuser",
            "PASSWORD": _parsed.password or "testpass",
            "HOST": _parsed.hostname or "localhost",
            "PORT": str(_parsed.port or 5432),
            "TEST": {
                "NAME": _db_name,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
