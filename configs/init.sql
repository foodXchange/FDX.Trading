-- FoodXchange Database Initialization Script
-- This script runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'supplier', 'buyer', 'analyst');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE import_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create base schema
CREATE SCHEMA IF NOT EXISTS foodxchange;

-- Set search path
SET search_path TO foodxchange, public;

-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'buyer',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS azure_service_health (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(500),
    status VARCHAR(50) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    status import_status DEFAULT 'pending',
    azure_job_id VARCHAR(255),
    result_data JSONB,
    error_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    supplier_id UUID REFERENCES users(id),
    description TEXT,
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    specifications JSONB,
    ai_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_import_jobs_user ON import_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_import_jobs_status ON import_jobs(status);
CREATE INDEX IF NOT EXISTS idx_azure_health_service ON azure_service_health(service_name, checked_at DESC);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_products_specs_gin ON products USING GIN (specifications);
CREATE INDEX IF NOT EXISTS idx_products_ai_gin ON products USING GIN (ai_analysis);

-- Create update trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to tables
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (email, username, password_hash, role)
VALUES ('admin@foodxchange.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQaXUIYJqgBy', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert sample data for testing
INSERT INTO users (email, username, password_hash, role)
VALUES 
    ('supplier1@example.com', 'supplier1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQaXUIYJqgBy', 'supplier'),
    ('buyer1@example.com', 'buyer1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQaXUIYJqgBy', 'buyer')
ON CONFLICT (email) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW v_recent_imports AS
SELECT 
    ij.id,
    ij.file_name,
    ij.status,
    ij.created_at,
    ij.completed_at,
    u.username,
    u.email
FROM import_jobs ij
JOIN users u ON ij.user_id = u.id
ORDER BY ij.created_at DESC
LIMIT 100;

CREATE OR REPLACE VIEW v_azure_health_summary AS
SELECT 
    service_name,
    COUNT(*) as total_checks,
    AVG(response_time_ms) as avg_response_time,
    SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) as healthy_count,
    MAX(checked_at) as last_checked
FROM azure_service_health
WHERE checked_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY service_name;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA foodxchange TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA foodxchange TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA foodxchange TO postgres;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'FoodXchange database initialized successfully!';
END $$;