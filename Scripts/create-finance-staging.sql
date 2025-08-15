-- =====================================================
-- FoodXchange Finance Staging Tables
-- For safe CSV import and normalization
-- =====================================================

USE fdxdb;
GO

-- Create staging schema if not exists
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'stg')
BEGIN
    EXEC('CREATE SCHEMA stg');
END
GO

-- =====================================================
-- 1) Commission Rates Staging (from Commission Rates CSV)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CommissionRatesRaw' AND schema_id = SCHEMA_ID('stg'))
BEGIN
    CREATE TABLE stg.CommissionRatesRaw (
        RowId INT IDENTITY(1,1) PRIMARY KEY,
        [Commission ID] NVARCHAR(100) NULL,
        [Buyer Company] NVARCHAR(300) NULL,
        [Supplier] NVARCHAR(300) NULL,
        [Commission Basis] NVARCHAR(40) NULL,     -- % or flat, etc.
        [Rate] NVARCHAR(100) NULL,                -- "3.5%" or "250 USD"
        [Currency] NVARCHAR(10) NULL,
        [Payer] NVARCHAR(20) NULL,                -- buyer/supplier
        [Incoterms] NVARCHAR(10) NULL,
        [Mode] NVARCHAR(15) NULL,                 -- sea/air/road/rail
        [Origin Country] NVARCHAR(2) NULL,
        [Dest Country] NVARCHAR(2) NULL,
        [Category] NVARCHAR(200) NULL,
        [Effective From] NVARCHAR(20) NULL,
        [Effective To] NVARCHAR(20) NULL,
        ImportedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- =====================================================
-- 2) Invoices Staging (from Invoices CSV)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'InvoicesRaw' AND schema_id = SCHEMA_ID('stg'))
BEGIN
    CREATE TABLE stg.InvoicesRaw (
        RowId INT IDENTITY(1,1) PRIMARY KEY,
        [Invoice ID] NVARCHAR(100) NULL,
        [Type] NVARCHAR(10) NULL,                      -- AR/AP
        [Counterparty Type] NVARCHAR(20) NULL,         -- buyer/supplier/external_org
        [Counterparty Name/Id] NVARCHAR(300) NULL,
        [Invoice ID/ Name (From Files)] NVARCHAR(200) NULL,
        [Issue Date] NVARCHAR(30) NULL,
        [Due Date] NVARCHAR(30) NULL,
        [Currency] NVARCHAR(10) NULL,
        [Subtotal] NVARCHAR(50) NULL,
        [Tax] NVARCHAR(50) NULL,
        [Status] NVARCHAR(30) NULL,
        [Order Code] NVARCHAR(60) NULL,
        [Shipment Id] NVARCHAR(100) NULL,
        [Payment Method] NVARCHAR(50) NULL,
        [Payment Reference] NVARCHAR(120) NULL,
        [Notes] NVARCHAR(MAX) NULL,
        ImportedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- =====================================================
-- 3) Shipping Staging (from Shipping CSV)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ShippingRaw' AND schema_id = SCHEMA_ID('stg'))
BEGIN
    CREATE TABLE stg.ShippingRaw (
        RowId INT IDENTITY(1,1) PRIMARY KEY,
        [Shipping ID] NVARCHAR(120) NULL,
        [Arrival Date] NVARCHAR(30) NULL,
        [Buyer Company] NVARCHAR(300) NULL,
        [Supplier] NVARCHAR(300) NULL,
        [Forwarder] NVARCHAR(300) NULL,
        [Customs Agent] NVARCHAR(300) NULL,
        [Invoice No] NVARCHAR(120) NULL,           -- forwarder/customs bill
        [Invoice Amount] NVARCHAR(50) NULL,
        [Invoice Currency] NVARCHAR(10) NULL,
        [Kind] NVARCHAR(40) NULL,                  -- freight/customs/insurance
        [Order Code] NVARCHAR(60) NULL,
        [Shipment Id] NVARCHAR(120) NULL,
        [Container Number] NVARCHAR(20) NULL,
        [BL Number] NVARCHAR(60) NULL,
        [Mode] NVARCHAR(15) NULL,
        [Port of Loading] NVARCHAR(120) NULL,
        [Port of Discharge] NVARCHAR(120) NULL,
        [ETD] NVARCHAR(30) NULL,
        [ETA] NVARCHAR(30) NULL,
        ImportedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- =====================================================
-- External Organizations table (for forwarders, customs agents, etc.)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExternalOrgs' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ExternalOrgs (
        ExternalOrgId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name NVARCHAR(300) NOT NULL,
        Type NVARCHAR(40) NOT NULL, -- forwarder/customs_agent/insurer/warehouse
        Country NVARCHAR(2) NULL,
        Contact NVARCHAR(200) NULL,
        Email NVARCHAR(200) NULL,
        Phone NVARCHAR(50) NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_ExternalOrgs_Name ON fdx.ExternalOrgs(Name);
END
GO

-- =====================================================
-- Upsert Stored Procedures for Normalization
-- =====================================================

-- Normalize Commission Rates from staging to production
CREATE OR ALTER PROCEDURE stg.usp_NormalizeCommissionRates
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        ;WITH NormalizedRates AS (
            SELECT
                Name = COALESCE([Commission ID], 
                               CONCAT([Buyer Company], ' -> ', [Supplier]),
                               CONCAT('Rate-', FORMAT(GETUTCDATE(), 'yyyyMMdd-HHmmss'))),
                Payer = COALESCE([Payer], 'supplier'),
                Basis = CASE 
                          WHEN [Commission Basis] LIKE '%freight%' THEN 'freight_value'
                          WHEN [Commission Basis] LIKE '%line%' THEN 'line_value'
                          ELSE 'order_value' 
                        END,
                RatePct = TRY_CAST(REPLACE(REPLACE([Rate], '%', ''), ' ', '') AS DECIMAL(9,4)),
                FlatAmount = CASE 
                              WHEN [Rate] LIKE '%USD%' THEN TRY_CAST(REPLACE(REPLACE(REPLACE([Rate], 'USD', ''), ' ', ''), ',', '') AS DECIMAL(19,4))
                              WHEN [Rate] LIKE '%EUR%' THEN TRY_CAST(REPLACE(REPLACE(REPLACE([Rate], 'EUR', ''), ' ', ''), ',', '') AS DECIMAL(19,4))
                              WHEN [Rate] LIKE '%ILS%' THEN TRY_CAST(REPLACE(REPLACE(REPLACE([Rate], 'ILS', ''), ' ', ''), ',', '') AS DECIMAL(19,4))
                              ELSE NULL
                            END,
                Currency = COALESCE(
                            CASE 
                              WHEN [Rate] LIKE '%USD%' THEN 'USD'
                              WHEN [Rate] LIKE '%EUR%' THEN 'EUR'
                              WHEN [Rate] LIKE '%ILS%' THEN 'ILS'
                              ELSE [Currency]
                            END, 'USD'),
                Incoterms = [Incoterms],
                Mode = LOWER([Mode]),
                OriginCountry = UPPER([Origin Country]),
                DestCountry = UPPER([Dest Country]),
                Category = [Category],
                EffFrom = TRY_CONVERT(date, [Effective From], 103), -- DD/MM/YYYY format
                EffTo = TRY_CONVERT(date, [Effective To], 103)
            FROM stg.CommissionRatesRaw
            WHERE [Commission ID] IS NOT NULL OR ([Buyer Company] IS NOT NULL AND [Supplier] IS NOT NULL)
        )
        MERGE fdx.CommissionRates AS target
        USING NormalizedRates AS source
        ON target.Name = source.Name 
           AND target.EffectiveFrom = COALESCE(source.EffFrom, CONVERT(date, SYSUTCDATETIME()))
        WHEN NOT MATCHED THEN
            INSERT (Name, Payer, Basis, RatePct, FlatAmount, Currency, Incoterms, Mode, 
                   OriginCountry, DestCountry, EffectiveFrom, EffectiveTo, Priority, IsActive)
            VALUES (source.Name, source.Payer, source.Basis, 
                   COALESCE(source.RatePct, 0), source.FlatAmount, source.Currency, 
                   source.Incoterms, source.Mode, source.OriginCountry, source.DestCountry,
                   COALESCE(source.EffFrom, CONVERT(date, SYSUTCDATETIME())), 
                   source.EffTo, 100, 1)
        WHEN MATCHED THEN
            UPDATE SET
                Payer = source.Payer,
                Basis = source.Basis,
                RatePct = COALESCE(source.RatePct, target.RatePct),
                FlatAmount = COALESCE(source.FlatAmount, target.FlatAmount),
                Currency = source.Currency,
                EffectiveTo = source.EffTo;

        COMMIT TRANSACTION;
        
        SELECT @@ROWCOUNT AS RecordsProcessed;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- Normalize Invoices from staging to production
CREATE OR ALTER PROCEDURE stg.usp_NormalizeInvoices
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- First ensure external orgs exist for any forwarders/customs agents
        INSERT INTO fdx.ExternalOrgs (Name, Type)
        SELECT DISTINCT [Counterparty Name/Id], 'external_org'
        FROM stg.InvoicesRaw
        WHERE [Counterparty Type] = 'external_org'
          AND [Counterparty Name/Id] IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM fdx.ExternalOrgs 
              WHERE Name = [Counterparty Name/Id]
          );

        -- Insert new invoices
        INSERT INTO fdx.Invoices (
            Type, OrderId, ShipmentId, CounterpartyType, CounterpartyId, 
            InvoiceCode, IssueDate, DueDate, Currency, Subtotal, TaxAmount, Status, ExternalRef
        )
        SELECT
            COALESCE(r.[Type], 'AR'),
            o.OrderId,
            TRY_CAST(r.[Shipment Id] AS UNIQUEIDENTIFIER),
            COALESCE(r.[Counterparty Type], 'buyer'),
            CASE 
                WHEN r.[Counterparty Type] = 'external_org' THEN eo.ExternalOrgId
                WHEN r.[Counterparty Type] = 'supplier' THEN o.SupplierId
                ELSE o.BuyerUserId
            END,
            COALESCE(r.[Invoice ID/ Name (From Files)], r.[Invoice ID]),
            TRY_CONVERT(date, r.[Issue Date], 103),
            TRY_CONVERT(date, r.[Due Date], 103),
            COALESCE(r.[Currency], 'USD'),
            ISNULL(TRY_CAST(REPLACE(REPLACE(r.[Subtotal], ',', ''), ' ', '') AS DECIMAL(19,4)), 0),
            ISNULL(TRY_CAST(REPLACE(REPLACE(r.[Tax], ',', ''), ' ', '') AS DECIMAL(19,4)), 0),
            COALESCE(r.[Status], 'issued'),
            r.[Invoice ID]
        FROM stg.InvoicesRaw r
        LEFT JOIN fdx.Orders o ON o.OrderCode = r.[Order Code]
        LEFT JOIN fdx.ExternalOrgs eo ON eo.Name = r.[Counterparty Name/Id]
        WHERE r.[Invoice ID] IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM fdx.Invoices i 
              WHERE i.InvoiceCode = COALESCE(r.[Invoice ID/ Name (From Files)], r.[Invoice ID])
          );

        COMMIT TRANSACTION;
        
        SELECT @@ROWCOUNT AS RecordsProcessed;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- Create AP invoices from Shipping data
CREATE OR ALTER PROCEDURE stg.usp_CreateAPFromShipping
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Ensure external orgs exist
        INSERT INTO fdx.ExternalOrgs (Name, Type)
        SELECT DISTINCT Name, Type
        FROM (
            SELECT [Forwarder] AS Name, 'forwarder' AS Type FROM stg.ShippingRaw WHERE [Forwarder] IS NOT NULL
            UNION
            SELECT [Customs Agent], 'customs_agent' FROM stg.ShippingRaw WHERE [Customs Agent] IS NOT NULL
        ) AS orgs
        WHERE NOT EXISTS (
            SELECT 1 FROM fdx.ExternalOrgs eo WHERE eo.Name = orgs.Name
        );

        -- Create AP invoices from shipping records
        INSERT INTO fdx.Invoices (
            Type, ShipmentId, CounterpartyType, CounterpartyId, 
            InvoiceCode, IssueDate, Currency, Subtotal, Status, ExternalRef
        )
        SELECT 
            'AP',
            TRY_CAST(r.[Shipment Id] AS UNIQUEIDENTIFIER),
            'external_org',
            eo.ExternalOrgId,
            COALESCE(r.[Invoice No], CONCAT('AP-SHIP-', r.[Shipping ID])),
            TRY_CONVERT(date, r.[Arrival Date], 103),
            COALESCE(r.[Invoice Currency], 'USD'),
            ISNULL(TRY_CAST(REPLACE(REPLACE(r.[Invoice Amount], ',', ''), ' ', '') AS DECIMAL(19,4)), 0),
            'issued',
            r.[Invoice No]
        FROM stg.ShippingRaw r
        LEFT JOIN fdx.ExternalOrgs eo ON eo.Name = COALESCE(r.[Forwarder], r.[Customs Agent])
        WHERE r.[Invoice No] IS NOT NULL
          AND eo.ExternalOrgId IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM fdx.Invoices i 
              WHERE i.InvoiceCode = COALESCE(r.[Invoice No], CONCAT('AP-SHIP-', r.[Shipping ID]))
          );

        -- Add invoice lines for AP invoices
        INSERT INTO fdx.InvoiceLines (
            InvoiceId, Kind, Description, Quantity, UnitPrice
        )
        SELECT
            i.InvoiceId,
            COALESCE(r.[Kind], 'freight'),
            CONCAT(
                CASE r.[Kind]
                    WHEN 'freight' THEN 'Freight charges - '
                    WHEN 'customs' THEN 'Customs clearance - '
                    WHEN 'insurance' THEN 'Insurance - '
                    ELSE 'Logistics service - '
                END,
                r.[Shipping ID]
            ),
            1,
            i.Subtotal
        FROM stg.ShippingRaw r
        INNER JOIN fdx.Invoices i ON i.ExternalRef = r.[Invoice No]
        WHERE NOT EXISTS (
            SELECT 1 FROM fdx.InvoiceLines il WHERE il.InvoiceId = i.InvoiceId
        );

        COMMIT TRANSACTION;
        
        SELECT @@ROWCOUNT AS RecordsProcessed;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =====================================================
-- Auto-accrue commissions trigger
-- =====================================================
CREATE OR ALTER TRIGGER fdx.tr_ShipmentMilestone_AccrueCommission
ON fdx.ShipmentMilestones
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM inserted WHERE Code IN ('ARRIVED','CUSTOMS_CLEARED')) 
        RETURN;

    DECLARE @tbl TABLE (ShipmentId UNIQUEIDENTIFIER, Code NVARCHAR(40));
    INSERT INTO @tbl 
    SELECT ShipmentId, Code 
    FROM inserted 
    WHERE Code IN ('ARRIVED','CUSTOMS_CLEARED');

    DECLARE @ShipmentId UNIQUEIDENTIFIER, @Code NVARCHAR(40);
    DECLARE cur CURSOR LOCAL FAST_FORWARD FOR 
        SELECT ShipmentId, Code FROM @tbl;
    
    OPEN cur; 
    FETCH NEXT FROM cur INTO @ShipmentId, @Code;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Idempotency: skip if any accrual already exists for this shipment
        IF NOT EXISTS (SELECT 1 FROM fdx.CommissionAccruals WHERE ShipmentId = @ShipmentId AND Status != 'cancelled')
        BEGIN
            EXEC fdx.usp_Commission_Accrue_OnShipment @ShipmentId, @Code;
        END

        FETCH NEXT FROM cur INTO @ShipmentId, @Code;
    END
    
    CLOSE cur; 
    DEALLOCATE cur;
END
GO

-- =====================================================
-- P&L View for Orders
-- =====================================================
CREATE OR ALTER VIEW fdx.vw_OrderPnL AS
SELECT
    o.OrderId,
    o.OrderCode,
    o.Currency,
    o.Status AS OrderStatus,
    o.TotalAmount AS OrderValue,
    AR_Total = COALESCE(
        (SELECT SUM(Subtotal + TaxAmount) 
         FROM fdx.Invoices i 
         WHERE i.OrderId = o.OrderId 
           AND i.Type = 'AR' 
           AND i.Status != 'cancelled'), 0),
    AP_Total = COALESCE(
        (SELECT SUM(Subtotal + TaxAmount) 
         FROM fdx.Invoices i 
         WHERE i.OrderId = o.OrderId 
           AND i.Type = 'AP' 
           AND i.Status != 'cancelled'), 0),
    CommissionAccrued = COALESCE(
        (SELECT SUM(CalculatedAmount) 
         FROM fdx.CommissionAccruals a 
         WHERE a.OrderId = o.OrderId 
           AND a.Status != 'cancelled'), 0),
    Net = COALESCE(
        (SELECT SUM(Subtotal + TaxAmount) 
         FROM fdx.Invoices i 
         WHERE i.OrderId = o.OrderId 
           AND i.Type = 'AR' 
           AND i.Status != 'cancelled'), 0)
        - COALESCE(
        (SELECT SUM(Subtotal + TaxAmount) 
         FROM fdx.Invoices i 
         WHERE i.OrderId = o.OrderId 
           AND i.Type = 'AP' 
           AND i.Status != 'cancelled'), 0)
FROM fdx.Orders o;
GO

PRINT 'Finance staging tables and procedures created successfully!';
GO