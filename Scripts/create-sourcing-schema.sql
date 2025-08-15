-- =================================================================
-- FDX SOURCING SCHEMA - Complete Supplier/Product/Category System
-- =================================================================
-- Designed for: Azure SQL Database
-- Maps to: Suppliers_Optimized.xlsx, Products 13_8_2025.csv, Products Category 15_8_2025.csv

USE fdxdb;
GO

-- Create schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'fdx')
BEGIN
    EXEC('CREATE SCHEMA fdx');
END
GO

-- =========================
-- 1. SUPPLIERS (from Suppliers_Optimized.xlsx)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'Suppliers')
BEGIN
    CREATE TABLE fdx.Suppliers (
        SupplierId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name NVARCHAR(300) NOT NULL,
        BrandOwnerName NVARCHAR(300) NULL,
        CountryCode CHAR(2) NULL,
        Website NVARCHAR(500) NULL,
        IsManufacturer BIT NOT NULL DEFAULT 1,
        Certifications NVARCHAR(400) NULL,  -- Quick list, normalized in SupplierCerts
        Active BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ModifiedAt DATETIMEOFFSET NULL,
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_Suppliers_Name ON fdx.Suppliers(Name);
    CREATE INDEX IX_Suppliers_Country ON fdx.Suppliers(CountryCode);
    CREATE INDEX IX_Suppliers_Active ON fdx.Suppliers(Active) WHERE Active = 1;
END
GO

-- =========================
-- 2. BRANDS (usually owned by supplier/manufacturer)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'Brands')
BEGIN
    CREATE TABLE fdx.Brands (
        BrandId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        SupplierId UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT FK_Brands_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        BrandName NVARCHAR(200) NOT NULL,
        IsDeleted BIT NOT NULL DEFAULT 0,
        CONSTRAINT UX_Brands_SupplierBrand UNIQUE (SupplierId, BrandName)
    );
    
    CREATE INDEX IX_Brands_Supplier ON fdx.Brands(SupplierId);
    CREATE INDEX IX_Brands_Name ON fdx.Brands(BrandName);
END
GO

-- =========================
-- 3. PRODUCT CATEGORIES (4 levels from Products Category file)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'ProductCategories')
BEGIN
    CREATE TABLE fdx.ProductCategories (
        CategoryId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        L1 NVARCHAR(100) NOT NULL,   -- Group
        L2 NVARCHAR(100) NULL,       -- Category
        L3 NVARCHAR(100) NULL,       -- SubCategory
        L4 NVARCHAR(100) NULL,       -- SubSubCategory
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_ProductCategories_Keys ON fdx.ProductCategories(L1, L2, L3, L4);
    CREATE INDEX IX_ProductCategories_L1 ON fdx.ProductCategories(L1);
    CREATE INDEX IX_ProductCategories_L2 ON fdx.ProductCategories(L2) WHERE L2 IS NOT NULL;
END
GO

-- =========================
-- 4. PRODUCTS (supplier SKUs from Products file)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'Products')
BEGIN
    CREATE TABLE fdx.Products (
        ProductId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        SupplierId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_Products_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        BrandId UNIQUEIDENTIFIER NULL 
            CONSTRAINT FK_Products_Brands FOREIGN KEY REFERENCES fdx.Brands(BrandId),
        SupplierProductCode NVARCHAR(100) NULL,
        ProductName NVARCHAR(300) NOT NULL,
        Description NVARCHAR(MAX) NULL,
        Packaging NVARCHAR(200) NULL,
        ShelfLifeDays INT NULL,
        CountryOfOrigin CHAR(2) NULL,
        Active BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ModifiedAt DATETIMEOFFSET NULL,
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE UNIQUE INDEX UX_Products_SupplierSku 
        ON fdx.Products(SupplierId, SupplierProductCode) 
        WHERE SupplierProductCode IS NOT NULL;
    CREATE INDEX IX_Products_Supplier ON fdx.Products(SupplierId);
    CREATE INDEX IX_Products_Brand ON fdx.Products(BrandId) WHERE BrandId IS NOT NULL;
    CREATE INDEX IX_Products_Name ON fdx.Products(ProductName);
    CREATE INDEX IX_Products_Active ON fdx.Products(Active) WHERE Active = 1;
END
GO

-- =========================
-- 5. PRODUCT ↔ CATEGORY MAP (N:M relationship)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'ProductCategoryMap')
BEGIN
    CREATE TABLE fdx.ProductCategoryMap (
        ProductId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_ProductCategoryMap_Products FOREIGN KEY REFERENCES fdx.Products(ProductId),
        CategoryId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_ProductCategoryMap_Categories FOREIGN KEY REFERENCES fdx.ProductCategories(CategoryId),
        CONSTRAINT PK_ProductCategoryMap PRIMARY KEY (ProductId, CategoryId)
    );
    
    CREATE INDEX IX_ProductCategoryMap_Category ON fdx.ProductCategoryMap(CategoryId);
END
GO

-- =========================
-- 6. PRODUCT ATTRIBUTES (structured booleans & enums)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'ProductAttributes')
BEGIN
    CREATE TABLE fdx.ProductAttributes (
        ProductId UNIQUEIDENTIFIER PRIMARY KEY 
            CONSTRAINT FK_ProductAttributes_Products FOREIGN KEY REFERENCES fdx.Products(ProductId),
        IsKosher BIT NULL,
        KosherPreference NVARCHAR(100) NULL,   -- e.g., OU, Badatz, Star-K
        IsFreeFrom BIT NULL,
        FreeFromOptions NVARCHAR(400) NULL,    -- CSV: dairy,gluten,nuts,soy
        AllergenInfo NVARCHAR(400) NULL,
        Organic BIT NULL,
        Vegan BIT NULL,
        Halal BIT NULL,
        NonGMO BIT NULL,
        FairTrade BIT NULL
    );
    
    CREATE INDEX IX_ProductAttributes_Kosher ON fdx.ProductAttributes(IsKosher) WHERE IsKosher = 1;
    CREATE INDEX IX_ProductAttributes_FreeFrom ON fdx.ProductAttributes(IsFreeFrom) WHERE IsFreeFrom = 1;
END
GO

-- =========================
-- 7. SUPPLIER CAPABILITIES & LOGISTICS
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'SupplierCapabilities')
BEGIN
    CREATE TABLE fdx.SupplierCapabilities (
        SupplierId UNIQUEIDENTIFIER PRIMARY KEY 
            CONSTRAINT FK_SupplierCapabilities_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        Incoterms NVARCHAR(200) NULL,          -- e.g., "FOB,CIF,DAP"
        ContainerLoading NVARCHAR(50) NULL,    -- Floor/Palletized
        PalletSize NVARCHAR(50) NULL,          -- EUR/US/UK
        MinOrderQty DECIMAL(18,2) NULL,
        LeadTimeDays INT NULL,
        ExportCountries NVARCHAR(MAX) NULL,    -- CSV of country codes
        PaymentTerms NVARCHAR(200) NULL,
        ProductionCapacity NVARCHAR(200) NULL
    );
END
GO

-- =========================
-- 8. CERTIFICATIONS (normalized)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'Certifications')
BEGIN
    CREATE TABLE fdx.Certifications (
        CertId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Scheme NVARCHAR(50) NOT NULL,          -- BRCGS, SQF, ISO22000, Sedex, SMETA
        Code NVARCHAR(100) NULL,               -- Site code
        Issuer NVARCHAR(100) NULL,
        Grade NVARCHAR(20) NULL                -- A, AA, etc.
    );
    
    CREATE INDEX IX_Certifications_Scheme ON fdx.Certifications(Scheme);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'SupplierCerts')
BEGIN
    CREATE TABLE fdx.SupplierCerts (
        SupplierId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_SupplierCerts_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        CertId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_SupplierCerts_Certifications FOREIGN KEY REFERENCES fdx.Certifications(CertId),
        ValidFrom DATE NULL,
        ValidTo DATE NULL,
        DocumentUrl NVARCHAR(500) NULL,
        CONSTRAINT PK_SupplierCerts PRIMARY KEY (SupplierId, CertId)
    );
    
    CREATE INDEX IX_SupplierCerts_Supplier ON fdx.SupplierCerts(SupplierId);
    CREATE INDEX IX_SupplierCerts_ValidTo ON fdx.SupplierCerts(ValidTo);
END
GO

-- =========================
-- 9. PRODUCT IMAGES
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'ProductImages')
BEGIN
    CREATE TABLE fdx.ProductImages (
        ImageId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ProductId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_ProductImages_Products FOREIGN KEY REFERENCES fdx.Products(ProductId),
        BlobUri NVARCHAR(800) NOT NULL,
        ContentType NVARCHAR(100) NULL,
        Caption NVARCHAR(200) NULL,
        DisplayOrder INT NOT NULL DEFAULT 0,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    
    CREATE INDEX IX_ProductImages_Product ON fdx.ProductImages(ProductId);
END
GO

-- =========================
-- 10. SOURCING MATCH SNAPSHOTS (audit trail)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'SourcingMatches')
BEGIN
    CREATE TABLE fdx.SourcingMatches (
        MatchId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        RequestId INT NOT NULL,                -- FK to existing dbo.Requests
        ProjectCode NVARCHAR(50) NULL,
        RunAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        RunBy NVARCHAR(100) NULL,
        FilterCriteria NVARCHAR(MAX) NULL,     -- JSON of applied filters
        Notes NVARCHAR(400) NULL
    );
    
    CREATE INDEX IX_SourcingMatches_Request ON fdx.SourcingMatches(RequestId);
    CREATE INDEX IX_SourcingMatches_RunAt ON fdx.SourcingMatches(RunAt DESC);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'SourcingMatchSuppliers')
BEGIN
    CREATE TABLE fdx.SourcingMatchSuppliers (
        MatchId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_SourcingMatchSuppliers_Matches FOREIGN KEY REFERENCES fdx.SourcingMatches(MatchId),
        SupplierId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_SourcingMatchSuppliers_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        Score DECIMAL(5,2) NOT NULL,           -- 0.00 to 100.00
        Rank INT NOT NULL,
        Why NVARCHAR(MAX) NULL,                -- JSON explanation
        CategoryMatch DECIMAL(5,2) NULL,       -- Component scores
        AttributeMatch DECIMAL(5,2) NULL,
        LogisticsMatch DECIMAL(5,2) NULL,
        CertificationBonus DECIMAL(5,2) NULL,
        CONSTRAINT PK_SourcingMatchSuppliers PRIMARY KEY (MatchId, SupplierId)
    );
    
    CREATE INDEX IX_SourcingMatchSuppliers_Score ON fdx.SourcingMatchSuppliers(Score DESC);
END
GO

-- =========================
-- 11. SUPPLIER CONTACTS (for communication)
-- =========================
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('fdx') AND name = 'SupplierContacts')
BEGIN
    CREATE TABLE fdx.SupplierContacts (
        ContactId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        SupplierId UNIQUEIDENTIFIER NOT NULL 
            CONSTRAINT FK_SupplierContacts_Suppliers FOREIGN KEY REFERENCES fdx.Suppliers(SupplierId),
        Name NVARCHAR(200) NOT NULL,
        Title NVARCHAR(100) NULL,
        Email NVARCHAR(200) NULL,
        Phone NVARCHAR(50) NULL,
        IsPrimary BIT NOT NULL DEFAULT 0,
        Active BIT NOT NULL DEFAULT 1
    );
    
    CREATE INDEX IX_SupplierContacts_Supplier ON fdx.SupplierContacts(SupplierId);
    CREATE INDEX IX_SupplierContacts_Email ON fdx.SupplierContacts(Email);
END
GO

-- =========================
-- 12. VIEWS FOR EASIER QUERYING
-- =========================

-- View: Products with full category path
IF EXISTS (SELECT * FROM sys.views WHERE schema_id = SCHEMA_ID('fdx') AND name = 'vw_ProductsWithCategories')
    DROP VIEW fdx.vw_ProductsWithCategories;
GO

CREATE VIEW fdx.vw_ProductsWithCategories AS
SELECT 
    p.ProductId,
    p.ProductName,
    p.SupplierId,
    s.Name AS SupplierName,
    s.CountryCode,
    b.BrandName,
    pc.L1, pc.L2, pc.L3, pc.L4,
    CONCAT(pc.L1, 
           CASE WHEN pc.L2 IS NOT NULL THEN ' > ' + pc.L2 ELSE '' END,
           CASE WHEN pc.L3 IS NOT NULL THEN ' > ' + pc.L3 ELSE '' END,
           CASE WHEN pc.L4 IS NOT NULL THEN ' > ' + pc.L4 ELSE '' END) AS CategoryPath,
    pa.IsKosher,
    pa.KosherPreference,
    pa.IsFreeFrom,
    pa.FreeFromOptions,
    p.Active
FROM fdx.Products p
    INNER JOIN fdx.Suppliers s ON p.SupplierId = s.SupplierId
    LEFT JOIN fdx.Brands b ON p.BrandId = b.BrandId
    LEFT JOIN fdx.ProductCategoryMap pcm ON p.ProductId = pcm.ProductId
    LEFT JOIN fdx.ProductCategories pc ON pcm.CategoryId = pc.CategoryId
    LEFT JOIN fdx.ProductAttributes pa ON p.ProductId = pa.ProductId
WHERE p.IsDeleted = 0 AND s.IsDeleted = 0;
GO

-- View: Suppliers with capabilities and cert count
IF EXISTS (SELECT * FROM sys.views WHERE schema_id = SCHEMA_ID('fdx') AND name = 'vw_SuppliersWithCapabilities')
    DROP VIEW fdx.vw_SuppliersWithCapabilities;
GO

CREATE VIEW fdx.vw_SuppliersWithCapabilities AS
SELECT 
    s.SupplierId,
    s.Name,
    s.CountryCode,
    s.Website,
    cap.Incoterms,
    cap.ContainerLoading,
    cap.LeadTimeDays,
    cap.MinOrderQty,
    cap.ExportCountries,
    COUNT(DISTINCT sc.CertId) AS CertificationCount,
    COUNT(DISTINCT p.ProductId) AS ProductCount,
    COUNT(DISTINCT b.BrandId) AS BrandCount
FROM fdx.Suppliers s
    LEFT JOIN fdx.SupplierCapabilities cap ON s.SupplierId = cap.SupplierId
    LEFT JOIN fdx.SupplierCerts sc ON s.SupplierId = sc.SupplierId
    LEFT JOIN fdx.Products p ON s.SupplierId = p.SupplierId AND p.IsDeleted = 0
    LEFT JOIN fdx.Brands b ON s.SupplierId = b.SupplierId AND b.IsDeleted = 0
WHERE s.IsDeleted = 0 AND s.Active = 1
GROUP BY s.SupplierId, s.Name, s.CountryCode, s.Website, 
         cap.Incoterms, cap.ContainerLoading, cap.LeadTimeDays, 
         cap.MinOrderQty, cap.ExportCountries;
GO

-- =========================
-- 13. STORED PROCEDURES
-- =========================

-- SP: Get top suppliers for a category
IF EXISTS (SELECT * FROM sys.procedures WHERE schema_id = SCHEMA_ID('fdx') AND name = 'sp_GetTopSuppliersForCategory')
    DROP PROCEDURE fdx.sp_GetTopSuppliersForCategory;
GO

CREATE PROCEDURE fdx.sp_GetTopSuppliersForCategory
    @L1 NVARCHAR(100) = NULL,
    @L2 NVARCHAR(100) = NULL,
    @L3 NVARCHAR(100) = NULL,
    @L4 NVARCHAR(100) = NULL,
    @TopN INT = 10
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TOP(@TopN)
        s.SupplierId,
        s.Name AS SupplierName,
        s.CountryCode,
        COUNT(DISTINCT p.ProductId) AS ProductCount,
        STRING_AGG(DISTINCT b.BrandName, ', ') AS Brands
    FROM fdx.Suppliers s
        INNER JOIN fdx.Products p ON s.SupplierId = p.SupplierId
        LEFT JOIN fdx.Brands b ON p.BrandId = b.BrandId
        INNER JOIN fdx.ProductCategoryMap pcm ON p.ProductId = pcm.ProductId
        INNER JOIN fdx.ProductCategories pc ON pcm.CategoryId = pc.CategoryId
    WHERE s.Active = 1 AND p.Active = 1
        AND s.IsDeleted = 0 AND p.IsDeleted = 0
        AND (@L1 IS NULL OR pc.L1 = @L1)
        AND (@L2 IS NULL OR pc.L2 = @L2)
        AND (@L3 IS NULL OR pc.L3 = @L3)
        AND (@L4 IS NULL OR pc.L4 = @L4)
    GROUP BY s.SupplierId, s.Name, s.CountryCode
    ORDER BY COUNT(DISTINCT p.ProductId) DESC;
END
GO

PRINT 'FDX Sourcing Schema created successfully!';
PRINT 'Tables created in fdx schema:';
PRINT '  - Suppliers, Brands, ProductCategories, Products';
PRINT '  - ProductCategoryMap, ProductAttributes, SupplierCapabilities';
PRINT '  - Certifications, SupplierCerts, ProductImages';
PRINT '  - SourcingMatches, SourcingMatchSuppliers, SupplierContacts';
PRINT 'Views: vw_ProductsWithCategories, vw_SuppliersWithCapabilities';
PRINT 'Stored Procedures: sp_GetTopSuppliersForCategory';
GO