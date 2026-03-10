-- Create the test database that Django/pytest-django expects.
-- This avoids the fragile CREATE/DROP DATABASE lifecycle within
-- the test runner that breaks under async TransactionTestCase.
SELECT 'CREATE DATABASE test_ziqreq_test OWNER testuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test_ziqreq_test')\gexec
