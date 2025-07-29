-- FoodXchange Sourcing Module - Database Schema
-- Lean schema focused on sourcing functionality

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Create custom types
CREATE TYPE user_role AS ENUM ('buyer', 'supplier', 'admin');
CREATE TYPE rfq_status AS ENUM ('draft', 'active', 'closed', 'awarded');
CREATE TYPE quote_status AS ENUM ('pending', 'submitted', 'accepted', 'rejected');
CREATE TYPE order_status AS ENUM ('draft', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled');
CREATE TYPE analysis_type AS ENUM ('image', 'text', 'hybrid');
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'buyer',
    company_name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Suppliers table
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(255),
    address TEXT,
    country VARCHAR(100),
    description TEXT,
    categories TEXT[], -- Array of product categories
    certifications TEXT[], -- Array of certifications
    rating DECIMAL(3,2) DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5.0),
    total_reviews INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit VARCHAR(50), -- kg, lbs, pieces, etc.
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    min_order_quantity INTEGER,
    available_quantity INTEGER,
    certifications TEXT[],
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- RFQs table (Request for Quotes)
CREATE TABLE rfqs (
    id SERIAL PRIMARY KEY,
    rfq_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirements TEXT,
    category VARCHAR(100),
    quantity INTEGER,
    unit VARCHAR(50),
    delivery_date DATE,
    status rfq_status DEFAULT 'draft',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Quotes table
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    rfq_id INTEGER REFERENCES rfqs(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    quantity INTEGER,
    unit VARCHAR(50),
    delivery_time_days INTEGER,
    terms_conditions TEXT,
    status quote_status DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    quote_id INTEGER REFERENCES quotes(id) ON DELETE SET NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status order_status DEFAULT 'draft',
    delivery_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50), -- 'new_rfq', 'quote_received', 'order_status', etc.
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- AI Product Analysis table
CREATE TABLE product_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    analysis_type analysis_type NOT NULL,
    input_data TEXT NOT NULL, -- image URL or search text
    ai_analysis JSONB, -- Azure AI analysis results
    product_name VARCHAR(255),
    product_category VARCHAR(100),
    confidence_score DECIMAL(3,2),
    status analysis_status DEFAULT 'pending',
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Product Briefs table
CREATE TABLE product_briefs (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES product_analyses(id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    specifications JSONB, -- Product specifications
    packaging_options JSONB, -- Available packaging sizes
    quality_standards JSONB, -- Quality requirements
    target_market TEXT,
    estimated_price_range JSONB, -- Min/max price estimates
    supplier_recommendations JSONB, -- Suggested suppliers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Product Images table
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES product_analyses(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    image_type VARCHAR(50), -- 'uploaded', 'reference', 'sample'
    file_size INTEGER,
    mime_type VARCHAR(100),
    azure_blob_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- AI Insights table
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES product_analyses(id) ON DELETE CASCADE,
    insight_type VARCHAR(100), -- 'market_trend', 'pricing_analysis', 'supplier_match'
    insight_data JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_suppliers_email ON suppliers(email);
CREATE INDEX idx_suppliers_categories ON suppliers USING gin(categories);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_search ON products USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_rfqs_user ON rfqs(user_id);
CREATE INDEX idx_rfqs_status ON rfqs(status);
CREATE INDEX idx_rfqs_number ON rfqs(rfq_number);
CREATE INDEX idx_quotes_rfq ON quotes(rfq_id);
CREATE INDEX idx_quotes_supplier ON quotes(supplier_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_supplier ON orders(supplier_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- AI Analysis indexes
CREATE INDEX idx_product_analyses_user ON product_analyses(user_id);
CREATE INDEX idx_product_analyses_type ON product_analyses(analysis_type);
CREATE INDEX idx_product_analyses_status ON product_analyses(status);
CREATE INDEX idx_product_analyses_category ON product_analyses(product_category);
CREATE INDEX idx_product_briefs_analysis ON product_briefs(analysis_id);
CREATE INDEX idx_product_briefs_category ON product_briefs(category);
CREATE INDEX idx_product_images_analysis ON product_images(analysis_id);
CREATE INDEX idx_ai_insights_analysis ON ai_insights(analysis_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rfqs_updated_at BEFORE UPDATE ON rfqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_analyses_updated_at BEFORE UPDATE ON product_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_briefs_updated_at BEFORE UPDATE ON product_briefs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO users (name, email, hashed_password, role, company_name) VALUES
('Admin User', 'admin@foodxchange.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'admin', 'FoodXchange Admin'),
('Test Buyer', 'buyer@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'buyer', 'Test Buyer Company'),
('Test Supplier', 'supplier@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'supplier', 'Test Supplier Company');

-- Insert sample suppliers
INSERT INTO suppliers (name, email, phone, website, country, description, categories, rating) VALUES
('Fresh Foods Co', 'contact@freshfoods.com', '+1-555-0101', 'https://freshfoods.com', 'USA', 'Premium fresh produce supplier', ARRAY['vegetables', 'fruits'], 4.5),
('Organic Farms Ltd', 'sales@organicfarms.com', '+1-555-0102', 'https://organicfarms.com', 'Canada', 'Certified organic produce', ARRAY['organic', 'vegetables'], 4.8),
('Global Seafood', 'info@globalseafood.com', '+1-555-0103', 'https://globalseafood.com', 'Norway', 'Premium seafood supplier', ARRAY['seafood', 'fish'], 4.2);

-- Insert sample products
INSERT INTO products (supplier_id, name, description, category, unit, price, min_order_quantity, available_quantity) VALUES
(1, 'Fresh Tomatoes', 'Premium vine-ripened tomatoes', 'vegetables', 'kg', 2.50, 10, 1000),
(1, 'Organic Carrots', 'Fresh organic carrots', 'vegetables', 'kg', 1.80, 5, 500),
(2, 'Organic Spinach', 'Certified organic spinach', 'organic', 'kg', 3.20, 5, 300),
(3, 'Atlantic Salmon', 'Fresh Atlantic salmon fillets', 'seafood', 'kg', 12.00, 5, 200);