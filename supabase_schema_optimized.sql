-- FoodXchange Optimized Database Schema for Supabase
-- Enhanced with better structure, relationships, and performance optimizations

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For GIN indexes

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table (Enhanced)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'buyer', 'supplier', 'user')),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies table (Enhanced)
CREATE TABLE IF NOT EXISTS companies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    registration_number VARCHAR(100) UNIQUE,
    company_type VARCHAR(20) NOT NULL CHECK (company_type IN ('buyer', 'supplier', 'both')),
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(255),
    logo_url TEXT,
    
    -- Address fields
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    
    -- Business details
    company_size VARCHAR(20) CHECK (company_size IN ('startup', 'small', 'medium', 'large', 'enterprise')),
    year_established INTEGER CHECK (year_established > 1800 AND year_established <= EXTRACT(YEAR FROM NOW())),
    annual_revenue VARCHAR(50),
    description TEXT,
    industry VARCHAR(100),
    
    -- Categories and preferences
    categories JSONB DEFAULT '[]'::jsonb,
    certifications JSONB DEFAULT '[]'::jsonb,
    payment_terms VARCHAR(100),
    credit_limit DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status and verification
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    verification_date TIMESTAMP WITH TIME ZONE,
    verification_documents JSONB DEFAULT '[]'::jsonb,
    
    -- Ratings and reviews
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    
    -- Integration
    external_id VARCHAR(100),
    integration_data JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Suppliers table (Enhanced)
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    website VARCHAR(255),
    logo_url TEXT,
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    
    -- Business details
    description TEXT,
    products TEXT,
    certifications TEXT,
    specialties JSONB DEFAULT '[]'::jsonb,
    
    -- Status and ratings
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    
    -- Business metrics
    response_time_hours INTEGER,
    fulfillment_rate DECIMAL(5,2),
    average_rating DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PRODUCT CATALOG
-- ============================================================================

-- Product Categories
CREATE TABLE IF NOT EXISTS product_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table (Enhanced)
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    category_id UUID REFERENCES product_categories(id),
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    barcode VARCHAR(100),
    
    -- Pricing
    base_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    unit VARCHAR(50) NOT NULL,
    min_order_quantity DECIMAL(10,2) DEFAULT 1,
    max_order_quantity DECIMAL(10,2),
    
    -- Inventory
    stock_quantity DECIMAL(10,2),
    reorder_level DECIMAL(10,2),
    lead_time_days INTEGER,
    
    -- Product details
    weight_kg DECIMAL(8,3),
    dimensions JSONB, -- {length, width, height, unit}
    specifications JSONB,
    images JSONB DEFAULT '[]'::jsonb,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- RFQ & QUOTING SYSTEM
-- ============================================================================

-- RFQs table (Enhanced)
CREATE TABLE IF NOT EXISTS rfqs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    title VARCHAR(200) NOT NULL,
    description TEXT,
    requirements TEXT,
    
    -- Status and timeline
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'closed', 'awarded', 'cancelled')),
    deadline DATE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    
    -- Budget and terms
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms VARCHAR(100),
    delivery_requirements TEXT,
    
    -- Categories and preferences
    categories JSONB DEFAULT '[]'::jsonb,
    preferred_suppliers JSONB DEFAULT '[]'::jsonb,
    
    -- Metrics
    total_quotes INTEGER DEFAULT 0,
    average_quote_amount DECIMAL(12,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RFQ Items (for detailed requirements)
CREATE TABLE IF NOT EXISTS rfq_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),
    specifications JSONB,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quotes table (Enhanced)
CREATE TABLE IF NOT EXISTS quotes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Quote details
    title VARCHAR(200),
    description TEXT,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status and timeline
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'accepted', 'rejected', 'expired')),
    valid_until DATE,
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    -- Terms
    payment_terms VARCHAR(100),
    delivery_terms TEXT,
    warranty_terms TEXT,
    
    -- Notes
    internal_notes TEXT,
    supplier_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quote Items
CREATE TABLE IF NOT EXISTS quote_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    rfq_item_id UUID REFERENCES rfq_items(id),
    product_id UUID REFERENCES products(id),
    
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    
    -- Delivery
    delivery_time_days INTEGER,
    minimum_order_quantity DECIMAL(10,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ORDER MANAGEMENT
-- ============================================================================

-- Orders table (Enhanced)
CREATE TABLE IF NOT EXISTS orders (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    quote_id UUID REFERENCES quotes(id),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Order details
    order_number VARCHAR(50) UNIQUE,
    title VARCHAR(200),
    description TEXT,
    
    -- Financial
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    shipping_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status and timeline
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    order_date DATE DEFAULT CURRENT_DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    
    -- Shipping
    shipping_address JSONB,
    billing_address JSONB,
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    
    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'partial', 'paid', 'overdue')),
    payment_method VARCHAR(100),
    payment_terms VARCHAR(100),
    
    -- Notes
    internal_notes TEXT,
    customer_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    quote_item_id UUID REFERENCES quote_items(id),
    product_id UUID REFERENCES products(id),
    
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- NOTIFICATIONS & COMMUNICATIONS
-- ============================================================================

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('info', 'success', 'warning', 'error', 'rfq', 'quote', 'order')),
    
    -- Reference to related entity
    entity_type VARCHAR(50), -- 'rfq', 'quote', 'order', etc.
    entity_id UUID,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company);

-- Company indexes
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_type ON companies(company_type);
CREATE INDEX IF NOT EXISTS idx_companies_country ON companies(country);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);
CREATE INDEX IF NOT EXISTS idx_companies_rating ON companies(rating);
CREATE INDEX IF NOT EXISTS idx_companies_categories ON companies USING GIN (categories);

-- Supplier indexes
CREATE INDEX IF NOT EXISTS idx_suppliers_company_id ON suppliers(company_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_status ON suppliers(status);
CREATE INDEX IF NOT EXISTS idx_suppliers_country ON suppliers(country);
CREATE INDEX IF NOT EXISTS idx_suppliers_rating ON suppliers(rating);

-- Product indexes
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(base_price);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- RFQ indexes
CREATE INDEX IF NOT EXISTS idx_rfqs_company_id ON rfqs(company_id);
CREATE INDEX IF NOT EXISTS idx_rfqs_status ON rfqs(status);
CREATE INDEX IF NOT EXISTS idx_rfqs_deadline ON rfqs(deadline);
CREATE INDEX IF NOT EXISTS idx_rfqs_created_at ON rfqs(created_at);
CREATE INDEX IF NOT EXISTS idx_rfqs_categories ON rfqs USING GIN (categories);

-- Quote indexes
CREATE INDEX IF NOT EXISTS idx_quotes_rfq_id ON quotes(rfq_id);
CREATE INDEX IF NOT EXISTS idx_quotes_supplier_id ON quotes(supplier_id);
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);
CREATE INDEX IF NOT EXISTS idx_quotes_amount ON quotes(total_amount);

-- Order indexes
CREATE INDEX IF NOT EXISTS idx_orders_company_id ON orders(company_id);
CREATE INDEX IF NOT EXISTS idx_orders_supplier_id ON orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rfqs_updated_at BEFORE UPDATE ON rfqs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE rfqs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rfq_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quote_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SAMPLE DATA INSERTS
-- ============================================================================

-- Insert sample product categories
INSERT INTO product_categories (name, description, sort_order) VALUES
('Fresh Produce', 'Fresh fruits and vegetables', 1),
('Meat & Poultry', 'Fresh and frozen meat products', 2),
('Dairy & Eggs', 'Milk, cheese, eggs and dairy products', 3),
('Grains & Cereals', 'Rice, wheat, oats and other grains', 4),
('Beverages', 'Juices, soft drinks, and other beverages', 5),
('Snacks & Confectionery', 'Chips, candies, and snack foods', 6)
ON CONFLICT DO NOTHING; 