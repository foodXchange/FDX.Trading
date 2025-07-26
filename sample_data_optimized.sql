-- Optimized Sample Data for FoodXchange Enhanced Schema
-- This creates comprehensive test data for your Supabase database

-- ============================================================================
-- SAMPLE USERS
-- ============================================================================

INSERT INTO users (name, email, hashed_password, phone, role, is_active, is_admin, email_verified) VALUES
('Admin User', 'admin@foodxchange.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', '+1-555-0101', 'admin', true, true, true),
('John Buyer', 'john@buyercorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', '+1-555-0102', 'buyer', true, false, true),
('Sarah Supplier', 'sarah@freshfoods.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', '+1-555-0103', 'supplier', true, false, true),
('Mike Manager', 'mike@qualitymeats.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', '+1-555-0104', 'supplier', true, false, true),
('Lisa Logistics', 'lisa@organicdairy.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', '+1-555-0105', 'supplier', true, false, true);

-- ============================================================================
-- SAMPLE COMPANIES
-- ============================================================================

INSERT INTO companies (name, legal_name, registration_number, company_type, email, phone, website, 
                      address_line1, city, state_province, postal_code, country, 
                      company_size, year_established, annual_revenue, description, industry,
                      categories, is_verified, rating, total_reviews) VALUES
('FoodXchange Inc', 'FoodXchange Incorporated', 'FX001', 'buyer', 'info@foodxchange.com', '+1-555-0123', 'https://foodxchange.com',
 '123 Main Street', 'New York', 'NY', '10001', 'USA',
 'large', 2020, '$10M-50M', 'Leading food procurement platform', 'Technology',
 '["technology", "food", "procurement"]'::jsonb, true, 4.8, 25),

('Buyer Corp', 'Buyer Corporation', 'BC001', 'buyer', 'info@buyercorp.com', '+1-555-0124', 'https://buyercorp.com',
 '456 Business Ave', 'Chicago', 'IL', '60601', 'USA',
 'medium', 2018, '$5M-10M', 'Restaurant chain operator', 'Food Service',
 '["restaurants", "hospitality", "food-service"]'::jsonb, true, 4.5, 18),

('Fresh Foods Ltd', 'Fresh Foods Limited', 'FF001', 'supplier', 'info@freshfoods.com', '+1-555-0201', 'https://freshfoods.com',
 '789 Fresh Street', 'Toronto', 'ON', 'M5V 2H1', 'Canada',
 'medium', 2015, '$5M-10M', 'Premium fresh produce supplier', 'Agriculture',
 '["fresh-produce", "organic", "local"]'::jsonb, true, 4.7, 32),

('Quality Meats Inc', 'Quality Meats Incorporated', 'QM001', 'supplier', 'sales@qualitymeats.com', '+1-555-0202', 'https://qualitymeats.com',
 '321 Meat Avenue', 'Chicago', 'IL', '60602', 'USA',
 'large', 2010, '$10M-50M', 'Premium meat and poultry supplier', 'Food Processing',
 '["meat", "poultry", "premium"]'::jsonb, true, 4.6, 28),

('Organic Dairy Co', 'Organic Dairy Company', 'OD001', 'supplier', 'contact@organicdairy.com', '+1-555-0203', 'https://organicdairy.com',
 '654 Dairy Road', 'Madison', 'WI', '53701', 'USA',
 'small', 2012, '$1M-5M', 'Organic dairy products supplier', 'Dairy',
 '["dairy", "organic", "farm-fresh"]'::jsonb, true, 4.9, 45);

-- ============================================================================
-- SAMPLE SUPPLIERS
-- ============================================================================

INSERT INTO suppliers (company_id, name, email, phone, website,
                      address_line1, city, state_province, postal_code, country,
                      description, products, certifications, specialties, status, rating, total_reviews,
                      response_time_hours, fulfillment_rate, average_rating) VALUES
((SELECT id FROM companies WHERE name = 'Fresh Foods Ltd'), 'Fresh Foods Ltd', 'info@freshfoods.com', '+1-555-0201', 'https://freshfoods.com',
 '789 Fresh Street', 'Toronto', 'ON', 'M5V 2H1', 'Canada',
 'Premium fresh produce supplier with over 20 years of experience', 'Fresh vegetables, fruits, herbs, microgreens', 'Organic Certified, GAP Certified, HACCP Certified', '["organic", "local", "seasonal"]'::jsonb, 'active', 4.7, 32, 4, 98.5, 4.7),

((SELECT id FROM companies WHERE name = 'Quality Meats Inc'), 'Quality Meats Inc', 'sales@qualitymeats.com', '+1-555-0202', 'https://qualitymeats.com',
 '321 Meat Avenue', 'Chicago', 'IL', '60602', 'USA',
 'Premium meat and poultry supplier serving restaurants nationwide', 'Beef, pork, chicken, lamb, specialty cuts', 'USDA Certified, HACCP Certified, Animal Welfare Approved', '["premium-cuts", "grass-fed", "organic"]'::jsonb, 'active', 4.6, 28, 6, 97.2, 4.6),

((SELECT id FROM companies WHERE name = 'Organic Dairy Co'), 'Organic Dairy Co', 'contact@organicdairy.com', '+1-555-0203', 'https://organicdairy.com',
 '654 Dairy Road', 'Madison', 'WI', '53701', 'USA',
 'Family-owned organic dairy farm producing premium dairy products', 'Milk, cheese, yogurt, butter, cream', 'Organic Certified, Animal Welfare Approved, Local Farm Certified', '["organic", "farm-fresh", "artisanal"]'::jsonb, 'active', 4.9, 45, 2, 99.1, 4.9);

-- ============================================================================
-- SAMPLE PRODUCTS
-- ============================================================================

INSERT INTO products (supplier_id, category_id, name, description, sku, barcode,
                     base_price, currency, unit, min_order_quantity, max_order_quantity,
                     stock_quantity, reorder_level, lead_time_days,
                     weight_kg, specifications, is_active, is_featured) VALUES
-- Fresh Foods Ltd Products
((SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd'), (SELECT id FROM product_categories WHERE name = 'Fresh Produce'), 
 'Organic Tomatoes', 'Fresh organic vine-ripened tomatoes', 'FF-TOM-ORG', '1234567890123',
 3.50, 'USD', 'kg', 5, 100, 500, 50, 2,
 0.15, '{"variety": "vine-ripened", "size": "medium", "packaging": "bulk"}'::jsonb, true, true),

((SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd'), (SELECT id FROM product_categories WHERE name = 'Fresh Produce'), 
 'Fresh Spinach', 'Baby spinach leaves, pre-washed', 'FF-SPI-BABY', '1234567890124',
 4.20, 'USD', 'kg', 2, 50, 200, 20, 1,
 0.05, '{"variety": "baby", "packaging": "pre-washed", "shelf-life": "7 days"}'::jsonb, true, false),

-- Quality Meats Inc Products
((SELECT id FROM suppliers WHERE name = 'Quality Meats Inc'), (SELECT id FROM product_categories WHERE name = 'Meat & Poultry'), 
 'Premium Beef Tenderloin', 'Grade A beef tenderloin, aged 21 days', 'QM-BEEF-TEND', '1234567890125',
 45.00, 'USD', 'kg', 1, 20, 100, 10, 3,
 0.5, '{"grade": "A", "aging": "21 days", "cut": "tenderloin", "packaging": "vacuum-sealed"}'::jsonb, true, true),

((SELECT id FROM suppliers WHERE name = 'Quality Meats Inc'), (SELECT id FROM product_categories WHERE name = 'Meat & Poultry'), 
 'Free-Range Chicken Breast', 'Boneless, skinless chicken breast', 'QM-CHICK-BRST', '1234567890126',
 12.50, 'USD', 'kg', 2, 30, 150, 15, 2,
 0.3, '{"type": "free-range", "cut": "breast", "preparation": "boneless, skinless"}'::jsonb, true, false),

-- Organic Dairy Co Products
((SELECT id FROM suppliers WHERE name = 'Organic Dairy Co'), (SELECT id FROM product_categories WHERE name = 'Dairy & Eggs'), 
 'Organic Whole Milk', 'Fresh organic whole milk, pasteurized', 'OD-MILK-WHOLE', '1234567890127',
 2.50, 'USD', 'liter', 5, 50, 300, 30, 1,
 1.03, '{"type": "whole", "fat-content": "3.25%", "packaging": "glass bottles", "shelf-life": "14 days"}'::jsonb, true, true),

((SELECT id FROM suppliers WHERE name = 'Organic Dairy Co'), (SELECT id FROM product_categories WHERE name = 'Dairy & Eggs'), 
 'Artisanal Cheddar Cheese', 'Aged cheddar cheese, 12 months', 'OD-CHEESE-CHED', '1234567890128',
 8.75, 'USD', 'kg', 1, 10, 50, 5, 2,
 0.25, '{"type": "cheddar", "aging": "12 months", "flavor": "sharp", "packaging": "wax-coated"}'::jsonb, true, false);

-- ============================================================================
-- SAMPLE RFQs
-- ============================================================================

INSERT INTO rfqs (company_id, created_by, title, description, requirements,
                 status, deadline, budget_min, budget_max, currency,
                 payment_terms, delivery_requirements, categories) VALUES
((SELECT id FROM companies WHERE name = 'Buyer Corp'), (SELECT id FROM users WHERE name = 'John Buyer'),
 'Fresh Vegetables Supply', 'Need fresh vegetables for restaurant chain expansion', 'Looking for reliable supplier for 5 new restaurant locations',
 'published', '2024-02-15', 3000.00, 8000.00, 'USD',
 'Net 30', 'Weekly deliveries to multiple locations', '["fresh-produce", "vegetables"]'::jsonb),

((SELECT id FROM companies WHERE name = 'FoodXchange Inc'), (SELECT id FROM users WHERE name = 'Admin User'),
 'Meat Supply Contract', 'Looking for quality meat supplier for 6 months', 'Premium cuts for high-end restaurant clients',
 'published', '2024-03-01', 10000.00, 25000.00, 'USD',
 'Net 45', 'Twice weekly deliveries, temperature controlled', '["meat", "premium-cuts"]'::jsonb),

((SELECT id FROM companies WHERE name = 'Buyer Corp'), (SELECT id FROM users WHERE name = 'John Buyer'),
 'Dairy Products Supply', 'Organic dairy products for health-focused menu', 'Organic milk, cheese, and yogurt for new health food concept',
 'draft', '2024-03-15', 2000.00, 5000.00, 'USD',
 'Net 30', 'Daily deliveries, early morning', '["dairy", "organic"]'::jsonb);

-- ============================================================================
-- SAMPLE RFQ ITEMS
-- ============================================================================

INSERT INTO rfq_items (rfq_id, product_name, description, quantity, unit, specifications, sort_order) VALUES
((SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply'), 'Organic Tomatoes', 'Vine-ripened organic tomatoes', 100, 'kg', '{"variety": "vine-ripened", "size": "medium"}'::jsonb, 1),
((SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply'), 'Fresh Spinach', 'Baby spinach leaves', 50, 'kg', '{"variety": "baby", "pre-washed": true}'::jsonb, 2),
((SELECT id FROM rfqs WHERE title = 'Meat Supply Contract'), 'Premium Beef Tenderloin', 'Grade A beef tenderloin', 50, 'kg', '{"grade": "A", "aging": "21 days"}'::jsonb, 1),
((SELECT id FROM rfqs WHERE title = 'Meat Supply Contract'), 'Free-Range Chicken Breast', 'Boneless, skinless chicken breast', 100, 'kg', '{"type": "free-range", "preparation": "boneless, skinless"}'::jsonb, 2),
((SELECT id FROM rfqs WHERE title = 'Dairy Products Supply'), 'Organic Whole Milk', 'Fresh organic whole milk', 200, 'liter', '{"type": "whole", "organic": true}'::jsonb, 1),
((SELECT id FROM rfqs WHERE title = 'Dairy Products Supply'), 'Artisanal Cheddar Cheese', 'Aged cheddar cheese', 25, 'kg', '{"type": "cheddar", "aging": "12 months"}'::jsonb, 2);

-- ============================================================================
-- SAMPLE QUOTES
-- ============================================================================

INSERT INTO quotes (rfq_id, supplier_id, created_by, title, description, total_amount, currency,
                   status, valid_until, payment_terms, delivery_terms, supplier_notes) VALUES
((SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply'), (SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd'), (SELECT id FROM users WHERE name = 'Sarah Supplier'),
 'Fresh Foods Ltd - Vegetable Supply Quote', 'Comprehensive vegetable supply solution for restaurant chain', 7200.00, 'USD',
 'submitted', '2024-02-10', 'Net 30', 'Weekly deliveries with temperature monitoring', 'We can provide additional organic options and flexible delivery schedules'),

((SELECT id FROM rfqs WHERE title = 'Meat Supply Contract'), (SELECT id FROM suppliers WHERE name = 'Quality Meats Inc'), (SELECT id FROM users WHERE name = 'Mike Manager'),
 'Quality Meats - Premium Meat Supply', 'Premium meat supply with guaranteed quality and delivery', 22500.00, 'USD',
 'submitted', '2024-02-25', 'Net 45', 'Twice weekly deliveries with real-time tracking', 'We offer volume discounts and can customize cuts to your specifications'),

((SELECT id FROM rfqs WHERE title = 'Dairy Products Supply'), (SELECT id FROM suppliers WHERE name = 'Organic Dairy Co'), (SELECT id FROM users WHERE name = 'Lisa Logistics'),
 'Organic Dairy Co - Dairy Supply Quote', 'Organic dairy products with farm-to-table traceability', 4200.00, 'USD',
 'submitted', '2024-03-10', 'Net 30', 'Daily early morning deliveries', 'All products are certified organic and sourced from our family farm');

-- ============================================================================
-- SAMPLE QUOTE ITEMS
-- ============================================================================

INSERT INTO quote_items (quote_id, rfq_item_id, product_id, product_name, description, quantity, unit, unit_price, total_price, delivery_time_days, minimum_order_quantity) VALUES
-- Fresh Foods Quote Items
((SELECT id FROM quotes WHERE title LIKE '%Fresh Foods Ltd%'), 
 (SELECT id FROM rfq_items WHERE product_name = 'Organic Tomatoes' AND rfq_id = (SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply')),
 (SELECT id FROM products WHERE name = 'Organic Tomatoes'),
 'Organic Tomatoes', 'Vine-ripened organic tomatoes', 100, 'kg', 3.25, 325.00, 2, 5),

((SELECT id FROM quotes WHERE title LIKE '%Fresh Foods Ltd%'), 
 (SELECT id FROM rfq_items WHERE product_name = 'Fresh Spinach' AND rfq_id = (SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply')),
 (SELECT id FROM products WHERE name = 'Fresh Spinach'),
 'Fresh Spinach', 'Baby spinach leaves, pre-washed', 50, 'kg', 4.00, 200.00, 1, 2),

-- Quality Meats Quote Items
((SELECT id FROM quotes WHERE title LIKE '%Quality Meats%'), 
 (SELECT id FROM rfq_items WHERE product_name = 'Premium Beef Tenderloin' AND rfq_id = (SELECT id FROM rfqs WHERE title = 'Meat Supply Contract')),
 (SELECT id FROM products WHERE name = 'Premium Beef Tenderloin'),
 'Premium Beef Tenderloin', 'Grade A beef tenderloin, aged 21 days', 50, 'kg', 42.00, 2100.00, 3, 1),

-- Organic Dairy Quote Items
((SELECT id FROM quotes WHERE title LIKE '%Organic Dairy Co%'), 
 (SELECT id FROM rfq_items WHERE product_name = 'Organic Whole Milk' AND rfq_id = (SELECT id FROM rfqs WHERE title = 'Dairy Products Supply')),
 (SELECT id FROM products WHERE name = 'Organic Whole Milk'),
 'Organic Whole Milk', 'Fresh organic whole milk', 200, 'liter', 2.25, 450.00, 1, 5);

-- ============================================================================
-- SAMPLE NOTIFICATIONS
-- ============================================================================

INSERT INTO notifications (user_id, company_id, title, message, type, entity_type, entity_id) VALUES
((SELECT id FROM users WHERE name = 'John Buyer'), (SELECT id FROM companies WHERE name = 'Buyer Corp'),
 'New Quote Received', 'You have received a new quote for Fresh Vegetables Supply', 'quote', 'quote', 
 (SELECT id FROM quotes WHERE title LIKE '%Fresh Foods Ltd%')),

((SELECT id FROM users WHERE name = 'Admin User'), (SELECT id FROM companies WHERE name = 'FoodXchange Inc'),
 'RFQ Published', 'Your RFQ "Meat Supply Contract" has been published successfully', 'rfq', 'rfq',
 (SELECT id FROM rfqs WHERE title = 'Meat Supply Contract')),

((SELECT id FROM users WHERE name = 'Sarah Supplier'), (SELECT id FROM companies WHERE name = 'Fresh Foods Ltd'),
 'New RFQ Available', 'A new RFQ for Fresh Vegetables Supply matches your specialties', 'rfq', 'rfq',
 (SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply')); 