-- ============================================================
-- JEET DATABASE — EXTENSIONS
-- ============================================================
-- PostgreSQL extensions enable advanced features beyond the
-- default install. We use these in production.
-- ============================================================

-- uuid-ossp: Generate UUIDs (the unguessable IDs we use everywhere)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgcrypto: Password hashing and crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- pg_trgm: Fuzzy text search (for searching students by partial name)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- citext: Case-insensitive text (emails like Foo@x.com == foo@x.com)
CREATE EXTENSION IF NOT EXISTS "citext";