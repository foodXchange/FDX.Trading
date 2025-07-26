-- Create least-privilege application user for FoodXchange
-- Run this script as the admin user (foodxchangedbadmin)

-- Create the application user
CREATE USER appuser WITH PASSWORD 'FoodX2024AppUser!';

-- Grant database connection
GRANT CONNECT ON DATABASE foodxchange TO appuser;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO appuser;

-- Grant table permissions (for existing tables)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO appuser;

-- Grant sequence permissions (for auto-increment columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- Grant permissions for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO appuser;

-- Verify permissions
\du appuser

-- Test the permissions (optional)
-- SET ROLE appuser;
-- SELECT current_user;
-- RESET ROLE;