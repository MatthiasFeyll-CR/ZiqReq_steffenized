# Test Results: pre-QA M1 cycle 0
Date: 2026-03-09T19:54:47+0100
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
collected 14 items

services/gateway/apps/authentication/tests/test_azure_ad.py ......       [ 42%]
services/gateway/apps/authentication/tests/test_dev_bypass.py EEEEEEE    [ 92%]
tests/test_smoke.py .                                                    [100%]

==================================== ERRORS ====================================
____ ERROR at setup of TestDevBypass.test_dev_login_404_without_auth_bypass ____

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
________ ERROR at setup of TestDevBypass.test_dev_login_creates_session ________

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
_ ERROR at setup of TestDevBypass.test_dev_login_nonexistent_user_returns_404 __

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
______ ERROR at setup of TestDevBypass.test_dev_switch_404_without_debug _______

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
____________ ERROR at setup of TestDevBypass.test_dev_switch_works _____________

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
__ ERROR at setup of TestDevBypass.test_dev_users_endpoint_404_in_production ___

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
____ ERROR at setup of TestDevBypass.test_dev_users_endpoint_in_bypass_mode ____

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
E       psycopg2.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError

The above exception was the direct cause of the following exception:
/usr/local/lib/python3.12/site-packages/django/db/transaction.py:198: in __enter__
    if not connection.get_autocommit():
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.12/site-packages/django/db/backends/base/base.py:454: in get_autocommit
    self.ensure_connection()
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
E       django.db.utils.OperationalError: connection to server at "postgres" (10.10.8.3), port 5432 failed: FATAL:  database "test_ziqreq_test" does not exist
E       DETAIL:  It seems to have just been dropped or renamed.

/usr/local/lib/python3.12/site-packages/psycopg2/__init__.py:122: OperationalError
=============================== warnings summary ===============================
tests/test_smoke.py::test_smoke
  /app:0: PytestWarning: Error when trying to teardown test databases: ProgrammingError('database "test_ziqreq_test" does not exist\n')

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_404_without_auth_bypass
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_creates_session
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_login_nonexistent_user_returns_404
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_switch_404_without_debug
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_switch_works
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_users_endpoint_404_in_production
ERROR services/gateway/apps/authentication/tests/test_dev_bypass.py::TestDevBypass::test_dev_users_endpoint_in_bypass_mode
==================== 7 passed, 1 warning, 7 errors in 2.12s ====================

```
