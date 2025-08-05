-- Quick Database Statistics
-- Run this to get an overview of your database

-- Summary Statistics
WITH stats AS (
    SELECT 
        (SELECT COUNT(*) FROM suppliers) as total_suppliers,
        (SELECT COUNT(*) FROM users) as total_users,
        (SELECT COUNT(*) FROM projects) as total_projects,
        (SELECT COUNT(*) FROM email_campaigns) as total_campaigns,
        (SELECT COUNT(*) FROM suppliers WHERE products IS NOT NULL AND LENGTH(products) > 200) as enhanced_suppliers
)
SELECT 
    total_suppliers as "Total Suppliers",
    enhanced_suppliers as "AI Enhanced",
    ROUND(enhanced_suppliers::numeric * 100 / total_suppliers, 2) as "Enhancement %",
    total_users as "Users",
    total_projects as "Projects",
    total_campaigns as "Email Campaigns"
FROM stats;

-- Top 10 Countries
SELECT 
    country as "Country",
    COUNT(*) as "Suppliers",
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM suppliers), 2) as "Percentage"
FROM suppliers 
GROUP BY country 
ORDER BY COUNT(*) DESC 
LIMIT 10;