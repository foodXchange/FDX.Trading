-- FoodXchange PostgreSQL Database Schema
-- Complete schema with all tables, indexes, and constraints

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Create custom types
CREATE TYPE company_type AS ENUM ('buyer', 'supplier', 'both');
CREATE TYPE company_size AS ENUM ('small', 'medium', 'large', 'enterprise');
CREATE TYPE order_status AS ENUM ('draft', 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'completed', 'cancelled', 'refunded');
CREATE TYPE payment_status AS ENUM ('pending', 'partial', 'paid', 'overdue', 'refunded');
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'cancelled', 'refunded');
CREATE TYPE payment_method AS ENUM ('wire_transfer', 'ach', 'check', 'credit_card', 'paypal', 'cash', 'credit_memo', 'other');
CREATE TYPE notification_type AS ENUM ('new_rfq', 'rfq_response', 'rfq_expired', 'new_quote', 'quote_accepted', 'quote_rejected', 'quote_expired', 'order_placed', 'order_confirmed', 'order_shipped', 'order_delivered', 'order_cancelled', 'payment_received', 'payment_overdue', 'invoice_generated', 'system_alert', 'price_alert', 'inventory_alert', 'new_message', 'document_shared', 'account_verified', 'password_reset', 'profile_update');
CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE communication_type AS ENUM ('email', 'phone', 'sms', 'meeting', 'video_call', 'chat', 'system', 'other');
CREATE TYPE communication_direction AS ENUM ('inbound', 'outbound', 'internal');

-- Companies table (central entity)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    registration_number VARCHAR(100) UNIQUE,
    company_type company_type DEFAULT 'buyer' NOT NULL,
    
    -- Contact information
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(255),
    
    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    
    -- Business details
    company_size company_size,
    year_established INTEGER,
    annual_revenue VARCHAR(50),
    description TEXT,
    industry VARCHAR(100),
    categories JSONB DEFAULT '[]',
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    verification_date TIMESTAMP,
    verification_documents JSONB DEFAULT '[]',
    
    -- Ratings
    rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    
    -- Financial
    payment_terms VARCHAR(100),
    credit_limit INTEGER, -- in cents
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Certifications
    certifications JSONB DEFAULT '[]',
    
    -- Preferences
    preferred_payment_methods JSONB DEFAULT '[]',
    delivery_preferences JSONB DEFAULT '{}',
    communication_preferences JSONB DEFAULT '{}',
    
    -- Integration
    external_id VARCHAR(100),
    integration_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    company VARCHAR(255), -- Legacy field
    role VARCHAR(50) DEFAULT 'buyer',
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Contacts table
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    department VARCHAR(100),
    
    -- Contact info
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    mobile VARCHAR(20),
    
    -- Permissions
    role VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    can_place_orders BOOLEAN DEFAULT FALSE,
    can_approve_quotes BOOLEAN DEFAULT FALSE,
    
    -- Preferences
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50),
    communication_preferences JSONB DEFAULT '{}',
    
    -- Additional
    notes TEXT,
    tags JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    last_contacted TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Suppliers table (legacy support + extended info)
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    
    -- Company info (legacy)
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(500),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    
    -- Business details
    categories JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending',
    rating FLOAT,
    response_rate FLOAT,
    average_response_time FLOAT,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Additional fields
    name VARCHAR(255), -- Alias
    specialties JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE NOT NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    
    -- Identification
    name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    sku VARCHAR(100),
    barcode VARCHAR(50),
    
    -- Details
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    
    -- Pricing
    price FLOAT,
    currency VARCHAR(3) DEFAULT 'USD',
    price_per VARCHAR(50),
    unit VARCHAR(50),
    
    -- Quantity
    moq FLOAT,
    quantity_available FLOAT,
    lead_time_days INTEGER,
    
    -- Specifications
    weight FLOAT,
    weight_unit VARCHAR(10) DEFAULT 'kg',
    dimensions VARCHAR(100),
    
    -- Certifications
    certifications JSONB DEFAULT '[]',
    is_organic BOOLEAN DEFAULT FALSE,
    is_halal BOOLEAN DEFAULT FALSE,
    is_kosher BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    
    -- Media
    image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    spec_sheet_url VARCHAR(500),
    
    -- Source
    source_url VARCHAR(500),
    language VARCHAR(10),
    confidence_score FLOAT,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    attributes JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_scraped TIMESTAMP
);

-- RFQs table
CREATE TABLE rfqs (
    id SERIAL PRIMARY KEY,
    rfq_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    assigned_contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    
    -- RFQ details
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity VARCHAR(100),
    delivery_date DATE,
    delivery_location VARCHAR(255),
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    requirements TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Quotes table
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    rfq_id INTEGER REFERENCES rfqs(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    
    -- Pricing
    price_per_unit DECIMAL(10,2),
    unit_price DECIMAL(10,2), -- Alias
    total_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Terms
    delivery_time VARCHAR(50),
    payment_terms VARCHAR(100),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    po_number VARCHAR(50),
    
    -- Parties
    buyer_company_id INTEGER REFERENCES companies(id) NOT NULL,
    supplier_company_id INTEGER REFERENCES companies(id) NOT NULL,
    buyer_contact_id INTEGER REFERENCES contacts(id),
    supplier_contact_id INTEGER REFERENCES contacts(id),
    
    -- References
    rfq_id INTEGER REFERENCES rfqs(id),
    quote_id INTEGER REFERENCES quotes(id),
    
    -- Status
    status order_status DEFAULT 'pending' NOT NULL,
    payment_status payment_status DEFAULT 'pending' NOT NULL,
    
    -- Amounts (in cents)
    subtotal INTEGER NOT NULL,
    tax_amount INTEGER DEFAULT 0,
    shipping_amount INTEGER DEFAULT 0,
    discount_amount INTEGER DEFAULT 0,
    total_amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    
    -- Payment
    payment_terms VARCHAR(200),
    payment_method VARCHAR(50),
    payment_due_date TIMESTAMP,
    
    -- Delivery
    delivery_date TIMESTAMP,
    requested_delivery_date TIMESTAMP,
    delivery_address TEXT,
    delivery_instructions TEXT,
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    
    -- Additional
    notes TEXT,
    internal_notes TEXT,
    special_requirements TEXT,
    documents JSONB DEFAULT '[]',
    
    -- Dates
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    confirmed_date TIMESTAMP,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP,
    completed_date TIMESTAMP,
    cancelled_date TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Order Items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    product_id INTEGER REFERENCES products(id),
    
    -- Product info
    product_name VARCHAR(200) NOT NULL,
    product_sku VARCHAR(100),
    product_description TEXT,
    
    -- Quantity and pricing
    quantity FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    unit_price INTEGER NOT NULL, -- in cents
    total_amount INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- References
    quote_item_id INTEGER,
    
    -- Specifications
    specifications JSONB DEFAULT '{}',
    
    -- Delivery
    requested_delivery_date TIMESTAMP,
    confirmed_delivery_date TIMESTAMP,
    
    -- Tracking
    quantity_shipped FLOAT DEFAULT 0,
    quantity_received FLOAT DEFAULT 0,
    quantity_invoiced FLOAT DEFAULT 0,
    
    -- Notes
    notes TEXT,
    supplier_notes TEXT,
    
    -- Quality
    quality_requirements TEXT,
    certifications_required JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Order Status History table
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    
    -- Status change
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    
    -- Change info
    changed_by_user_id INTEGER REFERENCES users(id),
    changed_by_name VARCHAR(200),
    changed_by_role VARCHAR(50),
    
    -- Details
    reason VARCHAR(200),
    notes TEXT,
    additional_data JSONB DEFAULT '{}',
    
    -- Tracking
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Invoices table
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- References
    order_id INTEGER REFERENCES orders(id) NOT NULL,
    buyer_company_id INTEGER REFERENCES companies(id) NOT NULL,
    supplier_company_id INTEGER REFERENCES companies(id) NOT NULL,
    
    -- Status
    status invoice_status DEFAULT 'draft' NOT NULL,
    
    -- Dates
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    due_date TIMESTAMP NOT NULL,
    
    -- Amounts (in cents)
    subtotal INTEGER NOT NULL,
    tax_amount INTEGER DEFAULT 0,
    tax_rate INTEGER, -- percentage * 100
    shipping_amount INTEGER DEFAULT 0,
    discount_amount INTEGER DEFAULT 0,
    total_amount INTEGER NOT NULL,
    amount_paid INTEGER DEFAULT 0,
    amount_due INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    
    -- Payment
    payment_terms VARCHAR(200),
    payment_instructions TEXT,
    
    -- Addresses
    bill_to_address TEXT,
    ship_to_address TEXT,
    
    -- Tax info
    buyer_tax_id VARCHAR(50),
    supplier_tax_id VARCHAR(50),
    
    -- Notes
    notes TEXT,
    internal_notes TEXT,
    
    -- Tracking
    sent_date TIMESTAMP,
    viewed_date TIMESTAMP,
    paid_date TIMESTAMP,
    
    -- Email
    sent_to_emails JSONB DEFAULT '[]',
    reminder_count INTEGER DEFAULT 0,
    last_reminder_date TIMESTAMP,
    
    -- Documents
    pdf_url VARCHAR(500),
    attachments JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Payments table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    reference_number VARCHAR(100),
    
    -- References
    invoice_id INTEGER REFERENCES invoices(id) NOT NULL,
    payer_company_id INTEGER REFERENCES companies(id) NOT NULL,
    payee_company_id INTEGER REFERENCES companies(id) NOT NULL,
    
    -- Payment details
    payment_method payment_method NOT NULL,
    status payment_status DEFAULT 'pending' NOT NULL,
    
    -- Amounts (in cents)
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    processing_fee INTEGER DEFAULT 0,
    net_amount INTEGER,
    
    -- Dates
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_date TIMESTAMP,
    cleared_date TIMESTAMP,
    
    -- Payment info
    account_last_four VARCHAR(4),
    routing_number_last_four VARCHAR(4),
    
    -- Processor
    processor VARCHAR(50),
    processor_transaction_id VARCHAR(255),
    processor_response JSONB DEFAULT '{}',
    
    -- Notes
    notes TEXT,
    internal_notes TEXT,
    
    -- Reconciliation
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciled_date TIMESTAMP,
    reconciled_by_user_id INTEGER REFERENCES users(id),
    
    -- Refunds
    is_refund BOOLEAN DEFAULT FALSE,
    original_payment_id INTEGER REFERENCES payments(id),
    refund_reason VARCHAR(200),
    
    -- Additional data
    additional_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Notification details
    type notification_type NOT NULL,
    priority notification_priority DEFAULT 'normal',
    
    -- Content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    action_url VARCHAR(500),
    action_text VARCHAR(100),
    
    -- References
    entity_type VARCHAR(50),
    entity_id INTEGER,
    
    -- Data
    additional_data JSONB DEFAULT '{}',
    channels JSONB DEFAULT '["in_app"]',
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Email tracking
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,
    email_opened BOOLEAN DEFAULT FALSE,
    email_opened_at TIMESTAMP,
    
    -- SMS tracking
    sms_sent BOOLEAN DEFAULT FALSE,
    sms_sent_at TIMESTAMP,
    
    -- Push tracking
    push_sent BOOLEAN DEFAULT FALSE,
    push_sent_at TIMESTAMP,
    
    -- Expiration
    expires_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Communication Logs table
CREATE TABLE communication_logs (
    id SERIAL PRIMARY KEY,
    
    -- Type
    type communication_type NOT NULL,
    direction communication_direction NOT NULL,
    
    -- Parties
    from_user_id INTEGER REFERENCES users(id),
    to_user_id INTEGER REFERENCES users(id),
    contact_id INTEGER REFERENCES contacts(id),
    company_id INTEGER REFERENCES companies(id),
    
    -- References
    entity_type VARCHAR(50),
    entity_id INTEGER,
    
    -- Content
    subject VARCHAR(500),
    content TEXT,
    summary TEXT,
    
    -- Email specific
    email_message_id VARCHAR(255),
    email_thread_id VARCHAR(255),
    
    -- Call/Meeting specific
    duration_seconds INTEGER,
    recording_url VARCHAR(500),
    participants JSONB DEFAULT '[]',
    
    -- Attachments
    attachments JSONB DEFAULT '[]',
    
    -- Outcome
    outcome VARCHAR(200),
    follow_up_required VARCHAR(200),
    follow_up_date TIMESTAMP,
    
    -- Analysis
    sentiment VARCHAR(50),
    key_points JSONB DEFAULT '[]',
    
    -- Additional data
    additional_data JSONB DEFAULT '{}',
    
    -- Timestamps
    communication_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Emails table (legacy + processing queue)
CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE,
    from_email VARCHAR(120) NOT NULL,
    sender_email VARCHAR(120) NOT NULL, -- Alias
    recipient_email VARCHAR(120),
    subject VARCHAR(500),
    body TEXT,
    email_type VARCHAR(50),
    classification VARCHAR(100),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    tasks_created JSONB DEFAULT '[]',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Activity Logs table
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    
    -- Action
    action VARCHAR(100) NOT NULL,
    description TEXT,
    details JSONB DEFAULT '{}',
    
    -- Entity reference
    entity_type VARCHAR(50),
    entity_id INTEGER,
    
    -- Result
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_companies_email ON companies(email);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_type ON companies(company_type);
CREATE INDEX idx_companies_country ON companies(country);
CREATE INDEX idx_companies_verified ON companies(is_verified) WHERE is_verified = TRUE;

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company ON users(company_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_primary ON contacts(company_id) WHERE is_primary = TRUE;

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_rfqs_number ON rfqs(rfq_number);
CREATE INDEX idx_rfqs_user ON rfqs(user_id);
CREATE INDEX idx_rfqs_company ON rfqs(company_id);
CREATE INDEX idx_rfqs_status ON rfqs(status);

CREATE INDEX idx_quotes_rfq ON quotes(rfq_id);
CREATE INDEX idx_quotes_supplier ON quotes(supplier_id);

CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_buyer ON orders(buyer_company_id);
CREATE INDEX idx_orders_supplier ON orders(supplier_company_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_date ON orders(order_date);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

CREATE INDEX idx_order_history_order ON order_status_history(order_id);
CREATE INDEX idx_order_history_date ON order_status_history(created_at);

CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_order ON invoices(order_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due ON invoices(due_date);

CREATE INDEX idx_payments_number ON payments(payment_number);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_date ON payments(payment_date);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_company ON notifications(company_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

CREATE INDEX idx_comm_logs_date ON communication_logs(communication_date);
CREATE INDEX idx_comm_logs_contact ON communication_logs(contact_id);
CREATE INDEX idx_comm_logs_company ON communication_logs(company_id);

CREATE INDEX idx_activity_action ON activity_logs(action);
CREATE INDEX idx_activity_date ON activity_logs(created_at);
CREATE INDEX idx_activity_user ON activity_logs(user_id);
CREATE INDEX idx_activity_company ON activity_logs(company_id);

-- Full-text search indexes
CREATE INDEX idx_products_search ON products USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_companies_search ON companies USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- JSONB indexes for common queries
CREATE INDEX idx_companies_categories ON companies USING gin(categories);
CREATE INDEX idx_companies_certifications ON companies USING gin(certifications);
CREATE INDEX idx_products_certifications ON products USING gin(certifications);
CREATE INDEX idx_products_tags ON products USING gin(tags);

-- Add triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rfqs_updated_at BEFORE UPDATE ON rfqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_items_updated_at BEFORE UPDATE ON order_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO foodxchange_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO foodxchange_app;