-- FoodXchange Azure PostgreSQL Setup Script
-- Run this script as the admin user to set up the database

-- Create the application user with limited privileges
CREATE USER foodxchange_app WITH PASSWORD 'Ud30078123';

-- Grant connection privilege to the database
GRANT CONNECT ON DATABASE foodxchange_db TO foodxchange_app;

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO foodxchange_app;

-- Grant permissions on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO foodxchange_app;

-- Grant permissions on sequences (for auto-increment fields)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO foodxchange_app;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO foodxchange_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO foodxchange_app;

-- Create the tables (if they don't exist)
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    country VARCHAR(100),
    products TEXT,
    certifications TEXT,
    status VARCHAR(50) DEFAULT 'active',
    rating FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RFQs table
CREATE TABLE IF NOT EXISTS rfqs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    product VARCHAR(200) NOT NULL,
    quantity FLOAT NOT NULL,
    unit VARCHAR(50),
    delivery_date DATE,
    delivery_location VARCHAR(200),
    requirements TEXT,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quotes table
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    rfq_id INTEGER REFERENCES rfqs(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    price_per_unit DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    delivery_time VARCHAR(100),
    payment_terms VARCHAR(200),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emails table
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    sender_email VARCHAR(120) NOT NULL,
    recipient_email VARCHAR(120),
    subject VARCHAR(500),
    body TEXT,
    email_type VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    metadata JSONB,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_rfqs_user_id ON rfqs(user_id);
CREATE INDEX IF NOT EXISTS idx_rfqs_status ON rfqs(status);
CREATE INDEX IF NOT EXISTS idx_quotes_rfq_id ON quotes(rfq_id);
CREATE INDEX IF NOT EXISTS idx_quotes_supplier_id ON quotes(supplier_id);
CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender_email);
CREATE INDEX IF NOT EXISTS idx_emails_processed ON emails(processed);

-- Grant permissions on the newly created tables
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO foodxchange_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON suppliers TO foodxchange_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON rfqs TO foodxchange_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON quotes TO foodxchange_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON emails TO foodxchange_app;

-- Grant permissions on sequences for the new tables
GRANT USAGE, SELECT ON users_id_seq TO foodxchange_app;
GRANT USAGE, SELECT ON suppliers_id_seq TO foodxchange_app;
GRANT USAGE, SELECT ON rfqs_id_seq TO foodxchange_app;
GRANT USAGE, SELECT ON quotes_id_seq TO foodxchange_app;
GRANT USAGE, SELECT ON emails_id_seq TO foodxchange_app;

-- Verify the setup
SELECT 
    'User created successfully' AS status,
    usename AS username,
    usesuper AS is_superuser,
    usecreatedb AS can_create_db
FROM pg_user 
WHERE usename = 'foodxchange_app';

-- List granted permissions
SELECT 
    'Table permissions' AS permission_type,
    tablename,
    string_agg(privilege_type, ', ') AS privileges
FROM information_schema.table_privileges
WHERE grantee = 'foodxchange_app' 
    AND table_schema = 'public'
GROUP BY tablename
ORDER BY tablename;