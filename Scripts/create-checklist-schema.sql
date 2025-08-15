-- =====================================================
-- FoodXchange Compliance Checklist System
-- First-class checklist for trackable compliance items
-- =====================================================

USE fdxdb;
GO

-- =====================================================
-- 1) CHECKLIST TEMPLATES
-- =====================================================

-- Template container per step template (e.g., LBL_CLAIMS_CHECK)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ChecklistTemplates' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ChecklistTemplates (
        ChecklistTemplateId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StepTemplateId      UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceStepTemplates(StepTemplateId),
        Title               NVARCHAR(200) NOT NULL,
        IsActive            BIT NOT NULL DEFAULT 1,
        CreatedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ChecklistTemplates_StepTemplate ON fdx.ChecklistTemplates(StepTemplateId);
END
GO

-- Template items
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ChecklistTemplateItems' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ChecklistTemplateItems (
        ChecklistTemplateItemId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ChecklistTemplateId     UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ChecklistTemplates(ChecklistTemplateId),
        ItemCode                NVARCHAR(80) NOT NULL,   -- e.g., LBL_ALLERGENS
        Title                   NVARCHAR(300) NOT NULL,
        Required                BIT NOT NULL DEFAULT 1,
        DefaultAssigneeRole     NVARCHAR(40) NULL,       -- e.g., 'agency_pm', 'buyer_qa_manager'
        SortOrder               INT NOT NULL DEFAULT 0,
        CreatedAt               DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_ChecklistTemplateItems_Code UNIQUE (ChecklistTemplateId, ItemCode)
    );
    CREATE INDEX IX_ChecklistTemplateItems_Template ON fdx.ChecklistTemplateItems(ChecklistTemplateId);
END
GO

-- =====================================================
-- 2) CHECKLIST INSTANCES
-- =====================================================

-- One checklist per step (when EvidenceType='checklist')
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceChecklists' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceChecklists (
        ChecklistId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StepId           UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceSteps(StepId),
        Title            NVARCHAR(200) NOT NULL,
        Status           NVARCHAR(20) NOT NULL DEFAULT 'open',  -- open/in-review/done/blocked
        CreatedAt        DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt        DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE UNIQUE INDEX UX_ComplianceChecklists_Step ON fdx.ComplianceChecklists(StepId);
    CREATE INDEX IX_ComplianceChecklists_Status ON fdx.ComplianceChecklists(Status);
END
GO

-- Checklist items
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceChecklistItems' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceChecklistItems (
        ItemId           UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ChecklistId      UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceChecklists(ChecklistId),
        ItemCode         NVARCHAR(80) NULL,
        Title            NVARCHAR(300) NOT NULL,
        Required         BIT NOT NULL DEFAULT 1,
        Status           NVARCHAR(15) NOT NULL DEFAULT 'open',  -- open/done/na/blocked
        AssignedToUserId UNIQUEIDENTIFIER NULL,
        AssignedToExternalId UNIQUEIDENTIFIER NULL,
        DueDate          DATE NULL,
        Notes            NVARCHAR(800) NULL,
        SortOrder        INT NOT NULL DEFAULT 0,
        CreatedAt        DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt        DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ChecklistItems_Checklist_Status ON fdx.ComplianceChecklistItems(ChecklistId, Status);
    CREATE INDEX IX_ChecklistItems_AssignedUser ON fdx.ComplianceChecklistItems(AssignedToUserId);
    CREATE INDEX IX_ChecklistItems_DueDate ON fdx.ComplianceChecklistItems(DueDate);
END
GO

-- =====================================================
-- 3) EVIDENCE LINK TO CHECKLIST ITEMS
-- =====================================================

-- Add ChecklistItemId to existing ComplianceEvidence table
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('fdx.ComplianceEvidence') AND name = 'ChecklistItemId')
BEGIN
    ALTER TABLE fdx.ComplianceEvidence
    ADD ChecklistItemId UNIQUEIDENTIFIER NULL 
        CONSTRAINT FK_ComplianceEvidence_ChecklistItem 
        REFERENCES fdx.ComplianceChecklistItems(ItemId);
        
    CREATE INDEX IX_Evidence_Item ON fdx.ComplianceEvidence(ChecklistItemId);
END
GO

-- =====================================================
-- 4) SEED DATA - Label Compliance Checklist
-- =====================================================

-- Seeding for Label Claims & Regulatory Check
DECLARE @labelStepId UNIQUEIDENTIFIER = 
    (SELECT StepTemplateId FROM fdx.ComplianceStepTemplates WHERE StepCode = 'LBL_CLAIMS');

IF @labelStepId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM fdx.ChecklistTemplates WHERE StepTemplateId = @labelStepId)
BEGIN
    DECLARE @checklistTemplateId UNIQUEIDENTIFIER = NEWID();
    
    INSERT INTO fdx.ChecklistTemplates (ChecklistTemplateId, StepTemplateId, Title, IsActive)
    VALUES (@checklistTemplateId, @labelStepId, N'Label Compliance (IL/EU)', 1);

    INSERT INTO fdx.ChecklistTemplateItems (ChecklistTemplateId, ItemCode, Title, Required, DefaultAssigneeRole, SortOrder) VALUES
    (@checklistTemplateId, 'LBL_INGREDIENTS',  N'Ingredients list formatted & ordered by weight', 1, 'agency_pm', 10),
    (@checklistTemplateId, 'LBL_ALLERGENS',    N'Allergen declarations per IL/EU rules', 1, 'buyer_qa_manager', 20),
    (@checklistTemplateId, 'LBL_NUTRITION',    N'Nutrition table per region (unit & lang)', 1, 'agency_pm', 30),
    (@checklistTemplateId, 'LBL_BARCODE',      N'Valid GTIN/EAN-13 scannable on artwork', 1, 'agency_pm', 40),
    (@checklistTemplateId, 'LBL_KOSHER_MARK',  N'Correct kosher mark + authority naming', 1, 'buyer_kosher_mgr', 50),
    (@checklistTemplateId, 'LBL_CLAIMS',       N'Claims substantiation files attached', 0, 'buyer_marketing', 60);
END
GO

-- Seeding for Kosher Label Marking Check
DECLARE @kosherMarkingStepId UNIQUEIDENTIFIER = 
    (SELECT StepTemplateId FROM fdx.ComplianceStepTemplates WHERE StepCode = 'KOSHER_LABEL_MARKING');

IF @kosherMarkingStepId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM fdx.ChecklistTemplates WHERE StepTemplateId = @kosherMarkingStepId)
BEGIN
    DECLARE @kosherChecklistTemplateId UNIQUEIDENTIFIER = NEWID();
    
    INSERT INTO fdx.ChecklistTemplates (ChecklistTemplateId, StepTemplateId, Title, IsActive)
    VALUES (@kosherChecklistTemplateId, @kosherMarkingStepId, N'Kosher Label Verification', 1);

    INSERT INTO fdx.ChecklistTemplateItems (ChecklistTemplateId, ItemCode, Title, Required, DefaultAssigneeRole, SortOrder) VALUES
    (@kosherChecklistTemplateId, 'KOSHER_SYMBOL', N'Kosher symbol matches certificate', 1, 'buyer_kosher_mgr', 10),
    (@kosherChecklistTemplateId, 'KOSHER_AUTH_NAME', N'Authority name correctly displayed', 1, 'buyer_kosher_mgr', 20),
    (@kosherChecklistTemplateId, 'KOSHER_DAIRY_MARK', N'Dairy/Pareve marking if applicable', 1, 'buyer_kosher_mgr', 30),
    (@kosherChecklistTemplateId, 'KOSHER_PASSOVER', N'Passover designation if applicable', 0, 'buyer_kosher_mgr', 40);
END
GO

-- =====================================================
-- 5) STORED PROCEDURES
-- =====================================================

-- Ensure checklist exists for a step
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_EnsureChecklistForStep
    @StepId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if checklist already exists
    IF EXISTS (SELECT 1 FROM fdx.ComplianceChecklists WHERE StepId = @StepId) 
        RETURN;

    -- Get the step template ID
    DECLARE @StepTemplateId UNIQUEIDENTIFIER =
        (SELECT StepTemplateId FROM fdx.ComplianceSteps WHERE StepId = @StepId);

    -- Find active checklist template for this step template
    DECLARE @ChecklistTemplateId UNIQUEIDENTIFIER =
        (SELECT TOP 1 ChecklistTemplateId
         FROM fdx.ChecklistTemplates
         WHERE StepTemplateId = @StepTemplateId AND IsActive = 1
         ORDER BY CreatedAt DESC);

    IF @ChecklistTemplateId IS NULL 
        RETURN;

    -- Create checklist instance
    DECLARE @ChecklistId UNIQUEIDENTIFIER = NEWID();
    
    INSERT INTO fdx.ComplianceChecklists (ChecklistId, StepId, Title, Status)
    SELECT @ChecklistId, @StepId, Title, 'open'
    FROM fdx.ChecklistTemplates 
    WHERE ChecklistTemplateId = @ChecklistTemplateId;

    -- Create checklist items from template
    INSERT INTO fdx.ComplianceChecklistItems
        (ChecklistId, ItemCode, Title, Required, SortOrder)
    SELECT 
        @ChecklistId, 
        ItemCode, 
        Title, 
        Required, 
        SortOrder
    FROM fdx.ChecklistTemplateItems
    WHERE ChecklistTemplateId = @ChecklistTemplateId
    ORDER BY SortOrder;
    
    SELECT @ChecklistId AS ChecklistId;
END
GO

-- Toggle checklist item and roll up progress
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_ChecklistItemSet
    @ItemId UNIQUEIDENTIFIER,
    @Status NVARCHAR(15),             -- open/done/na/blocked
    @UserId UNIQUEIDENTIFIER = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @Status NOT IN ('open', 'done', 'na', 'blocked') 
    BEGIN
        THROW 50010, 'Invalid checklist status. Must be: open, done, na, or blocked', 1;
    END

    -- Update item status
    UPDATE fdx.ComplianceChecklistItems 
    SET Status = @Status,
        UpdatedAt = SYSUTCDATETIME()
    WHERE ItemId = @ItemId;

    -- Get related IDs for rollup
    DECLARE @ChecklistId UNIQUEIDENTIFIER = 
        (SELECT ChecklistId FROM fdx.ComplianceChecklistItems WHERE ItemId = @ItemId);
    
    DECLARE @StepId UNIQUEIDENTIFIER = 
        (SELECT StepId FROM fdx.ComplianceChecklists WHERE ChecklistId = @ChecklistId);
    
    DECLARE @StageId UNIQUEIDENTIFIER = 
        (SELECT StageId FROM fdx.ComplianceSteps WHERE StepId = @StepId);
    
    DECLARE @ComplianceId UNIQUEIDENTIFIER = 
        (SELECT ComplianceId FROM fdx.ComplianceStages WHERE StageId = @StageId);

    -- Calculate checklist progress
    DECLARE @RequiredCount INT = 
        (SELECT COUNT(*) FROM fdx.ComplianceChecklistItems 
         WHERE ChecklistId = @ChecklistId AND Required = 1);
    
    DECLARE @DoneCount INT = 
        (SELECT COUNT(*) FROM fdx.ComplianceChecklistItems 
         WHERE ChecklistId = @ChecklistId AND Required = 1 AND Status IN ('done', 'na'));
    
    DECLARE @BlockedExists BIT = 
        CASE WHEN EXISTS(SELECT 1 FROM fdx.ComplianceChecklistItems 
                        WHERE ChecklistId = @ChecklistId AND Status = 'blocked') 
             THEN 1 ELSE 0 END;

    -- Update checklist status
    UPDATE fdx.ComplianceChecklists
    SET Status = CASE 
            WHEN @BlockedExists = 1 THEN 'blocked'
            WHEN @RequiredCount > 0 AND @DoneCount = @RequiredCount THEN 'in-review'
            ELSE 'open' 
        END,
        UpdatedAt = SYSUTCDATETIME()
    WHERE ChecklistId = @ChecklistId;

    -- If all required items are done, move step to in-review
    IF @RequiredCount > 0 AND @DoneCount = @RequiredCount
    BEGIN
        UPDATE fdx.ComplianceSteps 
        SET Status = 'in-review',
            UpdatedAt = SYSUTCDATETIME()
        WHERE StepId = @StepId AND Status NOT IN ('approved', 'rejected');
        
        -- Update stage progress
        EXEC fdx.usp_Compliance_UpdateStageProgress @StageId;
    END
    
    -- Return current progress info
    SELECT 
        @ChecklistId AS ChecklistId,
        @StepId AS StepId,
        @RequiredCount AS RequiredCount,
        @DoneCount AS DoneCount,
        CASE WHEN @RequiredCount > 0 
             THEN CAST(@DoneCount * 100.0 / @RequiredCount AS INT) 
             ELSE 0 END AS ProgressPercent;
END
GO

-- Update stage progress (helper proc)
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_UpdateStageProgress
    @StageId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @TotalSteps INT = 
        (SELECT COUNT(*) FROM fdx.ComplianceSteps WHERE StageId = @StageId);
    
    DECLARE @ApprovedSteps INT = 
        (SELECT COUNT(*) FROM fdx.ComplianceSteps 
         WHERE StageId = @StageId AND Status = 'approved');
    
    DECLARE @Progress INT = 
        CASE WHEN @TotalSteps > 0 
             THEN (@ApprovedSteps * 100) / @TotalSteps 
             ELSE 0 END;
    
    UPDATE fdx.ComplianceStages
    SET Progress = @Progress,
        UpdatedAt = SYSUTCDATETIME(),
        Status = CASE 
            WHEN @Progress = 100 THEN 'approved'
            WHEN @Progress > 0 THEN 'in-progress'
            ELSE Status
        END,
        ApprovedAt = CASE 
            WHEN @Progress = 100 THEN SYSUTCDATETIME()
            ELSE ApprovedAt
        END
    WHERE StageId = @StageId;
END
GO

PRINT 'Compliance Checklist schema created successfully!';
GO