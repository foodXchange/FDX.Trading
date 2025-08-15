-- Add Prutul S.A. as a supplier
DECLARE @SupplierId INT;

-- Check if Prutul already exists
IF NOT EXISTS (SELECT 1 FROM FdxUsers WHERE CompanyName = 'Prutul S.A.')
BEGIN
    INSERT INTO FdxUsers (
        Username,
        Password,
        Email,
        CompanyName,
        Type,
        Country,
        PhoneNumber,
        Website,
        Address,
        Category,
        CategoryId,
        BusinessType,
        FullDescription,
        SubCategories,
        CreatedAt,
        IsActive,
        RequiresPasswordChange,
        DataComplete,
        Verification,
        ImportedAt
    ) VALUES (
        'prutul_sa',
        'TempPassword123!', -- Will require password change
        'office@prutul.ro',
        'Prutul S.A.',
        3, -- Supplier
        'Romania',
        '+40 236 466 100', -- Typical Romania phone format
        'www.prutul.ro',
        'Galati Commercial Harbor, Galati County, Romania',
        'Vegetable Oil Producer',
        1, -- CategoryType.Manufacturer
        'Vegetable Oil Manufacturer & Exporter',
        'Leading producer of vegetable oil with 126+ years tradition. One of the most important agribusiness companies in Romania and major exporter in South-Eastern Europe. Modern factory with crushing, refining and bottling capabilities.',
        'Sunflower Oil, Rapeseed Oil, Soybean Oil, High Oleic Oil',
        GETDATE(),
        1,
        1,
        1,
        2, -- Verified
        GETDATE()
    );
    
    SET @SupplierId = SCOPE_IDENTITY();
    PRINT 'Created Prutul S.A. supplier with ID: ' + CAST(@SupplierId AS VARCHAR(10));
END
ELSE
BEGIN
    SELECT @SupplierId = Id FROM FdxUsers WHERE CompanyName = 'Prutul S.A.';
    PRINT 'Prutul S.A. already exists with ID: ' + CAST(@SupplierId AS VARCHAR(10));
END

-- Add Supplier Details
IF NOT EXISTS (SELECT 1 FROM SupplierDetails WHERE UserId = @SupplierId)
BEGIN
    INSERT INTO SupplierDetails (
        UserId,
        CompanyRegistrationNumber,
        TaxId,
        ProductCategories,
        Certifications,
        PaymentTerms,
        Incoterms,
        Currency,
        MinimumOrderValue,
        LeadTimeDays,
        PreferredSeaPort,
        WarehouseLocations,
        Description,
        SalesContactName,
        SalesContactEmail,
        SalesContactPhone,
        IsVerified,
        VerifiedAt,
        Rating,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'RO1234567', -- Placeholder
        'RO1234567',
        'Sunflower Oil, Rapeseed Oil, Soybean Oil, Vegetable Oils',
        'ISO, IFS, FSSC, FDA, Kosher, Halal, FOSFA, GAFTA',
        'T/T, L/C, 30 days net',
        'FOB, CIF, CFR, EXW',
        'EUR',
        5000.00, -- Minimum order value
        14, -- Lead time in days
        'Galati Commercial Harbor, Constanta Port',
        'Galati, Romania',
        'Top vegetable oil producer with 126+ years tradition. Modern facilities with crushing, refining and bottling capabilities. Export capacity: 6000 tons crude oil, 5000 tons sunflower meal via Danube River terminal.',
        'Sales Department',
        'office@prutul.ro',
        '+40 236 466 100',
        1, -- Verified
        GETDATE(),
        4.8, -- High rating
        GETDATE(),
        GETDATE()
    );
END

-- Add Sunflower Oil Products to SupplierProductCatalogs
-- Product 1: Conventional Sunflower Oil (Linoleic) - 1L
IF NOT EXISTS (SELECT 1 FROM SupplierProductCatalogs WHERE SupplierId = @SupplierId AND ProductCode = 'PRUT-SUN-1L')
BEGIN
    INSERT INTO SupplierProductCatalogs (
        SupplierId,
        ProductName,
        ProductCode,
        Category,
        SubCategory,
        Brand,
        Description,
        Specifications,
        MinOrderQuantity,
        Unit,
        PricePerUnit,
        Currency,
        IsAvailable,
        LeadTimeDays,
        CountryOfOrigin,
        Certifications,
        IsOrganic,
        IsKosher,
        IsHalal,
        IsGlutenFree,
        IsVegan,
        QualityScore,
        SearchTags,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'Refined Sunflower Oil - Conventional (Linoleic) 1L',
        'PRUT-SUN-1L',
        'Vegetable Oils',
        'Sunflower Oil',
        'Prutul',
        'Premium quality refined sunflower oil, conventional type with high linoleic acid content. Perfect for cooking, frying, and salad dressing.',
        'Type: Conventional (Linoleic), Processing: Refined, Deodorized, Winterized, Packaging: 1L PET bottle',
        1000, -- MOQ 1000 bottles
        'Bottles (1L)',
        2.50,
        'EUR',
        1,
        14,
        'Romania',
        'ISO, IFS, FSSC, FDA',
        0,
        1, -- Kosher
        1, -- Halal
        1, -- Gluten Free
        1, -- Vegan
        95,
        'sunflower oil, refined sunflower oil, cooking oil, vegetable oil, linoleic, conventional sunflower oil, prutul',
        GETDATE(),
        GETDATE()
    );
END

-- Product 2: High Oleic Sunflower Oil - Spornic Premium 1L
IF NOT EXISTS (SELECT 1 FROM SupplierProductCatalogs WHERE SupplierId = @SupplierId AND ProductCode = 'PRUT-HO-1L')
BEGIN
    INSERT INTO SupplierProductCatalogs (
        SupplierId,
        ProductName,
        ProductCode,
        Category,
        SubCategory,
        Brand,
        Description,
        Specifications,
        MinOrderQuantity,
        Unit,
        PricePerUnit,
        Currency,
        IsAvailable,
        LeadTimeDays,
        CountryOfOrigin,
        Certifications,
        IsOrganic,
        IsKosher,
        IsHalal,
        IsGlutenFree,
        IsVegan,
        QualityScore,
        SearchTags,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'High Oleic Sunflower Oil - Spornic Premium/Omega 9 1L',
        'PRUT-HO-1L',
        'Vegetable Oils',
        'Sunflower Oil',
        'Spornic Premium',
        'First 100% Romanian High Oleic sunflower oil with min. 75% oleic acid. Premium quality for household consumers. Excellent heat stability.',
        'Type: High Oleic (min. 75% oleic acid), Processing: Refined, Deodorized, Brand: Spornic Omega 9, Packaging: 1L PET bottle',
        1000,
        'Bottles (1L)',
        3.20,
        'EUR',
        1,
        14,
        'Romania',
        'ISO, IFS, FSSC, FDA',
        0,
        1,
        1,
        1,
        1,
        98,
        'sunflower oil, high oleic sunflower oil, omega 9, spornic, premium sunflower oil, cooking oil, healthy oil',
        GETDATE(),
        GETDATE()
    );
END

-- Product 3: Sunflower Oil 5L Family Pack
IF NOT EXISTS (SELECT 1 FROM SupplierProductCatalogs WHERE SupplierId = @SupplierId AND ProductCode = 'PRUT-SUN-5L')
BEGIN
    INSERT INTO SupplierProductCatalogs (
        SupplierId,
        ProductName,
        ProductCode,
        Category,
        SubCategory,
        Brand,
        Description,
        Specifications,
        MinOrderQuantity,
        Unit,
        PricePerUnit,
        Currency,
        IsAvailable,
        LeadTimeDays,
        CountryOfOrigin,
        Certifications,
        IsOrganic,
        IsKosher,
        IsHalal,
        IsGlutenFree,
        IsVegan,
        QualityScore,
        SearchTags,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'Refined Sunflower Oil - Family Pack 5L',
        'PRUT-SUN-5L',
        'Vegetable Oils',
        'Sunflower Oil',
        'Prutul',
        'Economy family pack refined sunflower oil. Ideal for households and small restaurants. Conventional type.',
        'Type: Conventional (Linoleic), Processing: Refined, Deodorized, Winterized, Packaging: 5L PET bottle',
        500,
        'Bottles (5L)',
        11.50,
        'EUR',
        1,
        14,
        'Romania',
        'ISO, IFS, FSSC, FDA',
        0,
        1,
        1,
        1,
        1,
        95,
        'sunflower oil, refined sunflower oil, family pack, 5 liter, bulk sunflower oil, cooking oil',
        GETDATE(),
        GETDATE()
    );
END

-- Product 4: High Oleic Sunflower Oil - HORECA Professional
IF NOT EXISTS (SELECT 1 FROM SupplierProductCatalogs WHERE SupplierId = @SupplierId AND ProductCode = 'PRUT-HO-PRO-5L')
BEGIN
    INSERT INTO SupplierProductCatalogs (
        SupplierId,
        ProductName,
        ProductCode,
        Category,
        SubCategory,
        Brand,
        Description,
        Specifications,
        MinOrderQuantity,
        Unit,
        PricePerUnit,
        Currency,
        IsAvailable,
        LeadTimeDays,
        CountryOfOrigin,
        Certifications,
        IsOrganic,
        IsKosher,
        IsHalal,
        IsGlutenFree,
        IsVegan,
        QualityScore,
        SearchTags,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'High Oleic Sunflower Oil - Spornic Professional 5L',
        'PRUT-HO-PRO-5L',
        'Vegetable Oils',
        'Sunflower Oil',
        'Spornic Professional',
        'Professional grade High Oleic sunflower oil for HORECA and Food Service industry. Superior frying performance and extended shelf life.',
        'Type: High Oleic (min. 75% oleic acid), Grade: Professional/HORECA, Processing: Refined, Packaging: 5L PET bottle',
        200,
        'Bottles (5L)',
        15.00,
        'EUR',
        1,
        14,
        'Romania',
        'ISO, IFS, FSSC, FDA, HACCP',
        0,
        1,
        1,
        1,
        1,
        98,
        'sunflower oil, high oleic, professional, HORECA, restaurant oil, frying oil, spornic professional',
        GETDATE(),
        GETDATE()
    );
END

-- Product 5: Crude Sunflower Oil (Bulk)
IF NOT EXISTS (SELECT 1 FROM SupplierProductCatalogs WHERE SupplierId = @SupplierId AND ProductCode = 'PRUT-CRUDE-BULK')
BEGIN
    INSERT INTO SupplierProductCatalogs (
        SupplierId,
        ProductName,
        ProductCode,
        Category,
        SubCategory,
        Brand,
        Description,
        Specifications,
        MinOrderQuantity,
        Unit,
        PricePerUnit,
        Currency,
        IsAvailable,
        LeadTimeDays,
        CountryOfOrigin,
        Certifications,
        IsOrganic,
        IsKosher,
        IsHalal,
        IsGlutenFree,
        IsVegan,
        QualityScore,
        SearchTags,
        CreatedAt,
        UpdatedAt
    ) VALUES (
        @SupplierId,
        'Crude Sunflower Oil - Bulk Export',
        'PRUT-CRUDE-BULK',
        'Vegetable Oils',
        'Sunflower Oil',
        'Prutul',
        'Crude sunflower oil for industrial refining. Export quality, shipped via Danube River terminal. Max capacity 6000 tons per shipment.',
        'Type: Crude, unrefined, FFA max 2%, Moisture max 0.2%, Shipping: Bulk vessel or flexitank',
        20000, -- 20 MT minimum
        'MT (Metric Tons)',
        850.00,
        'EUR',
        1,
        21,
        'Romania',
        'FOSFA, GAFTA standards',
        0,
        0,
        0,
        1,
        1,
        92,
        'crude sunflower oil, bulk sunflower oil, industrial oil, unrefined sunflower oil, export',
        GETDATE(),
        GETDATE()
    );
END

PRINT 'Successfully added Prutul S.A. and their sunflower oil products to the database';
PRINT 'Products added:';
PRINT '1. Refined Sunflower Oil - Conventional 1L';
PRINT '2. High Oleic Sunflower Oil - Spornic Premium 1L';
PRINT '3. Refined Sunflower Oil - Family Pack 5L';
PRINT '4. High Oleic Sunflower Oil - Professional 5L';
PRINT '5. Crude Sunflower Oil - Bulk Export';