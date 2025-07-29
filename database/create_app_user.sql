-- FoodXchange Sourcing Module - Database User Setup
-- Create application user for the sourcing module

-- Create the application user
CREATE USER foodxchange_app WITH PASSWORD 'FoodX2024Sourcing!';

-- Grant database connection
GRANT CONNECT ON DATABASE foodxchange TO foodxchange_app;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO foodxchange_app;

-- Grant table permissions (for existing tables)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO foodxchange_app;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO foodxchange_app;

-- Grant sequence permissions (for auto-increment columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO foodxchange_app;

-- Grant permissions for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO foodxchange_app;

-- Verify the user was created
\du foodxchange_app