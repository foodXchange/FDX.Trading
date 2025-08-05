-- FoodXchange Common SQL Queries
-- Use Ctrl+Shift+E to execute selected query

-- 1. Count all suppliers
SELECT COUNT(*) as total_suppliers FROM suppliers;

-- 2. Suppliers by country
SELECT country, COUNT(*) as count 
FROM suppliers 
GROUP BY country 
ORDER BY count DESC 
LIMIT 20;

-- 3. Search suppliers by product
SELECT supplier_name, company_name, country, products 
FROM suppliers 
WHERE products ILIKE '%olive oil%'
LIMIT 50;

-- 4. Recently added suppliers
SELECT supplier_name, country, created_at 
FROM suppliers 
ORDER BY created_at DESC 
LIMIT 20;

-- 5. AI-enhanced suppliers
SELECT COUNT(*) as enhanced_count 
FROM suppliers 
WHERE products IS NOT NULL 
AND LENGTH(products) > 200;

-- 6. My projects
SELECT * FROM projects 
WHERE user_email = 'udi@fdx.trading';

-- 7. Suppliers in Italy
SELECT supplier_name, company_name, company_email, products 
FROM suppliers 
WHERE country = 'Italy' 
LIMIT 100;

-- 8. Check email campaigns
SELECT name, status, sent_count, response_count 
FROM email_campaigns 
ORDER BY created_at DESC;

-- 9. Random sample of suppliers
SELECT * FROM suppliers 
ORDER BY RANDOM() 
LIMIT 10;

-- 10. Export all suppliers (careful - large!)
-- SELECT * FROM suppliers;