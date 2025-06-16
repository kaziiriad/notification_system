-- Initialize the notification_system database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if it doesn't exist (this might not work in init script, but good to have)
-- CREATE DATABASE notification_system;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (these will be created by Alembic migrations)
-- But we can add some basic ones here

-- Grant permissions to the postgres user
CREATE DATABASE notification_system IF NOT EXISTS;
CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE DATABASE notification_system OWNER myuser;
-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE notification_system TO myuser;


-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Database notification_system initialized successfully';
END $$;