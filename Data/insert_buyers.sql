-- Insert buyer users into FdxUsers table
INSERT INTO FdxUsers (Username, Password, Email, CompanyName, Type, Country, PhoneNumber, Website, Address, Category, CategoryId, BusinessType, FullDescription, SubCategories, CreatedAt, IsActive, RequiresPasswordChange, DataComplete, Verification, ImportedAt)
VALUES
-- Supermarket Chains
('shufersal', 'FDX2025!', 'info@shufersal.co.il', 'Shufersal', 2, 'Israel', '+972 3 123 4567', 'https://www.shufersal.co.il', 'Tel Aviv, Israel', 'Supermarket Chain', 101, 'Leading Israeli supermarket chain', 'One of Israel''s largest supermarket chains with 300+ stores', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('carrefour', 'FDX2025!', 'contact@carrefour.fr', 'Carrefour', 2, 'France', '+33 1 234 5678', 'https://www.carrefour.com', 'Paris, France', 'Supermarket Chain', 101, 'French multinational retail corporation', 'Global hypermarket chain with stores worldwide', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('yochananof', 'FDX2025!', 'service@yochananof.co.il', 'Yochananof', 2, 'Israel', '+972 3 234 5678', 'https://www.yochananof.co.il', 'Jerusalem, Israel', 'Supermarket Chain', 101, 'Israeli supermarket chain', 'Leading Israeli supermarket chain with competitive prices', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('rami_levy', 'FDX2025!', 'service@ramilevi.co.il', 'Rami Levy', 2, 'Israel', '+972 2 456 7890', 'https://www.ramilevi.co.il', 'Modiin, Israel', 'Supermarket Chain', 101, 'Discount supermarket chain', 'Israel''s largest discount supermarket chain', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('victory_supermarket', 'FDX2025!', 'contact@victory.co.il', 'Victory Supermarket', 2, 'Israel', '+972 3 012 3456', 'https://www.victory.co.il', 'Rishon LeZion, Israel', 'Supermarket Chain', 101, 'Growing retail chain', 'Growing retail chain in central Israel', '', GETDATE(), 1, 1, 1, 1, GETDATE()),

-- Wholesale Distributors
('h_cohen', 'FDX2025!', 'orders@hcohen.co.il', 'H. Cohen', 2, 'Israel', '+972 4 345 6789', 'https://www.hcohen.co.il', 'Haifa, Israel', 'Wholesale Distributor', 103, 'Major wholesale distributor', 'Major wholesale distributor supplying retailers and restaurants', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('middle_trade', 'FDX2025!', 'info@middletrade.com', 'Middle Trade', 2, 'Israel', '+972 3 456 7890', 'https://www.middletrade.com', 'Tel Aviv, Israel', 'Wholesale Distributor', 103, 'Import/export food distributor', 'Wholesale distribution specializing in import/export', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('machsanei_hashuk', 'FDX2025!', 'info@machsanei-hashuk.co.il', 'Machsanei Hashuk', 2, 'Israel', '+972 3 678 9012', 'https://www.machsanei-hashuk.co.il', 'Tel Aviv, Israel', 'Wholesale Distributor', 103, 'Fresh produce wholesale market', 'Wholesale market operator for fresh produce', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('zol_vebegadol', 'FDX2025!', 'service@zolvebegadol.co.il', 'Zol VeBegadol', 2, 'Israel', '+972 3 901 2345', 'https://www.zolvebegadol.co.il', 'Bnei Brak, Israel', 'Wholesale Distributor', 103, 'Warehouse-style discount retailer', 'Bulk purchases at wholesale prices', '', GETDATE(), 1, 1, 1, 1, GETDATE()),

-- Specialty Stores
('hasade_organic', 'FDX2025!', 'info@hasade-organic.co.il', 'HaSade Organic', 2, 'Israel', '+972 3 567 8901', 'https://www.hasade-organic.co.il', 'Tel Aviv, Israel', 'Specialty Store', 107, 'Organic and natural products', 'Specialty store chain for organic products', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('harduf', 'FDX2025!', 'sales@harduf.co.il', 'Harduf', 2, 'Israel', '+972 4 678 9012', 'https://www.harduf.co.il', 'Harduf, Israel', 'Specialty Store', 107, 'Organic food producer', 'Organic dairy and vegetables producer', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('eden_teva_market', 'FDX2025!', 'info@eden-teva.co.il', 'Eden Teva Market', 2, 'Israel', '+972 3 678 9012', 'https://www.eden-teva.co.il', 'Tel Aviv, Israel', 'Specialty Store', 107, 'Natural and organic food chain', 'Natural food chain across Israel', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('tiv_taam', 'FDX2025!', 'info@tivtaam.co.il', 'Tiv Taam', 2, 'Israel', '+972 3 234 5678', 'https://www.tivtaam.co.il', 'Tel Aviv, Israel', 'Specialty Store', 107, 'Non-kosher supermarket chain', 'Leading non-kosher chain with international products', '', GETDATE(), 1, 1, 1, 1, GETDATE()),

-- Convenience Stores
('dor_alon', 'FDX2025!', 'service@doralon.co.il', 'Dor Alon', 2, 'Israel', '+972 3 456 7890', 'https://www.doralon.co.il', 'Yakum, Israel', 'Convenience Store', 102, 'Gas station convenience stores', 'Energy company with 220 fueling stations and Am:Pm stores', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('stop_market', 'FDX2025!', 'info@stopmarket.co.il', 'Stop Market', 2, 'Israel', '+972 3 012 3456', 'https://www.stopmarket.co.il', 'Tel Aviv, Israel', 'Convenience Store', 102, 'Extended hours convenience chain', 'Convenience stores serving urban areas', '', GETDATE(), 1, 1, 1, 1, GETDATE()),

-- Online Retailers
('king_store', 'FDX2025!', 'orders@kingstore.co.il', 'King Store', 2, 'Israel', '+972 3 567 8901', 'https://www.kingstore.co.il', 'Ramat Gan, Israel', 'Online Retailer', 104, 'Online imported foods retailer', 'Online retailer for imported and specialty items', '', GETDATE(), 1, 1, 1, 1, GETDATE()),

-- Other Retail
('proplus', 'FDX2025!', 'service@proplus.co.il', 'ProPlus', 2, 'Israel', '+972 3 789 0123', 'https://www.proplus.co.il', 'Netanya, Israel', 'Retail', 107, 'Household and consumer products', 'Retail chain with competitive prices', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('super_sapir', 'FDX2025!', 'info@supersapir.co.il', 'Super Sapir', 2, 'Israel', '+972 8 890 1234', 'https://www.supersapir.co.il', 'Ashkelon, Israel', 'Retail', 107, 'Regional supermarket chain', 'Regional chain with personalized service', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('milouoff', 'FDX2025!', 'orders@milouoff.co.il', 'Milouoff', 2, 'Israel', '+972 3 901 2345', 'https://www.milouoff.co.il', 'Herzliya, Israel', 'Retail', 107, 'Imported and gourmet products', 'Specialty retailer for imported foods', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('mega_bool', 'FDX2025!', 'service@megabool.co.il', 'Mega Bool', 2, 'Israel', '+972 3 123 4567', 'https://www.megabool.co.il', 'Petah Tikva, Israel', 'Retail', 107, 'Discount bulk supermarket', 'Bulk purchasing for families and businesses', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('osher_ad', 'FDX2025!', 'info@osherad.co.il', 'Osher Ad', 2, 'Israel', '+972 2 345 6789', 'https://www.osherad.co.il', 'Jerusalem, Israel', 'Retail', 107, 'Discount supermarket chain', 'Known for low prices on wide range', '', GETDATE(), 1, 1, 1, 1, GETDATE()),
('fresh_market', 'FDX2025!', 'contact@freshmarket.co.il', 'Fresh Market', 2, 'Israel', '+972 3 890 1234', 'https://www.freshmarket.co.il', 'Raanana, Israel', 'Retail', 107, 'Premium fresh produce', 'Premium fresh produce and gourmet foods', '', GETDATE(), 1, 1, 1, 1, GETDATE());