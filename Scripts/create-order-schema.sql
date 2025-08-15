-- =====================================================
-- FoodXchange Order Module Schema
-- Orders can only be created after Compliance approval
-- Includes shipping, commission, and invoicing
-- =====================================================

USE fdxdb;
GO

-- =====================================================
-- SECTION 1: CORE ORDER TABLES
-- =====================================================

-- Orders (Header)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Orders' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Orders (
        OrderId            UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ProjectId          UNIQUEIDENTIFIER NOT NULL,
        ContractId         UNIQUEIDENTIFIER NOT NULL,
        BuyerUserId        UNIQUEIDENTIFIER NULL,        -- who placed the order
        SupplierId         UNIQUEIDENTIFIER NOT NULL,

        OrderCode          NVARCHAR(60) NOT NULL,        -- human-readable (e.g., ORD-2025-00123)
        Status             NVARCHAR(30) NOT NULL DEFAULT 'draft',  
        -- draft/placed/confirmed/ready_to_ship/shipped/in_transit/arrived/customs_cleared/delivered/closed/cancelled

        Currency           CHAR(3) NOT NULL,
        Incoterms          NVARCHAR(10) NOT NULL,        -- FOB/CIF/DAP/etc.
        DestinationCountry CHAR(2) NULL,                 -- buyer country/delivery country
        RequestedDelivery  DATE NULL,                    -- from CSV "Requested Delivery Date"

        SubtotalAmount     DECIMAL(19,4) NULL,
        FreightAmount      DECIMAL(19,4) NULL,
        InsuranceAmount    DECIMAL(19,4) NULL,
        TaxAmount          DECIMAL(19,4) NULL,
        TotalAmount        DECIMAL(19,4) NULL,

        OpenComments       NVARCHAR(MAX) NULL,           -- CSV: Open Comments
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_Orders_OrderCode ON fdx.Orders(OrderCode);
    CREATE INDEX IX_Orders_Contract ON fdx.Orders(ContractId);
    CREATE INDEX IX_Orders_Status ON fdx.Orders(Status);
    CREATE INDEX IX_Orders_Supplier ON fdx.Orders(SupplierId);
END
GO

-- Order Lines (derived from ContractLines, can be partial)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OrderLines' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.OrderLines (
        OrderLineId        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        OrderId            UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Orders(OrderId),
        ContractLineId     UNIQUEIDENTIFIER NULL,

        ProductId          UNIQUEIDENTIFIER NULL,
        ProductName        NVARCHAR(300) NOT NULL,
        Unit               NVARCHAR(20) NOT NULL,
        Quantity           DECIMAL(18,3) NOT NULL,       -- ordered quantity (can be <= contract)
        UnitPrice          DECIMAL(19,4) NOT NULL,       -- price snapshot from contract
        Currency           CHAR(3) NOT NULL,
        Incoterms          NVARCHAR(10) NOT NULL,

        RequestedDelivery  DATE NULL,                    -- per-line delivery date
        Notes              NVARCHAR(800) NULL,

        LineTotal          AS (ROUND(ISNULL(Quantity,0) * ISNULL(UnitPrice,0), 4)) PERSISTED,
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_OrderLines_Order ON fdx.OrderLines(OrderId);
    CREATE INDEX IX_OrderLines_Product ON fdx.OrderLines(ProductId);
END
GO

-- Order Participants (internal & external roles)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OrderParticipants' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.OrderParticipants (
        OrderParticipantId  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        OrderId             UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Orders(OrderId),
        Role                NVARCHAR(40) NOT NULL,   -- 'import_manager','forwarder','customs_agent','insurer','warehouse'
        UserId              UNIQUEIDENTIFIER NULL,   -- internal employee
        ExternalUserId      UNIQUEIDENTIFIER NULL,   -- from fdx.ExternalUsers
        AssignedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_OrderParticipants UNIQUE (
            OrderId, 
            Role, 
            COALESCE(UserId, '00000000-0000-0000-0000-000000000000'), 
            COALESCE(ExternalUserId, '00000000-0000-0000-0000-000000000000')
        )
    );
    CREATE INDEX IX_OrderParticipants_Order ON fdx.OrderParticipants(OrderId);
END
GO

-- =====================================================
-- SECTION 2: SHIPPING & LOGISTICS
-- =====================================================

-- Shipments (an order may have multiple shipments)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Shipments' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Shipments (
        ShipmentId          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        OrderId             UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Orders(OrderId),
        ShipmentCode        NVARCHAR(60) NOT NULL,
        Mode                NVARCHAR(15) NOT NULL,       -- 'sea','air','road','rail'
        TermsLocation       NVARCHAR(120) NULL,          -- Incoterm point (e.g., FOB Shanghai)
        Carrier             NVARCHAR(200) NULL,
        VesselVoyage        NVARCHAR(200) NULL,          -- sea
        AWB                 NVARCHAR(60)  NULL,          -- air waybill
        BL                  NVARCHAR(60)  NULL,          -- bill of lading
        ETD                 DATETIMEOFFSET NULL,         -- estimated time of departure
        ETA                 DATETIMEOFFSET NULL,         -- estimated time of arrival
        ATD                 DATETIMEOFFSET NULL,         -- actual time of departure
        ATA                 DATETIMEOFFSET NULL,         -- actual time of arrival
        Status              NVARCHAR(30) NOT NULL DEFAULT 'planning',  
        -- planning/booked/departed/in_transit/arrived/customs_cleared/delivered
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_Shipments_Order ON fdx.Shipments(OrderId, Status);
    CREATE UNIQUE INDEX UX_Shipments_Code ON fdx.Shipments(ShipmentCode);
END
GO

-- Containers/Packages
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Containers' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Containers (
        ContainerId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ShipmentId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Shipments(ShipmentId),
        ContainerType       NVARCHAR(50) NOT NULL,       -- 20GP/40HC/LCL/Pallet
        ContainerNumber     NVARCHAR(20) NULL,
        SealNumber          NVARCHAR(30) NULL,
        GrossWeightKg       DECIMAL(18,3) NULL,
        NetWeightKg         DECIMAL(18,3) NULL,
        VolumeM3            DECIMAL(18,3) NULL,
        Pallets             INT NULL,
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_Containers_Shipment ON fdx.Containers(ShipmentId);
END
GO

-- Shipment line allocations (how order lines are packed)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ShipmentLineAllocations' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ShipmentLineAllocations (
        AllocationId        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ShipmentId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Shipments(ShipmentId),
        OrderLineId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.OrderLines(OrderLineId),
        ContainerId         UNIQUEIDENTIFIER NULL REFERENCES fdx.Containers(ContainerId),
        Quantity            DECIMAL(18,3) NOT NULL,
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ShipmentLineAllocations_Shipment ON fdx.ShipmentLineAllocations(ShipmentId);
    CREATE INDEX IX_ShipmentLineAllocations_OrderLine ON fdx.ShipmentLineAllocations(OrderLineId);
END
GO

-- Trade & logistics documents
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ShipmentDocuments' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ShipmentDocuments (
        ShipmentDocumentId  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ShipmentId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Shipments(ShipmentId),
        DocType             NVARCHAR(40) NOT NULL,    
        -- 'proforma_invoice','commercial_invoice','packing_list','coo','health_cert','kosher_cert','insurance','bl','awb'
        BlobUri             NVARCHAR(800) NOT NULL,
        FileName            NVARCHAR(300) NOT NULL,
        UploadedBy          UNIQUEIDENTIFIER NULL,
        UploadedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ShipmentDocuments_Shipment ON fdx.ShipmentDocuments(ShipmentId);
    CREATE INDEX IX_ShipmentDocuments_Type ON fdx.ShipmentDocuments(DocType);
END
GO

-- Milestones / tracking events
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ShipmentMilestones' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ShipmentMilestones (
        MilestoneId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ShipmentId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Shipments(ShipmentId),
        Code                NVARCHAR(40) NOT NULL,  
        -- 'BOOKED','ETD_CONFIRMED','DEPARTED','IN_TRANSIT','ARRIVED','CUSTOMS_CLEARED','DELIVERED'
        OccurredAt          DATETIMEOFFSET NOT NULL,
        Location            NVARCHAR(120) NULL,
        Notes               NVARCHAR(400) NULL,
        CreatedBy           UNIQUEIDENTIFIER NULL,
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ShipmentMilestones_Shipment ON fdx.ShipmentMilestones(ShipmentId, OccurredAt DESC);
    CREATE INDEX IX_ShipmentMilestones_Code ON fdx.ShipmentMilestones(Code);
END
GO

-- =====================================================
-- SECTION 3: COMMISSION & FINANCE
-- =====================================================

-- Commission rate configuration
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CommissionRates' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.CommissionRates (
        RateId             UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name               NVARCHAR(200) NOT NULL,
        Payer              NVARCHAR(20) NOT NULL,        -- 'supplier' | 'buyer'
        Basis              NVARCHAR(20) NOT NULL,        -- 'order_value' | 'line_value' | 'freight_value'
        RatePct            DECIMAL(9,4) NULL,            -- percentage (e.g., 3.50)
        FlatAmount         DECIMAL(19,4) NULL,           -- if flat fee
        Currency           CHAR(3) NULL,                 -- currency for flat/min/max
        MinFee             DECIMAL(19,4) NULL,
        MaxFee             DECIMAL(19,4) NULL,

        -- Matching dimensions (nullable = wildcard)
        BuyerCompanyId     UNIQUEIDENTIFIER NULL,
        SupplierId         UNIQUEIDENTIFIER NULL,
        ProductCategoryId  UNIQUEIDENTIFIER NULL,
        Mode               NVARCHAR(15) NULL,            -- sea/air/road/rail
        OriginCountry      CHAR(2) NULL,
        DestCountry        CHAR(2) NULL,
        Incoterms          NVARCHAR(10) NULL,

        EffectiveFrom      DATE NOT NULL DEFAULT CONVERT(date, SYSUTCDATETIME()),
        EffectiveTo        DATE NULL,
        Priority           INT NOT NULL DEFAULT 100,     -- lower wins when multiple match
        IsActive           BIT NOT NULL DEFAULT 1,
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_CommissionRates_Match ON fdx.CommissionRates(
        BuyerCompanyId, SupplierId, ProductCategoryId, Mode, 
        OriginCountry, DestCountry, Incoterms, 
        EffectiveFrom, EffectiveTo, Priority
    );
END
GO

-- Commission accruals
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CommissionAccruals' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.CommissionAccruals (
        AccrualId          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        OrderId            UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Orders(OrderId),
        ShipmentId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Shipments(ShipmentId),
        OrderLineId        UNIQUEIDENTIFIER NULL REFERENCES fdx.OrderLines(OrderLineId),

        RateId             UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.CommissionRates(RateId),
        Basis              NVARCHAR(20) NOT NULL,
        BaseAmount         DECIMAL(19,4) NOT NULL,
        Currency           CHAR(3) NOT NULL,
        CalculatedAmount   DECIMAL(19,4) NOT NULL,

        Status             NVARCHAR(20) NOT NULL DEFAULT 'accrued',  -- accrued | invoiced | cancelled
        AccruedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        InvoiceId          UNIQUEIDENTIFIER NULL
    );
    CREATE INDEX IX_CommissionAccruals_OrderShipment ON fdx.CommissionAccruals(OrderId, ShipmentId, Status);
    CREATE INDEX IX_CommissionAccruals_Status ON fdx.CommissionAccruals(Status);
END
GO

-- Invoices (AR/AP)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Invoices' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Invoices (
        InvoiceId          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Type               NVARCHAR(2) NOT NULL,         -- 'AR' or 'AP'
        OrderId            UNIQUEIDENTIFIER NULL REFERENCES fdx.Orders(OrderId),
        ShipmentId         UNIQUEIDENTIFIER NULL REFERENCES fdx.Shipments(ShipmentId),

        -- counterparty
        CounterpartyType   NVARCHAR(20) NOT NULL,        -- 'buyer' | 'supplier' | 'external_org'
        CounterpartyId     UNIQUEIDENTIFIER NOT NULL,

        InvoiceCode        NVARCHAR(60) NOT NULL,        -- human-readable
        IssueDate          DATE NOT NULL DEFAULT CONVERT(date, SYSUTCDATETIME()),
        DueDate            DATE NULL,
        Currency           CHAR(3) NOT NULL,

        Subtotal           DECIMAL(19,4) NOT NULL DEFAULT 0,
        TaxAmount          DECIMAL(19,4) NOT NULL DEFAULT 0,
        Total              AS (ROUND(Subtotal + TaxAmount, 4)) PERSISTED,

        Status             NVARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft/issued/paid/cancelled
        ExternalRef        NVARCHAR(120) NULL,           -- e.g., forwarder invoice #
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_Invoices_Type_Order ON fdx.Invoices(Type, OrderId, Status);
    CREATE UNIQUE INDEX UX_Invoices_Code ON fdx.Invoices(InvoiceCode);
END
GO

-- Invoice line items
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'InvoiceLines' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.InvoiceLines (
        InvoiceLineId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        InvoiceId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Invoices(InvoiceId),
        Kind               NVARCHAR(20) NOT NULL,        
        -- 'commission' | 'product' | 'freight' | 'customs' | 'service' | 'insurance'
        Description        NVARCHAR(300) NOT NULL,
        Quantity           DECIMAL(18,3) NOT NULL DEFAULT 1,
        UnitPrice          DECIMAL(19,4) NOT NULL,
        Amount             AS (ROUND(Quantity * UnitPrice, 4)) PERSISTED,
        TaxPct             DECIMAL(7,4) NULL,
        ProductCategoryId  UNIQUEIDENTIFIER NULL,
        OrderLineId        UNIQUEIDENTIFIER NULL,
        ShipmentId         UNIQUEIDENTIFIER NULL,
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_InvoiceLines_Invoice ON fdx.InvoiceLines(InvoiceId);
END
GO

-- Payment records
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Payments' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Payments (
        PaymentId          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        InvoiceId          UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Invoices(InvoiceId),
        PaidAt             DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        Currency           CHAR(3) NOT NULL,
        Amount             DECIMAL(19,4) NOT NULL,
        Method             NVARCHAR(30) NULL,            -- wire/creditnote/etc.
        Reference          NVARCHAR(120) NULL,
        CreatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_Payments_Invoice ON fdx.Payments(InvoiceId);
END
GO

-- Order payment terms (optional)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OrderPaymentTerms' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.OrderPaymentTerms (
        OrderPaymentTermId  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        OrderId             UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Orders(OrderId),
        TermCode            NVARCHAR(40) NOT NULL,       -- e.g., '30%_DEPOSIT','70%_BALANCE'
        Currency            CHAR(3) NOT NULL,
        Amount              DECIMAL(19,4) NOT NULL,
        DueDate             DATE NULL,
        Status              NVARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/paid/overdue
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_OrderPaymentTerms_Order ON fdx.OrderPaymentTerms(OrderId);
END
GO

-- FX Rates (for cross-currency calculations)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FxRates' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.FxRates (
        RateDate   DATE NOT NULL,
        FromCcy    CHAR(3) NOT NULL,
        ToCcy      CHAR(3) NOT NULL,
        Rate       DECIMAL(18,8) NOT NULL,
        Source     NVARCHAR(50) NULL,
        CreatedAt  DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        PRIMARY KEY (RateDate, FromCcy, ToCcy)
    );
END
GO

PRINT 'Order module schema created successfully!';
GO