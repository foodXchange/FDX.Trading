-- =====================================================
-- FoodXchange Order Module Stored Procedures
-- Includes compliance gating, commission accrual, invoicing
-- =====================================================

USE fdxdb;
GO

-- =====================================================
-- CREATE ORDER FROM CONTRACT (WITH COMPLIANCE GATE)
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Order_CreateFromContract
    @ContractId UNIQUEIDENTIFIER,
    @BuyerUserId UNIQUEIDENTIFIER = NULL,
    @OrderCode NVARCHAR(60) = NULL,
    @RequestedDelivery DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Gate check: Compliance must be approved
        IF NOT EXISTS (
            SELECT 1 FROM fdx.ComplianceProcesses p 
            WHERE p.ContractId = @ContractId AND p.Status = 'approved'
        ) 
        BEGIN
            THROW 50020, 'Cannot create order: Compliance not approved for this contract', 1;
        END

        -- Get contract details (assuming contract tables exist)
        DECLARE @ProjectId UNIQUEIDENTIFIER;
        DECLARE @SupplierId UNIQUEIDENTIFIER;
        DECLARE @Currency CHAR(3) = 'USD';
        DECLARE @Incoterms NVARCHAR(10) = 'FOB';
        
        -- For now, use placeholder values (replace with actual contract lookup)
        SET @ProjectId = (SELECT TOP 1 ProjectId FROM fdx.ComplianceProcesses WHERE ContractId = @ContractId);
        SET @SupplierId = NEWID(); -- Replace with actual supplier lookup
        
        -- Generate order code if not provided
        IF @OrderCode IS NULL 
            SET @OrderCode = CONCAT('ORD-', FORMAT(GETUTCDATE(),'yyyy-MM-dd-'), 
                                    RIGHT('00000' + CAST(NEXT VALUE FOR fdx.OrderSequence AS VARCHAR(5)), 5));

        -- Create order header
        DECLARE @OrderId UNIQUEIDENTIFIER = NEWID();
        
        INSERT INTO fdx.Orders (
            OrderId, ProjectId, ContractId, BuyerUserId, SupplierId, 
            OrderCode, Status, Currency, Incoterms, RequestedDelivery
        )
        VALUES (
            @OrderId, @ProjectId, @ContractId, @BuyerUserId, @SupplierId,
            @OrderCode, 'placed', @Currency, @Incoterms, @RequestedDelivery
        );

        -- Copy contract lines to order lines (simplified - replace with actual contract line query)
        -- In production, this would copy from fdx.ContractLines
        INSERT INTO fdx.OrderLines (
            OrderId, ProductName, Unit, Quantity, UnitPrice, Currency, Incoterms, RequestedDelivery
        )
        SELECT 
            @OrderId,
            'Sample Product ' + CAST(ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS VARCHAR(10)),
            'KG',
            100,
            10.50,
            @Currency,
            @Incoterms,
            @RequestedDelivery
        FROM sys.objects -- Dummy source, replace with fdx.ContractLines
        WHERE object_id % 3 = 0 -- Just to get a few rows
        AND ROWNUM <= 5;

        -- Calculate order totals
        UPDATE fdx.Orders
        SET SubtotalAmount = (SELECT SUM(LineTotal) FROM fdx.OrderLines WHERE OrderId = @OrderId),
            TotalAmount = SubtotalAmount + ISNULL(FreightAmount, 0) + ISNULL(InsuranceAmount, 0) + ISNULL(TaxAmount, 0),
            UpdatedAt = SYSUTCDATETIME()
        WHERE OrderId = @OrderId;

        COMMIT TRANSACTION;
        
        -- Return the created order ID
        SELECT @OrderId AS OrderId, @OrderCode AS OrderCode;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- Create sequence for order numbers if not exists
IF NOT EXISTS (SELECT * FROM sys.sequences WHERE name = 'OrderSequence' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE SEQUENCE fdx.OrderSequence
        START WITH 1
        INCREMENT BY 1
        MINVALUE 1
        MAXVALUE 99999
        CYCLE;
END
GO

-- =====================================================
-- COMMISSION ACCRUAL ON SHIPMENT MILESTONE
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Commission_Accrue_OnShipment
    @ShipmentId UNIQUEIDENTIFIER,
    @Trigger NVARCHAR(40)  -- 'ARRIVED' | 'CUSTOMS_CLEARED'
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @OrderId UNIQUEIDENTIFIER = (SELECT OrderId FROM fdx.Shipments WHERE ShipmentId = @ShipmentId);
        
        -- Check if milestone exists
        IF NOT EXISTS(SELECT 1 FROM fdx.ShipmentMilestones WHERE ShipmentId = @ShipmentId AND Code = @Trigger)
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Check if already accrued for this shipment
        IF EXISTS(SELECT 1 FROM fdx.CommissionAccruals WHERE ShipmentId = @ShipmentId AND Status != 'cancelled')
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Get order details
        DECLARE @Currency CHAR(3) = (SELECT Currency FROM fdx.Orders WHERE OrderId = @OrderId);
        DECLARE @SupplierId UNIQUEIDENTIFIER = (SELECT SupplierId FROM fdx.Orders WHERE OrderId = @OrderId);
        DECLARE @Mode NVARCHAR(15) = (SELECT Mode FROM fdx.Shipments WHERE ShipmentId = @ShipmentId);

        -- Calculate base amount (sum of order lines)
        DECLARE @BaseAmount DECIMAL(19,4) = (
            SELECT SUM(ol.Quantity * ol.UnitPrice) 
            FROM fdx.OrderLines ol
            WHERE ol.OrderId = @OrderId
        );

        -- Find best matching commission rate
        DECLARE @RateId UNIQUEIDENTIFIER;
        DECLARE @RatePct DECIMAL(9,4);
        DECLARE @FlatAmount DECIMAL(19,4);
        DECLARE @MinFee DECIMAL(19,4);
        DECLARE @MaxFee DECIMAL(19,4);
        DECLARE @Payer NVARCHAR(20);

        SELECT TOP 1 
            @RateId = RateId,
            @RatePct = RatePct,
            @FlatAmount = FlatAmount,
            @MinFee = MinFee,
            @MaxFee = MaxFee,
            @Payer = Payer
        FROM fdx.CommissionRates
        WHERE IsActive = 1
            AND (EffectiveFrom <= CONVERT(date, SYSUTCDATETIME()))
            AND (EffectiveTo IS NULL OR EffectiveTo >= CONVERT(date, SYSUTCDATETIME()))
            AND (SupplierId IS NULL OR SupplierId = @SupplierId)
            AND (Mode IS NULL OR Mode = @Mode)
        ORDER BY 
            CASE WHEN SupplierId IS NOT NULL THEN 1 ELSE 2 END,  -- Specific supplier first
            CASE WHEN Mode IS NOT NULL THEN 1 ELSE 2 END,        -- Specific mode second
            Priority;

        -- If no rate found, exit
        IF @RateId IS NULL
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Calculate commission amount
        DECLARE @CalculatedAmount DECIMAL(19,4);
        
        IF @RatePct IS NOT NULL AND @RatePct > 0
            SET @CalculatedAmount = ROUND(@BaseAmount * (@RatePct / 100.0), 4);
        ELSE IF @FlatAmount IS NOT NULL
            SET @CalculatedAmount = @FlatAmount;
        ELSE
            SET @CalculatedAmount = 0;

        -- Apply min/max limits
        IF @MinFee IS NOT NULL AND @CalculatedAmount < @MinFee
            SET @CalculatedAmount = @MinFee;
        IF @MaxFee IS NOT NULL AND @CalculatedAmount > @MaxFee
            SET @CalculatedAmount = @MaxFee;

        -- Create accrual
        INSERT INTO fdx.CommissionAccruals (
            OrderId, ShipmentId, RateId, Basis, BaseAmount, Currency, CalculatedAmount, Status
        )
        VALUES (
            @OrderId, @ShipmentId, @RateId, 'order_value', @BaseAmount, @Currency, @CalculatedAmount, 'accrued'
        );

        COMMIT TRANSACTION;
        
        SELECT @CalculatedAmount AS AccruedAmount, @Payer AS Payer;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =====================================================
-- GENERATE COMMISSION INVOICE FROM ACCRUALS
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Commission_IssueInvoice_ForOrder
    @OrderId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;

        -- Check for non-invoiced accruals
        IF NOT EXISTS (SELECT 1 FROM fdx.CommissionAccruals WHERE OrderId = @OrderId AND Status = 'accrued')
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END

        DECLARE @OrderCurrency CHAR(3) = (SELECT Currency FROM fdx.Orders WHERE OrderId = @OrderId);
        DECLARE @SupplierId UNIQUEIDENTIFIER = (SELECT SupplierId FROM fdx.Orders WHERE OrderId = @OrderId);
        DECLARE @OrderCode NVARCHAR(60) = (SELECT OrderCode FROM fdx.Orders WHERE OrderId = @OrderId);

        -- Determine payer from first accrual's rate
        DECLARE @Payer NVARCHAR(20) = (
            SELECT TOP 1 r.Payer
            FROM fdx.CommissionAccruals a 
            JOIN fdx.CommissionRates r ON r.RateId = a.RateId
            WHERE a.OrderId = @OrderId AND a.Status = 'accrued'
            ORDER BY a.AccruedAt
        );

        -- Set invoice type and counterparty
        DECLARE @Type NVARCHAR(2);
        DECLARE @CounterpartyType NVARCHAR(20);
        DECLARE @CounterpartyId UNIQUEIDENTIFIER;
        
        IF @Payer = 'supplier'
        BEGIN 
            SET @Type = 'AR'; 
            SET @CounterpartyType = 'supplier'; 
            SET @CounterpartyId = @SupplierId; 
        END
        ELSE 
        BEGIN 
            SET @Type = 'AR'; 
            SET @CounterpartyType = 'buyer'; 
            SET @CounterpartyId = (SELECT BuyerUserId FROM fdx.Orders WHERE OrderId = @OrderId); 
        END

        -- Generate invoice code
        DECLARE @InvoiceCode NVARCHAR(60) = CONCAT('INV-COM-', @OrderCode, '-', FORMAT(GETUTCDATE(),'yyyyMMdd'));

        -- Create invoice header
        DECLARE @InvoiceId UNIQUEIDENTIFIER = NEWID();
        
        INSERT INTO fdx.Invoices (
            InvoiceId, Type, OrderId, CounterpartyType, CounterpartyId, 
            InvoiceCode, Currency, Status, IssueDate
        )
        VALUES (
            @InvoiceId, @Type, @OrderId, @CounterpartyType, @CounterpartyId,
            @InvoiceCode, @OrderCurrency, 'issued', CONVERT(date, SYSUTCDATETIME())
        );

        -- Create invoice lines from accruals
        INSERT INTO fdx.InvoiceLines (
            InvoiceId, Kind, Description, Quantity, UnitPrice
        )
        SELECT 
            @InvoiceId, 
            'commission', 
            CONCAT('Commission for shipment ', s.ShipmentCode),
            1, 
            a.CalculatedAmount
        FROM fdx.CommissionAccruals a
        JOIN fdx.Shipments s ON s.ShipmentId = a.ShipmentId
        WHERE a.OrderId = @OrderId AND a.Status = 'accrued';

        -- Update invoice total
        UPDATE fdx.Invoices
        SET Subtotal = (SELECT SUM(Amount) FROM fdx.InvoiceLines WHERE InvoiceId = @InvoiceId),
            UpdatedAt = SYSUTCDATETIME()
        WHERE InvoiceId = @InvoiceId;

        -- Mark accruals as invoiced
        UPDATE fdx.CommissionAccruals 
        SET Status = 'invoiced', 
            InvoiceId = @InvoiceId
        WHERE OrderId = @OrderId AND Status = 'accrued';

        COMMIT TRANSACTION;
        
        SELECT @InvoiceId AS InvoiceId, @InvoiceCode AS InvoiceCode;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- =====================================================
-- ADD SHIPMENT MILESTONE
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Shipment_AddMilestone
    @ShipmentId UNIQUEIDENTIFIER,
    @Code NVARCHAR(40),
    @OccurredAt DATETIMEOFFSET = NULL,
    @Location NVARCHAR(120) = NULL,
    @Notes NVARCHAR(400) = NULL,
    @CreatedBy UNIQUEIDENTIFIER = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        IF @OccurredAt IS NULL
            SET @OccurredAt = SYSUTCDATETIME();

        INSERT INTO fdx.ShipmentMilestones (
            ShipmentId, Code, OccurredAt, Location, Notes, CreatedBy
        )
        VALUES (
            @ShipmentId, @Code, @OccurredAt, @Location, @Notes, @CreatedBy
        );

        -- Update shipment status based on milestone
        DECLARE @NewStatus NVARCHAR(30);
        
        SET @NewStatus = CASE @Code
            WHEN 'BOOKED' THEN 'booked'
            WHEN 'DEPARTED' THEN 'in_transit'
            WHEN 'ARRIVED' THEN 'arrived'
            WHEN 'CUSTOMS_CLEARED' THEN 'customs_cleared'
            WHEN 'DELIVERED' THEN 'delivered'
            ELSE NULL
        END;

        IF @NewStatus IS NOT NULL
        BEGIN
            UPDATE fdx.Shipments
            SET Status = @NewStatus,
                UpdatedAt = SYSUTCDATETIME()
            WHERE ShipmentId = @ShipmentId;
        END

        -- Trigger commission accrual if applicable
        IF @Code IN ('ARRIVED', 'CUSTOMS_CLEARED')
        BEGIN
            EXEC fdx.usp_Commission_Accrue_OnShipment @ShipmentId, @Code;
        END
        
        SELECT 'Success' AS Result;
        
    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END
GO

-- =====================================================
-- UPDATE ORDER STATUS
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Order_UpdateStatus
    @OrderId UNIQUEIDENTIFIER,
    @NewStatus NVARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Validate status transition (simplified)
    DECLARE @CurrentStatus NVARCHAR(30) = (SELECT Status FROM fdx.Orders WHERE OrderId = @OrderId);
    
    -- Basic validation rules
    IF @CurrentStatus = 'closed' AND @NewStatus != 'closed'
    BEGIN
        THROW 50021, 'Cannot change status of a closed order', 1;
    END
    
    IF @CurrentStatus = 'cancelled'
    BEGIN
        THROW 50022, 'Cannot change status of a cancelled order', 1;
    END
    
    UPDATE fdx.Orders
    SET Status = @NewStatus,
        UpdatedAt = SYSUTCDATETIME()
    WHERE OrderId = @OrderId;
    
    SELECT 'Success' AS Result;
END
GO

PRINT 'Order module stored procedures created successfully!';
GO