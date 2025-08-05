-- Test PostgreSQL Connection
-- After installing SQLTools, open this file
-- Click the "Run on Active Connection" button that appears
-- Or press Ctrl+E to execute

SELECT 'Connected to FoodXchange!' as message, COUNT(*) as total_suppliers FROM suppliers;