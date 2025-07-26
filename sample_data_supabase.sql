-- Sample Data for FoodXchange
-- This creates test data for your Supabase database

-- Sample Users
INSERT INTO users (name, email, hashed_password, company, role, is_active, is_admin) VALUES
('Admin User', 'admin@foodxchange.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'FoodXchange Inc', 'admin', true, true),
('John Buyer', 'john@buyer.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'Buyer Corp', 'buyer', true, false),
('Sarah Supplier', 'sarah@supplier.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'Supplier Co', 'supplier', true, false);

-- Sample Companies
INSERT INTO companies (name, legal_name, registration_number, company_type, email, phone, country, is_active) VALUES
('FoodXchange Inc', 'FoodXchange Incorporated', 'FX001', 'buyer', 'info@foodxchange.com', '+1-555-0123', 'USA', true),
('Buyer Corp', 'Buyer Corporation', 'BC001', 'buyer', 'info@buyercorp.com', '+1-555-0124', 'USA', true),
('Supplier Co', 'Supplier Company', 'SC001', 'supplier', 'info@supplierco.com', '+1-555-0125', 'Canada', true);

-- Sample Suppliers
INSERT INTO suppliers (name, email, phone, address, country, products, status, rating) VALUES
('Fresh Foods Ltd', 'info@freshfoods.com', '+1-555-0201', '123 Fresh Street, Toronto', 'Canada', 'Fresh vegetables, fruits', 'active', 4.5),
('Quality Meats Inc', 'sales@qualitymeats.com', '+1-555-0202', '456 Meat Avenue, Chicago', 'USA', 'Beef, pork, chicken', 'active', 4.2),
('Organic Dairy Co', 'contact@organicdairy.com', '+1-555-0203', '789 Dairy Road, Wisconsin', 'USA', 'Milk, cheese, yogurt', 'active', 4.8);

-- Sample RFQs
INSERT INTO rfqs (title, description, company_id, status, deadline, budget) VALUES
('Fresh Vegetables Supply', 'Need fresh vegetables for restaurant chain', (SELECT id FROM companies WHERE name = 'Buyer Corp' LIMIT 1), 'active', '2024-02-15', 5000.00),
('Meat Supply Contract', 'Looking for quality meat supplier for 6 months', (SELECT id FROM companies WHERE name = 'FoodXchange Inc' LIMIT 1), 'draft', '2024-03-01', 15000.00);

-- Sample Quotes
INSERT INTO quotes (rfq_id, supplier_id, amount, currency, valid_until, status) VALUES
((SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply' LIMIT 1), (SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd' LIMIT 1), 4800.00, 'USD', '2024-02-10', 'pending'),
((SELECT id FROM rfqs WHERE title = 'Meat Supply Contract' LIMIT 1), (SELECT id FROM suppliers WHERE name = 'Quality Meats Inc' LIMIT 1), 14500.00, 'USD', '2024-02-25', 'pending');

-- Sample Products
INSERT INTO products (name, description, category, unit, price, currency, supplier_id, is_active) VALUES
('Organic Tomatoes', 'Fresh organic tomatoes', 'Vegetables', 'kg', 3.50, 'USD', (SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd' LIMIT 1), true),
('Premium Beef', 'High-quality beef cuts', 'Meat', 'kg', 12.00, 'USD', (SELECT id FROM suppliers WHERE name = 'Quality Meats Inc' LIMIT 1), true),
('Organic Milk', 'Fresh organic whole milk', 'Dairy', 'liter', 2.50, 'USD', (SELECT id FROM suppliers WHERE name = 'Organic Dairy Co' LIMIT 1), true); 