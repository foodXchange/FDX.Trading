-- Direct SQL script to import products from CSV data
-- This script inserts the products with all required fields

-- Sample products insert (simplified for demonstration)
INSERT INTO Products (ProductCode, ProductName, Category, SubCategory, Status, IsKosher, IsOrganic, IsVegan, IsGlutenFree, CreatedAt, ImportedAt)
VALUES 
('000425', 'Poyraz Olive oil -500ML', 'Pantry Staples', 'Oils', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000448', 'CRUSHED TOMATOES(Polpa) Tin 2650mlx6 VICTORIA PROPLUS', 'Pantry Staples', 'Canned Goods', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000279', 'Refined Sunflower Oil, 5 Litters', 'Pantry Staples', 'Oils', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000374', 'org sweetcorn supersweet kernel no cutting size ARDO', 'Frozen', 'Vegetables', 0, 0, 1, 1, 0, GETDATE(), GETDATE()),
('000375', 'sweetcorn supersweet kernel no cutting size', 'Frozen', 'Vegetables', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000376', 'Wokmix - Ardo Organic broccoli, Organic carrot strips', 'Frozen', 'Vegetables', 0, 0, 1, 1, 0, GETDATE(), GETDATE()),
('000377', 'Wokmix - Standard vegetables mix', 'Frozen', 'Vegetables', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000378', 'sweetcorn standard kernel', 'Frozen', 'Vegetables', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000099', 'Dressing Caesar Kens 3.78L', 'Condiments', 'Dressings', 0, 0, 0, 0, 0, GETDATE(), GETDATE()),
('000100', 'DRES BALSAMIC Wishbone 473ml', 'Condiments', 'Dressings', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000123', 'APRICOT IN SYRUP Victoria 3000ml', 'Canned Fruits', 'Fruits', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000155', 'COOKIES choco cream Gullon 470gr', 'Snacks', 'Cookies', 0, 0, 0, 0, 0, GETDATE(), GETDATE()),
('000180', 'Rice Arborio Scotti 1kg', 'Pantry Staples', 'Rice', 0, 0, 0, 1, 1, GETDATE(), GETDATE()),
('000200', 'Pasta Penne Barilla 500g', 'Pantry Staples', 'Pasta', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000220', 'Tomato Paste Victoria 800g', 'Pantry Staples', 'Canned Goods', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000250', 'Frozen Green Beans Ardo 1kg', 'Frozen', 'Vegetables', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000300', 'Honey Natural 500g', 'Pantry Staples', 'Sweeteners', 0, 0, 0, 0, 0, GETDATE(), GETDATE()),
('000350', 'Olive Oil Extra Virgin 1L', 'Pantry Staples', 'Oils', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000400', 'Flour All Purpose 1kg', 'Baking', 'Flour', 0, 0, 0, 1, 0, GETDATE(), GETDATE()),
('000450', 'Sugar White Granulated 1kg', 'Baking', 'Sweeteners', 0, 0, 0, 1, 0, GETDATE(), GETDATE());